# PPO 학습과 가중치 업데이트

[강화학습 목차](README.md) · [개념 학습 전체](../../README.md)

## 이 문서에서 다루는 내용

- [13. PPO 실제 학습 — 경험으로 Actor와 Critic을 바꾸기](#13-ppo-실제-학습--경험으로-actor와-critic을-바꾸기)

<a id="ppo-training"></a>

## 13. PPO 실제 학습 — 경험으로 Actor와 Critic을 바꾸기

24번부터는 Actor가 행동을 고르고 학습기가 가중치를 업데이트한다. 환경은 보상을 계산하고, PPO는 보상과 가치 추정으로 학습 신호를 만든다.
같은 관측 7개를 Actor·Critic에 넣되 Actor는 행동 분포, Critic은 미래 할인 누적 가치 하나를 출력한다.
두 네트워크는 각각 은닉층 `[32, 32]`이며 초기 가중치는 라이브러리가 생성한다.

<p align="center">
  <img src="diagrams/12-lesson24-training.png" alt="실제 Cartpole 학습 반복" width="337">
</p>
<p align="center"><sub>그림 12. 실제 Cartpole 학습 반복</sub></p>

### Rollout과 학습의 시간은 나눠 생각한다

현재 정책으로 1024환경에서 16 step씩 경험을 수집한다. 각 전이는 관측·행동·보상·종료와 정책/가치 정보를 가진다.
한 번 수집한 16,384개 전이로 여러 optimizer step을 수행하고, 바뀐 정책으로 다음 경험을 모은다.
16 step의 수집 구간은 300 step 에피소드와 다르다. 에피소드가 끝나기 전에 Critic으로 이후 가치를 추정해 학습할 수 있다.

| 단위 | 이번 설정 |
|---|---|
| 환경 step | 물리 step 2회 · 1/60초 |
| rollout | 환경당 16 step · 총 16,384 전이 |
| mini-batch | 4096개 전이 |
| epoch | 같은 rollout을 5회 사용 |
| iteration | rollout 수집 + 목표 계산 + 학습 + 기록 |
| 150 iteration | 2,457,600개 새 전이 · 기본 optimizer 3000회 |

PPO가 on-policy라는 것은 현재 정책으로 모은 경험을 주로 사용한다는 뜻이다. 같은 rollout을 몇 epoch 사용하는 것과 오래된 replay buffer를 계속 사용하는 것은 구분한다.

### Advantage는 즉시 보상만 보고 판단하지 않는다

보상은 지금 받은 점수, value는 앞으로의 할인 누적 보상 예측, return target은 보상과 bootstrap으로 만든 학습 목표다.
Advantage는 ‘이 행동이 현재 정책의 예상보다 얼마나 유리했나’를 나타낸다.
GAE는 `지금 보상 + 할인한 다음 가치 - 지금 가치`라는 TD 오차들을 여러 step에 걸쳐 섞는다. gamma는 미래 할인, lambda는 여러 길이의 추정 간 균형을 조절한다.
따라서 `즉시 보상 - Critic 값`만으로 설명하면 미래 보상과 시간 단위가 빠진다.

<p align="center">
  <img src="diagrams/13-ppo-update.png" alt="Advantage와 두 손실이 가중치를 바꾸는 과정" width="900">
</p>
<p align="center"><sub>그림 13. Advantage와 두 손실이 가중치를 바꾸는 과정</sub></p>

Actor는 양의 Advantage 행동을 더 자주, 음의 Advantage 행동을 덜 자주 고르도록 목적을 구성한다. Critic은 return target을 더 잘 예측하도록 학습한다.
이때 신경망 역전파가 수정 방향을 계산하고 optimizer가 가중치를 바꾼다.

### PPO clip·탐색·학습률은 서로 다른 기능이다

PPO는 같은 행동의 새/이전 정책 확률비로 정책 개선 목적을 만들고, clip된 목적과 비교해 지나친 개선을 억제하려 한다.
clip=0.2는 확률비 목적의 0.8~1.2 범위에 사용하며, 행동 ±0.2나 가중치 변화 ±20% 제한을 뜻하지 않는다. 모든 정책 변화를 강제로 막는 보장도 아니다.

탐색 σ는 행동 분포의 퍼짐이다. 처음 1.0으로 시작하고 학습된다. entropy 보너스는 정책이 너무 빨리 한 행동에 집중하지 않도록 장려한다.
연속 분포 entropy는 음수일 수 있다. 탐색이 줄었다는 사실만으로 성공을 판단하지 않는다.
학습률은 한 번 수정할 크기, gradient clipping은 수정 방향의 gradient 크기 제한, KL 기준은 이전/새 분포 변화에 따라 학습률을 조정하는 기준이다.

### 체크포인트·학습 로그·평가는 다르다

체크포인트에는 정책·가치·탐색 가중치와 optimizer·iteration 등 상태를 저장한다. model_0은 이번 Runner에서 첫 학습 iteration 후 모델이며 초기 가중치와 다르다.
실제 행동 실행에는 보통 Actor를 사용하지만 학습 재개에는 optimizer 등의 상태도 유용하다. 환경·관측 순서·행동 scale·라이브러리 버전도 함께 보관한다.

학습 중 mean_reward와 mean_episode_length는 최근 완료 에피소드의 평균이며 독립 평가 성공률이 아니다.
`Episode_Reward/*`는 이번 Isaac Lab에서 항별 누적을 최대 에피소드 시간으로 나눈 값이라 전체 점수와 구분한다.
최종 모델은 새 초기화·seed·평가 조건에서 보상·유지 시간·직립 오차·실패율을 다시 확인한다.

이번 실제 로그는 평균 보상 0.45→17.29, 길이 9.7→300 step으로 향상됐다. 세부 곡선·원본 로그·모델은 [24번 기록](../../../practice/04-reinforcement-learning/24-train-cartpole/README.md)에 있다.
