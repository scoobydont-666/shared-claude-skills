# Generating Property-Based Tests

Start with a behavioral contract and an independent oracle. Bound inputs by the
operation's time and memory budget, generate meaningful invalid cases separately,
and isolate external side effects. Roundtrip and idempotence checks are useful
complements, but neither proves correctness alone.

## Runnable Python examples

These self-contained Hypothesis tests illustrate bounded domains and independent
checks. Adapt them to the real public interface instead of testing only standard
library behavior in an application test suite.

```python
from collections import Counter
import json
from hypothesis import given
from hypothesis import strategies as st


@given(st.dictionaries(st.text(max_size=40), st.integers(-10000, 10000), max_size=20))
def test_json_roundtrip(value):
    assert json.loads(json.dumps(value)) == value


@given(st.lists(st.integers(-10000, 10000), max_size=100))
def test_sort_contract(values):
    result = sorted(values)
    assert Counter(result) == Counter(values)
    assert all(left <= right for left, right in zip(result, result[1:]))
    assert sorted(result) == result


@given(st.binary(max_size=1024))
def test_hex_roundtrip(data):
    assert bytes.fromhex(data.hex()) == data
```

Add known-format examples for serializers: an encoder and decoder that share the
same mistaken convention may satisfy a roundtrip. For invalid input, assert the
specified error type and that no state changed; never swallow all exceptions.

## Other languages

Use the project's installed PBT library and verify its versioned API before
writing generators. Generate bounded vectors in Rust before converting values to
allocation sizes. Clone explicitly when comparing a value before and after an
in-place sort. In JavaScript, choose JSON-representable values for JSON properties
and specify treatment of non-finite numbers, undefined and Unicode edge cases.
Do not mix examples from different library versions.

## Stateful behavior

For a cache or collection, generate a bounded sequence of public operations and
compare the result with a small independent model. Reset state for each generated
example. Include operations that fail and assert that their failure preserves the
required invariants. Record seeds, minimized examples and library versions for
reproduction; keep explicit regressions alongside generated tests.

See [strategies.md](strategies.md) for generator design and
[libraries.md](libraries.md) for official documentation.
