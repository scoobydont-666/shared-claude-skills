# Security Analysis Reference

## Table of Contents
1. [Injection Prevention](#1-injection-prevention)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [Secrets Management](#3-secrets-management)
4. [Input Validation](#4-input-validation)
5. [Supply Chain & Dependencies](#5-supply-chain--dependencies)

---

## 1. Injection Prevention

### Attack vectors to check
| Vector | Language/Context | What to look for |
|---|---|---|
| SQL injection | All w/ SQL | String formatting in queries, missing parameterization |
| Command injection | Bash, Python, Go | `os.system()`, `exec.Command()` with user input, unquoted vars |
| Path traversal | All w/ filesystem | User input in file paths without sanitization |
| Template injection | Python (Jinja2), Go (html/template) | User input rendered as template |
| LDAP injection | All w/ LDAP | Unescaped special chars in LDAP queries |
| Log injection | All | Unsanitized user input in log messages (newline injection) |

### Critical rules
- 🔴 **SQL:** Always use parameterized queries. Never `f"SELECT ... WHERE id = {user_input}"`
- 🔴 **Commands:** Never pass user input to shell. Use exec with argument arrays.
- 🔴 **Paths:** Resolve and validate against an allowed base directory: `os.path.realpath()`, `filepath.Clean()`
- 🔴 **Templates:** Use auto-escaping. Never `|safe` / `template.HTML()` with user input.
- 🟡 **Logs:** Strip or encode newlines/control chars from user input before logging

### Language-specific
- **Python:** `subprocess.run(["cmd", arg], shell=False)` not `os.system(f"cmd {arg}")`
- **Go:** `exec.Command("cmd", arg)` not `exec.Command("bash", "-c", "cmd " + arg)`
- **Bash:** Quote all variables. Use `--` to terminate option parsing.
- **Rust:** `Command::new("cmd").arg(input)` — arg() prevents injection by design
- **Terraform:** `external` data source with user-influenced commands is injection-prone

---

## 2. Authentication & Authorization

### Checklist
- [ ] Authentication happens before authorization (verify identity before checking perms)
- [ ] Auth checks happen server-side, not client-only
- [ ] Session tokens have appropriate expiration and rotation
- [ ] Password storage uses bcrypt/argon2/scrypt — never SHA/MD5
- [ ] API keys are scoped to minimum necessary permissions
- [ ] JWT validation checks: signature, expiration, issuer, audience
- [ ] Rate limiting on auth endpoints (login, token refresh)
- [ ] Account lockout or exponential backoff after failed attempts

### Critical rules
- 🔴 Auth bypass: any code path that reaches protected resources without auth check
- 🔴 Broken access control: user A can access user B's resources (IDOR)
- 🔴 Hardcoded admin credentials or backdoor accounts
- 🔴 JWT with `alg: none` accepted, or secret key in code
- 🟡 Missing CSRF protection on state-changing endpoints
- 🟡 Overly broad OAuth scopes

---

## 3. Secrets Management

### What counts as a secret
API keys, database credentials, private keys, tokens, certificates, webhook secrets,
encryption keys, service account credentials, OAuth client secrets.

### Detection patterns
```
# Common patterns that indicate hardcoded secrets (flag all):
password = "..."
api_key = "sk-..."
secret_key = "..."
AWS_SECRET_ACCESS_KEY = "..."
DATABASE_URL = "postgres://user:pass@..."
PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----"
```

### Critical rules
- 🔴 **Never hardcode secrets.** Use environment variables, vault, or secrets manager.
- 🔴 **Never commit secrets.** Check for `.env` files, `*.pem`, `*_key` in git history.
- 🔴 **Never log secrets.** Redact in log output, mask in error messages.
- 🔴 **Rotate after exposure.** If a secret was ever in code/logs, consider it compromised.
- 🟡 Use `.gitignore` for `.env`, `*.pem`, `terraform.tfstate` (contains secrets)
- 🟡 In Terraform: `sensitive = true` on variables, avoid `terraform.tfstate` in shared storage without encryption
- 🟡 In Ansible: use `ansible-vault`, `no_log: true` on tasks handling secrets

---

## 4. Input Validation

### Defense in depth
1. **Syntactic validation** — Type, format, length, allowed characters
2. **Semantic validation** — Business rules, range checks, consistency
3. **Sanitization** — Escape/encode for output context (HTML, SQL, shell)

### Checklist
- [ ] All external input validated at entry points (API handlers, CLI args, file parsers)
- [ ] Validation happens server-side (client validation is UX, not security)
- [ ] File uploads: validate type, size, and content (not just extension)
- [ ] Numeric inputs: check bounds, prevent integer overflow
- [ ] String inputs: max length enforced, encoding validated
- [ ] JSON/YAML parsing: depth limits to prevent DoS
- [ ] Deserialization: never deserialize untrusted data with unrestricted types (pickle, yaml.load)

### Critical rules
- 🔴 **Python:** Never `pickle.loads(untrusted)` or `yaml.load(untrusted, Loader=Loader)`
  - Use `yaml.safe_load()`, `json.loads()`
- 🔴 **Go:** Validate `Content-Type` before parsing. Set `http.MaxBytesReader`.
- 🔴 **Bash:** Validate all positional args before use. `[[ "$1" =~ ^[a-zA-Z0-9_-]+$ ]]`
- 🔴 **Terraform:** Validate variables with `validation` blocks.

---

## 5. Supply Chain & Dependencies

### Checklist
- [ ] Dependencies pinned to exact versions (lock files committed)
- [ ] No known CVEs in dependency tree (run `pip audit`, `cargo audit`, `npm audit`)
- [ ] Minimal dependency surface — don't add a library for a 10-line function
- [ ] Typosquatting check on new dependencies (verify package name and publisher)
- [ ] CI runs dependency audit on every PR

### Critical rules
- 🔴 Unpinned dependencies in production (can be hijacked via version bump)
- 🔴 Known critical CVEs in dependency tree
- 🟡 Stale dependencies (>1 year without update) — potential unpatched vulns
- 🟡 Unnecessary transitive dependencies — bloat and attack surface
