# CONFIGURATION.md (shared-claude-skills kit)

Every skill in this kit that uses {{...}} placeholders expects the
operator to fill in actual values in this file. Replace each
placeholder with the value for your environment, then install the kit
to `~/.claude/skills/`.

The placeholders are grouped by category. Within each category, list
your values in the indicated format.

---

## Paths

Paths must be absolute. Avoid `~` and `${HOME}` expansion — use the
fully-expanded path so the skill body can be read by tools that don't
expand shell variables.

```yaml
paths:
  MODEL_DIR:        # e.g. /opt/llm/models
  DATA_DIR:         # e.g. /opt/llm/data
  CHECKPOINT_DIR:   # e.g. /opt/llm/checkpoints
  POLICY_DIR:       # e.g. /opt/policy/packs
  HOME:             # absolute path to your $HOME (e.g. /home/<user>)
```

## Compute

```yaml
compute:
  GPU_COUNT:        # integer (e.g. 8)
  GPU_TYPE:         # GPU model identifier (e.g. A100-80GB, H100-80GB)
```

## Cluster

```yaml
cluster:
  K8S_CONTEXT:      # kubectl context name (e.g. prod-us-east)
  KUBECONFIG:       # absolute path to kubeconfig
  NODE_NAME:        # node name for kubectl targets (e.g. node-a-01)
```

## Infrastructure

```yaml
infra:
  BMC_ENDPOINT:            # IPMI/Redfish URL (e.g. https://<bmc-host>/redfish/v1)
  BMC_USERNAME:            # BMC user (vault ref recommended)
  BMC_PASSWORD:            # BMC password (vault ref recommended)
  POWER_STATE:             # 'on' | 'off' | 'soft' | 'cycle' | 'reset'

  VLLM_BASE_URL:           # vLLM serving URL (e.g. http://gpu-host:8000/v1)
  HEALTH_POLL_INTERVAL:    # seconds (e.g. 30)

  PRISM_CENTRAL_URL:       # Prism Central URL (e.g. https://prism.example.com:9440)
  PRISM_CENTRAL_USER:      # PC user
  PRISM_CENTRAL_PASSWORD:  # PC password (vault ref)

  MODEL_REGISTRY:          # HF Hub URL or local registry path
  HF_TOKEN:                # HuggingFace token (vault ref)
```

## Git

```yaml
git:
  GIT_REMOTE:                  # origin URL (e.g. git@github.com:org/repo.git)
  BRANCH_PROTECTION_LEVEL:     # main | dev | feature
  SWARM_REGISTRY:              # Swarm NFS root
  WORK_QUEUE_DIR:              # Swarm work queue directory
```

## Environments

```yaml
envs:
  STAGING_ENV:        # identifier (e.g. staging-us-east)
  PROD_ENV:           # identifier (e.g. prod-us-east)
```

## Auth

```yaml
auth:
  API_TOKEN:           # generic API token (vault ref)
  BOOTSTRAP_TOKEN:     # bootstrap-tier token (vault ref)
```

## Cost

```yaml
cost:
  ELECTRICITY_TARIFF:    # TOU tariff profile (e.g. peak-shoulder-off)
  CLOUD_BUDGET:          # monthly cloud spend cap (USD)
```

---

## How this file is consumed

Every skill in this kit has placeholder tokens like `{{GPU_COUNT}}`.
The build pipeline (`scripts/build.py`) reads this file and substitutes
each `{{...}}` with the value you set above. The resulting skill body
contains concrete paths/credentials tailored to your environment.

If you do not set a placeholder value, the skill body keeps the
literal `{{...}}` token (the build does not error out — missing
values are flagged in the skill body so the operator sees them).

## How secrets are handled

Every secret-shaped placeholder (`BMC_PASSWORD`, `PRISM_CENTRAL_PASSWORD`,
`API_TOKEN`, `BOOTSTRAP_TOKEN`, `HF_TOKEN`) is documented as a
"vault ref recommended" — meaning the value you put here may be a
vault reference string (e.g. `vault://kv/bmc-pass`) rather than the
literal secret. The build does NOT inline secrets into the skill
body; it inlines the reference path, and the consumer's vault plugin
resolves it at runtime.

## Validation

After you fill in the values, run `python3 scripts/build.py validate`
to confirm every `{{...}}` token in the kit has a corresponding entry
in this file. Missing values surface as warnings (build continues)
or errors (build aborts), depending on the `strictness` flag.
