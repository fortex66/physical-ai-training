"""제공 영상의 최종 표시값만 시각화한다. 원시 episode 데이터는 없다."""
from pathlib import Path
import json
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/lesson28-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
s = json.loads((root / 'analysis/evaluation-summary.json').read_text())
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), constrained_layout=True)
counts = [s['timeout_count'], s['fail_count']]
bars = axes[0].bar(['Timeout', 'Fail'], counts, color=['#eeeeee', '#777777'], edgecolor='#222222')
axes[0].set(title='First 200 completed episodes', ylabel='Episode count', ylim=(0, 220))
for b, n in zip(bars, counts):
    axes[0].text(b.get_x()+b.get_width()/2, n+5, f'{n} ({n/s["completed_episodes"]:.1%})', ha='center')
axes[1].barh(['Recorded mean'], [s['mean_episode_length_steps']], color='#999999', edgecolor='#222222', height=.4)
axes[1].axvline(1000, color='black', linestyle='--', label='Configured horizon (1000)')
axes[1].text(s['mean_episode_length_steps']+20, 0, '392.8 steps', va='center')
axes[1].set(xlim=(0, 1120), xlabel='Environment steps (0.02 s each)', title='Episode duration')
axes[1].set_ylim(-0.5, 0.7)
axes[1].legend(loc='upper left', frameon=False, fontsize=9)
fig.savefig(root / 'images/evaluation-results.png', dpi=170)
plt.close(fig)
