# Secure coding review patterns

Use these review questions with actual code, callers, tests and supported framework documentation. This file is a checklist of boundaries, not a copy-paste security library.

## Input and output

Validate types, ranges, lengths and allowed values at the boundary. Validate decoded/canonical values rather than ambiguous encodings. Reject invalid input explicitly; silent normalization can change identifiers or signatures. Protect output sinks with context-appropriate escaping. Parameterize database values; allowlist identifiers that cannot be parameters. Use argv subprocess calls without shell interpolation.

Enforce body limits while reading the stream and bound decompressed size. A Content-Length check alone does not handle missing, deceptive or chunked lengths. Bound response sizes, pagination, concurrency and execution time too.

## Filesystem access

Define an application-owned root and allowed operations. Resolve paths and verify containment by path components; string prefixes accept sibling paths with the same prefix. In Python, component-aware containment can use `Path.relative_to()` after resolution; in Go, inspect `filepath.Rel()` and reject absolute or parent-traversing results. These checks alone do not close check-to-open races.

For an attacker-writable tree, use a reviewed platform-appropriate descriptor/root-scoped API that constrains resolution during the open. Deny unintended symlinks and enforce creation/ownership/mode policies. Do not promise that a final-component no-follow flag protects ancestor directories. Test sibling-prefix paths, absolute inputs, encoded traversal where applicable, symlink escapes and concurrent replacement. Bound reads and avoid accepting devices/FIFOs where only regular files are intended.

## Outbound network requests

Prefer an allowlist of required services and protocols. Validate destination authority, port, resolved IPv4/IPv6 addresses and every redirect. Keep the validated destination bound to the actual connection; a separate DNS precheck can race a second resolution. Preserve TLS hostname/certificate checks while connecting to an approved address. Test metadata/link-local, loopback, private ranges, IPv4-mapped IPv6, redirects and DNS rebinding under the intended policy.

Do not copy a short `gethostbyname` blocklist as a complete SSRF defense. Use the application's reviewed HTTP/egress boundary and apply time, byte and redirect limits. Network isolation adds defense in depth.

## Identity, authorization and secrets

Authenticate using the selected protocol and supported library. Validate signatures, algorithms, issuer, audience, expiry and scope as applicable. Enforce per-object/per-tenant authorization in each consumer path; possession of an identifier is not permission. Test denied and allowed cases, including background tasks and cache reads.

Fetch secrets from the approved mechanism, fail when required secrets are absent, and never supply a development-secret fallback. Restrict filesystem/env/log visibility and lifetime. Do not log secrets, complete bearer tokens or sensitive request bodies. Exposing a secret read-only still discloses it. Plan revocation and rotation with operator authorization.

## API and browser controls

CORS is not authentication. Configure origins narrowly and evaluate credential behavior. Protect cookie-authenticated state changes against CSRF. Use secure cookie attributes, session ownership/expiry and appropriate rate limits. Protect health and metrics according to their disclosure risk; do not exempt broad path prefixes accidentally.

## Dependencies and deployment

Resolve supported dependency versions against current vendor advisories, pin/lock under the project's policy, and test upgrades. An old exact pin is reproducible but may be vulnerable. Record scanner versions, scope and database freshness; distinguish findings, errors and unavailable tools.

Use dedicated identities and minimal capabilities, devices, mounts and network access. Do not expose host control sockets to ordinary workloads. Separate untrusted CI from release credentials. Verify the actual rendered deployment, restart behavior and recovery; a source configuration is not runtime enforcement.

## Errors, logging and crypto

Use supported cryptographic libraries and protocols; do not invent encryption or token formats. Use secure randomness for security decisions. Return bounded useful errors without internal traces or secrets. Keep redacted audit evidence for sensitive operations with defined access and retention. Preserve cancellation and release resources on every important failure path.

## Report

For each finding record file/line, revision, reachable input, failed invariant, impact, proposed fix and tests. Label hypotheses and unknowns. Tests of examples prove only those examples; a system-level security claim needs actual consumer evidence.
