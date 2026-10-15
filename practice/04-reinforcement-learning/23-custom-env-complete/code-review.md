# 23번 코드 리뷰 — 환경 설계와 학습 전 기준 측정

[실습 기록](README.md) · [제공된 코드](23_custom_env_complete.py)

## 1. 선언과 실행을 구분하기

`obs_*` 함수는 상태에서 `(N, dim)` 관측을, `rew_*`는 `(N,)` 보상을, `term_*`는 `(N,)` bool 종료 판정을 반환한다.
여섯 Cfg를 `MyCartpoleEnvCfg`에 등록하고 `ManagerBasedRLEnv`를 생성하면 manager가 함수를 호출한다.
직접 만든 함수는 **관측 2 + 보상 3 + 종료 1 = 총 6개**다. 자료의 ‘5개’는 종료 함수를 제외한 관측·보상 함수 수로 구분해야 한다.
함수 접두사는 이름 규칙이며 자동 등록 기능은 아니다.

main의 `env_cfg.scene.num_envs = args_cli.num_envs`가 클래스 기본 4를 덮어쓴다. 사용자 버전 CLI 기본은 100이며 upstream과의 변경은 이 한 곳이다.

## 2. 정규분포 clamp는 균등 랜덤이 아니다

```python
action = torch.randn(env.num_envs, 1, device=env.device).clamp(-1, 1)
```

이번에는 실제로 입력을 ±1로 제한한다. 하지만 정규분포의 꼬리를 경계로 모으기 때문에 ±1에 값이 쌓인다. 22번의 균등 난수나 범위 안에서 재샘플링한 정규분포와 다르다.
ActionCfg 자체의 clip은 설정하지 않는다. 따라서 다른 실행기가 넘기는 입력까지 자동으로 ±1이 되는 것은 아니다.

관측을 행동 선택에 사용하지 않고 PPO·optimizer도 없으므로 전이 50,000개를 만들어도 정책 가중치는 학습되지 않는다.
힘 scale=100이며 직선 관절 단위는 N이다. 기본 카트 actuator의 damping=10을 유지하므로 ‘순수 외부 힘만 작용’한다고 해석하지 않는다.

## 3. 관측 함수와 clip의 역할

`obs_cart_normalized()`는 위치/3만 반환한다. 함수 내부에 clip은 없고 `ObsTerm(clip=(-1, 1))`에서 적용한다.
이 구분은 함수만 따로 호출할 때 중요하다.
관측 순서는 위치 2 → 속도 2 → sin/cos 2 → 정규화 위치 1이다. 노이즈는 비활성화한다.
중복 표현을 추가한 것이며 독립 센서 정보가 늘어난 것은 아니다. raw 각도가 남아 있어 전체 관측의 각도 경계 표현이 제거된 것도 아니다.

## 4. 막대 종료 조건과 태스크의 의미

```python
return torch.abs(angle) > max_angle
```

설정 max_angle=π/2이므로 정확히 90°는 참이 아니며, >90°일 때 종료한다. raw joint angle을 사용하고 wrap하지 않는다.
sin/cos 직립 보상은 주기적인 반면 이 종료 조건은 누적 각도로 판정한다. 현재처럼 ±45°에서 시작해 90° 초과 시 종료하는 balancing에는 의도에 맞지만, 여러 회전을 허용하는 swing-up에는 그대로 사용하기 어렵다.
‘90° 초과는 복구 불가’는 물리 법칙이 아니라 **이번 태스크에서 실패로 정한 경계**다. 목표가 바뀌면 초기화·종료·보상을 함께 다시 설계한다.

`time_out=True`는 truncation 분류이며 성공 플래그가 아니다. 이 파일에 성공 판정 함수는 없다.

## 5. 종료와 timeout이 동시에 발생하는 경우

현재 로그는 `timeout if truncated else terminated`를 사용한다. 두 플래그가 동시에 참이면 task 실패가 있어도 timeout으로만 출력한다.
정확한 기록은 두 플래그를 함께 출력하고, task 종료에서는 각 조건도 구분하는 편이 좋다.

```python
# 개선 예시 · 제공 코드에는 적용하지 않음
for idx in done_envs.tolist():
    print(idx, "terminated=", bool(terminated[idx]), "truncated=", bool(truncated[idx]))
    for name in env.termination_manager.active_terms:
        flag = env.termination_manager.get_term(name)[idx]
        if bool(flag):
            print("  조건:", name)
```

가치 학습에서는 termination이면 일반적으로 미래 가치 연결을 끊고, 순수 시간 제한에는 올바른 종료 상태의 가치를 bootstrap한다. 구체적 처리는 학습 래퍼·실행기에 달려 있다.
23번에는 Critic이 없으므로 실제 bootstrap 계산도 없다. timeout 설정만으로 가치 학습을 수행하지 않는다.

## 6. 보상 단위와 이상적 점수

함수 값 × 가중치 × 환경 step dt를 합산한다. `cos`는 [-1, 1], 중앙 가우시안은 최대 1이며 실제 sigma는 params의 1.5다.
`energy`는 raw action 제곱합이다. 실제 일·소비 전력을 측정하는 함수가 아니다.
최적 상태·행동 0에서 생존 1 + 직립 2 + 중앙 0.5 = 초당 3.5점, 5초에 약 17.5점이다.
실패 항도 dt를 곱하므로 task 실패 step의 -2 항 기여는 -2/60점이다. 종료 순간의 전체 보상에는 다른 항도 포함된다.

timeout 자체를 `is_terminated` 실패 벌점으로 세지는 않는다. 실패와 timeout이 동시 발생하면 task 실패는 그대로 고려된다.
양수 보상이나 큰 학습 전후 차이만으로 설계가 적절하다고 판단하지 않는다. 실제 직립 유지·카트 위치·실패 빈도와 함께 확인한다.

## 7. 누적 통계의 선택 편향과 실행 길이

보상을 더한 뒤 완료 에피소드를 저장하고 해당 환경의 버퍼를 0으로 초기화하는 흐름은 적절하다.
다만 통계는 `completed_rewards`만 사용한다. 500 step에서 진행 중인 긴 에피소드는 빠지며 짧게 실패한 환경은 더 많은 완료 에피소드를 제공한다.
따라서 이 평균은 환경별 평균이나 모든 진행 중인 경험의 평균이 아니다.
학습 전후 평가에서는 환경 수·seed·초기화·행동 분포를 기록하고, 정해진 수의 완결 에피소드로 평가하는 편이 비교하기 쉽다.

`episode_lengths`를 누적하지만 최종 평균 길이를 출력하지 않는다. 완료 길이·task 실패/timeout 수·위치 및 각도 오차도 같이 기록하면 사람이 결과를 판단하기 좋다.
1532회는 모든 환경의 완료 합계이며 PPO iteration·모델 업데이트 횟수가 아니다.

## 8. 자동 리셋과 private 필드

`env.step()` 내부에서 완료 환경만 자동 리셋한다. 반환 종료 플래그·보상은 끝난 에피소드에 해당하지만 관측은 새 초기 상태일 수 있다.
외부에서 전체 `env.reset()`을 매번 추가하면 진행 중인 다른 환경까지 초기화할 수 있으므로 주의한다.

보상·종료 Cfg 출력에는 `_term_names`, `_term_cfgs` 같은 private 필드를 사용한다. 공개 API로 바꾸면 내부 구조 변경에 덜 의존한다.

```python
# 개선 예시 · 원본에는 적용하지 않음
for name in env.reward_manager.active_terms:
    cfg = env.reward_manager.get_term_cfg(name)
    print(name, cfg.weight)
for name in env.termination_manager.active_terms:
    cfg = env.termination_manager.get_term_cfg(name)
    print(name, cfg.time_out)
```

## 9. 24번과의 연결 확인

기준 튜토리얼 24번은 같은 핵심 MDP 설계를 파일 안에 재정의하고 환경 수·학습 설정을 추가한다. 23번 Cfg를 import하는 방식은 아니다.
24번 관측은 **7차원**이며 Actor/Critic 은닉층은 각각 `[32, 32]`다. 기존 공용 모델 구성도의 입력 4개 표기를 이 확인에 맞춰 7개로 수정했다.
공통 환경 정의를 별도 모듈로 분리하면 학습·평가 사이 설정 불일치를 줄일 수 있다. 현재 원본 파일은 보존한다.

## 구현 근거

- [기준 24번: 환경과 학습 실행기](https://github.com/PinkWink/isaacsim_tutorials/blob/14f85fc6edece7cbb1faa50aa9fe3adef205e87a/24_train_cartpole/24_train_cartpole.py)
- [Isaac Lab v2.3.2 종료 manager](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/termination_manager.py)
- [환경 step·자동 리셋](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [Reward Manager](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
