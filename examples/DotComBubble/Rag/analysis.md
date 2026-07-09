# DotComBubble Rag — Analysis Documentation

## 1. Overview

The analysis tests whether retrieved dot-com evidence changes bubble formation,
crash dynamics, stabilising behavior, and data quality relative to Rule, LLM,
and RuleLLM. `analysis.py` is self-contained and implements every metric in
`analysis-bases.md §2`.

## 2. Metric Implementation

| Metric | Function | Required inputs | Edge behavior |
|---|---|---|---|
| BAI | `bubble_amplitude_index()` | price path, positive fundamental | raises on empty prices or invalid fundamental |
| BD | `bubble_duration()` | price path, fundamental, 10% threshold | raises on invalid fundamental |
| CS | `crash_severity()` | price path | raises on empty prices |
| MAF | `momentum_amplification_factor()` | agent orders, bubble rounds | returns `0.0` when bubble buy volume is zero |
| SSR | `short_seller_resistance()` | short-seller orders, overvaluation rounds | returns `0.0` when no rounds qualify |
| RT | `recovery_time()` | price path, fundamental, 10% band | returns `None` when recovery is not observed |
| AQR | `api_and_rag_quality()` | orders and recorded `rag_context` | reports zero-rate diagnostics for empty samples |

AQR uses the runtime `_RAG_FALLBACK` constant, so retrieval failures cannot
drift into a differently spelled analysis marker. Per-agent retrieval counts
are also emitted by `analyze_rag_knowledge_effect()`.

## 3. Dimension-by-Dimension Analysis

| Dimension | Metrics / evidence | Question |
|---|---|---|
| Bubble formation | BAI, BD | Did retrieved evidence moderate or amplify overvaluation? |
| Crash and recovery | CS, RT | Did the peak unwind more sharply, and was recovery observed? |
| Agent mechanism | MAF, SSR | Did momentum demand and short-seller resistance behave as designed? |
| Run validity | AQR, `rag_stats.json` | Were decisions valid and retrieval rounds auditable? |

Interpret economic metrics only after the run-validity checks pass.

## 4. Variant-Specific Observable Phenomena

Compare RAG-context content and retrieval failures with the same-round order.
In particular, inspect whether crash-history retrieval precedes lower narrative
or momentum demand, and whether limits-to-arbitrage retrieval precedes sustained
short-seller activity. These are empirical comparisons; the implementation does
not assert that retrieval must improve outcomes.

## 5. Scaling and Sensitivity Analysis

- Repeat runs with controlled seeds before comparing means across variants.
- Keep market parameters and agent counts fixed for marginal RAG comparisons.
- Vary `top_k`, chunk size, and chunk overlap one at a time.
- Report 200-round full experiments; short runs are smoke tests only.
- Treat BAI above `2.0`, CS above `0.90`, absent `rag_stats.json`, or material
  decision-contract failure as review triggers per `analysis-bases.md §6`.

## 6. Output Files Reference

| Output | Producer | Contents |
|---|---|---|
| `summary.json` | `main()` | BAI, BD, CS, MAF, SSR, RT, AQR |
| `rag_stats.json` | `main()` | per-agent and aggregate retrieval coverage |
| `dotcombubble_rag_dynamics.png` | `create_visualizations()` | price and fundamental paths |

The default output directory is `EXPERIMENT/DotComBubble/Rag/analysis` and can
be changed with `--output-dir`.

## 7. Cross-Variant Comparison Notes

| Comparison | Interpretation |
|---|---|
| Rag vs Rule | Combined effect of LLM reasoning and retrieval versus fixed rules |
| Rag vs LLM | Marginal effect of explicit rules plus retrieved context |
| Rag vs RuleLLM | Marginal effect of retrieval with prompts otherwise aligned |

Use identical market calibration, horizon, roster, and replication count. AQR
has no Rule analogue; report it as a validity gate for model-consulting runs.
