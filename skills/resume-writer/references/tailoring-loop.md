# Tailoring Loop — one resume per job

A generic resume is a resume for no one. The single highest-ROI move is tailoring to the
specific job description (JD). This is a tight loop: extract → map → mirror → measure.

## Step 1 — Extract the JD's keywords
From the posting, pull and bucket:
- **Hard requirements**: must-have skills, tools, years, certifications, degrees.
- **Title language**: the exact role name and any level signal (Senior/Staff/Lead).
- **Repeated themes**: anything mentioned 2+ times is what they actually care about.
- **Methodologies / ways of working**: Agile, GitOps, SRE, TDD, etc.
- **Domain terms**: industry/product vocabulary.

Separate **required** from **preferred/nice-to-have** — prioritize required.

## Step 2 — Map each keyword to truth
For every extracted keyword, find where in the candidate's real history it lives:
- A bullet that demonstrates it (strongest), and/or
- The Skills section (coverage), and/or
- **Gap** — they don't have it.

Build a quick coverage table:

| JD keyword | Required? | Where it's true in the resume | Action |
|---|:---:|---|---|
| Kubernetes | yes | Exp #1 bullet 2 | mirror exact term |
| Terraform | yes | Skills + Exp #2 | add a quantified bullet |
| Go | preferred | — (gap) | ask user; don't fabricate |

## Step 3 — Mirror exactly (where true)
- Use the JD's **exact term**, plus acronym+expansion once: "Kubernetes (K8s)",
  "Site Reliability Engineering (SRE)".
- Surface the most important matches **in bullets**, not just the Skills list — a keyword
  backed by a result is a far stronger signal than a bare list entry.
- Adjust the **summary's specialization clause** and the **target-title line** to match
  the role.
- Reorder Skills groups so the role's must-haves come first.

## Step 4 — Measure coverage and report honestly
Give the user a coverage read:
> "You cover 11/13 required keywords. Missing: **Go** and **Kafka**. Do you have real
> exposure to either? If not, we leave them out — keyword-stuffing skills you can't
> defend backfires in the screen and the interview."

**Never fabricate coverage.** If there's a genuine gap, surface it and let the user
decide (real adjacent experience to reframe, a learning-in-progress note, or omit).

## What tailoring does NOT mean
- It does **not** mean lying or inventing experience.
- It does **not** mean stuffing every keyword regardless of truth.
- It **does** mean: choosing which true things to emphasize, in the target's language,
  in the right order, and cutting what's irrelevant to *this* role.

## Efficiency tip
Maintain a **master resume** (everything, long) per `templates.md`. Each application is a
fast tailoring pass: copy master → cut to the target → mirror JD keywords → score → ship.
This is far faster and far stronger than maintaining one generic resume.
