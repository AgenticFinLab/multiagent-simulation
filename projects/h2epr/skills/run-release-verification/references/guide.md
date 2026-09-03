# Run and release verification guide

## Custody boundary

Raw outputs live beneath one ignored, event/backend/run-specific custody root.
Never overwrite a prior attempt. Record a logical custody locator in the run
manifest; absolute machine paths are operational metadata, not portable
identity. A failed attempt remains preserved with its terminal disposition.

For deterministic Rule, prepare three fresh roots:

- canonical materialization A;
- same-input materialization B;
- opaque generated-identity probe.

Do not derive B or the probe by copying A.

## Coordinate and trace invariants

At every logical coordinate require one sealed prestate, complete active-actor
observation and decision coverage, typed action/message intents, environment
dispositions, authoritative deltas, due-message transitions, annotations, a
tick seal, and the configured barrier order. Record hashes form one append-only
chain. The run seal commits the terminal state and final preseal record.

No message lifecycle may remain nonterminal at closeout. A deliberately open
domain state is permitted only when the Scenario termination contract allows
it; transport openness is not.

## Independent verification

1. Rebuild the run manifest from package, seed, identity variant, H2EPR source
   inventory, and MASim kernel inventory.
2. Recompute every record hash, previous-hash link, tick seal, run seal, output
   hash, count map, and coordinate summary.
3. Replay authoritative deltas from opening state and require exact terminal
   bytes.
4. Rebuild the Generated EPG from trace only. Require one first-class node per
   trace record, exact trace-ID coverage, valid endpoints, source-trace hash,
   and graph seal.
5. Reproduce deterministic roots independently and compare every scientific
   output plus run receipt byte for byte.
6. Compare the identity probe semantically while requiring opaque generated
   identities to differ where intended.

Outer checksums or producer `passed` fields never replace these derivations.

## Tamper cases

Rewrap each mutation with valid outer self-hashes and confirm failure: run
manifest parent drift, one trace payload/hash-chain change, tick/run seal
change, replay receipt lie, final-state change, coordinate/count summary lie,
Generated EPG missing/duplicated trace reference, graph endpoint change,
custody inventory mismatch, unresolved message, and H2EPR/MASim source drift.

## Publication, completion evidence, and disposition

The tracked release is a compact index: README, run manifest/receipt,
repeatability or model-provenance receipt, identity-conformance receipt where
applicable, and SHA-256 inventory. It points to ignored custody and does not
copy the trace or graph into Git.

Report package/binding/configuration/runtime/kernel/run/trace/seal/final/replay/
graph identities; actor/tick/record/node/edge and disposition counts; custody
locator and inventory; A/B and probe results; validation; exposure; claim
boundary; limitations; and next legal action. Any integrity failure returns to
its owning layer and prevents publication.
