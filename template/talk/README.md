# Tech Insight — Type B templates (talk / topic)

Use these when the deliverable is **one talk or topic of our own** (not a conference review).
For a conference with one card per paper, use the Type A templates one folder up.
The rules are in `../STYLE-GUIDE.md`, section 9.

| File | What it is |
|---|---|
| `tech-insight-talk-report-template.html` | the report: intro, contents, one section per part (5 coloured fields + animated figure), challenges, references |
| `tech-insight-talk-slides-template.html` | the browser deck (1920×1080, `←/→`, `T` = contents): title with part cards, contents, one content slide, challenges slide |
| `tech-insight-talk-slides-template.pptx` | the same 4 slides in PowerPoint, with **native animation** on the drawing (play in Slide Show) |
| `build_talk_pptx.py` | regenerates the `.pptx` (`py build_talk_pptx.py`) |
| `svg2pptx.py` | converts an animated SVG into native PowerPoint shapes and native animation effects |
| `sample-animation.svg` | the demo drawing: copy it, restyle it, keep the classes (`n`, `d`, `g`, `fade`) |

## Quick start

1. Copy the three templates into a folder named `<year>-<month>_<event>-<city>/` and rename them
   `<folder>-tech-insight-report.html`, `…-slides.html`, `…-slides.pptx`.
2. Replace every `[[PLACEHOLDER]]`. Duplicate the content slide / section for each part.
3. Draw each figure as an animated SVG (start from `sample-animation.svg`). In the HTML files,
   add it to `window.SVGS` under its name and reference it with `<img data-svg="name">`.
4. In `build_talk_pptx.py`, call `add_svg(slide, 'name.svg', left, top, width, height)` for each drawing.
5. Check the list in `../STYLE-GUIDE.md` §9: same parts and numbers on title, contents and kickers; digits for numbers.
