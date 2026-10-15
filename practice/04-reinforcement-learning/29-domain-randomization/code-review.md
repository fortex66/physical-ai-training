# 29번 코드 리뷰

사용자 제공 [원문 코드](29_domain_randomization.py)는 보존했다. PinkWink 튜토리얼 기준 commit `14f85fc6edece7cbb1faa50aa9fe3adef205e87a`의 29번 파일과 동일하다.
강의 PDF와 Isaac Lab **v2.3.2** 소스를 대조했으며 클라우드에서 Isaac Sim 물리 시뮬레이션을 재실행하지 않았다.

## 1. 학습 코드가 아닌 이벤트 데모

438행 `torch.randn(env.num_envs, 1)`로 행동을 만든다. obs를 Actor에 넣는 코드, Critic, PPO Runner, rollout 학습 버퍼, optimizer, 체크포인트 로드·저장이 없다.
443행의 reward 계산과 자동 reset은 환경 기능이다. 보상을 받는다는 사실만으로 학습이 일어나는 것은 아니다.
500 step으로 끝내며 영상은 16환경·완료24회를 보여준다. 강건성 향상을 주장하려면 별도의 학습·대조 평가가 필요하다.
argparse description의 ‘28’ 표기는 원문의 단순 오기이며 실제 파일은 29번이다.

## 2. 두 interval 이벤트가 발동하지 않는 설정

`episode_length_s=5`, `dt=1/120`, `decimation=2`로 상한은 300 환경 step이다.
`EventTermCfg.is_global_time` 기본값은 False이며 `EventManager.reset()`이 종료 환경의 남은 interval 시간을 새로 샘플링한다.
`ManagerBasedRLEnv.step()`은 종료·보상을 계산하고 종료 환경을 reset한 뒤 interval 이벤트를 처리한다.
따라서 대기 10~15초인 push와 5~10초인 외력은 최대 5초 episode에서 트리거되지 않는다. 막대가 오래 움직인다는 시각적 관찰이나 총 시뮬레이션 시간이 5초를 넘었다는 사실로 발동을 추론하면 안 된다.

491~499행 요약은 설정 내용을 무조건 출력하는 문자열이며 실행 이력이나 강건성 측정값이 아니다. PDF 17쪽의 ‘시뮬 시간이 5초/10초 누적되면 자동 적용’ 표현은 이번 기본 타이머·episode 길이에서는 성립하지 않는다.

관찰용 수정 선택지는 다음과 같다. 원문에는 적용하지 않았다.

- episode 5초를 유지한다면 push `(1,2)`, 외력 `(0.5,1)`초처럼 더 짧은 간격을 사용한다. term별 호출 횟수와 시간을 기록한다.
- 원래 간격을 유지한다면 episode와 전체 실행을 충분히 늘리고 초기 실패를 고려한다. 예컨대 episode 20초·전체 1800 환경 step(30초)은 시간 예산만 늘리는 제안이며 호출·효과 확인은 별도로 필요하다.
- `is_global_time=True`는 reset과 무관한 공통 타이머로 의미를 바꾸는 선택이다. 모든 환경이 같은 시점에 호출되어 독립 외란과 다르고, 총 8.33초 실행으로 10~15초 push를 볼 수 없는 점도 남는다.

## 3. startup 질량·관성의 의미

194~202행은 모든 body에 기본 질량 기준 uniform `[-.5,.5]kg`를 더한다. 모든 body의 질량을 `.5~1.5kg`로 설정하는 코드가 아니다.
v2.3.2 `randomize_rigid_body_mass`는 default_mass를 기준으로 연산해 반복 호출 시 오프셋이 누적되지 않으며 기본 `min_mass=1e-6`로 제한한다.
기본 `recompute_inertia=True`라서 기본 관성에 질량비를 곱한다. 형상이나 질량 중심을 함께 재설계하는 것은 아니며 균일 밀도 가정을 포함한다.
시뮬레이터의 최소 질량 제한이 공학적으로 타당한 랜덤화 범위를 보장하는 것은 아니다. 작은 부품에는 같은 ±0.5kg 대신 측정 근거가 있는 비율·절대 범위를 설계한다.
startup은 생성 시 한 번이며 일반적인 episode reset에서 다시 샘플링하지 않는다. episode마다 새 질량을 주고 싶다면 PhysX·CPU 비용·동역학 일관성까지 고려해 별도 설계한다.

## 4. reset과 즉시 출력된 관측

reset_cart와 reset_pole은 각 관절의 기본 위치·속도에 오프셋을 더하고 soft limit으로 제한한 뒤 시뮬레이터에 쓴다.
영상의 첫 4환경은 초기 위치가 서로 다르고 `(16,4)` 관측을 보여준다. 그러나 reset 직후 속도 출력은 모두 `0.0000`이다.
따라서 표는 위치·각도 변화의 근거로 사용하고 속도가 실제로 설정 범위에 들어갔다고 확대 해석하지 않았다.
속도 검증에는 이벤트 내부 샘플·write 직후 상태·시뮬레이션 동기화 후 상태를 나누어 기록해 캐시/갱신 시점과 설정 효과를 확인할 필요가 있다. 이 자료만으로 0 출력의 원인을 확정하지 않았다.

## 5. 속도 push와 외력은 서로 다른 조작

v2.3.2 `push_by_setting_velocity()`는 현재 root 속도를 읽고 지정 범위의 샘플을 **더한 뒤** write한다. 구현상 x 외 축은 0을 더하므로 기존 성분이 유지된다. 함수 docstring의 ‘속도 설정’만 보고 완전 대입과 혼동하지 않는다.
실제 임펄스와 똑같은 접촉 과정이나 힘 전달을 재현하지는 않는다. 특히 고정 베이스 Cartpole의 root 교란을 카트 slider 관절 외란과 같다고 가정하지 말고 대상 링크·관절 반응을 확인한다.

`apply_external_force_torque()`는 각 body에 3축 힘·토크를 샘플링해 permanent wrench 버퍼에 기록한다. 그 뒤 `write_data_to_sim()`에서 물리 step마다 적용되며 reset 또는 다음 설정에서 갱신/해제된다.
`force_range=(-1,1)`은 각 축 성분 범위이며 합력 크기가 항상 1N 이하라는 뜻은 아니다. 이 term은 별도 `is_global=True`를 주지 않으므로 기본 body 로컬 좌표계의 wrench이며 항상 월드 방향으로 일정한 바람이라고 해석하지 않는다.
현재 코드에서는 interval이 트리거되지 않아 이 외력 효과를 영상으로 검증했다고 주장하지 않는다.

## 6. 기존 Cartpole PPO 환경과 같다는 설명의 한계

이번 관측은 `joint_pos_rel(2)+joint_vel_rel(2)=4`이고 corruption=False다. 질량·외력은 직접 관측하지 않는다.
24번에서 사용한 7입력 정책과는 입력 구조가 다르므로 기존 checkpoint를 그대로 load하는 데모가 아니다.
종료는 timeout과 카트 위치 ±3m 이탈이며 막대 각도 실패 조건은 없다. 23번의 ‘완전한 환경’을 그대로 복사했다는 설명으로 막대 각도 종료까지 있다고 가정하지 않는다.

행동은 unbounded 표준정규분포다. `scale=100`만으로 ±100N 제한을 보장하지 않는다. 실제 actuator 한계와 action clip 설정은 별개다.
보상은 alive·종료 패널티·막대 편차·카트/막대 속도 항이며 RewardManager가 환경 dt를 곱한다. 474행은 현재 step의 환경 평균이고 episode 평균 누적 보상과 다르다.
16환경×500step은 8,000개 병렬 전이지만 500번의 학습 업데이트도, 8,000개 학습 샘플을 저장했다는 뜻도 아니다.

## 7. ‘필수적’, ‘더 강건하다’는 측정과 구분

랜덤화는 널리 사용하는 전이·강건성 기법이지만 모든 sim-to-real 시스템의 필수 조건이거나 적용만 하면 성능이 좋아지는 보장은 아니다.
현실 조건이 선택한 범위에 들어오는지, 정보가 충분한지, 제어 목적에 맞는지를 검증해야 한다. 표준 환경 학습 정책과 랜덤화 환경 학습 정책을 동일한 미사용 조건에서 여러 seed로 비교한다.

## 참고 구현

- [이벤트 함수·질량·push·외력·reset](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/mdp/events.py)
- [EventManager 타이머·reset·apply](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/event_manager.py)
- [EventTermCfg 기본값](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/managers/manager_term_cfg.py)
- [ManagerBasedRLEnv step·reset·startup](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [Articulation 외력 적용·reset](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/assets/articulation/articulation.py)
