# Known Supply Chain Compromises — Evaluated 2026-03-21

Reference data for supply-chain-risk-auditor skill. Updated when new incidents are discovered.

## Active Compromises (DO NOT INSTALL)

### aquasecurity/trivy — COMPROMISED
- **Date:** 2026-02-28 (first), 2026-03-19 (second)
- **What:** AI agent "hackerbot-claw" exploited `pull_request_target` GitHub Actions, stole secrets. Second compromise by "TeamPCP" using stolen PAT. Malicious v0.69.4 published. 75/76 release tags force-pushed in trivy-action.
- **Impact:** Malicious binaries phoned home to C2 domain
- **Safe version:** v0.69.3 (2026-03-03) — but trust is broken
- **Alternative:** [anchore/grype](https://github.com/anchore/grype)
- **Re-evaluate:** April 2026 at earliest

### BerriAI/litellm — CHRONIC VULNERABILITY
- **CVE count:** 15+ (3 Critical, multiple High)
- **Critical:** CVE-2024-4264, CVE-2024-5751 (RCE via unsafe `eval()`), CVE-2024-2952 (SSTI)
- **High:** RCE via callbacks, SSRF leaking API keys, SQL injection, API key leakage in logs
- **No SECURITY.md** in repo
- **Status:** New CVEs continue to appear regularly
- **Alternative:** Direct provider SDKs, or self-built proxy with strict input validation

## Patched But Watch-Listed

### openclaw/openclaw — HIGH ADVISORY VOLUME
- **CVE-2026-25253** (CVSS 8.8): WebSocket auth token theft. Patched >= 2026.1.29
- **29 pages of GitHub Security Advisories**
- **Ongoing:** New advisories monthly across 30+ messaging integrations
- **Our posture:** Deployed with NemoClaw sandbox, all channels disabled, Tailscale-only access

## Evaluation Criteria

When assessing a new dependency, check:
1. **GitHub Security Advisories:** `gh api repos/OWNER/REPO/security-advisories --jq '.[].summary'`
2. **CVE databases:** Search NVD for the package name
3. **Maintainer count:** Single-maintainer projects are higher risk
4. **Commit frequency:** Stale repos (>6 months no commits) are unmaintained
5. **Security policy:** Does the repo have SECURITY.md?
6. **Disclosure process:** Responsible disclosure or public issues?
7. **Dependency tree:** Heavy dependency trees amplify supply chain risk
