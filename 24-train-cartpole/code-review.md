# 24번 코드 리뷰 — PPO가 실제로 학습하는 지점

[실습 기록](README.md) · [코드](24_train_cartpole.py)

## 1. 23번과의 차이: 행동 생성과 업데이트를 Runner에 맡긴다

환경의 핵심 관측 7·행동 1·보상 6·종료 3·reset 설계는 23번과 같다. 제공 24번 코드는 기준 튜토리얼과 일치한다.
`RslRlVecEnvWrapper` → `OnPolicyRunner` → `runner.learn()`에서 학습이 시작된다.
main에 optimizer 코드가 보이지 않아도 학습 라이브러리 안의 수집·return 계산·loss·backward·optimizer.step이 호출된다.

이번 파일은 CartpoleTrainEnvCfg를 다시 정의하며 23번 파일을 import하지 않는다. 같은 설정을 여러 파일에 복제하면 학습·평가 환경이 달라질 수 있어 공통 모듈 분리가 개선 방향이다. 원본은 보존했다.

## 2. Wrapper 인터페이스: 자료의 설명은 버전에 따라 다르다

Isaac Lab v2.3.2 구현은 환경의 `(obs, reward, terminated, truncated, extras)`를 RSL-RL의 `(TensorDict, reward, dones, extras)`로 변환한다. `dones`는 두 종료 플래그의 OR이다.
자료의 ‘obs dict를 텐서 하나로 반환’은 이 버전의 정확한 타입 설명과 다르다. `policy` 그룹을 보존하는 TensorDict이며 구버전은 인터페이스가 다를 수 있다.
finite-horizon 설정이 아닌 경우 extras에 `time_outs`를 전달한다. wrapper 생성 때 환경 reset도 호출한다.

라이브러리 구현 설명에는 Isaac Lab v2.3.2와 RSL-RL v3.1.0을 참조했다. 첨부 자료에는 설치된 RSL-RL 버전 정보가 없으므로 실제 설치 버전을 확정한 것은 아니다.

## 3. 가장 중요한 행동 차이: 23번의 clamp가 사라진다

23번은 `randn(...).clamp(-1, 1)`이었다. 24번은 Actor 분포에서 샘플하며 `RslRlVecEnvWrapper(env)`에 `clip_actions`를 넘기지 않는다. JointEffortActionCfg의 clip도 없다.
따라서 정규분포 행동은 ±1을 넘을 수 있고 `100 × action` 명령 힘도 ±100 N을 넘을 수 있다. 기본 actuator 힘 제한·감쇠는 별도 적용된다.

±1 입력을 의도하면 wrapper의 clip을 명시하는 개선을 고려할 수 있다.

```python
# 개선 예시 · 원본에는 적용하지 않음
# 행동 분포·환경에 들어가는 입력이 달라지므로 실험 조건으로 기록
env = RslRlVecEnvWrapper(base_env, clip_actions=1.0)
```

클리핑된 명령과 정책이 샘플한 행동 확률의 관계도 고려해야 한다. 기존 체크포인트에 사후 clip을 추가하면 동작·보상 조건이 달라진다.
`energy` 항은 환경 ActionManager가 받은 raw action 제곱합으로, 실제 전력이나 순 구동력을 측정하는 항이 아니다.

## 4. PPO clip·Advantage·KL을 정확히 읽기

확률비 `new_probability / old_probability`를 Advantage와 곱해 정책 목적을 만든다. PPO는 clip된 항과 원래 항 중 보수적인 목적을 선택한다.
clip=0.2는 목적함수의 확률비 범위 0.8~1.2에 사용하며, 모든 행동 확률을 강제로 이 범위에 넣거나 가중치를 ±20%로 제한하지 않는다.

GAE는 여러 시간의 TD 오차를 할인·lambda로 합쳐 Advantage를 만든다. ‘Advantage=즉시 보상−Value’는 일반적으로 틀리며, 이후 보상과 bootstrap 가치가 포함된다.
Critic의 target도 완료 에피소드 실측 총점만이 아니라 GAE/가치 bootstrap을 포함한 return target이다.

adaptive learning rate는 고정 0.001이 아니다. 참조 RSL-RL 구현은 평균 KL이 desired_kl의 2배를 넘으면 낮추고, 절반보다 작으면 올리는 등으로 조절한다. ‘0.01을 넘으면 언제나 감소’라고 읽으면 안 된다.
학습 로그 최종 learning rate도 약 0.001975로 시작 설정과 다르다.

## 5. 수집 길이·epoch·iteration은 다른 단위다

1024환경 × 16 step = 16,384개 전이를 한 rollout으로 수집한다. 환경당 에피소드 최대 300 step과 달라 에피소드를 완결하지 않고도 학습한다.
4 mini-batch × 5 epoch는 기본 구성에서 iteration당 optimizer 20회다. 150 iteration이면 3000회이며 새로운 환경 경험은 총 2,457,600개다.
같은 rollout을 5번 사용해도 새로운 전이 수가 5배 늘어나는 것은 아니다.
영상 최종 2,457,600과 이 계산이 일치한다. 자료의 다른 총 step 값은 이번 실행 결과로 인용하지 않는다.

## 6. timeout 처리와 시작 카운터

`init_at_random_ep_len=True`는 episode_length_buf만 랜덤하게 초기화한다. 물리 상태를 과거로부터 미리 진행하지 않는다. 첫 episode는 실제 누적 길이·보상이 짧게 측정될 수 있다.

참조 RSL-RL PPO는 `time_outs`에 대해 rollout에 저장한 transition의 가치로 reward bootstrap 보정을 하고, rollout 끝에서는 마지막 관측 가치로 return을 계산한다.
이것을 ‘자동 리셋 뒤 관측이 곧 실패 직전 관측’이라고 해석하면 안 된다. 일반적인 올바른 timeout 처리 개념과 실제 라이브러리 근사 구현을 구분한다.
wrapper의 time_outs가 truncation을 전달하고 PPO가 이를 쓰므로 task 종료와 timeout 동시 발생 처리도 실제 버전 구현을 확인해야 한다.

## 7. 저장 경로와 재현 정보

현재 경로는 작업 디렉토리 기준 `logs/rsl_rl/cartpole_tutorial`로 고정이다. `run_name`은 빈 문자열이며 경로 생성에서 사용하지 않는다. 반복 실행하면 체크포인트 이름이 충돌하고 이벤트가 같은 폴더에 쌓일 수 있다.

```python
# 개선 예시 · 원본에는 적용하지 않음
from datetime import datetime
run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
log_root_path = os.path.abspath(os.path.join(
    "logs", "rsl_rl", agent_cfg.experiment_name, run_id))
```

원본 zip·펼친 이벤트·모델을 보존하고 파일 크기·SHA256 manifest도 추가했다.
첨부 로그에는 자동 저장된 환경/학습 설정 파일과 라이브러리 버전 기록은 없다. 소스·CLI·seed·패키지 버전·환경 설정을 함께 저장하면 재현에 도움이 된다.
코드가 CLI 환경 수·iteration은 연결하지만 명시적인 사용자 seed 설정과 학습 재개 load 호출은 하지 않는다.
체크포인트를 보유한다고 같은 학습을 처음부터 완전히 재현할 수 있는 것은 아니다.

## 8. 체크포인트 내용과 model_0의 의미

저장 주기는 50이고 최종 저장도 수행해 제공 파일은 0·50·100·149다. iteration은 0부터 표기하며 model_0은 첫 rollout 업데이트 후 저장한다.
참조 Runner는 model_state_dict, optimizer_state_dict, iter, infos 등을 저장한다. 최종 모델 메타데이터의 actor.0.weight `(32,7)`과 actor.4.weight `(1,32)`, iter 149를 확인했다.
모델은 관측 순서·scale·단위·종료·구동 설정과 함께 사용해야 한다. 평가하려면 Actor 실행과 같은 입력 전처리가 필요하며 Critic은 행동 생성에 필수는 아니다.

## 9. TensorBoard 지표를 성공률로 단정하지 않기

- `Train/mean_reward`·`mean_episode_length`는 참조 Runner에서 최근 완료 에피소드 버퍼(최대 100개)의 평균이다. 전체 1024환경 평균이나 iteration당 보상은 아니다.
- `Episode_Reward/*`는 Isaac Lab에서 완료 환경의 항별 누적을 **최대 에피소드 시간 5초로 나눈 값**이다. 실제로 실행한 각 episode 길이로 나눈 값이나 총 보상과 다르다.
- `Episode_Termination/*`는 manager의 환경별 마지막 완료 상태 집계를 바탕으로 한다. 값 1.0을 별도 평가 성공률 100%로 바꾸지 않는다. 아직 완료하지 않은 환경의 초기 기록은 0일 수 있어 학습 초반의 작은 실패 지표도 낮은 실패율로 단정하지 않는다.
- `Loss/entropy`는 연속 분포의 differential entropy여서 음수도 가능하다. 이번 최종 -0.8869는 오류 표시가 아니다.
- value loss와 surrogate loss는 크기·부호만으로 성능을 판단하지 않는다. target 변화와 데이터 분포도 영향을 준다.
- KL을 학습률 조절에 사용해도 제공 이벤트에 KL scalar가 자동으로 저장되는 것은 아니다. 이번 파일에는 별도 KL tag가 없다.

제공 이벤트에는 0~149의 150 iteration 기록이 있다. `*/time` tag의 step은 시간 축이므로 iteration tag와 혼동하지 않았고 CSV에서는 별도 시간 축 tag를 제외했다.
학습 지표는 좋아졌지만 최종 모델의 독립 평가·새 초기화·seed 비교는 이후 25번에서 수행한다.

## 구현 근거

- [Isaac Lab v2.3.2 Wrapper](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py)
- [Reward Manager의 episodic 로그](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/reward_manager.py)
- [Termination Manager](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/termination_manager.py)
- [RSL-RL v3.1.0 PPO](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/algorithms/ppo.py)
- [RSL-RL v3.1.0 Runner](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/runners/on_policy_runner.py)
- [RSL-RL v3.1.0 ActorCritic](https://github.com/leggedrobotics/rsl_rl/blob/v3.1.0/rsl_rl/modules/actor_critic.py)
