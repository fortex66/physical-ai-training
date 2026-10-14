"""강화학습 설명용 구성도 4장 생성. 실행: python render_diagrams.py (Pillow 필요)."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
BOLD = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')
if not FONT.exists():
    raise SystemExit('Noto Sans CJK 폰트가 필요합니다. fonts-noto-cjk를 설치하세요.')
INK = '#172b45'
BLUE = '#2162ad'
GREEN = '#24725d'
AMBER = '#ab6610'
PURPLE = '#7043a1'

class Diagram:
    def __init__(self, title, sub, h=1060):
        self.im = Image.new('RGB', (1440, h), '#f4f7fb')
        self.d = ImageDraw.Draw(self.im)
        self.text(50, 35, title, 39, bold=True)
        self.text(50, 96, sub, 23, color='#52647c')
    def text(self,x,y,s,size=24,color=INK,bold=False):
        self.d.text((x,y),s,font=ImageFont.truetype(str(BOLD if bold else FONT),size),fill=color)
    def box(self,x,y,w,h,title,lines=(),kind='blue'):
        colors={'blue':(BLUE,'#eaf2ff'),'green':(GREEN,'#e9f6f0'),'amber':(AMBER,'#fff4df'),'purple':(PURPLE,'#f2ecfb'),'gray':('#52647c','#ffffff')}
        stroke,fill=colors[kind]
        self.d.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=fill,outline=stroke,width=2)
        self.d.rounded_rectangle((x,y,x+6,y+h),radius=3,fill=stroke)
        self.text(x+22,y+18,title,27,color=stroke,bold=True)
        for n,line in enumerate(lines): self.text(x+22,y+63+n*28,line,22)
    def arrow(self,pts,label=None,labelpos=None,color=BLUE):
        self.d.line(pts,fill=color,width=4,joint='curve')
        a,b=pts[-2],pts[-1]; ang=math.atan2(b[1]-a[1],b[0]-a[0]); sz=13
        poly=[b,(b[0]-sz*math.cos(ang-.5),b[1]-sz*math.sin(ang-.5)),(b[0]-sz*math.cos(ang+.5),b[1]-sz*math.sin(ang+.5))]
        self.d.polygon(poly,fill=color)
        if label:
            x,y=labelpos; f=ImageFont.truetype(str(FONT),20); bb=self.d.textbbox((x,y),label,font=f)
            self.d.rectangle((bb[0]-5,bb[1]-3,bb[2]+5,bb[3]+3),fill='#f4f7fb')
            self.d.text((x,y),label,font=f,fill=color)
    def save(self,name): self.im.save(OUT/name)

# 1. 학습 구성: 환경과 학습기가 경험을 주고받고, 수집 뒤 가중치를 갱신.
p=Diagram('1. 실제 강화학습: 경험을 모아 정책을 개선한다', '20장은 환경을 준비하는 단계 · 아래의 신경망과 PPO 학습기는 24장 등에서 연결')
p.box(50,155,1340,125,'사용자가 정하는 것',['환경·관측·행동·보상·종료 조건  +  신경망 구조·학습 설정'],kind='gray')
p.box(50,340,300,140,'관측',['위치·각도·속도 등','행동 결정에 줄 정보'])
p.box(450,340,300,140,'Actor / Policy',['관측 → 행동 선택','학습 중에는 탐색'],kind='purple')
p.box(850,340,540,140,'Isaac Lab + Isaac Sim',['행동 적용 → 물리 진행','다음 관측·보상·종료 정보 반환'],kind='green')
p.arrow([(350,405),(450,405)],'입력',(373,370))
p.arrow([(750,405),(850,405)],'행동',(773,370))
p.arrow([(1390,400),(1415,400),(1415,308),(200,308),(200,340)],'다음 관측으로 계속 행동',(925,284),color=GREEN)
p.box(50,595,300,145,'Critic / 가치망',['앞으로 얻을 보상 추정','정책 학습의 비교 기준'],kind='purple')
p.box(450,595,460,145,'경험 수집 · Rollout',['관측·행동·보상·종료 정보','가치 추정·행동 확률 등'],kind='blue')
p.box(1020,595,370,145,'PPO 학습기',['예상보다 좋은 행동 평가','Actor·Critic 가중치 수정'],kind='amber')
p.arrow([(200,480),(200,595)],'관측',(215,520))
p.arrow([(600,480),(600,595)],'행동 정보',(615,530))
p.arrow([(1120,480),(1120,525),(850,525),(850,595)],'환경에서 얻은 경험',(873,535),color=GREEN)
p.arrow([(350,665),(450,665)],'추정값',(369,630),color=PURPLE)
p.arrow([(910,665),(1020,665)],'수집 후',(931,630))
p.box(50,855,690,115,'업데이트한 정책으로 다시 경험 수집',['행동 → 경험 → 업데이트를 여러 번 반복'],kind='purple')
p.box(850,855,540,115,'체크포인트 저장',['학습한 가중치를 나중에 로드해 제어'],kind='gray')
p.arrow([(1130,740),(1130,790),(395,790),(395,855)],color=AMBER)
p.arrow([(1290,740),(1290,855)],'저장',(1305,783),color=AMBER)
p.text(50,1007,'보상을 계산하는 환경과, 보상을 이용해 가중치를 바꾸는 학습기는 서로 다른 역할입니다.',22)
p.save('01-training-overview.png')

# 2. 24장 실제 설정으로 만든 모델 구조 예시. 20장에 없는 신경망임을 강조.
p=Diagram('2. Actor와 Critic: 입력은 비슷해도 출력의 역할이 다르다','모델 예시: 24장 Cartpole 설정 · Actor [32, 32], Critic [32, 32] · 20장에는 이 모델이 없음',h=950)
p.box(50,175,1340,110,'구조와 가중치는 다르다',['사용자: 은닉층·뉴런 수 선택     /     학습 라이브러리: 초기화     /     PPO: 가중치 업데이트'],kind='gray')
for y,name,output,detail in [(350,'Actor · 행동 선택','행동 분포','카트 힘 1개 선택'),(585,'Critic · 가치 추정','가치 V · 숫자 1개','앞으로의 보상 추정')]:
    p.text(50,y-44,name,27,color=PURPLE,bold=True)
    p.box(50,y,270,135,'관측 4개',['카트·막대 위치와 속도'])
    p.box(405,y,265,135,'은닉층 1',['뉴런 32개 · ELU'],kind='purple')
    p.box(755,y,265,135,'은닉층 2',['뉴런 32개 · ELU'],kind='purple')
    p.box(1105,y,285,135,output,[detail],kind='green')
    for a,b in [(320,405),(670,755),(1020,1105)]: p.arrow([(a,y+67),(b,y+67)])
p.box(50,800,1340,100,'학습과 실행',['Critic은 학습을 돕고, 로봇의 행동은 Actor가 선택합니다. Critic에 별도 관측을 줄 수도 있습니다.'],kind='amber')
p.save('02-actor-critic-model.png')

# 3. 제공 코드가 실제로 실행하는 경로.
p=Diagram('3. 20_base_env.py: 지금 실행되는 것은 환경 테스트','랜덤 행동 → env.step() → 관측·보상·종료 로그 · 신경망 생성과 PPO 업데이트는 없음',h=1190)
p.box(50,155,1340,125,'CartpoleEnvCfg · 환경 정의',['Scene  /  Actions  /  Observations  /  Rewards  /  Terminations  /  Events'],kind='gray')
p.box(50,335,610,140,'main() · 테스트 실행',['ManagerBasedRLEnv 생성','env.reset() → 첫 관측 받기'])
p.box(780,335,610,140,'ManagerBasedRLEnv · 환경 관리자',['설정대로 장면·행동·관측·보상 구성','종료한 환경은 자동으로 리셋'],kind='green')
p.arrow([(660,402),(780,402)],'설정 전달',(677,367))
p.arrow([(355,280),(355,335)])
p.arrow([(1085,280),(1085,335)])
p.box(50,565,610,145,'랜덤 행동 생성',['torch.randn(N, 1) · 관측과 무관','정규분포이며 ±1 범위로 제한되지 않음'],kind='amber')
p.box(780,565,610,145,'env.step(action)',['행동 처리 → 물리 2회 진행','종료·보상 계산 → 리셋 → 관측 반환'],kind='green')
p.arrow([(355,475),(355,565)])
p.arrow([(660,638),(780,638)],'행동',(697,600))
p.box(50,805,610,155,'로그와 실행 종료 관리',['보상 누적 · 종료 환경 episode 수 기록','현재 step의 환경 간 평균 보상 출력','2000 환경 step이면 데모 종료'])
p.box(780,805,610,155,'환경이 반환하는 것',['obs  /  rew  /  terminated','truncated  /  info'],kind='green')
p.arrow([(1085,710),(1085,805)])
p.arrow([(780,878),(660,878)],'결과',(694,840),color=GREEN)
p.arrow([(50,870),(25,870),(25,635),(50,635)],color=BLUE)
p.text(50,1005,'이 루프를 오래 돌려도 행동 분포나 가중치는 개선되지 않습니다.',27,color=AMBER,bold=True)
p.text(50,1054,'실제 학습으로 확장: 정책 모델 + 경험 수집 + PPO 업데이트 + 체크포인트 저장을 연결',24)
p.text(50,1110,'기본 N=4: 관측 (4,4), 행동 (4,1), 보상·종료 플래그 (4,) · 각 환경은 별도로 종료될 수 있음',22)
p.save('03-lesson20-structure.png')

# 4. v2.3.2 manager_based_rl_env.py의 주요 처리 순서.
p=Diagram('4. env.step(action) 한 번 안에서 일어나는 일','20장: physics dt=1/120초, decimation=2 → 환경 step 시간=1/60초',h=1350)
p.box(50,155,1340,105,'① 행동 처리 · Action Manager',['입력 (N,1) → 카트 effort 목표에 scale=100 적용'])
p.arrow([(355,260),(355,305)])
p.box(50,305,610,140,'② 물리 step 1 · 약 0.00833초',['현재 행동 적용 → 힘을 시뮬레이터에 전달','PhysX 계산 → 씬 상태 갱신'],kind='green')
p.box(780,305,610,140,'③ 물리 step 2 · 약 0.00833초',['같은 행동으로 물리 계산을 한 번 더 수행','조건에 따라 렌더링 → 씬 상태 갱신'],kind='green')
p.arrow([(660,375),(780,375)],'같은 행동',(678,340))
p.arrow([(1085,445),(1085,490),(720,490),(720,535)])
p.box(50,535,1340,135,'④ 환경·에피소드 카운터 증가 → 종료 판정 → 보상 계산',['terminated: 카트가 ±3 m 밖     /     truncated: 에피소드 5초 시간 상한','보상 = 각 항의 값 × 가중치 × 환경 step 시간(1/60초)의 합'],kind='amber')
p.arrow([(720,670),(720,715)])
p.box(50,715,1340,125,'⑤ 완료된 환경만 자동 리셋',['종료 환경의 초기 관절 위치·속도 재설정 · Event 실행 · 내부 버퍼 초기화','나머지 환경은 계속 진행'],kind='green')
p.arrow([(720,840),(720,885)])
p.box(50,885,1340,125,'⑥ 관측 계산 → 반환',['obs, rew, terminated, truncated, info','완료 환경: 보상·플래그는 이전 episode, 관측은 새 episode 초기 상태일 수 있음'])
p.arrow([(720,1010),(720,1060)])
p.box(50,1060,1340,110,'⑦ 다음 행동 결정',['20장: 다시 랜덤 샘플     /     실제 학습: 반환 상태를 정책 입력·경험 수집에 사용'],kind='purple')
p.text(50,1220,'시간 구분: 물리 120 Hz · 행동/환경 약 60 Hz · 최대 5초 ≈ 300 환경 step',25,bold=True)
p.text(50,1270,'렌더링은 화면 갱신이며, 신경망 가중치 업데이트나 학습 iteration과 다릅니다.',23)
p.save('04-environment-step.png')
print('Rendered 4 Korean diagrams')
