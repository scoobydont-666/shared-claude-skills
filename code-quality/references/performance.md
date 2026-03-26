# Performance Analysis Reference

## Table of Contents
1. [Algorithmic Complexity](#1-algorithmic-complexity)
2. [Memory & Allocation](#2-memory--allocation)
3. [Concurrency & Parallelism](#3-concurrency--parallelism)
4. [I/O & Network](#4-io--network)
5. [Profiling Strategies](#5-profiling-strategies)

---

## 1. Algorithmic Complexity

### Analysis checklist
- [ ] Identify hot paths (code executed per-request, per-event, or in tight loops)
- [ ] Determine Big-O for each hot path — time AND space
- [ ] Check for hidden quadratic behavior (nested iterations over growing collections)
- [ ] Look for repeated work (same computation in a loop without caching)
- [ ] Verify data structure choice matches access pattern

### Common anti-patterns
| Pattern | Problem | Fix |
|---|---|---|
| Nested loop over same collection | O(n²) | Sort + binary search, or use a set/map |
| String concatenation in loop | O(n²) due to copies (Python, Go, Java) | Use StringBuilder/join/bytes.Buffer |
| Linear search in hot path | O(n) per lookup | Use hash map, pre-index |
| Sorting when only min/max needed | O(n log n) | Use heap or single-pass min/max |
| Repeated regex compilation | Compilation per call | Compile once, reuse |
| Full collection copy for filtering | O(n) memory | Use iterators/generators, lazy evaluation |

### Critical rules
- 🔴 Any O(n²)+ in a hot path must be flagged with concrete N estimates
- 🔴 Unbounded growth (lists/maps that grow per-request without cleanup) is a memory leak
- 🟡 Premature optimization of cold paths is wasted effort — note but don't push

---

## 2. Memory & Allocation

### Patterns to flag
- 🔴 **Allocation in hot loops:** Creating objects/slices/maps inside tight loops
  - Fix: Pre-allocate, reuse buffers, use object pools
- 🔴 **Unbounded caches:** Maps/dicts that grow without eviction policy
  - Fix: LRU cache, TTL, max-size with eviction
- 🔴 **Large copies:** Passing large structs by value in Go, deep-copying in Python
  - Fix: Pass by reference/pointer, use copy-on-write where available
- 🟡 **String interning missed:** Repeated identical strings consuming memory
  - Fix: Intern or deduplicate (especially in long-running services)
- 🟡 **Closure captures:** Closures holding references to large scopes preventing GC
  - Fix: Capture only needed values, or explicitly nil out references

### Language-specific
- **Python:** Watch for: large list comprehensions (use generators), pandas copies,
  __slots__ missing on high-volume objects
- **Go:** Watch for: escape analysis failures (use `go build -gcflags='-m'`),
  unnecessary pointer indirection, sync.Pool for hot-path allocations
- **Rust:** Watch for: unnecessary clones, Box when stack allocation suffices,
  Vec growing without pre-allocated capacity

---

## 3. Concurrency & Parallelism

### Anti-patterns
| Pattern | Problem | Fix |
|---|---|---|
| Shared mutable state without sync | Race condition | Mutex, channel, or atomic |
| Lock held during I/O | Contention, deadlock risk | Release lock before I/O, use async |
| Unbounded goroutine/task spawn | Resource exhaustion | Worker pool, semaphore |
| Blocking call in async context | Thread/event loop starvation | Use async variant or spawn_blocking |
| Fire-and-forget without error handling | Silent failures | Collect results, log errors |

### Critical rules
- 🔴 Any shared mutable state without synchronization is a race condition
- 🔴 Blocking I/O in async context (tokio::spawn with sync I/O, asyncio with requests)
- 🔴 Goroutine/task leak: spawned work that never completes or is never awaited
- 🟡 Channel/queue without backpressure: can cause OOM under load
- 🟡 Over-synchronization: mutexes where atomic ops suffice

---

## 4. I/O & Network

### Patterns to flag
- 🔴 **N+1 queries:** Fetching related records one-by-one in a loop
  - Fix: Batch query, JOIN, or dataloader pattern
- 🔴 **Missing connection pooling:** Creating new DB/HTTP connections per request
  - Fix: Use connection pool (sqlalchemy pool, pgxpool, reqwest Client reuse)
- 🔴 **Unbuffered I/O:** Reading/writing byte-by-byte
  - Fix: Use buffered reader/writer
- 🟡 **Serial I/O when parallel is possible:** Sequential HTTP calls that could be concurrent
  - Fix: asyncio.gather, goroutine fan-out, tokio::join!
- 🟡 **Missing timeouts:** HTTP/DB calls without deadline
  - Fix: Always set timeout/context deadline

---

## 5. Profiling Strategies

### By language
| Language | CPU Profiling | Memory Profiling | Key Tool |
|---|---|---|---|
| Python | cProfile, py-spy | tracemalloc, memray | py-spy (sampling, low overhead) |
| Go | pprof (CPU) | pprof (heap) | `go tool pprof` |
| Rust | flamegraph, perf | DHAT, heaptrack | cargo-flamegraph |
| Bash | `time`, `strace` | N/A | `strace -c` for syscall breakdown |

### Methodology
1. **Measure first.** Never optimize without a profile.
2. **Identify the bottleneck.** Top 1-3 hot functions get 80% of attention.
3. **Set a target.** "Reduce p99 latency from 500ms to 100ms" — not "make it faster."
4. **Benchmark the fix.** Before/after comparison with same workload.
5. **Regression guard.** Add benchmark tests to prevent regression.
