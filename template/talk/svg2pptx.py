# -*- coding: utf-8 -*-
"""Convert one of the animated SVG drawings into NATIVE PowerPoint shapes with NATIVE entrance/exit/motion effects.
The SVG animations are CSS classes with start times (--d, --o, --d2, --dx, --dy); each becomes a PowerPoint effect
with the same start time, all starting automatically when the slide appears (nothing to click).
Use: add_svg(slide, svg_path, left_in, top_in, box_w_in, box_h_in)   (run with Windows python: python-pptx)"""
import re, math, copy
import xml.etree.ElementTree as ET
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

EMU = 914400
FONT = 'Segoe UI'
NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')


# ------------------------------------------------------------------ css
def parse_css(style_text):
    t = re.sub(r'@font-face\s*\{[^}]*\}', '', style_text)
    t = re.sub(r'@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', t)
    rules = []
    for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', t):
        props = dict((k.strip(), v.strip()) for k, v in (p.split(':', 1) for p in body.split(';') if ':' in p))
        for s in sel.split(','):
            rules.append((s.strip(), props))
    return rules


def style_of(el, rules):
    cls = (el.get('class') or '').split()
    p = {}
    for sel, props in rules:
        if sel == el.tag:
            p.update(props)
        elif sel.startswith('.') and set(sel[1:].split('.')) <= set(cls):
            p.update(props)
    for k, v in ((a.split(':', 1)) for a in (el.get('style') or '').split(';') if ':' in a):
        p[k.strip()] = v.strip()
    return p


def num(v, default=0.0):
    m = NUM.search(str(v)) if v is not None else None
    return float(m.group(0)) if m else default


def color(v):
    if v is None or v in ('none', 'transparent'):
        return None
    v = v.strip()
    names = {'white': 'FFFFFF', 'black': '000000'}
    if v in names:
        return names[v]
    if v.startswith('#'):
        v = v[1:]
        if len(v) == 3:
            v = ''.join(c * 2 for c in v)
        return v.upper()
    return None


# ------------------------------------------------------------------ path flattening
def arc_points(x1, y1, rx, ry, phi, fa, fs, x2, y2, n=18):
    phi = math.radians(phi)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num_ = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0, num_ / den)) * (-1 if fa == fs else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = c * cxp - s * cyp + (x1 + x2) / 2, s * cxp + c * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dth > 0: dth -= 2 * math.pi
    if fs and dth < 0: dth += 2 * math.pi
    pts = []
    for i in range(1, n + 1):
        t = th1 + dth * i / n
        pts.append((cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c))
    return pts


def flatten(d):
    toks = re.findall(r'[MmLlCcQqAaZzHhVv]|-?\d*\.?\d+(?:e-?\d+)?', d)
    i, pts, cur, start, cmd, closed = 0, [], (0.0, 0.0), None, None, False
    f = lambda: float(toks[i])
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd in 'Zz':
                closed = True; cur = start
                if start: pts.append(start)
                continue
        if cmd in 'Mm' or cmd in 'Ll':
            x, y = f(), float(toks[i + 1]); i += 2
            if cmd in 'ml': x, y = cur[0] + x, cur[1] + y
            cur = (x, y); pts.append(cur)
            if cmd == 'M': cmd = 'L'
            elif cmd == 'm': cmd = 'l'
            if start is None: start = cur
        elif cmd in 'Hh':
            x = f(); i += 1; cur = (x if cmd == 'H' else cur[0] + x, cur[1]); pts.append(cur)
        elif cmd in 'Vv':
            y = f(); i += 1; cur = (cur[0], y if cmd == 'V' else cur[1] + y); pts.append(cur)
        elif cmd in 'Cc':
            v = [float(t) for t in toks[i:i + 6]]; i += 6
            if cmd == 'c': v = [v[0] + cur[0], v[1] + cur[1], v[2] + cur[0], v[3] + cur[1], v[4] + cur[0], v[5] + cur[1]]
            p0 = cur
            for k in range(1, 17):
                t = k / 16; u = 1 - t
                pts.append((u**3 * p0[0] + 3 * u * u * t * v[0] + 3 * u * t * t * v[2] + t**3 * v[4],
                            u**3 * p0[1] + 3 * u * u * t * v[1] + 3 * u * t * t * v[3] + t**3 * v[5]))
            cur = (v[4], v[5])
        elif cmd in 'Qq':
            v = [float(t) for t in toks[i:i + 4]]; i += 4
            if cmd == 'q': v = [v[0] + cur[0], v[1] + cur[1], v[2] + cur[0], v[3] + cur[1]]
            p0 = cur
            for k in range(1, 13):
                t = k / 12; u = 1 - t
                pts.append((u * u * p0[0] + 2 * u * t * v[0] + t * t * v[2], u * u * p0[1] + 2 * u * t * v[1] + t * t * v[3]))
            cur = (v[2], v[3])
        elif cmd in 'Aa':
            v = [float(t) for t in toks[i:i + 7]]; i += 7
            x, y = (v[5], v[6]) if cmd == 'A' else (cur[0] + v[5], cur[1] + v[6])
            pts.extend(arc_points(cur[0], cur[1], v[0], v[1], v[2], int(v[3]), int(v[4]), x, y)); cur = (x, y)
        else:
            i += 1
    return pts, closed


# ------------------------------------------------------------------ timing xml
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'


class Timing:
    def __init__(self):
        self.fx = []                                   # (t_ms, spid, kind, dur_ms, arg)

    def add(self, spid, kind, t, dur=0.5, arg=None):
        self.fx.append((int(round(t * 1000)), spid, kind, int(round(dur * 1000)), arg))

    def xml(self):
        if not self.fx:
            return None
        self.fx.sort(key=lambda e: e[0])
        n = [3]

        def nid():
            n[0] += 1
            return n[0]

        def tgt(spid): return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'

        def vis(spid, val, delay=0):
            return (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst></p:cTn>{tgt(spid)}'
                    f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="{val}"/></p:to></p:set>')

        out = []
        for k, (t, spid, kind, dur, arg) in enumerate(self.fx):
            node = 'afterEffect' if k == 0 else 'withEffect'
            if kind == 'fade':
                pid, cls, sub = 10, 'entr', 0
                inner = vis(spid, 'visible') + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>{tgt(spid)}</p:cBhvr></p:animEffect>'
            elif kind == 'wipe':
                sub, filt = {'left': (8, 'wipe(left)'), 'right': (2, 'wipe(right)'), 'top': (1, 'wipe(down)'), 'bottom': (4, 'wipe(up)')}[arg]
                pid, cls = 22, 'entr'
                inner = vis(spid, 'visible') + f'<p:animEffect transition="in" filter="{filt}"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>{tgt(spid)}</p:cBhvr></p:animEffect>'
            elif kind == 'out':
                pid, cls, sub = 10, 'exit', 0
                inner = (f'<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>{tgt(spid)}</p:cBhvr></p:animEffect>'
                         + vis(spid, 'hidden', max(dur - 1, 0)))
            elif kind == 'move':
                pid, cls, sub = 0, 'path', 0
                dx, dy = arg
                inner = (f'<p:animMotion origin="layout" path="M 0 0 L {dx:.5f} {dy:.5f} E" pathEditMode="relative" rAng="0" ptsTypes="AA">'
                         f'<p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/>{tgt(spid)}'
                         f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr></p:animMotion>')
            else:
                continue
            out.append(f'<p:par><p:cTn id="{nid()}" presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}" fill="hold" nodeType="{node}">'
                       f'<p:stCondLst><p:cond delay="{t}"/></p:stCondLst><p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>')
        return (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
                f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                f'<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
                f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                + ''.join(out) +
                '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
                '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')


# ------------------------------------------------------------------ converter
class Conv:
    def __init__(self, slide, svg_path, left, top, bw, bh):
        txt = open(svg_path, encoding='utf-8').read()
        txt = re.sub(r'<style>.*?</style>', lambda m: m.group(0), txt, flags=re.S)
        self.root = ET.fromstring(txt)
        self.slide = slide
        vb = [float(x) for x in self.root.get('viewBox').split()]
        self.vx, self.vy, vw, vh = vb
        self.s = min(bw / vw, bh / vh)                         # inches per svg px
        self.ox = left + (bw - vw * self.s) / 2
        self.oy = top + (bh - vh * self.s) / 2
        self.rules = []
        for st in self.root.iter('{http://www.w3.org/2000/svg}style'):
            self.rules += parse_css(st.text or '')
        self.T = Timing()
        self.sw_in, self.sh_in = 13.333, 7.5

    # coordinates
    def X(self, x): return int((self.ox + (x - self.vx) * self.s) * EMU)
    def Y(self, y): return int((self.oy + (y - self.vy) * self.s) * EMU)
    def L(self, v): return int(v * self.s * EMU)

    # animation context ------------------------------------------------
    def ctx_for(self, el, parent):
        c = dict(parent)
        cls = (el.get('class') or '').split()
        st = {}
        for a in (el.get('style') or '').split(';'):
            if ':' in a:
                k, v = a.split(':', 1); st[k.strip()] = v.strip()
        d = num(st.get('--d'), 0.0)
        if 'n' in cls: c['ent'] = ('fade', d, 0.55, None)
        if 'dm' in cls: c['ent'] = ('fade', d, 0.55, None); c['dim'] = (d, num(st.get('--d2'), 5.0))
        if 'd' in cls: c['ent'] = ('wipe', d, 0.7, 'draw')
        if 'g' in cls and el.tag.endswith('rect') and 'class' in el.attrib and re.search(r'\bg\b', el.get('class')): c['ent'] = ('wipe', d, 1.2, 'left')
        if 'rej' in cls: c['ent'] = ('fade', d, 0.26, None); c['out'] = (d + 0.88 * 4.4, 0.5)
        if 'fade' in cls: c['out'] = (num(st.get('--o'), 0.0), 0.7)
        if 'mvin' in cls:
            c['ent'] = ('fade', d, 0.4, None); c['mv'] = (d + 0.5, num(st.get('--dx')), num(st.get('--dy')), 1.1)
        if 'mvout' in cls:
            c['mv'] = (d + 0.5, num(st.get('--dx')), num(st.get('--dy')), 1.1)
            if 'go' in cls: c['out'] = (d + 1.7, 0.5)
        if 'bad' in cls: c['bad'] = 6.4
        return c

    def effects(self, spid, ctx, pts=None, twin=False):
        ent = ctx.get('ent')
        if ent:
            kind, t, dur, arg = ent
            if kind == 'wipe':
                if arg == 'draw':
                    (x0, y0), (x1, y1) = pts[0], pts[-1]
                    dx, dy = x1 - x0, y1 - y0
                    arg = ('left' if dx >= 0 else 'right') if abs(dx) >= abs(dy) else ('top' if dy >= 0 else 'bottom')
                self.T.add(spid, 'wipe', t, dur, arg)
            else:
                self.T.add(spid, 'fade', t, dur)
        if ctx.get('out'): self.T.add(spid, 'out', ctx['out'][0], ctx['out'][1])
        if ctx.get('mv'):
            t, dx, dy, dur = ctx['mv']
            self.T.add(spid, 'move', t, dur, (dx * self.s / self.sw_in, dy * self.s / self.sh_in))

    # shapes -------------------------------------------------------------
    def style_shape(self, sp, fill, stroke, sw, alpha=1.0, dash=None, arrow=None):
        if fill:
            sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor.from_string(fill)
            if alpha < 1: self.alpha(sp._element.spPr.find(qn('a:solidFill')), alpha)
        else:
            sp.fill.background()
        if stroke:
            sp.line.color.rgb = RGBColor.from_string(stroke); sp.line.width = Pt(max(0.5, sw * self.s * 72))
            ln = sp._element.spPr.find(qn('a:ln'))
            if alpha < 1: self.alpha(ln.find(qn('a:solidFill')), alpha)
            if dash:
                e = etree.SubElement(ln, qn('a:prstDash')); e.set('val', 'dash')
            if arrow:
                e = etree.SubElement(ln, qn('a:tailEnd')); e.set('type', 'triangle'); e.set('w', 'med'); e.set('len', 'med')
        else:
            sp.line.fill.background()
        try: sp.shadow.inherit = False
        except Exception: pass

    @staticmethod
    def alpha(solid, a):
        clr = solid[0]
        e = etree.SubElement(clr, qn('a:alpha')); e.set('val', str(int(a * 100000)))

    def make(self, el, st, ctx, override=None, alpha_mul=1.0):
        """create one native shape for the svg element, return (shape, pts)"""
        tag = el.tag.split('}')[1]
        A = lambda k, d=None: el.get(k, d)
        fill = color(st.get('fill', A('fill', 'black' if tag == 'text' else None)))
        stroke = color(st.get('stroke', A('stroke')))
        sw = num(st.get('stroke-width', A('stroke-width')), 1.0)
        alpha = num(A('opacity'), 1.0) * alpha_mul
        if override:
            fill = override.get('fill', fill); stroke = override.get('stroke', stroke)
        dash = A('stroke-dasharray') not in (None, '') and 'class' in el.attrib and True
        if tag == 'rect':
            x, y, w, h = (num(A(k)) for k in ('x', 'y', 'width', 'height'))
            rx = num(A('rx'))
            sp = self.slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rx else MSO_SHAPE.RECTANGLE, self.X(x), self.Y(y), self.L(w), self.L(h))
            if rx: sp.adjustments[0] = min(0.5, rx / min(w, h))
            self.style_shape(sp, fill, stroke, sw, alpha, bool(A('stroke-dasharray')))
            return sp, None
        if tag in ('circle', 'ellipse'):
            cx, cy = num(A('cx')), num(A('cy'))
            rx = num(A('r')) if tag == 'circle' else num(A('rx'))
            ry = rx if tag == 'circle' else num(A('ry'))
            sp = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, self.X(cx - rx), self.Y(cy - ry), self.L(2 * rx), self.L(2 * ry))
            self.style_shape(sp, fill, stroke, sw, alpha, bool(A('stroke-dasharray')))
            return sp, None
        if tag in ('path', 'line', 'polyline'):
            if tag == 'line':
                pts, closed = [(num(A('x1')), num(A('y1'))), (num(A('x2')), num(A('y2')))], False
            elif tag == 'polyline':
                v = [float(t) for t in NUM.findall(A('points'))]; pts, closed = list(zip(v[::2], v[1::2])), False
            else:
                pts, closed = flatten(A('d'))
            if len(pts) < 2: return None, None
            P_ = [(self.X(x), self.Y(y)) for x, y in pts]
            fb = self.slide.shapes.build_freeform(P_[0][0], P_[0][1], scale=1.0)
            fb.add_line_segments(P_[1:], close=closed)
            sp = fb.convert_to_shape(0, 0)
            self.style_shape(sp, fill if tag == 'path' else None, stroke, sw, alpha, bool(A('stroke-dasharray')), arrow=bool(A('marker-end')) and stroke is not None)
            return sp, pts
        return None, None

    def text(self, el, st, ctx):
        s = el.text or ''
        if not s.strip(): return None
        fs_px = num(st.get('font-size'), 16.0)
        fs_in = fs_px * self.s
        x, y = num(el.get('x')), num(el.get('y'))
        anchor = st.get('text-anchor', 'start')
        wid = max(0.3, len(s) * fs_in * 0.62 + 0.3)
        left = self.ox + (x - self.vx) * self.s
        if anchor == 'middle': left -= wid / 2
        elif anchor == 'end': left -= wid
        top = self.oy + (y - self.vy) * self.s - 1.079 * fs_in
        tb = self.slide.shapes.add_textbox(int(left * EMU), int(top * EMU), int(wid * EMU), int(fs_in * 1.4 * EMU))
        tf = tb.text_frame; tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.TOP
        p = tf.paragraphs[0]
        p.alignment = {'middle': PP_ALIGN.CENTER, 'end': PP_ALIGN.RIGHT}.get(anchor, PP_ALIGN.LEFT)
        r = p.add_run(); r.text = s
        r.font.size = Pt(round(fs_in * 72 * 2) / 2); r.font.name = FONT
        r.font.bold = num(st.get('font-weight'), 400) >= 600
        r.font.color.rgb = RGBColor.from_string(color(st.get('fill', '#1f2328')) or '1F2328')
        return tb

    # walk ---------------------------------------------------------------
    def walk(self, el, parent_ctx):
        tag = el.tag.split('}')[1]
        if tag in ('defs', 'style', 'title', 'marker'):
            return
        ctx = self.ctx_for(el, parent_ctx)
        if tag == 'g':
            for ch in el:
                self.walk(ch, ctx)
            return
        st = style_of(el, self.rules)
        if tag == 'text':
            sp = self.text(el, st, ctx)
            if sp is not None: self.effects(sp.shape_id, ctx)
            return
        dim = ctx.get('dim')
        if dim:                                                    # bright for a while, then dimmed to 20 %
            sp, pts = self.make(el, st, ctx)
            if sp is None: return
            c1 = dict(ctx); c1['out'] = (dim[1], 0.6); c1.pop('dim')
            self.effects(sp.shape_id, c1, pts)
            sp2, _ = self.make(el, st, ctx, alpha_mul=0.2)
            self.T.add(sp2.shape_id, 'fade', dim[1], 0.6)
            return
        sp, pts = self.make(el, st, ctx)
        if sp is None: return
        self.effects(sp.shape_id, ctx, pts)
        if ctx.get('bad'):                                         # turns red once rejected
            sp2, _ = self.make(el, st, ctx, override=dict(fill='FBE6E3', stroke='C0392B'))
            self.T.add(sp2.shape_id, 'fade', ctx['bad'], 0.4)

    def run(self):
        for ch in self.root:
            self.walk(ch, {})
        x = self.T.xml()
        if x:
            sld = self.slide._element
            for old in sld.findall(qn('p:timing')): sld.remove(old)
            t = etree.fromstring(x)
            ext = sld.find(qn('p:extLst'))
            if ext is not None: ext.addprevious(t)
            else: sld.append(t)


def add_svg(slide, svg_path, left, top, bw, bh):
    Conv(slide, svg_path, left, top, bw, bh).run()
