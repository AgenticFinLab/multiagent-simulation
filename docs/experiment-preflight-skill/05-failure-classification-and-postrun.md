# Failure Classification and Post-Run Review

## Purpose

Use this file after a row fails or after a batch finishes. It separates
root-cause classification from source repair and keeps runner `SUCCESS` from
being treated as final sample acceptance without quality review.

## Failure Classification Before Fixing

When a row fails, classify first:

| Evidence | Class | Action |
|---|---|---|
| `KeyError`, unresolved prompt, unsupported config field | config/contract bug | fix source and rerun clean |
| malformed LLM output without decision JSON | prompt/parser/API-output contract | strengthen contract or scenario-local counted fallback |
| auth/quota/account overdue | API contamination | restore provider state and rerun affected rows |
| `SIGABRT`, thread resource error, Ray OOM | runtime resource | reduce concurrency/thread caps |
| no round progress inside stall window | stall | preserve logs and inspect setup/runtime boundary |
| extreme price/NaN/inf with exit 0 | quality risk | do Level-2 quality review; do not call it a code success issue |

Do not patch strategy, persona, or market logic just to make a row finish
unless the root cause is proven to be a bug rather than intended scenario
dynamics.

## Post-Run Minimum Review

After a batch completes:

- Copy only `SUCCESS` rows with complete isolated artifacts into the resource
  pack.
- Rebuild the success ledger.
- For failed rows, record status, exit code, duration, max round, first
  actionable error, and classification.
- For success rows, later run Level-2 checks for round count, structural fields,
  fallback rate, price/volume/portfolio sanity, and RAG retrieval health.
- Treat runner `SUCCESS` as provisional if logs contain Ray unhandled errors,
  tracebacks, fatal/native abort text, or heavy parser fallback. Such rows
  should stay out of the resource pack until repaired and rerun.
