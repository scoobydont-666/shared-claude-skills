# Resume Scoring Rubric (weighted, 0–100)

Grade every resume against this before shipping. **Pass bar: ≥ 85.** Below that, iterate
or flag exactly what only the user can supply (a missing metric, a confidential figure).
Report: total score, the weakest dimension, and what you changed.

| # | Dimension | Weight | What full marks looks like |
|---|-----------|:---:|----------------------------|
| 1 | **Impact & quantification** | 25 | Every bullet is an outcome, not a duty; numbers (%, $, time, scale) on the majority; strongest win front-loaded per role. |
| 2 | **Relevance & tailoring** | 20 | Clearly aimed at one target; JD keywords mirrored truthfully; irrelevant content cut; title language matches. |
| 3 | **Clarity & concision** | 15 | Tight lines, one idea each, ≤2 lines/bullet; no filler verbs; parallel grammar; right length for seniority. |
| 4 | **ATS / AI parseability** | 15 | Single column, standard headers, real text, contact in body, consistent dates, requested file format. |
| 5 | **Structure & scannability** | 10 | Logical section order; 6-second scan surfaces title/level/top wins; clean visual hierarchy. |
| 6 | **Authentic voice (no AI tells)** | 10 | No banned cliché vocabulary; varied rhythm; concrete specifics; defensible in interview. |
| 7 | **Mechanics & consistency** | 5 | No typos; consistent tense/format/punctuation; dates and titles match LinkedIn. |

Total: **/100**.

## Scoring guidance per dimension
Score each dimension as a fraction of its weight:
- **Full weight** = meets the "full marks" bar with no exceptions.
- **~70%** = mostly there, a few misses.
- **~40%** = pattern problems (e.g., half the bullets are duties).
- **0–20%** = dimension largely failing (e.g., multi-column ATS-breaking layout).

## Hard fails (cap the total at 70 until fixed)
Any of these caps the resume regardless of other strengths:
- Multi-column / table-based layout that breaks ATS parsing.
- More than a couple of "Responsible for / Helped / Worked on" duty bullets.
- Zero quantification anywhere.
- No discernible target / generic catch-all aimed at no role.
- Fabricated or unverifiable claims.
- Length wildly off (e.g., 5–6 page export for a non-academic role).
- Contact info only in the header/footer.

## Output format when scoring an existing resume
```
SCORE: 78/100  (below 85 pass bar)
Weakest: Impact & quantification (14/25) — most bullets describe duties, only 2 have numbers.
Also low: Authentic voice (6/10) — "spearheaded", "leveraged", "results-driven" present.
Top 5 fixes:
  1. ...
  2. ...
Need from you: the deploy-time and cost numbers for bullets 3 and 5 (don't want to invent them).
```
Always diagnose-then-rewrite: show the score and the problems before replacing the
user's work, so they trust the changes.
