# 26. ANYmal 4족 보행 PPO 학습

## 이번 실습의 핵심

**보행은 목표 속도를 따라가면서, 지면을 지지하는 발과 앞으로 옮기는 발을 조절해 몸을 안정적으로 이동시키는 제어 문제다.**
이번에는 Cartpole 환경을 직접 작성하는 대신 등록된 `Isaac-Velocity-Flat-Anymal-B-v0`를 불러와 PPO를 학습한다.
학습기는 목표 속도와 현재 몸·관절 상태를 보고 12개 관절의 위치 목표를 함께 결정한다.

[보행 개념 집중 정리](../learning-notes/legged-locomotion/README.md) · [코드 리뷰](code-review.md) · [공용 강화학습 개념](../learning-notes/reinforcement-learning/README.md#locomotion)

## 코드와 실행

- [제공된 코드](26_train_locomotion.py): [기준 튜토리얼](https://github.com/PinkWink/isaacsim_tutorials/blob/14f85fc6edece7cbb1faa50aa9fe3adef205e87a/26_train_locomotion/26_train_locomotion.py)과 동일하다.
- 출처: PinkLAB 「강좌 26 - 26_train_locomotion」

```bash
cd <physical-ai-training 저장소 경로>/26-train-locomotion
python 26_train_locomotion.py --headless --num_envs 2048 --max_iterations 300
# GUI로 학습 상태 관찰 · 환경 수를 바꾸면 총 경험 수도 달라짐
python 26_train_locomotion.py --num_envs 64 --max_iterations 300
# 저장된 로그를 볼 때
tensorboard --logdir logs/rsl_rl/anymal_locomotion_tutorial
```

환경·보상은 Isaac Lab의 등록 Cfg에서 읽고, PPO 설정은 이 파일의 `AnymalLocoPPORunnerCfg`를 사용한다.
학습 결과 경로는 실행 폴더 기준 `logs/rsl_rl/anymal_locomotion_tutorial`이다.

## 코드 실행 구조

<p align="center">
  <img src="../learning-notes/reinforcement-learning/diagrams/19-lesson26-training.png" alt="등록 환경을 불러와 보행 PPO를 학습하는 흐름" width="284">
</p>
<p align="center"><sub>그림 19. 등록 환경을 불러와 보행 PPO를 학습하는 흐름</sub></p>

`import isaaclab_tasks`로 태스크가 등록되고 `load_cfg_from_registry()`가 환경 Cfg를 가져온다. 병렬 수를 변경한 뒤 `gym.make()`로 환경을 만든다.
wrapper와 Runner에 연결한 이후 rollout·GAE·PPO 업데이트는 24번과 같은 원리다. 보행 자체를 구현하는 관측·행동·접촉·보상 함수는 등록 환경 안에 있다.

## 보행을 어떻게 배우는가

### 1. 명령 속도와 관절 행동은 다르다

명령은 기체 기준 전후 속도 `vx`, 좌우 속도 `vy`, 회전 속도 `ωz`다. ‘앞으로 0.5 m/s’는 어디로 얼마나 빠르게 이동할지 지시하며 어느 발을 언제 드는지는 알려주지 않는다.
정책이 관측을 이용해 네 다리의 관절 목표를 만든다. **차체 속도 명령을 관절 각속도에 그대로 넣는 구조가 아니다.**

참조 환경은 명령을 약 10초 간격으로 재설정하며 일부 환경은 정지 명령을 받는다. heading_command도 활성화되어 목표 방향 오차에서 yaw 속도 명령을 만든다.
영상의 초록 화살표는 목표 평면 속도, 파란 화살표는 현재 평면 속도다. 방향·길이의 차이는 추적 상태를 보여주며 발의 다음 착지점 표시는 아니다.

### 2. 지지기와 유각기의 협응

- **지지기(stance):** 발이 지면과 접촉해 지면 반력을 받는다. 다리가 몸을 지탱하고 추진·자세 조절에 기여한다.
- **유각기(swing):** 발이 지면에서 떨어져 다음 지점으로 이동한다. 발을 들고 앞으로 보내고 다시 착지하는 동작이다.

몸통에는 바닥에 고정된 기반이 없으므로 다리 토크만으로 몸을 원하는 곳으로 순간 이동시킬 수 없다. 발 접촉·마찰·중력이 몸의 운동을 결정한다.
한 다리를 들 때 다른 발의 지지와 몸의 기울기를 함께 맞춰야 한다. 정지 시 균형과 움직이는 중의 동적 균형은 같지 않다.

이 환경에는 대각선 다리를 번갈아 움직이라는 고정 trot 스케줄이나 명시적 위상 입력이 없다. **어떤 협응 동작이 유리한지 보상과 물리를 통해 학습한다.** 영상만으로 특정 보행 유형을 확정하지 않는다.

### 3. 정책은 무엇을 보고 무엇을 출력하나

<p align="center">
  <img src="../learning-notes/reinforcement-learning/diagrams/20-locomotion-control.png" alt="몸 상태·명령에서 관절 목표와 접촉 운동으로 이어지는 구조" width="900">
</p>
<p align="center"><sub>그림 20. 몸 상태·명령에서 관절 목표와 접촉 운동으로 이어지는 구조</sub></p>

| 관측 · Flat 참조 설정 | 차원 | 역할 |
|---|---:|---|
| 기체 선속도 | 3 | 현재 전후·좌우·수직 이동 |
| 기체 각속도 | 3 | 각 축 주위 회전 속도 · 자세 각도 자체가 아님 |
| projected gravity | 3 | 기체 좌표계에서 본 중력 방향 · 기울기 파악 |
| 속도 명령 | 3 | 목표 `vx, vy, ωz` |
| 기본 자세 대비 관절 위치 | 12 | 네 다리의 현재 구성 |
| 관절 속도 | 12 | 각 관절의 운동 상태 |
| 직전 행동 | 12 | 이전 명령과의 연속성 정보 |
| 합계 | **48** | Flat 정책 입력 · 학습 시 관측 노이즈 활성화 |

중력 투영만으로 yaw 방향을 모두 알 수는 없다. 관측의 몸 속도·관절 상태 등은 시뮬레이터에서 읽으며, 실제 로봇에서는 센서·상태 추정으로 같은 의미의 입력을 확보해야 한다.

행동은 **12개 관절 위치 목표**다. 참조 설정에서 `q_target = q_default + 0.5 × action`으로 변환한다.
현재 관절 각도에 계속 0.5씩 더하는 누적 명령이 아니다. 각 다리는 HAA·HFE·KFE 세 관절을 갖는다.
ANYmal-B는 하위 구동에 사전 학습된 LSTM actuator-net을 사용한다. 이번 PPO의 Actor·Critic MLP와는 별도 모델이며 ‘이번 정책도 LSTM’이라는 뜻이 아니다.

### 4. 보상이 움직임의 성격을 정한다

| 목표 | 대표 항 | 해석 |
|---|---|---|
| 명령 속도 따라가기 | 평면 선속도·yaw 각속도 추적 | 빠르게 달리기 자체가 아니라 명령과 오차를 줄이기 |
| 몸 안정화 | 수직 속도·roll/pitch 각속도·기울기 벌점 | 과도한 들썩임·흔들림·기울기 억제 |
| 구동 부담 줄이기 | 토크 제곱·관절 가속도·행동 변화 벌점 | 실제 소비 전력과 동일한 측정은 아님 |
| 발 이동 유도 | feet_air_time | 발이 공중에 있다 착지한 시점의 공중 시간 평가 |
| 비정상 접촉 억제 | 허벅지 접촉 벌점 | 발 이외 접촉과 지지 동작을 구분 |
| 에피소드 실패 | 몸통 접촉 종료 | 일정 접촉 힘을 넘으면 task 종료 |

접촉 센서는 공중 시간·비정상 접촉 보상과 종료 판정에 쓰인다. **발 접촉 힘 자체는 위 48차원 Actor 입력에 직접 포함되지 않는다.**
발 공중 시간 보상은 단순히 ‘오래 띄울수록 매 step 가점’이 아니다. 첫 착지 시 `(공중 시간 - 0.5초)`를 평가하고, 평면 이동 명령이 작으면 이 항은 비활성화된다. 짧은 스텝에서는 음수도 가능하다.
명령을 잘 따라도 토크·동작 변화가 크면 감점될 수 있다. 보행은 이 목표들을 함께 만족시키는 문제다.

## Cartpole에서 달라진 점

| 구분 | 24번 Cartpole | 26번 Flat ANYmal-B · 참조 설정 |
|---|---|---|
| 관측 / 행동 | 7 / 1 | 48 / 12 |
| 행동 의미 | 카트 힘 | 기본 자세 기준 관절 위치 목표 |
| Actor·Critic 은닉층 | 각각 [32, 32] | 각각 [128, 128, 128] |
| 환경 step | 1/60초 | 0.02초 · 50 Hz |
| 물리 step / decimation | 1/120초 / 2 | 0.005초 / 4 |
| 에피소드 상한 | 5초 · 300 step | 20초 · 1000 step |
| rollout | 16 step | 24 step · **0.48초** |
| 기본 환경 수 / iteration | 1024 / 150 | 2048 / 300 |

24 step이 보행 주기 0.5초를 ‘여러 번’ 포함한다는 설명은 이 설정과 맞지 않는다. rollout은 약 0.48초이며 에피소드가 끝나지 않아도 Critic으로 이후 가치를 연결한다.

2048 × 24 = 49,152개 전이를 iteration마다 수집한다. 4 mini-batch·5 epoch라 각 batch는 12,288개, 기본 optimizer 업데이트는 iteration당 20회다.
300 iteration의 총 전이는 **14,745,600개**다. 환경 수를 줄이면 같은 iteration이라도 학습 경험 수가 줄어든다.

## 실제 영상 결과

### 26-1 — 학습 초반

<p align="center">
  <img src="images/early-scene.png" alt="학습 초반의 여러 ANYmal과 속도 화살표" width="900">
</p>

<p align="center">
  <img src="images/early-training-log.png" alt="iteration 2의 학습 지표" width="666">
</p>

영상 초반 iteration 2에서 평균 보상 -3.61, 평균 에피소드 길이 63.02 step을 확인했다. 제자리 흔들림·짧은 이동·개별 리셋이 섞인 학습 중 장면이다.

[첫 번째 영상 — 약 40.35초](videos/26-1.webm)

### 26-2 — 학습 후반과 완료

<p align="center">
  <img src="images/late-scene.png" alt="학습 후반의 ANYmal 보행 장면" width="900">
</p>

<p align="center">
  <img src="images/training-complete.png" alt="최종 학습 지표와 학습 완료" width="666">
</p>

| 제공 영상의 최종 로그 · iteration 299 | 값 |
|---|---:|
| Mean reward | 18.93 |
| Mean episode length | 978.22 step · 환산 약 19.56초 |
| 총 전이 | 14,745,600 |
| 학습 시간 표시 | 00:08:02 |
| 평면 / yaw 속도 추적 보상 항 | 0.8878 / 0.4171 |
| feet_air_time 보상 항 | -0.0436 |
| timeout / 몸통 접촉 종료 지표 | 0.9581 / 0.0419 |

[영상 로그 전사 JSON](analysis/video-observations.json)

유지 길이와 보상은 향상됐다. 다만 위 값은 학습 중 집계이며 timeout 0.9581을 독립 평가 성공률 95.81%로 바꾸지 않는다. 발 공중 시간 항의 음수도 해당 함수·threshold·가중치로 해석해야 한다.
Cartpole과 보상 항·에피소드 시간이 달라 18.93 대 17.28 같은 숫자만으로 태스크 성능을 비교하지 않는다.
이번에는 TensorBoard 이벤트와 모델 파일이 첨부되지 않아 전체 학습 곡선이나 저장 모델을 새로 생성하지 않았다. 27번에서 고정 정책의 실제 명령 추적·생존·외란 대응을 평가한다.

[두 번째 영상 — 터미널 전용 게시본 · 약 14.21초](videos/26-2-terminal.webm)

두 번째 원본에는 마지막에 브라우저가 보여 **영상 전체에서 터미널 영역만 추출한 게시본**을 사용했다. 원본 전체 화면은 저장소에 게시하지 않았다. 장면 캡처는 브라우저가 나타나기 전 Isaac Sim viewport에서 추출했다.

## 강의 설명에서 구분할 점

- 기본 Flat 태스크는 height scan과 지형 커리큘럼을 끈다. Rough 환경 기능이 Flat에도 자동 적용되는 것은 아니다.
- 등록 환경을 쓴다고 이미 학습된 보행 정책을 받은 것은 아니다. 환경과 하위 actuator 모델은 제공되지만 이번 PPO 보행 정책은 새로 학습한다.
- 300 iteration은 실행 예산이며 모든 조건에서 안정 보행 완성을 보장하지 않는다.
- `--task ...Rough...`만 바꾸는 것은 Flat 체크포인트를 불러온 fine-tuning이 아니다. 원본 코드에는 체크포인트 load가 없다.

수치·시간·모델 의미와 설정 상속 관계는 [코드 리뷰](code-review.md)에 자세히 정리했다.
