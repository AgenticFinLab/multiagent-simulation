# EuropeanDebtCrisis LLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether LLM persona-driven crisis reasoning produces more or less severe crises than Rule. Key questions:
- Do LLM personas generate more realistic self-fulfilling spiral dynamics (earlier onset, sharper CDI)?
- Does LLM ECB intervention more authentically model the "whatever it takes" credibility effect?
- Does LLM stochasticity amplify or compress crisis variability?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                     | analysis-bases.md ref |
|----------------------------------------|------------------------------------------------------------------------------|-----------------------|
| Crisis Depth Index (CDI)               | `crisis_depth_index(price_history, fundamental)`                             | §2.1                  |
| Crisis Duration (CD)                   | `crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`        | §2.2                  |
| Amplification Ratio (AR)               | `amplification_ratio(creditor_sell_volume, periphery_sell_volume)`           | §2.3                  |
| Intervention Effectiveness Ratio (IER) | `intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`            | §2.4                  |
| Spread Recovery Time (SRT)             | `spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)` | §2.5                  |
| Arbitrage Profit Rate (APR)            | `arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`               | §2.6                  |

## §3 LLM-Specific Notes

- **LLMPeripheryBondSeller (§4.1)**: LLM may panic at different deviation levels each run — CDI variance is higher; may produce both more and less severe crises than Rule
- **LLMCreditorPanicker (§4.2)**: LLM models banking system contagion narrative; may amplify more aggressively if prompt generates fear narrative — AR upper bound higher than Rule
- **LLMCoreBondBuyer (§4.3)**: LLM flight-to-safety may be more responsive to narrative; provides variable counter-cyclical buying
- **LLMECBIntervenor (§4.4)**: LLM models Draghi commitment; may activate earlier and more aggressively — IER may exceed Rule in some runs, underperform in others
- **LLMHedgedFund (§4.5)**: LLM models limits-to-arbitrage caution; may withdraw at extreme crisis intensity — APR lower than Rule in severe runs
- **vs. Rule**: CDI range wider; CD range wider; both tails (better and worse crisis outcomes) are possible

## §4 Expected Ranges

| Metric | LLM Expected Range | vs. Rule Baseline                      |
|--------|--------------------|----------------------------------------|
| CDI    | 0.10–0.45          | Wider range                            |
| CD     | 5–40 rounds        | Much wider range                       |
| AR     | 0.5–2.0            | Higher upper bound                     |
| IER    | 0.50–1.00          | Higher ceiling but lower floor         |
| SRT    | 3–25 rounds        | More variable                          |
| APR    | 0.00–0.25          | Lower floor (LLM exits at crisis peak) |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.
