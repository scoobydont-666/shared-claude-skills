# Designing generated inputs

Start from the domain and invariant, not an API name remembered from another language. Consult the installed testing library's official strategy/arbitrary API for the pinned version. Hypothesis, fast-check and proptest have different function names and type contracts.

1. Generate valid domain objects by construction. Bound string/collection sizes and numeric ranges to keep resource usage predictable.
2. Generate invalid inputs separately, targeting the exact rejected boundary. Do not let broad filters discard almost every example.
3. Include edge cases explicitly: empty, singleton, duplicates, maximum allowed size, Unicode where relevant, boundary dates and invalid encodings.
4. Compose generators for nested objects while bounding depth. Avoid unbounded recursion and converting arbitrary signed integers into allocation sizes.
5. Preserve minimized counterexamples, seeds and library versions. Reproduce failures as regression examples when they reveal an important invariant.
6. Use an independent oracle, specification or metamorphic property. Roundtrip tests alone can pass two mutually incorrect transformations; combine them with known-answer and rejection tests.

Official starting points:
- https://hypothesis.readthedocs.io/en/latest/reference/strategies.html
- https://fast-check.dev/docs/core-blocks/arbitraries/
- https://proptest-rs.github.io/proptest/intro.html

No copy-paste cross-language generator scaffold is provided here. Validate APIs and shrinking behavior in the actual test environment before adding a new strategy.
