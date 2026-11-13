# -*- coding: utf-8 -*-
"""Validate translations before they are applied (standard library only).
  python check.py batch NN [--work <dir>]     check <work>/out/batch-NN.json against <work>/batches/batch-NN.json
  python check.py catalog <folder>            check every translated string of localization/catalogs/<folder>.json
Checks: every id answered; placeholders {1}{/1}{br} identical and in order; every number of the English text is present;
identifiers/acronyms (RISE, GPT-4, SWE-bench, arXiv ids) are kept; glossary terms flagged `must` are used; zh contains Chinese
(unless the string is a name/title that is kept as is); no leftover long English sentence.
Exit code 1 if any error is found (warnings do not fail)."""
import sys, re, json, csv
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PH = re.compile(r'\{/?\d+\}|\{br\}')
NUM = re.compile(r'\d[\d,.]*\d|\d')
IDENT = re.compile(r'\b(?:[A-Z][a-z]*[A-Z0-9][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*|[A-Za-z]+-\d+(?:\.\d+)?|arXiv:\d+\.\d+|[A-Z]{3,}[a-z]*)\b')
CJK = re.compile(r'[一-鿿]')
GLOSS = []
with open(REPO / 'localization' / 'glossary' / 'glossary.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        GLOSS.append(r)
TRANSLATED_ACR = {r['en'] for r in GLOSS if r['policy'] == 'translate'}


def check_one(en, zh):
    errs, warns = [], []
    if not zh.strip():
        return ['empty'], warns
    if zh == en:
        return errs, warns                                   # kept as is (name, title, label like "Tech Insight")
    if PH.findall(en) != PH.findall(zh):
        errs.append('placeholders differ: %s vs %s' % (PH.findall(en), PH.findall(zh)))
    plain_zh = PH.sub('', zh)
    plain_en = PH.sub('', en)
    for m in NUM.finditer(plain_en):
        n = m.group(0)
        if re.match(r'\s*(million|billion|thousand|trillion|k\b|M\b|B\b|K\b)', plain_en[m.end():]):
            continue                                         # 1.35 million -> 135 万: the unit changes the digits
        if n not in plain_zh and n.replace(',', '') not in plain_zh.replace(',', ''):
            errs.append('number missing: ' + n)
    for t in set(IDENT.findall(PH.sub('', en))):
        if t in TRANSLATED_ACR or t.lower() in {g['en'].lower() for g in GLOSS if g['policy'] == 'translate'}:
            continue
        if t not in plain_zh:
            warns.append('identifier not kept: ' + t)
    for g in GLOSS:
        if g['policy'] == 'translate' and g['must'] == '1' and re.search(r'(?i)\b' + re.escape(g['en']) + r'\b', en):
            if g['zh'] not in zh:
                warns.append('glossary: %s -> %s' % (g['en'], g['zh']))
    if not CJK.search(zh) and re.search(r'[A-Za-z]{4,} [A-Za-z]{3,} [A-Za-z]{3,}', plain_zh):
        errs.append('no Chinese in a long English-looking string')
    return errs, warns


def main():
    mode = sys.argv[1]
    work = Path(sys.argv[sys.argv.index('--work') + 1]) if '--work' in sys.argv else REPO / '_archive_removed' / 'i18n-work'
    bad = 0
    if mode == 'batch':
        nn = sys.argv[2]
        src = json.loads((work / 'batches' / f'batch-{nn}.json').read_text(encoding='utf-8'))
        out = json.loads((work / 'out' / f'batch-{nn}.json').read_text(encoding='utf-8'))
        pairs = [(e['id'], e['en'], out.get(e['id'])) for e in src]
        extra = set(out) - {e['id'] for e in src}
        if extra:
            print('unknown ids in answer:', sorted(extra)[:5]); bad += 1
    else:
        folder = sys.argv[2]
        cat = json.loads((REPO / 'localization' / 'catalogs' / f'{folder}.json').read_text(encoding='utf-8'))
        pairs = [(k, v['en'], v.get('zh')) for k, v in cat['strings'].items()]
    nw = 0
    for i, en, zh in pairs:
        if zh is None:
            print('MISSING', i, en[:70]); bad += 1; continue
        errs, warns = check_one(en, zh)
        for e in errs:
            print('ERROR  ', i, e, '|', en[:70], '=>', zh[:70]); bad += 1
        for w in warns:
            nw += 1
            if nw <= 40: print('warning', i, w, '|', en[:60])
    print(f'{len(pairs)} strings, {bad} errors, {nw} warnings')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
