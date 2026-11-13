# -*- coding: utf-8 -*-
"""Find the translatable text units in a finished Tech Insight HTML file (report or slides).
Standard library only. No re-serialising: the original text is kept byte for byte and only small insertions are made.

A *unit* is an element whose content is plain text plus inline tags (a, b, i, em, strong, span, sup, sub, br, code ...).
Inline tags are turned into placeholders so a translator keeps them:  <a href=..>x</a> -> {1}x{/1},  <br> -> {br}.
"""
import re, html, hashlib
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
INLINE = {'a', 'b', 'i', 'em', 'strong', 'span', 'sup', 'sub', 'br', 'code', 'u', 'small', 'mark', 'abbr', 'cite', 'kbd', 'wbr'}
SKIP_TAGS = {'script', 'style', 'svg', 'noscript', 'textarea', 'pre', 'head', 'template', 'iframe'}
SKIP_CLASSES = {'cite', 'reflist', 'ref', 'r', 'code', 'brandmark', 'sr-only', 'lang-toggle'}      # references, citations, code links, brand mark
ATTRS = ('alt', 'title', 'aria-label', 'data-toc', 'data-group', 'placeholder')
MARK_BEGIN, MARK_END = '<!-- i18n:begin -->', '<!-- i18n:end -->'


class Node:
    __slots__ = ('tag', 'attrs', 's0', 's1', 'e0', 'e1', 'parent', 'kids')

    def __init__(self, tag, attrs, s0, s1, parent):
        self.tag, self.attrs, self.s0, self.s1, self.parent = tag, dict(attrs), s0, s1, parent
        self.e0 = self.e1 = None          # end tag span (None for void / unclosed)
        self.kids = []

    def cls(self):
        return set((self.attrs.get('class') or '').split())


class _P(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer('\n', src):
            self.lines.append(m.end())
        self.root = Node('#root', {}, 0, 0, None)
        self.root.e0 = len(src)
        self.cur = self.root

    def pos(self):
        l, c = self.getpos()
        return self.lines[l - 1] + c

    def handle_starttag(self, tag, attrs):
        s0 = self.pos(); raw = self.get_starttag_text(); s1 = s0 + len(raw)
        n = Node(tag, attrs, s0, s1, self.cur); self.cur.kids.append(n)
        if tag in VOID or raw.endswith('/>'):
            n.e0 = n.e1 = s1
        else:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        s0 = self.pos(); raw = self.get_starttag_text(); s1 = s0 + len(raw)
        n = Node(tag, attrs, s0, s1, self.cur); self.cur.kids.append(n); n.e0 = n.e1 = s1

    def handle_endtag(self, tag):
        s0 = self.pos(); e = self.src.index('>', s0) + 1
        c = self.cur
        while c is not self.root and c.tag != tag:
            c = c.parent
        if c is self.root:
            return
        x = self.cur
        while x is not c:                      # elements the source never closed end where the parent closes
            x.e0 = x.e1 = s0
            x = x.parent
        c.e0, c.e1 = s0, e
        self.cur = c.parent


def parse(src):
    p = _P(src); p.feed(src); p.close()

    def fix(n):
        for k in n.kids:
            if k.e0 is None:
                k.e0 = k.e1 = len(src)
            fix(k)
    fix(p.root)
    return p.root


def content_span(n):
    return n.s1, (n.e0 if n.e0 is not None else n.s1)


def inline_only(n):
    return all(k.tag in INLINE and inline_only(k) for k in n.kids)


def skipped(n):
    return n.tag in SKIP_TAGS or bool(n.cls() & SKIP_CLASSES) or n.attrs.get('translate') == 'no'


WORD = re.compile(r'[A-Za-z]{2,}')


def translatable(text):
    t = text.strip()
    if not WORD.search(t):
        return False
    if re.fullmatch(r'[\w./:%#?=&@+-]+', t) and ('/' in t or '.' in t) and ' ' not in t:     # url, file name, id
        return False
    return True


def to_placeholders(src, a, b, node=None):
    """return (text with placeholders, [tag source strings in placeholder order])"""
    out, tags = [], []

    def walk(lo, hi, kids):
        pos = lo
        for k in kids:
            out.append(html.unescape(src[pos:k.s0]))
            if k.tag == 'br':
                tags.append(('br', src[k.s0:k.s1])); out.append('{br}')
            elif k.tag == 'wbr':
                pass
            else:
                idx = len(tags) + 1
                tags.append((idx, src[k.s0:k.s1], src[k.e0:k.e1] if k.e1 else ''))
                out.append('{%d}' % idx)
                cs, ce = content_span(k)
                walk(cs, ce, k.kids)
                out.append('{/%d}' % idx)
            pos = k.e1 if k.e1 else k.s1
        out.append(html.unescape(src[pos:hi]))
    kids = node.kids if node is not None else []
    walk(a, b, kids)
    return re.sub(r'\s+', ' ', ''.join(out)).strip(), tags


def from_placeholders(zh, tags):
    """expand a translated string with placeholders back to HTML using this occurrence's tags"""
    by = {t[0]: t for t in tags}

    def rep(m):
        g = m.group(1)
        if g == 'br':
            return by['br'][1] if 'br' in by else '<br>'
        if g.startswith('/'):
            t = by.get(int(g[1:])); return t[2] if t else ''
        t = by.get(int(g)); return t[1] if t else ''
    esc = html.escape(zh, quote=False)
    return re.sub(r'\{(/?\d+|br)\}', rep, esc)


def key(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:10]


def find_units(src):
    """returns list of dict(kind='el'|'loose'|'attr', ...) in document order"""
    root = parse(src)
    units = []

    def visit(n, in_body):
        if n.tag == 'body':
            in_body = True
        if skipped(n):
            return
        for k in n.kids:
            pass
        a, b = content_span(n)
        if n.tag not in ('#root', 'html', 'body', 'main', 'nav', 'header') and inline_only(n):     # nav: its links are separate units, the toggle lives inside it
            text, tags = to_placeholders(src, a, b, n)
            if translatable(re.sub(r'\{/?\w+\}', '', text)):
                units.append(dict(kind='el', node=n, text=text, tags=tags))
        else:
            # loose text directly inside a mixed element
            pos = a
            for k in n.kids + [None]:
                hi = k.s0 if k is not None else b
                seg = src[pos:hi]
                if k is None or True:
                    t = html.unescape(re.sub(r'\s+', ' ', seg)).strip()
                    if in_body and translatable(t) and n.tag not in ('#root', 'html'):
                        units.append(dict(kind='loose', s0=pos, s1=hi, text=t, tags=[], node=n))
                if k is not None:
                    visit(k, in_body)
                    pos = k.e1 if k.e1 else k.s1
        # attributes
        for name in ATTRS:
            v = n.attrs.get(name)
            if v and translatable(v) and not (name == 'title' and n.tag == 'title'):
                units.append(dict(kind='attr', node=n, attr=name, text=html.unescape(v), tags=[]))

    visit(root, False)
    # <title> and meta description live in <head>
    head_end = src.find('</head>')
    head = src[:head_end if head_end > 0 else 0]
    for m in re.finditer(r'<title>(.*?)</title>', head, re.S):
        t = html.unescape(m.group(1)).strip()
        if translatable(t):
            units.append(dict(kind='doctitle', s0=m.start(1), s1=m.end(1), text=t, tags=[], node=None))
    for m in re.finditer(r'<meta\s+name="description"\s+content="([^"]*)"', head):
        t = html.unescape(m.group(1)).strip()
        if translatable(t):
            units.append(dict(kind='metadesc', s0=m.start(1), s1=m.end(1), text=t, tags=[], node=None))
    return units
