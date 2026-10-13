# Property-Based Testing Libraries

Prefer the library already used by the repository. Check its installed version
and official documentation before adding dependencies or copying an API example.
Pin dependencies using the project's normal lockfile and review update changes.

| Ecosystem | Library | Official documentation |
|---|---|---|
| Python | Hypothesis | https://hypothesis.readthedocs.io/ |
| JavaScript / TypeScript | fast-check | https://fast-check.dev/docs/ |
| Rust | proptest | https://proptest-rs.github.io/proptest/ |
| Go | rapid | https://github.com/flyingmutant/rapid |
| JVM | jqwik | https://jqwik.net/docs/current/user-guide.html |
| Solidity | Echidna | https://secure-contracts.com/program-analysis/echidna/ |

Set explicit size and runtime bounds, understand the framework's shrinking and
replay behavior, and preserve the smallest failing input. Reset state between
generated examples; an ordinary test fixture may have a different lifetime than
each individual generated case.

For smart contracts, define non-vacuous state invariants: conservation subject to
explicit mint/burn rules, authorization, and accounting over the modeled actors.
Checking that an unsigned supply is nonnegative proves nothing. Decide which
external contracts are modeled and isolate the harness from live funds or networks.
