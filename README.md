# Physical AI 학습 기록

Isaac Sim / Isaac Lab 교육에서 배운 개념과 실습 결과, 느낀 점을 정리했습니다.

## 개념

| 개념 | 핵심 내용 |
|---|---|
| [NVIDIA 생태계](learning-notes/00-overview/nvidia-ecosystem/README.md) | Isaac Sim·Isaac Lab·Omniverse·GR00T의 역할과 연결 |
| [물리·충돌·물성](learning-notes/01-simulation-basics/physics.md) | 형상에 질량·관성·마찰·반발을 더하는 방법 |
| [시뮬레이션 루프와 리셋](learning-notes/01-simulation-basics/simulation-loop.md) | 명령 전달·물리 진행·상태 갱신과 초기화 |
| [다중 환경과 선택 제어](learning-notes/01-simulation-basics/parallel-environments.md) | 환경 복제·배치와 일부 환경만 제어하는 방법 |
| [로봇 구조와 관절](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#articulation) | 링크와 관절로 연결된 로봇의 상태와 구동 |
| [PD·PID와 중력 보상](learning-notes/02-robot-control-and-sensors/pd-pid-gravity-compensation/README.md) | 오차를 줄이는 제어와 중력에 의한 처짐 보완 |
| [카메라와 RayCaster](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#sensors) | 색상·깊이 영상과 광선 교차점의 차이 |
| [토크와 접촉 힘](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#torque-contact) | 회전시키는 힘과 레버 길이·접촉의 관계 |
| [URDF와 USD](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#urdf) | 로봇 구조·물리 속성과 장면을 표현하는 형식 |
| [정기구학](learning-notes/02-robot-control-and-sensors/forward-kinematics/README.md) | 관절 상태로 손끝의 위치와 방향 구하기 |
| [역기구학](learning-notes/02-robot-control-and-sensors/inverse-kinematics/README.md) | 손끝 목표로 필요한 관절 움직임 구하기 |
| [상태 머신과 Pick & Place](learning-notes/02-robot-control-and-sensors/state-machine-pick-and-place/README.md) | 단계와 전환 조건으로 집기·옮기기 순서 구성 |
| [차동 구동](learning-notes/03-mobile-robots/differential-drive/README.md) | 좌우 바퀴 속도로 직진과 회전 만들기 |
| [오도메트리](learning-notes/03-mobile-robots/wheel-odometry/README.md) | 바퀴 회전으로 이동 거리와 방향 추정 |
| [Waypoint 주행](learning-notes/03-mobile-robots/waypoint-navigation/README.md) | 목표점과 현재 위치의 차이로 주행 보정 |
| [LiDAR](learning-notes/03-mobile-robots/lidar-scanning/README.md) | 주변 표면까지의 거리와 스캔 좌표계 이해 |
| [장애물 회피](learning-notes/03-mobile-robots/reactive-obstacle-avoidance/README.md) | 주변 거리에 따라 진행 방향을 바꾸는 규칙 |
| [강화학습 기초](learning-notes/04-reinforcement-learning/reinforcement-learning/01-foundations.md) | 행동의 결과를 경험하며 더 나은 동작을 배우는 과정 |
| [강화학습 환경·관측·행동·보상](learning-notes/04-reinforcement-learning/reinforcement-learning/02-environment-design.md) | 로봇이 보고·행동하고·점수를 받는 규칙 설계 |
| [강화학습 step과 피드백](learning-notes/04-reinforcement-learning/reinforcement-learning/03-step-feedback.md) | 관측 → 행동 → 물리 진행 → 다음 관측의 반복 |
| [PPO 학습](learning-notes/04-reinforcement-learning/reinforcement-learning/04-ppo-training.md) | 모은 경험으로 신경망 가중치를 개선하는 방법 |
| [Rollout·미니배치·epoch·iteration](learning-notes/04-reinforcement-learning/reinforcement-learning/05-rollout-and-minibatch.md) | 경험 수집과 반복 학습을 세는 단위 |
| [강화학습 흐름과 결과 확인](learning-notes/04-reinforcement-learning/reinforcement-learning/06-policy-evaluation.md) | 환경 구성에서 학습·실행·결과 비교까지의 흐름 |
| [보행](learning-notes/04-reinforcement-learning/legged-locomotion/README.md) | 관절 움직임과 발의 접촉으로 균형을 잡고 이동 |
| [Domain Shift](learning-notes/04-reinforcement-learning/domain-shift/README.md) | 학습 때와 실행 때 조건이 달라지는 현상 |
| [Domain Randomization](learning-notes/04-reinforcement-learning/domain-randomization/README.md) | 다양한 환경 조건을 경험하도록 설정하는 방법 |
| [휴머노이드 서기](learning-notes/05-humanoid-rl/humanoid-standing/README.md) | 몸의 자세와 관절을 조절해 균형 유지 |
| [모션 모방과 RSI](learning-notes/05-humanoid-rl/motion-imitation/README.md) | 기준 모션을 따라 배우고 다양한 시점에서 시작하는 방법 |

## 실습

### 시뮬레이션 기초

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 03 | [갈릴레오 자유낙하 실험](practice/01-simulation-basics/03-galileo/README.md) | 질량이 다른 두 공의 낙하 시간을 비교한다. |
| 04 | [시뮬레이션 루프와 탄성 실험](practice/01-simulation-basics/04-simulation-loop/README.md) | 반발 계수에 따른 튀는 높이와 리셋 동작을 확인한다. |

### 로봇 제어 및 센서

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 05 | [로봇 불러오기](practice/02-robot-control-and-sensors/05-spawn-robot/README.md) | Franka 로봇을 배치하고 관절 상태를 읽는다. |
| 06 | [관절 제어와 중력 보상](practice/02-robot-control-and-sensors/06-robot-joint-control/README.md) | 관절 각도를 조절하고 중력 보상 전후를 비교한다. |
| 07 | [여러 환경 만들기](practice/02-robot-control-and-sensors/07-scene-design/README.md) | 환경 수를 바꿔 여러 실습 공간을 자동으로 배치한다. |
| 08 | [여러 로봇과 선택 제어](practice/02-robot-control-and-sensors/08-multi-robot/README.md) | 여러 로봇을 배치하고 특정 환경만 골라 제어한다. |
| 09 | [RGB·Depth 카메라](practice/02-robot-control-and-sensors/09-camera-sensor/README.md) | 카메라로 색상 영상과 깊이 정보를 받아본다. |
| 10 | [RayCaster 높이 측정](practice/02-robot-control-and-sensors/10-ray-caster/README.md) | 광선을 쏘아 계단 표면의 높이를 측정한다. |
| 11 | [토크·접촉 힘과 URDF](practice/02-robot-control-and-sensors/11-torque-lever-contact/README.md) | 레버 길이에 따른 접촉 힘을 비교하고 URDF를 살펴본다. |
| 12 | [정기구학](practice/02-robot-control-and-sensors/12-forward-kinematics/README.md) | 관절 각도가 바뀔 때 로봇 손끝의 위치와 방향을 확인한다. |
| 13 | [역기구학](practice/02-robot-control-and-sensors/13-differential-ik/README.md) | 손끝 목표 위치와 방향에 맞는 관절 움직임을 계산한다. |
| 14 | [Pick & Place](practice/02-robot-control-and-sensors/14-pick-and-place/README.md) | 접근·잡기·이동·놓기 순서로 물체를 옮긴다. |

### 모바일 로봇

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 15 | [모바일 로봇과 차동 구동](practice/03-mobile-robots/15-spawn-mobile-robot/README.md) | 좌우 바퀴 속도를 바꿔 직진·회전·원호 주행을 만든다. |
| 16 | [경로 주행과 오도메트리](practice/03-mobile-robots/16-mobile-base-control/README.md) | 경로를 따라 주행하고 바퀴 회전으로 위치를 추정한다. |
| 17 | [Waypoint 주행](practice/03-mobile-robots/17-mobile-navigation/README.md) | 목표점까지의 거리와 방향을 이용해 주행한다. |
| 18 | [LiDAR와 미로 주행](practice/03-mobile-robots/18-lidar-maze/README.md) | 미로를 주행하며 주변 장애물의 거리를 시각화한다. |
| 19 | [장애물 회피](practice/03-mobile-robots/19-obstacle-avoidance/README.md) | 장애물과의 거리에 따라 목표 추적과 회피를 전환한다. |

### 강화학습 환경

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 20 | [강화학습 환경 기초](practice/04-reinforcement-learning/20-base-env/README.md) | 랜덤 행동으로 관측·보상·종료·리셋 흐름을 확인한다. |
| 21 | [관측과 보상](practice/04-reinforcement-learning/21-observation-reward/README.md) | 관측 정보를 구성하고 보상 항목을 직접 만든다. |
| 22 | [행동 공간](practice/04-reinforcement-learning/22-action-space/README.md) | 같은 행동 값을 힘·위치·속도 명령으로 적용해본다. |
| 23 | [강화학습 환경 만들기](practice/04-reinforcement-learning/23-custom-env-complete/README.md) | 관측·행동·보상·종료 조건을 모아 환경을 완성한다. |
| 24 | [Cartpole 강화학습](practice/04-reinforcement-learning/24-train-cartpole/README.md) | PPO로 Cartpole 균형 유지를 학습하고 변화를 살펴본다. |
| 25 | [Cartpole 결과 비교](practice/04-reinforcement-learning/25-evaluate-policy/README.md) | 학습한 동작과 랜덤 행동의 균형 유지 결과를 비교한다. |
| 26 | [4족 로봇 보행 학습](practice/04-reinforcement-learning/26-train-locomotion/README.md) | ANYmal이 속도 명령에 맞춰 걷도록 학습한다. |
| 27 | [4족 로봇 보행 결과](practice/04-reinforcement-learning/27-evaluate-locomotion/README.md) | 학습된 ANYmal의 보행과 넘어지는 상황을 확인한다. |
| 28 | [다양한 지형과 Domain Shift](practice/04-reinforcement-learning/28-terrain-generation/README.md) | 지형이 달라졌을 때 보행이 어떻게 바뀌는지 확인한다. |
| 29 | [Domain Randomization](practice/04-reinforcement-learning/29-domain-randomization/README.md) | 질량·초기 상태·외란 등 환경 조건을 바꿔본다. |

### 휴머노이드 강화학습

| 강좌 | 실습 | 간략한 내용 |
|---|---|---|
| 35 | [휴머노이드 서기](practice/05-humanoid-rl/35-g1-standing/README.md) | G1이 넘어지지 않고 서 있도록 균형 유지를 학습한다. |
| 36 | [휴머노이드 보행과 모션 모방](practice/05-humanoid-rl/36-g1-motion-imitation/README.md) | G1의 모션 추종을 학습하고 쿵푸 동작의 어려움을 살펴본다. |

## 공통 실습 환경

실습용 로컬 PC의 사양과 실행 환경입니다. 공통 정보는 이 페이지에서 관리합니다.

### PC 사양

| 항목 | 사양 |
|---|---|
| 모델 | HP Victus by HP Gaming Laptop 15-fa1xxx |
| CPU | 13th Gen Intel Core i7-13620H · 논리 프로세서 16개 표시 |
| 메모리 | 32.0 GiB |
| NVIDIA GPU | NVIDIA GeForce RTX 4060 Laptop GPU · nvidia-smi 총메모리 8188MiB 표시 |
| 내장 GPU | Intel Graphics (RPL-P) |
| 디스크 용량 | 1.0 TB |
| 펌웨어 | F.18 |

### 소프트웨어 환경

| 항목 | 환경 |
| --- | --- |
| OS | Ubuntu 24.04.5 LTS · 64-bit |
| 커널 | Linux 7.0.0-38-generic |
| 데스크톱 | GNOME 46 · X11 |
| NVIDIA 드라이버 | 580.178.04 |
| Isaac Sim | 5.1.0 |
| Isaac Lab | 2.3.2 |
| Python | 3.11 |
| 가상환경 | `~/isaac/env_isaaclab` |
| 튜토리얼 경로 | `~/isaac/isaacsim_tutorials` |
| 그래프 표시 | matplotlib · TkAgg |

`nvidia-smi`의 CUDA Version 13.0 표시는 드라이버의 지원 수준이며, 설치된 CUDA Toolkit·PyTorch CUDA 런타임 버전을 확인한 값은 아닙니다.

### 공통 실행 준비

```bash
source ~/isaac/env_isaaclab/bin/activate
```

이후 각 실습 폴더로 이동해 해당 Python 파일을 실행합니다. 스크립트는 하나씩 실행하고 앞선 실행을 종료한 뒤 다음 예제를 시작합니다.

## 학습 자료

- [PinkWink Isaac Sim 튜토리얼](https://github.com/PinkWink/isaacsim_tutorials)
- [학습 기록 작성 기준](CONTRIBUTING.md)

코드의 출처와 기준 버전은 각 실습 문서에 기록합니다.
