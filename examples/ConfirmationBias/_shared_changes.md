# Shared-changes queue — ConfirmationBias polish run (2026-07-12)

This file records edits to shared-fabric artefacts (`examples/AGENT_POOL/`)
that the ConfirmationBias polish run identified as required but did NOT apply
itself, per the concurrency-safety rule of the polish invocation:

> For AGENT_POOL icon/design.md changes, generate PNG in place if needed but
> write mapping-row additions to `examples/ConfirmationBias/_shared_changes.md`
> for main-session merge. Do NOT edit `examples/AGENT_POOL/agent_images/design.md`
> yourself.

The three PNG files were generated in place under
`examples/AGENT_POOL/agent_images/icons/` because the polish-simulation-pipeline
`§6.3 Part A Step 0` icon-completeness preflight is a hard gate that cannot be
satisfied without the physical asset. The mapping-row additions to
`agent_images/design.md` are queued here for the main session to merge into the
pool-level design ledger.

## 1. Icons already committed to `examples/AGENT_POOL/agent_images/icons/`

| # | Icon PNG filename                     | Agent profile                                  | Notes                          |
|---|---------------------------------------|------------------------------------------------|--------------------------------|
| 1 | `finance-belief-anchor.png`           | `examples/AGENT_POOL/finance/belief-anchor.md` | Generated 2026-07-12, 512x512  |
| 2 | `finance-selective-scanner.png`       | `examples/AGENT_POOL/finance/selective-scanner.md` | Generated 2026-07-12, 512x512 |
| 3 | `finance-balanced-analyst.png`        | `examples/AGENT_POOL/finance/balanced-analyst.md`  | Generated 2026-07-12, 512x512 |

The three pool profiles already carry an `| Icon |` row in their Design
Provenance table (line 52 of each `.md`) that points at the correct relative
path `../agent_images/icons/finance-<stem>.png`; no profile edits are required
by the mapping-row merge below.

## 2. Mapping rows to append to `examples/AGENT_POOL/agent_images/design.md`

Insert the following three rows at the end of the existing mapping table
(after row #32 `finance/value-contrarian.md`). Row numbers assume the current
32-row table; adjust if the table grew between now and merge.

```markdown
| 33 | `finance/belief-anchor.md`                   | `finance-belief-anchor.png`                   | 信念锚定型投资者 | Belief-state compounding under confirming signals → self-reinforcing "+" motif |
| 34 | `finance/selective-scanner.md`               | `finance-selective-scanner.png`               | 选择型投资者     | Selective information search / myside bias → magnifier-with-highlight motif    |
| 35 | `finance/balanced-analyst.md`                | `finance-balanced-analyst.png`                | 均衡分析型投资者 | Rational Bayesian evidence weighing → equal-armed balance-scale motif          |
```

Additionally, append a dated `## Notes` bullet immediately after the existing
`2026-07-12` bullet (currently the last note):

```markdown
- 2026-07-12: Mapping rows #33–#35 added for the ConfirmationBias scenario
  archetypes (belief-anchor, selective-scanner, balanced-analyst). PNGs were
  generated fresh in this session; the mapping-row gap was closed as part of
  the polish-simulation-pipeline Step 2 icon-resolution sub-gate.
```

Also update the "Icons are 32 total" line in the `## Notes` section to read
"Icons are 35 total".

## 3. Why this queue exists

The ConfirmationBias polish run is a concurrent worker. The main session owns
`examples/AGENT_POOL/agent_images/design.md` and merges shared-fabric edits
from all polish workers to keep row numbering monotonic and avoid
merge-conflict rework. The icon PNGs themselves are safe to commit from a
worker because filename collisions between concurrent workers are prevented
by the domain-prefix convention (`finance-<stem>.png` where `<stem>` uniquely
identifies the archetype).

## 4. Verification after merge

After the main session merges the three rows and the `Notes` bullet:

- `grep -c '^| ' examples/AGENT_POOL/agent_images/design.md` should equal
  35 mapping rows + 1 header row = 36 (or 35 + 1 = 36 total pipe-prefixed lines
  inside the table).
- `git diff --stat examples/AGENT_POOL/agent_images/design.md` should show
  ~4 insertions (three table rows + one Notes bullet).
