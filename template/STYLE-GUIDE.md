# Tech Conference Insights — Shared Standard & Style Guide

> One house style for every Tech Insight deliverable: the **slide deck** (`.pptx` and
> `slides.html`) and the **long report** (`report.html`). Derived from a review of all
> existing decks under `D:\tech-conference-insights\` (AAAI, SysCon, NeurIPS '24/'25,
> IJCAI '25, ICLR '26) and aligned to the reference visual language the team liked
> (Geist / minimalist report + deck system).

---

## 1. Why this exists

Across the existing decks the *content* was already converging on the same idea — one
paper per slide, described by goal / problem / method / contribution / impact, an
author line, a figure, and a citation — but every author used **different labels,
fonts, colours, and amounts of text**. Some slides carried 3,000+ characters; others
carried 150. This guide fixes **one schema, one type system, one palette** so that:

- every contributor fills in the *same* fields in the *same* order;
- the deck and the report look like they came from one hand;
- overflow is handled predictably (auto-fit + continuation in HTML; a stated character
  budget + summarisation rule for PPTX).

The three template files in this folder are the canonical implementations. **Copy a
template, replace the placeholder text, done.** Do not restyle.

---

## 2. The per-paper schema (the heart of the standard)

Every paper / talk is one **Insight card**. Fill these fields, in this order. The
existing decks used many synonyms — the middle column is the **canonical label**; the
right column shows the synonyms seen in past decks that map onto it.

| # | Canonical field | Maps from (past wording)                                                        |
|---|-----------------|--------------------------------------------------------------------------------|
| — | **Title**       | the paper / talk title, verbatim                                               |
| — | **Authors · Affiliation** | "Authors:", "Speaker:", "1st author + affiliation", logo              |
| 1 | **Goal**        | "Goal", "Workshop Goal", "Objective", "Topic"                                  |
| 2 | **Challenge**   | "Problem", "Pain Point", "Background & Pain Point", "Limitations", "Why it matters" |
| 3 | **Method**      | "Approach", "Method", "Technical Highlight", "Proposed Approach"               |
| 4 | **Novelty**     | "Breakthrough", "Contribution", "Key insight", "Tech Clue", "What's new vs prior" |
| 5 | **Impact**      | "Business Inspiration", "Insights for Huawei", "Value for Industry", "Implications" |
| — | **Figure**      | one key figure/diagram from the paper — **up to two** when a paper needs it (they stack in the side column / the report card) |
| — | **Code**        | if the paper has a code repo, a `Code · github.com/org/repo` link sits **just above** the reference |
| — | **Reference**   | IEEE-style citation, pinned to the bottom — **first author + "et al." only** (never list 2nd+ authors) |

**Rules**

- Fields 1–5 are **mandatory**. Figure is strongly recommended. Reference is mandatory.
- Each field is **one tight idea**. See the length budget in §6.
- Keep the labels exactly as the canonical names (GOAL, CHALLENGE, METHOD, NOVELTY,
  IMPACT). They are colour-coded (see §5) so readers scan the same way every time.
- "Impact" is where the *organisational relevance* lives (the old "Insights for
  Huawei" / "Implications"). Keep it concrete and forward-looking.

---

## 3. Deck / report structure

Both the deck and the report follow the same running order:

1. **Conference information** — the first slide/section is about the *conference*: its
   name + year, full name, city/country, and dates. (No author / department / security
   metadata — keep the opener about the event, not the presenter.) A short "Focus" line
   names the angle the deck takes.
2. **Table of contents** — the papers covered, grouped by theme, numbered. Uses the same
   clean numbered list in the deck and the report.
3. **Conference statistics** — a stats card: # submissions, accepted, acceptance rate,
   oral talks, plus awards/headline themes. (Numbers in monospace — see §5.)
4. **Insight cards** — one per paper, using the §2 schema. This is the bulk.
5. **Conclusions** — synthesis across the papers: *Insights · Vision · Implications*.
6. **References** — full IEEE list (report only; deck pins each ref to its own slide).

> On every insight slide/card the **author line sits directly under the title** (not in a
> separate box), and a **figure from the paper** sits on the right.

---

## 4. Type system

| Role | Family | Size (report) | Size (deck, 1920×1080 base*) | Weight |
|------|--------|---------------|------------------------------|--------|
| Deck title (H1) | Geist | 30px | 68px | 620 |
| Slide / section headline (H2) | Geist | 22px | 38px | 600 |
| Kicker / eyebrow | Geist Mono | 11px UPPER | 15px UPPER | 500 |
| Field label (GOAL…) | Geist Mono | 11px UPPER | 13px UPPER | 600 |
| Body text | Geist | 14px | 15–16px | 400 |
| Numbers / stats / code | Geist Mono | 22px | 24–28px | 500, tabular-nums |
| Caption / source / reference | Geist Mono | 9–12px | 12–13px | 500 |

\* Deck sizes are the *authoring* sizes on the 1920×1080 stage. `slides.html`
auto-scales each slide's body up to **1.7×** to fill the space, so a light slide looks
large and a dense slide stays readable — you never hand-tune font sizes.

**Font stacks** (use these verbatim):

```css
--font-sans: "Geist", "Inter", ui-sans-serif, system-ui, "Segoe UI", sans-serif;
--font-mono: "Geist Mono", ui-monospace, "Cascadia Code", "Consolas", monospace;
```

- HTML templates load **Geist** + **Geist Mono** from Google Fonts (works online; falls
  back to Inter / Segoe UI / system fonts offline — the layout does not shift).
- The **PPTX** template uses **Segoe UI** (+ Consolas for numbers) because Geist is not
  installed in Office by default. If you install the Geist font, swap the theme font in
  *Slide Master → Fonts* and the whole deck follows. Keep the mono/sans split either way.
- Headlines use tight tracking (`letter-spacing:-.02em`); kickers/labels use loose
  tracking (`+.02em`) and UPPERCASE. Numbers always use tabular (monospaced) figures.

---

## 5. Colour & "boxing" (cards / coinciding coloring)

The palette is deliberately quiet — light neutral canvas, near-black ink, one deep-green
brand accent, and a small set of role colours for the field labels and stat tiles.

```
--bg      #f4f5f6   page / slide background (soft grey, not white)
--card    #fafbfb   card surface (one step lighter than bg)
--fg      #1b1d1f   primary text (near-black)
--muted   #6d7277   secondary text, captions, labels
--line    #dde1e4   hairline borders / dividers
--inset   #eceff1   inset chips, table zebra, blockquotes
--brand   #123524   deep green — title accents, bars, the brand mark
--accent  #1b7049   green — primary data series, "GOAL" label, positive
--ok      #12a66a   success / "pass" green
--warn    #8a5508   caution (text) / #e79a22 (fill)
--bad     #e7000b   failure / risk / "CHALLENGE" label
--plan    #5d34bd   purple — "METHOD" label, secondary series
--work    #2788f5   blue — "NOVELTY" label, tertiary series
```

**Field-label colour coding** (used on every Insight card so the eye learns the rhythm):

| Label      | Colour      |
|------------|-------------|
| GOAL       | `--accent` green  |
| CHALLENGE  | `--bad` red       |
| METHOD     | `--plan` purple   |
| NOVELTY    | `--work` blue     |
| IMPACT     | `--brand` deep green |

**Boxing rules**

- **Cards**: surface `--card`, `1px solid --line` ring, `border-radius:10px`, subtle
  shadow (`0 1px 2px rgba(15,23,42,.06), 0 3px 10px rgba(15,23,42,.04)`). Use for each
  Insight and for the Conference-Overview stat block.
- A **4px coloured left spine** on each field (in that field's label colour) replaces
  heavy boxing — it reads as structured without getting noisy.
- **Stat tiles**: big monospace number + small muted caption, separated by hairlines.
- **No drop shadows heavier than the card shadow, no gradients, no clip-art.** The only
  images are: affiliation logos, author photos, and figures lifted from the paper.
- Dark mode is optional and already wired in the HTML (it follows the OS setting).

---

## 6. Length budget & the "too much text" rule

The single biggest problem in the old decks was **text overflow**. The standard caps it.

**Per Insight card, target budget** (so one paper = one slide at a comfortable size):

| Field      | Target            | Hard max        |
|------------|-------------------|-----------------|
| Title      | ≤ 14 words        | 2 lines         |
| Authors    | 1st author + "et al." + affiliation | 2 lines |
| Goal       | ≤ 25 words / 1 sentence | 2 lines   |
| Challenge  | ≤ 35 words        | 3 lines         |
| Method     | ≤ 45 words (or 3 bullets) | 4 lines |
| Novelty    | ≤ 30 words        | 2 lines         |
| Impact     | ≤ 35 words        | 3 lines         |

**Total body ≈ 170 words / ~1,100 characters per card.** For reference, the old NeurIPS
'25 single-paper slides (Pain Point / Tech Clue / Breakthrough / Business Inspiration)
already sit near this budget and are the model to follow. The old 3,000-character
slides do **not** fit and must be summarised.

**What to do when content is longer than the budget:**

1. **`slides.html` handles it automatically** — if a card is too tall it auto-paginates
   onto a "(continued)" slide and auto-fits the text, so nothing is ever clipped. You
   still lose impact when a card runs long, so prefer to trim.
2. **In the report** there is no height limit — longer prose is fine there. Put the full
   detail in the report and the *summary* on the slide.
3. **In the PPTX**, there is no auto-fit. If a field exceeds its budget, **summarise**:
   - cut background/throat-clearing; lead with the finding;
   - turn prose into ≤ 3 bullets;
   - move method detail and extra results to the report;
   - a figure often replaces a paragraph — use it.

Rule of thumb: **the slide is the headline, the report is the article.** If you cannot
make a field fit its budget, that is a signal to summarise, not to shrink the font.

---

## 7. The three templates in this folder

| File | Use it for |
|------|-----------|
| `tech-insight-report-template.html` | the long, scrolling, read-at-your-desk report |
| `tech-insight-slides-template.html` | the browser deck (present full-screen, arrow keys, `T` = contents); prints to PDF at 1920×1080 |
| `tech-insight-slides-template.pptx` | the editable PowerPoint, when a native `.pptx` is required |
| `build_pptx.py` | the script that regenerates the `.pptx` (run `py build_pptx.py`) |

All three share the schema (§2), structure (§3), type system (§4) and palette (§5).
Fill in the placeholders — they are written as `[[LIKE THIS]]` — and delete the demo
Insight cards you don't need. **Do not change fonts, sizes, or colours**; that is the
whole point of having a standard.

---

## 8. Quick checklist before you ship

- [ ] Slide 1 is **conference information** (name, full name, city, dates) — no presenter
      /department/security metadata.
- [ ] Slide 2 is the **table of contents**; slide 3 is **conference statistics**.
- [ ] Each Insight has the author line **under the title** and all of
      GOAL / CHALLENGE / METHOD / NOVELTY / IMPACT.
- [ ] Each card has a **figure from the paper** (one, or two stacked when needed) and an
      IEEE reference (**first author + "et al." only**) pinned at the bottom.
- [ ] If the paper has a code repo, a **`Code · …` link sits just above the reference**.
- [ ] No field exceeds its length budget (§6); long content summarised, detail → report.
- [ ] Numbers are in monospace; labels are UPPERCASE mono in their assigned colour.
- [ ] Figures are real paper figures / logos — no stock art, no gradients.
- [ ] Conclusions slide synthesises *across* papers (Insights · Vision · Implications).
