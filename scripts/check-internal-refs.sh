#!/usr/bin/env bash
# Check for internal infrastructure references in skills documentation
# This script prevents reintroduction of leaked topology during development
# Exit code: 0 if clean, 1 if violations found

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DENY_PATTERNS="${REPO_ROOT}/scripts/deny-patterns.txt"
SKILLS_DIR="${REPO_ROOT}/skills"

if [[ ! -f "$DENY_PATTERNS" ]]; then
    echo "ERROR: deny-patterns.txt not found at ${DENY_PATTERNS}"
    exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "ERROR: skills directory not found at ${SKILLS_DIR}"
    exit 1
fi

# Extract non-comment, non-empty lines from deny patterns
patterns=$(grep -v '^\s*#' "$DENY_PATTERNS" | grep -v '^\s*$' | sort -u)

violations=0
temp_grep_output=$(mktemp)
trap 'rm -f "$temp_grep_output"' EXIT

echo "Checking skills for internal infrastructure references..."
echo "Deny patterns source: ${DENY_PATTERNS}"
echo ""

# Check each pattern
while IFS= read -r pattern; do
    if [[ -z "$pattern" ]]; then
        continue
    fi

    # Use grep with extended regex to find violations
    # -r: recursive, -n: line numbers, -l: file names only (in summary)
    if grep -rE "$pattern" "$SKILLS_DIR" > "$temp_grep_output" 2>/dev/null; then
        violation_count=$(wc -l < "$temp_grep_output")
        if [[ $violation_count -gt 0 ]]; then
            echo "VIOLATION: Pattern '${pattern}' found in ${violation_count} lines:"
            head -5 "$temp_grep_output" | sed 's/^/  /'
            if [[ $violation_count -gt 5 ]]; then
                echo "  ... and $((violation_count - 5)) more lines"
            fi
            violations=$((violations + violation_count))
        fi
    fi
done <<< "$patterns"

echo ""
if [[ $violations -eq 0 ]]; then
    echo "✓ PASS: No internal infrastructure references found."
    exit 0
else
    echo "✗ FAIL: Found ${violations} internal reference violations."
    echo ""
    echo "Remediation:"
    echo "  - Replace fleet hostnames with placeholders: <gpu-host>, <cpu-host>, <orchestrator-host>"
    echo "  - Replace project codenames with: <your-project>, <internal-project>"
    echo "  - Replace service ports with: <service-port>, <local-port>"
    echo "  - Replace internal subnets with: <internal-subnet>, <gateway-ip>"
    echo "  - Replace internal paths with: <repo-path>, <config-dir>, <project-root>"
    echo "  - Remove generic 'budi' references outside budi-analytics skill"
    echo "  - Rename claude-swarm to hydra-swarm where appropriate"
    exit 1
fi
