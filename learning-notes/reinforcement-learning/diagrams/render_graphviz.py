"""Graphviz DOT 소스에서 문서용 PNG와 확대용 SVG를 생성한다."""
from pathlib import Path
import shutil
import subprocess


def main():
    if not shutil.which('dot'):
        raise SystemExit('Graphviz의 dot 명령이 필요합니다.')
    root = Path(__file__).resolve().parent
    sources = sorted(root.glob('*.dot'))
    for source in sources:
        for fmt in ('svg', 'png'):
            result = subprocess.run(
                ['dot', '-T' + fmt, '-Gdpi=120', str(source), '-o', str(source.with_suffix('.' + fmt))],
                capture_output=True, text=True,
            )
            if result.returncode:
                raise SystemExit(result.stderr)
    print(f'{len(sources)}개 구성도의 PNG·SVG 생성 완료')


if __name__ == '__main__':
    main()
