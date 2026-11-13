# -*- coding: utf-8 -*-
"""Add the English | Chinese toggle and the Chinese strings to a finished report / slide HTML (standard library only).
  py localization/tools/apply_html.py <folder | index>     apply to every *.html of the folder, or to index.html (idempotent)
  py localization/tools/apply_html.py <folder> --strip     remove everything this tool added (back to the original English file)
  py localization/tools/apply_html.py <folder> --selftest  apply, strip again and check that the result equals the original
The English markup is never changed: translatable elements only get a data-i18n attribute (loose text is wrapped in a
<span data-i18n data-i18n-w>); the Chinese strings are embedded as JSON; localization/snippets/language-toggle.html does the switching."""
import sys, re, json, html
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import htmlunits as H

REPO = Path(__file__).resolve().parents[2]
SNIPPET = (REPO / 'localization' / 'snippets' / 'language-toggle.html').read_text(encoding='utf-8')
CJK_FONTS = '"Geist","Microsoft YaHei","PingFang SC","Noto Sans SC",'


def strip(src):
    src = re.sub(re.escape(H.MARK_BEGIN) + r'.*?' + re.escape(H.MARK_END) + r'\n?', '', src, flags=re.S)
    src = re.sub(r'<span data-i18n="\d+" data-i18n-w>(.*?)</span>', r'\1', src, flags=re.S)
    src = re.sub(r' data-i18n="\d+"', '', src)
    src = re.sub(r' data-i18n-a="[^"]*"', '', src)
    return src


def zh_svg(svg, cat):
    """Chinese twin of an animated SVG drawing: same shapes, <text> contents from the catalog."""
    head, sep, rest = svg.partition('</style>')

    def rep(m):
        t = re.sub(r'\s+', ' ', html.unescape(m.group(2))).strip()
        e = cat.get(H.key(t))
        if not e or e['zh'] == e['en']:
            return m.group(0)
        return m.group(1) + html.escape(e['zh'], quote=False) + '</text>'
    body = re.sub(r'(<text[^>]*>)([^<]+)</text>', rep, rest)
    head = head.replace('"Geist",', CJK_FONTS, 1) if CJK_FONTS not in head else head
    return head + sep + body


def apply(src, cat):
    src = strip(src)
    units = H.find_units(src)
    edits = []                                   # (pos, delete_len, text)
    zmap, amap, doc = {}, {}, {}
    n = 0
    per_node = {}
    for u in units:
        e = cat.get(H.key(u['text']))
        if not e or not e.get('zh') or e['zh'] == u['text']:
            if not e or not e.get('zh'):
                u['missing'] = True
            continue
        n += 1
        if u['kind'] == 'el':
            zmap[n] = H.from_placeholders(e['zh'], u['tags'])
            per_node.setdefault(id(u['node']), (u['node'], {}))[1]['t'] = n
        elif u['kind'] == 'attr':
            amap[n] = e['zh']
            per_node.setdefault(id(u['node']), (u['node'], {}))[1].setdefault('a', []).append('%s=%d' % (u['attr'], n))
        elif u['kind'] == 'loose':
            zmap[n] = html.escape(e['zh'], quote=False)
            seg = src[u['s0']:u['s1']]
            edits.append((u['s0'], u['s1'] - u['s0'], '<span data-i18n="%d" data-i18n-w>%s</span>' % (n, seg)))
        elif u['kind'] == 'doctitle':
            doc['title'] = e['zh']
        elif u['kind'] == 'metadesc':
            doc['desc'] = e['zh']
    for node, d in per_node.values():
        raw = src[node.s0:node.s1]
        pos = node.s1 - (2 if raw.endswith('/>') else 1)
        ins = ''
        if 't' in d:
            ins += ' data-i18n="%d"' % d['t']
        if 'a' in d:
            ins += ' data-i18n-a="%s"' % ';'.join(d['a'])
        edits.append((pos, 0, ins))
    for pos, dl, text in sorted(edits, key=lambda e: -e[0]):
        src = src[:pos] + text + src[pos + dl:]
    payload = dict(t={str(k): v for k, v in zmap.items()}, a={str(k): v for k, v in amap.items()}, doc=doc)
    m = re.search(r'window\.SVGS\s*=\s*(\{.*?\});\s*\n', src, re.S)
    if m:
        try:
            payload['svg'] = {k: zh_svg(v, cat) for k, v in json.loads(m.group(1)).items()}
        except Exception as ex:
            print('  svg skipped:', ex)
    data = '<script id="i18n-zh" type="application/json">' + json.dumps(payload, ensure_ascii=False).replace('</', '<\\/').replace('<!--', '<\\!--') + '</script>'
    block = H.MARK_BEGIN + '\n' + SNIPPET.replace('<!--I18N_DATA-->', data) + '\n' + H.MARK_END + '\n'
    i = src.rindex('</body>')
    src = src[:i] + block + src[i:]
    missing = [u['text'] for u in units if u.get('missing')]
    return src, n, missing


def main():
    folder = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'apply'
    cat = json.loads((REPO / 'localization' / 'catalogs' / f'{folder}.json').read_text(encoding='utf-8'))['strings']
    for f in ([REPO / 'index.html'] if folder == 'index' else sorted((REPO / folder).glob('*.html'))):
        orig = f.read_bytes().decode('utf-8')
        if mode == '--strip':
            f.write_bytes(strip(orig).encode('utf-8')); print('stripped', f.name); continue
        out, n, missing = apply(orig, cat)
        if mode == '--selftest':
            base = strip(orig)
            print(f.name, 'roundtrip', 'OK' if strip(out) == base else 'DIFFERENT', n, 'translated', len(missing), 'missing')
            continue
        f.write_bytes(out.encode('utf-8'))
        print(f'{f.name}: {n} strings translated, {len(missing)} without Chinese', ('| e.g. ' + missing[0][:60]) if missing else '')


if __name__ == '__main__':
    main()
