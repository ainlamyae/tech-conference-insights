# Tech Insight — Templates

Shared, standardized templates for every tech-conference insight deliverable.
Derived from the existing decks in this repo and the team's preferred visual language.

## Two template types

| | **Type A · Conference insight** | **Type B · Talk / topic** |
|---|---|---|
| For | a conference or workshop: one card per paper or talk | one talk or topic of our own: a few parts, each explained with an animated drawing |
| Folder | this folder (`template/`) | [`talk/`](talk/) |
| Example | `2025-11_NeurIPS-mexico-city/` | `2026-11_Open-day-waterloo/` |
| Slide content | Goal · Challenge · Method · Novelty · Impact card + paper figure | headline, one sentence, one animated drawing, 3 short chips |
| Visuals | figures taken from the papers | drawings we make (animated SVG; native PowerPoint animation) |
| References | IEEE, first author + et al., one per card | numbered list in the slide footer, full list in the report |
| Ends with | Conclusions: Insights · Vision · Implications | Challenges: up to 4 columns of 3 points |

Both types use the same fonts, colours, card style and 1920×1080 deck stage (see `STYLE-GUIDE.md`; Type B is §9).

## Files (Type A · Conference insight)

| File | What it is |
|------|-----------|
| **STYLE-GUIDE.md** | **Read this first.** The shared standard: per-paper schema, deck structure, fonts, sizes, palette, card/colour rules, and the text-length budget. |
| `tech-insight-report-template.html` | Long scrolling report. Open in any browser. |
| `tech-insight-slides-template.html` | Browser slide deck (1920×1080, auto-fit). `←/→` navigate, `T` = contents, `Ctrl-P` → PDF. |
| `tech-insight-slides-template.pptx` | Editable PowerPoint version. |
| `build_pptx.py` | Regenerates the `.pptx` (`py build_pptx.py`). Edit here for structural changes. |
| `assets/` | Put affiliation logos, author photos, and paper figures here. |
| `talk/` | **Type B** templates (talk / topic): report, deck, PowerPoint with native animation, `svg2pptx.py`. See `talk/README.md`. |

## Quick start

1. **Copy** the template you need out of this folder and rename it for your conference
   (e.g. `NeurIPS-2025-tech-insight-slides.html`; the PowerPoint becomes `…-slides-EN.pptx`).
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

## Languages (English | Chinese)

Each finished conference folder holds 4 files: report.html, slides.html, `…-slides-EN.pptx`, `…-slides-CN.pptx`.
The HTML files switch language with a button (names only, no flags). Build the English version with these templates, then run the
toolkit in [`../localization/`](../localization/README.md) to add the Chinese. See `STYLE-GUIDE.md` §10.
