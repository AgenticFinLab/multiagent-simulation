# EuropeanDebtCrisis RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether embedded threshold rules preserve Rule baseline crisis dynamics while adding LLM quantity adaptability. Key questions:
- Does rule embedding maintain CDI and CD within Rule baseline range?
- Does LLM quantity adaptation within thresholds affect IER or SRT?
- How does RuleLLM sit between Rule (stable) and LLM (variable) on all metrics?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                     | analysis-bases.md ref |
|----------------------------------------|------------------------------------------------------------------------------|-----------------------|
| Crisis Depth Index (CDI)               | `crisis_depth_index(price_history, fundamental)`                             | §2.1                  |
| Crisis Duration (CD)                   | `crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`        | §2.2                  |
| Amplification Ratio (AR)               | `amplification_ratio(creditor_sell_volume, periphery_sell_volume)`           | §2.3                  |
| Intervention Effectiveness Ratio (IER) | `intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`            | §2.4                  |
| Spread Recovery Time (SRT)             | `spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)` | §2.5                  |
| Arbitrage Profit Rate (APR)            | `arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`               | §2.6                  |

## §3 RuleLLM-Specific Notes

- **RuleLLMPeripheryBondSeller (§4.1)**: Sell threshold is locked — crisis onset timing identical to Rule; LLM only adjusts quantity per round
- **RuleLLMCreditorPanicker (§4.2)**: Panic threshold locked — doom loop second wave timing matches Rule; AR bounded
- **RuleLLMCoreBondBuyer (§4.3)**: Flight threshold locked; LLM may adjust quantity upward in deep crises — slightly better CDI floor than Rule
- **RuleLLMECBIntervenor (§4.4)**: Intervention threshold locked; LLM may buy more aggressively within bound — IER similar to Rule; SRT may be shorter
- **RuleLLMHedgedFund (§4.5)**: Entry threshold locked; LLM adaptive sizing within 0–500 — APR may be slightly different from Rule
- **vs. LLM**: CDI and CD range narrower; AR lower upper bound; more stable crisis trajectory

## §4 Expected Ranges

| Metric | RuleLLM Expected Range | vs. Rule Baseline | vs. LLM Baseline         |
|--------|------------------------|-------------------|--------------------------|
| CDI    | 0.14–0.32              | Within ±5%        | Much narrower range      |
| CD     | 10–28 rounds           | Within ±10%       | Much shorter upper bound |
| AR     | 0.8–1.4                | Within ±5%        | Lower upper bound        |
| IER    | 0.72–0.95              | Within ±5%        | Higher floor             |
| SRT    | 4–18 rounds            | Within ±15%       | Narrower range           |
| APR    | 0.04–0.22              | Similar           | Similar                  |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.
