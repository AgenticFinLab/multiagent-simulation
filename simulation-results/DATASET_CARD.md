# Dataset Card: Standardized Simulation-180

## Purpose

This dataset records full configured-round MASim simulations for 45 financial
scenarios under four mechanisms: Rule, LLM, RuleLLM, and Rag.

## Contents

The tracked package includes runtime metadata, isolated configs,
machine-readable analysis outputs, quality ledgers, aggregate metrics, and
checksums. Logs, PNG figures, and raw runtime message/record stores are
excluded from normal Git tracking and distributed through the external full
resource-pack archive.

## Intended Use

- Compare scenario behavior across four mechanisms.
- Inspect completed analysis JSON outputs and validation summaries.
- Reproduce analysis locally from `analysis-config/` and copied artifacts.
- Retrieve full logs, figures, and raw artifacts through the external
  resource-pack archive.

## Limitations

Runner success is not the same as economic validity. Use `summary.json`,
`aggregate/validation-overall.csv`, `aggregate/validation-criteria.csv`, and
scenario documentation when judging whether a scenario reproduces the target
mechanism.
