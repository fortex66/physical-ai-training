# 25번 코드 리뷰 — 추론과 평가 통계의 의미

[실습 기록](README.md) · [원본 코드](25_evaluate_policy.py)

## 1. 업데이트 없는 추론과 평균 행동

Runner를 생성하고 `load(..., load_optimizer=False)`로 학습 상태 중 모델 가중치를 복원한 뒤 `get_inference_policy()`를 얻는다. 평가 루프에서 `runner.learn()`·backward·optimizer.step은 호출하지 않는다.
`max_iterations=0` 설정 자체가 추론을 구현하는 것은 아니며, 실제 학습 호출이 없는 실행 흐름이 핵심이다.

참조 RSL-RL v3.1.0에서 `get_inference_policy()`는 모델을 eval 모드로 바꾸고 `act_inference`를 반환한다. 이 함수는 Actor의 평균 출력을 사용하며 탐색 분포에서 sample하지 않는다.
`no_grad()`는 autograd 기록을 끄는 기능이다. `model.eval()`은 dropout/정규화 등 모델 모드에 관한 기능이다. 둘만으로 임의의 확률적 정책이 deterministic으로 바뀌지는 않는다.

이번 추론은 저장한 경로를 재생하지 않는다. 매번 관측 7개를 입력해 카트 힘 행동 1개를 계산한다. Critic은 Runner 구조에서 함께 로드하지만 이 행동 계산에는 쓰지 않는다.

## 2. 체크포인트 탐색은 best 선택이 아니다

`find_latest_checkpoint()`는 search_paths를 우선순위대로 순회하고, **처음 파일이 있는 폴더 안에서** 파일명 iteration 숫자가 가장 큰 것을 반환한다.
모든 폴더의 최신 파일이나 수정 시간이 최신인 파일을 고르는 것은 아니다. 성능 점수도 비교하지 않는다.
`model_149`가 `model_50`보다 나중인 것은 숫자 비교로 해결하지만, 나중 모델이 항상 더 좋다는 뜻은 아니다.

이 저장소의 폴더명은 `24-train-cartpole`이며 원본 자동 탐색 후보의 `24_train_cartpole`과 다르다. 원본 코드 보존을 위해 실행 명령에는 `--checkpoint ../24-train-cartpole/.../model_149.pt`를 명시했다.
찾지 못한 명시 경로도 경고 후 랜덤 정책으로 전환한다. 학습 정책을 평가하려는 실험에서는 누락 시 명확히 실패시키는 편이 결과 혼동을 막는다.

```python
# 개선 예시 · 제공 원본에는 적용하지 않음
if not args_cli.random and not (checkpoint_path and os.path.isfile(checkpoint_path)):
    raise FileNotFoundError(f"평가 체크포인트가 없습니다: {checkpoint_path}")
```

체크포인트에는 가중치 외에 optimizer·iteration 등도 들어갈 수 있다. 자료의 ‘가중치만 저장’은 첨부 24번 모델 전체 내용을 정확히 설명하지 않는다.
네트워크 크기뿐 아니라 activation·관측 순서·전처리·행동 단위도 맞춰야 한다. activation이 다르면 shape 오류 없이 동작 의미가 달라질 수도 있다.

## 3. 두 실행 경로의 인터페이스

랜덤 모드는 기본 환경에서 `(obs dict, reward, terminated, truncated, info)`를 받는다. 학습 모드는 wrapper에서 `(TensorDict, reward, dones, info)`를 받는다(Isaac Lab v2.3.2 참조).
정책 입력도 wrapper의 TensorDict 형식을 유지한다. 자료의 ‘텐서 하나 반환’은 버전에 따라 다르다.

학습 경로는 `terminated = dones & ~truncated`로 복원한다. task 종료와 timeout이 동시에 참인 정보는 이렇게 하면 잃는다.
엄밀한 평가에서는 기본 환경의 termination_manager 신호를 보존하거나 wrapper에서 원래 플래그를 전달하는 방식이 좋다.

```python
# 개선 예시 · wrapped step 직후 원본 manager의 task 종료 신호 확인
# Isaac Lab v2.3.2 기준 · 원본 코드에는 적용하지 않음
task_failed = env.termination_manager.terminated.clone()
time_limited = env.termination_manager.time_outs.clone()
```

현재 설정은 timeout extras를 전달하지만 finite-horizon 설정 등으로 time_outs가 없으면 복원 방식도 달라진다. 실제 라이브러리 버전과 인터페이스를 함께 확인한다.

## 4. 성공 지표와 이름이 다르다

```python
success_rate = sum(1 for length in all_lengths if length >= 290) / len(all_lengths) * 100
```

290/60≈4.83초다. 5초 전체는 300 step이며, 295 step에서 실패해도 현재 코드는 성공으로 센다.
시간 제한 자체도 보편적인 성공 판정은 아니다. 이번 balancing에서 ‘task 실패 없이 상한까지 유지’를 성공으로 정하려면 완료 시 실패 플래그까지 저장한다.

```python
# 개선 개념 · 종료 정보가 보존된 경우 완료 환경별 기록
success = bool(time_limited[idx]) and not bool(task_failed[idx]) and ep_len >= 300
```

직립 오차·카트 중앙 오차·최대 힘 등의 기준은 별도 추가해야 한다. 영상의 학습 정책은 64회 모두 300 step이므로 현재 길이 기준 달성률 100%를 기록하지만, 모든 조건에서의 성공 보장은 아니다.

## 5. 목표 에피소드 수를 초과할 수 있다

while 조건은 step 시작 시에만 `len(all_rewards) < num_episodes`를 확인한다. 같은 step에서 완료한 env를 for 루프가 모두 추가하므로 마지막 묶음에서 초과한다.
실제 랜덤 영상은 목표 64·완료 65다. 이 통계는 64회가 아닌 65회 평균이다.

```python
# 개선 예시 · 완료 목록 기록 시 목표 수를 엄밀히 제한
for idx in done_envs:
    if len(all_rewards) >= args_cli.num_episodes:
        break
    # 해당 에피소드 보상·길이·종료 플래그 기록
```

동시 완료에서 낮은 env index부터 자르면 선택 편향이 생길 수 있다. 환경별 일정 수의 에피소드를 평가하거나 동시 완료 순서·표본 규칙을 정해 함께 기록하는 방법도 있다.
모든 통계는 실제 분모와 표본 선택 규칙을 명시한다.

## 6. 공정한 비교와 통계의 한계

두 영상은 같은 핵심 Cartpole 태스크지만 학습 정책은 평균 행동, 랜덤은 clamp된 정규 난수다. 학습 행동에는 wrapper clip을 지정하지 않는다.
동일한 확률 분포끼리의 비교가 아니라 **학습한 제어기와 관측을 무시하는 baseline의 비교**다.
seed를 명시하지 않으며 모델 생성·초기화 경로도 달라 같은 환경 번호의 초기 상태가 자동으로 짝지어지는 것은 아니다. 정밀 비교에는 공통 초기 상태 목록·평가 seed·완료 표본 수를 맞추는 편이 좋다.

최대·최소는 범위이며 분산·표준편차가 아니다. 원본 코드는 표준편차나 신뢰구간을 출력하지 않는다.
제공 통계 CSV/JSON은 영상 최종 로그를 옮겼으며 원시 에피소드별 평가 데이터로 간주하지 않는다.
중도 종료 시에는 목표보다 적은 완료 기록으로도 결과가 출력될 수 있으므로 실제 완료 수를 확인한다.

## 7. 학습·평가가 공유해야 할 것

같은 정책 계약(입력 크기·순서·전처리, 액션 순서·단위·scale, 모델 구조)을 유지해야 한다.
성능 비교의 보상·초기화·종료 조건도 맞추거나 변경 사항을 기록한다. 반면 headless/GUI와 병렬 수는 학습/평가의 정의가 아니며 평가를 headless로 많이 수행할 수도 있다.
정책 배포가 stochastic이라면 그 모드의 평가도 의미 있다. deterministic 평균 행동이 모든 정책에서 반드시 최적이라는 보장은 없다.

체크포인트 선택용 평가와 최종 성능 보고용 평가를 나눠 선택에 사용하지 않은 초기 상태·seed에서도 확인한다.
26~29 확장에서도 같은 원칙으로 학습 지형과 평가 지형·랜덤화 조건을 구분한다.

## 구현 근거

- [RSL-RL v3.1.0 Runner: load·get_inference_policy](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/runners/on_policy_runner.py)
- [ActorCritic: act와 act_inference](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/modules/actor_critic.py)
- [Isaac Lab v2.3.2 VecEnvWrapper](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py)
- [TerminationManager 종료 신호](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/termination_manager.py)

위 라이브러리는 설명의 참조 구현이며 첨부 자료로 설치된 RSL-RL 버전까지 확정한 것은 아니다.
