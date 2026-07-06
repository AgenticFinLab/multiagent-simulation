# AsianFinancialCrisis — Scenario Target

## §1 Meta

| Field         | Content                                                                 |
|---------------|-------------------------------------------------------------------------|
| Name          | AsianFinancialCrisis                                                    |
| Domain        | finance                                                                 |
| Requested By  | Sijia Chen                                                              |
| Produced By   | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Codex)      |
| Created       | 2026-07-05                                                              |
| Pipeline      | masim/skills/create-simulation-pipeline.md                              |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                 |
| Status        | released                                                                |

## §2 Phenomenon Statement

### §2.1 Trigger
The scenario begins with an emerging-market exchange-rate proxy near its pre-crisis fundamental value after several years of short-term foreign capital inflows. The vulnerable state is a large stock of foreign-funded positions whose owners are willing to exit once the currency falls slightly below perceived fair value. A small initial depreciation, reserve-pressure signal, or negative regional shock pushes the deviation below the hot-money reversal threshold. That threshold crossing turns a stable peg-like environment into a sudden-stop episode.

### §2.2 Mechanism
The amplification loop is a capital-flow reversal and contagion feedback. Hot money sells after a small depreciation, the market price falls further, cross-border contagion traders combine the negative deviation with recent returns, and their sales deepen the depreciation. The deeper depreciation then validates more exit, triggering further short-term capital withdrawal and stronger contagion selling. Stabilising capital enters only after larger discounts, so the crisis can overshoot fundamentals before rescue and value demand form a floor.

### §2.3 Participants
The core participant classes are short-term foreign funders, cross-border contagion sellers, official crisis-rescue capital, long-horizon value buyers, and background noise/liquidity traders. Short-term foreign funders represent leveraged external creditors and portfolio investors that reverse positions when exchange-rate stress appears. Contagion sellers represent regional investors and common-creditor channels that cut exposure across countries once one market falls. Official rescue capital and value buyers provide stabilising demand after severe dislocation, while noise traders add background order flow and prevent a mechanically deterministic path.

### §2.4 Resolution
The crisis stops when forced and contagion selling has exhausted enough positions and stabilising demand becomes large relative to remaining outflows. Official rescue capital activates after the deviation breaches the intervention threshold, modelling IMF-style support that is large but delayed. Value buyers enter at deeper discounts and add a private-sector floor once expected recovery compensation exceeds risk. Recovery is partial rather than instant because mean reversion is slow and short-term capital does not immediately return after a sudden stop.

## §3 Research Goals

1. **Crisis severity calibration.** Can the simulation generate a maximum drawdown in the 30% to 60% range associated with severe Asian currency-crisis episodes?
2. **Cascade timing and velocity.** Does the crisis cross the full-crisis threshold within a plausible window, and does the largest round-to-round depreciation exceed 2%?
3. **Agent-sequence validation.** Does hot-money exit precede contagion selling, and do rescue and value-buying agents enter only after larger deviations?
4. **Ablation.** If the contagion seller is removed, does crisis depth and return autocorrelation fall materially relative to the full model?
5. **Parameter sweep and variant comparison.** How do price impact and model-driven decision variants change crisis depth, onset, and recovery relative to the deterministic baseline?

## §4 Theoretical Anchors

### §4.1 Sudden Stops and Hot-Money Reversal

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis: Diagnosis, remedies, prospects. *Brookings Papers on Economic Activity*, 1998(1), 1-90. https://doi.org/10.1353/eca.1998.0009 |
| Key mechanism (≤30 words) | Short-term foreign capital reverses abruptly after small stress signals, forcing large sales before fundamentals fully adjust. |
| Key equation              | Exit rule: sell when `deviation_t < -theta_reversal`; quantity `Q_sell = phi_sell * position_t`, where `theta_reversal` is the stress threshold. |
| Motivates agent           | `hot-money-funder` (§7). |
| Parameter implication     | `theta_reversal` range 0.01 to 0.05, default 0.02; `phi_sell` range 0.40 to 0.80, default 0.60. |

### §4.2 Twin Crises and Regional Contagion

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Kaminsky, G. L., & Reinhart, C. M. (1999). The twin crises: The causes of banking and balance-of-payments problems. *American Economic Review*, 89(3), 473-500. https://doi.org/10.1257/aer.89.3.473 |
| Key mechanism (≤30 words) | Currency and banking stress reinforce each other, while regional markets transmit pressure through common creditors and panic correlations. |
| Key equation              | `contagion_signal_t = w_dev * deviation_t + w_ret * return_t`; sell when `contagion_signal_t < theta_contagion`. |
| Motivates agent           | `contagion-trader` (§7). |
| Parameter implication     | `w_dev` range 0.40 to 0.80, default 0.60; `w_ret` range 0.20 to 0.60, default 0.40; `theta_contagion` range -0.05 to -0.01, default -0.025. |

### §4.3 IMF Crisis Lending and Conditional Rescue

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigers? A model of the Asian crisis. *European Economic Review*, 43(7), 1211-1236. https://doi.org/10.1016/S0014-2921(98)00111-0 |
| Key mechanism (≤30 words) | Official rescue lending can stabilise crisis prices, but intervention is delayed until stress is severe and conditional support is credible. |
| Key equation              | Rescue rule: buy when `deviation_t < theta_rescue`; quantity `Q_buy = phi_rescue * cash_t / price_t`. |
| Motivates agent           | `imf-rescuer` (§7). |
| Parameter implication     | `theta_rescue` range -0.15 to -0.03, default -0.05; `phi_rescue` range 0.10 to 0.40, default 0.25. |

### §4.4 Crisis Liquidity and Contrarian Value Buying

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤30 words) | Funding stress creates fire-sale discounts; patient capital supplies stabilising demand only after compensation is high enough. |
| Key equation              | Buy when `deviation_t < theta_value`; quantity `Q_buy = phi_value * cash_t / price_t`; sell after recovery when `deviation_t > theta_recovery`. |
| Motivates agent           | `value-contrarian` (§7). |
| Parameter implication     | `theta_value` range -0.20 to -0.05, default -0.08; `phi_value` range 0.10 to 0.40, default 0.20. |

### §4.5 Noise Trading and Background Liquidity

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Non-informational trades add liquidity and volatility, preventing all movement from being mechanically explained by crisis agents. |
| Key equation              | Trade with probability `p_noise`; conditional direction is random and quantity is bounded by cash or position. |
| Motivates agent           | `noise-trader` (§7). |
| Parameter implication     | `p_noise` range 0.10 to 0.50, default 0.30. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | Severe Asian crisis episodes produce peak currency drawdowns in the moderate-to-severe range. | `0.30 <= max_drawdown <= 0.60` | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009 | `analysis.py: _compute_max_drawdown()` in [30, 60] percent |
| F2 | Full crisis onset occurs only after initial pressure propagates beyond the first hot-money exit. | `10 <= crisis_onset_round <= 20` | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473 | `analysis.py: _compute_crisis_onset()` in [10, 20] |
| F3 | Sudden stops generate sharp round-to-round depreciation rather than smooth drift. | `crisis_velocity > 2.0` percent per round | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009 | `analysis.py: _compute_crisis_velocity()` > 2.0 |
| F4 | Contagion phases exhibit positive return autocorrelation from selling feedback. | `0.25 <= ac1 <= 0.50` | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473; Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 | `analysis.py: _compute_rolling_ac1()` in [0.25, 0.50] |
| F5 | Official rescue demand activates only after severe stress, and should measurably slow the decline. | first rescue after `deviation < -0.05`; post-rescue decline rate lower than pre-rescue rate | Corsetti, Pesenti & Roubini (1999), https://doi.org/10.1016/S0014-2921(98)00111-0 | `analysis.py: rescue_activation_round()` and post-rescue slope comparison |

## §6 Historical / Empirical Anchors

### §6.1 1997 Asian Financial Crisis

| Field             | Content |
|-------------------|---------|
| Name + dates      | 1997 Asian Financial Crisis, with the Thai baht depeg on 1997-07-02 and regional spread through late 1997. |
| Trigger           | Thailand abandoned the baht peg after reserve pressure and speculative attacks, revealing short-term external-debt vulnerability across the region. |
| Quantitative arc  | Thai baht fell roughly 15-20% immediately after depegging and about 50% peak-to-trough; Indonesian rupiah and Korean won suffered larger regional declines; IMF packages for Thailand, Indonesia, and Korea totalled more than 100 billion USD in commitments. |
| Agent mapping     | `hot-money-funder` maps to short-term foreign creditors and portfolio investors; `contagion-trader` maps to regional investors and common-creditor channels; `imf-rescuer` maps to IMF-style support; `value-contrarian` maps to long-horizon crisis buyers; `noise-trader` maps to background non-informational flow. |
| Primary source(s) | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009; Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473; Corsetti, Pesenti & Roubini (1999), https://doi.org/10.1016/S0014-2921(98)00111-0 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| hot-money-funder | hedge fund or foreign short-term portfolio creditor | Sudden Stops (§4.1) | Destabilising | price, deviation, cash | "Exists to reverse short-term foreign capital exposure when currency stress appears." | (none - likely new) |
| contagion-trader | active cross-border hedge fund or regional portfolio manager | Contagion (§4.2) | Destabilising | price, prev_price, deviation | "Exists to transmit regional stress through deviation and momentum-sensitive selling." | examples/AGENT_POOL/finance/momentum-trader.md (family match only) |
| imf-rescuer | official sector crisis lender or sovereign stabilisation fund | Policy Intervention (§4.3) | Stabilising | price, deviation, cash | "Exists to supply delayed official support after severe exchange-rate stress." | (none - likely new) |
| value-contrarian | long-horizon value fund or distressed-asset investor | Liquidity / Funding (§4.4) | Stabilising | price, fundamental, deviation | "Exists to buy crisis discounts when compensation for liquidity risk is sufficient." | examples/AGENT_POOL/finance/contrarian-trader.md |
| noise-trader | uninformed retail or liquidity-motivated trader | Noise Trading (§4.5) | Context-dependent | price, cash, position | "Exists to add background liquidity and non-informational volatility." | examples/AGENT_POOL/finance/noise-trader.md |

Diversity notes: the roster includes two destabilising agents, two stabilising agents, and one context-dependent background trader. Theory families are not repeated more than twice, and the signal sets differ across deviation, momentum, cash, and position channels.

## §8 Environment Specification

### §8.1 Price Formation

Single price-impact plus mean-reversion market:

`P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)`, where `D(t)` is aggregate buy quantity minus sell quantity, `F` is constant fundamental value, `lambda` is price impact, `gamma` is mean reversion, and `epsilon(t)` is Gaussian noise. The formula is calibrated as an exchange-rate / regional asset proxy rather than a literal bilateral FX peg. High price impact reflects thin crisis liquidity; slow mean reversion reflects persistent capital-flow pressure.

### §8.2 Information Broadcast

| Field         | Type  | Definition | Rationale |
|---------------|-------|------------|-----------|
| `price`       | float | Current market price or exchange-rate proxy. | Primary state signal for all agents. |
| `prev_price`  | float | Previous round price. | Required for contagion momentum and return calculation. |
| `fundamental` | float | Constant pre-crisis fair value. | Required for deviation and recovery calculations. |
| `deviation`   | float | `(price - fundamental) / fundamental`. | Primary crisis-pressure signal for four agents. |
| `volume`      | float | Total trading volume proxy. | Supports phase diagnostics and crisis activity measurement. |
| `round`       | int   | Current round. | Supports phase tracking and analysis. |

### §8.3 Constraints and Frictions

| Item | Yes / No | Rationale |
|------|----------|-----------|
| Short-selling allowed | No | The baseline crisis is generated by liquidation of existing exposure, not naked shorting. |
| Explicit reserve stock | No | Reserve depletion is represented by delayed official support and price-impact pressure, not by a separate balance-sheet variable. |
| IMF-style support | Yes | Required to test delayed rescue and stabilisation effects. |
| Price floor | Yes | Prevents non-positive exchange-rate proxy values. |
| Circuit breaker | No | Currency crises historically continue across days and markets rather than halt through one exchange mechanism. |

### §8.4 Round Granularity

Each round approximates a short crisis-trading interval, such as one trading day or a compressed policy-relevant window. A 200-round run covers pre-crisis stability, sudden stop, contagion cascade, rescue activation, and partial recovery. Smoke tests may use fewer rounds to validate imports, initialization, state updates, output writing, and analysis readability.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|-----------------------------------|-----------------|-------------------|-----------------|
| initial price | P(0) | environment (§8.1) | 100 normalised crisis index | 100.0 | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009; index normalization to pre-crisis level |
| fundamental value | F | environment (§8.1) | 100 normalised | 100.0 | Source: normalization |
| price impact | lambda | environment (§8.1) | 0.02 to 0.08 | 0.04 | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009; crisis thin-liquidity calibration |
| mean reversion | gamma | environment (§8.1) | 0.01 to 0.05 | 0.02 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| noise standard deviation | sigma | environment (§8.1) | 0.01 to 0.03 | 0.02 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| reversal threshold | theta_reversal | hot-money-funder (§7) | 0.01 to 0.05 | 0.02 | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009 |
| hot-money sell ratio | phi_hm_sell | hot-money-funder (§7) | 0.40 to 0.80 | 0.60 | Radelet & Sachs (1998), https://doi.org/10.1353/eca.1998.0009 |
| hot-money buy ratio | phi_hm_buy | hot-money-funder (§7) | 0.10 to 0.40 | 0.30 | Calvo (1998), stable URL: https://www.ucema.edu.ar/publicaciones/download/volume1/calvo.pdf |
| contagion deviation weight | w_dev | contagion-trader (§7) | 0.40 to 0.80 | 0.60 | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473 |
| contagion return weight | w_ret | contagion-trader (§7) | 0.20 to 0.60 | 0.40 | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473 |
| contagion threshold | theta_contagion | contagion-trader (§7) | -0.05 to -0.01 | -0.025 | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473 |
| contagion sell ratio | phi_ct_sell | contagion-trader (§7) | 0.30 to 0.70 | 0.50 | Kaminsky & Reinhart (1999), https://doi.org/10.1257/aer.89.3.473 |
| rescue threshold | theta_rescue | imf-rescuer (§7) | -0.15 to -0.03 | -0.05 | Corsetti, Pesenti & Roubini (1999), https://doi.org/10.1016/S0014-2921(98)00111-0 |
| rescue buy ratio | phi_rescue | imf-rescuer (§7) | 0.10 to 0.40 | 0.25 | Corsetti, Pesenti & Roubini (1999), https://doi.org/10.1016/S0014-2921(98)00111-0 |
| value-entry threshold | theta_value | value-contrarian (§7) | -0.20 to -0.05 | -0.08 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| value buy ratio | phi_value_buy | value-contrarian (§7) | 0.10 to 0.40 | 0.20 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| value sell ratio | phi_value_sell | value-contrarian (§7) | 0.10 to 0.40 | 0.20 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| noise trade probability | p_noise | noise-trader (§7) | 0.10 to 0.50 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |

Normalization cap: 1 of 18 rows is marked `Source: normalization`, under the §11 cap of 10%.

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---------|--------|-----------|
| Rule | Yes | Deterministic baseline for crisis depth, onset, velocity, and agent-sequence validation. |
| LLM | Yes | Tests whether model-driven crisis reasoning amplifies or delays the rule-based cascade. |
| RuleLLM | Yes | Tests whether explicit crisis rules inside model reasoning preserve threshold timing while allowing judgmental sizing. |
| Rag | Yes | Tests whether retrieved historical crisis knowledge moderates, accelerates, or strengthens crisis actions. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| The deterministic variant initializes agents, runs from repository root, writes records, and completes without uncaught exceptions. | green |
| At least one crisis-pressure mechanism activates: hot-money exit, contagion selling, rescue buying, or value buying. | green |
| Analysis can load generated records and compute the core metrics from §5. | green |
| Stale references to other scenarios are absent from `examples/AsianFinancialCrisis/` and `configs/AsianFinancialCrisis/`. | green |
