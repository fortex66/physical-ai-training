"""영상에서 전사한 표시값 CSV로 평가 그림 생성. 필요: matplotlib."""
from pathlib import Path
import csv
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    rows = list(csv.DictReader((root / 'analysis/episode-results.csv').open()))
    episodes = [int(row['episode']) for row in rows]
    rewards = [float(row['displayed_reward']) for row in rows]
    lengths = [int(row['length_steps']) for row in rows]
    threshold = int(max(lengths) * 0.9)
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 14,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    axes[0].plot(episodes, rewards, 'o-', color='#222222', linewidth=1, markersize=4)
    axes[0].axhline(statistics.mean(rewards), color='#777777', linestyle='--',
                    label=f'Mean of displayed values: {statistics.mean(rewards):.2f}')
    axes[0].set(title='Episode reward (rounded video values)', ylabel='Reward')
    axes[0].legend(fontsize=9)
    axes[1].plot(episodes, lengths, 'o-', color='#222222', linewidth=1, markersize=4)
    axes[1].axhline(threshold, color='#777777', linestyle='--',
                    label=f'Code threshold: {threshold} steps')
    axes[1].set(title='Completed episode length', ylabel='Environment steps', ylim=(0, 1100))
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.set(xlabel='Completed episode number', xticks=[1, 5, 10, 15, 20])
        ax.grid(alpha=.18)
    fig.savefig(root / 'images/episode-results.png', dpi=140, facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    main()
