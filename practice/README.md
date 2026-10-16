# 실습

[저장소 홈](../README.md) · [개념](../learning-notes/README.md)

## 시뮬레이션 기초

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 03 | [갈릴레오 자유낙하 실험](01-simulation-basics/03-galileo/README.md) | 질량이 다른 두 공의 낙하 시간을 비교한다. |
| 04 | [시뮬레이션 루프와 탄성 실험](01-simulation-basics/04-simulation-loop/README.md) | 반발 계수에 따른 튀는 높이와 리셋 동작을 확인한다. |

## 로봇 제어 및 센서

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 05 | [로봇 불러오기](02-robot-control-and-sensors/05-spawn-robot/README.md) | Franka 로봇을 배치하고 관절 상태를 읽는다. |
| 06 | [관절 제어와 중력 보상](02-robot-control-and-sensors/06-robot-joint-control/README.md) | 관절 각도를 조절하고 중력 보상 전후를 비교한다. |
| 07 | [여러 환경 만들기](02-robot-control-and-sensors/07-scene-design/README.md) | 환경 수를 바꿔 여러 실습 공간을 자동으로 배치한다. |
| 08 | [여러 로봇과 선택 제어](02-robot-control-and-sensors/08-multi-robot/README.md) | 여러 로봇을 배치하고 특정 환경만 골라 제어한다. |
| 09 | [RGB·Depth 카메라](02-robot-control-and-sensors/09-camera-sensor/README.md) | 카메라로 색상 영상과 깊이 정보를 받아본다. |
| 10 | [RayCaster 높이 측정](02-robot-control-and-sensors/10-ray-caster/README.md) | 광선을 쏘아 계단 표면의 높이를 측정한다. |
| 11 | [토크·접촉 힘과 URDF](02-robot-control-and-sensors/11-torque-lever-contact/README.md) | 레버 길이에 따른 접촉 힘을 비교하고 URDF를 살펴본다. |
| 12 | [정기구학](02-robot-control-and-sensors/12-forward-kinematics/README.md) | 관절 각도가 바뀔 때 로봇 손끝의 위치와 방향을 확인한다. |
| 13 | [역기구학](02-robot-control-and-sensors/13-differential-ik/README.md) | 손끝 목표 위치와 방향에 맞는 관절 움직임을 계산한다. |
| 14 | [Pick & Place](02-robot-control-and-sensors/14-pick-and-place/README.md) | 접근·잡기·이동·놓기 순서로 물체를 옮긴다. |

## 모바일 로봇

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 15 | [모바일 로봇과 차동 구동](03-mobile-robots/15-spawn-mobile-robot/README.md) | 좌우 바퀴 속도를 바꿔 직진·회전·원호 주행을 만든다. |
| 16 | [경로 주행과 오도메트리](03-mobile-robots/16-mobile-base-control/README.md) | 경로를 따라 주행하고 바퀴 회전으로 위치를 추정한다. |
| 17 | [Waypoint 주행](03-mobile-robots/17-mobile-navigation/README.md) | 목표점까지의 거리와 방향을 이용해 주행한다. |
| 18 | [LiDAR와 미로 주행](03-mobile-robots/18-lidar-maze/README.md) | 미로를 주행하며 주변 장애물의 거리를 시각화한다. |
| 19 | [장애물 회피](03-mobile-robots/19-obstacle-avoidance/README.md) | 장애물과의 거리에 따라 목표 추적과 회피를 전환한다. |

## 강화학습 환경

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 20 | [강화학습 환경 기초](04-reinforcement-learning/20-base-env/README.md) | 랜덤 행동으로 관측·보상·종료·리셋 흐름을 확인한다. |
| 21 | [관측과 보상](04-reinforcement-learning/21-observation-reward/README.md) | 관측 정보를 구성하고 보상 항목을 직접 만든다. |
| 22 | [행동 공간](04-reinforcement-learning/22-action-space/README.md) | 같은 행동 값을 힘·위치·속도 명령으로 적용해본다. |
| 23 | [강화학습 환경 만들기](04-reinforcement-learning/23-custom-env-complete/README.md) | 관측·행동·보상·종료 조건을 모아 환경을 완성한다. |
| 24 | [Cartpole 강화학습](04-reinforcement-learning/24-train-cartpole/README.md) | PPO로 Cartpole 균형 유지를 학습하고 변화를 살펴본다. |
| 25 | [Cartpole 결과 비교](04-reinforcement-learning/25-evaluate-policy/README.md) | 학습한 동작과 랜덤 행동의 균형 유지 결과를 비교한다. |
| 26 | [4족 로봇 보행 학습](04-reinforcement-learning/26-train-locomotion/README.md) | ANYmal이 속도 명령에 맞춰 걷도록 학습한다. |
| 27 | [4족 로봇 보행 결과](04-reinforcement-learning/27-evaluate-locomotion/README.md) | 학습된 ANYmal의 보행과 넘어지는 상황을 확인한다. |
| 28 | [다양한 지형과 Domain Shift](04-reinforcement-learning/28-terrain-generation/README.md) | 지형이 달라졌을 때 보행이 어떻게 바뀌는지 확인한다. |
| 29 | [Domain Randomization](04-reinforcement-learning/29-domain-randomization/README.md) | 질량·초기 상태·외란 등 환경 조건을 바꿔본다. |

## 휴머노이드 강화학습

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 35 | [휴머노이드 서기](05-humanoid-rl/35-g1-standing/README.md) | G1이 넘어지지 않고 서 있도록 균형 유지를 학습한다. |
| 36 | [휴머노이드 보행과 모션 모방](05-humanoid-rl/36-g1-motion-imitation/README.md) | G1의 모션 추종을 학습하고 쿵푸 동작의 어려움을 살펴본다. |
