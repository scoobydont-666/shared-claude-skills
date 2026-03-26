# ProjectA AI Financial Wizard — Tax Module Integration Guide

This reference defines how the CPA TCP skill maps to the ProjectA AI Financial Wizard development pipeline. Use when building tax agent prompts, RAG knowledge chunks, test scenarios, or validating ProjectA's tax outputs.

---

## Table of Contents

1. Architecture Context
2. Tax Knowledge Unit Design
3. RAG Chunking Strategy for Tax Content
4. Test Scenario Templates
5. Quality Validation Framework
6. Dual-Audience Content Strategy

---

## 1. Architecture Context

ProjectA AI Financial Wizard runs on Josh's GPU cluster as a multi-agent LangGraph pipeline with ChromaDB for RAG retrieval. The tax module is one of several financial service verticals.

### Where Tax Fits in the Pipeline
- **Intake Agent**: Classifies query → routes to tax agent if tax-related
- **Tax Agent**: Receives query + retrieved context from ChromaDB → generates response
- **Validation Agent**: Reviews tax agent output for accuracy, completeness, required disclaimers
- **Response Agent**: Formats final output for the target audience (professional CPA vs. consumer)

### Tax Agent Requirements
- Must distinguish federal vs. California treatment on every substantive question
- Must cite IRC/RTC sections when making technical claims
- Must identify when information may be stale and flag for verification
- Must include appropriate disclaimers (mirrors the veteran disclaimer from the CPA skill)
- Must calibrate response depth to the detected audience (professional vs. consumer)

---

## 2. Tax Knowledge Unit Design

Structure tax rules as discrete, retrievable knowledge units for ChromaDB ingestion. Each unit should be self-contained enough to be useful when retrieved independently, but include cross-references to related units.

### Knowledge Unit Template

```json
{
  "unit_id": "TCP-I-199A-001",
  "title": "§199A Qualified Business Income Deduction — Overview",
  "category": "individual_tax",
  "subcategory": "deductions",
  "tcp_area": "I",
  "applicable_entities": ["individual", "trust", "estate"],
  "applicable_tax_years": ["2018-2025"],
  "sunset_risk": true,
  "federal_rule": "20% deduction on qualified business income from pass-through entities and sole proprietorships. Subject to W-2 wage and UBIA limitations above taxable income thresholds. SSTB limitations apply.",
  "california_treatment": "DOES NOT CONFORM. California taxes 100% of pass-through income with no QBI deduction. RTC has no equivalent provision.",
  "conformity_status": "decoupled",
  "key_irc_sections": ["199A"],
  "key_rtc_sections": [],
  "related_units": ["TCP-I-199A-002", "TCP-I-199A-003", "TCP-II-SCORP-BASIS-001"],
  "planning_notes": "Major federal-CA divergence. S-corp owners in CA face full state tax on income that receives 20% federal deduction. Quantify the CA impact in every entity selection analysis.",
  "risk_level": "moderate",
  "last_verified": "2026-03-01",
  "verification_sources": ["IRC §199A", "Reg §1.199A-1 through -6", "FTB Pub 1001"]
}
```

### Naming Convention
- `TCP-{area}-{topic}-{sequence}`: e.g., `TCP-I-199A-001`, `TCP-II-SCORP-BASIS-003`
- Areas: I (Individual), II (Entity), III (Property), IV (Compliance), CA (California-specific)
- Use descriptive topic slugs: `CAPGAINS`, `PASSIVE`, `1031`, `PTE-ELECTION`, `RESIDENCY`

### Required Metadata Fields
Every knowledge unit MUST include:
- `federal_rule`: The federal tax treatment
- `california_treatment`: How California treats it (conform / decouple / modified conformity)
- `conformity_status`: One of `conforms`, `decoupled`, `partial`, `modified`
- `applicable_tax_years`: When this rule applies (critical for sunset provisions)
- `sunset_risk`: Boolean — is this provision scheduled to expire?
- `last_verified`: Date of last verification against primary sources
- `verification_sources`: What to check for updates

---

## 3. RAG Chunking Strategy for Tax Content

### Chunking Principles for Tax

Tax content has specific chunking challenges:
- Rules have complex dependencies (basis calculations reference multiple IRC sections)
- Federal and California treatments must be co-located for effective retrieval
- Tax years matter — a rule from 2023 may not apply to a 2025 question
- Numerical thresholds change annually with inflation adjustments

### Recommended Chunk Sizes
- **Atomic rule chunks**: 200–400 tokens each. One IRC section, one concept.
- **Contextual wrapper chunks**: 400–800 tokens. Combines the federal rule + CA treatment + key planning note for a single topic.
- **Scenario chunks**: 600–1000 tokens. Complete analysis of a common tax scenario.

### Chunk Design Rules
1. **Always pair federal + California**: Never create a federal-only chunk without a corresponding CA treatment note. The retrieval system must return both together.
2. **Include tax year in the chunk text**: Don't rely on metadata alone. Write "For tax years 2018–2025, §199A provides…" so the LLM sees the temporal scope.
3. **Embed threshold amounts with date stamps**: "The §199A taxable income threshold is $191,950 (single) / $383,900 (MFJ) for 2024. These amounts are inflation-adjusted annually."
4. **Cross-reference related chunks by ID**: Include `related_units` so the retrieval system can pull related context.
5. **Separate computation rules from planning guidance**: Keep the mechanical "how to calculate" separate from the strategic "when to use this."

### Embedding Model Considerations
- Tax content is highly technical with domain-specific vocabulary
- IRC section numbers (§199A, §1031, §469) should be treated as important retrieval tokens
- Consider fine-tuning the embedding model on tax corpora if retrieval quality is insufficient with general-purpose embeddings
- Test retrieval with actual tax questions to validate chunk boundaries

---

## 4. Test Scenario Templates

Generate realistic tax scenarios for the multi-agent LangGraph pipeline test suite. Each scenario should test a specific combination of federal + California rules.

### Scenario Categories

**Category A: Straightforward Compliance**
Single-issue questions with clear answers. Tests basic retrieval and accuracy.
```
Scenario: "A single California resident earned $85,000 in W-2 wages in 2025. They contributed $7,000 to a traditional IRA. Their employer does not offer a retirement plan. What is the federal deduction? What is the California treatment?"
Expected: Full IRA deduction federally (no active participant, under AGI limit). California conforms — same deduction on CA return.
Tests: Individual tax, deductions, CA conformity on retirement contributions.
```

**Category B: Federal-California Divergence**
Questions where federal and California treatments differ. Tests the system's ability to distinguish and present both.
```
Scenario: "A California S-corp owner has $300,000 of QBI from her consulting business (SSTB). Her taxable income is $150,000 (single). What is her federal §199A deduction? What happens on her California return?"
Expected: Federal — full $60,000 QBI deduction (under SSTB threshold, so SSTB limitation doesn't apply). California — no deduction, full $300,000 taxed at CA rates.
Tests: §199A, SSTB rules, CA decoupling, entity taxation.
```

**Category C: Multi-Issue Planning**
Complex scenarios requiring analysis across multiple tax areas. Tests the system's ability to synthesize.
```
Scenario: "A tech founder in Fremont is exercising 50,000 ISOs with a $5 exercise price when the FMV is $25/share. He plans to hold for qualifying disposition treatment. He also has $200,000 in W-2 income. Analyze the federal and California AMT implications."
Expected: Federal — $1M bargain element is an AMT preference. Calculate tentative minimum tax, compare to regular tax. California — same preference applies for CA AMT at 7% rate. Even if federal AMT credit offsets federal impact in future years, the CA AMT credit is separate and limited. Flag the CA AMT trap.
Tests: Tech equity, AMT, ISO rules, CA AMT, multi-year planning.
```

**Category D: Residency & Multi-State**
Departure/arrival scenarios that test California sourcing rules.
```
Scenario: "A software engineer moved from San Jose to Austin, TX on July 1, 2025. She earned $250,000 in total W-2 wages ($125,000 earned while in CA, $125,000 earned while in TX). She also has $50,000 in RSU vesting in October 2025 — the grant was made 3 years ago while she was a CA resident. What does she owe California?"
Expected: Part-year resident. W-2 wages sourced by duty days: $125,000 taxable to CA. RSU vesting: CA allocates based on service period in CA (grant-to-vest). If 2 of 3 years were CA service, ~$33,333 of the RSU income is CA-source even though she was in TX at vesting. Flag FTB aggressive position.
Tests: Residency, part-year, RSU sourcing, duty days allocation.
```

**Category E: Entity Selection & Planning**
Strategic planning scenarios that test the system's ability to recommend and model.
```
Scenario: "A freelance marketing consultant in Oakland earns $400,000/year. She currently operates as a sole proprietor. She's considering forming an S-corp. Model the tax impact for federal + California, including self-employment tax savings, §199A implications, reasonable salary requirements, and the PTE tax election."
Expected: Comprehensive analysis comparing sole prop vs. S-corp. SE tax savings from reduced salary. §199A SSTB analysis (consulting is SSTB, but she's under the threshold). California PTE election benefit modeling (9.3% PTE tax deductible at federal level vs. SALT cap). Must address reasonable compensation doctrine.
Tests: Entity selection, SE tax, §199A, SSTB, PTE election, multi-factor planning.
```

### Test Suite Coverage Matrix

Ensure the test suite covers every combination:

| Dimension | Values to Test |
|---|---|
| Tax area | Individual, Entity, Property, Compliance |
| Entity type | Individual, S-corp, Partnership, C-corp, Trust |
| CA conformity | Conforms, Decoupled, Modified |
| Residency | CA resident, Nonresident, Part-year |
| Complexity | Single-issue, Multi-issue, Planning |
| Audience | Professional CPA, Educated consumer |
| Tax year | Current, Prior, Multi-year |

Target: minimum 65 test scenarios covering the full matrix (aligns with existing 65/65 test suite target).

---

## 5. Quality Validation Framework

When reviewing ProjectA AI tax outputs, apply these validation criteria — the same standards a competent 50-year California CPA would use.

### Accuracy Checklist
- [ ] Federal rule stated correctly with proper IRC citation
- [ ] California treatment explicitly stated (conform/decouple/modify)
- [ ] RTC citation included for California-specific rules
- [ ] Numerical thresholds correct for the stated tax year
- [ ] Inflation-adjusted amounts current (or flagged for verification)
- [ ] Entity type correctly identified and rules applied accordingly
- [ ] Residency status properly determined and sourcing rules applied

### Completeness Checklist
- [ ] Both federal AND California treatment addressed
- [ ] Related issues flagged (e.g., §199A analysis mentions SSTB status)
- [ ] Planning opportunities identified
- [ ] Risks and aggressive positions labeled
- [ ] Sunset provisions flagged (e.g., TCJA expiration)
- [ ] Disclaimer included

### Tone & Audience Calibration
- [ ] Professional audience: uses IRC/RTC citations, assumes technical knowledge, includes computation details
- [ ] Consumer audience: explains concepts in plain language, avoids unexplained jargon, includes "what this means for you" translation
- [ ] Both: maintains the calm authority of an experienced practitioner

### Red Flags (Automatic Failure)
- Stating California conforms when it decouples (or vice versa)
- Applying wrong tax year thresholds without noting the discrepancy
- Missing AMT implications on ISO exercises
- Ignoring California's taxation of capital gains as ordinary income
- Failing to mention PTE election when discussing SALT cap impact on pass-through owners
- Providing a guarantee or certainty about a tax outcome
- Missing the veteran disclaimer on substantive tax advice

---

## 6. Dual-Audience Content Strategy

ProjectA AI serves two audiences: professional CPAs using it as a research/productivity tool, and educated consumers seeking tax guidance. The knowledge base must support both.

### Professional Mode
- Lead with IRC/RTC citations
- Include computation mechanics and formulas
- Reference regulations, rulings, and case law
- Assume familiarity with tax terminology
- Focus on planning strategies and risk calibration
- Provide conservative / moderate / aggressive options

### Consumer Mode
- Lead with the practical impact ("what this means for your taxes")
- Explain technical terms on first use
- Use concrete dollar examples
- Highlight action items and deadlines
- Simplify without being inaccurate — never sacrifice correctness for accessibility
- Emphasize when to seek professional help

### Content Tagging for Audience Routing
Each knowledge unit should include audience-appropriate variants:
```json
{
  "professional_summary": "§199A provides a 20% QBI deduction subject to W-2 wage and UBIA limitations above the applicable threshold. California decouples — no state-level QBI deduction available.",
  "consumer_summary": "If you own a business through an S-corp or partnership, you may be able to deduct 20% of your business income on your federal taxes. However, California doesn't offer this deduction — you'll pay full state tax on all your business income."
}
```

Both summaries must be technically accurate. The consumer version simplifies language, not substance.
