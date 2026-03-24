# Bash/Shell Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Script Structure & Packaging](#3-script-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: Google Shell Style Guide + ShellCheck
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Variables (local) | `snake_case` | `retry_count`, `file_path` |
| Variables (exported/env) | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `LOG_LEVEL` |
| Functions | `snake_case` | `parse_config()`, `validate_input()` |
| Constants | `UPPER_SNAKE_CASE` + `readonly` | `readonly MAX_RETRIES=5` |
| Script filenames | `kebab-case` or `snake_case`, no extension or `.sh` | `deploy-app`, `run_tests.sh` |
| Temp files | Prefixed with script name | `${SCRIPT_NAME}.tmp.$$` |

**Critical rules:**
- 🔴 Always quote variable expansions: `"${var}"` not `$var`
- 🔴 Use `local` for function variables to prevent scope leakage
- 🔴 Never use single-letter variable names outside loops
- 🟡 Prefix internal/private functions with `_` (e.g., `_validate_arg`)
- 🟡 Use `declare -r` or `readonly` for constants
- 🟡 Avoid `ALLCAPS` for non-exported local vars (conflicts with env convention)

**Style detection hints:**
- If you see `camelCase` functions → non-standard but match it
- If you see `function foo { }` vs `foo() { }` → match the form in use

---

## 2. Error Handling

### Strict mode (always enable at script top)
```bash
#!/usr/bin/env bash
set -euo pipefail
```

| Flag | Effect |
|---|---|
| `-e` | Exit on any command failure |
| `-u` | Error on unset variables |
| `-o pipefail` | Pipe fails if any command in pipeline fails |

**Critical rules:**
- 🔴 Always `set -euo pipefail` unless there's a documented reason not to
- 🔴 Use `trap` for cleanup on EXIT, ERR, INT, TERM
- 🔴 Check return codes explicitly for commands where failure is expected
- 🔴 Never use `set +e` to suppress errors globally — scope it

### Trap patterns
```bash
cleanup() {
    local exit_code=$?
    rm -f "${TMPFILE:-}"
    exit "$exit_code"
}
trap cleanup EXIT

# ERR trap for debugging (optional but useful)
on_error() {
    echo "ERROR: ${BASH_SOURCE[1]}:${BASH_LINENO[0]} — command '${BASH_COMMAND}' failed" >&2
}
trap on_error ERR
```

### Conditional execution
```bash
# GOOD: explicit error handling
if ! result=$(some_command 2>&1); then
    log_error "some_command failed: ${result}"
    return 1
fi

# BAD: swallowing errors
some_command || true  # Only OK with comment explaining why
```

### Exit codes
- 🔴 Use meaningful exit codes: 0=success, 1=general error, 2=usage error
- 🟡 For complex scripts, define named codes: `readonly E_BADARG=2`

---

## 3. Script Structure & Packaging

### Standard script layout
```bash
#!/usr/bin/env bash
# script-name — one-line description
# Usage: script-name [options] <required-arg>

set -euo pipefail

# --- Constants ---
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

# --- Globals ---
VERBOSE=0
DRY_RUN=0

# --- Functions ---
usage() { ... }
log_info() { ... }
log_error() { ... }
main() { ... }

# --- Entrypoint ---
main "$@"
```

### Multi-file projects
```
my-tool/
├── bin/
│   └── my-tool           # entrypoint, sources lib/
├── lib/
│   ├── common.sh         # shared functions
│   ├── config.sh         # config parsing
│   └── deploy.sh         # domain logic
├── tests/
│   └── test_common.sh    # bats or shunit2
├── Makefile              # install/test targets
└── README.md
```

**Critical rules:**
- 🔴 Always use `#!/usr/bin/env bash` not `#!/bin/bash` (portability)
- 🔴 Source libraries with full paths: `source "${SCRIPT_DIR}/lib/common.sh"`
- 🔴 `main "$@"` at bottom — never run logic at top level
- 🟡 Parse args with `getopts` or manual `while/case` — not positional assumptions
- 🟡 Use `mktemp` for temp files, never hardcoded paths

---

## 4. Logging & Observability

### Logging functions
```bash
readonly LOG_LEVEL="${LOG_LEVEL:-INFO}"

log_debug() { [[ "${LOG_LEVEL}" == "DEBUG" ]] && echo "[DEBUG] $(date -Iseconds) $*" >&2; }
log_info()  { echo "[INFO]  $(date -Iseconds) $*" >&2; }
log_warn()  { echo "[WARN]  $(date -Iseconds) $*" >&2; }
log_error() { echo "[ERROR] $(date -Iseconds) $*" >&2; }
```

**Critical rules:**
- 🔴 All log output to stderr (`>&2`), never stdout (stdout is for data/piping)
- 🔴 Include timestamps in any long-running script
- 🟡 Use `[LEVEL]` prefix for grepability
- 🟡 Support `VERBOSE` / `DEBUG` env var for debug output
- 🟡 For systemd services: skip timestamps (journald adds them), use structured fields

### Debugging
- `set -x` scoped to functions, never globally in production
- `PS4='+ ${BASH_SOURCE}:${LINENO}: '` for better trace output
- `bash -n script.sh` for syntax checking without execution
