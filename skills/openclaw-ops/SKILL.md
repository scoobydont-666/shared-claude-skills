---
name: openclaw-ops
description: >
  OpenClaw and NemoClaw operations — sandbox management, inference provider config,
  policy configuration, Tailscale integration, security hardening, skill vetting.
  Trigger on: "OpenClaw", "NemoClaw", "OpenShell", "sandbox", "openclaw tui",
  "agent assistant", "ClawHub", "gateway token", or any task involving the
  personal AI assistant deployment.
---

# OpenClaw/NemoClaw Operations

## Deployment Architecture

| Component | Status | Port | Access |
|---|---|---|---|
| OpenClaw | latest | 18789 (loopback) | Tailscale Serve -> HTTPS |
| NemoClaw | alpha | 8080 (OpenShell gateway) | Internal |
| Sandbox | configurable | — | `nemoclaw <name> connect` |
| Tailscale | Connected | YOUR_TAILSCALE_IP | `https://YOUR_HOST.YOUR_TAILNET/` |

## Security Posture

- All messaging channels **disabled** (WhatsApp, Telegram, Discord, Slack, Signal, Matrix, IRC)
- DM policy: **disabled** on all channels
- Gateway auth: **token-based**
- Gateway bind: **loopback only** (127.0.0.1:18789)
- UFW: port 18789 **denied** from LAN, **allowed** via tailscale0
- NemoClaw sandbox: OpenShell with Landlock + seccomp + network namespace isolation

## Interaction

**Recommended: CLI/TUI via Tailscale SSH (most secure)**
```bash
# From any device on your tailnet
ssh user@YOUR_HOST    # via Tailscale
openclaw tui          # interactive chat

# Or inside the sandbox
nemoclaw my-assistant connect
openclaw tui
```

**Web dashboard:** `https://YOUR_HOST.YOUR_TAILNET/` (tailnet only)

## Inference

**Primary:** Local Ollama (recommended for privacy)
- Point to your Ollama instance (e.g., YOUR_OLLAMA_HOST:11434)
- Available models depend on your setup

**Fallback:** Anthropic Claude API (if configured)

## Key Commands

```bash
# Gateway
openclaw gateway status
openclaw gateway restart
systemctl --user status openclaw-gateway

# Sandbox
nemoclaw list
nemoclaw my-assistant status
nemoclaw my-assistant connect
nemoclaw my-assistant logs --follow
nemoclaw my-assistant destroy         # nuclear option

# Config
openclaw config set <key> <value>
openclaw doctor                       # health check
openclaw security audit --deep        # policy drift check

# Tailscale
sudo tailscale serve status
sudo tailscale serve --bg 18789       # re-enable serve
sudo tailscale serve --https=443 off  # disable serve
```

## Security Warnings

1. **CVE-2026-25253** (CVSS 8.8) — patched in >= 2026.1.29. Ensure you run a patched version.
2. **Large attack surface** from messaging integrations — keep them all disabled unless needed.
3. **ClawHub skills** — no mandatory vetting. Treat all as untrusted. Audit before installing.
4. **NemoClaw is alpha** — expect instability. The sandbox is the security-critical layer.
5. **API keys** — never paste in chat. Use env vars or config files with 600 permissions.

## Rules

- Never enable messaging channels without explicit approval
- Never install ClawHub skills without security review
- Never expose OpenClaw ports to LAN (Tailscale only)
- Always verify sandbox is active before trusting isolation
- Rotate gateway token if compromised
- Keep OpenClaw updated (check: `openclaw --version`)
