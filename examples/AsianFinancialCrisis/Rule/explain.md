# AsianFinancialCrisis Rule — Simulation Documentation

## §1 Overview

| Item                      | Description                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------|
| **Variant**               | Rule                                                                                                                |
| **Implements**            | `../simulation-bases.md`                                                                                            |
| **Decision Logic**        | Pure formula-based; all agents use deterministic threshold/signal rules                                             |
| **Key Difference**        | No language model; instant reproducibility; exact threshold triggers; baseline for all cross-variant comparisons    |
| **Research Contribution** | Establishes the theoretical minimum behavioral complexity needed to reproduce Asian-crisis-style contagion dynamics |


## §2 Theory to Implementation Mapping

### HotMoneyFunder: Theory → Implementation Mapping

Theory citation: `simulation-bases.md §4.1`.

| Theory Component         | Implementation                                                                  |
|------------------------------------|---------------------------------------------------------------------------------|
| Hot money reversal at first stress | `if deviation < -reversal_threshold (0.02): sell sell_ratio (0.60) of position` |
| Momentum entry on rising markets   | `if deviation > reversal_threshold (0.02): buy buy_ratio (0.30) of cash`        |
| No loyalty to market or asset      | No position holding logic; aggressive reversal regardless of P&L                |
| Operates with leverage             | `initial_position = 3000` with `initial_cash = 800,000` (financed position)     |

### ContagionTrader: Theory → Implementation Mapping

Theory citation: `simulation-bases.md §4.2`.

| Theory Component        | Implementation                                                                      |
|-----------------------------------|-------------------------------------------------------------------------------------|
| Dual-signal contagion detection   | `signal = contagion_weight × deviation + cross_border_sensitivity × price_return`   |
| Regional crisis front-running     | `if signal < contagion_threshold (-0.025): sell sell_ratio (0.50) of position`      |
| Contagion weight on deviation     | `contagion_weight = 0.60` (deviation dominates cross-market stress signal)          |
| Cross-border momentum sensitivity | `cross_border_sensitivity = 0.40` (price return reflects regional rebalancing flow) |

### IMFRescuer: Theory → Implementation Mapping

Theory citation: `simulation-bases.md §4.3`.

| Theory Component     | Implementation                                                          |
|--------------------------------|-------------------------------------------------------------------------|
| Patient emergency intervention | `if deviation < rescue_threshold (-0.05): buy buy_ratio (0.25) of cash` |
| Deep pockets rescue packages   | `initial_cash = 5,000,000` (largest cash reserve of all agents)         |
| No pre-existing position       | `initial_position = 0.0` — enters only on crisis                        |
| Stabilizing not profit-seeking | No sell logic — holds all bought positions throughout simulation        |

### ValueContrarian: Theory → Implementation Mapping

Theory citation: `simulation-bases.md §4.4`.

| Theory Component | Implementation                                                                     |
|----------------------------|------------------------------------------------------------------------------------|
| Buy deep discounts         | `if deviation < oversold_threshold (-0.08): buy buy_ratio (0.20) of cash`          |
| Sell overbought            | `if deviation > overbought_threshold (+0.10): sell sell_ratio (0.20) of position`  |
| Proportional sizing        | Fixed ratios (0.20/0.20) — conservative, not position-sized to deviation magnitude |

### NoiseTrader: Theory → Implementation Mapping

Theory citation: `simulation-bases.md §4.5`.

| Theory Component | Implementation                                                        |
|----------------------------|-----------------------------------------------------------------------|
| Random uninformed trading  | `if random.random() < trade_probability (0.30): randomly buy or sell` |
| Small position sizes       | `qty = random.randint(100, 500)` — smaller than institutional agents  |


## §3 Market Mechanism Implementation

### Price Formation Formula

`P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε`

*(Full formula derivation: simulation-bases.md §3.1)*

| sim-bases Variable | Python Variable     | Config Path                       | Value |
|--------------------|---------------------|-----------------------------------|-------|
| λ (price impact)   | `price_impact`      | `market.extras.price_impact`      | 0.04  |
| γ (mean reversion) | `mean_reversion`    | `market.extras.mean_reversion`    | 0.02  |
| σ (noise std)      | `noise_std`         | `market.extras.noise_std`         | 0.02  |
| F (fundamental)    | `fundamental_value` | `market.extras.fundamental_value` | 100.0 |
| P(0) (initial)     | `initial_price`     | `market.extras.initial_price`     | 100.0 |

Note: λ = 0.04 is significantly higher than typical developed-market simulations (0.001–0.005), reflecting the thin liquidity of 1997 East Asian currency/equity markets where moderate selling creates large price moves.


## §4 Variant-Specific Features

- **Pure threshold logic**: All agent decisions reduce to threshold comparisons on `deviation` or composite signals; no stochastic behavior beyond NoiseTrader
- **Contagion signal uniqueness**: ContagionTrader is the only agent that uses `prev_price` (for `price_return`); this requires `Market.decide()` to broadcast `prev_price` in addition to other fields
- **Asymmetric intervention size**: IMFRescuer has $5M cash (5–25× other agents) but activates at a deeper threshold than HotMoneyFunder, representing the documented IMF intervention delay
- **Two destabilizing agent pairs**: Both HotMoneyFunder (2 instances) and ContagionTrader (2 instances) are destabilizing; their combined selling dominates early-crisis dynamics


## §5 Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────┐
  │  Market (Rule)                          │
  │  P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε │
  │  Broadcasts: {price, prev_price,        │
  │               fundamental, deviation,   │
  │               volume, round}            │
  └─────────────────┬───────────────────────┘
                    │ market_data (to all)
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
  │HotMoney  │ │Contagion│ │IMF     │ │Value     │
  │Funder×2  │ │Trader×2 │ │Rescuer │ │Contrarian│
  │ dev<-2%  │ │signal<  │ │ dev<   │ │ dev<-8%  │
  │→sell 60% │ │-0.025  │ │-5%→buy │ │→buy 20%  │
  └──────────┘ └────────┘ └────────┘ └──────────┘
        │ orders                   Noise×3
        └─────────────────────────────────┐
                                          ▼
                                  Market aggregates
                                  D(t) = Σbuy − Σsell
```


## §6 Configuration Reference

| Config Path                                   | Key Parameter    | Value  | Notes                            |
|-----------------------------------------------|------------------|--------|----------------------------------|
| `market.extras.price_impact`                  | λ                | 0.04   | High for thin EM liquidity       |
| `market.extras.mean_reversion`                | γ                | 0.02   | Low — crisis overrides reversion |
| `hot_money_funder.extras.reversal_threshold`  | Reversal trigger | 0.02   | Symmetric ±2%                    |
| `contagion_trader.extras.contagion_weight`    | w₁ in signal     | 0.60   | Deviation-dominant signal        |
| `contagion_trader.extras.contagion_threshold` | Signal trigger   | −0.025 | Dual-negative required           |
| `imf_rescuer.extras.rescue_threshold`         | IMF trigger      | −0.05  | 5% below fundamental             |
| `value_contrarian.extras.oversold_threshold`  | Buy trigger      | −0.08  | Deep discount required           |

Full config: `configs/AsianFinancialCrisis/Rule/players.yml`


## §7 Running Instructions

```bash
# From project root:
python examples/AsianFinancialCrisis/Rule/run_asianfinancialcrisis_rule.py \
    -c configs/AsianFinancialCrisis/Rule/simulation.yml

# Run analysis:
python examples/AsianFinancialCrisis/Rule/analysis.py \
    -c configs/AsianFinancialCrisis/Rule/simulation.yml
```

Output: `EXPERIMENT/AsianFinancialCrisis/Rule/records/`


## §8 Expected Behavior Patterns

| Phase              | Deviation Range    | Dominant Agents                                | Observable Signal                                                            |
|--------------------|--------------------|------------------------------------------------|------------------------------------------------------------------------------|
| **Stable**         | [−2%, +2%]         | NoiseTrader                                    | Small oscillations around fundamental; no large orders                       |
| **Hot Money Exit** | [−5%, −2%]         | HotMoneyFunder (×2 selling)                    | Large sell orders from HotMoneyFunder; deviation deepens                     |
| **Contagion**      | [−10%, −5%]        | ContagionTrader + HotMoneyFunder               | Dual negative signal triggers contagion sell cascade                         |
| **Crisis Peak**    | [−30% to −60%]     | All destabilizing agents; IMFRescuer first buy | Maximum drawdown; IMFRescuer activates at −5%; ValueContrarian at −8%        |
| **Recovery**       | Stabilizing > −20% | IMFRescuer + ValueContrarian                   | Mean reversion gradually restores; contagion sellers have exhausted position |


## §9 References

*(Theory sections from simulation-bases.md — do not re-state; cross-reference only)*

- `../simulation-bases.md §1` — Phenomenon definition (1997 Asian Financial Crisis)
- `../simulation-bases.md §2` — Theoretical foundation for all 5 agent types
- `../simulation-bases.md §3` — Market design principles (λ=0.04 rationale)
- `../simulation-bases.md §6` — Full parameter reference
- `../simulation-bases.md §8` — Historical case calibration targets
- `../analysis-bases.md §2` — Core metrics (max drawdown, crisis velocity, etc.)
