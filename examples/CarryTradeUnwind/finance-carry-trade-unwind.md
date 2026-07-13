# CarryTradeUnwind - Scenario Target

## §1 Meta

| Field       | Content                                                            |
|-------------|--------------------------------------------------------------------|
| Name        | CarryTradeUnwind                                                   |
| Domain      | finance                                                            |
| Produced By | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created     | 2026-07-08                                                         |
| Pipeline    | masim/skills/create-simulation-pipeline.md                         |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)            |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins after leveraged investors have built crowded carry positions by borrowing in a low-yield funding currency and buying higher-yield risky assets. A sudden funding-currency appreciation, risk-off shock, or volatility spike raises mark-to-market losses on those positions. The trigger is a financing and exchange-rate shock, not a change in the fundamental value of the traded asset.

### §2.2 Mechanism

The core mechanism is a funding-liquidity and forced-deleveraging spiral. Carry traders sell as the funding currency appreciates, leveraged carry funds breach stop-loss or margin thresholds, and their liquidation pressure pushes the price further away from the pre-shock carry equilibrium. Higher volatility then tightens risk constraints, causing additional exits and transmitting stress through a self-reinforcing carry-unwind loop.

### §2.3 Participants

The causal participants are carry traders, leveraged carry funds, funding-currency buyers, hedged carry traders, and noise traders. Carry traders and leveraged funds provide the crowded directional exposure, funding-currency buyers represent safe-haven and repatriation demand, hedged carry traders reduce exposure when volatility rises, and noise traders supply background FX order flow. The market coordinator aggregates orders and updates the funding-currency exchange-rate proxy.

### §2.4 Resolution

The episode ends when forced sellers exhaust risk budget or inventory, safe-haven demand and mean reversion become large enough relative to remaining sell pressure, and volatility no longer forces additional exits. The expected resolution is partial stabilization after a sharp unwind, not immediate restoration of the pre-shock carry environment. Historical carry crashes often reverse only partly over the simulation horizon.

## §3 Research Goals

1. Measure whether crowded leveraged carry positions can generate a 10%-25% maximum drawdown after a funding-currency appreciation shock.
2. Test by ablation whether removing the leveraged carry fund materially reduces drawdown, unwind velocity, and crisis-onset speed.
3. Sweep `stop_loss`, `leverage`, `risk_threshold`, and `vol_threshold` to estimate when the carry unwind becomes self-reinforcing.
4. Compare Rule, LLM, RuleLLM, and Rag variants to determine whether model-based reasoning delays, accelerates, or constrains forced unwind behavior.

## §4 Theoretical Anchors

### §4.1 Carry trade returns and crash risk

| Field                     | Content                                                                                                                                                                   |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). Carry trades and currency crashes. *NBER Macroeconomics Annual*, 23(1), 313-348. https://doi.org/10.1086/593088 |
| Key mechanism (≤30 words) | Leveraged carry returns are exposed to rare funding-currency appreciations that create sharp crash risk.                                                                  |
| Key equation              | `carry_demand = leverage * carry_size` when `abs(deviation) > unwind_threshold`, with direction determined by the deviation sign.                                         |
| Motivates agent           | carry-trader                                                                                                                                                              |
| Parameter implication     | `unwind_threshold` range 0.01-0.04, `carry_size` range 400-1200, and `leverage` range 3.0-8.0, default 0.02, 800, and 5.0.                                                |

### §4.2 Funding-liquidity and market-liquidity spiral

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤30 words) | Funding losses force sales, sales worsen market liquidity, and lower prices create further funding pressure.                                                               |
| Key equation              | `forced_sell = min(position, leverage * base_size)` when `deviation > stop_loss`.                                                                                          |
| Motivates agent           | leveraged-carry-fund                                                                                                                                                       |
| Parameter implication     | `stop_loss` range 0.02-0.06, `base_size` range 400-1200, default 0.03 and 800.                                                                                             |

### §4.3 Safe-haven currency demand

| Field                     | Content                                                                                                                             |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Ranaldo, A., & Soderlind, P. (2010). Safe haven currencies. *Review of Finance*, 14(3), 385-407. https://doi.org/10.1093/rof/rfq007 |
| Key mechanism (≤30 words) | Safe-haven and repatriation flows buy funding currencies during stress and partially offset forced carry liquidation.               |
| Key equation              | `buy_qty = position_size` when `deviation < -risk_threshold`.                                                                       |
| Motivates agent           | funding-currency-buyer                                                                                                              |
| Parameter implication     | `risk_threshold` range 0.03-0.08 and `position_size` range 300-800, default 0.05 and 500.                                           |

### §4.4 Carry trades and global FX volatility

| Field                     | Content                                                                                                                                                                                                    |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Menkhoff, L., Sarno, L., Schmeling, M., & Schrimpf, A. (2012). Carry trades and global foreign exchange volatility. *Journal of Finance*, 67(2), 681-718. https://doi.org/10.1111/j.1540-6261.2012.01728.x |
| Key mechanism (≤30 words) | Global FX volatility predicts carry-trade losses and causes volatility-aware strategies to reduce exposure.                                                                                                |
| Key equation              | `adjusted_qty = base_qty * (1 - hedge_ratio)` if `rolling_vol < vol_threshold`; sell if `rolling_vol > vol_threshold`.                                                                                     |
| Motivates agent           | hedged-carry-trader                                                                                                                                                                                        |
| Parameter implication     | `hedge_ratio` range 0.20-0.50 and `vol_threshold` range 0.03-0.08, default 0.30 and 0.05.                                                                                                                  |

### §4.5 Noise and background FX order flow

| Field                     | Content                                                                                                               |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x     |
| Key mechanism (≤30 words) | Uninformed background order flow creates liquidity, volatility, and non-systematic FX demand around the carry unwind. |
| Key equation              | `trade ~ Bernoulli(trade_probability)` with bounded random buy or sell quantity conditional on activation.            |
| Motivates agent           | noise-trader                                                                                                          |
| Parameter implication     | `trade_probability` range 0.10-0.40, default 0.30.                                                                    |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                               | Quantitative range                    | Citation                                                                 | Acceptance metric                                       |
|----|-----------------------------------------------------------------------------------|---------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------|
| F1 | A crowded carry unwind creates a crash-scale drawdown in the exchange-rate proxy. | 10% <= max drawdown <= 25%            | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088    | `analysis.py: compute_max_drawdown()` in [10, 25]       |
| F2 | The unwind has a rapid peak velocity after stop-loss or margin constraints bind.  | peak per-round change >= 2%           | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098       | `analysis.py: compute_unwind_velocity()` >= 2           |
| F3 | Leveraged carry funds dominate forced selling during the cascade phase.           | forced-seller volume share >= 50%     | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098       | `analysis.py: compute_agent_volume_share()` >= 0.50     |
| F4 | Carry crashes partially recover after forced selling weakens.                     | 0.30 <= recovery ratio <= 0.80        | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088    | `analysis.py: compute_recovery_ratio()` in [0.30, 0.80] |
| F5 | Volatility-aware carry traders exit earlier than forced-liquidation carry funds.  | hedged exit at least 3 rounds earlier | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x | `analysis.py: compare_exit_rounds()` >= 3               |

## §6 Historical / Empirical Anchors

### §6.1 Russian default and LTCM carry unwind

| Field             | Content                                                                                                                                                                                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Russian default / LTCM carry unwind, 1998-08 to 1998-10.                                                                                                                                                                                                 |
| Trigger           | Global risk-off, leveraged-fund losses, and funding stress caused rapid deleveraging of yen-funded and other carry positions.                                                                                                                            |
| Quantitative arc  | USD/JPY fell roughly 15% in October 1998 while leveraged positions were reduced over weeks.                                                                                                                                                              |
| Agent mapping     | carry-trader maps to ordinary carry accumulators; leveraged-carry-fund maps to forced deleveragers; funding-currency-buyer maps to safe-haven demand; hedged-carry-trader maps to volatility-aware macro funds; noise-trader maps to background FX flow. |
| Primary source(s) | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098; Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088                                                                                                                |

### §6.2 Global financial crisis yen carry unwind

| Field             | Content                                                                                                                                                                                                                                                                          |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Global financial crisis JPY carry unwind, 2007-2008.                                                                                                                                                                                                                             |
| Trigger           | Risk appetite collapsed, volatility rose, and leveraged investors unwound long high-yield currency positions.                                                                                                                                                                    |
| Quantitative arc  | USD/JPY fell from about 110 to 88 in roughly six weeks, about a 20% move.                                                                                                                                                                                                        |
| Agent mapping     | leveraged-carry-fund maps to margin-constrained funds; carry-trader maps to broad carry flow; funding-currency-buyer maps to yen safe-haven and repatriation flow; hedged-carry-trader maps to volatility-managed carry strategies; noise-trader maps to non-carry FX liquidity. |
| Primary source(s) | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088; Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x                                                                                                                                  |

### §6.3 Swiss franc floor removal

| Field             | Content                                                                                                                                                                                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Swiss franc floor removal, 2015-01-15.                                                                                                                                                                                                                                     |
| Trigger           | The Swiss National Bank removed the EUR/CHF floor, abruptly repricing a funding and safe-haven currency.                                                                                                                                                                   |
| Quantitative arc  | EUR/CHF moved about 20%-30% intraday, with extreme liquidity withdrawal and stop-loss execution.                                                                                                                                                                           |
| Agent mapping     | leveraged-carry-fund maps to forced CHF short-covering; funding-currency-buyer maps to safe-haven CHF demand; hedged-carry-trader maps to participants with options or risk controls; carry-trader maps to directional carry exposure; noise-trader maps to residual flow. |
| Primary source(s) | Bank for International Settlements. (2015). *Triennial Central Bank Survey and FX market commentary*. https://www.bis.org                                                                                                                                                  |

## §7 Agent Roster

| Agent name (kebab)     | Real-world counterpart                   | Theory family (§4 anchor)             | Domain role       | Primary signals               | Intent line                                                                                         | Expected pool match                                   |
|------------------------|------------------------------------------|---------------------------------------|-------------------|-------------------------------|-----------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| carry-trader           | hedge fund / leveraged currency investor | Carry Trade / Risk-On-Risk-Off (§4.1) | Destabilising     | price, deviation, round       | Exists to build carry exposure in calm conditions and unwind when the funding currency appreciates. | examples/AGENT_POOL/finance/carry-trader.md           |
| leveraged-carry-fund   | macro hedge fund / leveraged fund        | Liquidity / Funding (§4.2)            | Destabilising     | price, deviation, position    | Exists to transmit margin and stop-loss pressure into forced FX selling.                            | examples/AGENT_POOL/finance/leveraged-carry-fund.md   |
| funding-currency-buyer | reserve manager / safe-haven buyer       | Safe-haven currency demand (§4.3)     | Stabilising       | price, deviation, round       | Exists to provide partial safe-haven demand when downside carry stress becomes severe.              | examples/AGENT_POOL/finance/funding-currency-buyer.md |
| hedged-carry-trader    | volatility-managed macro fund            | Volatility-managed carry (§4.4)       | Context-dependent | price, deviation, rolling_vol | Exists to reduce carry exposure when FX volatility rises above its risk budget.                     | examples/AGENT_POOL/finance/hedged-carry-trader.md    |
| noise-trader           | uninformed FX liquidity participant      | Noise / Market Microstructure (§4.5)  | Context-dependent | price, round, rng_state       | Exists to supply bounded background FX order flow.                                                  | examples/AGENT_POOL/finance/noise-trader.md           |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a dealer-style single-price FX proxy. The funding-currency price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where positive net demand raises the funding-currency price and negative net demand lowers it. The price-impact term captures liquidity stress during crowded unwinds, while the mean-reversion term captures long-run purchasing-power or valuation gravity.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, `round`, and the historical price window needed to compute rolling volatility. `price` and `deviation` drive carry and stop-loss rules, `round` supports phase detection, and rolling volatility supports the hedged carry trader. No unrelated return-salience signal is required for this scenario.

### §8.3 Constraints and Frictions

Agents have cash, inventory, leverage, stop-loss, and position-size constraints. Short exposure is represented by inventory-constrained sell decisions rather than unlimited short creation. The market applies a positive price floor, bounded Gaussian noise, and finite price impact so liquidation pressure remains interpretable.

### §8.4 Round Granularity

One round represents one stress-period trading interval in which FX prices, margin information, and public risk signals refresh. The calibration maps tens of rounds to days or weeks, consistent with the 1998 and 2008 carry-unwind anchors. The full run length includes buildup, stress, cascade, partial stabilization, and post-unwind phases.

## §9 Parameter Seeds

| Parameter                 | Symbol         | Belongs to (agent / environment) | Empirical range       | Candidate default | Source citation                                                                                                                               |
|---------------------------|----------------|----------------------------------|-----------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| unwind threshold          | `theta_unwind` | carry-trader (§7)                | 0.01-0.04             | 0.02              | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088                                                                         |
| carry base size           | `q_carry`      | carry-trader (§7)                | 400-1200              | 800               | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088                                                                         |
| carry leverage            | `L_c`          | carry-trader (§7)                | 3.0-8.0               | 5.0               | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088                                                                         |
| deviation sizing scale    | `s_dev`        | carry-trader (§7)                | 2500-7500             | 5000              | Brunnermeier, Nagel & Pedersen (2009), https://doi.org/10.1086/593088                                                                         |
| stop loss                 | `theta_stop`   | leveraged-carry-fund (§7)        | 0.02-0.06             | 0.03              | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098                                                                            |
| leveraged fund base size  | `q_lcf`        | leveraged-carry-fund (§7)        | 400-1200              | 800               | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098                                                                            |
| safe-haven risk threshold | `theta_safe`   | funding-currency-buyer (§7)      | 0.03-0.08             | 0.05              | Ranaldo & Soderlind (2010), https://doi.org/10.1093/rof/rfq007                                                                                |
| safe-haven position size  | `q_safe`       | funding-currency-buyer (§7)      | 300-800               | 500               | Ranaldo & Soderlind (2010), https://doi.org/10.1093/rof/rfq007                                                                                |
| hedge ratio               | `h`            | hedged-carry-trader (§7)         | 0.20-0.50             | 0.30              | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x                                                                      |
| volatility threshold      | `theta_vol`    | hedged-carry-trader (§7)         | 0.03-0.08             | 0.05              | Menkhoff et al. (2012), https://doi.org/10.1111/j.1540-6261.2012.01728.x                                                                      |
| trade probability         | `p_n`          | noise-trader (§7)                | 0.10-0.40             | 0.30              | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                                                              |
| price impact              | `lambda`       | environment (§8.1)               | 0.001-0.010           | 0.003             | FX market depth normalization, calibrated to §6.1-§6.2 arcs                                                                                   |
| mean reversion            | `gamma`        | environment (§8.1)               | 0.005-0.030           | 0.02              | Rogoff, K. (1996). The purchasing power parity puzzle. *Journal of Economic Literature*, 34(2), 647-668. https://www.jstor.org/stable/2729217 |
| fundamental value         | `F`            | environment (§8.1)               | Source: normalization | 1.0               | Source: normalization                                                                                                                         |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                    |
|---------|--------|--------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the carry-unwind mechanism.                            |
| LLM     | Yes    | Tests whether persona-only reasoning changes forced-exit and safe-haven behavior.          |
| RuleLLM | Yes    | Tests whether explicit numerical rules constrain LLM carry-unwind decisions.               |
| Rag     | Yes    | Tests whether retrieved historical carry-crash context changes leverage and exit behavior. |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
