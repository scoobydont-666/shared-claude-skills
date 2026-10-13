---
name: container-sandbox
description: Prepare isolated disposable environments for testing scripts, migrations and risky changes;
  inspect mounts, credentials, network access and cleanup before execution.
---
# Disposable execution environments

A container shares its host kernel. It is not a sufficient boundary for arbitrary hostile code. Use an approved disposable VM or stronger isolation for untrusted workloads. Choose isolation based on the actual trust boundary.

## Prepare

- Inspect the script and expected writes. Use a disposable copy containing no secrets, credentials or private data that the workload is not allowed to read.
- Use an approved image pinned by digest. Resolve the image before disabling networking.
- Run non-root, drop capabilities, enable no-new-privileges, use a read-only root filesystem, bound memory/processes, and disable networking unless explicitly needed.
- Do not mount SSH keys, cloud credentials, the container socket, host root, or host networking. Read-only secret mounts still disclose secrets.
- Use a unique output directory owned by the operator. Never reuse a shared fixed `/tmp` directory.

## Example structure

Set `SANDBOX_IMAGE` to a reviewed `name@sha256:...` image and `SANDBOX_INPUT` to a disposable sanitized input directory. Verify both before running:

```bash
: "${SANDBOX_IMAGE:?Set a reviewed digest-pinned image}"
: "${SANDBOX_INPUT:?Set a sanitized absolute input directory}"
SANDBOX_OUTPUT=$(mktemp -d)
docker run --rm --network none --read-only \
  --user "$(id -u):$(id -g)" --cap-drop ALL \
  --security-opt no-new-privileges --pids-limit 128 --memory 1g \
  --tmpfs /tmp:rw,nosuid,nodev,size=128m \
  --mount "type=bind,src=$SANDBOX_INPUT,dst=/input,readonly" \
  --mount "type=bind,src=$SANDBOX_OUTPUT,dst=/output" \
  "$SANDBOX_IMAGE" /bin/sh -c 'cp -R /input/. /output/ && cd /output && ./test.sh'
```

The image must contain the chosen shell and dependencies; do not silently fetch packages during the test. This example is a template, not proof of containment on a particular host. Device/GPU passthrough expands the boundary and needs separate review.

Inspect results before use. Keep failed-run evidence and output until no longer needed. Remove only the verified directory created by this run under the user's cleanup policy. Ansible check mode can still contact real hosts; use disposable inventory and targets, never production credentials as a sandbox shortcut.
