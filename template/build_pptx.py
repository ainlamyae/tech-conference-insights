#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build tech-insight-slides-template.pptx from the shared Tech Insight standard.
Run:  py build_pptx.py
See STYLE-GUIDE.md for the schema, palette and type system this encodes.

The PPTX uses Segoe UI (sans) + Consolas (mono/numbers) because Geist is not a
default Office font. Install Geist and swap the theme font in Slide Master -> Fonts
to brand-match the HTML exactly; keep the sans/mono split either way.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---- palette (see STYLE-GUIDE §5) -------------------------------------------
C = {
    "bg":"F4F5F6","card":"FAFBFB","fg":"1B1D1F","muted":"6D7277","line":"DDE1E4",
    "inset":"ECEFF1","brand":"123524","accent":"1B7049","ok":"12A66A","warn":"8A5508",
    "bad":"E7000B","plan":"5D34BD","work":"2788F5","white":"FFFFFF",
}
def rgb(k): return RGBColor.from_string(C[k])
SANS, MONO = "Segoe UI", "Consolas"

# field label -> spine colour (see STYLE-GUIDE §5)
FIELD_COLOR = {"GOAL":"accent","CHALLENGE":"bad","METHOD":"plan","NOVELTY":"work","IMPACT":"brand"}

prs = Presentation()
prs.slide_width  = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height

# ---------- low-level helpers ------------------------------------------------
def add_slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb("bg")
    return s

def rect(s, l, t, w, h, fill=None, line=None, line_w=1.0, radius=False, dash=None):
    shp_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sp = s.shapes.add_shape(shp_type, Inches(l), Inches(t), Inches(w), Inches(h))
    if radius:
        try: sp.adjustments[0] = 0.06
        except Exception: pass
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = rgb(line); sp.line.width = Pt(line_w)
        if dash:
            ln = sp.line._get_or_add_ln(); d = ln.makeelement(qn('a:prstDash'), {'val': dash}); ln.append(d)
    sp.shadow.inherit = False
    return sp

def text(s, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         space_after=4, line_spacing=1.08, wrap=True):
    """runs: list of paragraphs; each paragraph is a list of (txt, font, size, color, bold, italic)."""
    tb = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    for m in ("left","right","top","bottom"):
        setattr(tf, f"margin_{m}", 0)
    for pi, para in enumerate(runs):
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        p.alignment = align; p.space_before = Pt(0); p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        for (t_, font, size, color, bold, *rest) in para:
            r = p.add_run(); r.text = t_
            r.font.name = font; r.font.size = Pt(size); r.font.bold = bold
            r.font.color.rgb = rgb(color)
            if rest and rest[0]: r.font.italic = True
    return tb

def R(t_, font=SANS, size=14, color="fg", bold=False, italic=False):
    return (t_, font, size, color, bold, italic)

LM, RM = 0.78, 0.78           # left / right page margins
CW = 13.333 - LM - RM         # content width

def kicker_head(s, kick, title, title_size=30):
    text(s, LM, 0.52, CW, 0.4, [[R(kick, MONO, 13, "muted", True)]])
    text(s, LM, 0.92, CW, 1.1, [[R(title, SANS, title_size, "fg", True)]], line_spacing=1.08)

# =============================================================================
# 1) CONFERENCE INFORMATION  (slide 1)
# =============================================================================
s = add_slide()
rect(s, LM, 1.7, 0.34, 0.34, fill="brand", radius=True)
text(s, LM+0.46, 1.66, 6, 0.45, [[R("Tech Insight", MONO, 18, "fg", True)]])
text(s, LM, 2.35, CW, 0.4, [[R("Tech Insight Report", MONO, 13, "muted", True)]])
text(s, LM, 2.8, CW, 1.0, [[R("[[CONFERENCE YEAR — e.g. ICLR 2026]]", SANS, 50, "fg", True)]])
text(s, LM, 3.9, CW, 0.5, [[R("[[Full conference name]]", SANS, 22, "muted")]])
text(s, LM, 4.45, CW, 0.5, [[R("[[City, Country]] · [[Month YYYY]]", SANS, 22, "fg", True)]])
# conference facts (no presenter / classification metadata)
for lab, val, xx, wd in [("Location", "[[City, Country]]", LM, 3.0),
                         ("Dates", "[[Month D–D, YYYY]]", LM+3.2, 2.6),
                         ("Focus", "[[The angle this deck takes]]", LM+6.1, 5.6)]:
    text(s, xx, 5.7, wd, 1.1, [[R(lab, SANS, 11, "muted")],[R(val, MONO, 14, "fg", True)]], space_after=3, line_spacing=1.05)

# =============================================================================
# 2) TABLE OF CONTENTS  (slide 2)
# =============================================================================
s = add_slide()
kicker_head(s, "CONTENTS", "Papers covered, by theme")
rows = [("[[Conference overview]]","[[dates, scale, themes]]"),
        ("[[Paper 1 short title]]","[[one line]]"),
        ("[[Paper 2 short title]]","[[one line]]"),
        ("[[Conclusions]]","[[insights · vision · implications]]")]
y = 2.1
for n,(b,sp) in enumerate(rows, 1):
    rect(s, LM, y, CW, 0.82, fill="card", line="line", radius=True)
    text(s, LM+0.28, y, 0.6, 0.82, [[R(f"{n:02d}", MONO, 18, "accent", True)]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, LM+0.95, y, CW-1.2, 0.82,
         [[R(b+"  ", SANS, 18, "fg", True), R("— "+sp, SANS, 15, "muted")]],
         anchor=MSO_ANCHOR.MIDDLE)
    y += 0.98

# =============================================================================
# 3) CONFERENCE STATISTICS  (slide 3)
# =============================================================================
s = add_slide()
kicker_head(s, "CONFERENCE STATISTICS", "[[Full conference name, dates & place]]")
rect(s, LM, 2.1, CW, 1.75, fill="card", line="line", radius=True)
tiles = [("[[5,404]]","submissions"),("[[1,042]]","accepted"),
         ("[[19.3%]]","acceptance rate"),("[[6 days]]","[[Aug 16–22]]")]
tw = CW/4
for i,(num,lab) in enumerate(tiles):
    tx = LM + i*tw
    text(s, tx+0.3, 2.5, tw-0.35, 0.8, [[R(num, MONO, 32, "fg", True)]], wrap=False)
    text(s, tx+0.3, 3.35, tw-0.35, 0.4, [[R(lab, SANS, 14, "muted")]])
text(s, LM, 4.2, CW, 1.5,
     [[R("Headline themes:  ", SANS, 18, "fg", True),
       R("[[theme 1 · theme 2 · theme 3 · theme 4 — the topics that dominated the program]].", SANS, 18, "muted")]],
     line_spacing=1.3)

# =============================================================================
# 4) INSIGHT SLIDE  (the core card) — generated by a function so it is reusable
# =============================================================================
def insight_slide(num, title, author, affil, fields, ref, code=None, fig2=False):
    s = add_slide()
    kicker_head(s, f"INSIGHT {num}", title, title_size=26)
    # byline UNDER the title (report style)
    text(s, LM, 1.8, CW, 0.35, [[R(author + "  ·  ", SANS, 13, "fg", True), R(affil, SANS, 13, "muted")]])
    top = 2.4
    # ---- left column: the five fields with coloured spines ----
    fx, fw = LM, 7.4
    fh = (6.55 - top) / len(fields)          # equal vertical share
    for lab, body in fields:
        rect(s, fx, top+0.03, 0.07, fh-0.22, fill=FIELD_COLOR[lab])   # coloured spine
        text(s, fx+0.24, top, fw-0.3, 0.3, [[R(lab, MONO, 12, FIELD_COLOR[lab], True)]])
        text(s, fx+0.24, top+0.32, fw-0.3, fh-0.38, [[R(body, SANS, 13.5, "fg")]], line_spacing=1.1)
        top += fh
    # ---- right column: one figure, or TWO stacked (fig2=True) ----
    rx, rw = 8.55, 4.0
    if fig2:   # two-figure case — some papers need 2 pictures
        rect(s, rx, 2.4, rw, 1.95, fill="inset", line="line", radius=True)
        text(s, rx, 2.4, rw, 1.95, [[R("FIGURE 1 FROM PAPER", MONO, 10, "muted")]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        rect(s, rx, 4.5, rw, 1.95, fill="inset", line="line", radius=True)
        text(s, rx, 4.5, rw, 1.95, [[R("FIGURE 2 FROM PAPER", MONO, 10, "muted")]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    else:
        rect(s, rx, 2.4, rw, 3.1, fill="inset", line="line", radius=True)
        text(s, rx, 2.4, rw, 3.1, [[R("ADD KEY FIGURE", MONO, 11, "muted")],[R("FROM THE PAPER", MONO, 11, "muted")]],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space_after=0)
        text(s, rx, 5.6, rw, 0.5, [[R("[[caption from the paper]].", MONO, 10, "muted")]])
    # ---- code link (if any) above the reference, pinned to the bottom ----
    if code:
        text(s, LM, 6.5, CW, 0.28, [[R("Code · ", MONO, 10, "muted", True), R(code, MONO, 10, "work")]])
    rect(s, LM, 6.8, CW, 0.012, fill="line")
    text(s, LM, 6.88, CW, 0.4, [[R(ref, MONO, 10.5, "muted")]], line_spacing=1.05)
    return s

insight_slide(
    "01", "[[Paper title — verbatim, ≤ 14 words]]",
    "[[First Author]] et al.", "[[Affiliation]] · [[Track]]",
    [("GOAL","[[What the work sets out to achieve — ≤ 25 words.]]"),
     ("CHALLENGE","[[The problem / pain point it addresses — ≤ 35 words.]]"),
     ("METHOD","[[Mechanism 1 · Mechanism 2 · Mechanism 3 — ≤ 45 words or 3 bullets.]]"),
     ("NOVELTY","[[What is new vs prior art — the breakthrough / contribution, ≤ 30 words.]]"),
     ("IMPACT","[[Why it matters + concrete implication for our products / research — ≤ 35 words.]]")],
    "[1] First Author et al., “Paper title,” arXiv:xxxx.xxxxx, Year.",
    code="github.com/org/repo")

# Second demo slide — TWO-FIGURE example (set fig2=True for papers that need 2 pictures)
insight_slide(
    "02", "[[Second paper title]]",
    "[[First Author]] et al.", "[[Affiliation]]",
    [("GOAL","[[…]]"),("CHALLENGE","[[…]]"),("METHOD","[[…]]"),("NOVELTY","[[…]]"),("IMPACT","[[…]]")],
    "[2] First Author et al., “Paper title,” arXiv:xxxx.xxxxx, Year.",
    code="github.com/org/repo", fig2=True)

# =============================================================================
# 5) CONCLUSIONS
# =============================================================================
s = add_slide()
kicker_head(s, "CONCLUSIONS", "Synthesis across the papers")
cols = [("INSIGHTS","accent",["[[Cross-cutting insight 1]]","[[Cross-cutting insight 2]]"]),
        ("VISION","work",["[[Where the field is heading 1]]","[[Where the field is heading 2]]"]),
        ("IMPLICATIONS FOR US","brand",["[[Concrete bet 1]]","[[Concrete bet 2]]"])]
cw = (CW - 0.6)/3
for i,(h,col,items) in enumerate(cols):
    cx = LM + i*(cw+0.3)
    rect(s, cx, 2.1, cw, 4.2, fill="card", line="line", radius=True)
    text(s, cx+0.3, 2.4, cw-0.6, 0.4, [[R(h, MONO, 13, col, True)]])
    paras = [[R("•  "+it, SANS, 15, "fg")] for it in items]
    text(s, cx+0.3, 3.0, cw-0.6, 3.0, paras, line_spacing=1.2, space_after=10)

# =============================================================================
import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tech-insight-slides-template.pptx")
prs.save(out)
print("Saved:", out, "with", len(prs.slides._sldIdLst), "slides")
