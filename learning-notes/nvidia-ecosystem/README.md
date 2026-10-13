# 공식 이미지로 보는 NVIDIA 생태계 · ACT

학습일: 2026-10-13

NVIDIA 공식 이미지와 기술 설명을 바탕으로 정리한 **5쪽 PDF 학습 자료**입니다.
전체 구성도와 한국어 설명은 학습용으로 재구성했고, 공식 이미지의 출처와 버전을 PDF에 표시했습니다.

## 자료 보기

- [PDF 보기 / 다운로드](physical-ai-ecosystem.pdf)
- [이미지 출처와 ACT 참고 문서 목록](sources.json)

## PDF 구성

| 페이지 | 내용 |
|---|---|
| 1 | NVIDIA 생태계 전체 구성도 |
| 2 | Omniverse·Isaac Sim·Isaac Lab·Mimic |
| 3 | Cosmos와 GR00T N1 계열의 역할 및 공식 구조도 |
| 4 | GR00T Dreams 공식 참조 아키텍처 해설 |
| 5 | ACT 모방학습과 실제 로봇 활용 근거 |

## ACT는 실제 현장에서 많이 쓰이나?

**실제 로봇의 모방학습 연구·실증에서 활용되는 알고리즘이라고 설명할 근거는 있습니다.**
원본 ACT 공개 구현은 실물 로봇의 학습과 평가를 지원하며,
LeRobot 공식 문서는 빠른 학습, 낮은 계산 요구량과 성능을 이유로 ACT를 입문 시 첫 모델로 추천합니다.

다만 실제 로봇으로 실험하는 것과 제조 공장의 양산 라인에서 광범위하게 운용하는 것은 다릅니다.
이번에 확인한 자료는 ACT의 실물 로봇 활용과 실용적인 학습 도구로서의 위치를 뒷받침하지만,
제조업 전체의 도입 규모나 주류 여부를 입증하지는 않습니다.

학습 기록에는 다음처럼 표현합니다.

> ACT는 실제 로봇 조작의 모방학습 연구·실증과 공개 개발 생태계에서 활용되는 알고리즘이며,
> 특정 작업의 시연 기반 정책을 학습할 때 실용적인 출발점이다.
> 제조 공장의 광범위한 양산 적용 여부는 별도 도입 사례와 운영 자료로 확인해야 한다.

근거:

- [ACT 원본 공개 구현](https://github.com/tonyzhaozh/act)
- [LeRobot ACT 공식 문서](https://github.com/huggingface/lerobot/blob/main/docs/source/act.mdx)
- [LeRobot 프로젝트와 실제 로봇 학습·실행 워크플로우](https://github.com/huggingface/lerobot)

## 주요 NVIDIA 출처

- [Omniverse Kit App Template](https://github.com/NVIDIA-Omniverse/kit-app-template)
- [Isaac Sim](https://github.com/isaac-sim/IsaacSim)
- [Isaac Lab](https://github.com/isaac-sim/IsaacLab)
- [Isaac Lab Mimic 공식 워크플로우](https://github.com/isaac-sim/IsaacLab/blob/main/docs/source/overview/imitation-learning/teleop_imitation.rst)
- [Cosmos-Transfer1](https://github.com/nvidia-cosmos/cosmos-transfer1)
- [GR00T N1.5 브랜치](https://github.com/NVIDIA/Isaac-GR00T/tree/n1d5)
- [GR00T Dreams 공식 참조 아키텍처](https://github.com/NVIDIA/GR00T-Dreams/blob/main/reference_architecture/reference_architecture.md)
