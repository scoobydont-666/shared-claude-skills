# C Code Consistency Reference

## Naming Conventions

Match the existing project, C language version, compiler and target platform.
Use module prefixes for public symbols, descriptive local names and consistent
header guards. Avoid identifiers reserved by the language or platform. Keep
ownership and lifetime contracts visible in public declarations. Prefer ordinary
functions to macros that evaluate arguments multiple times.

## Error Handling

Check return values at the operation that can fail. Distinguish EOF, short reads,
truncation and I/O errors. A read limited to `capacity - 1` bytes cannot establish
that the complete input fitted; check for remaining input under the format's
contract. Preserve an error code before cleanup can overwrite it.

Use one documented error convention per API. Initialize output values before
returning failure. Release each acquired resource exactly once on every path;
a cleanup label is appropriate when it makes partial initialization explicit.
Never continue with a partially initialized object as if initialization succeeded.

### Memory and bounds

- State whether each pointer is borrowed, owned or transferred, and for how long.
  A non-null pointer is not evidence of a live object. Never read a generation
  field through a potentially freed pointer; validate handles through separately
  owned live storage, with synchronization for concurrent access.
- Check allocation size arithmetic for overflow before allocating. Use a temporary
  pointer for `realloc` so failure does not lose the original allocation.
- Validate signed indices for negativity before converting to `size_t`; then
  compare against the actual element count before indexing.
- Track buffer capacity separately from initialized length. A byte buffer is not
  necessarily a terminated string. Check formatting return values for truncation.
- Use only APIs provided by the target platform. Do not assume nonstandard string
  functions are universally available or that bounded copies terminate strings.
- Test empty, maximum-sized, truncated and malformed inputs, and allocation failure.
  Treat signed overflow, invalid shifts, aliasing and lifetime errors as defects.

## Project Structure & Packaging

Separate public headers, private implementation and tests. Headers must be
self-contained and expose only the intended API. Keep platform dependencies behind
small adapters. Use the repository's build system and explicitly select its C
standard; do not silently change the ABI or compiler requirements for style.

Enable the supported warning set and investigate new warnings. Use address and
undefined-behavior sanitizers for representative tests where supported; use a
separate thread-sanitizer configuration for concurrent code. A clean sanitizer
run covers the executed paths, not every possible execution.

### Concurrency

Document the owner of shared state and the synchronization protecting it.
`volatile` does not provide atomicity or thread synchronization. Declare atomic
objects with the appropriate atomic type from the start; do not cast ordinary
storage to an atomic pointer. Specify and justify weaker memory ordering when
sequential consistency is insufficient for performance.

For thread creation failures, join or safely stop every thread already started
before releasing data it might access. Specify who frees each argument allocation
on both success and failure. Joining a thread is not optional cleanup when other
resources depend on its lifetime. Avoid concurrent destruction of locks or objects
still reachable by workers.

## Logging / Observability

Use fixed format strings and matching argument types. Keep secrets and raw private
buffers out of logs; record operation, status and bounded diagnostic metadata.
Preserve error information before logging or cleanup. Signal handlers may only use
operations permitted in that context; ordinary logging libraries are not assumed
async-signal-safe. Diagnostics must not change normal success/failure semantics.

## Review output

Report the violated contract, affected input or lifetime, observable failure and
smallest safe correction. Distinguish demonstrated undefined behavior from a
style preference. Verify critical fixes with an executable reproducer and the
project's supported compiler configuration.
