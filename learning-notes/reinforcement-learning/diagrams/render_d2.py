"""D2 + ELK로 SVG를 생성하고 resvg로 PNG를 렌더링한다.
필요: D2 v0.9.0, Python fonttools/resvg-py. 실행: python render_d2.py
"""
from pathlib import Path
import base64
import io
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
import resvg_py


def main():
    root = Path(__file__).resolve().parent
    d2 = os.environ.get('D2_BIN') or shutil.which('d2')
    if not d2:
        raise SystemExit('D2 명령이 필요합니다. D2_BIN으로 경로를 지정할 수 있습니다.')
    font = root / 'fonts/TrainingDiagramSans-Medium.ttf'
    font_data = TTFont(font)
    font_data.flavor = 'woff'
    buf = io.BytesIO()
    font_data.save(buf)
    encoded = base64.b64encode(buf.getvalue()).decode()
    ns = '{http://www.w3.org/2000/svg}'
    ET.register_namespace('', ns[1:-1])
    for source in sorted(root.glob('*.d2')):
        svg = source.with_suffix('.svg')
        result = subprocess.run([d2, '--layout=elk', '--pad=18', '--elk-nodeNodeBetweenLayers=45', '--elk-edgeNodeBetweenLayers=25', str(source), str(svg)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(result.stderr)
        tree = ET.parse(svg)
        # Embed a Korean font for browser display; keep native D2 shape layout.
        for style in tree.findall('.//' + ns + 'style'):
            style.text = re.sub(r'@font-face\s*\{[^}]*\}', '', style.text or '')
        style = ET.SubElement(tree.getroot(), ns + 'style')
        style.text = '@font-face{font-family:"Training Diagram Sans";font-weight:500;src:url("data:font/woff;base64,' + encoded + '")}'
        for text in tree.findall('.//' + ns + 'text'):
            text.set('style', (text.get('style') or '') + ';font-family:Training Diagram Sans;font-weight:500')
        tree.write(svg, encoding='unicode', xml_declaration=False)
        source.with_suffix('.png').write_bytes(resvg_py.svg_to_bytes(
            svg_path=str(svg), font_files=[str(font)], font_family='Training Diagram Sans', background='#ffffff'))
    print('D2 구성도 SVG·PNG 생성 완료')


if __name__ == '__main__':
    main()
