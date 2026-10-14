# 20번 강화학습 환경 코드 리뷰

[실행 코드](20_base_env.py) · [실습 결과](README.md) · [강화학습 개념](../learning-notes/reinforcement-learning/README.md)

제공된 코드를 기준으로 환경 정의와 실행 흐름을 리뷰했다.
원본 파일을 보존하며, 아래 수정 예시는 아직 실행 코드에 적용하지 않았다.
라이브러리 동작 설명은 Isaac Lab v2.3.2 소스와 대조했다.

[환경 구성도·물리 step 처리 순서](../learning-notes/reinforcement-learning/diagrams/README.md)를 함께 보면 아래 리뷰를 코드 실행 흐름에 연결하기 쉽습니다.

## 먼저 알아야 할 결론

1. 환경의 관측·행동·보상·종료·리셋 구조는 정의돼 있다.
2. Policy·Critic 신경망 생성, PPO 업데이트와 체크포인트 저장은 없다.
3. 랜덤 행동과 보상을 오래 출력해도 정책 가중치가 학습되지는 않는다.
4. 학습 전에 행동 범위, 종료 의도와 보상 크기를 다시 확인해야 한다.

## 흐름을 따라 읽기

| 코드 | 역할 | 확인할 점 |
|---|---|---|
| `CartpoleSceneCfg` | 로봇과 장면 구성 | 어떤 로봇 관절을 사용하는가? |
| [`ActionsCfg`](20_base_env.py#L102) | 행동을 카트 effort로 변환 | 범위·scale·물리 힘 제한 |
| [`ObservationsCfg`](20_base_env.py#L122) | policy 관측 그룹 생성 | 항목·단위·순서와 입력 크기 |
| [`EventCfg`](20_base_env.py#L153) | 에피소드 초기 상태 변경 | 초기 난이도와 위치·속도 범위 |
| [`RewardsCfg`](20_base_env.py#L188) | 평가 기준 구성 | 의도·상대 크기·시간 간격 |
| [`TerminationsCfg`](20_base_env.py#L232) | task 종료와 시간 제한 | 막대 각도 종료 유무 |
| [`CartpoleEnvCfg`](20_base_env.py#L254) | 전체 구성과 주기 설정 | decimation·episode 길이 |
| [`main`의 실행 루프](20_base_env.py#L335) | 랜덤 행동·로그·자동 리셋 확인 | 실제 학습 과정 유무 |

## 리뷰 1. `PolicyCfg`는 정책 신경망이 아니다

```python
class PolicyCfg(ObsGroup):
    joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
    joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel)
```

여기서는 정책에 줄 입력을 구성한다. 두 위치와 두 속도를 합친 `(N, 4)` 관측 텐서다.
`policy: PolicyCfg()`는 관측 그룹 등록이지 Actor 생성이 아니다.
별도 `critic` 관측 그룹이 없다고 이후 PPO의 Critic을 사용할 수 없다는 뜻도 아니다.
Actor와 Critic이 같은 관측을 쓰는 학습 구성도 가능하다.

`policy`·`critic` 그룹의 연결은 학습기와 래퍼·버전 설정의 역할이다.
그룹 이름만으로 임의의 PPO·SAC 구현에 신경망이 자동 연결된다고 일반화하지 않는다.

## 리뷰 2. 랜덤 행동의 주석과 실제 분포가 다르다

[행동 생성 코드](20_base_env.py#L335)는 다음과 같다.

```python
action = torch.randn(env.num_envs, 1, device=env.device)
```

주석은 ‘균일 랜덤 [-1, 1]’이라고 하지만 실제로는 평균 0·표준편차 1의 정규분포다.
±1 밖의 값도 발생하며 코드에 입력 범위를 제한하는 처리가 없다.
`scale=100`은 곱셈 설정이므로, 처리된 effort 목표가 반드시 ±100 N 안이라는 보장은 없다.
예를 들어 action=1.5는 스케일링 단계에서 150 N 목표에 해당한다.
실제 적용 힘에는 로봇 actuator와 물리 한계가 추가로 영향을 줄 수 있다.

의도가 정말 균일한 [-1, 1] 테스트라면 다음처럼 샘플링할 수 있다.

```python
# 개선 예시 · 현재 파일에는 적용하지 않음
# shape=(N,1)을 유지하며 [-1,1] 범위의 균일 분포 샘플 생성
action = torch.empty(env.num_envs, 1, device=env.device).uniform_(-1.0, 1.0)
```

`randn().clamp(-1, 1)`은 제한된 정규분포 샘플이며 균일분포와는 다르다.
실제 학습에서는 정책 출력 분포, action clipping과 scale을 함께 설계한다.

## 리뷰 3. 막대가 기울면 감점하지만 종료하지는 않는다

현재 task termination은 카트 위치가 `[-3, 3]` 범위 밖으로 나간 경우뿐이다.
그 외에는 5초 시간 제한으로 중단된다.
막대 각도 임계값을 넘으면 종료하는 항은 없다.

따라서 ‘균형을 잃으면 곧바로 실패 종료하는 Cartpole’을 의도했다면 종료 설정이 부족하다.
반대로 쓰러진 상태에서도 회복하는 문제를 의도했다면 계속 진행하는 것이 설계 선택일 수 있다.
보상과 종료는 의도한 작업에 맞춰 함께 정해야 한다.

관절 각도 편차 감점은 기본값에서의 raw 절댓값 차이다.
여러 바퀴 회전할 수 있는 문제를 다룬다면 같은 물리 방향의 각도 표현과 주기성을 고려할지도 확인한다.
현재 함수는 이를 별도로 정규화하지 않는다.

## 리뷰 4. `weight=+1`과 반환되는 +1은 다르다

주석을 그대로 읽으면 step마다 생존 +1, 실패 -2처럼 보인다.
하지만 보상 매니저는 다음처럼 계산한다.

```text
각 보상 기여 = 보상 함수 값 × 가중치 × 환경 step 시간
최종 보상 = 각 기여의 합계
환경 step 시간 = decimation × 물리 dt = 1/60초
```

생존 항의 함수 값이 1일 때 그 항의 기여는 약 +0.01667이다.
termination 항의 함수 값이 1이면 기여는 약 -0.03333이다.
다른 항의 감점은 여기에 별도로 더해진다.
종료 감점에 시간 간격이 곱해지는 점은 원하는 실패 비용을 설계할 때 특히 확인해야 한다.

설명용으로 생존 중 막대 편차 0.5 rad, 카트 속도 0.2 m/s, 막대 속도 0.1 rad/s라고 하자.

```text
시간 적용 전 평가값 = 1 - 0.5 - 0.01×0.2 - 0.005×0.1
                    = 0.4975
반환 보상            = 0.4975 / 60 ≈ 0.00829
```

그래서 작은 보상 숫자가 나온다고 계산이 잘못됐다고 판단할 수는 없다.
모든 조건이 이상적이고 task termination 없이 5초를 유지한다면 생존 항 누적은 대략 5점이며, 300점이 아니다.

## 리뷰 5. timeout을 실패 감점과 혼동하지 않는다

```python
time_out = DoneTerm(func=mdp.time_out, time_out=True)
```

`time_out=True`는 이 종료 항을 truncation으로 분류한다.
`mdp.is_terminated`는 task termination을 읽으므로 순수 시간 제한에는 -2 가중치 항이 적용되지 않는다.
`mdp.is_alive`도 task termination 여부를 기준으로 하므로 시간 제한만 있는 마지막 step에서는 생존 항이 계산된다.
시간 제한과 경계 이탈이 동시에 발생하면 task termination도 함께 고려된다.

일반적으로 termination은 성공일 수도 실패일 수도 있다.
이 코드의 반환값 설명에 있는 ‘실패로 끝남’은 현재 경계 이탈 조건에 해당하며, 모든 환경의 termination 정의는 아니다.

## 리뷰 6. 종료된 환경의 반환 관측은 새 에피소드 상태일 수 있다

```python
obs, rew, terminated, truncated, info = env.step(action)
done = terminated | truncated
```

Isaac Lab은 완료 환경을 `env.step()` 안에서 리셋하고 관측을 다시 계산한다.
따라서 종료 step의 보상·플래그는 끝난 에피소드에 해당하지만,
해당 환경의 반환 관측은 새 에피소드 초기 상태일 수 있다.

현재 코드는 행동이 관측과 무관한 랜덤 값이라 이를 학습 데이터에 저장하는 문제는 없다.
나중에 학습기를 직접 구현할 때는 종료 전 관측과 리셋 후 관측을 혼동하지 않도록 해야 한다.
truncation의 가치 보충에는 학습기·래퍼에 맞는 timeout·끝 상태 처리가 필요하다.
원본 반환 튜플만 임의의 학습 버퍼에 붙이는 것보다 공식 학습 래퍼와 종료 처리를 확인한다.

## 리뷰 7. 누적 보상 저장은 가중치 업데이트가 아니다

```python
total_reward += rew
```

환경별 에피소드 점수를 합쳐 로그로 출력하는 코드다.
이 파일에는 Actor·Critic, optimizer, loss, 역전파, PPO 실행기가 없다.
보상이 좋았던 행동을 다음에 더 자주 선택하도록 만드는 과정도 없다.

20번의 목적은 환경 인터페이스 확인이다.
24번에서는 RSL-RL의 학습 실행기에 환경과 신경망·PPO 설정을 전달하고 `runner.learn()`으로 실제 학습한다.
Critic을 추가한다는 것은 여기 관측 클래스 이름만 추가하는 것이 아니라 학습기의 가치망을 구성하는 것이다.

## 리뷰 8. 실행 상한과 로그를 정확히 읽는다

제공 코드의 실행 상한은 2000 환경 step이지만 직전 주석은 여전히 ‘300 스텝 후 종료’다.
이것은 알고리즘 오류가 아닌 주석과 동작의 불일치다.
2000은 에피소드 수·PPO iteration·신경망 업데이트 횟수가 아니다.

- 2000 환경 step은 약 33.33초의 시뮬레이션 시간이다.
- episode 상한은 5초이며, 카트 경계 이탈 시 더 일찍 끝날 수 있다.
- 환경 4개라면 step당 관측·행동 전이 4개를 만들 수 있다.
- 종료된 에피소드만 합계 로그를 출력하므로, 실행 상한에서 진행 중인 에피소드의 합계는 종료 로그에 포함되지 않을 수 있다.
- ‘평균 보상’은 현재 step의 환경 간 평균이며 학습 iteration별 성능 그래프가 아니다.

## 학습 전에 확인할 설계

| 질문 | 현재 코드 | 다음 단계에서 결정할 것 |
|---|---|---|
| 실패란 무엇인가? | 카트 경계 이탈 | 막대 자세 실패·회복의 목적 |
| 행동 크기는 적절한가? | 정규분포 랜덤 ×100 | 범위·물리 한계·구동 비용 |
| 보상은 의도와 맞는가? | 생존·각도·속도 항 | 항별 규모·실패 비용·평가 지표 |
| 어떤 상태에서 배울까? | ±45° 등 랜덤 초기화 | 시작 난이도·학습 분포 |
| Policy·Critic 입력은? | policy 관측 4개 | 같은 관측 또는 별도 critic 관측 |
| 어떻게 업데이트할까? | 업데이트 없음 | PPO 실행기·래퍼·학습 설정 |

이후 강화학습 실습도 환경 구성, 보상·종료 의도, 실제 학습 호출과 평가 지표를 나눠 리뷰한다.

## 구현 근거

- [보상 시간 스케일링](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
- [is_alive·is_terminated·각도·속도 보상](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/rewards.py)
- [종료 계산·자동 리셋·반환 관측](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [관절 행동 scale·offset·선택적 clip](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/actions/joint_actions.py)
- [카트 경계 비교](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/terminations.py)
