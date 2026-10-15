# 보행과 일반화

[강화학습 목차](README.md) · [개념 학습 전체](../../README.md)

## 이 문서에서 다루는 내용

- [17. 보행 학습 — 명령을 관절 협응과 지면 접촉으로 바꾸기](#17-보행-학습--명령을-관절-협응과-지면-접촉으로-바꾸기)
- [20. 보행 정책 평가 — 평균 행동과 고정된 판정 기준](#20-보행-정책-평가--평균-행동과-고정된-판정-기준)
- [21. Domain Shift — 같은 정책도 다른 지형에서는 달라진다](#21-domain-shift--같은-정책도-다른-지형에서는-달라진다)
- [22. Domain Randomization — 정책의 행동과 환경 조건의 랜덤성을 구분한다](#22-domain-randomization--정책의-행동과-환경-조건의-랜덤성을-구분한다)

<a id="locomotion"></a>

## 17. 보행 학습 — 명령을 관절 협응과 지면 접촉으로 바꾸기

26번은 `(vx, vy, ωz)` 명령을 보고 12개 관절 위치 목표를 함께 선택하는 정책을 학습한다.
몸을 직접 이동시키는 명령이 아니라 actuator 토크와 발 접촉·마찰로 몸의 속도와 균형을 만든다.
지지기에는 발이 하중을 지탱하고, 유각기에는 다음 착지를 준비한다. 고정 보행 스케줄 없이 속도 추적·안정성·구동 부담·발 공중 시간 목적에서 협응을 학습한다.

<p align="center">
  <img src="diagrams/20-locomotion-control.png" alt="보행 명령·관측에서 관절 목표와 접촉 운동까지" width="900">
</p>
<p align="center"><sub>그림 20. 보행 명령·관측에서 관절 목표와 접촉 운동까지</sub></p>

참조 Flat 관측은 48차원, 행동은 12개 관절의 기본 자세 대비 위치 명령이다. 하위 ANYdrive LSTM actuator-net과 PPO의 MLP 정책은 별개다.
정책에 들어가는 몸 상태와 보상·종료에 쓰이는 접촉 센서를 구분한다. 접촉 힘을 Actor 입력으로 직접 쓰는 구성은 아니다.

환경 step 0.02초이므로 24 step rollout은 0.48초다. 완결 보행 주기를 여러 번 넣는다는 의미가 아니며 GAE로 이후 가치를 연결한다.
Flat은 지형 커리큘럼과 height scan을 끈다. 학습 완료 iteration 수는 예산이며, 고정 모델의 명령 추적·외란 대응·새 지형 성능은 별도 평가한다.

[보행 집중 개념](../legged-locomotion/README.md) · [26번 결과](../../../practice/04-reinforcement-learning/26-train-locomotion/README.md) · [코드 리뷰](../../../practice/04-reinforcement-learning/26-train-locomotion/code-review.md)

<a id="locomotion-evaluation"></a>

## 20. 보행 정책 평가 — 평균 행동과 고정된 판정 기준

27번은 26번 모델을 로드하고 Actor 평균으로 매 관측에 반응한다. 가중치를 업데이트하지 않지만 로봇·actuator 상태는 계속 진행된다.
정책의 탐색 샘플링을 없애도 환경 노이즈·초기화·명령·외란까지 고정되는 것은 아니다. 기본 Flat 학습 Cfg를 평가에서도 사용한다는 점을 확인한다.

생존 지표는 모든 모델에 같은 기준이어야 한다. `int(max(관측 episode 길이)*0.9)`처럼 평가 표본에서 기준을 다시 정하면 전부 일찍 실패한 정책도 높은 비율을 얻을 수 있다.
고정 horizon·task 실패 없는 timeout과 명령 추적 오차 등을 함께 기록한다.
제공 27번 영상은 20회 모두 길이 1000·timeout 표시, 평균 보상 23.99지만 이 표본을 모든 초기 상태·지형의 성공으로 일반화하지 않는다.

[27번 결과·추론 구조](../../../practice/04-reinforcement-learning/27-evaluate-locomotion/README.md) · [생존률·환경 노이즈 코드 리뷰](../../../practice/04-reinforcement-learning/27-evaluate-locomotion/code-review.md)

<a id="domain-shift"></a>

## 21. Domain Shift — 같은 정책도 다른 지형에서는 달라진다

Domain Shift는 학습과 실행 조건의 분포가 달라지는 현상이다. 평지에서 배운 행동이 계단에서 다른 발 접촉을 만들면 다음 자세·관측이 바뀌고, 그 관측에 대한 행동이 다시 상태를 바꾸는 피드백이 이어진다.
입력·출력 차원이 같아 checkpoint를 load할 수 있어도 관측값의 분포나 성능이 같다는 뜻은 아니다.

28번은 Flat 정책 가중치를 고정하고 지형을 교체하는 평가다. 관측→행동→물리 step→새 관측·보상·종료는 반복하지만 PPO 업데이트는 없다. 보상을 계산하거나 episode를 reset한다고 실패를 학습하는 것은 아니다.
26번의 49,152개 전이 수집·5 epoch를 반복할 때도 학습 경험의 조건이 중요하다. 환경 수와 반복 수만 늘려 평지 경험을 많이 모으는 것과 다양한 지형에서 학습하는 것은 다르다.

대응에는 다양한 지형 학습·물리 랜덤화·실제 성공에 따른 난이도 curriculum·추가 관측·fine-tuning이 있다. 환경 변경이 반드시 재학습을 요구하거나 모든 분포 차이가 실패를 일으키는 것은 아니다.
Rough task의 height scan처럼 관측을 늘리면 기존 입력층과 호환되지 않을 수 있어 별도 설계가 필요하다.

28번 영상의 혼합 지형 timeout은 21/200(10.5%)다. 먼저 완료된 N회를 집계하는 방식은 짧은 실패가 더 포함될 수 있으므로, 지형·환경별 할당량과 여러 seed로 공정하게 평가해야 한다. timeout은 작업 성공이나 속도 추종 성공과도 구분한다.

[Domain Shift 상세 개념·피드백 구조·PPO 연결·대응·평가 방법](../domain-shift/README.md) · [28번 결과](../../../practice/04-reinforcement-learning/28-terrain-generation/README.md) · [코드 리뷰](../../../practice/04-reinforcement-learning/28-terrain-generation/code-review.md)

<a id="domain-randomization"></a>

## 22. Domain Randomization — 정책의 행동과 환경 조건의 랜덤성을 구분한다

학습할 환경의 질량·마찰·초기 상태·센서·외란 등을 범위 안에서 바꿔 여러 조건의 경험을 제공한다.
행동 탐색은 policy의 action 샘플링이고, Domain Randomization은 환경 조건 설계이며, PPO optimizer는 가중치 수정이다. 세 동작은 서로 다르다.
같은 rollout·미니배치·epoch 구조를 유지하더라도 경험이 생성되는 조건을 바꾸면 정책이 다양한 반응을 학습하게 할 수 있다.

`startup`은 환경 생성 때 한 번, `reset`은 초기화 때, `interval`은 타이머 조건을 만족할 때 실행한다. 랜덤화한 조건을 모두 Actor에 직접 주는 것은 아니므로 숨은 물성으로 인한 부분 관측도 고려한다.
현실적인 범위를 선택하고 미사용 조건의 동일 평가로 효과를 확인한다. 랜덤화 자체가 일반화나 sim-to-real 성공을 보장하지 않는다.

29번은 이벤트를 구성한 뒤 랜덤 행동으로 500 step 실행하는 데모이며 PPO 학습은 없다. 또한 최대5초 episode가 interval 타이머를 reset하므로 5~10초·10~15초 외란은 현재 설정에서 발동하지 않는다.
term 등록·요약 출력과 실제 이벤트 호출을 구분해야 한다.

[상세 개념·PPO 연결·범위 설계·평가](../domain-randomization/README.md) · [29번 데모](../../../practice/04-reinforcement-learning/29-domain-randomization/README.md) · [코드 리뷰](../../../practice/04-reinforcement-learning/29-domain-randomization/code-review.md)
