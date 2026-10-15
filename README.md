# Physical AI 학습 기록

Isaac Sim / Isaac Lab 강의를 따라 실습하면서 결과물과 배운 내용을 정리하는 저장소입니다.

## 학습 자료

- [PinkWink Isaac Sim 튜토리얼](https://github.com/PinkWink/isaacsim_tutorials)

이 저장소에는 실습 코드, 결과물과 학습 기록을 함께 남깁니다. 코드의 출처와 기준 버전은 각 실습 문서에 기록합니다.

## 공통 실습 환경

실습용 로컬 PC의 사양과 실행 환경입니다. 공통 정보는 이 페이지에서 관리합니다.

### PC 사양

| 항목 | 사양 |
|---|---|
| 모델 | HP Victus by HP Gaming Laptop 15-fa1xxx |
| CPU | 13th Gen Intel Core i7-13620H · 논리 프로세서 16개 표시 |
| 메모리 | 32.0 GiB |
| NVIDIA GPU | NVIDIA GeForce RTX 4060 Laptop GPU |
| 내장 GPU | Intel Graphics (RPL-P) |
| 디스크 용량 | 1.0 TB |
| 펌웨어 | F.18 |

### 소프트웨어 환경

| 항목 | 환경 |
| --- | --- |
| OS | Ubuntu 24.04.5 LTS · 64-bit |
| 커널 | Linux 7.0.0-38-generic |
| 데스크톱 | GNOME 46 · X11 |
| Isaac Sim | 5.1.0 |
| Isaac Lab | 2.3.2 |
| Python | 3.11 |
| 가상환경 | `~/isaac/env_isaaclab` |
| 튜토리얼 경로 | `~/isaac/isaacsim_tutorials` |
| 그래프 표시 | matplotlib · TkAgg |

### 공통 실행 준비

```bash
source ~/isaac/env_isaaclab/bin/activate
```

이후 각 실습 폴더로 이동해 해당 Python 파일을 실행합니다. 스크립트는 하나씩 실행하고 앞선 실행을 종료한 뒤 다음 예제를 시작합니다.

## 개념 학습

- [NVIDIA 생태계](learning-notes/nvidia-ecosystem/README.md): 전체 구성도 및 자료
- [PD·PID 제어와 중력 보상](learning-notes/pd-pid-gravity-compensation/README.md): 각 제어 항의 역할, PD의 정상상태 오차, 중력 보상과 06번 실습의 연결

지금까지의 핵심 개념은 아래에서 주제별로 볼 수 있습니다. 각 실습 페이지의 이론 설명도 유지합니다.

| 핵심 개념 | 핵심 내용 | 개념 정리 |
|---|---|---|
| 물리 설정 · 03~04 | 형상에 강체·충돌·질량·관성·마찰·반발 속성을 더해 운동을 구성 | [물리 설정](learning-notes/robotics-core-concepts/README.md#physics) |
| 루프·리셋 · 04·07 | 명령 전달 → 물리 진행 → 상태 갱신, 자세와 속도를 함께 초기화 | [시간과 리셋](learning-notes/robotics-core-concepts/README.md#loop-reset) |
| Articulation · 05~06 | 관절로 연결된 링크의 상태와 구동 명령 관리 | [로봇 관절 구조](learning-notes/robotics-core-concepts/README.md#articulation) |
| 다중 환경 · 07~08 | 환경 자동 복제·배치, `env_ids`로 특정 환경 선택 제어 | [다중 환경](learning-notes/robotics-core-concepts/README.md#parallel-envs) |
| 센서 · 09~10 | RGB·Depth 영상과 광선 교차점의 의미·좌표계 구분 | [카메라와 RayCaster](learning-notes/robotics-core-concepts/README.md#sensors) |
| 토크·접촉 힘 · 11 | 같은 토크에서도 레버 길이에 따라 전달 힘이 달라짐 | [레버와 ContactSensor](learning-notes/robotics-core-concepts/README.md#torque-contact) |
| URDF·USD · 11 | 링크·관절·물리 속성을 기술하고 시뮬레이션 자산으로 변환 | [모델 형식](learning-notes/robotics-core-concepts/README.md#urdf) |
| 정기구학 · 12 | 관절 상태 → 말단의 위치·방향, 좌표계와 TCP 고려 | [정기구학 개념](learning-notes/forward-kinematics/README.md) |
| 역기구학 · 13 | 말단 목표 → 관절 목표, Jacobian과 DLS로 반복 계산 | [IK·Jacobian·DLS](learning-notes/inverse-kinematics/README.md) |
| 상태 머신 · 14 | 단계별 IK 목표·그리퍼 명령·전환 조건으로 작업 순서 구성 | [상태 머신·Pick & Place](learning-notes/state-machine-pick-and-place/README.md) |
| 차동 구동 · 15 | 선속도·각속도 명령을 좌우 바퀴 각속도로 변환 | [차동 구동·유니사이클](learning-notes/differential-drive/README.md) |
| 오도메트리 · 16 | 바퀴 회전량으로 위치·방향 추정, 실제 위치와 오차 비교 | [오도메트리·비홀로노믹 주행](learning-notes/wheel-odometry/README.md) |
| Waypoint 제어 · 17 | 목표 거리·방향 오차로 속도 보정, 도달 시 다음 목표 선택 | [P 제어·내비게이션](learning-notes/waypoint-navigation/README.md) |
| 2D LiDAR · 18 | 광선 교차점에서 거리 계산, 월드 지도와 센서 기준 스캔 비교 | [LiDAR 스캔·좌표계](learning-notes/lidar-scanning/README.md) |
| 장애물 회피 · 19 | 장애물 거리로 목표 추적·회피 전환, 실제 우회 궤적 확인 | [반응형 회피](learning-notes/reactive-obstacle-avoidance/README.md) |
| 강화학습 기초 · 20~29 | Policy·Critic·PPO, step 피드백·관측·보상·액션·종료 구분 | [강화학습 개념](learning-notes/reinforcement-learning/README.md) · [step 피드백](learning-notes/reinforcement-learning/README.md#step-feedback) · [학습 반복·미니배치](learning-notes/reinforcement-learning/README.md#ppo-training-cycle) · [구성도 모음](learning-notes/reinforcement-learning/diagrams/README.md) |
| 다족 보행 · 26 | 지지·유각기, 속도 명령·관절 제어·접촉·보상 | [보행 개념](learning-notes/legged-locomotion/README.md) |
| Domain Shift · 28 | 지형 변화·관측 분포·일반화·추가 학습·공정한 평가 | [Domain Shift와 강화학습](learning-notes/domain-shift/README.md) |
| Domain Randomization · 29 | 환경 조건의 다양화·이벤트 시점·PPO 연결·강건성 평가 | [도메인 랜덤화](learning-notes/domain-randomization/README.md) |
| 휴머노이드 서기 · 35 | G1 균형·관절 목표와 PD·보상·PPO·학습/랜덤 평가 | [휴머노이드 서기](learning-notes/humanoid-standing/README.md) |

## 실습 기록

| 강좌 | 내용 | 기록 |
|---|---|---|
| 03 | 갈릴레오 자유낙하 실험 | [실험 조건·결과·영상·배운 점](03-galileo/README.md) · [코드](03-galileo/03_galileo_experiment.py) |
| 04 | 시뮬레이션 루프와 탄성 비교 · 강체 리셋 수정 | [실험 결과·수정 이유·영상](04-simulation-loop/README.md) · [수정된 코드](04-simulation-loop/04_simulation_loop.py) |
| 05 | Franka Panda 로봇 배치 · 랜덤 관절 입력 · 상태 읽기와 리셋 | [실습 결과·영상·배운 점](05-spawn-robot/README.md) · [코드](05-spawn-robot/05_spawn_robot.py) |
| 06 | 관절 위치 제어 · 중력 보상 · 손끝 위치 마커 비교 | [세 실습 결과·영상·코드](06-robot-joint-control/README.md) |
| 07 | InteractiveScene · 환경 자동 복제 · 4개/16개 환경 비교 | [실습 결과·환경 자동 배치·코드](07-scene-design/README.md) |
| 08 | 다중 로봇 · 초기 자세 설정 · 특정 환경 선택 제어 | [실습 결과·선택 제어·코드](08-multi-robot/README.md) |
| 09 | RGB·Depth 카메라 · 실시간 표시 · 레일 카메라 궤도 촬영 | [실습 결과·카메라 데이터·코드](09-camera-sensor/README.md) |
| 10 | RayCaster · 격자 광선 · 계단 높이 단면 스캔 | [실습 결과·측정 원리·코드](10-ray-caster/README.md) |
| 11 | 토크·레버·접촉 힘 비교 · URDF 모델 구성 | [실습 결과·URDF 설명·코드·모델](11-torque-lever-contact/README.md) |
| 12 | 정기구학 · 관절 구성별 말단 위치·방향 · 좌표 프레임 표시 | [실습 결과·정기구학 설명·코드](12-forward-kinematics/README.md) |
| 13 | 미분 역기구학 · Jacobian·DLS · 목표 포즈 추종 | [실습 결과·오차 비교·코드](13-differential-ik/README.md) |
| 14 | IK + 상태 머신 · 그리퍼 제어 · Pick & Place | [실습 결과·7단계 작업·코드](14-pick-and-place/README.md) |
| 15 | JetBot 배치 · 차동 구동 · 전진·회전·원호 주행 | [실습 결과·바퀴 속도 변환·코드](15-spawn-mobile-robot/README.md) |
| 16 | JetBot 경로 패턴 · 바퀴 오도메트리 · 위치 오차 비교 | [실습 결과·위치 추정·코드](16-mobile-base-control/README.md) |
| 17 | JetBot Waypoint 내비게이션 · P 제어 · 사각형 순환 | [실습 결과·피드백 제어·코드](17-mobile-navigation/README.md) |
| 18 | JetBot 미로 주행 · 360° LiDAR · 지도·극좌표 스캔 | [실습 결과·거리 측정·코드](18-lidar-maze/README.md) |
| 19 | JetBot 거리 기반 장애물 회피 · NAV·AVOID · 실제 궤적 기록 | [실습 결과·회피 제어·코드](19-obstacle-avoidance/README.md) |
| 20 | 강화학습 환경 기초 · Cartpole 랜덤 행동 · 관측·보상·종료·리셋 | [실습 결과](20-base-env/README.md) · [코드 리뷰](20-base-env/code-review.md) · [코드](20-base-env/20_base_env.py) |
| 21 | 커스텀 관측·보상 · sin/cos·정규화 · 항별 보상 해석 | [실습 결과](21-observation-reward/README.md) · [코드 리뷰](21-observation-reward/code-review.md) · [코드](21-observation-reward/21_observation_reward.py) |
| 22 | 액션 공간 · 힘/위치/속도 명령 · scale·offset·actuator 연결 | [실습 결과](22-action-space/README.md) · [코드 리뷰](22-action-space/code-review.md) · [코드](22-action-space/22_action_space.py) |
| 23 | 커스텀 RL 환경 완성 · 막대 실패 종료 · 학습 전 baseline | [실습 결과](23-custom-env-complete/README.md) · [코드 리뷰](23-custom-env-complete/code-review.md) · [코드](23-custom-env-complete/23_custom_env_complete.py) |
| 24 | Cartpole PPO 학습 · Actor·Critic·GAE · 실제 곡선·체크포인트 | [실습 결과·학습 구조](24-train-cartpole/README.md) · [코드 리뷰](24-train-cartpole/code-review.md) · [코드](24-train-cartpole/24_train_cartpole.py) |
| 25 | 학습 정책 vs 랜덤 평가 · deterministic 추론 · RL 워크플로우 마무리 | [실습 결과·비교](25-evaluate-policy/README.md) · [코드 리뷰](25-evaluate-policy/code-review.md) · [코드](25-evaluate-policy/25_evaluate_policy.py) |
| 26 | ANYmal 보행 PPO · 속도 추적·지지/유각기·관절 목표·접촉 보상 | [실습 결과·보행 개념·학습 곡선](26-train-locomotion/README.md) · [코드 리뷰](26-train-locomotion/code-review.md) · [코드](26-train-locomotion/26_train_locomotion.py) |
| 27 | 학습된 ANYmal 정책 평가 · 평균 행동·명령 추적·생존 지표 검토 | [실습 결과](27-evaluate-locomotion/README.md) · [코드 리뷰](27-evaluate-locomotion/code-review.md) · [코드](27-evaluate-locomotion/27_evaluate_locomotion.py) |
| 28 | 혼합 지형 생성 · 고정 보행 정책 · Domain Shift와 일반화 | [실습 결과](28-terrain-generation/README.md) · [코드 리뷰](28-terrain-generation/code-review.md) · [코드](28-terrain-generation/28_terrain_generation.py) |
| 29 | Domain Randomization · 질량·초기 상태·이벤트 타이머 검토 | [실습 결과](29-domain-randomization/README.md) · [코드 리뷰](29-domain-randomization/code-review.md) · [코드](29-domain-randomization/29_domain_randomization.py) |
| 35 | G1 휴머노이드 서기 · PPO·학습/랜덤 평가·PD 근사 토크 | [실습 결과·학습 곡선](35-g1-standing/README.md) · [코드 리뷰](35-g1-standing/code-review.md) · [공유 환경 코드](35-g1-standing/g1_standing_env.py) |

[학습 기록 작성 기준](CONTRIBUTING.md)
