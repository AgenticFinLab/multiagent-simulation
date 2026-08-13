# H2EPR contract case specifications v1

This directory contains test-only, declarative inputs for the public Phase-0
contract suite. It is not a runtime fixture, MASim scenario, H2EPR experiment,
public contract schema, or historical audit directory.

The four JSON files hold exactly 255 behavior cases. Each row declares one
explicit semantic condition, local legacy provenance, validation category,
expected result, fixture base, validator subject, and ordered closed-vocabulary
mutation operations. Python adapters load these files with `json` and reject
unknown fields, operations, subjects, duplicate identities, and unsafe paths.

Public case identity uses only the explicit semantic condition, responsibility,
and expected result. Legacy provenance supports the local one-to-one migration
receipt but cannot select a validator or mutation and never appears in the
public validation receipt.

Each `semantic_condition_id` is a concise behavior name, not a serialized
mutation recipe. It states the invariant that is accepted or rejected; the
ordered `operations` remain the executable description of how the synthetic
case exercises that invariant. Names are unique lowercase kebab-case, no more
than 96 characters, and remain stable if legacy IDs, positions, suites, or
source order change.

Public names and identity-bearing descriptor locators exclude audit-round,
suite-count, directive, promotion, timestamp, hash-fragment, and clipped-word
identity. Product and schema-version literals inside frozen mutation payloads
remain behavior data and are not interpreted as public audit identity.
