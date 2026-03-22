---
name: fleet-manager
description: >
  Multi-machine fleet operations — SSH key management, cross-host syncing,
  Ansible playbook execution, fleet health checks, and inventory management.
  Trigger on: "fleet", "SSH to", "sync to", "cross-host", "deploy to", "rsync",
  "fleet health", "all machines", "inventory", or any task involving coordination
  between multiple hosts in your fleet.
---

# Fleet Manager

Coordinate operations across a multi-host fleet via SSH, rsync, and Ansible.

## Fleet Inventory Template

Customize this for your environment:

| Host | IP | Role | SSH | OS |
|---|---|---|---|---|
| YOUR_HOST_1 | YOUR_IP_1 | Primary server (services, monitoring) | key auth | Ubuntu 24.04 |
| YOUR_HOST_2 | YOUR_IP_2 | GPU cluster / compute workloads | key auth | Ubuntu 24.04 |
| YOUR_HOST_3 | YOUR_IP_3 | Worker node | key auth | Ubuntu 24.04 |

## SSH Access

- All hosts should use key-only auth (no passwords)
- Keys: `~/.ssh/id_ed25519` on each host
- Establish bidirectional key auth between hosts that need to sync

## Cross-Host Operations

### Sync config/skills between hosts
```bash
# Host A -> Host B
rsync -avz --exclude='.env.local' --exclude='.secrets.map' \
  /path/to/config/ user@YOUR_IP_2:/path/to/config/
ssh user@YOUR_IP_2 "cd /path/to/config && ./scripts/install.sh"

# Host B -> Host A (pull changes)
rsync -avz --exclude='.env.local' --exclude='.secrets.map' \
  user@YOUR_IP_2:/path/to/config/ /path/to/config/
```

### Remote Command Execution
```bash
ssh user@YOUR_IP_1 "command here"
ssh user@YOUR_IP_2 "command here"
```

### Fleet Health Check
```bash
for host in YOUR_IP_1 YOUR_IP_2 YOUR_IP_3; do
    echo "=== $host ==="
    ssh -o ConnectTimeout=3 user@$host "hostname && uptime && free -h | head -2" 2>/dev/null || echo "UNREACHABLE"
done
```

## Rules

- Always use `127.0.0.1` not `localhost` on all hosts (avoids IPv6 resolution issues)
- Know which hosts have NOPASSWD sudo vs password-required sudo
- Keep an Ansible inventory file for your fleet
- When syncing skills/config, use a git repo — not raw cp
- Test commands on one host before rolling to the fleet
