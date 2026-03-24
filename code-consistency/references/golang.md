# Golang Code Consistency Reference

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Error Handling](#2-error-handling)
3. [Project Structure & Packaging](#3-project-structure--packaging)
4. [Logging & Observability](#4-logging--observability)

---

## 1. Naming Conventions

### Authoritative baseline: Effective Go + Uber Go Style Guide
Detect and match the project's existing style first. Below is the standard baseline.

| Symbol | Convention | Example |
|---|---|---|
| Variables (local) | `camelCase` | `userID`, `retryCount` |
| Functions / methods (exported) | `PascalCase` | `ParseToken()`, `NewClient()` |
| Functions / methods (unexported) | `camelCase` | `parseHeader()`, `newConn()` |
| Types / structs | `PascalCase` | `InvoiceProcessor`, `GraphNode` |
| Interfaces | `PascalCase`, often `-er` suffix | `Reader`, `Stringer`, `TokenValidator` |
| Constants | `PascalCase` (exported) or `camelCase` (unexported) | `MaxRetries`, `defaultTimeout` |
| Errors (sentinel) | `Err`-prefix | `ErrNotFound`, `ErrTimeout` |
| Error types | `-Error` suffix | `ValidationError`, `NetworkError` |
| Packages | `lowercase`, single word | `auth`, `invoice`, `httpclient` |
| Test files | `_test.go` suffix | `handler_test.go` |
| Test functions | `TestXxx` / `BenchmarkXxx` / `FuzzXxx` | `TestParseToken` |

**Critical rules:**
- 🔴 Never stutter: if package is `auth`, don't name the type `auth.AuthClient` → use `auth.Client`
- 🔴 Acronyms stay consistently cased: `userID` not `userId`; `HTTPClient` not `HttpClient`
- 🔴 Interface with one method: name it `MethodName + er` (e.g., `io.Reader`, `fmt.Stringer`)
- 🟡 Receiver names: short, consistent, never `this` or `self`; use first letter(s) of type name
- 🟡 Avoid `util`, `common`, `misc` package names — they become dumping grounds

---

## 2. Error Handling

### The Go contract: always check errors
```go
// CRITICAL: Never ignore returned errors
result, err := doSomething()
if err != nil {
    return fmt.Errorf("doSomething: %w", err)  // wrap with context
}
```

### Error wrapping (Go 1.13+)
```go
// Wrap to add context — use %w so errors.Is / errors.As work
return fmt.Errorf("process invoice %s: %w", id, err)

// Unwrap to check type
if errors.Is(err, ErrNotFound) { ... }

var ve *ValidationError
if errors.As(err, &ve) { ... }
```

### Sentinel errors
```go
// Define at package level
var (
    ErrNotFound   = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// CRITICAL: Use %w not %v when wrapping — %v breaks errors.Is
// BAD:
return fmt.Errorf("lookup failed: %v", ErrNotFound)  // loses sentinel identity
// GOOD:
return fmt.Errorf("lookup %s: %w", id, ErrNotFound)
```

### Custom error types
```go
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}
```

### Panic vs error
- 🔴 Never use `panic` for expected error conditions — only for true invariant violations (impossible states)
- 🔴 Always recover panics at service/goroutine boundaries (HTTP handler, goroutine launcher)
- 🟡 `log.Fatal` / `os.Exit` only in `main()` — never in library code

---

## 3. Project Structure & Packaging

### Standard layout (match if detected; recommended for services)
```
my-service/
├── cmd/
│   └── server/
│       └── main.go          # entry point; wires everything together
├── internal/                # private — not importable by external modules
│   ├── auth/
│   │   ├── handler.go
│   │   └── handler_test.go
│   └── invoice/
│       ├── service.go
│       ├── repository.go
│       └── model.go
├── pkg/                     # public — importable by external modules (use sparingly)
│   └── apierror/
├── api/                     # protobuf / OpenAPI definitions
├── go.mod
├── go.sum
└── Makefile
```

### Library layout (simpler — match if detected)
```
my-lib/
├── client.go
├── client_test.go
├── options.go
├── errors.go
├── go.mod
└── README.md
```

**Critical rules:**
- 🔴 Put as much as possible under `internal/` — default to private
- 🔴 `main.go` should be a thin wire-up only; no business logic
- 🔴 Avoid circular imports — reorganize into `internal/` sub-packages
- 🟡 One package per directory; package name matches directory name
- 🟡 Interfaces belong in the package that *uses* them, not the one that *implements* them (Go proverb)
- 🟡 `init()` functions: avoid unless initializing package-level state that cannot be done otherwise

### `go.mod` essentials
```
module github.com/org/my-service

go 1.22

require (
    go.uber.org/zap v1.27.0
    ...
)
```

---

## 4. Logging & Observability

### Library detection priority
1. Detect which logger is already imported — match it
2. If greenfield on Go 1.21+: prefer `log/slog` (stdlib, structured, zero extra deps)
3. High-performance / existing Uber codebases: `go.uber.org/zap`
4. Minimalist structured logging: `github.com/rs/zerolog`
5. Fall back to `log` (stdlib) only if simplicity is explicit requirement

---

### `log/slog` (stdlib, Go 1.21+)
```go
import "log/slog"

// Package-level logger (or inject via context)
logger := slog.Default()

// Structured key-value pairs
logger.Info("payment initiated",
    slog.String("order_id", orderID),
    slog.Float64("amount", order.Total),
)
logger.Warn("rate limit approaching",
    slog.Int("current", count),
    slog.Int("limit", maxReqs),
)
logger.Error("db query failed",
    slog.String("table", "invoices"),
    slog.Any("error", err),
)

// JSON handler at entry point
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
slog.SetDefault(slog.New(handler))
```

---

### `go.uber.org/zap`
```go
import "go.uber.org/zap"

// Build logger (entry point)
logger, _ := zap.NewProduction()
defer logger.Sync()
sugar := logger.Sugar()

// Structured
logger.Info("payment initiated",
    zap.String("order_id", orderID),
    zap.Float64("amount", order.Total),
)

// With context (child logger)
reqLogger := logger.With(
    zap.String("request_id", reqID),
    zap.String("user_id", userID),
)
reqLogger.Info("processing request")
```

**Critical rules:**
- 🔴 Call `logger.Sync()` (deferred) in `main()` to flush buffered log entries
- 🟡 Prefer `zap.String(...)` typed fields over `zap.Any(...)` for performance
- 🟡 Use `logger.With(...)` to create child loggers with request-scoped context

---

### `github.com/rs/zerolog`
```go
import (
    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
)

// Global logger setup (entry point)
zerolog.TimeFieldFormat = zerolog.TimeFormatUnixMs
log.Logger = zerolog.New(os.Stdout).With().Timestamp().Logger()

// Usage
log.Info().
    Str("order_id", orderID).
    Float64("amount", order.Total).
    Msg("payment initiated")

log.Error().
    Err(err).
    Str("table", "invoices").
    Msg("db query failed")
```

---

### OpenTelemetry (Go)
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/trace"
)

var tracer = otel.Tracer("my-service/invoice")

func ProcessPayment(ctx context.Context, orderID string) (*Receipt, error) {
    ctx, span := tracer.Start(ctx, "payment.process",
        trace.WithAttributes(
            attribute.String("order.id", orderID),
        ),
    )
    defer span.End()

    receipt, err := charge(ctx, orderID)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return nil, fmt.Errorf("charge order %s: %w", orderID, err)
    }

    span.SetStatus(codes.Ok, "")
    return receipt, nil
}
```

**Critical rules:**
- 🔴 Always pass `context.Context` as the first argument to any function that does I/O — this enables trace propagation
- 🔴 Always `defer span.End()` immediately after `tracer.Start()`
- 🔴 Call `span.RecordError(err)` AND `span.SetStatus(codes.Error, ...)` on failures — they serve different purposes
- 🟡 Span names: `service.operation` dot-notation, lowercase (`"payment.process"` not `"ProcessPayment"`)
- 🟡 Inject tracer via `otel.Tracer(__name__)` at package level; don't pass tracers as arguments
- 🟡 Instrument at service call boundaries and significant business operations; avoid over-instrumentation

---

### Context propagation in goroutines
```go
// CRITICAL: context does NOT flow into goroutines automatically
ctx, span := tracer.Start(ctx, "fan-out")
defer span.End()

go func(ctx context.Context) {  // pass ctx explicitly
    childCtx, childSpan := tracer.Start(ctx, "worker.task")
    defer childSpan.End()
    // ...
}(ctx)
```

---

### Log Level Guide

| Level | When to use |
|---|---|
| `Debug` | Detailed diagnostic info; disabled in production |
| `Info` | Normal operational events: startup, requests, completions |
| `Warn` | Unexpected but recoverable; degraded mode; approaching limits |
| `Error` | Operation failed; system continues; requires attention |
