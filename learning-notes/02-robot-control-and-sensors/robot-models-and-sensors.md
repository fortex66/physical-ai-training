# 로봇 구조·센서·토크·모델 형식

[개념 학습 전체](../README.md)

<a id="articulation"></a>
## 3. Articulation — 관절로 연결된 강체

Articulation은 링크들이 관절로 연결된 로봇·기구를 다루는 구조다.
단일 강체의 위치·속도에 더해 관절 위치·속도·토크와 각 링크의 포즈를 관리한다.

회전 관절 위치는 rad, 직선 관절 위치는 m로 표현한다.
팔 관절과 그리퍼 관절이 같은 배열에 있어도 단위와 역할이 같다고 가정하면 안 된다.
관절 위치 목표와 토크 목표는 다른 명령이며, 실제 응답은 actuator 설정과 물리 조건에 따라 달라진다.

[05 로봇 배치·관절 상태](../../practice/02-robot-control-and-sensors/05-spawn-robot/README.md) · [06 관절 제어](../../practice/02-robot-control-and-sensors/06-robot-joint-control/README.md)

<a id="sensors"></a>
## 5. RGB·Depth와 RayCaster

| 센서 | 읽는 데이터 | 해석할 때 확인할 것 |
|---|---|---|
| RGB 카메라 | 픽셀 색상 | 이미지 채널·해상도 |
| Depth 카메라 | 픽셀별 깊이 · m | 광학 축 기준 깊이인지 카메라 중심에서의 거리인지 |
| RayCaster | 지정 광선과 대상 메시의 교차점 | 출력 좌표계·대상 메시·미교차 값 |

Depth는 사용하는 `data_types`에 따라 의미가 달라질 수 있다.
`distance_to_image_plane`과 `distance_to_camera`를 동일한 값으로 가정하지 않는다.
화면의 색상 지도는 깊이 숫자를 색으로 표현한 것이다.

RayCaster의 `ray_hits_w`는 월드 교차점 `(x, y, z)`다.
z 좌표는 표면의 월드 높이이며 센서에서 표면까지의 거리와 구분한다.
여러 광선의 높이를 평균 내면 단의 경계에서 중간값이 생길 수 있다.

물리·렌더링 진행 후 센서 데이터를 갱신해 읽는다.
`InteractiveScene`에 등록한 센서는 씬 갱신을 통해 관리하고, 직접 만든 센서는 해당 객체의 갱신을 수행한다.

[09 RGB·Depth](../../practice/02-robot-control-and-sensors/09-camera-sensor/README.md) · [10 격자 광선·높이 스캔](../../practice/02-robot-control-and-sensors/10-ray-caster/README.md)

<a id="torque-contact"></a>
## 6. 토크·레버·접촉 힘

토크의 크기는 힘과 회전축에서 힘의 작용선까지의 수직 거리의 곱이다.
이번 수평 레버 예제에서는 같은 토크일 때 짧은 레버가 더 큰 접촉 힘을 전달한다.

균일한 빔의 자체 무게와 끝점의 반력을 고려한 정적 평형식은 다음과 같다.

$$
F=\frac{\tau}{L}+\frac{mg}{2}
$$

중력 항이 더해지므로 총 접촉 힘의 비율을 레버 길이의 역비율과 같다고 볼 수는 없다.
이 식은 수평 빔·끝점 접촉·정적 평형을 가정한다.

`ContactSensor.data.net_forces_w`는 대상 강체에 작용하는 월드 기준 순접촉 힘 벡터다.
모터 토크와 다른 데이터이며, 특정 접촉 상대만 읽으려면 센서의 대상·필터 구성을 고려해야 한다.

[11 토크·접촉 힘 비교](../../practice/02-robot-control-and-sensors/11-torque-lever-contact/README.md)

<a id="urdf"></a>
## 7. URDF와 USD

URDF는 로봇 구조를 표현하는 XML이다.
`link`는 강체 부품, `joint`는 부품 사이의 연결이며,
시각 형상·충돌 형상·질량·무게중심·관성·관절 축과 범위를 기술한다.

Isaac Sim에서는 URDF를 USD로 변환해 장면·물리 자산으로 사용한다.
USD는 로봇뿐 아니라 장면 구성과 여러 자산을 표현하며 여러 레이어·참조 파일로 나눌 수 있다.
URDF 모델과 제어 프로그램은 역할이 다르다. 입력 명령·센서·실험 루프는 별도로 구성한다.

[11 URDF 설명·레버 모델 파일](../../practice/02-robot-control-and-sensors/11-torque-lever-contact/README.md)
