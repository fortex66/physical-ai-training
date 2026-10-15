# 35번 코드 리뷰 — G1 휴머노이드 서기

사용자 ZIP의 Python4개는 보존했다. 기준 PinkWink commit `14f85fc6edece7cbb1faa50aa9fe3adef205e87a` 대비 35_1 기본 환경 수만64→100으로 바뀌었다.
강의41쪽·코드·영상·추가 최종 사진·TensorBoard2파일·checkpoint 메타데이터를 대조했다. Isaac Lab v2.3.2·RSL-RL v3.1.0 공개 소스를 참조했으며 실제 설치된 RSL-RL 버전은 확인되지 않았다. 클라우드에서 G1 물리 실행·재학습은 하지 않았다.

## 1. 공유 모듈은 정의를 모으지만 평가 일치가 자동 보장되지는 않는다

35_2·35_3은 `G1StandingEnvCfg`와 `make_ppo_runner_cfg()`를 공유한다. 관측120·행동37, 두 MLP `[128,64,32]`의 정의를 맞춘다.
35_1은 씬·행동만 재사용하고 관측/보상/종료를 비운 별도 Cfg다. 따라서 ‘정책만 다른 완전히 같은 환경’이라는 PDF4·17쪽 표현은 엄밀하지 않다.
35_1은 고정 bias+noise를 ±2 clip, 평가 랜덤은 독립 정규 샘플을 ±1 clip한다. 정량 대조는 같은35_3의 학습/랜덤 모드로 해야 한다.
공유 파일을 변경하면 과거 checkpoint와의 호환성이 깨질 수 있으므로 원래 Cfg 버전도 보존해야 한다.

## 2. 관측·행동·구동의 실제 의미

G1_MINIMAL_CFG는 최소 충돌 메시 자산을 쓰는 모델이며 v2.3.2는 self collision을 끈다. 37관절은 발/다리·허리·팔·손가락을 포함하며 특정 실물 G1 모델의 DOF와 동일하다고 일반화하지 않는다.
`3+3+3+37+37+37=120`이며 직접적인 절대 root 높이·목표 이동 명령·발 접촉력은 없다. 높이는 reward/termination에서 읽는 값이다.
`JointPositionActionCfg(scale=.25)`는 default 관절 위치+오프셋이고 hard clip이나 관절 속도 제한이 아니다. 학습 Gaussian 출력에는 ±1 clip이 자동 적용되지 않는다.
하위 구동은 implicit PD다. ANYmal의 별도 actuator-net과 구분한다. 200Hz 물리 substep 안에서 같은50Hz 목표를 유지하며 PD·접촉 물리를 계산한다.

## 3. 0.74m는 전체 신장이 아니다

높이 함수는 `robot.data.root_pos_w[:,2]`를 사용한다. 로봇 전체 키나 CoM을 계산하지 않는다.
`exp(-(z-.74)^2/.01)`의 10cm 오차에서 e^-1이며 높이가 조금 다르면 무조건0인 이진 성공 보상도 아니다.
일반 지형 높이 차이를 빼지 않은 월드 z이므로 높이가 다른 타일·플랫폼에 그대로 적용하려면 기준 높이를 재설계해야 한다.
정지 위치·yaw·root 수평 속도를 직접 유지하는 보상은 없으므로 이 보상만으로 ‘같은 자리에서 완전히 정지’를 보장하지 않는다.
기본 서기 자세에서 출발하고 낮은 높이/기울기로 조기 종료하므로 누운 상태에서 일어나는 get-up 학습과도 다르다.

## 4. PPO와 정규화·checkpoint

512환경×24step은12,288전이, 8미니배치면1,536개씩이다. 5epoch이므로 한 iteration당40optimizer step이며, 1000iteration이면12,288,000전이·설정상40,000optimizer step이다.
이전26번의 4미니배치·20회를 그대로 적용하면 안 된다. 초기 탐색 std는.5이며 학습 가능한 분포 파라미터다.
`init_at_random_ep_len=True`는 RSL-RL 참조 구현에서 episode_length_buf를 무작위 설정한다. 실제 자세를 무작위로 만들어 과거 상태부터 시뮬레이션하는 기능이 아니다.

`model_999.pt`를 zipfile+pickletools로만 정적으로 검사했다. Actor weight shape은 `(128,120),(64,128),(32,64),(37,32)`, Critic 끝층은 `(1,32)`다.
Actor/Critic 정규화의 mean/var/std/count와 optimizer_state_dict·iter·infos 키가 들어 있다. PDF36쪽의 ‘checkpoint에는 가중치만 저장’은 부정확하다.
평가 시 네트워크뿐 아니라 정규화 통계도 load해야 한다. `load_optimizer=False`는 평가에 불필요한 optimizer 복원을 생략한다.

## 5. 학습 로그 두 개를 합치지 않음

동일 logs 경로에 event `.12079.0`은0~22, `.12469.0`은0~999가 존재한다. 같은 iteration 축이 겹쳐 별도 run으로 분석했다. 완주 run만 곡선·1000행 CSV에 사용한다.
스크립트는 timestamp 없는 고정 디렉터리에 모델을 저장하므로 다시 학습하면 같은 model 번호를 덮어쓸 수 있다. 원본 ZIP과 SHA256 manifest를 보존했다.
각 checkpoint가 어느 짧은 run에서 왔는지 전부 추적할 수 있는 run ID는 없으므로 모든 모델이 단일 run 산출물이라고 추가 보장하지 않는다. 최종사진은 완주 run의999 지표와 일치한다.

`Episode_Reward`는 가중 보상 누적을 **최대 episode 시간5초**로 나눈 manager 로그다. episode 실제 길이로 나눈 평균이나 총보상 자체와 다르다.
`Train/mean_reward`는 Runner의 완료 episode 통계 버퍼다. 마지막 iteration의 term log 합×5와 수치가 가깝더라도 항상 같은 표본 평균이라는 보장은 없다.

## 6. 강의 예시를 이번 로그로 정정

- 최종 평균 보상77.8972, 길이250, 높이 term14.9859, action-rate-.1687, joint-velocity-.0366, joint-limit-.2006이다.
- PDF27쪽의 ‘joint_limits가0으로 수렴’은 첨부 run과 다르다. soft-limit 위반 패널티가 남는다. 원인 관절은 aggregate만으로 알 수 없다.
- 최종 엔트로피 -19.7037은 연속 분포의 differential entropy로 가능하다. 0을 탐색 종료의 공통 기준으로 삼지 않는다.
- surrogate loss가 음수이거나 value loss가 작다는 이유만으로 실제 정책 성능 개선·완벽한 Critic을 확정하지 않는다.
- FPS7022는 병렬 전이/s다. PDF의 예시12000FPS·수집.94초를 이 PC의 이번 실행 수치로 쓰지 않았다.

## 7. 10회 요청이 학습 평가에서는12회가 되는 이유

35_3은 while 조건으로만 전체 개수를 검사하고 같은 step의 done_envs를 전부 추가한다. 4환경이 동시에 끝나면4→8→12개가 된다. 요청10에 맞춰 안쪽에서 중단하지 않는다.
이번 학습 영상은 실제12회 전부250step, 랜덤 영상은10회 평균40.5step이다. 12개를 임의로10개로 잘라 보고하지 않았다.
병렬환경에서 먼저 종료된 N개 표본만 수집하는 편향도 남아 있다. 더 공정한 실험은 환경/seed/초기조건별 고정 할당량을 완료한다.

`success_threshold=int(250*.95)=237`이므로 코드 지표는237step(4.74초) 이상 비율이다. ‘5초 서있기’라는 표시는 timeout-only 판정과 다르다.
학습 모드의 `terminated=dones & ~truncated`는 동시 실패·timeout의 실패를 지울 수 있다. 실제 실패 없는 timeout은 별도 원래 플래그로 판정해야 한다.
평가는 기본 상태 reset이고 관측 corruption=False이며 이 예제에 별도의 reset 자세 랜덤화·질량 랜덤화·push 이벤트가 없다. 기본 reset_scene_to_default와 구분한다.
그래서 동일한 시작의 deterministic 평균 정책 결과가 반복될 수 있으며, 12회가 다양한 초기 상태의 독립 표본이라는 뜻은 아니다.

## 8. 토크 그래프·통계의 범위

G1 implicit actuator의 `applied_torque`는 Kp×위치오차+Kd×속도오차+feedforward를 계산하고 effort limit으로 clip한 근사값이다. PhysX 실제 모터 힘이나 힘 센서 측정값과 구분한다.
코드는 환경 step 후 마지막 substep 기준 근사 토크를 env0에서50Hz로 기록한다. 전체200Hz 물리 토크 이력을 저장하거나 평균하는 것은 아니다.
대상은 왼쪽 다리6개+torso1개이며 모든37관절 토크가 아니다. episode reset 뒤에도 직전 step 토크 표본을 기록하므로 경계의 값은 reset 전후 상태와 함께 해석해야 한다.
학습750표본·15초와 랜덤120표본·2.4초를 직접 비교했다는 점을 명시했다. 평균 절댓값·최댓값만으로 에너지·실물 모터 열부하를 계산할 수 없다.

출력 PNG 파일명이 모드와 무관하게 같아 마지막 실행 결과로 덮어쓴다. 첨부 PNG 제목은 random policy다. 그대로 보존하고 학습 토크는35-3 영상에서 별도 캡처했다.

## 근거 구현

- [Isaac Lab v2.3.2 G1·G1_MINIMAL_CFG](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_assets/isaaclab_assets/robots/unitree.py)
- [implicit PD·근사 effort](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/actuators/actuator_pd.py)
- [JointPositionAction 처리](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/actions/joint_actions.py)
- [RewardManager 로그](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
- [RSL-RL v3.1.0 OnPolicyRunner 학습·저장·추론](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/runners/on_policy_runner.py)
- [로그·모델 해시](analysis/log-manifest.json) · [정적 checkpoint 메타데이터](analysis/checkpoint-metadata.json)
