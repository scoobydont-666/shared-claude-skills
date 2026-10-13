# Refactoring for Testability

## Mixed I/O Functions → Pure Core + Shell

### Before: Untestable I/O
```python
def process_orders(json_file):
    """Hard to test — file I/O + business logic mixed"""
    with open(json_file) as f:
        data = json.load(f)

    results = []
    for order in data['orders']:
        total = sum(item['price'] * item['qty'] for item in order['items'])
        if total > 1000:
            order['discount'] = total * 0.1
        results.append(order)

    with open('processed.json', 'w') as f:
        json.dump(results, f)

    return len(results)
```

### After: Testable Pure Core
```python
def apply_bulk_discount(order: Dict) -> Dict:
    """Pure function — no I/O, fully testable"""
    total = sum(item['price'] * item['qty'] for item in order['items'])
    if total > 1000:
        order['discount'] = total * 0.1
    return order

# Now testable with PBT
@given(st.lists(st.fixed_dictionaries({
    'items': st.lists(st.fixed_dictionaries({
        'price': st.floats(min_value=0, max_value=1000),
        'qty': st.integers(min_value=1, max_value=10)
    }))
})))
def test_discount_calculation(orders):
    for order in orders:
        result = apply_bulk_discount(order.copy())
        total = sum(item['price'] * item['qty'] for item in result['items'])
        if total > 1000:
            assert 'discount' in result
            assert abs(result['discount'] - total * 0.1) < 0.01
```

## Missing Inverse Functions → Create Them

### Before: One-Way Encoding
```python
def encode_name(name: str) -> str:
    return name.upper().replace(' ', '_')
# Can't test roundtrip property
```

### After: With Explicit Inverse
```python
def encode_name(name: str) -> str:
    return name.upper().replace(' ', '_')

def decode_name(encoded: str) -> str:
    return encoded.replace('_', ' ').title()

@given(st.text(alphabet=st.characters(
    whitelist_categories=('Ll', 'Lu'),
    whitelist_characters=' '
), min_size=1))
def test_name_encoding_roundtrip(name):
    encoded = encode_name(name)
    decoded = decode_name(encoded)
    assert decoded.lower() == name.lower()
```

## Non-Deterministic Functions → Inject Randomness

### Before: Hidden Randomness
```python
def shuffle_list(items):
    result = items.copy()
    random.shuffle(result)
    return result
```

### After: Injected Seed
```python
def shuffle_list(items, rng=None):
    if rng is None:
        rng = random.Random()
    result = items.copy()
    rng.shuffle(result)
    return result

@given(st.lists(st.integers()), st.randoms())
def test_shuffle_with_rng(items, rng):
    shuffled = shuffle_list(items, rng=rng)
    assert sorted(shuffled) == sorted(items)
```

## Complex State → Extract Checkable Invariants

```python
class BankAccount:
    def _check_invariants(self):
        """Extract invariant as method for testing"""
        expected_balance = sum(
            amt if op == 'deposit' else -amt
            for op, amt in self.transactions
        )
        assert self.balance == expected_balance

@given(st.lists(st.tuples(
    st.sampled_from(['deposit', 'withdraw']),
    st.integers(min_value=1, max_value=1000)
)))
def test_account_invariant(operations):
    account = BankAccount(balance=10000)
    for op, amount in operations:
        try:
            if op == 'withdraw':
                account.withdraw(amount)
            else:
                account.deposit(amount)
        except ValueError:
            pass
        account._check_invariants()
```

## Checklist: Is This Function Testable?

- [ ] No file I/O (move to shell)
- [ ] No database calls (inject repository)
- [ ] No random.random() (inject seed/RNG)
- [ ] No datetime.now() (inject current_time parameter)
- [ ] No API calls (inject HTTP client or mock)
- [ ] Pure function: same input always gives same output
- [ ] Can state invariants? If not, refactor
- [ ] Can identify a roundtrip? If yes, test it
- [ ] Can identify idempotence? If yes, test it
