# Simulation Results

This package contains the GitHub-facing assets for the
`example-standardization` 180-sample experiment set:

- 45 financial scenarios
- 4 mechanisms per scenario: Rule, LLM, RuleLLM, Rag
- 180 full configured-round runtime successes
- 180 Level-2 audited samples
- 180 analysis-complete samples
- 45 RAG samples with `rag_stats.json`

The tracked package is analysis-ready and metadata-complete. It intentionally
omits large runtime and presentation artifacts from normal Git tracking:
`records/`, `communication/`, `monitoring/`, `checkpoints/`, `logs/`, and
analysis PNG figures. Those omitted artifacts are available in the external
full resource-pack archive documented in `RESOURCE_PACK_EXTERNAL.md`.

Tracked package size at build time: 4946223 bytes.
Omitted raw artifact bytes recorded: 5174599729 bytes.

## Layout

```text
samples/<Scenario>/<Mode>/
  sample.json
  source-results.csv
  config/
  analysis-config/
  artifacts/analysis/summary.json
  artifacts/analysis/rag_stats.json  # Rag only
  runtime-manifest.json
  FULL_ARTIFACTS.md
```

Aggregate validation files:

- `aggregate/validation-overall.csv`: one Level-3 scenario-validity row per
  sample.
- `aggregate/validation-criteria.csv`: per-criterion validation rows.
- `aggregate/validation-summary.csv`: combined machine-readable table.
- `aggregate/validation-summary.md`: human-readable interpretation and counts.

## Verification

```bash
python simulation-results/scripts/verify_tracked_results.py
```

To verify a separately downloaded full resource-pack:

```bash
python simulation-results/scripts/verify_full_resource_pack.py \
  --resource-pack /path/to/resource-pack
```

Operational execution plans, machine-specific notes, credentials, and raw
incoming runs are not part of the tracked result package.
