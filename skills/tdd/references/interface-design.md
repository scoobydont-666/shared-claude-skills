# Interface Design for Testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, don't produce side effects**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area**
   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup

4. **Rust: Traits as seams**

   ```rust
   // Testable — trait defines the boundary
   trait Storage {
       fn save(&self, key: &str, value: &[u8]) -> Result<(), StorageError>;
       fn load(&self, key: &str) -> Result<Vec<u8>, StorageError>;
   }

   fn process_data(input: &[u8], store: &impl Storage) -> Result<Summary, AppError> {
       let result = transform(input);
       store.save("latest", &result)?;
       Ok(Summary { size: result.len() })
   }

   // Test: no disk, no network
   #[cfg(test)]
   struct InMemoryStorage(std::cell::RefCell<std::collections::HashMap<String, Vec<u8>>>);
   ```

   ```rust
   // Testable — return values over side effects
   fn calculate_tax(income: Decimal, deductions: &[Deduction]) -> TaxResult {
       // Pure computation, trivially testable
   }

   // Hard to test — side effect buried inside
   fn process_return(income: Decimal, deductions: &[Deduction], db: &PgPool) {
       let tax = /* compute */;
       db.execute("INSERT INTO returns ...").unwrap(); // side effect
   }
   ```
