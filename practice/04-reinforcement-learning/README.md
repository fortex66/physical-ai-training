# 4. 강화학습 환경

[실습 전체](../README.md) · [저장소 홈](../../README.md)

환경 설계에서 PPO 학습·평가·보행·일반화까지 이어간다.

## 먼저 볼 개념

[강화학습 환경 개념](../../learning-notes/04-reinforcement-learning/README.md)

## 실습 목록

| 강좌 | 내용 | 기록 |
|---|---|---|
| 20 | 강화학습 환경 기초 · Cartpole 랜덤 행동 · 관측·보상·종료·리셋 | [실습 결과](20-base-env/README.md) · [코드 리뷰](20-base-env/code-review.md) · [코드](20-base-env/20_base_env.py) |
| 21 | 커스텀 관측·보상 · sin/cos·정규화 · 항별 보상 해석 | [실습 결과](21-observation-reward/README.md) · [코드 리뷰](21-observation-reward/code-review.md) · [코드](21-observation-reward/21_observation_reward.py) |
| 22 | 액션 공간 · 힘/위치/속도 명령 · scale·offset·actuator 연결 | [실습 결과](22-action-space/README.md) · [코드 리뷰](22-action-space/code-review.md) · [코드](22-action-space/22_action_space.py) |
| 23 | 커스텀 RL 환경 완성 · 막대 실패 종료 · 학습 전 baseline | [실습 결과](23-custom-env-complete/README.md) · [코드 리뷰](23-custom-env-complete/code-review.md) · [코드](23-custom-env-complete/23_custom_env_complete.py) |
| 24 | Cartpole PPO 학습 · Actor·Critic·GAE · 실제 곡선·체크포인트 | [실습 결과·학습 구조](24-train-cartpole/README.md) · [코드 리뷰](24-train-cartpole/code-review.md) · [코드](24-train-cartpole/24_train_cartpole.py) |
| 25 | 학습 정책 vs 랜덤 평가 · deterministic 추론 · RL 워크플로우 마무리 | [실습 결과·비교](25-evaluate-policy/README.md) · [코드 리뷰](25-evaluate-policy/code-review.md) · [코드](25-evaluate-policy/25_evaluate_policy.py) |
| 26 | ANYmal 보행 PPO · 속도 추적·지지/유각기·관절 목표·접촉 보상 | [실습 결과·보행 개념·학습 곡선](26-train-locomotion/README.md) · [코드 리뷰](26-train-locomotion/code-review.md) · [코드](26-train-locomotion/26_train_locomotion.py) |
| 27 | 학습된 ANYmal 정책 평가 · 평균 행동·명령 추적·생존 지표 검토 | [실습 결과](27-evaluate-locomotion/README.md) · [코드 리뷰](27-evaluate-locomotion/code-review.md) · [코드](27-evaluate-locomotion/27_evaluate_locomotion.py) |
| 28 | 혼합 지형 생성 · 고정 보행 정책 · Domain Shift와 일반화 | [실습 결과](28-terrain-generation/README.md) · [코드 리뷰](28-terrain-generation/code-review.md) · [코드](28-terrain-generation/28_terrain_generation.py) |
| 29 | Domain Randomization · 질량·초기 상태·이벤트 타이머 검토 | [실습 결과](29-domain-randomization/README.md) · [코드 리뷰](29-domain-randomization/code-review.md) · [코드](29-domain-randomization/29_domain_randomization.py) |

각 강좌 폴더에서 설명·코드·영상·이미지를 확인할 수 있습니다. 학습이 있는 강좌는 로그·체크포인트와 코드 리뷰도 함께 보관합니다.

20~23장은 환경 구성·검증, 24장은 PPO 학습, 25장은 정책 평가입니다. 26~27장은 보행 학습·평가, 28장은 지형 변화 평가, 29장은 랜덤화 이벤트 실습으로 구분합니다.
