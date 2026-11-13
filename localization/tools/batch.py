# -*- coding: utf-8 -*-
"""Split the to-do files into translation batches, and merge the translated batches back into the catalogs.
  py localization/tools/batch.py make  [--size 300] [--work <dir>]     -> <work>/batches/batch-NN.json  (list of {id, en, ctx})
  py localization/tools/batch.py merge [--work <dir>]                  <- <work>/out/batch-NN.json       ({id: zh})  -> catalogs/<folder>.json
A batch file is what a translator (person or model) gets; the answer is one JSON object {id: Chinese}."""
import sys, json, glob
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CAT = REPO / 'localization' / 'catalogs'


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    mode = sys.argv[1]
    work = Path(arg('--work', REPO / '_archive_removed' / 'i18n-work'))
    if mode == 'make':
        size = int(arg('--size', 300))
        seen, items = {}, []
        for f in sorted((work / 'todo').glob('*.json')):
            for e in json.loads(f.read_text(encoding='utf-8')):
                if e['id'] in seen:
                    seen[e['id']]['ctx'] = sorted(set(seen[e['id']]['ctx']) | set(e['ctx']))[:3]
                    continue
                seen[e['id']] = dict(id=e['id'], en=e['en'], ctx=e['ctx'])
                items.append(seen[e['id']])
        (work / 'batches').mkdir(exist_ok=True)
        for old in (work / 'batches').glob('batch-*.json'):
            old.unlink()
        n = 0
        for i in range(0, len(items), size):
            n += 1
            (work / 'batches' / f'batch-{n:02d}.json').write_text(json.dumps(items[i:i + size], ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{len(items)} unique strings -> {n} batches')
    elif mode == 'merge':
        out = {}
        for f in sorted((work / 'out').glob('batch-*.json')):
            out.update(json.loads(f.read_text(encoding='utf-8')))
        total = 0
        for f in sorted((work / 'todo').glob('*.json')):
            folder = f.stem
            cp = CAT / f'{folder}.json'
            cat = json.loads(cp.read_text(encoding='utf-8'))
            for e in json.loads(f.read_text(encoding='utf-8')):
                if e['id'] in out and out[e['id']].strip():
                    cat['strings'][e['id']] = dict(en=e['en'], zh=out[e['id']].strip(), cls=(e['ctx'] or ['body'])[0])
                    total += 1
            cp.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'merged {total} strings from {len(out)} translated ids')


if __name__ == '__main__':
    main()
