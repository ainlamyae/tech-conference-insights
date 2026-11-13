# Localization toolkit (English | Chinese)

Everything needed to give a finished Tech Insight deliverable set a Chinese version, and to reuse the same work for the next conference.
Result per conference folder: 4 files.

| File | What |
|---|---|
| `<Name>-tech-insight-report.html` | report with an **English \| Chinese** button (top bar) |
| `<Name>-tech-insight-slides.html` | deck with the button bottom right, beside the slide number (key `L`) |
| `<Name>-tech-insight-slides-EN.pptx` | PowerPoint, English |
| `<Name>-tech-insight-slides-CN.pptx` | PowerPoint, Chinese (Simplified) |

The button shows language names only (no flags). The choice is remembered in the browser; `?lang=zh` in the address opens the Chinese view.

## Folders

| Folder | Content |
|---|---|
| `glossary/glossary.csv` | term dictionary (English, Chinese, translate or keep, must-use flag) |
| `glossary/taxonomy.md` | string classes and the translation rules (what stays English, digits, punctuation, placeholders) |
| `catalogs/<folder>.json` | the approved Chinese strings of each conference (`{id: {en, zh, cls}}`; the id is a hash of the English text, shared by the report, deck and pptx) |
| `tools/` | `htmlunits.py` (finds text units), `extract.py`, `batch.py`, `check.py`, `apply_html.py`, `make_cn_pptx.py` |
| `snippets/language-toggle.html` | the button, its CSS and the switching script |

Temporary work (to-do lists, translation batches, screenshots, logs) lives outside the repository, in `_archive_removed/i18n-work/`.

## Localize a new conference (5 steps)

Run on Windows (`py`, python-pptx installed) from the repository root. `<folder>` = the conference folder name, e.g. `2027-05_ICLR-vienna`.

1. **Name the files**: `…-slides.pptx` becomes `…-slides-EN.pptx` (`git mv`).
2. **Extract**: `py localization\tools\extract.py <folder>` writes `_archive_removed\i18n-work\todo\<folder>.json` (only strings without Chinese; strings already in a catalog are reused).
3. **Translate**: `py localization\tools\batch.py make` cuts the to-do files into batches (`…\batches\batch-NN.json`). Translate each batch with the glossary and taxonomy (a person or a model), answer one JSON `{id: Chinese}` per batch into `…\out\batch-NN.json`, check it with `python localization\tools\check.py batch NN`, then `py localization\tools\batch.py merge`. Verify the whole catalog: `python localization\tools\check.py catalog <folder>`.
4. **Apply to the HTML files**: `py localization\tools\apply_html.py <folder>` (safe to repeat; `--strip` removes everything it added; `--selftest` proves the English file is unchanged).
5. **Make the Chinese PowerPoint**: `py localization\tools\make_cn_pptx.py <folder>` (writes `…-slides-CN.pptx`; lists the shapes whose font was reduced to fit and the paragraphs without Chinese in `_archive_removed\i18n-work\logs\`).

Finally add the CN link next to the EN link in `README.md`, `index.html` and `sitemap.xml` (after editing `index.html`, run `py localization\tools\extract.py index`, translate the new strings, then `py localization\tools\apply_html.py index`: the overview page has the same button and its own catalog `catalogs/index.json`), then open the Chinese files once in a browser and in PowerPoint Slide Show.

**After any rebuild of a report or deck** (for example the Open Day builders in `_archive_removed/open-day/tools/`) run step 4 again, and step 5 after rebuilding the EN pptx.

## Rules (short)
- Simplified Chinese. Keep in English: paper and talk titles, author names and affiliations, model/method/dataset/benchmark/product names, arXiv/DOI/URLs, references.
- Numbers of two and above are written as digits in both languages.
- No flags or icons for languages; the buttons say `English` and `Chinese`.
- Pictures with English text inside (paper figures) and the live run replay of the Open Day deck stay English.
- Never put internal or confidential project names in any file, catalog or glossary.
