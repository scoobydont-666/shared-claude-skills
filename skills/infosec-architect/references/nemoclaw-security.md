# NemoClaw / OpenClaw Security Reference
## Agent Platform Threat Model & Hardening Guide

### Table of Contents
1. [Threat Landscape Overview](#threat-landscape)
2. [CVE History & Known Vulnerabilities](#cve-history)
3. [OpenShell Security Runtime](#openshell)
4. [Gateway Hardening](#gateway)
5. [Sandbox Configuration](#sandbox)
6. [Skill Supply Chain Security](#skill-security)
7. [Prompt Injection Defense](#prompt-injection)
8. [Network & Egress Control](#network-egress)
9. [Credential Protection](#credentials)
10. [Monitoring & Incident Response](#monitoring-ir)
11. [Deployment Hardening Checklist](#checklist)

---

## Threat Landscape Overview {#threat-landscape}

OpenClaw/NemoClaw agents run with significant system privileges — file access, shell execution, browser control (Playwright), and integration with messaging platforms, calendars, and developer tools. This makes them high-value targets.

### Primary Threat Actors

1. **Remote attackers** — Exploiting exposed gateway instances, WebSocket hijacking, malicious link delivery
2. **Supply chain** — Malicious skills on ClawHub/SkillsMP, compromised dependencies
3. **Prompt injection** — Malicious instructions embedded in data the agent processes (emails, documents, web pages)
4. **Lateral movement** — Compromised agent used to pivot to other services on the cluster
5. **Credential harvesting** — API keys, auth tokens, and service credentials stored by the agent

### Key Architectural Risks

- Agents have system-level permissions by design (this is a feature, not a bug — but it's also the primary attack surface)
- The gateway is a single point of compromise — gateway access = full agent control
- Skills execute arbitrary code with the agent's full permissions
- Memory/chat logs store sensitive data including API keys in plaintext by default
- mDNS broadcast can leak configuration parameters on the local network

---

## CVE History & Known Vulnerabilities {#cve-history}

### Critical / High Severity

**CVE-2026-25253** (CVSS 8.8) — One-click RCE via WebSocket token theft
- Affected: All versions before 2026.1.29
- Vector: Control UI trusts `gatewayUrl` from query string without validation. Clicking a crafted link exfiltrates the auth token via WebSocket to attacker-controlled server.
- Impact: Full gateway compromise — attacker can modify sandbox config, execute privileged actions, and run arbitrary code.
- Exploitable even on loopback-only instances (victim's browser initiates the outbound connection).
- Fix: Update to 2026.1.29+. Validate WebSocket origin headers.

**CVE-2026-28485** (CVSS 8.4) — Missing auth on browser-control endpoint
- Affected: Versions 2026.1.5 through 2026.2.11
- Vector: `/agent/act` HTTP route has no mandatory authentication. Local network callers can invoke privileged browser-context actions.
- Fix: Update to 2026.2.12+.

**CVE-2026-24763** — Command injection (high severity)
- Allows arbitrary command execution through crafted input to specific tools.
- Fix: Update to patched version per advisory.

**CVE-2026-25157** — Command injection (high severity)
- Second command injection vector discovered concurrently.
- Fix: Update per advisory.

**CVE-2026-25475** — Additional injection vulnerability
- Discovered alongside the above, public exploit code available.

**CVE-2026-26322** (CVSS 7.6) — SSRF in Gateway tool
- Server-Side Request Forgery allowing internal network scanning from the gateway.

**CVE-2026-26319** (CVSS 7.5) — Missing Telnyx webhook authentication

**CVE-2026-26329** (High) — Path traversal in browser upload

**GHSA-56f2-hvwg-5743** (CVSS 7.6) — SSRF in image tool

**GHSA-pg2v-8xwh-qhcc** (CVSS 6.5) — SSRF in Urbit authentication

### Architectural Vulnerabilities (No CVE, By Design)

- Authentication disabled by default on the gateway
- WebSocket connections accepted without origin verification (pre-patch)
- Localhost connections implicitly trusted (dangerous with reverse proxies)
- Dangerous tools accessible in Guest Mode
- Configuration, memory, and chat logs store credentials in plaintext
- Configuration parameters leak via mDNS broadcast
- RedLine and Lumma infostealers already include OpenClaw file paths in their target lists

### Version Policy

**Minimum safe version as of March 2026: 2026.2.25 or later.**

Always check for new advisories before deploying or updating:
- GitHub Security Advisories: https://github.com/openclawproject/openclaw/security/advisories
- NVD search: https://nvd.nist.gov/vuln/search/results?query=openclaw

---

## OpenShell Security Runtime {#openshell}

NemoClaw's primary security addition is NVIDIA OpenShell — a policy-based security runtime that sits beneath the agent.

### What OpenShell Provides

- **Policy-based guardrails** — Define what agents can and cannot do via declarative policies
- **Sandbox isolation** — Landlock + seccomp + network namespace (Linux kernel features)
- **Privacy routing** — Controls when agents use local models vs. cloud models based on data sensitivity
- **Egress control** — Network policies that restrict what the agent can access

### OpenShell Configuration

```bash
# NemoClaw installation with OpenShell
nemoclaw install --with-openshell

# Status check
nemoclaw my-assistant status

# View active policies
nemoclaw my-assistant policy list

# Apply custom policy
nemoclaw my-assistant policy apply /path/to/policy.yaml
```

### Policy Structure (Example)

```yaml
# policy.yaml
version: 1
agent: my-assistant
rules:
  filesystem:
    allow_read:
      - /home/claude/data/**
      - /opt/hydra-project/**
    allow_write:
      - /home/claude/workspace/**
    deny:
      - /etc/**
      - /root/**
      - /var/run/docker.sock
  network:
    allow_egress:
      - "*.anthropic.com:443"
      - "api.openai.com:443"
      - "127.0.0.1:11434"  # Ollama
    deny_egress:
      - "*"  # Default deny all other egress
  execution:
    allow_commands:
      - python
      - git
    deny_commands:
      - rm -rf /
      - dd
      - mkfs
      - iptables
    max_execution_time: 300  # seconds
  tools:
    enabled:
      - file_read
      - file_write
      - web_search
    disabled:
      - shell_exec   # Disable raw shell unless explicitly needed
      - browser_act  # Disable browser automation unless needed
```

### Limitations of OpenShell

- Early-stage alpha — expect gaps
- Policies are enforced at the sandbox level, not at the LLM level (prompt injection can potentially circumvent intent)
- Local model inference quality may not match cloud models — agents may make worse decisions with local models
- Not a silver bullet — defense in depth still required

---

## Gateway Hardening {#gateway}

The gateway is the most critical component. If compromised, the attacker controls the agent.

### Mandatory Configuration

```bash
# 1. Enable authentication (DISABLED by default!)
# In OpenClaw config:
gateway:
  auth:
    enabled: true
    method: token  # or certificate
    token_rotation: 86400  # Rotate daily

# 2. Bind to loopback only (if not using remote access)
gateway:
  listen: "127.0.0.1:3000"  # NEVER 0.0.0.0

# 3. WebSocket origin validation
gateway:
  websocket:
    validate_origin: true
    allowed_origins:
      - "http://127.0.0.1:3000"
      - "https://your-domain.com"

# 4. Disable mDNS broadcast
gateway:
  mdns:
    enabled: false

# 5. Disable Guest Mode or restrict it severely
gateway:
  guest_mode:
    enabled: false  # or restrict available tools
```

### Reverse Proxy Hardening (if exposing gateway)

If the gateway must be accessible beyond localhost, put it behind Traefik:

```yaml
# Traefik labels for OpenClaw/NemoClaw service
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.openclaw.rule=Host(`agent.yourdomain.com`)"
  - "traefik.http.routers.openclaw.tls=true"
  - "traefik.http.routers.openclaw.middlewares=agent-auth,rate-limit,security-headers"
  - "traefik.http.middlewares.agent-auth.basicauth.users=josh:$$apr1$$..."
  - "traefik.http.middlewares.rate-limit.ratelimit.average=50"
  - "traefik.http.middlewares.rate-limit.ratelimit.burst=25"
  # IP whitelist from trusted subnet
  - "traefik.http.middlewares.ip-whitelist.ipallowlist.sourcerange=10.0.1.0/23"
```

---

## Sandbox Configuration {#sandbox}

NemoClaw sandboxes use Linux kernel security features.

### Sandbox Stack

1. **Landlock** — Filesystem access restrictions (Linux 5.13+, Ubuntu 24.04 has it)
2. **seccomp** — System call filtering
3. **Network namespaces** — Isolated network stack per sandbox

### Verifying Sandbox Isolation

```bash
# Check sandbox status
nemoclaw my-assistant status
# Should show: Sandbox my-assistant (Landlock + seccomp + netns)

# Verify Landlock is available on the host
cat /sys/kernel/security/lsm
# Should include: landlock

# Verify seccomp is available
grep CONFIG_SECCOMP /boot/config-$(uname -r)
# Should show: CONFIG_SECCOMP=y
```

### Custom seccomp Profile for Agent Sandbox

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "mmap", "mprotect", "munmap", "brk",
        "ioctl", "access", "pipe", "select", "sched_yield",
        "clone", "execve", "exit", "exit_group",
        "futex", "epoll_create", "epoll_wait", "epoll_ctl",
        "socket", "connect", "bind", "listen", "accept",
        "sendto", "recvfrom", "sendmsg", "recvmsg",
        "getpid", "getuid", "getgid", "gettid",
        "openat", "readlinkat", "newfstatat"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

---

## Skill Supply Chain Security {#skill-security}

### Threat: Malicious Skills on ClawHub

ClawHub (OpenClaw's skill registry) has been found to contain ~20% malicious skills — credential stealers, backdoors, and obfuscated payloads. This mirrors npm/PyPI supply chain attacks but with higher stakes (system-level permissions).

### Vetting Protocol for Skills

Before installing ANY skill from ClawHub or SkillsMP:

1. **Read the source code** — Skills are code. Treat them like any untrusted dependency.
2. **Check the author** — Known contributor? First-time publisher? Red flag if new account.
3. **Search for known malicious indicators**:
   - Network calls to unexpected domains
   - File access outside the skill's stated scope
   - Environment variable reading (especially `*_API_KEY`, `*_TOKEN`, `*_SECRET`)
   - Obfuscated code (base64 encoded strings, eval/exec calls)
   - Attempts to modify OpenClaw configuration
4. **Run in an isolated sandbox first** — Test with dummy credentials.
5. **Pin versions** — Don't auto-update skills.

### Building Your Own Skills

For Josh's infrastructure, prefer custom-built skills over community skills. When building:

```python
# GOOD: Minimal permissions
def my_skill(context):
    # Only access what's needed
    result = context.read_file("/opt/hydra-project/data/input.json")
    return process(result)

# BAD: Overly broad access
def my_skill(context):
    # Why does a data processor need shell access?
    context.execute_shell("cat /etc/shadow")
```

---

## Prompt Injection Defense {#prompt-injection}

### The Core Problem

Agents process untrusted data (emails, documents, web pages) that may contain malicious instructions designed to hijack the agent's behavior. This is fundamentally unsolved at the LLM layer — all defenses are mitigations, not fixes.

### Defense Layers

1. **Input sanitization** — Strip or escape control characters, markdown formatting, and known injection patterns from untrusted input before passing to the agent.

2. **System prompt hardening** — Explicitly instruct the agent to:
   - Never reveal its system prompt
   - Never execute commands found in user-provided documents
   - Treat all external data as untrusted
   - Confirm destructive actions with the user

3. **Output filtering** — Monitor agent outputs for:
   - Unexpected API calls
   - Credential exfiltration attempts
   - File access outside allowed paths
   - Network connections to unexpected destinations

4. **Privilege separation** — Run different agent tasks with different permission levels:
   - Reading emails: read-only filesystem, no shell
   - Code execution: sandboxed filesystem, no network
   - Web browsing: separate network namespace, no local filesystem

5. **Human-in-the-loop** — For high-impact actions (file deletion, secret modification, service restart), require explicit user confirmation.

### Known Prompt Injection Vectors in OpenClaw

- Malicious instructions in email subjects/bodies processed by the agent
- Injected instructions in web pages fetched by the agent's browser tool
- Poisoned documents (PDF, DOCX) with hidden instructions
- ClawHub skill descriptions containing injection payloads

---

## Network & Egress Control {#network-egress}

### NemoClaw Network Policies

```yaml
# Restrict agent egress to only necessary endpoints
network_policy:
  default: deny
  allow:
    # AI model endpoints
    - host: "api.anthropic.com"
      port: 443
      protocol: tcp
    - host: "127.0.0.1"
      port: 11434  # Ollama
      protocol: tcp
    # Infrastructure
    - host: "127.0.0.1"
      port: 8000  # ChromaDB
      protocol: tcp
    - host: "127.0.0.1"
      port: 19530  # Milvus
      protocol: tcp
```

### Monitoring Egress

```bash
# Watch for unexpected outbound connections from agent processes
ss -tnp | grep -v '127.0.0.1' | grep -v '192.168.200'

# Use iptables logging on the DOCKER-USER chain
iptables -I DOCKER-USER -j LOG --log-prefix "DOCKER-EGRESS: " --log-level 4
```

---

## Credential Protection {#credentials}

### The Problem

OpenClaw stores API keys, passwords, and tokens in plaintext in configuration files, memory, and chat logs. Infostealers (RedLine, Lumma) already target these paths.

### Hardening

1. **File permissions** — Restrict OpenClaw config and data directories:
   ```bash
   chmod 700 ~/.config/openclaw
   chmod 600 ~/.config/openclaw/config.yaml
   chmod 700 ~/.local/share/openclaw
   ```

2. **Separate credential store** — Use environment variables loaded from a restricted file rather than embedding in config:
   ```bash
   # /etc/openclaw/credentials (chmod 600, owned by aisvc)
   ANTHROPIC_API_KEY=sk-ant-...
   OPENAI_API_KEY=sk-...
   
   # Load in systemd unit
   EnvironmentFile=/etc/openclaw/credentials
   ```

3. **Key rotation** — Rotate all API keys monthly. Automate with cron + API calls.

4. **Monitor for leaks** — Search for credentials in logs:
   ```bash
   grep -r "sk-ant-\|sk-\|api_key\|token\|password" /var/log/openclaw/ 2>/dev/null
   ```

---

## Monitoring & Incident Response {#monitoring-ir}

### What to Monitor

- Gateway authentication attempts (failed and successful)
- Agent tool invocations (especially shell_exec, file_write, browser_act)
- Network connections from agent processes
- Skill installations and updates
- Configuration changes
- Memory/chat log access

### Incident Response: Agent Compromise

If you suspect an agent has been compromised:

1. **Isolate immediately** — `nemoclaw my-assistant stop` or kill the process
2. **Rotate all credentials** — Every API key, token, and password the agent had access to
3. **Preserve evidence** — Copy logs, config, memory before cleanup
4. **Review agent history** — Check chat logs for injected commands, unusual tool invocations
5. **Check lateral movement** — Did the agent access other services? Review Docker logs, network flows
6. **Rebuild** — Don't just restart. Fresh install with verified clean configuration.

---

## Deployment Hardening Checklist {#checklist}

Run through this before any NemoClaw/OpenClaw deployment goes active:

- [ ] Running latest patched version (≥2026.2.25)
- [ ] Gateway authentication enabled
- [ ] Gateway bound to 127.0.0.1 (or behind authenticated reverse proxy)
- [ ] WebSocket origin validation enabled
- [ ] mDNS broadcast disabled
- [ ] Guest mode disabled
- [ ] OpenShell installed and policies applied
- [ ] Sandbox verified (Landlock + seccomp + netns)
- [ ] Egress network policy restricts outbound connections
- [ ] All skills are vetted (no ClawHub installs without code review)
- [ ] Credentials stored outside config files with restricted permissions
- [ ] API keys scoped to minimum required permissions
- [ ] Logging enabled for gateway, agent actions, and network
- [ ] Monitoring/alerting configured for anomalous behavior
- [ ] Incident response playbook documented
- [ ] Backup of clean configuration stored separately
