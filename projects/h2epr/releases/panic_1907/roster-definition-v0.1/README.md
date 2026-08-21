# Panic of 1907 Roster Definition release v0.1

- Status: accepted semantic release
- Event: `H2EPR-0288`
- Roster: `v0.4`
- Released: 21 August 2026

This release closes the H2EPR-0288 semantic production phase. It pins seven
Agent Definitions, five population models, the event roster and semantic
skeleton, the shared evidence authorities, and five interface preflights.

## What the release establishes

Every roster row now has a reviewed disposition:

- seven individual, institutional or procedural Agent Definitions;
- five heterogeneous-participant population models;
- NYSE and event infrastructure assigned to scenario/environment ownership;
- Treasury public deposits retained as an explicit exogenous resource input;
- one shared source register and claim-level evidence ledger; and
- no concrete Contracts V1 counterexample from the production preflights.

The release is a semantic research input. It is not an executable participant
bundle, a simulation configuration, a historical calibration result or a
scientific-validity claim.

## Files

- [`manifest.json`](manifest.json) records identities, versions, repository-
  relative paths and SHA-256 values.
- [`SHA256SUMS`](SHA256SUMS) verifies the manifest, this README and every
  pinned semantic input from this directory.
- The [research roster](../../../agents/rosters/panic_1907.md) owns event
  membership and dispositions.
- The [semantic skeleton](../../../scenarios/panic_1907/semantic-skeleton.md)
  owns shared event concepts and causal boundaries.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

## Consolidated mapping entry

The next stage starts from this manifest and treats the current two-role
binding as a retained engineering reference, not as the roster-wide mapping.
A consolidated mapping review must, in order:

1. verify release identities and classify every semantic observation, state,
   authority, intent, message, lifecycle, resource and result;
2. compose multiple capabilities under one historical participant identity and
   one authoritative resource/exposure truth;
3. define the shared event lifecycles for support, withdrawal, credit,
   clearing, committee work, resource commitment, call loans and broker
   funding;
4. map role-scoped information and system-only structural variants without
   hidden defaults or cross-role leakage;
5. establish semantic intent registries and cross-object validation for the
   full released roster;
6. re-check V1 carrier fit and document any concrete irreducible
   counterexample before proposing a narrow successor; and
7. select bounded conformance and interaction cases before implementation.

This release does not itself authorize those engineering changes, simulation,
Rule v2, LLM/RAG or a Contract successor.
