# -*- coding: utf-8 -*-
"""Build tech-insight-talk-slides-template.pptx (Type B: talk / topic deck).
Run:  py build_talk_pptx.py        (needs python-pptx; svg2pptx.py and sample-animation.svg in this folder)
Every drawing is NATIVE shapes with NATIVE PowerPoint animation (see svg2pptx.py): in Slide Show the boxes fade in,
the arrows wipe in, the bars grow, all by themselves, at the start times written in the SVG (--d:...s).
To use your own drawing: write an SVG with the same classes (n = fade in, d = arrow wipe, g = bar grows, fade = fades out)
and call add_svg(slide, 'my-drawing.svg', left, top, box_w, box_h)."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from svg2pptx import add_svg

HERE = Path(__file__).resolve().parent
C = dict(bg='F4F5F6', card='FAFBFB', fg='1B1D1F', muted='6D7277', line='DDE1E4', brand='123524', accent='1B7049', ok='12A66A',
         warn='8A5508', bad='E7000B', plan='5D34BD', work='2788F5', white='FFFFFF')
rgb = lambda k: RGBColor.from_string(C[k])
SANS, MONO = 'Segoe UI', 'Consolas'
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb('bg')
    return s


def rect(s, l, t, w, h, fill=None, line=None, lw=0.75, radius=False):
    sp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    if radius: sp.adjustments[0] = 0.06
    if fill: sp.fill.solid(); sp.fill.fore_color.rgb = rgb(fill)
    else: sp.fill.background()
    if line: sp.line.color.rgb = rgb(line); sp.line.width = Pt(lw)
    else: sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def text(s, l, t, w, h, runs, size=12, color='fg', font=SANS, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate(runs if isinstance(runs, list) else [runs]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = para
        r.font.size = Pt(size); r.font.name = font; r.font.bold = bold; r.font.color.rgb = rgb(color)
    return tb


def header(s, kicker, title, lede=None):
    text(s, 0.5, 0.38, 10, 0.25, kicker.upper(), size=10, color='muted', font=MONO)
    text(s, 0.5, 0.66, 12.3, 0.6, title, size=28, bold=True)
    if lede: text(s, 0.5, 1.3, 12.3, 0.4, lede, size=14, color='muted')


def footer(s, refs):
    ln = s.shapes.add_connector(1, Inches(0.5), Inches(6.78), Inches(12.8), Inches(6.78)); ln.line.color.rgb = rgb('line'); ln.line.width = Pt(0.75)
    text(s, 0.5, 6.84, 12.3, 0.55, refs, size=7, color='muted', font=MONO)


# ---- 1 · title: the talk and the parts it covers (the same parts, numbered the same way, as the contents slide)
s = slide()
rect(s, 0.5, 1.45, 0.3, 0.3, fill='brand', radius=True)
text(s, 0.92, 1.45, 8, 0.3, '[[Event name · City]]', size=14, font=MONO, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.5, 1.95, 10, 0.25, '[[SHORT LABEL · MONTH YEAR]]', size=10, color='muted', font=MONO)
text(s, 0.5, 2.3, 12.3, 1.2, '[[Talk title]]', size=44, bold=True)
text(s, 0.5, 3.45, 11.2, 0.9, '[[One or two sentences: what the talk covers and why it matters.]]', size=16, color='muted')
cols = ['accent', 'ok', 'work', 'warn', 'brand', 'plan']
for i, col in enumerate(cols):
    x = 0.5 + i * 2.07
    rect(s, x, 4.55, 1.95, 1.15, fill='card', line='line', radius=True); rect(s, x, 4.55, 0.06, 1.15, fill=col)
    text(s, x + 0.18, 4.65, 1.7, 0.2, f'{i + 1:02d}', size=9, color=col, font=MONO, bold=True)
    text(s, x + 0.18, 4.88, 1.72, 0.3, f'[[Part {i + 1}]]', size=12.5, bold=True)
    text(s, x + 0.18, 5.22, 1.72, 0.4, '[[one line]]', size=9, color='muted')
for i, (lab, val) in enumerate([('Event', '[[Event]]'), ('Date', '[[Month Year]]')]):
    text(s, 0.5 + i * 4.1, 6.15, 3.8, 0.25, lab, size=10, color='muted')
    text(s, 0.5 + i * 4.1, 6.4, 3.8, 0.3, val, size=13, font=MONO)
s.notes_slide.notes_text_frame.text = '[[Speaker script for this slide. Write numbers as digits.]]'

# ---- 2 · contents
s = slide()
header(s, 'Contents', '[[6]] parts, one system', '[[One sentence that joins the parts.]]')
for i in range(6):
    y = 1.9 + i * 0.78
    rect(s, 0.5, y, 12.3, 0.66, fill='card', line='line', radius=True)
    text(s, 0.75, y + 0.2, 0.6, 0.3, f'{i + 1:02d}', size=12, color='accent', font=MONO, bold=True)
    text(s, 1.4, y + 0.17, 4.6, 0.4, f'[[Part {i + 1} name]]', size=15, bold=True)
    text(s, 6.0, y + 0.2, 5.4, 0.4, '[[one line about the part]]', size=12, color='muted')
    text(s, 11.5, y + 0.2, 1.1, 0.3, '[[n]] slides', size=11, color='muted', font=MONO, align=PP_ALIGN.RIGHT)

# ---- 3 · content slide: native animated drawing + 3 chips + references footer
s = slide()
header(s, '01 · [[Part one]]', '[[Slide title]]', '[[One sentence: the message of this slide.]]')
add_svg(s, HERE / 'sample-animation.svg', 0.5, 1.82, 12.3, 3.72)
spine = ['accent', 'plan', 'work']
for i in range(3):
    x = 0.5 + i * 4.15
    rect(s, x, 5.68, 3.95, 0.95, fill='card', line='line', radius=True); rect(s, x, 5.68, 0.06, 0.95, fill=spine[i])
    text(s, x + 0.2, 5.76, 3.6, 0.2, f'[[LABEL {i + 1}]]', size=8, color=spine[i], font=MONO, bold=True)
    text(s, x + 0.2, 5.98, 3.6, 0.6, '[[One short sentence.]]', size=11)
footer(s, '[1] [[A. Author et al., "Title," arXiv:0000.00000, Year.]]  ·  [2] [[B. Author et al., "Title," Venue, Year.]]')
s.notes_slide.notes_text_frame.text = '[[Speaker script for this slide.]]'

# ---- 4 · challenges: up to 4 columns of 3 points
s = slide()
header(s, '07 · Challenges', '[[4]] challenges ahead', '[[What has to be true for the idea to work in practice.]]')
ccol = ['accent', 'warn', 'work', 'plan']
for i in range(4):
    x = 0.5 + i * 3.1
    rect(s, x, 1.85, 2.95, 4.85, fill='card', line='line', radius=True); rect(s, x, 1.85, 2.95, 0.07, fill=ccol[i])
    text(s, x + 0.18, 2.02, 2.6, 0.25, f'{i + 1:02d}', size=10, color=ccol[i], font=MONO, bold=True)
    text(s, x + 0.18, 2.28, 2.65, 0.4, f'[[Challenge {i + 1}]]', size=16, bold=True)
    text(s, x + 0.18, 2.66, 2.65, 0.5, '[[The question it answers?]]', size=9.5, bold=True)
    for j in range(3):
        y = 3.22 + j * 1.15
        rect(s, x + 0.18, y, 0.04, 1.06, fill=ccol[i])
        text(s, x + 0.3, y, 2.55, 0.3, '[[Short lead sentence.]]', size=9, bold=True)
        text(s, x + 0.3, y + 0.3, 2.55, 0.78, '[[One or two sentences of detail.]] [1]', size=8)
footer(s, '[1] [[Full reference.]]')

out = HERE / 'tech-insight-talk-slides-template.pptx'
prs.save(str(out))
print('saved', out, len(prs.slides), 'slides')
