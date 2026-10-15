# 28번 코드 리뷰

[원문 코드](28_terrain_generation.py)는 수정하지 않았다. 사용자 첨부 코드·강의 PDF와 Isaac Lab **v2.3.2** 공개 구현을 대조했다. 클라우드에서 Isaac Sim 물리 실행을 다시 수행한 결과는 아니다.

## 1. 학습 없는 평가라는 점

232~254행에서 Flat Cfg의 terrain을 교체하고 환경을 만든다. 282~285행은 네트워크 생성·모델 로드·추론 함수 획득이다.
312~352행은 정책 추론과 환경 step·완료 episode 수집이다. `runner.learn()`·backward·optimizer step이 없다.
`max_iterations=0`만으로 설명하기보다 **학습 함수를 호출하지 않는다**는 것이 직접적인 근거다.
기본 관측 48·행동 12, Actor/Critic hidden `[128,128,128]`, ELU를 유지한다. 관측 크기뿐 아니라 순서·단위·정규화·행동 scale도 체크포인트와 맞아야 한다.

## 2. 강의의 ‘차원과 분포는 같다’는 보완 필요

PDF 6쪽은 관측/액션의 ‘차원과 분포는 같지만’ 물리가 달라진다고 표현한다.
정확히는 **입출력 규격은 유지하지만 실제 관측·행동의 분포까지 같다는 보장은 없다.** 지형 접촉으로 몸 자세·속도·관절 상태가 바뀌기 때문이다.
‘환경이 바뀌면 다시 학습해야 한다’, 코드 375~377행의 ‘일반화되지 않습니다’도 일반 법칙이 아니다.
해당 문구는 통계와 무관하게 출력되는 고정 문자열이다. 다른 체크포인트가 잘 걸어도 그대로 출력하므로 실제 성능 판정에 대신 쓰면 안 된다.

## 3. terrain만 대입해도 엄격한 단일 변수 실험은 아니다

기존 Flat terrain은 v2.3.2에서 `friction_combine_mode="multiply"`, `restitution_combine_mode="multiply"`다.
244~248행 새 `RigidBodyMaterialCfg`는 이를 명시하지 않아 기본 `average`를 사용한다. 접촉 쌍의 최종 결합은 양쪽 재질 설정과 PhysX 우선순위도 따르므로 실제 마찰계수가 얼마나 달라졌는지는 이 필드만으로 확정하지 않는다.
Cfg 초기화 당시 `sim.physics_material`은 기존 지면 재질을 참조하며, 새 terrain을 대입한다고 해당 필드까지 자동 동기화되는 것은 아니다.
엄밀한 비교에서는 기존 physics material 설정을 복사해 유지하고, 시작 위치·seed·명령·노이즈·외란도 맞춘다.
단, source/target의 지형 때문에 상태 분포가 달라지는 것은 Domain Shift의 핵심이며 강제로 같게 맞추려는 대상이 아니다.

## 4. 지형 생성 curriculum과 환경 curriculum

104~149행 `curriculum=True`는 TerrainGenerator의 난이도별 배치 방식이다. 행 r의 난이도는 `(r+uniform())/4`로 정해지며 끝값 0·1을 정확히 배치한다는 뜻이 아니다.
Flat Cfg의 `curriculum.terrain_levels=None`은 그대로다. 242행 `max_init_terrain_level=None`은 모든 행에서 시작할 수 있게 한다.
따라서 **쉬운 곳부터 시작해 성공할 때 승급하는 학습**은 이 코드에 없다. `num_cols` 자체가 종류 수는 아니며 이번 4종·각 25%·4열 조합에서 종류별 한 열이 된다.
`num_envs`는 타일 수와 다르다. importer는 종류 열을 환경 ID로 배분하고 난이도 행을 무작위 배정한다. 환경끼리 같은 타일 origin을 사용할 수 있지만 별도 병렬 환경이라는 구분은 유지한다.

## 5. 먼저 완료한 N개를 모으는 표본 편향

312·348행은 전 환경에서 **종료가 먼저 발생한 episode N개**를 모으면 멈춘다.
예를 들어 환경 A가 100 step마다 실패하고 B가 1000 step 동안 버티면 첫 10개 완료 집계는 A의 실패에 치우칠 수 있다. B의 성공이 완료되기 전에 중단될 수도 있다.
환경160개에 목표200회면 이런 영향을 무시하기 어렵다. 같은 step에 여러 환경이 끝났을 때 마지막 일부는 낮은 env ID부터 포함하며 지형 종류와 ID가 연결되어 추가 편향이 생길 수 있다.

개선 실험에서는 `(env_id, terrain_type, terrain_level, episode_index)`마다 고정 episode 할당량을 둔다.
완료한 환경도 시뮬레이션은 계속 진행하되 할당량을 채운 환경의 추가 결과는 집계에서 제외하고, 각 할당량을 전부 채울 때까지 기다린다. 지형/난이도/seed별 결과를 별도 기록해 동일 가중치로 비교한다.
중간 중단 시 진행 중 episode도 censored 표본으로 구분하고 종료까지 본 것처럼 취급하지 않는다. 원문에는 이 변경을 적용하지 않았다.

## 6. timeout/fail과 실제 성공의 차이

320~321행은 `terminated = dones & ~time_outs`로 복원한다. 같은 step에 실패와 timeout이 동시에 참이면 실패 정보가 사라지고 timeout에 포함된다.
실패 우선 판정을 하려면 `unwrapped.reset_terminated`·`reset_time_outs` 또는 term별 로그를 **env.step 직후** 보존해 동시 플래그를 구분해야 한다. v2.3.2 기본 종료는 timeout과 base 접촉이다.
fail은 몸통 접촉 종료를 묶어 부르는 이름이며 모든 넘어짐을 시각적으로 분류한 값이 아니다. timeout도 명령 속도 오차나 목표 지형 완주를 검사하지 않는다.
27번의 표본 최대 길이×90% 기준 대신 timeout을 직접 세는 점은 개선됐지만, 공정한 평가에는 표본 편향·동시 종료·별도 작업 성공 기준도 고려해야 한다.

## 7. 체크포인트·추론·확장

- 187~217행은 첫 발견 경로의 가장 큰 모델 번호를 우선한다. 모든 run의 최적 모델을 찾아주는 함수가 아니다.
- 287~291행은 체크포인트가 없으면 랜덤으로 대체한다. 비교 실험에서는 파일 부재 시 예외로 멈추는 방식이 혼동을 줄인다.
- 314행 랜덤 행동만 `[-1,1]`로 clip한다. 학습된 평균 행동에도 같은 clip이 적용된다고 가정하지 않는다.
- 기본 task는 학습 Cfg다. 추론의 평균 행동과 별개로 관측 corruption·reset 랜덤화·명령 변화·push 등이 남아 있다.
- Rough 기본 task는 height scan을 포함한다. 이름만 바꾸고 48입력 Flat checkpoint를 load하는 것은 입력 shape 불일치가 날 수 있다.
- fine-tuning은 호환되는 네트워크 로드 후 **거친 지형에서 rollout·PPO 업데이트를 추가 실행**하는 별도 작업이다. 이 파일은 해당 기능을 구현하지 않는다.

## 근거 자료

- 사용자 제공 「강좌 28」 PDF: 3·6·8·11·13~17쪽과 원문 코드 대조. 예상 출력은 실제 측정과 구분했다.
- [Isaac Lab v2.3.2 Flat 환경](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_b/flat_env_cfg.py)
- [보행 기본 환경·보상·종료·재질](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/velocity_env_cfg.py)
- [TerrainGenerator 난이도·종류 배치](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/terrains/terrain_generator.py)
- [TerrainImporter 시작 위치 배정](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/terrains/terrain_importer.py)
- [RigidBodyMaterialCfg 기본 결합 방식](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/sim/spawners/materials/physics_materials_cfg.py)
- [환경 step·종료 플래그](https://github.com/isaac-sim/IsaacLab/blob/v2.3.2/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
