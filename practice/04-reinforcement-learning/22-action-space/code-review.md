# 22번 코드 리뷰 — 액션 공간과 실제 구동의 연결

[실습 기록](README.md) · [제공된 코드](22_action_space.py)

## 1. 실행 흐름과 학습 여부

`--action_mode` → 세 EnvCfg 중 선택 → 같은 씬·관측·보상·종료를 가진 환경 생성 → 리셋 → 행동 생성 → `env.step()` → 누적 로그 → 1000 step에서 종료한다.
행동은 사인파와 균등 난수다. 관측을 입력받아 행동을 정하는 신경망이나 optimizer·PPO 실행기가 없어 정책을 학습하지 않는다.
20~21의 `randn()`과 달리 이번 `2 * rand() - 1`은 [-1, 1) 안에서 샘플링한다.

## 2. 가장 중요한 사항: 액션 설정과 actuator 설정은 별개

[기본 Cartpole 설정](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_assets/isaaclab_assets/robots/cartpole.py)의 카트 actuator는 `stiffness=0`, `damping=10`, `effort_limit_sim=400`이다.
제공 코드는 `CARTPOLE_CFG.replace(prim_path=...)`만 호출하며 모드별 게인은 바꾸지 않는다.

액션 항은 `set_joint_effort_target`·`set_joint_position_target`·`set_joint_velocity_target` 중 어떤 목표를 전달할지 결정한다. 게인 변경 기능은 없다.

| 모드 | 현재 설정의 해석 |
|---|---|
| effort | 외부 힘 명령에 damping에 의한 속도 저항도 작용할 수 있음 |
| position | stiffness=0이므로 목표 위치 오차로 만드는 복원 힘 없음 · 잔존 속도 목표/감쇠 효과와 구분 |
| velocity | damping=10이 속도 오차에 반응 · 힘 제한과 동역학 때문에 목표 속도와 실제 속도가 다를 수 있음 |

implicit drive를 개념적으로 설명하면 `힘 = Kp × 위치 오차 + Kd × 속도 오차 + 외부 effort`다. 이는 단위·역할 설명이며 PhysX의 이산 해석을 그대로 구현한 식은 아니다.
따라서 강의의 ‘effort는 게인을 무시’, ‘position은 PD로 추종’을 이 파일의 실제 동작으로 단정하면 안 된다.

세 제어를 명확히 비교하려면 선택한 모드에 맞게 **카트 actuator만** 다시 구성한다. 예시는 튜닝 시작점이며 제공 원본에는 적용하지 않았다.

```python
# main(): env_cfg를 선택한 뒤, ManagerBasedRLEnv 생성 전에 넣는 개선 예시
from isaaclab.actuators import ImplicitActuatorCfg

kp, kd = {
    "effort": (0.0, 0.0),       # 순수 외부 힘 비교
    "position": (100.0, 10.0), # 위치 추종용 게인 예시
    "velocity": (0.0, 10.0),   # 속도 추종용 게인 예시
}[action_mode]
actuators = dict(env_cfg.scene.robot.actuators)
actuators["cart_actuator"] = ImplicitActuatorCfg(
    joint_names_expr=["slider_to_cart"],
    effort_limit_sim=400.0,
    stiffness=kp,
    damping=kd,
)
env_cfg.scene.robot = env_cfg.scene.robot.replace(actuators=actuators)
```

게인을 바꾸면 액션뿐 아니라 구동 특성도 달라지는 실험임을 기록한다. position은 목표/실제 위치, velocity는 목표/실제 속도, effort는 입력/적용 힘을 함께 비교해야 한다.

## 3. scale은 제한 장치가 아니다

[JointAction 구현](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/actions/joint_actions.py)은 `raw_action * scale + offset` 후 설정된 `clip`을 적용한다.
이번 코드는 clip을 설정하지 않는다. 입력이 ±1인 이유는 생성 함수이지 ActionCfg의 강제 제한이 아니다. 영상의 `Box(-inf, inf, ...)`도 그 차이를 보여준다.
나중에 PPO로 연결하면 분포 샘플을 항상 ±1로 가정하지 말고 학습 래퍼의 clipping·정책 출력 변환을 확인한다.
ActionTerm의 clip은 처리된 명령 단위이며, actuator의 힘 제한이나 관절의 위치 제한과도 별개다.

`use_default_offset=False`도 설정한 `offset`을 사용하므로 언제나 ‘scale만 적용’이라고 일반화하면 안 된다. 기본 offset이 0일 때만 그렇게 된다.
`True`는 기본 관절 위치/속도를 offset으로 사용하며 현재 상태에 더하는 상대 제어와 다르다.

## 4. 한 행동의 물리 적용 시간과 사인파 위상

물리 dt=1/120초, decimation=2라 환경 step=1/60초다. 한 번 생성한 행동을 두 물리 step에서 적용한다.
초기 구간 `sin(total_steps * 0.05)`의 0.05는 step당 위상 증가량(rad)이다. 실제 시간 기반으로 표현하려면 다음처럼 쓸 수 있다.

```python
# 같은 주파수의 개선 표현 · 원본에는 적용하지 않음
phase = total_steps * env.step_dt * 3.0
scalar = torch.sin(torch.tensor(phase, device=env.device))
action = scalar * torch.ones_like(action)
```

현재 사인파는 모든 환경에 같은 값을 주지만 초기 상태는 무작위이므로 실제 운동까지 같지는 않다.
랜덤 구간은 학습된 정책의 분포와 같지 않으며 ‘탐색 단계’라는 설명도 실제 모델 업데이트를 뜻하지 않는다.

## 5. 종료·누적 로그와 반환 관측

`done = terminated | truncated`로 두 종류의 완료를 처리하는 것은 적절하다. 최종 step 보상을 더하고 완료 환경의 누적 버퍼를 0으로 되돌린다.
다만 로그는 종료 원인을 출력하지 않는다. 플래그를 함께 기록하면 경계 이탈과 시간 제한을 구분할 수 있다.
`completed_episodes`는 모든 환경의 완료 수를 합친 번호이며 환경별 에피소드 번호가 아니다.

환경이 완료 환경을 자동 리셋하므로 `obs['policy']`의 위치·각도는 종료 직전이 아닌 새 에피소드 상태일 수 있다. 보상과 종료 플래그는 끝난 에피소드 결과다.
1000 step 실행 상한은 에피소드 수나 학습 iteration 수가 아니다.
관측은 기본 상태를 뺀 relative 값이다. 이 Cartpole의 기본 관절 위치가 0이라 로그와 실제 위치·각도 값이 일치한다.

## 6. 보상과 비교 실험

생존 +1, task 종료 -2, 막대 기본 각도 이탈 L1 -1, 카트 속도 L1 -0.01, 막대 속도 L1 -0.005의 가중치를 둔다. 반환 보상에는 환경 step dt도 곱해진다.
21장의 7차원 관측·커스텀 6개 보상 대신 기본 4차원 관측·5개 보상을 사용한다.
막대 각도는 벌점일 뿐 종료 조건은 아니다. timeout은 `is_terminated`의 실패 감점과 구분된다.

모드마다 scale·게인·명령 단위가 다르고 seed도 고정하지 않으므로 완료 횟수 하나로 어느 모드가 우수하다고 결론 내리지 않는다.
특히 position의 장시간 생존은 stiffness=0인 현재 설정에서 목표 추종의 증거가 아니다.

## 구현 근거

- [Isaac Lab v2.3.2 Cartpole actuator 설정](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_assets/isaaclab_assets/robots/cartpole.py)
- [JointAction 변환·목표 전달](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/actions/joint_actions.py)
- [환경 step·자동 리셋](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [Reward Manager](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
