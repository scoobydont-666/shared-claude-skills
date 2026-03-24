# Python Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Project Structure & Packaging](#3-project-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: PEP 8
Always detect and match the project's existing style first. The rules below are
the standard baseline to fall back on when no project style is detectable.

| Symbol | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `user_id`, `retry_count` |
| Functions / methods | `snake_case` | `get_token()`, `parse_response()` |
| Classes | `PascalCase` | `InvoiceProcessor`, `GraphNode` |
| Constants (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private members | `_leading_underscore` | `_cache`, `_validate()` |
| Name-mangled (true private) | `__double_leading` | `__secret` (use sparingly) |
| Type aliases | `PascalCase` | `UserId = int` |
| Protocols / ABCs | `PascalCase` | `Serializable`, `Runnable` |

**Critical rules:**
- 🔴 Never use single-letter names outside of loop indices or math contexts
- 🔴 Never shadow builtins (`list`, `id`, `type`, `input`, `filter`, etc.)
- 🔴 Boolean variables/functions should read as predicates: `is_valid`, `has_permission`, `can_retry`
- 🟡 Avoid abbreviations unless they are universally understood in context (`url`, `id`, `db`, `cfg`)

**Style detection hints:**
- If you see `camelCase` functions → project may use JS-influenced or older Django style; match it
- If you see `kConstantName` → Google Python style; match it

---

## 2. Error Handling

### Standard library patterns

```python
# CRITICAL: Always use specific exception types, never bare except
try:
    result = process(data)
except ValueError as e:
    raise ProcessingError(f"Invalid data format: {data!r}") from e  # chain!

# CRITICAL: Never silently swallow exceptions
# BAD:
try:
    do_thing()
except Exception:
    pass

# OK (with explicit intent):
try:
    do_thing()
except SomeExpectedError:
    logger.debug("Expected failure, continuing", exc_info=True)
```

### Custom exception hierarchy
```python
# SUGGEST: Define a base exception for your package
class AppError(Exception):
    """Base for all application errors."""

class ValidationError(AppError):
    pass

class NetworkError(AppError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
```

### Exception chaining
- 🔴 Always use `raise NewError(...) from original` when re-raising to preserve traceback
- 🔴 Use `raise NewError(...) from None` only when the original error is irrelevant to the caller

### Context managers
- 🟡 Prefer `contextlib.suppress(ExceptionType)` over try/except/pass for intentional suppression
- 🟡 Use `contextlib.contextmanager` for resource cleanup when a class is overkill

---

## 3. Project Structure & Packaging

### Modern layout (preferred — `src/` layout)
```
my-project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── models.py
│       └── utils.py
├── tests/
│   ├── conftest.py
│   └── test_core.py
├── pyproject.toml          # single source of truth
└── README.md
```

### Legacy flat layout (match if detected)
```
my-project/
├── my_package/
│   ├── __init__.py
│   └── ...
├── tests/
└── setup.py / setup.cfg
```

### `pyproject.toml` essentials
```toml
[build-system]
requires = ["hatchling"]   # or setuptools, flit — match what's present
build-backend = "hatchling.build"

[project]
name = "my-package"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [...]

[tool.ruff]         # or [tool.black], [tool.isort] — match what's present
[tool.mypy]
strict = true
```

**Critical rules:**
- 🔴 Never import from `tests/` in application code
- 🔴 `__init__.py` should not contain logic; only re-exports if needed
- 🟡 Keep `__init__.py` minimal — explicit imports in calling code are clearer
- 🟡 One class per module is a good heuristic for larger codebases

---

## 4. Logging & Observability

### Library detection priority
1. Detect which library is already imported — match it
2. If greenfield: prefer `structlog` for structured output, `loguru` for simplicity
3. Fall back to `logging` (stdlib) if no preference stated

---

### stdlib `logging`
```python
import logging

logger = logging.getLogger(__name__)  # ALWAYS use __name__

# Configuration at entry point only (main.py / app factory)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# Usage
logger.debug("Cache miss", extra={"key": cache_key})
logger.warning("Retry attempt %d of %d", attempt, max_retries)
logger.exception("Unexpected failure")  # logs ERROR + traceback
```

**Critical rules:**
- 🔴 Never call `logging.basicConfig()` inside a library — only in application entry points
- 🔴 Never use `print()` for diagnostics in library code — use `logger`
- 🔴 Use `logger.exception()` inside except blocks, not `logger.error(exc)`

---

### `structlog`
```python
import structlog

log = structlog.get_logger()

# Bind context that applies to all subsequent calls in this scope
log = log.bind(user_id=user.id, request_id=req_id)

log.info("payment.initiated", amount=order.total, currency="USD")
log.warning("rate_limit.approaching", current=count, limit=MAX)
log.error("db.query_failed", table="invoices", exc_info=True)
```

**Setup (entry point):**
```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

---

### `loguru`
```python
from loguru import logger

# Bind context
logger.bind(user_id=user.id).info("Login successful")

# Structured output via sink configuration
logger.add("app.log", serialize=True)  # JSON output

logger.debug("Processing item {item_id}", item_id=item.id)
logger.exception("Caught unexpected error")  # includes traceback
```

---

### OpenTelemetry (Python)
```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def process_payment(order_id: str) -> Receipt:
    with tracer.start_as_current_span("payment.process") as span:
        span.set_attribute("order.id", order_id)
        try:
            result = _charge(order_id)
            span.set_status(Status(StatusCode.OK))
            return result
        except PaymentError as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise
```

**Critical rules:**
- 🔴 Always propagate context via `context.attach()` when crossing thread/async boundaries
- 🟡 Span names should be `service.operation` dot-notation, lowercase
- 🟡 Record exceptions with `span.record_exception(e)` before re-raising
- 🟡 Avoid creating spans for trivial operations — instrument at service boundaries and key business operations

---

### Log Level Guide

| Level | When to use |
|---|---|
| `DEBUG` | Detailed diagnostic info; fine-grained flow; only for development |
| `INFO` | Normal operational events: startup, requests, jobs completed |
| `WARNING` | Something unexpected but recoverable; approaching limits |
| `ERROR` | Operation failed; requires attention; system continues |
| `CRITICAL` | System cannot continue; immediate action required |
