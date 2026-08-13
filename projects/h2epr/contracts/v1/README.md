# H2EPR contracts V1

This directory is the stable, self-contained contract surface for Phase-0
event-process simulation design.

- `specifications/` explains the scientific and engineering contracts.
- `schemas/catalog.json` lists exactly 28 Draft 2020-12 schemas with stable
  identifiers rooted at
  `https://agenticfinlab.local/h2epr/contracts/v1/schemas/`.
- `../../tests/` resolves every reference offline and replays the retained
  synthetic behavior suite.

The contracts describe artifacts and validators, not a runtime implementation.
An object satisfying JSON Schema may still fail cross-object semantic checks;
an auditable invalid trace may be retained for diagnosis but is ineligible for
compilation or evaluation.

Canonical scientific JSON is UTF-8, NFC-normalized, key-sorted, compact JSON.
Array order is semantic unless a field explicitly defines set semantics.
Operational metadata is excluded only where the relevant hash preimage says so.

