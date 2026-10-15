# Physical AI 학습 기록

Isaac Sim / Isaac Lab 교육에서 배운 개념과 실습 결과를 정리한 저장소입니다. **개념 학습 → 실습 기록** 순서로 구성했습니다.

## 개념 학습

[전체 개념 목차](learning-notes/README.md) · [NVIDIA 생태계](learning-notes/00-overview/nvidia-ecosystem/README.md) · [핵심 개념 요약](learning-notes/00-overview/robotics-core-concepts/README.md)

| 분야 | 주요 개념 |
|---|---|
| [시뮬레이션 기초](learning-notes/01-simulation-basics/README.md) | 물리·충돌·물성 / 시간·루프·리셋 / 환경 복제 |
| [로봇 제어 및 센서](learning-notes/02-robot-control-and-sensors/README.md) | Articulation / PD·중력 보상 / 센서·URDF / FK·IK·상태 머신 |
| [모바일 로봇](learning-notes/03-mobile-robots/README.md) | 차동 구동 / 오도메트리 / Waypoint / LiDAR·회피 |
| [강화학습 환경](learning-notes/04-reinforcement-learning/README.md) | Policy·Critic / 관측·행동·보상·종료 / PPO·미니배치 / 평가·일반화 |
| [휴머노이드 강화학습](learning-notes/05-humanoid-rl/README.md) | G1 균형·서기 / 모션 모방 / RSI / 태스크·보상 설계 |

## 실습 기록

[전체 실습 목차](practice/README.md)

| 파트 | 강좌 | 내용 |
|---|---|---|
| [1. 시뮬레이션 기초](practice/01-simulation-basics/README.md) | 03~04 | 강체·충돌·중력·반발과 시뮬레이션 루프·리셋을 이해한다. |
| [2. 로봇 제어 및 센서](practice/02-robot-control-and-sensors/README.md) | 05~14 | 로봇 관절 제어·다중 환경·센서·기구학을 작업 시퀀스로 연결한다. |
| [3. 모바일 로봇](practice/03-mobile-robots/README.md) | 15~19 | 차동 구동에서 위치 추정·목표점 주행·장애물 회피까지 연결한다. |
| [4. 강화학습 환경](practice/04-reinforcement-learning/README.md) | 20~29 | 환경 설계에서 PPO 학습·평가·보행·일반화까지 이어간다. |
| [5. 휴머노이드 강화학습](practice/05-humanoid-rl/README.md) | 35~36 | G1의 서기와 레퍼런스 모션 추종을 학습하고 평가한다. |

각 강좌 폴더에 코드·결과 이미지·영상과 학습 기록을 함께 보관합니다. 강화학습 실습에는 코드 리뷰·학습 로그·체크포인트도 연결되어 있습니다.

## 저장소 구성

```text
learning-notes/  # 분야별 이론과 공통 구성도
practice/        # 다섯 파트의 강좌별 코드·결과물
README.md        # 학습 안내와 공통 실습 환경
CONTRIBUTING.md  # 학습 기록 작성 기준
```

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
