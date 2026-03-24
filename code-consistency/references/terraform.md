# Terraform (HCL) Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling & Validation](#2-error-handling--validation)
3. [Module Structure & Packaging](#3-module-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: HashiCorp Style Conventions + terraform-best-practices
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Resources | `snake_case`, type-prefixed logical name | `aws_instance.web_server` |
| Data sources | `snake_case` | `data.aws_ami.ubuntu_latest` |
| Variables | `snake_case` | `var.instance_type`, `var.enable_monitoring` |
| Outputs | `snake_case` | `output.cluster_endpoint` |
| Locals | `snake_case` | `local.common_tags` |
| Modules | `snake_case`, descriptive | `module.vpc`, `module.eks_cluster` |
| Files | `snake_case.tf` | `main.tf`, `variables.tf`, `outputs.tf` |
| Workspaces | `kebab-case` or `snake_case` | `prod-us-east-1`, `staging` |
| Providers | lowercase | `provider "aws" { }` |

**Critical rules:**
- 🔴 Never hardcode values that should be variables — especially regions, AMIs, CIDRs
- 🔴 Resource names should describe purpose, not duplicate type: `aws_instance.api` not `aws_instance.aws_instance_api`
- 🔴 Boolean variables: use `enable_*` or `is_*` prefix: `var.enable_monitoring`
- 🟡 Use plural for collections: `var.subnet_ids`, `var.allowed_cidrs`
- 🟡 Group related resources logically, not alphabetically

---

## 2. Error Handling & Validation

### Variable validation
```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
  validation {
    condition     = can(regex("^t[23]\\.", var.instance_type))
    error_message = "Only t2 or t3 instance types are allowed."
  }
}
```

### Preconditions and postconditions (TF 1.2+)
```hcl
resource "aws_instance" "api" {
  # ...
  lifecycle {
    precondition {
      condition     = data.aws_ami.selected.architecture == "x86_64"
      error_message = "AMI must be x86_64 architecture."
    }
    postcondition {
      condition     = self.public_ip != ""
      error_message = "Instance must have a public IP assigned."
    }
  }
}
```

**Critical rules:**
- 🔴 All variables must have `description` and `type`
- 🔴 Use `validation` blocks for variables with constrained values
- 🔴 Sensitive variables: mark with `sensitive = true`
- 🟡 Use `precondition`/`postcondition` for runtime invariants
- 🟡 Use `nullable = false` (TF 1.1+) when null is not a valid input

---

## 3. Module Structure & Packaging

### Root module layout
```
infrastructure/
├── main.tf                # primary resources
├── variables.tf           # all input variables
├── outputs.tf             # all outputs
├── providers.tf           # provider config + required_providers
├── versions.tf            # terraform { required_version }
├── locals.tf              # computed values
├── data.tf                # data sources
├── backend.tf             # state backend config
└── terraform.tfvars       # (git-ignored) local overrides
```

### Reusable module layout
```
modules/
└── vpc/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── versions.tf
    ├── README.md          # auto-generated with terraform-docs
    └── examples/
        └── basic/
            └── main.tf
```

### Environment structure
```
environments/
├── dev/
│   ├── main.tf            # calls modules
│   ├── terraform.tfvars
│   └── backend.tf
├── staging/
│   └── ...
└── prod/
    └── ...
```

**Critical rules:**
- 🔴 Pin provider versions: `version = "~> 5.0"` not `>= 5.0`
- 🔴 Pin terraform version: `required_version = ">= 1.5, < 2.0"`
- 🔴 Remote state backend: never local state in team/production use
- 🔴 State locking: enable DynamoDB (AWS) or equivalent
- 🟡 Use `terraform-docs` for auto-generated module README
- 🟡 Limit module depth to 2 levels — deep nesting is a maintenance trap
- 🟡 Outputs from child modules should be re-exported by root if consumed externally

---

## 4. Logging & Observability

### Terraform execution logging
```bash
# Debug output levels: TRACE, DEBUG, INFO, WARN, ERROR
export TF_LOG=INFO
export TF_LOG_PATH="./terraform.log"

# Provider-specific logging
export TF_LOG_PROVIDER=DEBUG
```

### Plan output conventions
- 🔴 Always run `terraform plan` before `apply` in CI — save plan to file
- 🔴 In CI: `terraform plan -out=tfplan && terraform apply tfplan`
- 🟡 Use `-compact-warnings` in CI to reduce noise
- 🟡 Parse plan JSON output for automated policy checks: `terraform show -json tfplan`

### Tagging for observability (cloud resources)
```hcl
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
    Repository  = var.repository_url
  }
}

resource "aws_instance" "api" {
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-api-${var.environment}"
    Role = "api-server"
  })
}
```

**Critical rules:**
- 🔴 Tag all taggable resources with at minimum: Environment, Project, ManagedBy
- 🟡 Use `default_tags` in provider block (AWS provider 3.38+) to reduce duplication
- 🟡 Emit resource identifiers as outputs for cross-stack observability
