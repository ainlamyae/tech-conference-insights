# Tech Insight — Templates

Shared, standardized templates for every tech-conference insight deliverable.
Derived from the existing decks in this repo and the team's preferred visual language.

## Files

| File | What it is |
|------|-----------|
| **STYLE-GUIDE.md** | **Read this first.** The shared standard: per-paper schema, deck structure, fonts, sizes, palette, card/colour rules, and the text-length budget. |
| `tech-insight-report-template.html` | Long scrolling report. Open in any browser. |
| `tech-insight-slides-template.html` | Browser slide deck (1920×1080, auto-fit). `←/→` navigate, `T` = contents, `Ctrl-P` → PDF. |
| `tech-insight-slides-template.pptx` | Editable PowerPoint version. |
| `build_pptx.py` | Regenerates the `.pptx` (`py build_pptx.py`). Edit here for structural changes. |
| `assets/` | Put affiliation logos, author photos, and paper figures here. |

## Quick start

1. **Copy** the template you need out of this folder and rename it for your conference
   (e.g. `NeurIPS-2025-tech-insight-slides.html`).
2. **Fill in** every `[[PLACEHOLDER]]`. In the PPTX, just click the placeholder text and type.
3. **One paper = one Insight card.** Duplicate a card/slide per paper; keep all five
   fields — **Goal · Challenge · Method · Novelty · Impact** — plus authors, a figure,
   and an IEEE reference.
4. **Mind the length budget** (STYLE-GUIDE §6). If a field won't fit, *summarise* it —
   the slide is the headline, the report is the article.
5. Drop images into `assets/` and swap the placeholder `<div>`s for `<img>` (HTML) or
   Insert → Picture (PPTX).

## The one rule

Fill in the content; **don't restyle.** Fonts, sizes, and colours are the standard —
that's what makes every author's deck look like one team's work.
