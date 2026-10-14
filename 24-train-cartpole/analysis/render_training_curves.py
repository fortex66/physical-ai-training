"""제공 TensorBoard 이벤트의 iteration scalar를 CSV·곡선으로 변환한다.
필요: tensorboard, matplotlib. 실행: python analysis/render_training_curves.py
"""
from pathlib import Path
import csv
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    events = sorted((root / 'logs/rsl_rl/cartpole_tutorial').glob('events.out*'))
    if len(events) != 1:
        raise SystemExit('제공 이벤트 1개를 기준으로 합니다. 여러 run의 이벤트는 분리해 분석하세요.')
    accumulator = EventAccumulator(str(events[0]), size_guidance={'scalars': 0})
    accumulator.Reload()
    data = {tag: accumulator.Scalars(tag) for tag in accumulator.Tags()['scalars']
            if not tag.endswith('/time')}
    tags = list(data)
    lookup = {tag: {item.step: item.value for item in rows} for tag, rows in data.items()}
    iterations = sorted({item.step for rows in data.values() for item in rows})
    with (root / 'analysis/training-metrics.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['iteration'] + tags)
        for iteration in iterations:
            writer.writerow([iteration] + [lookup[tag].get(iteration, '') for tag in tags])
    plt.rcParams.update({'font.size': 13, 'axes.titlesize': 15, 'axes.labelsize': 12,
                         'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    panels = [
        ('Train/mean_reward', 'Mean episode reward', 'Episode reward'),
        ('Train/mean_episode_length', 'Mean episode length', 'Environment steps'),
        ('Policy/mean_noise_std', 'Policy exploration standard deviation', 'Action std'),
        ('Loss/value_function', 'Critic value loss', 'Loss (log scale)'),
    ]
    for ax, (tag, title, ylabel) in zip(axes.flat, panels):
        values = data[tag]
        ax.plot([item.step for item in values], [item.value for item in values],
                color='#2858A5', linewidth=1.8)
        ax.set(title=title, xlabel='Training iteration (0-149)', ylabel=ylabel)
        ax.grid(alpha=.18)
        if tag == 'Train/mean_reward':
            ax.axhline(17.5, color='#8B95A3', linewidth=1, linestyle='--', label='Ideal reference: 17.5')
            ax.legend(fontsize=10, loc='lower right')
        elif tag == 'Train/mean_episode_length':
            ax.axhline(300, color='#8B95A3', linewidth=1, linestyle='--')
        elif tag == 'Loss/value_function':
            ax.set_yscale('log')
    fig.savefig(root / 'images/training-curves.png', dpi=140, facecolor='white')
    plt.close(fig)
    print('제공 이벤트에서 CSV·학습 곡선 생성 완료')


if __name__ == '__main__':
    main()
