# Property-Driven Development

## Design-for-Testability Patterns

The key principle: **separate pure logic from I/O**.

### Before: I/O Mixed with Logic
```python
def process_user_batch(filename):
    """Hard to test — I/O entangled with logic"""
    users = []
    with open(filename) as f:
        for line in f:
            name, age = line.strip().split(',')
            if int(age) >= 18:
                users.append({'name': name, 'age': int(age)})

    # Save somewhere
    with open('output.csv', 'w') as f:
        for u in users:
            f.write(f"{u['name']},{u['age']}\n")

    return len(users)
```

### After: Pure Core + Thin Shell
```python
def filter_adults(users: List[Dict]) -> List[Dict]:
    """Pure logic — testable with PBT"""
    return [u for u in users if u['age'] >= 18]

def process_user_batch(filename):
    """Thin shell — minimal logic, manual tests OK"""
    users = []
    with open(filename) as f:
        for line in f:
            name, age = line.strip().split(',')
            users.append({'name': name, 'age': int(age)})

    adults = filter_adults(users)

    with open('output.csv', 'w') as f:
        for u in adults:
            f.write(f"{u['name']},{u['age']}\n")

    return len(adults)

# Now testable with PBT
@given(st.lists(st.fixed_dictionaries({
    'name': st.text(),
    'age': st.integers(0, 150)
})))
def test_filter_adults(users):
    result = filter_adults(users)
    assert all(u['age'] >= 18 for u in result)
    assert len(result) <= len(users)
```

## Identifying Properties BEFORE Writing Code

Ask these questions for every function:

1. **What's the contract?** What does this function promise?
2. **What's an inverse?** Can I undo this operation?
3. **What's unchanged?** What property should always hold?
4. **What's comparable?** Is there another path to the same answer?

### Example: Cache Implementation

```python
# BEFORE: Vague requirements
# "Implement a cache"

# AFTER: Properties defined
# 1. Get after Set: cache.set(k, v); cache.get(k) == v
# 2. Set is idempotent: set twice, value unchanged
# 3. Eviction: cache size never exceeds max_size
# 4. LRU: recently used items stay longer
# 5. Delete works: cache.delete(k); cache.get(k) == None

# Now code is clear:
class LRUCache:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.data = {}
        self.access_order = []

    def set(self, key, value):
        if key in self.data:
            self.access_order.remove(key)

        self.data[key] = value
        self.access_order.append(key)

        while len(self.data) > self.max_size:
            lru_key = self.access_order.pop(0)
            del self.data[lru_key]

    def get(self, key):
        if key in self.data:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.data[key]
        return None

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            self.access_order.remove(key)
```

## Property-First API Design

If you can't state a property, the API is unclear.

### Bad: Unclear Contract
```python
def transform(x):
    """Transforms something"""
    # What does it do?
    # Is it deterministic?
    # What are valid inputs?
    return magic(x)
```

### Good: Properties Define Contract
```python
def normalize_path(path: str) -> str:
    """
    Normalize a file path to canonical form.

    Properties:
    - Idempotent: normalize(normalize(x)) == normalize(x)
    - Equivalence: preserves the specified lexical meaning, not original spelling
    - Deterministic: same input always gives same output

    Examples:
      normalize("foo//bar") == "foo/bar"
      normalize("foo/./bar") == "foo/bar"
      Dot-dot behavior must be specified separately; lexical normalization
      does not prove filesystem containment or account for symlinks.
    """
    # Now implementation must satisfy these properties
```

## Worked Example: Cache with Invariants

```python
from hypothesis import given, assume
import hypothesis.strategies as st

class LRUCache:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.data = {}
        self.access_log = []

    def set(self, key, value):
        if key in self.data:
            self.access_log.remove(key)
        self.data[key] = value
        self.access_log.append(key)
        self._evict()

    def get(self, key):
        if key in self.data:
            self.access_log.remove(key)
            self.access_log.append(key)
            return self.data[key]
        return None

    def _evict(self):
        while len(self.data) > self.max_size:
            oldest = self.access_log.pop(0)
            del self.data[oldest]

    # Invariants we'll test
    def _check_invariants(self):
        assert len(self.data) <= self.max_size
        assert len(self.access_log) == len(self.data)
        assert set(self.access_log) == set(self.data.keys())

# Properties as PBT
@given(st.lists(st.tuples(st.integers(), st.integers())))
def test_lru_size_invariant(operations):
    cache = LRUCache(max_size=3)
    for key, value in operations:
        cache.set(key, value)
        cache._check_invariants()
        assert len(cache.data) <= 3

@given(st.integers(), st.integers())
def test_lru_retrieval(key, value):
    cache = LRUCache(max_size=5)
    cache.set(key, value)
    assert cache.get(key) == value
    cache._check_invariants()

@given(st.lists(st.tuples(st.integers(), st.integers())))
def test_lru_ordering(operations):
    assume(len(operations) > 0)
    cache = LRUCache(max_size=10)

    for key, value in operations:
        cache.set(key, value)

    # Last set item should be last in access_log
    if operations:
        last_key, last_value = operations[-1]
        assert cache.access_log[-1] == last_key
        cache._check_invariants()
```

This approach ensures the cache behaves correctly before the first real user touches it.
