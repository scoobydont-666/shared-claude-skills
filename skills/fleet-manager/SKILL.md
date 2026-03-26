---
name: fleet-manager
description: >
  Multi-machine fleet operations — SSH key management, cross-host syncing,
  Ansible playbook execution, fleet health checks, and inventory management.
  Trigger on: "fleet", "SSH to", "sync to node_gpu", "sync to node_primary", "cross-host",
  "deploy to", "rsync", "fleet health", "all machines", "inventory", or any
  task involving coordination between node_primary, node_gpu, node_miner, or future hosts.
---

# Fleet Manager

Coordinate operations across the Swarm fleet: node_primary, node_gpu, node_miner, and future hosts.

## Fleet Inventory

| Host | IP | Role | SSH | OS |
|---|---|---|---|---|
| node_primary | 10.0.0.20 | Monero fullnode + relay + monitoring | key auth | Ubuntu 24.04 |
| node_gpu | 10.0.0.10 | GPU cluster, Docker Swarm, AI workloads | key auth | Ubuntu 24.04 |
| node_reserve2 | 10.0.1.2 | Swarm worker, Ollama, ComfyUI | key auth | Ubuntu 24.04 |
| node_miner | 10.0.0.30 | XMRig miner (pending Ubuntu migration) | key auth (pending) | HiveOS → Ubuntu |

## SSH Access

- All hosts use key-only auth (no passwords)
- Keys: `~/.ssh/id_ed25519` on each host
- node_primary ↔ node_gpu: bidirectional key auth established
- node_reserve2: key auth from node_gpu established. node_primary → node_reserve2 may need host key acceptance.
- node_miner: pending physical access for Ubuntu migration

## Cross-Host Operations

### Sync claude-config
```bash
# node_primary → node_gpu
rsync -avz --exclude='.env.local' --exclude='.secrets.map' \
  /opt/claude-configs/claude-config/ swarm_user@10.0.0.10:~/claude-configs/claude-config/
ssh swarm_user@10.0.0.10 "cd ~/claude-configs/claude-config && ./scripts/install.sh"

# node_gpu → node_primary (pull changes)
rsync -avz --exclude='.env.local' --exclude='.secrets.map' \
  swarm_user@10.0.0.10:~/claude-configs/claude-config/ /opt/claude-configs/claude-config/
```

### Remote Command Execution
```bash
ssh swarm_user@10.0.0.10 "command here"              # node_gpu
ssh swarm_user@10.0.0.20 "command here"              # node_primary (from node_gpu)
ssh swarm_user@10.0.1.2 "command here"               # node_reserve2
```

### Fleet Health Check
```bash
for host in 10.0.0.20 10.0.0.10 10.0.1.2 10.0.0.30; do
    echo "=== $host ==="
    ssh -o ConnectTimeout=3 swarm_user@$host "hostname && uptime && free -h | head -2" 2>/dev/null || echo "UNREACHABLE"
done
```

## Rules

- Always use `127.0.0.1` not `localhost` on all hosts
- node_gpu sudo requires password (not NOPASSWD like node_primary)
- node_primary is NOT a miner — never deploy XMRig there
- Ansible inventory for monero-farm: `/opt/swarm-projects/project-b/ansible/inventory/hosts.yml`
- Use Tailscale for secure cross-network access (node_primary: 100.64.0.1)
- When syncing skills/config, use claude-config repo — not raw cp

## Sudoers Differences

| Host | sudo | Notes |
|---|---|---|
| node_primary | NOPASSWD (scoped to ~37 commands) | See /etc/sudoers.d/swarm_user |
| node_gpu | password required | Use `echo "$node_gpu_PASS" \| sudo -S` or interactive |
| node_reserve2 | password required | Same as node_gpu |
| node_miner | TBD | Not yet configured |
