# -*- coding: utf-8 -*-
"""Make the Chinese PowerPoint from the English one (python-pptx; run with Windows `py`).
  py localization/tools/make_cn_pptx.py <folder>
Reads  <folder>/<Name>-tech-insight-slides-EN.pptx  (or ...-slides.pptx before the rename)
Writes <folder>/<Name>-tech-insight-slides-CN.pptx
Every paragraph (shapes, tables, speaker notes) is looked up in localization/catalogs/<folder>.json by its English text.
Formatting is kept (the translation goes into the first run); East Asian font Microsoft YaHei and lang zh-CN are set.
Overflow guard: if the Chinese text would need more lines than the English text, the font is reduced in 0.5 pt steps (floor 75 %);
those shapes are listed so they can be checked by eye. Paragraphs without a Chinese string are listed too."""
import sys, re, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import htmlunits as H
from pptx import Presentation
from pptx.util import Pt
from lxml import etree

REPO = Path(__file__).resolve().parents[2]
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
CJK = re.compile(r'[一-鿿　-〿＀-￯]')
EA_FONT = 'Microsoft YaHei'


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def width_em(t):
    return sum(1.0 if CJK.match(c) else 0.52 for c in t)


def lines(t, width_in, size_pt):
    per_line = max(1.0, width_in * 72 / size_pt)
    return max(1, math.ceil(width_em(t) / per_line))


def set_ea(run):
    rpr = run._r.get_or_add_rPr()
    rpr.set('lang', 'zh-CN')
    for old in rpr.findall('{%s}ea' % A):
        rpr.remove(old)
    ea = etree.Element('{%s}ea' % A, typeface=EA_FONT)
    latin = rpr.find('{%s}latin' % A)
    if latin is not None:
        latin.addnext(ea)
    else:
        nxt = [c for c in rpr if etree.QName(c).localname in ('cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst')]
        if nxt:
            nxt[0].addprevious(ea)
        else:
            rpr.append(ea)


def convert_paragraph(pa, zh, width_in, log, where):
    runs = pa.runs
    if not runs:
        return
    en_text = pa.text.replace('\v', ' ')
    first = runs[0]
    size = first.font.size.pt if first.font.size else None
    first.text = zh
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for br in pa._p.findall('{%s}br' % A):
        pa._p.remove(br)
    set_ea(first)
    if size and width_in and width_in > 0.3:
        need_en, need_zh = lines(en_text, width_in, size), lines(zh, width_in, size)
        s = size
        while need_zh > need_en and s > size * 0.75:
            s -= 0.5
            need_zh = lines(zh, width_in, s)
        if s != size:
            first.font.size = Pt(s)
            log.append(f'{where}: font {size} -> {s} ({zh[:30]})')
        if need_zh > need_en:
            log.append(f'{where}: CHECK, may still be too long ({zh[:30]})')


def main():
    folder = sys.argv[1]
    d = REPO / folder
    cat = json.loads((REPO / 'localization' / 'catalogs' / f'{folder}.json').read_text(encoding='utf-8'))['strings']
    src = next(iter(sorted(d.glob('*-slides-EN.pptx'))), None) or next(iter(sorted(d.glob('*-slides.pptx'))))
    prs = Presentation(str(src))
    log, missing = [], []
    stats = dict(done=0, kept=0)

    def do_tf(tf, width_in, where):
        for pa in tf.paragraphs:
            t = norm(pa.text.replace('\v', ' '))
            if not t or not H.translatable(t):
                continue
            e = cat.get(H.key(t))
            if e is None or not e.get('zh'):
                missing.append(f'{where}: {t[:60]}'); continue
            if e['zh'] == t:
                stats['kept'] += 1; continue
            convert_paragraph(pa, e['zh'], width_in, log, where)
            stats['done'] += 1

    def walk(shapes, where):
        for sh in shapes:
            if sh.shape_type == 6:
                walk(sh.shapes, where)
            if sh.has_text_frame:
                w = sh.width / 914400 if sh.width else None
                do_tf(sh.text_frame, w, where)
            if getattr(sh, 'has_table', False) and sh.has_table:
                cols = [c.width / 914400 for c in sh.table.columns]
                for row in sh.table.rows:
                    for ci, c in enumerate(row.cells):
                        do_tf(c.text_frame, cols[ci], where)
    for i, s in enumerate(prs.slides, 1):
        walk(s.shapes, f'slide {i}')
        if s.has_notes_slide:
            do_tf(s.notes_slide.notes_text_frame, None, f'slide {i} notes')
    out = src.with_name(re.sub(r'-slides(-EN)?\.pptx$', '-slides-CN.pptx', src.name))
    prs.save(str(out))
    work = REPO / '_archive_removed' / 'i18n-work' / 'logs'
    work.mkdir(parents=True, exist_ok=True)
    (work / f'{folder}-cn-pptx.log').write_text('\n'.join(['FONT/OVERFLOW'] + log + ['', 'NO CHINESE FOUND'] + missing), encoding='utf-8')
    print(f'{out.name}: {stats["done"]} paragraphs translated, {stats["kept"]} kept, {len(log)} size notes, {len(missing)} without Chinese')


if __name__ == '__main__':
    main()
