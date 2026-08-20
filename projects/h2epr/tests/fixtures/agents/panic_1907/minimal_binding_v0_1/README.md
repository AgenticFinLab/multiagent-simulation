# Panic of 1907 minimal binding engineering baseline

This frozen fixture preserves the `0.1.0-dev` two-role Definitions and their deterministic three-tick binding.
It verifies fail-closed Definition hashes, observation and intent envelopes, request/result separation, trace
integrity, and replay. It does not implement or validate the current `0.2.0` reference Definitions.

## Fixture contents

| File | SHA-256 |
|---|---|
| `knickerbocker-trust.md` | `6929b1fe29ae1f618dabe0e552b9d0dfe6d42462e8b66570df07680e9fe3ff05` |
| `new-york-clearing-house.md` | `0f7452c71c2c07269dc8b605dcbe30d77eb6736560212cd81dfaf96dc6eec66d` |
| `evidence-ledger.md` | `3f8489aff5f46a48ede934a291cdb6bd4c886cbf3abdfd2481756bad42d76af7` |
| `micro-situation.md` | `604d6085fd51aa3c6e5b1f59dbce830e5ecbec7eee2fb538bbd9c4e71ff76974` |
| relocated `binding-catalog.json` | `456cfe761a9b120110c20fc54aa39a2aa0217aec46225714725935471a6c8b2a` |

The binding catalog originally had SHA-256
`1c6d12f21b88ecae8de1dd3b2de90de4f4821a41b47442692fc3140fc52458fa`; relocation changed only its four
repository-relative asset locators. The four referenced Markdown hashes remain unchanged.

The corresponding implementation is `h2epr.agents.panic_1907_baseline`, and its dedicated tests are in
`tests/agents/test_panic_1907_agent_baseline.py`. Changes are limited to correcting a defect in the fixture or
its verification. Current Agent research and behavior changes belong only at `agents/defines/panic_1907/`.
