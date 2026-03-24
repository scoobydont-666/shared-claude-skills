# Architecture Analysis Reference

## Table of Contents
1. [SOLID Principles](#1-solid-principles)
2. [Coupling & Cohesion](#2-coupling--cohesion)
3. [Layering & Boundaries](#3-layering--boundaries)
4. [Abstraction Quality](#4-abstraction-quality)
5. [Technical Debt Indicators](#5-technical-debt-indicators)

---

## 1. SOLID Principles

### Single Responsibility Principle (SRP)
A module/class/function should have one reason to change.

**Detection:**
- Does the module change when unrelated business rules change?
- Does the class name contain "And" or "Manager" or "Handler" without specificity?
- Does the file import from 5+ unrelated domains?

**Common violations:**
| Smell | Example | Fix |
|---|---|---|
| Controller does business logic | HTTP handler validates, computes, persists | Extract service layer |
| Config + runtime in one class | Class loads config AND uses it for processing | Separate config parsing from usage |
| Model + serialization coupled | Data class includes JSON/DB serialization logic | Use separate serializer/mapper |
| "Utils" module > 200 lines | Grab-bag of unrelated helpers | Split by domain |

- 🔴 A single module that changes for 3+ unrelated reasons
- 🟡 A function with >2 distinct responsibilities (validate + transform + persist)

### Open/Closed Principle (OCP)
Open for extension, closed for modification.

**Detection:**
- Adding a new variant requires modifying existing if/switch chains
- New feature types require touching core logic

**Fix patterns:**
- Strategy pattern / interface dispatch
- Plugin architecture / registry pattern
- Configuration-driven behavior

- 🟡 Long if/elif/switch on type discriminators that grow with each new feature

### Liskov Substitution Principle (LSP)
Subtypes must be substitutable for their base types without breaking behavior.

**Detection:**
- Overridden methods that throw "not implemented"
- Subclass that narrows preconditions or widens postconditions
- isinstance/type checks after receiving an interface type

- 🔴 A subclass/implementation that silently ignores or breaks the contract of its interface

### Interface Segregation Principle (ISP)
No client should be forced to depend on methods it doesn't use.

**Detection:**
- Interface/trait with >7 methods
- Implementations that stub out half the interface with no-ops
- Callers that use only 1-2 methods of a large interface

- 🟡 Interface with >7 methods — consider splitting into role-specific interfaces

### Dependency Inversion Principle (DIP)
High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Detection:**
- Business logic imports database driver, HTTP client, or framework directly
- Concrete types in function signatures where interfaces would suffice
- Configuration/infrastructure decisions leak into domain logic

- 🔴 Domain/business layer importing infrastructure packages directly
- 🟡 Function accepting concrete type when only a subset of methods are used

---

## 2. Coupling & Cohesion

### Coupling types (ordered from worst to best)
| Type | Description | Example | Severity |
|---|---|---|---|
| Content | Module reaches into internals of another | Accessing private fields via reflection | 🔴 |
| Common | Modules share global mutable state | Global config dict mutated at runtime | 🔴 |
| Control | Module passes flag to control another's logic | `process(data, is_admin=True)` changing behavior | 🟡 |
| Stamp | Module passes a data structure, uses only part | Passing entire User when only user_id needed | 🟡 |
| Data | Modules communicate via parameters/return values | Function takes specific args, returns result | ✅ |
| Message | Modules communicate via events/messages | Event bus, message queue | ✅ |

### Cohesion types (ordered from worst to best)
| Type | Description | Severity |
|---|---|---|
| Coincidental | Elements have no meaningful relationship | 🔴 |
| Logical | Elements are in same category but unrelated in function | 🟡 |
| Temporal | Elements happen to execute at the same time | 🟡 |
| Functional | All elements contribute to a single well-defined task | ✅ |

### What to flag
- 🔴 **Circular dependencies:** Module A imports B, B imports A (directly or transitively)
- 🔴 **Shared mutable state:** Global/singleton state modified by multiple modules
- 🔴 **Tight coupling to framework:** Business logic that can't run without the web framework
- 🟡 **Feature envy:** Method that uses more data from another class than its own
- 🟡 **Inappropriate intimacy:** Two modules that know too much about each other's internals
- 🟡 **Shotgun surgery:** A single change requires editing 5+ files across modules

---

## 3. Layering & Boundaries

### Clean architecture layers (inside → outside)
```
┌─────────────────────────────┐
│     Domain / Entities       │  Pure business logic, no dependencies
├─────────────────────────────┤
│     Use Cases / Services    │  Orchestration, depends on domain only
├─────────────────────────────┤
│     Interface Adapters      │  Controllers, repos, presenters
├─────────────────────────────┤
│     Infrastructure          │  DB drivers, HTTP, filesystem, frameworks
└─────────────────────────────┘
```

**The dependency rule:** Dependencies point inward. Inner layers never import outer layers.

### Boundary checklist
- [ ] Domain layer has zero infrastructure imports
- [ ] Use cases depend on repository interfaces, not concrete DB implementations
- [ ] Controllers/handlers are thin — delegate to use cases immediately
- [ ] Infrastructure adapters implement interfaces defined in inner layers
- [ ] Configuration is loaded at the outermost layer and injected inward

### What to flag
- 🔴 **Domain imports infrastructure:** `from sqlalchemy import ...` in a domain model
- 🔴 **No clear boundaries:** All logic in one layer, flat structure with no separation
- 🟡 **Leaky abstraction:** Repository that exposes ORM-specific query objects
- 🟡 **Anemic domain:** Domain models are data-only with all logic in services
- 🟡 **Over-layered:** 6+ layers with pass-through methods that add no value

---

## 4. Abstraction Quality

### Good abstractions
- Hide complexity behind a simple interface
- Are stable — don't change when implementation details change
- Are discoverable — name and signature communicate purpose
- Are composable — can be combined without understanding internals

### Bad abstractions (worse than no abstraction)
| Smell | Problem | Fix |
|---|---|---|
| Premature abstraction | Interface with one implementation, added "just in case" | Remove until second use case exists |
| Leaky abstraction | Caller must understand internals to use correctly | Redesign interface to hide details |
| Wrong abstraction | Forced into a pattern that doesn't fit the domain | Start over from use cases |
| Incomplete abstraction | Half the operations go through abstraction, half bypass | Complete the abstraction or remove it |

### What to flag
- 🔴 **Abstraction that misleads:** Interface promises something the implementation can't deliver
- 🟡 **Speculative generality:** Abstract factory for one product, visitor pattern for one type
- 🟡 **Primitive obsession:** Using strings/ints for domain concepts (user_id as string everywhere)
  - Fix: Value objects / newtypes
- 🟡 **Missing abstraction:** Same 3-4 parameters always passed together
  - Fix: Introduce a data class / struct

---

## 5. Technical Debt Indicators

### Quantifiable signals
| Indicator | How to detect | Threshold |
|---|---|---|
| File size | Lines of code per file | 🟡 >400 LOC, 🔴 >800 LOC |
| Function size | Lines per function/method | 🟡 >50 LOC, 🔴 >100 LOC |
| Parameter count | Args per function | 🟡 >5, 🔴 >8 |
| Cyclomatic complexity | Branches per function | 🟡 >10, 🔴 >20 |
| Nesting depth | Max indent level | 🟡 >3, 🔴 >5 |
| Dependency count | Imports per module | 🟡 >10, 🔴 >20 |
| Circular deps | Import cycles | 🔴 Any |
| Dead code | Unreachable functions, unused exports | 🟡 Any |
| TODO/FIXME/HACK | Deferred work markers | 🟡 Count and report |

### Debt categorization
| Category | Impact | Urgency |
|---|---|---|
| **Reckless + deliberate** | "We don't have time for tests" | High — pay down immediately |
| **Reckless + inadvertent** | "What's a service layer?" | High — educate and refactor |
| **Prudent + deliberate** | "Ship now, refactor next sprint" | Medium — track and schedule |
| **Prudent + inadvertent** | "Now we know how it should've been" | Low — refactor when touching area |

### Reporting
When technical debt is significant, provide:
1. **Debt inventory** — numbered list of items with category and estimated impact
2. **Prioritized paydown plan** — which items to fix first and why
3. **Risk assessment** — what breaks if debt is left unpaid
