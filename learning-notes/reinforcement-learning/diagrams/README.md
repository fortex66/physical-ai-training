# D2로 보는 강화학습과 20~22장 실행 구조

20장은 환경을 테스트하며, 정책 가중치를 학습하는 코드는 아직 없다.
흰 배경·진한 글자·파란 강조색을 사용한 D2 구성도로 실제 학습 구조와 현재 실행 구조를 구분한다.
GitHub에서는 이미지를 바로 표시하고, 벡터 SVG와 편집용 D2 소스도 제공한다.

## 1. 전체 강화학습 구조

![강화학습 전체 흐름](01-training-overview.png)

경험을 일정량 모은 뒤 PPO가 가중치를 업데이트하고, 바뀐 정책으로 다시 경험을 수집한다.
보상 하나를 받는 것과 모델 업데이트 한 번은 같은 단위가 아니다.

## 2. Actor·Critic 모델 구조

![Actor·Critic 모델 구조](02-actor-critic-model.png)

24장의 실제 은닉층 설정 `[32, 32]`를 예시로 사용했다. 행동 분포에는 신경망 평균 출력과 탐색용 표준편차 등이 사용된다.
위 다이어그램은 역할을 묶어 보여주는 구성도다. Critic은 보상 함수를 대신 만들지 않으며, 학습에서는 두 모델의 관련 가중치를 갱신한다.
20장에는 이 신경망이 없고, 21장의 관측 7개와 24장 예시의 관측 4개도 구분한다.

## 3. 20번 파일 실행 구조

![20장 코드 실행 구조](03-lesson20-structure.png)

환경이 반환한 관측을 다음 행동 생성에 사용하지 않는다. 결과는 로그로 기록하며 행동은 계속 무작위다.

## 4. 환경 step과 물리 step

![환경 step과 물리 처리 순서](04-environment-step.png)

환경 4개는 같은 환경 step 안에서 함께 진행하고, 완료한 환경만 개별 리셋한다.
완료 환경의 보상·플래그는 끝난 에피소드 결과지만 반환 관측은 새 에피소드 초기 상태일 수 있다.
다이어그램은 주 처리 순서를 나타내며 recorder 등 부가 경로는 생략했다.

| 단위 | 20장 설정 |
|---|---|
| 물리 step | 1/120초 |
| 환경 step | 물리 step 2회 · 1/60초 |
| 에피소드 상한 | 5초 · 약 300 환경 step |
| 데모 상한 | 2000 환경 step |
| 학습 iteration | 20장에는 없음 |

## 실제 학습으로 연결하려면

환경에 정책 신경망·학습 래퍼·PPO 실행기를 연결한다.
24장의 `OnPolicyRunner`와 `runner.learn()`이 경험 수집과 가중치 학습을 수행하는 연결에 해당한다.

[강화학습 개념](../README.md) · [20장 실습](../../../20-base-env/README.md) · [20장 코드 리뷰](../../../20-base-env/code-review.md)

처리 순서는 [Isaac Lab v2.3.2 환경 구현](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)을 기준으로 정리했다.

## 5. 보상 값과 로그의 관계

![보상 처리와 누적 단위](05-reward-accounting.png)

## 6. 21장 코드 실행 구조

![21장 환경 구성과 실행](06-lesson21-structure.png)

## 7. 21장 관측 구성

![관측 항을 합쳐 7차원 입력 구성](07-observation-schema.png)

## 8. 21장 보상 구성

![각 보상 항과 가중치 합](08-reward-schema.png)

## 9. 관측 전처리 순서

![함수·modifier·noise·clip·scale·그룹 연결](09-observation-processing.png)

## 10. 액션 공간과 구동 연결

![입력 행동을 힘·위치·속도 명령으로 변환](10-action-space.png)

세 가지 중 선택한 모드의 명령을 전달한다. 목표값과 실제 상태는 같지 않으며 actuator 게인과 힘 제한을 함께 확인한다.
[22장 실습·영상](../../../22-action-space/README.md) · [22장 코드 리뷰](../../../22-action-space/code-review.md)

## 사용 도구와 편집 가능한 원본

[D2](https://github.com/d2lang/d2)의 ELK 레이아웃으로 생성했다.
색은 진한 글자와 파란 강조색 중심으로 줄이고, 설명은 본문으로 옮겨 도형 안에는 핵심 단계만 표시했다.
도형 높이·글자·단계 간격을 줄여 전체 크기를 다듬었다. 한글 폰트를 포함한 SVG와 문서 표시용 PNG를 함께 제공한다. D2 소스로 내용과 배치를 수정할 수 있다.

| 구성도 | 확대용 SVG | D2 소스 |
|---|---|---|
| 강화학습 전체 흐름 | [SVG](01-training-overview.svg) | [D2](01-training-overview.d2) |
| Actor·Critic 모델 구조 | [SVG](02-actor-critic-model.svg) | [D2](02-actor-critic-model.d2) |
| 20장 코드 실행 구조 | [SVG](03-lesson20-structure.svg) | [D2](03-lesson20-structure.d2) |
| 환경 step과 물리 처리 순서 | [SVG](04-environment-step.svg) | [D2](04-environment-step.d2) |
| 보상 로그와 누적값의 관계 | [SVG](05-reward-accounting.svg) | [D2](05-reward-accounting.d2) |
| 21장 커스텀 관측·보상 실행 구조 | [SVG](06-lesson21-structure.svg) | [D2](06-lesson21-structure.d2) |
| 21장 관측 7차원 구성 | [SVG](07-observation-schema.svg) | [D2](07-observation-schema.d2) |
| 21장 보상 항과 가중치 | [SVG](08-reward-schema.svg) | [D2](08-reward-schema.d2) |
| 관측 전처리 순서 | [SVG](09-observation-processing.svg) | [D2](09-observation-processing.d2) |
| 액션 공간과 구동 연결 | [SVG](10-action-space.svg) | [D2](10-action-space.d2) |

다시 생성하려면 D2 v0.9.0과 Python의 `fonttools`, `resvg-py`가 필요하다.

```bash
python learning-notes/reinforcement-learning/diagrams/render_d2.py
```

폰트는 [Noto Sans KR](https://github.com/google/fonts/tree/main/ofl/notosanskr) 기반의 서브셋이다.
수정본은 Training Diagram Sans 이름으로 제공하며 [SIL Open Font License](fonts/OFL.txt)를 적용한다.

[21장 실습](../../../21-observation-reward/README.md) · [21장 코드 리뷰](../../../21-observation-reward/code-review.md)
