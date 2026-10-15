# 다중 환경 복제·좌표·선택 제어

[개념 학습 전체](../README.md)

<a id="parallel-envs"></a>
## 4. 다중 환경과 선택 제어

`InteractiveSceneCfg`에 환경의 구성 요소를 선언하고 `num_envs`로 복제 개수를 지정한다.
`{ENV_REGEX_NS}`를 사용하는 자산은 환경별 경로 아래에 배치한다.
`env_spacing`은 환경 원점 사이의 배치 간격이며 로봇 외형 사이의 빈 공간을 의미하지 않는다.

환경 기준 위치에 `scene.env_origins`를 더하면 이 예제들의 월드 위치가 된다.
환경마다 원점이 다르므로 같은 로컬 위치라도 월드 위치는 다를 수 있다.

`env_ids`는 제어할 환경을, `joint_ids`는 제어할 관절을 고른다.
선택한 환경에만 명령을 보낼 때는 명령 텐서의 첫 차원이 선택한 환경 수와 맞아야 한다.
다중 환경 복제 자체가 학습은 아니지만, 병렬 실험·강화학습·일부 환경만 리셋하는 구성의 기반이 된다.

[07 환경 자동 복제](../../practice/02-robot-control-and-sensors/07-scene-design/README.md) · [08 특정 환경 선택 제어](../../practice/02-robot-control-and-sensors/08-multi-robot/README.md)
