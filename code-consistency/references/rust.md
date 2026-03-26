# Rust Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Project Structure & Packaging](#3-project-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: RFC 430 + Rust API Guidelines
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `user_id`, `retry_count` |
| Functions / methods | `snake_case` | `parse_token()`, `into_inner()` |
| Types / structs / enums | `PascalCase` | `InvoiceProcessor`, `TokenKind` |
| Traits | `PascalCase` (often adjective/verb) | `Serialize`, `Display`, `AsyncRead` |
| Enum variants | `PascalCase` | `Color::DarkBlue`, `Error::NotFound` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PORT` |
| Static variables | `UPPER_SNAKE_CASE` | `GLOBAL_ALLOCATOR` |
| Modules | `snake_case` | `mod config;`, `mod auth;` |
| Crates | `snake_case` (hyphens in Cargo.toml, underscores in code) | `my-crate` → `my_crate` |
| Lifetimes | short lowercase | `'a`, `'ctx`, `'de` |
| Type parameters | single uppercase or short PascalCase | `T`, `E`, `Key`, `Value` |
| Macros | `snake_case!` | `vec![]`, `println!()` |
| Feature flags | `kebab-case` in Cargo.toml | `serde-support`, `async-runtime` |

**Critical rules:**
- 🔴 Conversion methods: `as_*` (cheap ref), `to_*` (expensive/clone), `into_*` (consuming)
- 🔴 Accessor methods: field name directly (`fn name(&self) -> &str`), not `get_name`
- 🔴 Builder pattern: `fn with_<field>(mut self, val: T) -> Self` or `fn <field>(mut self, val: T) -> Self`
- 🔴 Boolean methods: `is_*`, `has_*`, `can_*`, `should_*`
- 🟡 Avoid `_impl` suffix — use inner modules or different names
- 🟡 Test modules: `#[cfg(test)] mod tests { ... }` inside each file

---

## 2. Error Handling

### Result/Option patterns
```rust
// CRITICAL: Use Result<T, E> for recoverable errors, never panic in library code
pub fn parse_config(path: &Path) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)
        .map_err(|e| ConfigError::Io { path: path.to_owned(), source: e })?;
    toml::from_str(&content)
        .map_err(|e| ConfigError::Parse { source: e })
}
```

### Custom error types
```rust
// thiserror (preferred for libraries)
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("configuration error: {0}")]
    Config(#[from] ConfigError),
    #[error("network error: {0}")]
    Network(#[from] reqwest::Error),
    #[error("validation failed: {message}")]
    Validation { message: String },
}

// anyhow (preferred for applications/binaries)
use anyhow::{Context, Result};

fn main() -> Result<()> {
    let config = load_config()
        .context("failed to load application config")?;
    Ok(())
}
```

**Critical rules:**
- 🔴 Libraries: use `thiserror` with typed errors. Never `anyhow` in public API.
- 🔴 Binaries: `anyhow::Result` is fine for top-level, always add `.context()`
- 🔴 Never `unwrap()` or `expect()` in library code — return Result
- 🔴 `unwrap()` in binaries: only in `main()` setup or with a comment explaining the invariant
- 🟡 Use `?` operator everywhere possible — avoid manual match on Result
- 🟡 Implement `Display` and `Error` (or derive via thiserror) for all error types

---

## 3. Project Structure & Packaging

### Binary project
```
my-app/
├── src/
│   ├── main.rs
│   ├── lib.rs            # if exposing a library too
│   ├── config.rs
│   ├── cli.rs            # clap argument parsing
│   └── handlers/
│       ├── mod.rs
│       └── auth.rs
├── tests/
│   └── integration_test.rs
├── benches/
│   └── benchmarks.rs
├── Cargo.toml
└── README.md
```

### Library project
```
my-lib/
├── src/
│   ├── lib.rs            # public API, re-exports
│   ├── types.rs
│   ├── parser.rs
│   └── internal/         # private implementation
│       ├── mod.rs
│       └── detail.rs
├── examples/
│   └── basic_usage.rs
├── tests/
│   └── integration.rs
├── Cargo.toml
└── README.md
```

### Workspace (multi-crate)
```
my-workspace/
├── Cargo.toml            # [workspace] definition
├── crates/
│   ├── core/
│   ├── api/
│   └── cli/
└── README.md
```

**Critical rules:**
- 🔴 `lib.rs` is the public API surface — be deliberate about `pub` exports
- 🔴 Use `pub(crate)` for crate-internal items, not `pub`
- 🔴 Feature flags: additive only, never remove functionality behind a flag
- 🟡 Group related types in modules, one concept per file
- 🟡 Use `mod.rs` or `module_name.rs` — be consistent (Rust 2018+ prefers the latter)

---

## 4. Logging & Observability

### Library detection priority
1. Detect which crate is in `Cargo.toml` — match it
2. Greenfield: `tracing` for async/instrumented code, `log` + `env_logger` for simple CLIs

### tracing (preferred)
```rust
use tracing::{info, warn, error, instrument, debug};

#[instrument(skip(db_pool), fields(user_id = %user_id))]
async fn process_request(user_id: UserId, db_pool: &PgPool) -> Result<Response> {
    info!("processing request");
    let user = db_pool.get_user(user_id).await
        .context("failed to fetch user")?;
    debug!(?user, "user loaded");
    Ok(build_response(user))
}
```

### Subscriber setup (binary)
```rust
use tracing_subscriber::{fmt, EnvFilter, prelude::*};

fn init_tracing() {
    tracing_subscriber::registry()
        .with(fmt::layer().json())  // or .pretty() for dev
        .with(EnvFilter::from_default_env())
        .init();
}
```

**Critical rules:**
- 🔴 Use `#[instrument]` on async functions — manually passing spans is error-prone
- 🔴 `skip` large or sensitive fields in `#[instrument]`
- 🔴 Never `println!` for logging in production code
- 🟡 Use structured fields: `info!(count = items.len(), "processed batch")`
- 🟡 Use `?field` for Debug formatting, `%field` for Display
- 🟡 Configure via `RUST_LOG` env var with `EnvFilter`
