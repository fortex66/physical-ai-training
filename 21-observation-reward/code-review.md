# 21번 커스텀 관측·보상 코드 리뷰

[실습 결과](README.md) · [제공 코드](21_observation_reward.py) · [강화학습 개념](../learning-notes/reinforcement-learning/README.md)

제공 코드는 수정 없이 보존한다. 아래는 코드·강의 설명과 Isaac Lab v2.3.2 구현을 대조한 리뷰다.
20번에서 확인한 랜덤 행동 범위, 시간 스케일링과 자동 리셋도 계속 적용된다.

## 1. 관측 7개는 맞지만 독립 정보 7개는 아니다

[관측 설정](21_observation_reward.py#L210)은 기본 위치 2개 + 속도 2개 + sin/cos 2개 + 정규화 위치 1개다.
함수 반환 크기를 `(N, 차원)`으로 맞추고 그룹에서 연결하는 구성은 맞다.

하지만 raw 위치에 이미 막대 각도와 카트 위치가 포함돼 있다.
sin/cos와 정규화 위치는 같은 상태의 다른 표현이지 새 센서 정보가 아니다.
raw 각도 항도 남아 있으므로 sin/cos를 추가했다고 전체 입력의 경계 표현이 없어지는 것은 아니다.
학습 입력을 바꾸려면 중복 표현의 목적과 관측 순서·단위도 명시해야 한다.

20번의 4차원 모델과 21번의 7차원 모델은 입력 형상이 다르다.
4차원 관측으로 학습한 신경망을 변경 없이 7차원 입력에 바로 연결할 수는 없다.
같은 차원이라도 항 순서·scale이 바뀌면 입력의 의미가 달라진다.

## 2. 정규화·clip·scale·noise는 다른 처리다

```python
cart_pos_norm = ObsTerm(
    func=cart_position_normalized,
    params={"max_pos": 3.0},
    clip=(-1.0, 1.0),
)
```

위치/3은 함수 내부의 크기 변환이며, 그 자체가 범위를 보장하지는 않는다.
±1 제한은 ObsTerm의 clip이 처리한다.
그룹 전체를 정규화한 것이 아니라 추가한 위치 항 하나에 적용한 것이다.

Isaac Lab v2.3.2의 일반 처리 순서는 다음과 같다.

![관측 전처리 순서](../learning-notes/reinforcement-learning/diagrams/09-observation-processing.png)

이 코드에는 noise와 ObsTerm.scale 설정이 없고 `enable_corruption=False`다.
강의에서 옵션을 소개하는 것과 현재 코드에 옵션이 적용됐다는 것은 다르다.
noise를 실험하려면 노이즈 설정과 그룹의 corruption 활성화를 함께 확인한다.

## 3. 직립 보너스의 실제 범위는 [-1, 1]

[직립 함수](21_observation_reward.py#L121)는 `torch.cos(pole_angle)`을 반환한다.
주석의 ‘0~1’, ‘90°에서 최소’ 설명과 다르다.

| 각도 | 원시 값 | weight=2 적용 값 · dt 적용 전 |
|---|---|---|
| 0° | +1 | +2 |
| 90° | 0 | 0 |
| 180° | -1 | -2 |

거꾸로 선 상태를 감점하는 것이 의도라면 현재 식은 사용할 수 있다.
정말 0~1 보너스를 원하면 `(cos(각도)+1)/2` 같은 다른 함수를 선택할 수 있지만,
보상의 기준점·상대 규모도 바뀌므로 의도에 맞게 결정해야 한다. 원본 코드에는 적용하지 않았다.

## 4. 가우시안 중앙 보상의 폭

[중앙 보상](21_observation_reward.py#L136)은 카트 위치가 0일 때 1이고, 멀어질수록 작아진다.
`RewardsCfg`의 실제 sigma는 함수 기본값 1.0이 아니라 params의 **1.5**다.

sigma가 작으면 중앙에서 조금 벗어나도 점수가 빨리 줄고, 크면 넓은 범위에 보상을 준다.
sigma는 양수, 위치 정규화의 max_pos도 양수여야 한다.
원시 보상, 가중치 0.5 적용 값과 최종 dt 적용 기여를 구분한다.

## 5. ‘energy’는 실제 에너지·실제 힘의 제곱합이 아니다

[패널티 함수](21_observation_reward.py#L156)는 다음 값을 쓴다.

```python
return torch.sum(env.action_manager.action ** 2, dim=-1)
```

`ActionManager.action`은 환경에 입력한 raw action이다.
scale=100 적용 후의 힘, 실제 actuator 힘, 물리 에너지 측정값이 아니다.
정확한 표현은 **입력 행동 크기의 제곱합을 줄이는 regularization**이다.

입력 행동이 1이면 raw 제곱합은 1이다.
카트 힘 목표는 스케일링 단계에서 100 N에 해당하지만 현재 패널티는 100²가 아니다.
scale을 바꾸면 같은 raw action의 물리 효과가 달라지므로 패널티 의도도 함께 확인한다.
실제 일·에너지를 평가하려면 힘·속도·시간 또는 별도 모터 모델 등 다른 물리량이 필요하다.

## 6. 항별 로그는 누적 총점과 단위가 다르다

[항별 출력](21_observation_reward.py#L419)은 `_step_reward`를 직접 읽는다.
Isaac Lab v2.3.2에서는 세 값의 의미가 다음과 같다.

| 값 | 의미 |
|---|---|
| `_step_reward[n, 항]` | 마지막 step의 함수 값 × weight · dt 적용 전 |
| `rew[n]` | 모든 가중 항의 합 × 환경 dt |
| `episode_rewards[n]` | 에피소드 동안 받은 rew의 누적 합 |

즉 마지막 항별 값들을 더한 뒤 `1/60`을 곱하면 그 step의 반환 보상과 연결된다.
그대로 더해서 에피소드 전체 총점과 비교하면 안 된다.
코드가 출력하는 것은 에피소드 종료 시점의 **마지막 값**이며 항별 에피소드 누적 기여도가 아니다.

영상에 직립 항 -1.2700이 나타나도 이는 누적 감점 -1.27점이라는 뜻이 아니다.
각 항이 에피소드 전체에 얼마나 기여했는지 비교하려면 항별 누적 기록을 별도로 관리해야 한다.

## 7. private 필드 접근과 공개 조회 API

`_term_names`, `_term_cfgs`, `_step_reward`는 내부 필드라 라이브러리 변경에 취약하다.
v2.3.2에는 다음 공개 API가 있다.

```python
# 개선 예시 · 원본에는 적용하지 않음
for name in env.reward_manager.active_terms:
    cfg = env.reward_manager.get_term_cfg(name)
    print(name, cfg.weight)

for name, values in env.reward_manager.get_active_iterable_terms(env_idx=0):
    weighted_value = values[0]  # dt 적용 전 마지막 값
    step_contribution = weighted_value * env.step_dt
    print(name, weighted_value, step_contribution)
```

공개 API를 사용해도 조회값의 시간 단위가 바뀌는 것은 아니다.
에피소드별 누적을 원하면 별도 버퍼와 완료 환경 초기화가 필요하다.

## 8. 코드에 있지만 사용하지 않는 것

`all_joint_velocities()`는 정의돼 있지만 ObsTerm에 등록하지 않는다.
실제 속도 관측은 `mdp.joint_vel_rel`이며 두 함수를 동시에 사용하는 것은 아니다.
`wrap_to_pi` import도 현재 코드에서 사용하지 않는다.
관측 차원은 선언된 함수 수가 아니라 **등록·활성화된 항의 반환 차원**으로 계산한다.

## 9. 20번에서 이어지는 확인 사항

- 여전히 `torch.randn()`으로 행동을 만들며 ±1 제한이나 신경망 가중치 업데이트는 없다.
- 카트 경계 이탈·시간 제한만 종료 조건이며 막대 각도 종료는 없다.
- 종료 로그는 `terminated`만 출력하므로 `truncated`도 함께 출력하면 이유를 읽기 쉽다.
- episode_count는 모든 환경의 완료 수를 합친 전역 번호이며 환경별 에피소드 번호가 아니다.
- 실행 상한 1000은 환경 step 수이며 학습 iteration이나 에피소드 수가 아니다.

관측을 늘리거나 보상 총점이 바뀌었다는 사실만으로 학습이 좋아졌다고 결론 내리지 않는다.
정책 학습 실험에서는 초기화·seed·학습 예산·평가 조건을 맞추고 작업 성공 지표도 비교한다.

## 구현 근거

- [Observation Manager: noise·clip·scale 처리](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/observation_manager.py)
- [Action Manager: raw action](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/action_manager.py)
- [Reward Manager: dt·로그·공개 API](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
