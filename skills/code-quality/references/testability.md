# Testability Analysis Reference

## Table of Contents
1. [Design for Testability](#1-design-for-testability)
2. [Dependency Management](#2-dependency-management)
3. [Test Pyramid & Coverage](#3-test-pyramid--coverage)
4. [Anti-Patterns](#4-anti-patterns)

---

## 1. Design for Testability

### Seam identification
A "seam" is a place where you can alter behavior without editing the code under test.
Every external dependency should have a seam.

| Dependency Type | Seam Technique |
|---|---|
| Database | Repository interface / data access layer |
| HTTP client | Interface + mock implementation |
| File system | Abstraction layer or in-memory FS |
| Time/clock | Inject clock interface, don't call `time.Now()` directly |
| Random | Inject seed or generator |
| Environment vars | Config struct populated at startup, not read inline |
| External service | Client interface with mock |

### Checklist
- [ ] Can each public function be tested without network/disk/database?
- [ ] Are side effects (I/O, mutations) concentrated at boundaries, not scattered?
- [ ] Can behavior be verified through return values or observable state, not just side effects?
- [ ] Are dependencies injected, not constructed internally?
- [ ] Can the module be tested independently of other modules?

---

## 2. Dependency Management

### Dependency injection patterns
```python
# GOOD: Injectable dependency
class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier

# BAD: Hidden dependency
class OrderService:
    def __init__(self):
        self.repo = PostgresOrderRepo()  # hardcoded, untestable
        self.notifier = EmailNotifier()  # hardcoded, untestable
```

```go
// GOOD: Interface-based injection
type OrderService struct {
    repo     OrderRepository  // interface
    notifier Notifier         // interface
}

// BAD: Concrete dependency
type OrderService struct {
    db *sql.DB  // concrete, requires real DB to test
}
```

### Critical rules
- 🔴 **God objects:** Classes/structs with >7 dependencies indicate too many responsibilities
- 🔴 **Hidden deps:** Functions that import and instantiate their own deps internally
- 🔴 **Global state:** Singletons, module-level mutable vars, or class-level state
  shared across tests (causes flaky tests, test order dependency)
- 🟡 **Constructor logic:** Constructors that do work (I/O, validation, computation)
  beyond simple assignment are hard to test
- 🟡 **Static/class methods that access state:** Can't be overridden in tests

---

## 3. Test Pyramid & Coverage

### Test pyramid
```
         /  E2E  \          Few, slow, expensive
        /----------\
       / Integration \      Moderate count, test boundaries
      /----------------\
     /    Unit Tests     \  Many, fast, isolated
    /____________________\
```

### Coverage analysis
Don't chase 100%. Focus on:
- **Critical paths:** Payment, auth, data mutation — must have high coverage
- **Complex logic:** Branching, state machines, calculations — test all branches
- **Edge cases:** Boundary values, empty inputs, error conditions
- **Regression targets:** Any bug that was found in production gets a test

### What to flag
- 🔴 **No tests at all** for code handling money, auth, or data integrity
- 🔴 **Tests that always pass:** No assertions, or assertions on constants
- 🔴 **Tests coupled to implementation:** Mock every internal method, break on any refactor
- 🟡 **Missing negative tests:** Only happy path tested, no error/edge cases
- 🟡 **Slow unit tests:** Unit tests taking >100ms indicate hidden I/O
- 🟡 **Test duplication:** Same scenario tested at multiple levels without purpose

---

## 4. Anti-Patterns

### Untestable code smells
| Smell | Why it's untestable | Fix |
|---|---|---|
| Business logic in controller/handler | Requires HTTP/framework setup to test | Extract to service/domain layer |
| Logic in constructor | Can't test without constructing | Move to init() or factory method |
| Deep inheritance hierarchy | Must understand full chain to test | Favor composition over inheritance |
| Law of Demeter violations (`a.b.c.d()`) | Must mock entire chain | Inject direct dependency |
| Conditional logic in tests | Tests have bugs too | One assertion path per test |
| Shared test fixtures/setup | Tests affect each other | Isolated per-test setup |
| Time-dependent tests | Flaky, fail on different machines | Inject clock/freeze time |

### God function indicators
A function that is hard to test because it does too much:
- >50 lines of logic (excluding boilerplate)
- >3 levels of nesting
- >2 distinct responsibilities (e.g., validate + transform + persist)
- >5 parameters

**Fix:** Extract each responsibility into its own testable function.

### Mock discipline
- Mock at boundaries (I/O, external services), not internal implementation
- If you need >3 mocks for a single test, the code has too many dependencies
- Prefer fakes (in-memory implementations) over mocks for complex interfaces
- Never mock what you don't own — wrap it in an adapter, mock the adapter
