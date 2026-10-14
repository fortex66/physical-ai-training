# Mermaid로 보는 강화학습과 20장 실행 구조

20장은 환경을 테스트하며, 정책 가중치를 학습하는 코드는 아직 없다.
아래 네 다이어그램은 실제 학습 구조와 현재 실행 구조를 구분한다.

## 1. 전체 강화학습 구조

```mermaid
flowchart TD
    CONFIG["사용자 설정: 환경·관측·행동·보상·종료 + 신경망·학습 설정"] --> ENV["Isaac Lab 환경 + Isaac Sim 물리"]
    CONFIG --> ACTOR["Actor / Policy: 관측으로 행동 선택"]
    OBS["현재 관측"] --> ACTOR
    OBS --> CRITIC["Critic: 앞으로 얻을 보상 추정"]
    ACTOR -->|행동| ENV
    ENV -->|다음 관측| OBS
    ENV -->|보상·종료·다음 관측| BUFFER["Rollout: 경험을 일정량 수집"]
    ACTOR -->|행동·확률 정보| BUFFER
    CRITIC -->|가치 추정| BUFFER
    BUFFER --> PPO["PPO: 경험으로 정책과 가치망 업데이트"]
    PPO -->|가중치 수정| ACTOR
    PPO -->|가중치 수정| CRITIC
    PPO --> SAVE["체크포인트 저장 → 나중에 정책 로드·제어"]
    classDef env fill:#eaf6ef,stroke:#24725d,color:#172b45;
    classDef model fill:#f2ecfb,stroke:#7043a1,color:#172b45;
    classDef learn fill:#fff4df,stroke:#ab6610,color:#172b45;
    class ENV env;
    class ACTOR,CRITIC model;
    class BUFFER,PPO learn;
```

경험을 일정량 모은 뒤 PPO가 가중치를 업데이트하고, 바뀐 정책으로 다시 경험을 수집한다.
보상 하나를 받는 것과 모델 업데이트 한 번은 같은 단위가 아니다.

## 2. Actor·Critic 모델 구조

```mermaid
flowchart LR
    subgraph ACTOR["Actor: 행동 선택 · 24장 Cartpole 예시"]
        AIN["관측 4개"] --> A1["은닉층 1: 32 뉴런·ELU"] --> A2["은닉층 2: 32 뉴런·ELU"] --> AOUT["행동 분포 → 카트 행동 1개 선택"]
    end
    subgraph CRITIC["Critic: 가치 추정 · 같은 관측 사용 예시"]
        CIN["관측 4개"] --> C1["은닉층 1: 32 뉴런·ELU"] --> C2["은닉층 2: 32 뉴런·ELU"] --> COUT["앞으로의 보상 추정 V: 숫자 1개"]
    end
    PPO["PPO 학습"] -.->|가중치 수정| A1
    PPO -.->|가중치 수정| C1
```

24장의 실제 은닉층 설정 `[32, 32]`를 예시로 사용했다. 행동 분포에는 신경망 평균 출력과 탐색용 표준편차 등이 사용된다.
위 다이어그램은 역할을 묶어 보여주는 구성도다. Critic은 보상 함수를 대신 만들지 않으며, 학습에서는 두 모델의 관련 가중치를 갱신한다.
20장에는 이 신경망이 없고, 21장의 관측 7개와 24장 예시의 관측 4개도 구분한다.

## 3. 20번 파일 실행 구조

```mermaid
flowchart TD
    CFG["CartpoleEnvCfg: Scene·Actions·Observations·Rewards·Terminations·Events"] --> CREATE["main: ManagerBasedRLEnv 생성"]
    CREATE --> RESET["env.reset: 첫 관측 받기"]
    RESET --> RANDOM["torch.randn: 관측과 무관한 랜덤 행동"]
    RANDOM --> STEP["env.step: 행동 처리·물리 진행·종료·보상·리셋"]
    STEP --> RESULT["반환: obs, rew, terminated, truncated, info"]
    RESULT --> LOG["보상 누적·에피소드 수·현재 step 평균 보상 기록"]
    LOG --> LIMIT{"2000 환경 step인가?"}
    LIMIT -->|아니오| RANDOM
    LIMIT -->|예| CLOSE["env.close: 데모 종료"]
    NOTE["20장에는 Actor·Critic 생성과 PPO 가중치 업데이트가 없음"] -.-> RANDOM
```

환경이 반환한 관측을 다음 행동 생성에 사용하지 않는다. 결과는 로그로 기록하며 행동은 계속 무작위다.

## 4. 환경 step과 물리 step

```mermaid
flowchart TD
    INPUT["env.step(action): 행동 1회 입력"] --> PROCESS["Action Manager: 카트 effort 목표로 변환·scale 100"]
    PROCESS --> PHYS1["물리 step 1: 행동 적용 → PhysX 진행 → 씬 상태 갱신"]
    PHYS1 --> PHYS2["물리 step 2: 같은 행동 → PhysX 진행 → 씬 상태 갱신"]
    PHYS2 --> COUNTER["환경·에피소드 카운터 증가"]
    COUNTER --> TERM["종료 계산: 카트 경계 이탈 / 에피소드 5초 상한"]
    TERM --> REWARD["보상 계산: 각 항의 값 × 가중치 × 환경 dt의 합"]
    REWARD --> DONE{"완료한 환경이 있는가?"}
    DONE -->|예| RESET["해당 환경만 초기 상태로 리셋·Event 실행"]
    DONE -->|아니오| OBS["관측 계산"]
    RESET --> OBS
    OBS --> RETURN["관측·보상·종료 플래그·info 반환"]
    RETURN --> NEXT["다음 행동: 20장은 다시 랜덤 샘플"]
    TIME["물리 dt=1/120초 · decimation=2 · 환경 dt=1/60초"] -.-> PHYS1
    TIME -.-> PHYS2
```

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
