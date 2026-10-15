# 시뮬레이션 시간·루프·리셋

[개념 학습 전체](../README.md)

<a id="loop-reset"></a>
## 2. 시뮬레이션 루프와 리셋

Isaac Lab의 기본 흐름은 **명령 전달 → 물리 진행 → 상태 갱신**이다.

```python
scene.write_data_to_sim()
sim.step()
scene.update(sim_dt)
```

고정 시간 간격 `dt`에서 500번의 물리 스텝은 시뮬레이션 시간 `500 × dt`에 해당한다.
이는 PC에서 실제로 기다린 시간과 다를 수 있다.

에피소드 리셋에는 위치·방향과 속도를 함께 복원한다.
로봇은 관절 위치·관절 속도와 필요에 따라 루트 상태·제어 목표도 초기화한다.
`scene.reset()` 같은 버퍼 초기화만으로 임의의 초기 자세로 순간 이동하는 것은 아니다.
상태를 물리 엔진에 쓰는 API와 내부 버퍼를 초기화하는 API를 구분한다.

[04 강체 리셋](../../practice/01-simulation-basics/04-simulation-loop/README.md) · [07 씬 루프와 로봇 리셋](../../practice/02-robot-control-and-sensors/07-scene-design/README.md)
