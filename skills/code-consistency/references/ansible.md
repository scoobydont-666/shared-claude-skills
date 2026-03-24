# Ansible (YAML) Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Role & Collection Structure](#3-role--collection-structure)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: Ansible Best Practices + ansible-lint defaults
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `http_port`, `db_password` |
| Role names | `snake_case` or `kebab-case` (match project) | `common_setup`, `docker-install` |
| Task names | Sentence case, imperative, descriptive | `Install nginx packages` |
| Handler names | Sentence case, descriptive action | `Restart nginx` |
| Playbook files | `snake_case.yml` | `site.yml`, `deploy_app.yml` |
| Group names | `snake_case` | `web_servers`, `db_primary` |
| Tags | `snake_case` | `packages`, `configuration`, `firewall` |
| Collection namespace | `snake_case` | `myorg.infrastructure` |
| Registered variables | `snake_case`, descriptive of content | `apt_result`, `service_status` |

**Critical rules:**
- 🔴 Always name every task — unnamed tasks are undebuggable
- 🔴 Use `.yml` not `.yaml` (or vice versa) — pick one, be consistent project-wide
- 🔴 Prefix role variables with role name: `nginx_port` not `port` (avoid collision)
- 🟡 Use FQCN (Fully Qualified Collection Name): `ansible.builtin.apt` not `apt`
- 🟡 Boolean values: use `true`/`false`, not `yes`/`no` (YAML 1.2 compliance)

---

## 2. Error Handling

### Task-level error control
```yaml
# Block/rescue/always (Ansible's try/catch/finally)
- name: Deploy application with rollback
  block:
    - name: Deploy new version
      ansible.builtin.copy:
        src: app-v2/
        dest: /opt/app/
    - name: Restart service
      ansible.builtin.systemd:
        name: myapp
        state: restarted
  rescue:
    - name: Rollback to previous version
      ansible.builtin.copy:
        src: app-v1/
        dest: /opt/app/
    - name: Restart service with old version
      ansible.builtin.systemd:
        name: myapp
        state: restarted
  always:
    - name: Verify service is running
      ansible.builtin.systemd:
        name: myapp
        state: started
      register: service_check
      failed_when: service_check.status.ActiveState != "active"
```

### Validation patterns
```yaml
# Assert preconditions
- name: Validate required variables
  ansible.builtin.assert:
    that:
      - app_version is defined
      - app_version | regex_search('^\d+\.\d+\.\d+$')
      - deploy_environment in ['dev', 'staging', 'prod']
    fail_msg: "Invalid deployment parameters"
    quiet: true

# Check connectivity before proceeding
- name: Verify target is reachable
  ansible.builtin.wait_for:
    host: "{{ inventory_hostname }}"
    port: 22
    timeout: 30
```

**Critical rules:**
- 🔴 Use `block/rescue` for multi-step operations that need rollback
- 🔴 Use `failed_when` / `changed_when` to define correct success criteria
- 🔴 Never `ignore_errors: true` without a subsequent check on the registered result
- 🟡 Use `ansible.builtin.assert` for precondition validation
- 🟡 Use `any_errors_fatal: true` on plays where partial failure is worse than total failure

---

## 3. Role & Collection Structure

### Role layout
```
roles/
└── nginx/
    ├── tasks/
    │   ├── main.yml          # entry point, includes others
    │   ├── install.yml
    │   └── configure.yml
    ├── handlers/
    │   └── main.yml
    ├── templates/
    │   └── nginx.conf.j2
    ├── files/                # static files
    ├── vars/
    │   └── main.yml          # role-internal variables
    ├── defaults/
    │   └── main.yml          # user-overridable defaults
    ├── meta/
    │   └── main.yml          # dependencies, galaxy metadata
    ├── molecule/             # testing
    │   └── default/
    │       ├── molecule.yml
    │       └── converge.yml
    └── README.md
```

### Project layout
```
ansible-project/
├── inventories/
│   ├── dev/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── prod/
│       ├── hosts.yml
│       └── group_vars/
├── playbooks/
│   ├── site.yml
│   ├── deploy.yml
│   └── rollback.yml
├── roles/
├── collections/
│   └── requirements.yml
├── ansible.cfg
└── README.md
```

**Critical rules:**
- 🔴 `defaults/main.yml` for user-tunable values, `vars/main.yml` for internal constants
- 🔴 Never put secrets in vars files — use `ansible-vault` or external secrets manager
- 🔴 Pin collection versions in `requirements.yml`
- 🟡 One responsibility per role — `nginx` role should not also configure the firewall
- 🟡 Use Molecule for role testing
- 🟡 Use `group_vars/` and `host_vars/` — avoid `set_fact` for persistent config

---

## 4. Logging & Observability

### Verbosity levels
```bash
ansible-playbook site.yml          # minimal output
ansible-playbook site.yml -v       # task results
ansible-playbook site.yml -vv      # task input parameters
ansible-playbook site.yml -vvv     # connection debugging
ansible-playbook site.yml -vvvv    # full plugin debugging
```

### Debug output in playbooks
```yaml
# Conditional debug output
- name: Show deployment details
  ansible.builtin.debug:
    msg: "Deploying {{ app_version }} to {{ deploy_environment }}"
  when: ansible_verbosity >= 1

# Dump variable for troubleshooting
- name: Show full service status
  ansible.builtin.debug:
    var: service_check
  when: ansible_verbosity >= 2
```

### Callback plugins for observability
```ini
# ansible.cfg
[defaults]
callbacks_enabled = ansible.posix.profile_tasks, ansible.posix.timer
stdout_callback = yaml

# For CI/CD: JSON output for machine parsing
# stdout_callback = json
```

**Critical rules:**
- 🔴 Never use `debug` tasks without `when: ansible_verbosity` guard in production playbooks
- 🔴 Use `no_log: true` on tasks handling secrets (prevents credential leaking in output)
- 🟡 Enable `profile_tasks` callback to identify slow tasks
- 🟡 Use `--diff` mode for configuration tasks to see what changed
- 🟡 Log playbook runs to a file in CI: `ANSIBLE_LOG_PATH=./ansible.log`
