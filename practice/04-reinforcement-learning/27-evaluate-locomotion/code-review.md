# 27번 코드 리뷰 — 고정 보행 정책과 평가 지표

[실습 기록](README.md) · [제공 코드](27_evaluate_locomotion.py)

## 1. 원본과 평가 흐름

제공 파일은 기준 튜토리얼과 동일하다. CLI 기본은 Flat ANYmal-B·환경 16개·에피소드 20회다.
환경 Cfg 로드 → `gym.make` → wrapper → Runner 생성·모델 load → 추론 함수 → 완료 episode 통계 순서다.
26번과 같은 Actor·Critic MLP `[128,128,128]`·ELU를 사용한다. activation과 관측 순서·단위·행동 scale도 맞춰야 하며 크기만 맞는 것으로 충분하지 않다.
`max_iterations=0` 자체가 추론을 구현하는 것은 아니다. 실제로 learn/backward/optimizer 업데이트를 호출하지 않는다.

## 2. 평균 행동과 환경 노이즈

참조 RSL-RL v3.1.0의 get_inference_policy는 eval 모드의 act_inference를 반환하고 Actor 평균을 사용한다. no_grad는 autograd 기록을 끈다.
학습된 탐색 표준편차가 체크포인트에 들어 있어도 이 행동 선택에서는 Gaussian sample을 사용하지 않는다.
환경 Cfg는 학습용 Flat을 로드하므로 관측 노이즈·랜덤 상태·속도 명령·외란 등이 남을 수 있다. Play 태스크로 자동 바꾸거나 seed를 고정하는 코드는 없다.
PPO 모델 가중치는 고정이지만 actuator-net의 시간 상태나 물리 상태는 진행된다.

## 3. 생존률의 정의가 자료 설명과 다르다

코드의 `int(max(all_lengths)*0.9)`는 **표본 최장 길이**의 90%다. 주석의 ‘평균 길이’도 아니고 환경 최대 episode 길이를 직접 읽는 것도 아니다.
자료의 ‘timeout 도달 비율’과 같지 않다. 전부 40 step 실패인 표본이라도 threshold=36·생존률=100%가 될 수 있다.
영상의 100%는 900 step 기준이며 실제 완료 행은 모두 1000 step timeout으로 출력됐다. 이 별도 관측과 지표 정의를 구분한다.

개선 시에는 모든 정책에 같은 평가 horizon을 적용하고 원래의 task 실패·timeout 플래그를 저장한다.

```python
# 개선 개념 · 제공 원본에는 적용하지 않음
horizon = unwrapped.max_episode_length
# env.step 직후 원래 종료 신호를 보존
failed = unwrapped.termination_manager.terminated.clone()
time_limited = unwrapped.termination_manager.time_outs.clone()
# 완료 환경 idx에서 결과에 함께 저장
survived = bool(time_limited[idx]) and not bool(failed[idx]) and ep_len >= horizon
```

직립 유지·속도 오차·구동 부담 등의 작업 기준은 추가로 설계해야 한다. 시간만 채우고 명령을 잘 따르지 못하는 정책도 있을 수 있다.

## 4. wrapper에서 플래그 복원

참조 Isaac Lab v2.3.2 wrapper는 TensorDict·reward·dones·extras를 반환한다. dones는 task 종료와 truncation의 OR이며 조건에 따라 time_outs를 extras에 넣는다.
현재 코드는 `terminated = dones & ~truncated`로 복원해 두 플래그가 동시에 참인 경우 task 실패 정보를 잃는다. 결과 reason도 timeout을 우선 출력한다.
엄밀한 평가에서는 원래 manager 플래그를 보존하거나 wrapper의 원래 종료 정보를 별도로 전달하는 편이 낫다. 화면의 timeout 표시만으로 동시 실패까지 배제할 수는 없다.
wrapper 생성이 초기 reset을 수행하므로 get_observations로 시작한다. 완료 환경은 자동 리셋되며 전체 reset을 매 완료마다 추가할 필요가 없다.

## 5. 25번과 달리 완료 표본 수를 제한한다

done_envs 내부 루프에서 목표 에피소드 수에 도달하면 break하므로 동시 완료로 20회를 넘겨 기록하지 않는다. 영상도 실제 20회다.
다만 먼저 끝난 환경의 기록과 동시 완료 시 낮은 env index가 선택되는 규칙이 있다. 환경별 동일 수·여러 seed·같은 초기 상태 목록으로 평가하면 비교가 더 명확하다.
사용자가 GUI를 먼저 종료하면 목표 수 미달이어도 완료된 기록으로 통계가 출력될 수 있어 실제 분모를 확인해야 한다.

## 6. 자동 탐색의 의미와 저장소 경로

search_paths 중 첫 체크포인트가 있는 경로를 사용한다. 그 폴더의 직접 파일을 숫자로 정렬하고, 직접 파일이 없으면 하위 폴더 파일을 `(부모 경로 문자열, iteration)` 순서로 정렬한다.
즉 전체 후보에서 iteration이 가장 큰 모델·수정 시간이 최신인 모델·성능이 가장 좋은 모델을 고르는 기능이 아니다. 하위 run 선택은 폴더명 문자열 순서에 좌우된다.
문서 문자열의 탐색 경로 설명보다 실제 search_paths가 기준이다.

원본은 `26_train_locomotion`을 찾지만 저장소는 `26-train-locomotion`이므로 실행 예시에서 model_299 경로를 명시했다.
명시한 경로가 잘못돼도 경고 후 랜덤으로 전환한다. 학습 정책 실험에서는 누락 시 예외를 내는 편이 혼동을 줄인다.

## 7. 랜덤 비교와 입력 범위

랜덤 모드는 12차원 정규 난수에 clamp(-1,1)을 적용한다. 학습 정책은 Actor 평균이며 wrapper에 clip_actions를 지정하지 않는다.
따라서 학습 행동도 자동으로 ±1이라고 가정하지 않는다. 관절 위치 변환·actuator 토크 제한은 입력 clamp와 별개다.
둘은 다른 분포의 제어기를 비교하는 실험이다. 제공 영상에는 학습 정책만 있으므로 자료의 랜덤 결과 예시를 실제 결과로 옮기지 않았다.

## 8. 보상·통계와 모델의 내용

영상은 20회·평균 보상 23.99·길이 1000·최대/최소 25.97/21.75다. episode CSV는 화면의 반올림 값 전사이며 원시 reward 로그가 아니다.
최대/최소는 범위를 보여주지만 분산·표준편차와 같지 않다. JSON의 표본 표준편차는 이 반올림된 20개 보상으로 계산한 근사값이며 모집단의 변동성을 확정하지 않는다.
26번 최근 학습 버퍼 평균 18.93과 27번 고정 정책의 20회 평균 23.99는 행동 선택·표본·집계 조건이 달라 단순 학습 전후 차이로 보지 않는다.

26번 checkpoint에는 모델뿐 아니라 optimizer·iteration 등도 들어 있다. 자료의 ‘가중치만 저장’은 전체 파일을 정확히 설명하지 않는다. 평가의 load_optimizer=False는 optimizer 복원만 생략한다.
영상에서 학습 정책 로드는 확인했지만 보이는 구간만으로 사용한 파일 전체 경로를 확정하지 않았다. 저장소 실행 안내는 보존된 model_299를 명시한다.

## 9. 게시 자료와 재현 범위

원본 78.61초 영상 끝에 개인 창이 있어 게시용은 안전한 0~70초 구간으로 만들었다. 결과 캡처는 실제 viewport·터미널에서 추출했다.
제공 코드는 수정하지 않았으며 체크포인트는 26번 저장 파일로 연결한다. 평가를 cloud에서 재실행하거나 랜덤 결과를 새로 생성하지 않았다.

## 구현 근거

- [Isaac Lab v2.3.2 ANYmal-B Flat](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_b/flat_env_cfg.py)
- [기본 보행 환경 Cfg](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py)
- [VecEnvWrapper](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py)
- [RSL-RL v3.1.0 Runner](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/runners/on_policy_runner.py)
- [ActorCritic 추론](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/modules/actor_critic.py)

위 버전은 설명에 사용한 참조 구현이며 설치된 RSL-RL 버전 전체를 첨부 자료로 확정한 것은 아니다.
