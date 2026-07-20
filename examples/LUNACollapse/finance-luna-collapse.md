# LUNACollapse - Scenario Target

## §1 Meta

| Field | Content |
|---|---|
| Name | LUNACollapse |
| Domain | finance |
| Phenomenon | Confidence loss in an algorithmic stablecoin converts redemption pressure into governance-token dilution, liquidation, and a self-reinforcing price collapse. |
| Requested By | Wenyou |
| Produced By | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Codex) |
| Created | 2026-07-20 |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Target Spec | masim/skills/define-simulation-scenario-skill.md v1.2.0 |
| Status | released |

## §2 Phenomenon Statement

### §2.1 Trigger

Large UST sales break confidence in the one-dollar peg during May 2022. Holders reassess whether conversion will remain available and begin redeeming or exiting. The simulation represents this event with a bounded, reproducible depeg identification stimulus rather than an unexplained random crash.

### §2.2 Mechanism

Below-peg redemption creates or releases LUNA-like supply that is sold into a thin market. Falling governance-token value weakens the credibility of future redemptions, while collateral liquidations and Anchor-style withdrawals add further selling. The feedback loop is redemption pressure to dilution and selling, then lower collateral confidence, then additional redemption pressure.

### §2.3 Participants

Stablecoin holders initiate withdrawals after a confidence threshold is crossed. Arbitrageurs execute the conversion mechanism, DeFi lenders liquidate impaired collateral, and Anchor depositors exit the yield ecosystem. Value buyers provide a limited stabilizing demand channel at deep discounts.

### §2.4 Resolution

The cascade slows when finite inventories limit additional sales and value demand begins absorbing flow. Weak mean reversion can then pull price toward its public anchor, although the run may finish below fundamental value. A positive price floor prevents numerical failure without forcing recovery.

## §3 Research Goals

1. Does the common depeg stimulus produce a material but finite LUNA-like drawdown, deviation, and sell-volume response?
2. Does ablating stablecoin holders, DeFi lenders, or Anchor depositors reduce collapse depth or persistence?
3. How do `price_impact`, `market_depth`, and the redemption or liquidation thresholds change onset, drawdown, and recovery in parameter sweeps?
4. Can value-buyer demand materially offset destabilizing sell pressure after a deep discount?
5. Do Rule, LLM, and RuleLLM preserve the same causal mechanism while differing in timing and action intensity?

## §4 Theoretical Anchors

### §4.1 Threshold Stablecoin Run

| Field | Content |
|---|---|
| Full citation | Uhlig, H. (2022). A Luna-tic Stablecoin Crash. *NBER Working Paper 30256*. https://doi.org/10.3386/w30256 |
| Key mechanism | Stablecoin holders burn or sell only after their heterogeneous perceived probability of failed convertibility crosses a threshold. |
| Key equation | Sell when `deviation < -redemption_threshold`, where deviation is the public stress proxy and quantity is bounded by inventory. |
| Motivates agent | stablecoin-holder |
| Parameter implication | `redemption_threshold=0.05` lies within a bounded confidence-loss region and is tested by sweep. |

### §4.2 Algorithmic Stablecoin Arbitrage

| Field | Content |
|---|---|
| Full citation | Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. https://arxiv.org/abs/2006.12388 |
| Key mechanism | A conversion mechanism can stabilize a peg in normal conditions but transmit a run into the volatile backing or governance asset during stress. |
| Key equation | When `abs(deviation)>arb_threshold`, conversion flow scales with `abs(deviation)` and is clipped by inventory and a fixed maximum. |
| Motivates agent | arbitrageur |
| Parameter implication | `arb_threshold=0.02` separates ordinary noise from an active conversion channel. |

### §4.3 DeFi Liquidation Contagion

| Field | Content |
|---|---|
| Full citation | Werner, S. M., Perez, D., Gudgeon, L., Klages-Mundt, A., Harz, D., & Knottenbelt, W. J. (2022). SoK: Decentralized Finance. *AFT 2022*, 30-46. https://doi.org/10.1145/3558535.3559780 |
| Key mechanism | Collateral impairment turns discretionary risk management into forced liquidation and transmits price shocks across DeFi positions. |
| Key equation | Liquidate `floor(0.60*position)` when `deviation < -liquidation_threshold`. |
| Motivates agent | de-fi-lender |
| Parameter implication | `liquidation_threshold=0.15` activates after a material collateral decline. |

### §4.4 Run-prone Yield Deposits

| Field | Content |
|---|---|
| Full citation | Diamond, D. W., & Dybvig, P. H. (1983). Bank Runs, Deposit Insurance, and Liquidity. *Journal of Political Economy*, 91(3), 401-419. https://doi.org/10.1086/261155 |
| Key mechanism | Demandable claims backed by longer-horizon assets can support self-reinforcing withdrawals when confidence deteriorates. |
| Key equation | Withdraw `floor(0.40*position)` when `deviation < -yield_threshold`. |
| Motivates agent | anchor-depositor |
| Parameter implication | `yield_threshold=0.05` makes yield-protocol flight respond near the initial confidence break. |

### §4.5 Limits to Arbitrage

| Field | Content |
|---|---|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism | Capital and horizon constraints can prevent value-oriented traders from eliminating severe mispricing during a run. |
| Key equation | Buy a cash-feasible bounded quantity only when `deviation < -discount_threshold`. |
| Motivates agent | value-buyer |
| Parameter implication | `discount_threshold=0.30` delays stabilizing demand until the discount is deep. |

## §5 Stylized Facts

| # | Fact | Quantitative range | Citation | Acceptance metric |
|---|---|---|---|---|
| F1 | The run creates a material governance-token dislocation without numerical collapse. | `5% <= max_abs_deviation_pct <= 60%` | Uhlig (2022); BIS (2022) | `calculate_metrics(): max_abs_deviation_pct` |
| F2 | The simulated price path has a finite peak-to-trough collapse. | `5% <= abs(max_drawdown_pct) <= 60%` | Uhlig (2022) and normalized mechanism calibration | `calculate_metrics(): max_drawdown_pct` |
| F3 | Crisis activity is observable rather than an all-hold trajectory. | `total_volume > 0` | Werner et al. (2022) and mechanism requirement | `calculate_metrics(): total_volume` |
| F4 | Stress persists beyond the initial stimulus but remains bounded. | `1% <= mean_abs_deviation_pct <= 40%` | Uhlig (2022) | `calculate_metrics(): mean_abs_deviation_pct` |
| F5 | The final state remains positive and no worse than the maximum observed stress. | `final_price > 0` and `abs(final_deviation_pct) <= max_abs_deviation_pct` | positive-price invariant | `calculate_metrics(): final, final_deviation_pct` |

## §6 Historical / Empirical Anchors

### §6.1 TerraUSD and LUNA Collapse, May 2022

| Field | Content |
|---|---|
| Name + dates | TerraUSD and LUNA collapse, 2022-05-07 to 2022-05-15 |
| Trigger | Large UST sales broke the peg and confidence in algorithmic convertibility. |
| Quantitative arc | UST fell from about one dollar to a few cents, while NBER evidence describes more than 90% market-value destruction and the SEC reports more than $40 billion in combined value erased. |
| Agent mapping | UST owners map to stablecoin-holder; conversion desks to arbitrageur; collateral protocols to de-fi-lender; Anchor users to anchor-depositor; distressed buyers to value-buyer. |
| Primary source(s) | Uhlig (2022), https://doi.org/10.3386/w30256; SEC amended complaint, https://www.sec.gov/files/terraform-labs-pte-ltd-amended-complaint.pdf; BIS Annual Economic Report 2022, https://www.bis.org/publ/arpdf/ar2022e3.htm |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|---|---|---|---|---|---|---|
| stablecoin-holder | UST holder | Threshold Stablecoin Run (§4.1) | Destabilising | price, fundamental, deviation | Exists to convert confidence loss into redemption selling. | examples/AGENT_POOL/finance/stablecoin-holder.md |
| arbitrageur | algorithmic conversion trader | Algorithmic Stablecoin Arbitrage (§4.2) | Context-dependent | price, fundamental, deviation | Exists to execute the conversion channel that can amplify stress. | examples/AGENT_POOL/finance/arbitrageur.md |
| de-fi-lender | collateralized lending protocol | DeFi Liquidation Contagion (§4.3) | Destabilising | price, fundamental, deviation | Exists to translate collateral impairment into forced selling. | examples/AGENT_POOL/finance/de-fi-lender.md |
| anchor-depositor | high-yield protocol depositor | Run-prone Yield Deposits (§4.4) | Destabilising | price, deviation, round | Exists to model ecosystem withdrawal after confidence deteriorates. | examples/AGENT_POOL/finance/anchor-depositor.md |
| value-buyer | constrained contrarian investor | Limits to Arbitrage (§4.5) | Stabilising | price, fundamental, deviation | Exists to supply bounded demand at deep discounts. | examples/AGENT_POOL/finance/value-buyer.md |

## §8 Environment Specification

### §8.1 Price Formation

The shipped scenario uses the explicitly disclosed single-risky-asset approximation of `crypto-algostable-depeg`: `P(t+1)=max(P_floor,P(t)+lambda*D(t)/M+gamma*(F-P(t))+epsilon(t)+F*S(t))`. The public pool profile records that full two-asset UST/LUNA mint-burn coupling remains outside this implementation. Order impact is normalized by market depth so agent population changes do not create unit-scale explosions.

### §8.2 Information Broadcast

Every round broadcasts `price`, `fundamental`, `deviation`, and `round`. Participants also observe their own cash and inventory. No private signal or future state is broadcast.

### §8.3 Constraints and Frictions

Orders are clipped by cash and inventory, prices have a strictly positive floor, and short selling is disabled. Redemption, liquidation, withdrawal, and value-entry thresholds create non-linear activation. No circuit breaker is imposed.

### §8.4 Round Granularity

One round is a stress-market clearing interval rather than a literal block or calendar day. A 200-round formal run contains a short controlled stimulus followed by endogenous trading and recovery dynamics. This scale supports mechanism identification without claiming tick-level historical reconstruction.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to | Empirical / calibration range | Candidate default | Source citation |
|---|---|---|---|---|---|
| `initial_price`, `fundamental_value` | `P0,F` | §8.1 environment | positive normalized index | `100,100` | normalization |
| `price_impact`, `market_depth` | `lambda,M` | §8.1 environment | positive | `0.04,100` | market-impact normalization; Klages-Mundt et al. (2020) mechanism calibration |
| `mean_reversion`, `noise_std` | `gamma,sigma` | §8.1 environment | `[0,1]`, non-negative | `0.005,0.015` | controlled mechanism calibration |
| `shock_schedule` | `S(t)` | §8.1 environment | bounded signed map | rounds 20-23: `-0.06,-0.05,-0.04,-0.03` | SEC (2023) and Uhlig (2022) event identification |
| `redemption_threshold` | `theta_r` | stablecoin-holder | `(0,0.20]` | `0.05` | Uhlig (2022) threshold mechanism |
| `arb_threshold` | `theta_a` | arbitrageur | `(0,0.10]` | `0.02` | Klages-Mundt et al. (2020) |
| `liquidation_threshold` | `theta_l` | de-fi-lender | `(0,0.50]` | `0.15` | Werner et al. (2022) and scenario calibration |
| `yield_threshold` | `theta_y` | anchor-depositor | `(0,0.20]` | `0.05` | Diamond and Dybvig (1983) and event calibration |
| `discount_threshold` | `theta_v` | value-buyer | `(0,0.80]` | `0.30` | Shleifer and Vishny (1997) |
| `random_seed`, `price_floor` | `seed,Pmin` | §8.1 environment | non-negative integer, positive | `20260720,0.01` | reproducibility and numerical invariant |
| `initial_cash`, `initial_position`, `base_size` | `C0,H0,Q0` | all agents | non-negative and role-specific | config-specific | bounded portfolio calibration |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Canonical identity prefix | Rationale |
|---|---|---|---|
| Rule | Yes | `rule_` | Deterministic causal baseline and formal calibration run. |
| LLM | Yes | `llm_` | Tests persona-driven decisions under the common market contract. |
| RuleLLM | Yes | `rulellm_` | Tests rule-guided language-model decisions. |
| Rag | Yes | `ragllm_` | Preserves retrieval-grounded reasoning; current polish scope is static and import validation only. |

### §10.2 Pass / Fail Criteria

1. All five §5 facts pass in a fresh 200-round Rule run with finite positive prices and machine-readable analysis output.
2. All five roster agents resolve across §4, pool profiles/icons, configuration identities, topology, and implementation classes.
3. Rule, LLM, and RuleLLM pass configuration, import, setup, and bounded decision-contract checks; Rag passes static configuration/import checks in this run scope.
4. Every §3 question is traceable to a metric, ablation, sweep, or cross-variant comparison.
5. Four fixed PNG outputs and `summary.json` are generated by analysis without an interactive display dependency.
