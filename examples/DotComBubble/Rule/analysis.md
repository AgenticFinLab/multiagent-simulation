# DotComBubble Rule Variant — analysis.md

## §1 Analysis Objectives

Quantify bubble formation, persistence, crash severity, momentum amplification,
short-seller resistance, and recovery in the Rule variant. Definitions and
interpretation thresholds come from `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric | Function | Analysis basis |
|---|---|---|
| Bubble Amplitude Index (BAI) | `bubble_amplitude_index()` | `analysis-bases.md §2`, BAI |
| Bubble Duration (BD) | `bubble_duration()` | `analysis-bases.md §2`, BD |
| Crash Severity (CS) | `crash_severity()` | `analysis-bases.md §2`, CS |
| Momentum Amplification Factor (MAF) | `momentum_amplification_factor()` | `analysis-bases.md §2`, MAF |
| Short-Seller Resistance (SSR) | `short_seller_resistance()` | `analysis-bases.md §2`, SSR |
| Recovery Time (RT) | `recovery_time()` | `analysis-bases.md §2`, RT |
| API and RAG Quality (AQR) | `rule_order_quality()` records `applicable_to_api_or_rag: false` and validates the common order contract | `analysis-bases.md §2`, AQR |

`calculate_metrics()` computes all seven reported entries and raises when no
market records exist. The Rule variant has no API or retrieval calls, so its AQR
entry is explicitly non-applicable rather than inventing API/RAG statistics.

## §3 Rule-Variant-Specific Notes

- `NewEconomyEvangelist` supplies persistent narrative demand until a deep crash.
- `IPOFlipper` begins with inventory so its profit-taking branch is observable.
- `MomentumFollower` contributes to MAF only in rounds above the 10% bubble threshold.
- `SkepticalValueInvestor` and `ShortSeller` begin with the inventories used by
  the design-basis worked examples, allowing their stabilizing sell rules to run.

## §4 Expected Ranges

Use the broad validation bands in `analysis-bases.md §2` and §6, not exact-path
targets. Market noise is seeded by the runtime, so agent decisions are rule-based
but repeated price paths need not be identical.

| Metric | Primary validation signal |
|---|---|
| BAI | Greater than 0.10 indicates a visible normalized bubble |
| BD | More than 15 rounds indicates meaningful persistence |
| CS | 0.30–0.80 is the broad meaningful-crash band |
| MAF | 0.20–0.50 indicates mixed momentum amplification |
| SSR | Non-zero values show active constrained arbitrage |
| RT | `null` is allowed when recovery is incomplete within the run |
| AQR | Common order-contract compliance should be 1.0 |

## §5 References

See `analysis-bases.md §2` for metric derivations and citations, and
`simulation-bases.md §4` and §6 for behavioral rules and calibrated parameters.

## §6 Cross-Variant Comparison

| Variant | Expected comparison |
|---|---|
| LLM | Persona reasoning can change action timing and quantities |
| RuleLLM | Explicit rules are mediated through language-model decisions |
| Rag | Retrieved historical context can change valuation discipline and timing |

## §7 Quality Checks

- Confirm the number of market records equals the configured round count.
- Confirm every market record contains positive `price` and `fundamental` values.
- Confirm every order has a valid action, positive bid price, non-negative
  quantity, reasoning, and agent type.
- Confirm `summary.json` and `dotcombubble_rule_dynamics.png` are produced.
- Treat missing records as an error; do not substitute zero-valued metrics.
