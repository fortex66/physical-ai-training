"""첨부된 두 TensorBoard run을 분리하고 완주 run의 곡선을 생성한다.
실행: python analysis/render_training_curves.py (tensorboard, matplotlib 필요)
"""
from pathlib import Path
import csv
import json
import hashlib
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/g1-standing-matplotlib')
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    logs = root / 'logs/rsl_rl/g1_standing_tutorial'
    runs = []
    data = None
    for file in sorted(logs.glob('events.out*')):
        event = EventAccumulator(str(file), size_guidance={'scalars': 0})
        event.Reload()
        scalars = {tag: event.Scalars(tag) for tag in event.Tags()['scalars'] if not tag.endswith('/time')}
        steps = [item.step for item in scalars['Train/mean_reward']]
        runs.append({'file': str(file.relative_to(root)), 'points': len(steps), 'first_iteration': steps[0],
                     'last_iteration': steps[-1], 'final_mean_reward': scalars['Train/mean_reward'][-1].value})
        # Explicitly select the supplied completed run, without merging overlapping iteration axes.
        if file.name.endswith('.12469.0'):
            assert steps == list(range(1000))
            data, selected = scalars, file
    if data is None:
        raise SystemExit('첨부 완주 run(.12469.0)을 찾을 수 없습니다. run을 합치지 마세요.')
    iterations = list(range(1000))
    lookup = {tag: {v.step: v.value for v in values} for tag, values in data.items()}
    with (root / 'analysis/training-metrics.csv').open('w', newline='') as file:
        w = csv.writer(file, lineterminator="\n"); w.writerow(['iteration'] + list(data))
        for i in iterations: w.writerow([i] + [lookup[t].get(i, '') for t in data])
    times = [v.wall_time for vals in data.values() for v in vals]
    summary = {'scope': 'Training scalars, not independent robustness evaluation', 'runs': runs,
               'selected_run': str(selected.relative_to(root)), 'iterations': 1000,
               'num_envs': 512, 'steps_per_env': 24, 'transitions_per_iteration': 12288,
               'mini_batches': 8, 'samples_per_minibatch': 1536, 'epochs': 5,
               'optimizer_steps_per_iteration': 40, 'total_transitions': 12288000,
               'count_basis': 'Supplied code defaults and final screenshot total; scalar file does not store environment count',
               'event_wall_time_span_seconds': max(times)-min(times),
               'metrics': {t: {'first': vals[0].value, 'last': vals[-1].value,
                               'last_20_iteration_mean': sum(v.value for v in vals[-20:])/len(vals[-20:])}
                           for t, vals in data.items()}}
    (root / 'analysis/training-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    manifest = {str(p.relative_to(root)): {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted((root/'logs').rglob('*')) if p.is_file()}
    (root / 'analysis/log-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 12, 'axes.spines.top': False, 'axes.spines.right': False})
    plots = {
        'learning-progress': [('Train/mean_reward', 'Mean episode reward', 'Reward'),
                             ('Train/mean_episode_length', 'Mean episode length', 'Environment steps'),
                             ('Episode_Termination/time_out', 'Timeout aggregate', 'Manager metric'),
                             ('Episode_Termination/bad_orientation', 'Tilt termination aggregate', 'Manager metric')],
        'standing-rewards': [('Episode_Reward/height_reward', 'Height reward', 'Weighted episodic log'),
                             ('Episode_Reward/alive_bonus', 'Alive bonus', 'Weighted episodic log'),
                             ('Episode_Reward/flat_orientation', 'Body tilt penalty', 'Weighted episodic log'),
                             ('Episode_Reward/action_rate', 'Action-change penalty', 'Weighted episodic log'),
                             ('Episode_Reward/joint_vel', 'Joint-velocity penalty', 'Weighted episodic log'),
                             ('Episode_Reward/joint_limits', 'Soft-limit penalty', 'Weighted episodic log')],
        'optimization': [('Loss/value_function', 'Critic value loss', 'Loss (log scale)'),
                         ('Loss/surrogate', 'PPO surrogate loss', 'Loss'),
                         ('Loss/entropy', 'Continuous policy entropy', 'Differential entropy'),
                         ('Policy/mean_noise_std', 'Exploration standard deviation', 'Mean action std')],
        'performance': [('Perf/total_fps', 'Parallel transitions per second', 'Transitions/s'),
                        ('Perf/collection time', 'Rollout collection time', 'Seconds/iteration'),
                        ('Perf/learning_time', 'PPO update time', 'Seconds/iteration'),
                        ('Loss/learning_rate', 'Adaptive learning rate', 'Learning rate')],
    }
    for name, panels in plots.items():
        rows = len(panels)//2
        fig, axes = plt.subplots(rows, 2, figsize=(11, 3*rows), constrained_layout=True)
        for ax,(tag,title,ylabel) in zip(axes.flat, panels):
            vals = data[tag]
            ax.plot([v.step for v in vals], [v.value for v in vals], color='#252525', lw=1.1)
            ax.set(title=title, xlabel='Training iteration (0-999)', ylabel=ylabel)
            ax.grid(alpha=.18)
            if tag=='Train/mean_episode_length':
                ax.axhline(250,color='#888888',ls='--',lw=1,label='5 s horizon');ax.legend(fontsize=9)
            if tag.startswith('Episode_Termination/'): ax.set_ylim(-.02,1.02)
            if tag=='Loss/value_function':ax.set_yscale('log')
            if tag=='Loss/learning_rate':ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        fig.savefig(root / f'images/{name}.png', dpi=150, facecolor='white');plt.close(fig)
    print('완주 run 1000 iteration · scalar 19항목 · 그래프 4개 · 짧은 run 분리 기록')


if __name__ == '__main__': main()
