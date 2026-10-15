# 휴머노이드와 모션 모방

[강화학습 목차](README.md) · [개념 학습 전체](../../README.md)

## 이 문서에서 다루는 내용

- [23. 휴머노이드 서기 — Policy·PD·접촉 물리의 역할](#23-휴머노이드-서기--policypd접촉-물리의-역할)
- [24. 모션 모방 강화학습 — 레퍼런스·RSI·PPO](#24-모션-모방-강화학습--레퍼런스rsippo)

<a id="humanoid-standing"></a>

## 23. 휴머노이드 서기 — Policy·PD·접촉 물리의 역할

35번은 G1의120관측에서37개 관절 목표 오프셋을 내고, implicit PD와 발 접촉 물리로 자세를 유지한다. 정책이 실제 토크를 직접 출력하거나 중력 보상 함수를 호출하는 구조는 아니다.
root 높이·기울기·생존·움직임·한계를 보상으로 삼고 PPO로 학습한다. root 높이0.74m는 전체 신장이나 CoM 높이와 다르다.

512환경×24step=12,288개 전이를 8미니배치×5epoch로 사용하므로 iteration당40회 optimizer 업데이트다. 정규화 통계도 checkpoint에 포함한다.
추가 사진과 완주 event 로그의 마지막 평균 보상은77.90·길이250step이다. 별도 평가 영상은 학습12회 모두250step, 랜덤10회 평균40.5step이었다.
이 결과는 기본 서기 자세·평면 조건의 성능이며 쓰러진 상태의 get-up·외란 회복·걷기까지 검증한 것은 아니다.

[휴머노이드 균형·PD·보상·PPO 개념](../../05-humanoid-rl/humanoid-standing/README.md) · [35번 실습·실제 곡선](../../../practice/05-humanoid-rl/35-g1-standing/README.md) · [코드 리뷰](../../../practice/05-humanoid-rl/35-g1-standing/code-review.md)

<a id="motion-imitation"></a>

## 24. 모션 모방 강화학습 — 레퍼런스·RSI·PPO

36번은 리타게팅된 모션을 관측의 목표·추종 보상·RSI 초기화에 사용한다. 기록된 자세를 그대로 재생하거나 행동 라벨을 회귀하는 Behavior Cloning과 다르다.
기본 관측 103개·행동 23개의 정책이 물리 안에서 동작을 만들고 PPO로 학습한다. RSI는 클립의 임의 위상에서 자세·속도를 맞추며 episode 카운터와 목표 위상이 일치해야 한다.

보행 가중치에 쿵푸 목표를 주는 것과 쿵푸로 다시 학습하는 것은 다르다. 재학습해도 낮은 자세·후진·회전·빠른 동작과 보상·종료가 충돌하면 태스크 정의를 수정해야 한다.
전용 환경은 속도 벡터·yaw·높이 편차와 RSI를 보완해 107관측이 되므로 기본 103모델과 그대로 호환되지 않는다.
학습·평가에서 모델과 모션을 함께 명시하고 생존율뿐 아니라 추종 오차·방향·접촉을 평가한다.

[모션 모방 상세 개념](../../05-humanoid-rl/motion-imitation/README.md) · [36번 결과·쿵푸 실패 분석](../../../practice/05-humanoid-rl/36-g1-motion-imitation/README.md) · [기준 코드 리뷰](../../../practice/05-humanoid-rl/36-g1-motion-imitation/code-review.md)
