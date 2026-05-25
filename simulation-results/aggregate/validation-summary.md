# Validation Summary

This report summarizes Level-3 scenario-validity checks extracted from each
sample's `artifacts/analysis/summary.json`.

Important interpretation:

- `scenario_validity_fail` means an analysis target or calibration criterion was
  not satisfied for that completed sample.
- It does not mean the simulation crashed, analysis failed, or the resource-pack
  sample is missing.
- Do not mechanically rerun a `scenario_validity_fail` row. First inspect the
  scenario documentation, analysis target, and observed metrics.

## Files

- `validation-overall.csv`: one row per sample.
- `validation-criteria.csv`: one row per reported validation criterion.
- `validation-summary.csv`: combined machine-readable table with `row_type`.

## Overall Rows

| Status | Count |
|---|---:|
| true | 147 |
| false | 33 |
| not_reported | 0 |

## Criteria Rows

| Status | Count |
|---|---:|
| true | 486 |
| false | 123 |
| not_reported | 64 |

## Overall Status by Mechanism

| Mechanism | true | false | not_reported |
|---|---:|---:|---:|
| Rule | 38 | 7 | 0 |
| LLM | 36 | 9 | 0 |
| RuleLLM | 37 | 8 | 0 |
| Rag | 36 | 9 | 0 |

## Samples With Overall Scenario-Validity Failures

| Scenario | Mechanisms |
|---|---|
| AnchoringEffect | Rag |
| ArchegosCollapse | Rule, LLM, RuleLLM, Rag |
| AsianFinancialCrisis | Rule, LLM, RuleLLM, Rag |
| AvailabilityBias | LLM, Rag |
| BlackMonday1987 | RuleLLM, Rag |
| CarryTradeUnwind | Rule, LLM, RuleLLM |
| ConfirmationBias | Rule, LLM, RuleLLM, Rag |
| CreditCycle | Rule, LLM, RuleLLM, Rag |
| CurrencyCrisis | Rule, LLM, RuleLLM, Rag |
| DispositionEffect | LLM |
| LTCMCollapse | Rule, LLM, RuleLLM, Rag |
