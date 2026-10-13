# PBT Test Quality Checklist

## Is the Property Actually Checking Something Meaningful?

### Good: Strong Properties
```python
@given(st.lists(st.integers()))
def test_sorted_is_sorted(items):
    result = sorted(items)
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
```

### Weak: Properties That Pass Even With Bugs
```python
# Weak: only checks no exception
@given(st.text())
def test_parse_json(text):
    try:
        json.loads(text)
    except:
        pass
    # PASSES even if parse_json is broken
```

## Is the Generator Covering the Real Input Domain?

```python
# BAD: Only generates positive integers
@given(st.integers(min_value=0))
def test_abs_value(n):
    assert abs(n) >= 0

# GOOD: Cover negative too
@given(st.integers())
def test_abs_value(n):
    result = abs(n)
    assert result >= 0
    assert abs(-n) == abs(n)
```

## Are Properties Strong Enough?

```python
# Weak: passes even if function broken
@given(st.integers())
def test_add(a, b):
    result = add(a, b)
    assert result > -1000000  # Too loose

# Strong: detects real bugs
@given(st.integers(), st.integers())
def test_add(a, b):
    result = add(a, b)
    assert result == a + b  # Precise
    assert result == b + a  # Commutative
    assert add(a, 0) == a   # Identity
```

## Anti-Patterns

### Testing Implementation Instead of Contract
```python
# BAD: Leaks implementation details
@given(st.integers())
def test_cache_implementation(n):
    cache = Cache()
    cache.set(1, n)
    assert len(cache._dict) == 1  # Internal structure

# GOOD: Tests observable behavior
@given(st.integers())
def test_cache_contract(n):
    cache = Cache()
    cache.set(1, n)
    assert cache.get(1) == n
```

### Overfitting to Specific Test Case
```python
# BAD: Only works for lists of exactly 3
@given(st.lists(st.integers(), min_size=3, max_size=3))
def test_specific(items):
    assert len(items) == 3

# GOOD: General property
@given(st.lists(st.integers()))
def test_general(items):
    assert len(sorted(items)) == len(items)
```

## Quality Checklist

- [ ] Property checks a meaningful invariant (not trivial)
- [ ] Generator covers the real domain (not too narrow)
- [ ] Edge cases included (empty, zero, negative, boundaries)
- [ ] Property strong enough to catch bugs (not "no exception")
- [ ] Seed pinning works for CI reproduction
- [ ] Property is language-agnostic (not tied to implementation)
- [ ] No nondeterminism in tested code (or seed injected)
- [ ] Clear example inputs if property fails
- [ ] Shrinking produces minimal failure case
- [ ] Property documented with example invariants
