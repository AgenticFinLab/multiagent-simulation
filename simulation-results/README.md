# Simulation Results

This directory is the lightweight Git-tracked index for the
`example-standardization` 180-sample experiment set:

- 45 financial scenarios
- 4 mechanisms per scenario: Rule, LLM, RuleLLM, Rag
- 180 full configured-round runtime successes
- 180 Level-2 audited samples
- 180 analysis-complete samples
- 45 RAG samples with `rag_stats.json`

The Git-tracked package is analysis-ready and metadata-complete, but it is not
the complete runtime artifact bundle. To keep the repository maintainable, this
directory intentionally omits large runtime and presentation artifacts:
`records/`, `communication/`, `monitoring/`, `checkpoints/`, `logs/`, and
analysis PNG figures.

The complete resource pack is distributed as a GitHub Release asset:

```text
https://github.com/AgenticFinLab/multiagent-simulation/releases/tag/simulation-results-v1
```

Download these two files from the release:

```text
simulation-180-standardized-resource-pack.tar.zst
simulation-180-standardized-resource-pack.tar.zst.sha256
```

Archive SHA256:

```text
327a4c55d5e03ad338b5009f7a380b8ba7e12fa522ae07f7502d6ab47b5c05a7
```

See `RESOURCE_PACK_EXTERNAL.md` for the full resource-pack publication and
verification details.

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

The full release archive expands to:

```text
resource-pack/
  samples/<Scenario>/<Mode>/
    logs/
    artifacts/analysis/*.png
    artifacts/records/
    artifacts/communication/
    artifacts/monitoring/
    artifacts/checkpoints/
    ...same metadata/config files as the lightweight package
```

Aggregate validation files:

- `aggregate/validation-overall.csv`: one Level-3 scenario-validity row per
  sample.
- `aggregate/validation-criteria.csv`: per-criterion validation rows.
- `aggregate/validation-summary.csv`: combined machine-readable table.
- `aggregate/validation-summary.md`: human-readable interpretation and counts.

## Verification

Verify the lightweight Git-tracked package:

```bash
python simulation-results/scripts/verify_tracked_results.py
```

Verify the downloaded full resource-pack:

```bash
sha256sum -c simulation-180-standardized-resource-pack.tar.zst.sha256
tar --zstd -xf simulation-180-standardized-resource-pack.tar.zst
python simulation-results/scripts/verify_full_resource_pack.py \
  --resource-pack resource-pack
```

Operational execution plans, machine-specific notes, credentials, and raw
incoming runs are not part of the tracked result package.
