# Simulation-180 Summary

## Counts

- Scenarios: 45
- Samples: 180
- Runtime accepted: 180
- Analysis complete: 180
- Analysis PNG files: 771

## By Mechanism

| Mechanism | Samples |
|---|---:|
| Rule | 45 |
| LLM | 45 |
| RuleLLM | 45 |
| Rag | 45 |

## Quality Acceptance

| Status | Samples |
|---|---:|
| accepted | 180 |

All tracked samples are accepted into the GitHub-facing result package. Detailed
non-blocking retry and parser diagnostics are retained as counters in
`quality/quality-ledger.csv`. Non-blocking triage labels are intentionally kept
out of this GitHub-facing package.

## Scenario-Validity Validation

These are Level-3 analysis targets, not runtime acceptance gates.

| Row Type | true | false | not_reported |
|---|---:|---:|---:|
| overall samples | 147 | 33 | 0 |
| criteria rows | 486 | 123 | 64 |

See `aggregate/validation-summary.md`, `aggregate/validation-overall.csv`, and
`aggregate/validation-criteria.csv` for details.
