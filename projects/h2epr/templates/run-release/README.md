# Run release template

A tracked run release is a compact index into ignored custody. Include:

- `README.md` with exact commands and claim boundary;
- `run-manifest.json`;
- `run-receipt.json`;
- `determinism-receipt.json` for deterministic backends, or a model provenance
  receipt for model backends;
- generated-identity conformance and any cross-event contract receipt; and
- `SHA256SUMS`.

Pin package, manifest, binding, realization, shared and backend configurations,
seed/model settings, H2EPR runtime, MASim kernel, trace, state, seals, replay,
Generated EPG, counts, unresolved transport, and custody locator. Large bytes
remain ignored and reproducible.

For current Rule, materializations A and B use fresh directories but the same
logical custody locator so all eight scientific outputs and `run-receipt.json`
can be byte-identical. The determinism receipt hash-links the independently
derived identity-conformance receipt. The run receipt records the ignored
custody locator and inventory hash, exact trace coverage, and zero unresolved
transport.
The current run receipt also reports independently rederived outcome
assessments. These may be false in a valid release. Failed-attempt receipts and
partial state are diagnostic custody, not substitutes for a run release.

Publish only from three already sealed custody roots:

```bash
PYTHONPATH=projects/h2epr/src python -B -m h2epr.cli publish-run-release \
  --data-root data/h2epr \
  --package projects/h2epr/events/<event-slug>/package \
  --canonical <materialization-a> --repeat <materialization-b> \
  --probe <identity-probe> \
  --release projects/h2epr/releases/<event-slug>/rule \
  --title "<event title>" \
  --simulation-reading-link ../../../reports/<event-slug>/rule/simulation-reading.md
```

The publisher refuses an existing release root and fails on schema, self-hash,
package, binding, source-inventory, custody, semantic lineage, replay,
independent graph compilation, transport, A/B, or generated-identity drift.
For deterministic Rule, publication also rematerializes canonical, repeat, and
identity-probe variants in temporary custody and requires exact output and
receipt bytes. Recomputed producer seals or outer checksums do not replace this
independent reproduction gate.
