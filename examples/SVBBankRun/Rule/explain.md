# SVBBankRun Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Deterministic proxy-market formulas. |
| Key Difference from Other Variants | No API calls; all agent actions follow configured thresholds. |
| Primary Research Contribution | Establishes the baseline bank-health proxy run dynamics. |
| Files | `players.py`, `run_svbbankrun.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Depositor -> `simulation-bases.md §4.1` | `Depositor._make_decision()` sells proxy units when `deviation < -extras["withdrawal_threshold"]`. |
| SocialMediaInfluencer -> `simulation-bases.md §4.2` | `SocialMediaInfluencer._make_decision()` scales sell pressure by `extras["amplification_factor"]`. |
| BankManager -> `simulation-bases.md §4.3` | `BankManager._make_decision()` buys up to 500 units when deviation is below -5%. |
| Regulator -> `simulation-bases.md §4.4` | `Regulator._make_decision()` probabilistically buys `2000` units below `intervention_threshold`. |
| BondTrader -> `simulation-bases.md §4.5` | `BondTrader._make_decision()` trades up to 500 units when absolute deviation exceeds 3%. |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

`Market.decide()` computes `net_demand`, applies `price_impact`, `mean_reversion`,
and Gaussian `noise_std`, then broadcasts `price`, `fundamental`, `deviation`,
`volume`, and `net_demand`.

## §4 Variant-Specific Features

The Rule variant uses direct config parameters from
`configs/SVBBankRun/Rule/players.yml`. It is the only variant with no LLM parser,
fallback, or RAG retrieval path.

## §5 Architecture Diagram

```text
Market -> market_update -> Depositor / Influencer / Manager / Regulator / BondTrader
Agents -> investor_order(action, quantity, agent_type) -> Market
```

## §6 Configuration Contract

| Component | Config |
|---|---|
| Market | `initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std` |
| Depositor | `initial_cash`, `initial_position`, `withdrawal_threshold` |
| SocialMediaInfluencer | `initial_cash`, `initial_position`, `amplification_factor` |
| BankManager | `initial_cash`, `initial_position`, `duration_gap` |
| Regulator | `initial_cash`, `initial_position`, `intervention_threshold`, `guarantee_probability` |
| BondTrader | `initial_cash`, `initial_position`, `yield_sensitivity`, `position_size` |

## §7 Run Command

```bash
python examples/SVBBankRun/Rule/run_svbbankrun.py -c configs/SVBBankRun/Rule/simulation.yml
```

## §8 Validation Checklist

- Orders contain `action`, `quantity`, and `agent_type`.
- Market records 200 rounds for full experiments.
- Rule analysis writes `summary.json` and four fixed PNG outputs.

## §9 Expected Variant Behavior

The Rule variant should show deterministic threshold-driven run pressure:
depositor and influencer sell pressure increases after negative bank-health
deviation, while manager and regulator support appears only under stress.
