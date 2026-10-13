# Interpreting PBT Failures

## Shrunk Examples: Reading Minimized Failing Inputs

When PBT finds a failing case, it shrinks to the simplest example.

```python
@given(st.lists(st.integers()))
def test_process_list(items):
    result = process(items)
    assert len(result) == len(items)

# Hypothesis found failure with: [0, 1, 2, 3, ..., 100]
# Shrunk to simplest: [0]
```

The shrunk example tells you: the simplest failing input, exact trigger values, minimal case to debug.

**Action:** Run the test with just the shrunk example to debug locally.

## Bug vs Test Bug: How to Tell

### Sign: Bug in Code
```python
@given(st.integers(min_value=1))
def test_divide_by_two(n):
    assert divide(n, 2) == n // 2
# If divide() returns wrong result → code bug
```

### Sign: Bug in Property
```python
@given(st.lists(st.integers()))
def test_sum(items):
    assert sum(items) == len(items)  # WRONG PROPERTY
# sum([1,2,3]) = 6, len([1,2,3]) = 3 → test bug
```

**Decision rule:** If the shrunk example is obviously valid input and the expected output is clearly correct, it's a code bug. If the expected output doesn't make sense for the input, it's a test bug.

## Flaky PBT: Usually Non-Determinism in Code

### Symptoms
- Test passes sometimes, fails sometimes
- Different failures on different runs
- Failures that can't be reproduced with the same seed

### Root Causes
1. **Thread races** — concurrent writes without synchronization
2. **Time dependency** — `datetime.now()` in tested code
3. **External state** — database, file system, network
4. **Global mutable state** — module-level variables modified during test

### Fix: Inject control or synchronize
```python
# Bad: hidden time dependency
def is_expired(token):
    return datetime.now() > token.expires_at

# Good: injectable time
def is_expired(token, now=None):
    now = now or datetime.now()
    return now > token.expires_at
```

## Categorizing Bugs Found by PBT

| Category | Example | PBT Finds It When |
|----------|---------|-------------------|
| **Boundary** | `arr[n-1]` when n=0 | Generator produces 0 or empty |
| **Overflow** | `x + y` when x=MAX_INT | Generator produces extreme values |
| **Encoding** | Invalid surrogate pairs | Generator produces full unicode range |
| **State** | get() after delete() returns stale | Stateful testing with operation sequences |
| **Concurrency** | Race in cache eviction | Flaky failures with timing variations |

## What to Do After Fixing

1. **Verify fix works** — run with the exact seed that failed
2. **Add shrunk case as explicit test** — regression protection
3. **Keep PBT test running** — ensures fix doesn't regress

```python
# Step 2: Explicit regression test
def test_boundary_explicit():
    """Regression: PBT found n=0 case"""
    with pytest.raises(ValueError):
        get_last([], 0)

# Step 3: Keep PBT running
@given(st.integers(min_value=-10, max_value=1000))
def test_get_last_robust(n):
    if n > 0:
        arr = list(range(n))
        assert get_last(arr, n) == n - 1
    else:
        with pytest.raises(ValueError):
            get_last([], n)
```
