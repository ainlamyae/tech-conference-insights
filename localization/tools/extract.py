# -*- coding: utf-8 -*-
"""Collect every translatable string of one conference folder (report.html, slides.html, EN pptx, SVG drawings)
and write the ones that have no Chinese yet to a to-do file.
Run (Windows):  py localization/tools/extract.py <folder-name | index> [--work <dir>]
Catalog (kept, reusable):  localization/catalogs/<folder>.json
To-do (temporary):         <work>/todo/<folder>.json      (default work dir: _archive_removed/i18n-work)"""
import sys, json, re, html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import htmlunits as H

REPO = Path(__file__).resolve().parents[2]
CAT = REPO / 'localization' / 'catalogs'
KEEP_AUTO = re.compile(r'^\s*(\[\d+\]|Code\s*·)')           # reference lines, code links: kept as they are


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def html_strings(path):
    src = path.read_text(encoding='utf-8')
    out = []
    for u in H.find_units(src):
        n = u.get('node')
        ctx = (n.tag + ('.' + n.attrs['class'].split()[0] if n is not None and n.attrs.get('class') else '')) if n is not None else u['kind']
        if u['kind'] == 'attr':
            ctx = 'attr:' + u['attr']
        out.append((u['text'], ctx))
    # animated SVG drawings stored as strings in the page (Open Day style)
    m = re.search(r'window\.SVGS\s*=\s*(\{.*?\});\s*\n', src, re.S)
    if m:
        try:
            for name, svg in json.loads(m.group(1)).items():
                for t in re.findall(r'<text[^>]*>([^<]+)</text>', re.sub(r'<style>.*?</style>', '', svg, flags=re.S)):
                    t = norm(html.unescape(t))
                    if H.translatable(t):
                        out.append((t, 'svg:' + name))
        except Exception as e:
            print('  svg parse failed', e)
    return out


def pptx_strings(path):
    from pptx import Presentation
    p = Presentation(str(path))
    out = []

    def para_texts(tf, ctx):
        for pa in tf.paragraphs:
            t = norm(pa.text.replace('\v', ' '))
            if t and H.translatable(t):
                out.append((t, ctx))

    def walk(shapes, ctx):
        for sh in shapes:
            if sh.shape_type == 6:
                walk(sh.shapes, ctx)
            if sh.has_text_frame:
                para_texts(sh.text_frame, ctx)
            if getattr(sh, 'has_table', False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        para_texts(c.text_frame, ctx)
    for i, s in enumerate(p.slides, 1):
        walk(s.shapes, 'pptx')
        if s.has_notes_slide:
            para_texts(s.notes_slide.notes_text_frame, 'pptx-notes')
    return out


def main():
    folder = sys.argv[1]
    work = Path(sys.argv[sys.argv.index('--work') + 1]) if '--work' in sys.argv else REPO / '_archive_removed' / 'i18n-work'
    d = REPO / folder
    is_index = folder == 'index'                  # the overview page index.html at the repository root
    cat_path = CAT / f'{folder}.json'
    cat = json.loads(cat_path.read_text(encoding='utf-8')) if cat_path.exists() else {'folder': folder, 'strings': {}}
    found = {}
    for f in ([REPO / 'index.html'] if is_index else sorted(d.glob('*.html'))):
        for t, ctx in html_strings(f):
            found.setdefault(H.key(t), dict(en=t, ctx=set(), files=set()))['ctx'].add(ctx); found[H.key(t)]['files'].add('report' if 'report' in f.name else 'slides')
    for f in ([] if is_index else sorted(d.glob('*-slides*.pptx'))):
        if f.name.endswith('-CN.pptx'):
            continue
        for t, ctx in pptx_strings(f):
            found.setdefault(H.key(t), dict(en=t, ctx=set(), files=set()))['ctx'].add(ctx); found[H.key(t)]['files'].add('pptx')
    todo = []
    for k, v in found.items():
        have = cat['strings'].get(k)
        if KEEP_AUTO.match(v['en']):
            cat['strings'][k] = dict(en=v['en'], zh=v['en'], cls='keep')
            continue
        if have and have.get('zh'):
            continue
        todo.append(dict(id=k, en=v['en'], ctx=sorted(v['ctx'])[:3], files=sorted(v['files'])))
    cat_path.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding='utf-8')
    (work / 'todo').mkdir(parents=True, exist_ok=True)
    (work / 'todo' / f'{folder}.json').write_text(json.dumps(todo, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{folder}: {len(found)} unique strings, {len(todo)} to translate')


if __name__ == '__main__':
    main()
