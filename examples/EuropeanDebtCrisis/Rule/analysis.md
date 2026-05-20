# EuropeanDebtCrisis Rule — Analysis Documentation

## §1 Analysis Objectives

Establish the deterministic baseline for crisis dynamics. Key questions:
- Does the Rule variant produce a self-fulfilling crisis spiral when thresholds are calibrated to historical parameters?
- Is ECBIntervenor's intervention threshold sufficient to halt the spiral?
- How does the doom loop (PeripheryBondSeller + CreditorPanicker) compare to ECB stabilization?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                     | analysis-bases.md ref |
|----------------------------------------|------------------------------------------------------------------------------|-----------------------|
| Crisis Depth Index (CDI)               | `crisis_depth_index(price_history, fundamental)`                             | §2.1                  |
| Crisis Duration (CD)                   | `crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`        | §2.2                  |
| Amplification Ratio (AR)               | `amplification_ratio(creditor_sell_volume, periphery_sell_volume)`           | §2.3                  |
| Intervention Effectiveness Ratio (IER) | `intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`            | §2.4                  |
| Spread Recovery Time (SRT)             | `spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)` | §2.5                  |
| Arbitrage Profit Rate (APR)            | `arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`               | §2.6                  |

## §3 Rule-Specific Notes

- **PeripheryBondSeller (§4.1)**: Fixed sell_threshold means crisis always triggers at the same deviation level; no variability in crisis onset timing
- **CreditorPanicker (§4.2)**: Fixed panic_threshold creates discrete second wave; AR is predictable given parameters; doom loop timing is deterministic
- **CoreBondBuyer (§4.3)**: Partial stabilizer at flight_threshold; contributes consistent buy volume but insufficient alone to prevent crisis
- **ECBIntervenor (§4.4)**: Fixed intervention_threshold determines IER; if threshold is deeper than CDI trough, IER may be low; calibration is critical
- **HedgedFund (§4.5)**: Symmetric entry_threshold means profit depends on whether crisis is deep and sustained; APR higher in longer crises
- **Rule baseline**: All metrics are deterministic given seed; CDI and CD are stable across identical runs

## §4 Expected Ranges

| Metric | Rule Expected Range | Interpretation                                         |
|--------|---------------------|--------------------------------------------------------|
| CDI    | 0.15–0.30           | Crisis reaches 15–30% below fundamental                |
| CD     | 10–25 rounds        | Crisis persists for 10–25 rounds                       |
| AR     | 0.8–1.5             | CreditorPanicker amplifies by 80–150% of initial shock |
| IER    | 0.75–0.95           | ECB covers 75–95% of crisis rounds                     |
| SRT    | 5–15 rounds         | Recovery takes 5–15 rounds after ECB activates         |
| APR    | 0.05–0.20           | HedgedFund earns 5–20% on spread exploitation          |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Cross-Variant Comparison

| Variant | Expected comparison |
|---|---|
| LLM | More variable crisis depth and intervention timing from persona reasoning |
| RuleLLM | Close to Rule because decision thresholds are embedded in the prompt |
| Rag | RuleLLM-like behavior modified by retrieved sovereign-crisis context |

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Confirm price and fundamental histories are present for all rounds.
- Confirm crisis metrics raise on missing records rather than fabricating zeros.
- Confirm order payloads contain valid `action` and numeric `quantity`.
