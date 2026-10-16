# 개념

[저장소 홈](../README.md) · [실습](../practice/README.md)

| 개념 | 핵심 내용 |
|---|---|
| [NVIDIA 생태계](00-overview/nvidia-ecosystem/README.md) | Isaac Sim·Isaac Lab·Omniverse·GR00T의 역할과 연결 |
| [물리·충돌·물성](01-simulation-basics/physics.md) | 형상에 질량·관성·마찰·반발을 더하는 방법 |
| [시뮬레이션 루프와 리셋](01-simulation-basics/simulation-loop.md) | 명령 전달·물리 진행·상태 갱신과 초기화 |
| [다중 환경과 선택 제어](01-simulation-basics/parallel-environments.md) | 환경 복제·배치와 일부 환경만 제어하는 방법 |
| [로봇 구조와 관절](02-robot-control-and-sensors/robot-models-and-sensors.md#articulation) | 링크와 관절로 연결된 로봇의 상태와 구동 |
| [PD·PID와 중력 보상](02-robot-control-and-sensors/pd-pid-gravity-compensation/README.md) | 오차를 줄이는 제어와 중력에 의한 처짐 보완 |
| [카메라와 RayCaster](02-robot-control-and-sensors/robot-models-and-sensors.md#sensors) | 색상·깊이 영상과 광선 교차점의 차이 |
| [토크와 접촉 힘](02-robot-control-and-sensors/robot-models-and-sensors.md#torque-contact) | 회전시키는 힘과 레버 길이·접촉의 관계 |
| [URDF와 USD](02-robot-control-and-sensors/robot-models-and-sensors.md#urdf) | 로봇 구조·물리 속성과 장면을 표현하는 형식 |
| [정기구학](02-robot-control-and-sensors/forward-kinematics/README.md) | 관절 상태로 손끝의 위치와 방향 구하기 |
| [역기구학](02-robot-control-and-sensors/inverse-kinematics/README.md) | 손끝 목표로 필요한 관절 움직임 구하기 |
| [상태 머신과 Pick & Place](02-robot-control-and-sensors/state-machine-pick-and-place/README.md) | 단계와 전환 조건으로 집기·옮기기 순서 구성 |
| [차동 구동](03-mobile-robots/differential-drive/README.md) | 좌우 바퀴 속도로 직진과 회전 만들기 |
| [오도메트리](03-mobile-robots/wheel-odometry/README.md) | 바퀴 회전으로 이동 거리와 방향 추정 |
| [Waypoint 주행](03-mobile-robots/waypoint-navigation/README.md) | 목표점과 현재 위치의 차이로 주행 보정 |
| [LiDAR](03-mobile-robots/lidar-scanning/README.md) | 주변 표면까지의 거리와 스캔 좌표계 이해 |
| [장애물 회피](03-mobile-robots/reactive-obstacle-avoidance/README.md) | 주변 거리에 따라 진행 방향을 바꾸는 규칙 |
| [강화학습 기초](04-reinforcement-learning/reinforcement-learning/01-foundations.md) | 행동의 결과를 경험하며 더 나은 동작을 배우는 과정 |
| [강화학습 환경·관측·행동·보상](04-reinforcement-learning/reinforcement-learning/02-environment-design.md) | 로봇이 보고·행동하고·점수를 받는 규칙 설계 |
| [강화학습 step과 피드백](04-reinforcement-learning/reinforcement-learning/03-step-feedback.md) | 관측 → 행동 → 물리 진행 → 다음 관측의 반복 |
| [PPO 학습](04-reinforcement-learning/reinforcement-learning/04-ppo-training.md) | 모은 경험으로 신경망 가중치를 개선하는 방법 |
| [Rollout·미니배치·epoch·iteration](04-reinforcement-learning/reinforcement-learning/05-rollout-and-minibatch.md) | 경험 수집과 반복 학습을 세는 단위 |
| [강화학습 흐름과 결과 확인](04-reinforcement-learning/reinforcement-learning/06-policy-evaluation.md) | 환경 구성에서 학습·실행·결과 비교까지의 흐름 |
| [보행](04-reinforcement-learning/legged-locomotion/README.md) | 관절 움직임과 발의 접촉으로 균형을 잡고 이동 |
| [Domain Shift](04-reinforcement-learning/domain-shift/README.md) | 학습 때와 실행 때 조건이 달라지는 현상 |
| [Domain Randomization](04-reinforcement-learning/domain-randomization/README.md) | 다양한 환경 조건을 경험하도록 설정하는 방법 |
| [휴머노이드 서기](05-humanoid-rl/humanoid-standing/README.md) | 몸의 자세와 관절을 조절해 균형 유지 |
| [모션 모방과 RSI](05-humanoid-rl/motion-imitation/README.md) | 기준 모션을 따라 배우고 다양한 시점에서 시작하는 방법 |
