"""첨부 TensorBoard 이벤트로 CSV·통계·학습 곡선을 생성한다.
필요: tensorboard, matplotlib. 실행: python analysis/render_training_curves.py
"""
from pathlib import Path
import csv
import hashlib
import json
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    event_files = list((root / 'logs/rsl_rl/anymal_locomotion_tutorial').glob('events.out*'))
    if len(event_files) != 1:
        raise SystemExit('첨부된 단일 run을 분석합니다. 다른 run은 분리해서 분석하세요.')
    event = EventAccumulator(str(event_files[0]), size_guidance={'scalars': 0})
    event.Reload()
    data = {tag: event.Scalars(tag) for tag in event.Tags()['scalars'] if not tag.endswith('/time')}
    iterations = sorted({item.step for values in data.values() for item in values})
    lookup = {tag: {item.step: item.value for item in values} for tag, values in data.items()}
    with (root / 'analysis/training-metrics.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['iteration'] + list(data))
        for step in iterations:
            writer.writerow([step] + [lookup[tag].get(step, '') for tag in data])
    wall_times = [item.wall_time for values in data.values() for item in values]
    summary = {
        'source': str(event_files[0].relative_to(root)),
        'scope': 'Training run scalar logs, not independent policy evaluation',
        'iterations': len(iterations), 'first_iteration': iterations[0], 'last_iteration': iterations[-1],
        'total_transitions': 2048 * 24 * len(iterations),
        'transition_count_basis': '2048 environments and 24 rollout steps from code and video; event scalars do not directly store this count',
        'event_wall_time_span_seconds': max(wall_times) - min(wall_times),
        'metrics': {tag: {'first': values[0].value, 'iteration_2': lookup[tag].get(2),
                           'last': values[-1].value,
                           'last_20_iteration_mean': sum(item.value for item in values[-20:]) / len(values[-20:])}
                    for tag, values in data.items()},
    }
    (root / 'analysis/training-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    manifest = {str(file.relative_to(root)): {'bytes': file.stat().st_size,
                'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}
                for file in sorted((root / 'logs').rglob('*')) if file.is_file()}
    (root / 'analysis/log-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 14, 'axes.labelsize': 11,
                         'axes.spines.top': False, 'axes.spines.right': False})
    figures = {
        'learning-progress': [
            ('Train/mean_reward', 'Mean episode reward', 'Reward'),
            ('Train/mean_episode_length', 'Mean episode length', 'Environment steps'),
            ('Episode_Termination/time_out', 'Time-limit termination metric', 'Manager aggregate'),
            ('Episode_Termination/base_contact', 'Base-contact termination metric', 'Manager aggregate')],
        'velocity-tracking': [
            ('Episode_Reward/track_lin_vel_xy_exp', 'Planar velocity tracking reward', 'Weighted episodic log'),
            ('Episode_Reward/track_ang_vel_z_exp', 'Yaw-rate tracking reward', 'Weighted episodic log'),
            ('Metrics/base_velocity/error_vel_xy', 'Accumulated planar error metric', 'Normalized accumulation'),
            ('Metrics/base_velocity/error_vel_yaw', 'Accumulated yaw-rate error metric', 'Normalized accumulation')],
        'gait-costs': [
            ('Episode_Reward/feet_air_time', 'Feet air-time reward term', 'Weighted episodic log'),
            ('Episode_Reward/action_rate_l2', 'Action-change penalty term', 'Weighted episodic log'),
            ('Episode_Reward/dof_torques_l2', 'Joint-torque penalty term', 'Weighted episodic log'),
            ('Episode_Reward/flat_orientation_l2', 'Body-tilt penalty term', 'Weighted episodic log')],
        'optimization': [
            ('Loss/value_function', 'Critic value loss', 'Loss (log scale)'),
            ('Loss/learning_rate', 'Adaptive learning rate', 'Learning rate'),
            ('Policy/mean_noise_std', 'Policy exploration standard deviation', 'Mean action std'),
            ('Loss/entropy', 'Policy entropy', 'Differential entropy')],
    }
    for name, panels in figures.items():
        fig, axes = plt.subplots(2, 2, figsize=(11.5, 6.8), constrained_layout=True)
        for ax, (tag, title, ylabel) in zip(axes.flat, panels):
            values = data[tag]
            ax.plot([item.step for item in values], [item.value for item in values],
                    color='#252525', linewidth=1.5)
            ax.set(title=title, xlabel='Training iteration (0-299)', ylabel=ylabel)
            ax.grid(alpha=.18)
            if tag == 'Train/mean_episode_length':
                ax.axhline(1000, color='#888888', linestyle='--', linewidth=1, label='20 s limit: 1000 steps')
                ax.legend(fontsize=9, loc='lower right')
            if tag.startswith('Episode_Termination/'):
                ax.set_ylim(-.02, 1.02)
            if tag == 'Loss/value_function':
                ax.set_yscale('log')
            if tag == 'Loss/learning_rate':
                ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        fig.savefig(root / f'images/{name}.png', dpi=140, facecolor='white')
        plt.close(fig)
    print(f'{len(iterations)} iteration · {len(data)} scalar tags · 그래프 4개·CSV·통계·manifest 생성 완료')


if __name__ == '__main__':
    main()
