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

## 실습 기록

| 강좌 | 내용 | 기록 |
|---|---|---|
| 03 | 갈릴레오 자유낙하 실험 | [실험 조건·결과·영상·배운 점](03-galileo/README.md) · [코드](03-galileo/03_galileo_experiment.py) |
| 04 | 시뮬레이션 루프와 탄성 비교 · 강체 리셋 수정 | [실험 결과·수정 이유·영상](04-simulation-loop/README.md) · [수정된 코드](04-simulation-loop/04_simulation_loop.py) |
| 05 | Franka Panda 로봇 배치 · 랜덤 관절 입력 · 상태 읽기와 리셋 | [실습 결과·영상·배운 점](05-spawn-robot/README.md) · [코드](05-spawn-robot/05_spawn_robot.py) |
| 06 | 관절 위치 제어 · 중력 보상 · 손끝 위치 마커 비교 | [세 실습 결과·영상·코드](06-robot-joint-control/README.md) |
| 07 | InteractiveScene · 환경 자동 복제 · 4개/16개 환경 비교 | [실습 결과·환경 자동 배치·코드](07-scene-design/README.md) |
| 08 | 다중 로봇 · 초기 자세 설정 · 특정 환경 선택 제어 | [실습 결과·선택 제어·코드](08-multi-robot/README.md) |
