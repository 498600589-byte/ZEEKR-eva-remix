"""Build the offline style comparison page with a local lottie-web runtime."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lottie-web', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    styles = ROOT / 'styles'
    data = json.loads((styles / 'catalog.json').read_bytes())
    for style in data['styles'].values():
        style['animations'] = {
            row['name']: json.loads((styles / style['path'] / f"{row['name']}.json").read_bytes())
            for row in data['expressions'].values()
        }
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    template = (ROOT / 'tools' / 'style_preview.html').read_text(encoding='utf-8')
    runtime = args.lottie_web.read_text(encoding='utf-8')
    args.output.write_text(template.replace('@@LOTTIE@@', runtime).replace('@@DATA@@', payload), encoding='utf-8')


if __name__ == '__main__':
    main()
