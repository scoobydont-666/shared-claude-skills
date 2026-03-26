# Fleet Port Map

All ports across the Swarm fleet. Check before assigning new ports.

## node_primary (10.0.0.20)

| Port | Service | Bind | Notes |
|---|---|---|---|
| 22 | SSH | 0.0.0.0 | UFW: LAN only |
| 2222 | P2Pool nano stratum | 0.0.0.0 | UFW: LAN only |
| 3000 | Grafana | 0.0.0.0 | HTTPS, UFW: LAN only |
| 3001 | Semaphore (Ansible UI) | 127.0.0.1 | |
| 3333 | P2Pool mini stratum | 0.0.0.0 | UFW: LAN only |
| 4444 | P2Pool main stratum | 0.0.0.0 | UFW: LAN only |
| 8000 | p2pool-observer-exporter | 127.0.0.1 | |
| 8080 | OpenShell gateway | 0.0.0.0 | NemoClaw sandbox |
| 8088 | CrowdSec LAPI | 127.0.0.1 | Moved from 8080 |
| 9050 | Tor | 127.0.0.1 | |
| 9090 | Prometheus | 127.0.0.1 | |
| 9100 | node-exporter | 127.0.0.1 | |
| 18080 | monerod P2P | 0.0.0.0 | UFW: open |
| 18081 | monerod RPC | 127.0.0.1 | |
| 18082 | monerod ZMQ-RPC | 127.0.0.1 | |
| 18083 | monerod ZMQ-pub | 127.0.0.1 | |
| 18096 | unified-exporter | 127.0.0.1 | |
| 18789 | OpenClaw dashboard | 127.0.0.1 | Tailscale Serve → HTTPS |
| 37888 | P2Pool mini P2P | 0.0.0.0 | UFW: open |
| 37889 | P2Pool main P2P | 0.0.0.0 | UFW: open |
| 37890 | P2Pool nano P2P | 0.0.0.0 | UFW: open |

## node_gpu (10.0.0.10)

| Port | Service | Bind | Notes |
|---|---|---|---|
| 22 | SSH | 0.0.0.0 | Key-only |
| 80 | Traefik HTTP | 0.0.0.0 | Docker Swarm |
| 2049 | NFS | 0.0.0.0 | |
| 3000 | Grafana | 0.0.0.0 | Docker Swarm (currently 0/1) |
| 8080 | OpenWebUI | 0.0.0.0 | Docker Swarm |
| 8081 | SearXNG | 0.0.0.0 | Docker Swarm |
| 8100 | ChromaDB | 0.0.0.0 | Docker Swarm |
| 8501 | ProjectA | 0.0.0.0 | Python (not in Swarm) |
| 8888 | Traefik dashboard | 0.0.0.0 | Docker Swarm |
| 9090 | Prometheus | 0.0.0.0 | Docker Swarm |
| 9100 | node-exporter | 0.0.0.0 | Docker Swarm |
| 9400 | dcgm-exporter | 0.0.0.0 | Docker container |
| 11434 | Ollama | 0.0.0.0 | Docker container |

## node_reserve2 (192.168.200.87)

| Port | Service | Bind | Notes |
|---|---|---|---|
| 22 | SSH | 0.0.0.0 | Key auth |
| 8188 | ComfyUI | 0.0.0.0 | systemd, GPU |
| 11434 | Ollama | 0.0.0.0 | Docker container, GPU |

## Reserved (new projects, not yet deployed)

| Port | Service | Head |
|---|---|---|
| 8502 | ProjectD | — |
| 8503 | Audit Sentinel | #4 |
| 8504 | ClauseHound | #6 |
| 8505 | Prompt Forge | #7 |
| 8506 | DocuMint | #8 |
| 7100 | Tax Prep MCP inbound | — |
| 7200 | Tax Prep MCP outbound | — |

## Conflict Notes

- Port 8502: claimed by both ProjectD and STR Manager — needs resolution
- Port 8080: OpenWebUI on node_gpu, OpenShell on node_primary — no conflict (different hosts)
- Port 3000: Grafana on both hosts — no conflict (different hosts)
