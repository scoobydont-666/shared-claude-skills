# ATS & AI-Parser Optimization

Most resumes are read by software before a human sees them: an **ATS** (Applicant
Tracking System — Workday, Greenhouse, Lever, Taleo, iCIMS) that parses fields and
keyword-matches, and increasingly an **LLM screener** that summarizes and ranks the
candidate against the role. Both reward clean structure and exact-keyword truth; both
are defeated by visual gimmicks that break parsing.

## How parsing actually fails
ATS/LLM parsers read the document's text stream top-to-bottom. They break on:
- **Multi-column layouts** — text gets interleaved across columns into nonsense.
- **Tables** for content — cells get read out of order or dropped.
- **Text boxes / shapes / SmartArt** — often invisible to the parser.
- **Headers/footers** holding real info (name, phone, email) — frequently ignored.
- **Images / icons / logos / photos** — unreadable; skills-as-graphics = invisible skills.
- **Non-standard section names** — "Where I've Made Impact" won't map to "Experience".
- **Fancy fonts / ligatures / bullet glyphs** — can garble or drop characters.
- **Dates in odd formats** — keep `MMM YYYY – MMM YYYY` (e.g., "Aug 2021 – Present").

## Format rules (do these)
- **Single column.** One linear top-to-bottom flow.
- **Standard section headers**, spelled the boring way: `Summary`, `Experience` (or
  `Professional Experience`), `Skills`, `Education`, `Certifications`, `Projects`.
- **Real text, not images**, for everything that must be read — especially skills.
- **Standard fonts**: Calibri, Arial, Helvetica, Georgia, Garamond, Lato, 10–12pt body.
- **Real bullet characters** (`•`, `-`), left-aligned, no nested decorative glyphs.
- **Contact info in the body**, top of page one — never only in the header/footer.
- **No tables/columns** for skills or experience. A simple skills list wrapped across
  lines parses fine; a 3-column skills grid does not.
- **Consistent date placement** (right-aligned or after the title), same format throughout.

## File format: what to submit
- **.docx is the most universally ATS-safe** binary format (python-docx via the
  `ms-office-suite` skill produces clean output).
- **PDF** is fine for most modern ATS *and* preserves layout for humans — but only if
  it's text-based (selectable text), not a scanned/flattened image, and only when the
  posting accepts PDF. Some older Taleo/iCIMS instances still mangle PDFs.
- **Rule: submit the format the posting asks for.** If it says "upload .docx", do that.
  If unspecified, .docx is the safe default; offer a matching PDF for emailing to humans.
- **Filename**: `First-Last-Resume.pdf` (or `-Role.docx` when tailored). Never
  `resume_final_v7(2).pdf`.

## Keyword strategy (the part that gets you matched)
1. **Pull keywords from the JD**, not your imagination: required skills, tools,
   methodologies, certifications, and the title language itself.
2. **Mirror exact terms.** If the JD says "Kubernetes", don't write only "K8s" — write
   "Kubernetes (K8s)". Include both the **acronym and the spelled-out form** once each:
   "Site Reliability Engineering (SRE)", "Infrastructure as Code (IaC)".
3. **Place keywords where they're true** — inside accomplishment bullets (strongest
   signal) *and* in a grouped Skills section (coverage). A skill that only appears in the
   Skills list with no supporting bullet reads as thin.
4. **Match the title vocabulary.** If they hire a "Platform Engineer" and you were a
   "DevOps Engineer" doing platform work, you may add a parenthetical or a target title
   in the summary — honestly.
5. **Never keyword-stuff.** Hidden white text, keyword walls, or skills you can't defend
   in an interview will sink you with both the LLM screener and the human. Truth only.

## Writing for the LLM screener specifically
LLM screeners summarize your resume and answer "does this person fit?". Help them:
- **Put the answer up top.** A crisp summary + a quantified first bullet per role gives
  the model the strongest signal in the smallest space.
- **Be explicit, not clever.** State the years, the scale, the stack plainly. The model
  can't infer "obviously senior" from vibes.
- **Co-locate context.** Keep the tech stack and the outcome in the same bullet so the
  model attributes the skill to a real result.
- **No contradictions.** Inconsistent dates/titles between resume and LinkedIn lower
  confidence — keep them in sync.

## Quick ATS self-check
- [ ] Single column, no tables/text-boxes/images for real content?
- [ ] Standard section headers?
- [ ] Contact info in the body (not only header/footer)?
- [ ] Dates consistent `MMM YYYY` format?
- [ ] JD keywords mirrored exactly, acronym + expansion, only where true?
- [ ] Selectable text (not a scanned image), submitted in the requested format?
- [ ] Resume ↔ LinkedIn titles/dates consistent?
