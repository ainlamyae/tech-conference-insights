# String taxonomy and translation rules (English -> Simplified Chinese)

Every extracted string belongs to one class. The class decides what the translator does.

| Class | Examples | Rule |
|---|---|---|
| `label` | GOAL, CHALLENGE, kickers ("Insight 03 · ...", "04 · Conclusions") | translate with the glossary; keep the numbers and the middle dot |
| `ui` | Contents (T), nav items, buttons, captions "Fig. 3." | translate; keep key letters such as (T) |
| `heading` | section headings, slide titles of our own talks | translate |
| `body` | field text, ledes, bullets, chips, narration | translate; same meaning, no additions |
| `caption` | figure captions | translate; keep method/model names |
| `stat` | unit words next to numbers (submissions, accepted) | translate |
| `title` | paper and talk titles (the h2 of an insight card, items in the contents list) | **keep exactly as written** |
| `name` | author names, affiliations, methods, models, datasets, benchmarks, products | **keep exactly as written** |
| `reference` | `[n] Author et al., ...`, URLs, arXiv/DOI ids | **keep** (never sent to the translator) |
| `number` | 20,000 / 30% / 2025 | digits stay digits |

## Style
- Simplified Chinese (zh-CN). Plain, direct, professional. Short sentences. No marketing tone.
- Numbers of two and above stay **digits**. Dates: `2025 年 12 月 2–7 日`. Percentages and decimals unchanged.
- Put one space between Chinese text and Latin words or digits (`使用 GPT-4 进行 3 轮评估`).
- Chinese punctuation (，。：；（）) in Chinese sentences; keep ASCII punctuation inside English names and numbers.
- Keep the middle dot ` · ` and the dash ` — ` separators as they are.
- Inline placeholders `{1}...{/1}` and `{br}` must be kept, balanced and in the same order; do not translate inside a placeholder.
- Do not add or drop information. Keep every number, percentage, acronym and identifier of the English text.
- Keep English: paper/talk titles, author names, affiliations, model/method/dataset/benchmark/product names (RISE, SAGA, GPT-4, SWE-bench, NeurIPS), acronyms of those, arXiv/DOI/URL, code.
- Locations and months are translated (San Diego, USA -> 美国圣迭戈).
- Terms: follow `glossary.csv` (column `must` = 1 means the Chinese term has to appear when the English term appears in a translated sentence).
- Never use internal or confidential project names; use the public name from the glossary.
