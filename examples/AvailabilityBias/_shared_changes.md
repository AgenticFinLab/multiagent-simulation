# Shared-changes queue — AvailabilityBias polish run (2026-07-12)

This file records edits to shared-fabric artefacts (`examples/AGENT_POOL/`)
that the AvailabilityBias polish run identified as required but did NOT apply
itself, per the concurrency-safety rule of the polish invocation:

> For AGENT_POOL icon/design.md changes, generate PNG in place if needed but
> write mapping-row additions to `examples/AvailabilityBias/_shared_changes.md`
> for main-session merge. Do NOT edit `examples/AGENT_POOL/agent_images/design.md`
> yourself.

The two PNG files were generated in place under
`examples/AGENT_POOL/agent_images/icons/` because the polish-simulation-pipeline
`§6.3 Part A Step 0` icon-completeness preflight is a hard gate that cannot be
satisfied without the physical asset. The mapping-row additions to
`agent_images/design.md` are queued here for the main session to merge into the
pool-level design ledger.

## 1. Icons already committed to `examples/AGENT_POOL/agent_images/icons/`

| # | Icon PNG filename                              | Agent profile                                              | Notes                          |
|---|------------------------------------------------|------------------------------------------------------------|--------------------------------|
| 1 | `finance-recent-event-overweighter.png`        | `examples/AGENT_POOL/finance/recent-event-overweighter.md` | Generated 2026-07-12, 1024x1024|
| 2 | `finance-media-influenced-trader.png`          | `examples/AGENT_POOL/finance/media-influenced-trader.md`   | Generated 2026-07-12, 1024x1024|

Both pool profiles now carry an `| Icon |` row in their Design Provenance table
pointing at the correct relative path `../agent_images/icons/finance-<stem>.png`;
these two Icon-row edits are inside `examples/AGENT_POOL/finance/` and were
committed by this polish run to satisfy the Step 0 four-check gate (profile
.md ✓ / Icon row ✓ / PNG ✓ / design.md mapping row pending main-session merge).

The three remaining AvailabilityBias-referenced pool profiles
(`rational-updater.md`, `fundamental-analyst.md`, `noise-trader.md`) already
had complete four-check state (Icon row + PNG + design.md mapping rows #17, #7,
#14 respectively) before this run.

## 2. Mapping rows to append to `examples/AGENT_POOL/agent_images/design.md`

Insert the following two rows at the end of the existing mapping table (after
row #32 `finance/value-contrarian.md`). Row numbers assume the current 32-row
table; adjust if the table grew between now and merge (e.g. if the
ConfirmationBias polish run's rows #33–#35 landed first, these become #36–#37).

```markdown
| 33 | `finance/recent-event-overweighter.md`       | `finance-recent-event-overweighter.png`       | 近期事件偏好投资者 | Recency salience / overweighted latest bar → dumbbell-on-recent-bar motif |
| 34 | `finance/media-influenced-trader.md`         | `finance-media-influenced-trader.png`         | 媒体影响投资者     | Media narrative amplification → megaphone-to-price-arrow motif           |
```

Additionally, append a dated `## Notes` bullet immediately after the existing
`2026-07-12` ConfirmationBias bullet (or after the AsianFinancialCrisis bullet
if that is the latest at merge time):

```markdown
- 2026-07-12: Mapping rows #33-#34 (or subsequent numbering after prior worker
  merges) added for the AvailabilityBias scenario archetypes
  (recent-event-overweighter, media-influenced-trader). PNGs were generated
  fresh in this session; the mapping-row gap was closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.
```

Also update the "Icons are 32 total" line in the `## Notes` section to reflect
the new total after all concurrent polish workers merge (e.g. "Icons are 34
total" if only this run merges, or a higher number if concurrent worker rows
land first).

## 3. Why this queue exists

The AvailabilityBias polish run is a concurrent worker. The main session owns
`examples/AGENT_POOL/agent_images/design.md` and merges shared-fabric edits
from all polish workers to keep row numbering monotonic and avoid
merge-conflict rework. The icon PNGs themselves are safe to commit from a
worker because filename collisions between concurrent workers are prevented by
the domain-prefix convention (`finance-<stem>.png` where `<stem>` uniquely
identifies the archetype). The Icon-row edits inside the two pool profile .md
files are also safe from a worker because each profile is single-owner per
archetype.

## 4. Verification after merge

After the main session merges the two rows and the `Notes` bullet:

- `grep -c '^| ' examples/AGENT_POOL/agent_images/design.md` should equal the
  new mapping-row total + 1 (header row).
- `git diff --stat examples/AGENT_POOL/agent_images/design.md` should show
  ~3 insertions (two table rows + one Notes bullet, plus optional Icons-total
  line update).
