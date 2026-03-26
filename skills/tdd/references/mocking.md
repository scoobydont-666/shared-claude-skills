# When to Mock

Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint

**3. Rust: Trait-based injection (preferred over mock crates)**

```rust
// Define trait at boundary
trait PaymentGateway {
    fn charge(&self, amount: u64) -> Result<Receipt, PaymentError>;
}

// Production implementation
struct StripeGateway { api_key: String }
impl PaymentGateway for StripeGateway {
    fn charge(&self, amount: u64) -> Result<Receipt, PaymentError> { /* real Stripe call */ }
}

// Test double — simple struct, no mock framework needed
struct FakeGateway { should_fail: bool }
impl PaymentGateway for FakeGateway {
    fn charge(&self, amount: u64) -> Result<Receipt, PaymentError> {
        if self.should_fail { Err(PaymentError::Declined) }
        else { Ok(Receipt { amount, id: "fake-123".into() }) }
    }
}

// Function under test accepts any PaymentGateway
fn process_order(order: &Order, gateway: &impl PaymentGateway) -> Result<Confirmation, OrderError> {
    let receipt = gateway.charge(order.total)?;
    Ok(Confirmation { receipt_id: receipt.id })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn successful_order_returns_confirmation() {
        let gateway = FakeGateway { should_fail: false };
        let order = Order { total: 5000 };
        let result = process_order(&order, &gateway);
        assert!(result.is_ok());
    }
}
```

**When to use `mockall` in Rust:** Only when the trait has many methods and writing a full fake is tedious. For most cases, a simple test double struct is cleaner and more readable.
