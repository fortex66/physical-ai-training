"""제공 영상의 반올림된 최종 집계만 그린다. 학습 곡선이나 원시 episode 로그가 아니다."""
from pathlib import Path
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/motion36-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root=Path(__file__).resolve().parents[1]
    s=json.loads((root/'analysis/results-summary.json').read_text())
    keys=['random_walking','trained_walking','post_kungfu_run']
    labels=['Random\n(n=10)','Walking model\n(n=12)','Post-kungfu run*\n(n=10)']
    fig,axes=plt.subplots(1,2,figsize=(10,3.7),constrained_layout=True)
    plt.rcParams.update({'font.size':10})
    for ax,field,title,ylabel in [(axes[0],'mean_length_steps','Recorded episode duration','Environment steps (0.02 s)'),
                                  (axes[1],'joint_rms_rad','Reported mean joint RMS','Radians')]:
        values=[s['evaluations'][k][field] for k in keys]
        bars=ax.bar(labels,values,color=['#cccccc','#777777','#eeeeee'],edgecolor='#222222')
        for bar,value in zip(bars,values):
            ax.text(bar.get_x()+bar.get_width()/2,value+max(values)*.03,f'{value:g}',ha='center')
        ax.set(title=title,ylabel=ylabel,ylim=(0,max(values)*1.22))
        ax.spines[['top','right']].set_visible(False)
    fig.savefig(root/'images/evaluation-comparison.png',dpi=170,facecolor='white');plt.close(fig)


if __name__=='__main__': main()
