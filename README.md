# Physical AI 학습 기록

Isaac Sim / Isaac Lab 교육에서 배운 개념과 실습 결과, 느낀 점을 정리했습니다.

## 개념

- [NVIDIA 생태계](learning-notes/00-overview/nvidia-ecosystem/README.md)
- [물리·충돌·물성](learning-notes/01-simulation-basics/physics.md)
- [시뮬레이션 루프와 리셋](learning-notes/01-simulation-basics/simulation-loop.md)
- [다중 환경과 선택 제어](learning-notes/01-simulation-basics/parallel-environments.md)
- [로봇 구조와 관절](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#articulation)
- [PD·PID와 중력 보상](learning-notes/02-robot-control-and-sensors/pd-pid-gravity-compensation/README.md)
- [카메라와 RayCaster](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#sensors)
- [토크와 접촉 힘](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#torque-contact)
- [URDF와 USD](learning-notes/02-robot-control-and-sensors/robot-models-and-sensors.md#urdf)
- [정기구학](learning-notes/02-robot-control-and-sensors/forward-kinematics/README.md)
- [역기구학](learning-notes/02-robot-control-and-sensors/inverse-kinematics/README.md)
- [상태 머신과 Pick & Place](learning-notes/02-robot-control-and-sensors/state-machine-pick-and-place/README.md)
- [차동 구동](learning-notes/03-mobile-robots/differential-drive/README.md)
- [오도메트리](learning-notes/03-mobile-robots/wheel-odometry/README.md)
- [Waypoint 주행](learning-notes/03-mobile-robots/waypoint-navigation/README.md)
- [LiDAR](learning-notes/03-mobile-robots/lidar-scanning/README.md)
- [장애물 회피](learning-notes/03-mobile-robots/reactive-obstacle-avoidance/README.md)
- [강화학습 기초](learning-notes/04-reinforcement-learning/reinforcement-learning/01-foundations.md)
- [강화학습 환경·관측·행동·보상](learning-notes/04-reinforcement-learning/reinforcement-learning/02-environment-design.md)
- [강화학습 step과 피드백](learning-notes/04-reinforcement-learning/reinforcement-learning/03-step-feedback.md)
- [PPO 학습](learning-notes/04-reinforcement-learning/reinforcement-learning/04-ppo-training.md)
- [Rollout·미니배치·epoch·iteration](learning-notes/04-reinforcement-learning/reinforcement-learning/05-rollout-and-minibatch.md)
- [강화학습 흐름과 결과 확인](learning-notes/04-reinforcement-learning/reinforcement-learning/06-policy-evaluation.md)
- [보행](learning-notes/04-reinforcement-learning/legged-locomotion/README.md)
- [Domain Shift](learning-notes/04-reinforcement-learning/domain-shift/README.md)
- [Domain Randomization](learning-notes/04-reinforcement-learning/domain-randomization/README.md)
- [휴머노이드 서기](learning-notes/05-humanoid-rl/humanoid-standing/README.md)
- [모션 모방과 RSI](learning-notes/05-humanoid-rl/motion-imitation/README.md)

## 실습

### 시뮬레이션 기초

| 강좌 | 실습 |
|---|---|
| 03 | [갈릴레오 자유낙하 실험](practice/01-simulation-basics/03-galileo/README.md) |
| 04 | [시뮬레이션 루프와 탄성 실험](practice/01-simulation-basics/04-simulation-loop/README.md) |

### 로봇 제어 및 센서

| 강좌 | 실습 |
|---|---|
| 05 | [로봇 불러오기](practice/02-robot-control-and-sensors/05-spawn-robot/README.md) |
| 06 | [관절 제어와 중력 보상](practice/02-robot-control-and-sensors/06-robot-joint-control/README.md) |
| 07 | [여러 환경 만들기](practice/02-robot-control-and-sensors/07-scene-design/README.md) |
| 08 | [여러 로봇과 선택 제어](practice/02-robot-control-and-sensors/08-multi-robot/README.md) |
| 09 | [RGB·Depth 카메라](practice/02-robot-control-and-sensors/09-camera-sensor/README.md) |
| 10 | [RayCaster 높이 측정](practice/02-robot-control-and-sensors/10-ray-caster/README.md) |
| 11 | [토크·접촉 힘과 URDF](practice/02-robot-control-and-sensors/11-torque-lever-contact/README.md) |
| 12 | [정기구학](practice/02-robot-control-and-sensors/12-forward-kinematics/README.md) |
| 13 | [역기구학](practice/02-robot-control-and-sensors/13-differential-ik/README.md) |
| 14 | [Pick & Place](practice/02-robot-control-and-sensors/14-pick-and-place/README.md) |

### 모바일 로봇

| 강좌 | 실습 |
|---|---|
| 15 | [모바일 로봇과 차동 구동](practice/03-mobile-robots/15-spawn-mobile-robot/README.md) |
| 16 | [경로 주행과 오도메트리](practice/03-mobile-robots/16-mobile-base-control/README.md) |
| 17 | [Waypoint 주행](practice/03-mobile-robots/17-mobile-navigation/README.md) |
| 18 | [LiDAR와 미로 주행](practice/03-mobile-robots/18-lidar-maze/README.md) |
| 19 | [장애물 회피](practice/03-mobile-robots/19-obstacle-avoidance/README.md) |

### 강화학습 환경

| 강좌 | 실습 |
|---|---|
| 20 | [강화학습 환경 기초](practice/04-reinforcement-learning/20-base-env/README.md) |
| 21 | [관측과 보상](practice/04-reinforcement-learning/21-observation-reward/README.md) |
| 22 | [행동 공간](practice/04-reinforcement-learning/22-action-space/README.md) |
| 23 | [강화학습 환경 만들기](practice/04-reinforcement-learning/23-custom-env-complete/README.md) |
| 24 | [Cartpole 강화학습](practice/04-reinforcement-learning/24-train-cartpole/README.md) |
| 25 | [Cartpole 결과 비교](practice/04-reinforcement-learning/25-evaluate-policy/README.md) |
| 26 | [4족 로봇 보행 학습](practice/04-reinforcement-learning/26-train-locomotion/README.md) |
| 27 | [4족 로봇 보행 결과](practice/04-reinforcement-learning/27-evaluate-locomotion/README.md) |
| 28 | [다양한 지형과 Domain Shift](practice/04-reinforcement-learning/28-terrain-generation/README.md) |
| 29 | [Domain Randomization](practice/04-reinforcement-learning/29-domain-randomization/README.md) |

### 휴머노이드 강화학습

| 강좌 | 실습 |
|---|---|
| 35 | [휴머노이드 서기](practice/05-humanoid-rl/35-g1-standing/README.md) |
| 36 | [휴머노이드 보행과 모션 모방](practice/05-humanoid-rl/36-g1-motion-imitation/README.md) |

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
