# CurrencyCrisis Rule Variant — analysis.md

## §1 Metrics and Functions

| Metric                                      | Function                                                                      | analysis-bases.md Ref |
|---------------------------------------------|-------------------------------------------------------------------------------|-----------------------|
| Attack Intensity Index (AII)                | `attack_intensity_index(price_history, fundamental)`                          | §2.1                  |
| Peg Survival Duration (PSD)                 | `peg_survival_duration(price_history, fundamental, breach_threshold=-0.05)`   | §2.2                  |
| Defense Exhaustion Rate (DER)               | `defense_exhaustion_rate(defender_cash_history, initial_cash, crisis_rounds)` | §2.3                  |
| Self-Fulfilling Amplification Factor (SFAF) | `self_fulfilling_amplification_factor(agent_volume_by_type)`                  | §2.4                  |
| Fundamental Anchor Strength (FAS)           | `fundamental_anchor_strength(hedger_orders, attack_phase_rounds)`             | §2.5                  |
| Recovery Speed (RS)                         | `recovery_speed(price_history, fundamental, recovery_threshold=0.03)`         | §2.6                  |
| Wealth Transfer Index (WTI)                 | `wealth_transfer_index(agent_final_states, final_price, initial_wealth)`      | §2.7                  |

## §2 Rule Variant Notes

**Analysis script**: `CurrencyCrisis/Rule/analysis.py`

The Rule variant produces fully deterministic outputs for a given random seed. Key variant-specific analysis notes:

- **AII determinism**: SpeculativeAttacker's scaled sell `qty × (1 + |δ| × 10)` means AII is determined mechanically; minimal run-to-run variance (noise term only).
- **PSD precision**: Peg breach is triggered at exact δ = −0.05 threshold; PSD is predictable from parameter settings.
- **SFAF baseline**: Rule variant provides the mechanical SFAF baseline (expected ≈ 0.6–0.9) against which LLM coordination amplification is measured.
- **DER regularity**: Two-tier defense (600/1000 units) produces step-function DER; useful for calibrating reserve sufficiency.
- **WTI near-zero design**: Rule symmetric design means neither side dominates; deviations from zero indicate parameter imbalance.

## §3 Output Files

Rule variant produces the following output files in `outputs/CurrencyCrisis/Rule/`:

| File                   | Content                                   |
|------------------------|-------------------------------------------|
| `price_history.csv`    | Round-by-round price and deviation        |
| `agent_orders.csv`     | Per-agent order action, quantity, round   |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round |
| `metrics_summary.json` | AII, PSD, DER, SFAF, FAS, RS, WTI         |

## §4 Phase Attribution

For each attack event (δ < −0.03), compute per-agent sell and buy contribution:

```python
attack_sellers = {
    "SpeculativeAttacker": sum_sell_volume_during_attack,
    "SelfFulfillingTrader": sum_sell_volume_during_attack,
}
attack_buyers = {
    "CentralBankDefender": sum_buy_volume_during_attack,
    "FundamentalHedger": sum_buy_volume_during_attack,
}
```

SFAF is computed as `attack_sellers["SelfFulfillingTrader"] / attack_sellers["SpeculativeAttacker"]` (analysis-bases.md §2.4).  
FAS is computed from `attack_buyers["FundamentalHedger"]` active rounds fraction (analysis-bases.md §2.5).

## §5 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
