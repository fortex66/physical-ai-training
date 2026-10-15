# 26번 코드 리뷰 — 등록된 보행 환경의 실제 의미

[실습 기록](README.md) · [제공 코드](26_train_locomotion.py)

## 1. 환경 레지스트리와 PPO 설정의 출처

`isaaclab_tasks` import가 Gym 레지스트리를 등록한다. `load_cfg_from_registry(task, "env_cfg_entry_point")`가 환경 Cfg를 반환하며 main에서 병렬 수를 덮어쓴다.
`gym.make(task, cfg=env_cfg)` → `RslRlVecEnvWrapper` → `OnPolicyRunner.learn()`로 학습한다. 제공 파일은 기준 튜토리얼과 동일하다.

환경은 등록 Cfg를 사용하지만 **에이전트 설정은 등록된 rsl_rl_cfg_entry_point에서 읽지 않는다.** 이 파일의 `[128,128,128]`·24 rollout·PPO 설정이 적용된다. task를 바꿔도 최적의 agent 설정이 자동 선택되는 것은 아니다.

## 2. 설정 상속을 따라 확인한 Flat 환경

Isaac Lab v2.3.2의 등록 경로는 `AnymalBFlatEnvCfg → AnymalBRoughEnvCfg → LocomotionVelocityRoughEnvCfg`다.
Flat은 지형을 plane으로 바꾸고 height scanner·정책 height_scan·terrain_levels curriculum을 제거한다.
따라서 main 주석의 ‘지형 커리큘럼 자동 적용’은 기본 Flat에는 맞지 않는다.
반면 관측 노이즈·초기 상태 랜덤화·일부 물성/질량/무게중심 변동·주기적 속도 교란은 학습 환경에 남는다. ‘평지이므로 아무 랜덤화도 없음’도 아니다.

이 문서는 v2.3.2 소스를 근거로 설명한다. 실제 실행 시 export한 Cfg나 패키지 잠금 파일은 첨부되지 않았으므로 수정된 로컬 설치 전체와 일치한다고 단정하지 않는다.

## 3. 위치 행동과 LSTM actuator-net

등록 Action은 `JointPositionActionCfg(scale=0.5, use_default_offset=True)`다.
`q_target = q_default + 0.5 × action`이며 rad 단위의 관절 목표로 변환한다. 몸통의 위치 목표나 매 step 현재 관절 위치에 더하는 누적 명령이 아니다.
ANYmal-B의 다리 actuator는 `ANYDRIVE_3_LSTM_ACTUATOR_CFG`이며 제공된 actuator-net으로 구동 동역학을 모사한다. 이를 단순 implicit PD라고 단정하면 안 된다.
PPO의 Actor·Critic은 ELU MLP다. actuator의 LSTM은 별도 사전 학습 모델이고, 이번 PPO가 동시에 새로 학습하는 대상이 아니다.

`RslRlVecEnvWrapper(env)`는 참조 v2.3.2에서 clip_actions=None이므로 ‘기본값이 입력을 ±1로 자른다’는 주석은 맞지 않는다. ActionCfg에도 clip을 따로 지정하지 않는다. 정책 입력 제한·관절 한계·actuator 토크 제한은 서로 다른 설정이다.

## 4. 관측 48개와 센서의 용도

3(선속도)+3(각속도)+3(중력 투영)+3(속도 명령)+12(위치)+12(속도)+12(이전 행동)=48이다.
각속도는 기체 축 주위 회전율이지 roll/pitch/yaw 각도 값이 아니다. 투영 중력은 기울기 정보를 주지만 중력 축 주변 yaw 회전은 구분하지 못한다.
이전 액션을 관측에 넣기만 해서 동작이 자동으로 부드러워지는 것은 아니다. action_rate_l2 등 목적과 함께 작용한다.
접촉 센서는 발 공중 시간·허벅지 접촉·몸통 실패에 사용되지만 발 접촉 힘이 직접 Actor 관측 항에 포함된 것은 아니다.

## 5. 속도 명령은 학습해야 할 목표다

기본 command는 기체 기준 `(vx, vy, ωz)`다. heading_command=True이므로 yaw 명령은 목표 heading 오차에서 생성될 수 있다.
기본 재샘플 주기는 10초, 일부 환경은 정지 명령이며 평면·yaw 명령 범위 설정은 각각 ±1 m/s·±1 rad/s다.
영상의 초록/파랑 화살표는 command/current 평면 속도다. 지형의 법선·발 착지 위치·발의 접촉력을 표시하는 화살표가 아니다.

## 6. 활성 보상과 접촉·종료

참조 Flat 설정의 비영 가중치는 다음과 같다. 무게중심/구동 등 설정도 상속되므로 코드의 출력 설명만 보고 Cfg를 대신하지 않는다.

| 항 | Flat 가중치 |
|---|---:|
| track_lin_vel_xy_exp | +1.0 |
| track_ang_vel_z_exp | +0.5 |
| lin_vel_z_l2 | -2.0 |
| ang_vel_xy_l2 | -0.05 |
| dof_torques_l2 | -2.5e-5 |
| dof_acc_l2 | -2.5e-7 |
| action_rate_l2 | -0.01 |
| feet_air_time | +0.5 |
| undesired_contacts · THIGH | -1.0 |
| flat_orientation_l2 | -5.0 |

`dof_pos_limits` 가중치는 0이다. 영상에 항 이름이 보인다고 학습에 비영 기여를 하는 것은 아니다.
feet_air_time은 **첫 착지 시점**에 `(last_air_time - 0.5)`를 합하며 평면 명령 norm>0.1에서 활성화한다. 오래 공중에 머무는 매 프레임마다 점수를 주거나 대각선 trot 주기를 지정하는 함수가 아니다.
발을 들지 않거나 짧게 스텝하면 보상이 음수가 될 수 있다. 제자리 yaw 명령만 있을 때도 평면 명령 조건을 구분해야 한다.

허벅지 접촉은 벌점, 몸통 base의 접촉 힘 threshold=1 초과는 task 종료다. 발의 정상 접촉은 지지에 필요하다. timeout은 20초이며 이 태스크에는 Cartpole 같은 생존 +1 항을 직접 정의하지 않는다.
또한 코드의 Cartpole ‘4개 보상’ 설명과 달리 24번 실제 Cfg는 6개 항이다.

## 7. rollout은 0.48초이며 여러 보행 주기가 아니다

물리 dt=0.005초·decimation=4라 정책/환경 step은 0.02초다. 24 step은 0.48초이므로 ‘0.5초 주기를 여러 번 포함’이라는 설명과 맞지 않는다.
GAE·bootstrap으로 수집 구간 밖의 가치를 연결하고 많은 iteration에서 반복 경험한다. 각 rollout에 완결 보행 주기가 여러 번 들어가야만 학습할 수 있는 것은 아니다.

2048환경 ×24=49,152 전이/iteration, 4 batch·5 epoch면 기본 optimizer 20회/iteration이다.
300 iteration은 총 14,745,600 전이·기본 optimizer 6000회다. 영상 최종 전이 수와 일치한다.
에피소드 상한은 20초·1000 환경 step이며 iteration·rollout과 다른 단위다.

## 8. 학습 통계 해석

영상 iteration 2의 평균 보상 -3.61·길이 63.02에서 최종 보상 18.93·길이 978.22로 변했다. 최종 시간 표시는 8분 2초다.
이 값은 영상에 보인 학습 중 집계이며 TensorBoard 원시 이벤트는 제공되지 않았다. 두 지점으로 전체 학습 곡선을 만들어내지 않았다.
최근 완료 에피소드 평균, 최대 episode 시간으로 정규화한 Episode_Reward, 종료 manager의 마지막 종료 집계를 구분한다. timeout=0.9581은 독립 평가 성공률이 아니다.
속도 error metric도 command 관리자의 집계 단위를 확인해야 하며 화면 한 시점의 순간 추적 오차로 단정하지 않는다.
Cartpole과 보상/시간/목표가 다르므로 총점 절대값을 비교하지 않는다. ‘300이면 robust 완성’, ‘모든 GPU에서 정해진 시간/VRAM’은 보장할 수 없다.

## 9. Rough 전환은 자동 fine-tuning이 아니다

원본에는 `--checkpoint` 인자나 `runner.load()`가 없다. `--task Isaac-Velocity-Rough-Anymal-B-v0`는 다른 환경으로 새 학습을 시작할 뿐 Flat 가중치를 이어서 학습하지 않는다.
Rough에는 height scan이 추가돼 입력 차원도 달라질 수 있다. 기존 Flat 체크포인트를 단순 load하면 모델 입력 크기가 맞지 않을 수 있어 관측·모델 전환 방법을 먼저 설계해야 한다.
추가 지형·노이즈·외란 조건에서의 보행은 27 평가와 이후 지형/랜덤화 실험에서 확인한다.

## 10. 로그·모델과 게시 자료

현재 로그 경로는 run별 하위 폴더 없이 고정이다. 재실행 시 모델 이름이 충돌할 수 있어 24번 리뷰의 timestamp 경로·Cfg/버전/seed 저장 방식을 적용할 수 있다.
`init_at_random_ep_len=True`는 처음 episode 시간 카운터를 분산하며 물리 상태를 미리 과거부터 시뮬레이션하는 기능이 아니다.
저장 주기 50과 마지막 저장으로, 300회 완료 시 예상 파일은 model_0·50·100·150·200·250·299.pt다. 이번에는 실제 체크포인트가 첨부되지 않아 파일 존재를 확인한 것은 아니다.
두 번째 영상은 끝에 브라우저가 보여 터미널 영역만 lossless VP9로 추출한 게시본을 만들었다. 원본 전체 화면은 공개하지 않았고 결과 숫자·로그는 수정하지 않았다.

## 확인한 소스

- [등록 태스크](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_b/__init__.py)
- [Flat override](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_b/flat_env_cfg.py)
- [Rough·ANYmal-B 연결](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_b/rough_env_cfg.py)
- [기본 보행 환경 전체 Cfg](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py)
- [ANYmal 자산·actuator-net](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_assets/isaaclab_assets/robots/anymal.py)
- [발 공중 시간 보상](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/mdp/rewards.py)
- [속도 command와 화살표](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/commands/velocity_command.py)
