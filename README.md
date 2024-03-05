# Tech-Conference Insight Reports

Concise **insight reports** for recent AI and systems-engineering conferences. Each conference is distilled into a standard set of four deliverables, generated from a shared visual template:

- **`…-tech-insight-report.html`** — a long, scrolling read-at-your-desk report.
- **`…-tech-insight-slides.html`** — a browser slide deck (1920×1080; `←/→` to navigate, `T` for contents, `Ctrl-P` → PDF).
- **`…-tech-insight-slides-EN.pptx`** — an editable PowerPoint version in English.
- **`…-tech-insight-slides-CN.pptx`** — the same deck in Chinese (Simplified).

All four are **self-contained** — images are embedded — so they open on their own with no extra files. The two HTML files have an **English | Chinese** button (in the report: top bar; in the slides: bottom right, beside the slide number, key `L`).

**Start at [`index.html`](index.html)** for a linked overview of every conference. The index is versioned — each conference added to the repo bumps the version shown in its footer.

## Conferences

| Conference | When & where | Covered | Files |
|---|---|---|---|
| **AAAI 2024** | Vancouver, Canada · February 20–27, 2024 | 13 papers | [report](2024-02_AAAI-vancouver/AAAI-2024-tech-insight-report.html) · [slides](2024-02_AAAI-vancouver/AAAI-2024-tech-insight-slides.html) · [pptx EN](2024-02_AAAI-vancouver/AAAI-2024-tech-insight-slides-EN.pptx) · [pptx CN](2024-02_AAAI-vancouver/AAAI-2024-tech-insight-slides-CN.pptx) |

## Layout

```
<year-month>_<conference>/
  <Name>-<year>-tech-insight-report.html     # scrolling report
  <Name>-<year>-tech-insight-slides.html     # browser deck
  <Name>-<year>-tech-insight-slides-EN.pptx  # PowerPoint, English
  <Name>-<year>-tech-insight-slides-CN.pptx  # PowerPoint, Chinese
index.html     # linked, versioned overview of all conferences
template/      # shared house style (STYLE-GUIDE.md + HTML/PPTX templates)
```

## License

Released under the [MIT License](LICENSE). © 2024 ainlamyae.
