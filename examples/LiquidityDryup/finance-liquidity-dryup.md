# LiquidityDryup

## §1 Meta

| Field | Content |
|---|---|
| Name | LiquidityDryup |
| Domain | finance |
| Phenomenon | Endogenous withdrawal of market-making capacity amplifies order flow into a persistent liquidity and price-impact spiral. |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0) |

## §2 Phenomenon Statement

### §2.1 Trigger

A sufficiently large absolute return raises perceived inventory and adverse-selection risk above the market makers' withdrawal threshold. Liquidity providers reduce quoted depth while liquidity seekers, momentum traders, and noise traders continue submitting orders.

### §2.2 Mechanism

Aggregate depth is endogenous. As market makers withdraw, the same net demand produces a larger price change; the larger return triggers further withdrawal and momentum demand. Value traders provide a bounded stabilizing channel once price departs far enough from fundamental value. The feedback loop is:

`stress -> liquidity withdrawal -> higher effective price impact -> larger return -> more stress`.

### §2.3 Participants

Market makers supply depth but withdraw under stress; liquidity seekers demand immediacy; value traders trade against fundamental mispricing and can restore some depth; momentum traders amplify recent returns; noise traders supply zero-mean background order flow.

### §2.4 Resolution

The dry-up resolves when bounded contrarian liquidity and mean reversion reduce absolute returns below the withdrawal threshold, allowing market makers to re-enter. Failure to recover within the expected duration indicates insufficient stabilizing capacity or excessive price impact.

## §3 Research Goals

1. Can endogenous market-maker withdrawal generate a liquidity-ratio trough between 0.05 and 0.30 within 200 rounds?
2. Does removing momentum traders reduce peak absolute deviation by at least 30%?
3. How do `volatility_threshold`, `price_impact`, and `base_liquidity_provision` change dry-up depth and duration?
4. Does value-trader activation precede measurable recovery in liquidity and price deviation?
5. Do Rule, LLM, RuleLLM, and Rag variants preserve the same causal mechanism while differing in onset, duration, and retrieval-conditioned recovery?

## §4 Theoretical Anchors

### §4.1 Demand and Supply of Immediacy

| Field | Content |
|---|---|
| Full citation | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb04594.x |
| Key mechanism | Market liquidity is determined by the interaction between demand for immediacy and the limited capacity of intermediaries to supply it. |
| Key equation | `total_liquidity(t) = base_liquidity + sum(provides_liquidity_i(t))` |
| Motivates agent | market-maker, liquidity-seeker |
| Parameter implication | `base_liquidity` in [20, 60]; at least three market-maker instances for a visible withdrawal channel. |

### §4.2 Market and Funding Liquidity Spirals

| Field | Content |
|---|---|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism | Market liquidity and intermediary funding capacity reinforce each other, allowing liquidity to disappear suddenly under stress. |
| Key equation | `effective_lambda(t) = price_impact * 100 / max(total_liquidity(t), 10)` |
| Motivates agent | market-maker, liquidity-seeker |
| Parameter implication | `volatility_threshold` in [0.015, 0.03]; liquidity multiplier bounded at 10. |

### §4.3 Linear Price Impact

| Field | Content |
|---|---|
| Full citation | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 |
| Key mechanism | Net order flow moves price through a liquidity-dependent price-impact coefficient. |
| Key equation | `P(t+1) = P(t) + effective_lambda(t) * net_demand(t) + gamma * (F - P(t)) + epsilon(t)` |
| Motivates agent | market coordinator |
| Parameter implication | `price_impact` in [0.04, 0.10]; crisis impact should be 3-10 times the normal regime. |

### §4.4 Illiquidity as Return per Unit Volume

| Field | Content |
|---|---|
| Full citation | Amihud, Y. (2002). Illiquidity and stock returns: cross-section and time-series effects. *Journal of Financial Markets*, 5(1), 31-56. https://doi.org/10.1016/S1386-4181(01)00024-6 |
| Key mechanism | Absolute return per unit trading volume provides an observable proxy for price impact and market illiquidity. |
| Key equation | `MPI(t) = abs(return(t)) / max(volume(t), epsilon)` |
| Motivates agent | analysis and validation layer |
| Parameter implication | Report crisis-to-baseline MPI multiplier and reject non-finite values. |

### §4.5 Limits to Arbitrage and Momentum Amplification

| Field | Content |
|---|---|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x; De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| Key mechanism | Stabilizing capital is bounded while positive-feedback trading can amplify a shock before convergence occurs. |
| Key equation | `momentum_qty = clip(momentum_multiplier * return, -cap, cap)`; value liquidity activates only when `abs(deviation) > trade_threshold`. |
| Motivates agent | value-trader, momentum-trader |
| Parameter implication | `momentum_threshold` in [0.005, 0.02]; `trade_threshold` in [0.02, 0.06]. |

## §5 Stylized Facts

| # | Stylized Fact | Numeric Range | Primary Source | Acceptance Metric |
|---|---|---|---|---|
| F1 | A severe dry-up produces a low liquidity-ratio trough | minimum LRI in [0.05, 0.30] | Brunnermeier & Pedersen (2009) | `liquidity_ratio_index()` |
| F2 | Price impact rises sharply in the stress regime | crisis MPI / baseline MPI in [3, 10] | Kyle (1985); Amihud (2002) | `market_price_impact()` |
| F3 | A calibrated crisis persists but eventually recovers | longest dry-up in [10, 60] rounds | scenario calibration | `liquidity_persistence_duration()` |
| F4 | Momentum trading materially amplifies dislocation | no-momentum PAD at least 30% lower | De Long et al. (1990) | `peak_absolute_deviation()` ablation |
| F5 | Bounded value capital supplies a visible recovery channel | value-trader liquidity share in [0.15, 0.75] | Shleifer & Vishny (1997) | `liquidity_provision_index()` |

## §6 Historical / Empirical Anchors

| # | Event | Year | Core Mechanism | Scenario Mapping |
|---|---|---|---|---|
| H1 | Black Monday | 1987 | Program selling overwhelmed specialist capacity and coincided with withdrawal of bids | momentum-trader shock plus market-maker withdrawal |
| H2 | LTCM / Russian default turmoil | 1998 | Forced deleveraging met limited dealer balance-sheet capacity | liquidity-seeker demand plus bounded value liquidity |
| H3 | U.S. Treasury market turmoil | March 2020 | Widespread selling, reduced depth, wider spreads, and dealer constraints impaired even a normally deep market | full withdrawal-impact-recovery loop; Federal Reserve evidence: https://www.federalreserve.gov/monetarypolicy/2020-06-mpr-part2.htm |

## §7 Agent Roster

| # | Kebab Name | Theory Family | Market Role | Time Horizon | Risk Tolerance | Information | Determinism |
|---|---|---|---|---|---|---|---|
| 1 | market-maker | Market microstructure | Stabilizing until stress withdrawal | Short | Low | return, liquidity, inventory | Rule-deterministic / model-conditioned |
| 2 | liquidity-seeker | Liquidity spirals | Liquidity consuming | Short | High | liquidity and execution need | Stochastic-given-seed / model-conditioned |
| 3 | value-trader | Limits to arbitrage | Stabilizing | Medium-Long | Medium | price and fundamental | Rule-deterministic / model-conditioned |
| 4 | momentum-trader | Positive feedback | Destabilizing | Short | High | recent return | Rule-deterministic / model-conditioned |
| 5 | noise-trader | Noise trading | Neutral background flow | Short | High | no directional signal | Stochastic-given-seed / model-conditioned |

## §8 Environment Specification

### §8.1 Price Formation

`P(t+1) = P(t) + price_impact * liquidity_factor(t) * net_demand(t) + mean_reversion * (F - P(t)) + epsilon(t)`, where `liquidity_factor(t) = 100 / max(total_liquidity(t), 10)`.

### §8.2 Information Broadcast

The market broadcasts `{price, prev_price, return, fundamental, deviation, volume, net_demand, total_liquidity, liquidity_factor, round}` each round.

### §8.3 Constraints and Frictions

- Cash and long-position constraints apply to executable orders.
- Liquidity provision is non-negative and bounded by role.
- Effective price impact is capped by the liquidity floor.
- Invalid, missing, or non-finite decision fields are rejected rather than silently imputed.

### §8.4 Round Granularity

Star topology: the market coordinates one broadcast-decide-collect-clear cycle per round; investors operate in parallel after the market broadcast.

## §9 Parameter Seeds

| # | Parameter | Belongs to | Default | Empirical / Test Range | Source |
|---|---|---|---|---|---|
| 1 | initial_price | market | 100.0 | normalized | scenario normalization |
| 2 | fundamental_value | market | 100.0 | normalized | scenario normalization |
| 3 | price_impact | market | 0.08 | [0.04, 0.10] | Kyle (1985) mechanism calibration |
| 4 | mean_reversion | market | 0.015 | [0.005, 0.03] | slow fundamental anchor |
| 5 | noise_std | market | 0.4 | [0.1, 0.8] | scenario calibration |
| 6 | volatility_threshold | market-maker | 0.02 | [0.015, 0.03] | Brunnermeier & Pedersen (2009) stress trigger |
| 7 | base_liquidity | market-maker | 30.0 | [20, 60] | Grossman & Miller (1988) capacity |
| 8 | target_volatility | liquidity-seeker | 15.0 | [8, 25] | execution-demand calibration |
| 9 | liquidity_base | liquidity-seeker | 100.0 | [75, 150] | normal-depth normalization |
| 10 | trade_threshold | value-trader | 0.03 | [0.02, 0.06] | limits-to-arbitrage activation |
| 11 | base_liquidity_provision | value-trader | 20.0 | [10, 40] | bounded recovery capacity |
| 12 | value_multiplier | value-trader | 30.0 | [15, 60] | deviation sensitivity |
| 13 | momentum_threshold | momentum-trader | 0.01 | [0.005, 0.02] | De Long et al. (1990) |
| 14 | momentum_multiplier | momentum-trader | 200.0 | [100, 500] | positive-feedback calibration |
| 15 | noise_volatility | noise-trader | 10.0 | [5, 15] | Black (1986) background flow |
| 16 | initial_cash | all investors | 10000.0 | fixed parity seed | cross-variant resource parity |
| 17 | initial_position | all investors | 50.0 | fixed parity seed | enables symmetric buy/sell behavior |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes |
|---|---|---|
| Rule | Yes | Explicit threshold and quantity rules |
| LLM | Yes | Persona-conditioned decisions with the same five-agent taxonomy |
| RuleLLM | Yes | Explicit quantitative rules embedded under `== PERSONA ==` and `== DECISION RULES ==` |
| Rag | Yes | RuleLLM behavior plus retrieval, with explicit retrieval-failure accounting |

### §10.2 Pass / Fail Criteria

1. All four variants compile, import, load their YAML, and complete a five-round smoke run.
2. Every configuration agent key, identity, class, prompt, pool archetype, topology node, and documentation label uses the same canonical five-agent taxonomy.
3. Full runs contain finite prices, returns, liquidity, deviations, and analysis metrics; malformed model decisions are recorded as failures rather than filled with scientific defaults.
4. At least one calibrated run reaches LRI below 0.50 and subsequently recovers above 0.50; permanent or absent dry-up is a calibration failure.
5. The no-momentum ablation reduces peak absolute deviation by at least 30%, and the value-trader recovery channel produces a non-zero liquidity share.
