# Cluster Hardening Reference
## Docker Swarm + GPU Infrastructure Security Baselines

### Table of Contents
1. [Docker Daemon Hardening](#docker-daemon)
2. [Swarm-Specific Security](#swarm-security)
3. [NVIDIA GPU Runtime Security](#gpu-security)
4. [Network Segmentation](#network)
5. [Host OS Hardening](#host-os)
6. [Traefik & TLS](#traefik-tls)
7. [Container Runtime Security](#container-runtime)
8. [Secrets Management](#secrets)
9. [Image Supply Chain](#image-supply-chain)
10. [Monitoring & Audit](#monitoring)

---

## Docker Daemon Hardening {#docker-daemon}

### daemon.json Security Baseline

```json
{
  "icc": false,
  "no-new-privileges": true,
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "default-ulimits": {
    "nofile": { "Name": "nofile", "Hard": 65536, "Soft": 32768 },
    "nproc": { "Name": "nproc", "Hard": 4096, "Soft": 2048 }
  },
  "storage-driver": "overlay2"
}
```

Key controls:
- `icc: false` — Disables inter-container communication on the default bridge. Containers must use explicit links or user-defined networks.
- `no-new-privileges: true` — Prevents container processes from gaining additional privileges via setuid/setgid binaries.
- `userns-remap` — Maps container root to unprivileged host UID. CAVEAT: Conflicts with NVIDIA runtime in some configurations — test thoroughly with GPU workloads. May need to exclude GPU containers from user namespace remapping.
- `live-restore: true` — Keeps containers running during daemon restarts (important for long-running GPU workloads).

### Docker Socket Protection

The Docker socket (`/var/run/docker.sock`) is equivalent to root access. NEVER mount it into containers unless absolutely required.

```bash
# Verify no containers have the socket mounted
docker ps --format '{{.Names}}' | xargs -I {} docker inspect {} --format '{{range .Mounts}}{{if eq .Source "/var/run/docker.sock"}}DANGER: {} has docker.sock{{end}}{{end}}'

# If remote API is needed, use TLS mutual auth
# Generate CA, server, and client certs
# Configure in daemon.json:
# "tls": true, "tlscacert": "/etc/docker/ca.pem", "tlscert": "/etc/docker/server-cert.pem", "tlskey": "/etc/docker/server-key.pem", "tlsverify": true
```

### Authorization Plugin

For multi-user environments, consider the OPA (Open Policy Agent) authorization plugin to enforce fine-grained Docker API access control.

---

## Swarm-Specific Security {#swarm-security}

### Manager Node Protection

- Run an odd number of manager nodes (1 for homelab, 3 for production).
- Manager nodes should NOT run workloads — use node labels and constraints to keep workloads on worker nodes.
- The Raft consensus log contains secrets and swarm state. Encrypt it:

```bash
# Enable autolock (encrypts Raft log at rest)
docker swarm update --autolock=true
# Save the unlock key securely — you need it after every daemon restart
docker swarm unlock-key
```

### Secret Rotation

```bash
# Rotate a secret (creates new version, updates services)
echo "new-secret-value" | docker secret create my_secret_v2 -
docker service update --secret-rm my_secret --secret-add source=my_secret_v2,target=my_secret my_service
docker secret rm my_secret
```

### Node Certificate Management

Swarm auto-rotates node certificates. Shorten the rotation period:

```bash
# Default is 90 days — reduce to 30
docker swarm update --cert-expiry 720h
```

---

## NVIDIA GPU Runtime Security {#gpu-security}

### Attack Surface

GPU passthrough introduces specific risks:
- **Privileged mode** — Many GPU containers run `--privileged`. This grants ALL Linux capabilities, access to all host devices, and effectively breaks container isolation.
- **NVIDIA device files** — `/dev/nvidia*` access is required but grants direct hardware access.
- **CUDA libraries** — Shared libraries from the host. A compromised CUDA library = code execution in every GPU container.
- **GPU memory** — Not isolated between containers sharing a GPU. One container can potentially read another's GPU memory.

### Hardening GPU Containers

```yaml
# docker-compose / stack file — NEVER use privileged mode
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
# Instead of --privileged, use specific device access:
# NVIDIA_VISIBLE_DEVICES controls which GPUs are accessible
# NVIDIA_DRIVER_CAPABILITIES limits what the container can do with the GPU
environment:
  - NVIDIA_VISIBLE_DEVICES=0          # Only GPU 0, not all
  - NVIDIA_DRIVER_CAPABILITIES=compute # Only compute, not video/display/utility
```

Drop capabilities aggressively on GPU containers:

```yaml
cap_drop:
  - ALL
cap_add:
  - SYS_NICE  # For GPU scheduling priority only if needed
security_opt:
  - no-new-privileges:true
  - seccomp=default
```

### Driver Version Monitoring

NVIDIA driver CVEs are common. Monitor:
- https://nvidia.custhelp.com/app/answers/detail/a_id/1021 (security bulletins)
- Subscribe to the NVIDIA security mailing list

```bash
# Check current driver version
nvidia-smi --query-gpu=driver_version --format=csv,noheader
# Compare against latest security bulletin
```

---

## Network Segmentation {#network}

### Docker Network Architecture

```
┌─────────────────────────────────────────────┐
│                 Host Network                 │
│  10.0.0.0/24 (trusted management)       │
├─────────────────────────────────────────────┤
│          Docker Overlay Networks             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ frontend │  │ backend  │  │  data    │  │
│  │ (Traefik)│  │ (APIs)   │  │ (DBs)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────┤
│        Swarm Ingress (encrypted)             │
└─────────────────────────────────────────────┘
```

Principles:
- **Separate overlay networks** for each trust boundary (frontend, backend, data).
- **Encrypt overlay traffic**: `docker network create --driver overlay --opt encrypted my_network`
- Backend services (ChromaDB, Milvus, PostgreSQL) should NEVER be on the frontend network.
- Bind database services to `127.0.0.1` — never `0.0.0.0`.

### UFW Rules Baseline

```bash
# Default deny incoming, allow outgoing
ufw default deny incoming
ufw default allow outgoing

# SSH from trusted subnet only
ufw allow from 10.0.0.0/24 to any port 22 proto tcp

# Docker Swarm (manager-to-manager, manager-to-worker)
ufw allow from 10.0.0.0/24 to any port 2377 proto tcp  # Swarm management
ufw allow from 10.0.0.0/24 to any port 7946             # Node discovery (TCP+UDP)
ufw allow from 10.0.0.0/24 to any port 4789 proto udp   # Overlay network

# Traefik entrypoints (adjust to your needs)
ufw allow 80/tcp    # HTTP (redirect to HTTPS)
ufw allow 443/tcp   # HTTPS

# Deny all Docker-managed port exposure by default
# Add /etc/docker/daemon.json: "iptables": false
# Then manually manage Docker port forwarding in UFW
# WARNING: Docker bypasses UFW by default! See iptables note below.
```

**CRITICAL**: Docker manipulates iptables directly and bypasses UFW. To prevent this:

```bash
# Option 1: Disable Docker's iptables management (requires manual rules)
# In daemon.json: "iptables": false
# Then you must manually create DOCKER-USER chain rules

# Option 2 (recommended): Use DOCKER-USER chain
iptables -I DOCKER-USER -i eth0 ! -s 10.0.0.0/24 -j DROP
```

---

## Host OS Hardening {#host-os}

### SSH Lockdown

```
# /etc/ssh/sshd_config
Port 22
AddressFamily inet
ListenAddress 0.0.0.0
Protocol 2

PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes

MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2

AllowUsers swarm-user
AllowAgents swarm-user

X11Forwarding no
PermitTunnel no
AllowTcpForwarding no
GatewayPorts no
```

### Kernel Hardening (sysctl)

```bash
# /etc/sysctl.d/99-security.conf
# Network
net.ipv4.ip_forward = 1              # Required for Docker
net.ipv4.conf.all.rp_filter = 1      # Reverse path filtering
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.tcp_syncookies = 1

# Kernel
kernel.randomize_va_space = 2        # Full ASLR
kernel.kptr_restrict = 1             # Hide kernel pointers
kernel.dmesg_restrict = 1            # Restrict dmesg to root
kernel.yama.ptrace_scope = 1         # Restrict ptrace
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
fs.suid_dumpable = 0                 # No core dumps from setuid
```

### Automatic Security Updates

```bash
# Install unattended-upgrades
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";  # Manual reboot for GPU hosts
Unattended-Upgrade::Mail "root";
```

---

## Traefik & TLS {#traefik-tls}

### Secure Traefik Configuration

```yaml
# traefik.yml (static config)
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
    http:
      tls:
        options: default

tls:
  options:
    default:
      minVersion: VersionTLS12
      cipherSuites:
        - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
      sniStrict: true

api:
  dashboard: true
  insecure: false  # NEVER expose dashboard without auth

# Rate limiting middleware
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
    security-headers:
      headers:
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
        forceSTSHeader: true
        contentTypeNosniff: true
        browserXssFilter: true
        frameDeny: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customResponseHeaders:
          X-Powered-By: ""
          Server: ""
```

---

## Container Runtime Security {#container-runtime}

### Seccomp Profiles

Use default seccomp profile at minimum. For high-security containers, create custom profiles that whitelist only needed syscalls.

```bash
# Verify seccomp is active
docker info --format '{{.SecurityOptions}}'
# Should include: seccomp

# Run container with custom profile
docker run --security-opt seccomp=/path/to/profile.json myimage
```

### Read-Only Root Filesystem

```yaml
services:
  myservice:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
    volumes:
      - data:/app/data  # Only writable mount is the data volume
```

### Resource Limits

Always set memory and CPU limits to prevent DoS from runaway containers:

```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 2G
      cpus: '1.0'
```

---

## Secrets Management {#secrets}

### Hierarchy of Approaches (best to worst)

1. **Docker Swarm secrets** — Encrypted in transit and at rest in Raft log. Available to containers at `/run/secrets/`. Best for Swarm services.
2. **Environment files with restrictive permissions** — `.env` files with `chmod 600`, owned by root. Acceptable for docker-compose dev.
3. **Environment variables in compose** — Visible via `docker inspect`. Avoid for production.
4. **Hardcoded in images or source** — NEVER. Not even "temporarily".

### Docker Secrets Usage

```bash
# Create secret from file
docker secret create db_password /path/to/password_file
# Create from stdin
echo "s3cur3p@ss" | docker secret create db_password -

# Grant to service
docker service create --secret db_password myservice
# Available inside container at /run/secrets/db_password
```

### API Key Rotation Protocol

For Claude API, Ollama endpoints, and other service keys:
1. Generate new key
2. Create new Docker secret version
3. Update services to use new secret
4. Verify services healthy
5. Revoke old key
6. Delete old Docker secret

---

## Image Supply Chain {#image-supply-chain}

### Scanning

```bash
# Trivy — scan before deploy
trivy image --severity HIGH,CRITICAL myimage:latest

# Grype — alternative scanner
grype myimage:latest

# Scan in CI or as pre-deploy gate
```

### Base Image Selection

- Prefer `-slim` or `-alpine` variants (smaller attack surface).
- Pin image digests, not just tags: `python:3.12-slim@sha256:abc123...`
- Rebuild images weekly to pick up base image security patches.

### Multi-Stage Builds

```dockerfile
# Build stage — has compilers, dev tools
FROM python:3.12-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage — minimal
FROM python:3.12-slim
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY app/ /app/
USER 1000:1000
CMD ["python", "-m", "app"]
```

---

## Monitoring & Audit {#monitoring}

### Docker Events

```bash
# Stream all Docker events (useful for detecting unauthorized actions)
docker events --filter 'type=container' --format '{{.Time}} {{.Action}} {{.Actor.Attributes.name}}'
```

### File Integrity Monitoring

```bash
# AIDE — Advanced Intrusion Detection Environment
apt install aide
aide --init
cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
# Cron: aide --check daily
```

### Log Aggregation

Centralize container and host logs. At minimum:
- Docker daemon logs
- Container stdout/stderr via json-file driver
- sshd auth logs
- UFW/iptables logs
- NVIDIA driver logs (`/var/log/nvidia*`)
- NemoClaw/OpenClaw gateway logs

```bash
# Verify logging driver
docker info --format '{{.LoggingDriver}}'
# Should be json-file or a centralized driver
```
