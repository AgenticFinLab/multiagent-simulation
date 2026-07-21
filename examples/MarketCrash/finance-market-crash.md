# Market Crash - Scenario Target

## §1 Meta

| Field | Content |
|---|---|
| Name | MarketCrash |
| Domain | finance |
| Phenomenon | Volatility-sensitive deleveraging and panic sales exhaust dealer liquidity, amplify price declines, and eventually attract patient stabilising capital. |
| Pipeline | masim/skills/create-simulation-pipeline.md |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2) |

## §2 Phenomenon Statement

### §2.1 Trigger

The market begins in a stressed state in which realised volatility is above the risk target used by systematic funds. Risk-parity funds therefore reduce exposure while leveraged hedge funds face worsening leverage and funding capacity. Their first sales push prices below the recent reference level and reduce immediately available liquidity. The trigger is a balance-sheet adjustment under stress, not an unexplained news jump.

### §2.2 Mechanism

The central mechanism is a volatility-deleveraging-liquidity feedback loop. Falling prices raise measured volatility and portfolio losses, which induce risk-parity scaling, leveraged liquidation, and loss-averse panic sales. Simultaneous orders consume dealer capacity, so each unit of net selling has greater price impact as liquidity falls. The larger price decline then triggers additional selling in the next round.

### §2.3 Participants

Risk-parity funds transmit volatility into mechanical exposure changes, while leveraged hedge funds transmit losses into forced sales. Panic sellers amplify salient drawdowns, and market makers provide liquidity only while their inventory capacity permits. Passive investors adjust slowly and therefore supply little immediate offset during the acute phase. Bottom fishers enter after sufficiently large discounts and represent delayed stabilising demand.

### §2.4 Resolution

The decline ends when forced selling is exhausted and net demand ceases to be persistently negative. Dealer liquidity then recovers gradually, reducing the price impact of subsequent orders. Passive rebalancing and bottom-fisher purchases become large enough to offset residual sales. Price may recover only partially because the experiment studies market functioning rather than imposing a guaranteed return to the starting value.

## §3 Research Goals

1. How strongly does the initial volatility stress determine maximum drawdown and crash speed in a parameter sweep?
2. Does removing the market-maker archetype materially worsen minimum liquidity and one-round price loss in an ablation?
3. How much of cumulative selling is attributable to risk-parity, leveraged, and panic-selling channels?
4. Do Rule, LLM, RuleLLM, and Rag variants preserve the same qualitative crash and stabilisation sequence?

## §4 Theoretical Anchors

### §4.1 Volatility-managed exposure

| Field | Content |
|---|---|
| Full citation | Moreira, A., & Muir, T. (2017). Volatility-Managed Portfolios. *Journal of Finance*, 72(4), 1611-1644. https://doi.org/10.1111/jofi.12513 |
| Key mechanism (≤50 words) | Optimal risky exposure falls when conditional variance rises, so volatility-sensitive strategies sell after volatility increases. |
| Key equation | `w_t = k / sigma_t^2`, where `w_t` is risky exposure, `sigma_t` is conditional volatility, and `k` is a risk-budget constant. |
| Motivates agent | risk-parity-fund |
| Parameter implication | The volatility target and adjustment speed imply a target band of 1.5-3.0 simulation volatility units and a scaling speed of 0.1-0.5 per round. |

### §4.2 Funding-liquidity spiral

| Field | Content |
|---|---|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market Liquidity and Funding Liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤50 words) | Losses tighten funding constraints and force sales; declining market liquidity increases margins and price impact, creating a mutually reinforcing spiral. |
| Key equation | `q_t <= capital_t / margin_t`, where `q_t` is the funded position and higher stress raises `margin_t`, reducing feasible exposure. |
| Motivates agent | leveraged-hedge-fund; market-maker |
| Parameter implication | Leverage of 1.5-3.0 and a minimum liquidity ratio of 0.05-0.30 produce bounded stress amplification. |

### §4.3 Slow-moving capital

| Field | Content |
|---|---|
| Full citation | Duffie, D. (2010). Asset Price Dynamics with Slow-Moving Capital. *Journal of Finance*, 65(4), 1237-1267. https://doi.org/10.1111/j.1540-6261.2010.01569.x |
| Key mechanism (≤50 words) | Capital reaches dislocated markets with delay, allowing temporary price deviations before patient investors restore demand. |
| Key equation | `K_(t+1) = K_t + eta(K* - K_t)`, where `K_t` is deployed stabilising capital and `eta` is the adjustment rate. |
| Motivates agent | passive-investor |
| Parameter implication | Rebalancing every 10-30 rounds represents deliberately slow capital adjustment at the simulation cadence. |

### §4.4 Prospect-theory selling

| Field | Content |
|---|---|
| Full citation | Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185 |
| Key mechanism (≤50 words) | Losses relative to a reference point receive greater decision weight than comparable gains, making sharp drawdowns disproportionately salient. |
| Key equation | `v(x) = x^alpha` for gains and `v(x) = -lambda(-x)^beta` for losses, with `lambda > 1`. |
| Motivates agent | panic-seller |
| Parameter implication | A panic threshold of 3%-12% and loss sensitivity above one operationalise asymmetric reactions to drawdowns. |

### §4.5 Contrarian value demand

| Field | Content |
|---|---|
| Full citation | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian Investment, Extrapolation, and Risk. *Journal of Finance*, 49(5), 1541-1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x |
| Key mechanism (≤50 words) | Contrarian investors purchase securities after sufficiently large price declines when expected value exceeds the distressed market price. |
| Key equation | `buy_t > 0` when `(F - P_t) / F >= d*`, where `F` is fundamental value and `d*` is the discount threshold. |
| Motivates agent | bottom-fisher |
| Parameter implication | A value-entry discount of 8%-30% and order sizes of 5-25 units create delayed, bounded stabilisation. |

## §5 Stylized Facts

| # | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|---|---|---|---|---|
| F1 | Stress produces a material peak-to-trough decline. | 10% ≤ maximum drawdown ≤ 75% | FSB (2020), *Holistic Review of the March Market Turmoil*, https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/ | `analysis.py: maximum_drawdown()` ∈ [0.10, 0.75] |
| F2 | The crash contains at least one discontinuously severe simulation round. | largest one-round loss ≥ 2% | FSB (2020), https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/ | `analysis.py: largest_one_round_drop()` ≥ 0.02 |
| F3 | Liquidity deteriorates substantially during the acute selling phase. | minimum liquidity ratio ≤ 0.50 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 | `analysis.py: minimum_liquidity()` ≤ 0.50 |
| F4 | Volatility remains strongly state-dependent across the stress and recovery phases. | peak volatility / run volatility floor ≥ 1.5 | Moreira & Muir (2017), https://doi.org/10.1111/jofi.12513 | `analysis.py: volatility_spike_ratio()` ≥ 1.5 |
| F5 | Stabilising value demand activates only after the decline is underway. | bottom-fisher buy volume > 0 after drawdown ≥ 10% | Lakonishok et al. (1994), https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | `analysis.py: bottom_fisher_absorption()` > 0 |

## §6 Historical / Empirical Anchors

### §6.1 March 2020 global market turmoil

| Field | Content |
|---|---|
| Name + dates | March 2020 global market turmoil, 2020-02-24 to 2020-03-23 |
| Trigger | Pandemic-related repricing generated a rush for cash and portfolio rebalancing across normally liquid markets. |
| Quantitative arc | The S&P 500 fell about 34% from its February peak to its March trough; FSB reports indicate that ten-year U.S. Treasury market depth fell about 93% from its February average before policy support restored functioning. |
| Agent mapping | Risk-parity funds map to volatility-targeting strategies; leveraged hedge funds to relative-value funds reducing positions; market makers to constrained dealers; passive investors to benchmarked long-only funds; panic sellers to investors raising cash; bottom fishers to patient buyers entering after dislocation. |
| Primary source(s) | Financial Stability Board (2020), *Holistic Review of the March Market Turmoil*, https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/; Board of Governors of the Federal Reserve System (2020), https://www.federalreserve.gov/monetarypolicy/2020-06-mpr-part2.htm |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|---|---|---|---|---|---|---|
| risk-parity-fund | volatility-targeting multi-asset fund | Volatility-managed exposure (§4.1) | Destabilising | price, volatility, round | Exists to translate elevated volatility into systematic exposure reduction. | examples/AGENT_POOL/finance/risk-parity-fund.md |
| leveraged-hedge-fund | leveraged relative-value hedge fund | Funding-liquidity spiral (§4.2) | Destabilising | price, leverage, liquidity | Exists to transmit losses and funding pressure into forced liquidation. | examples/AGENT_POOL/finance/leveraged-hedge-fund.md |
| market-maker | securities dealer | Funding-liquidity spiral (§4.2) | Context-dependent | price, liquidity, net demand | Exists to absorb order imbalance until inventory and liquidity constraints bind. | examples/AGENT_POOL/finance/market-maker.md |
| passive-investor | benchmarked long-only fund | Slow-moving capital (§4.3) | Stabilising | price, fundamental, round | Exists to rebalance slowly toward a strategic allocation. | examples/AGENT_POOL/finance/passive-investor.md |
| panic-seller | loss-sensitive retail or discretionary investor | Prospect-theory selling (§4.4) | Destabilising | price, drawdown, volatility | Exists to amplify salient losses through threshold-driven selling. | examples/AGENT_POOL/finance/panic-seller.md |
| bottom-fisher | contrarian value investor | Contrarian value demand (§4.5) | Stabilising | price, fundamental, drawdown | Exists to supply delayed demand after a sufficiently deep discount. | examples/AGENT_POOL/finance/bottom-fisher.md |

## §8 Environment Specification

### §8.1 Price Formation

A single-asset dealer market aggregates signed orders once per round. Net order flow moves price through linear impact, while mean reversion provides a weak fundamental anchor. Effective price impact rises when liquidity is depleted, consistent with the funding-liquidity mechanism in §4.2.

### §8.2 Information Broadcast

Every round broadcasts price, previous price, fundamental value, deviation, return, volatility, liquidity, volume, net demand, drawdown, and round. Price and return support portfolio adjustment; volatility activates risk targeting; liquidity reveals dealer capacity; drawdown activates loss-sensitive and value-demand channels. All participants receive the same market snapshot.

### §8.3 Constraints and Frictions

Short selling is No because this experiment isolates long-position liquidation. Margin pressure is Yes through the leveraged fund's exposure constraint. Circuit breakers are No so the endogenous feedback loop remains observable. Trading is synchronous, cash and position constraints are enforced, and liquidity recovers only gradually after imbalance subsides.

### §8.4 Round Granularity

One round represents approximately one stressed trading interval rather than a full day. Two hundred rounds cover an acute event, the liquidation cascade, and early stabilisation. The short cadence is justified by the rapid deterioration and recovery of market depth documented during March 2020.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|---|---|---|---|---|---|
| initial price | `P0` | environment (§8.1) | 100 normalised units | 100 | Source: normalization |
| initial stress volatility | `sigma0` | environment (§8.2) | 2.0-4.0 units | 4.0 | Moreira & Muir (2017), https://doi.org/10.1111/jofi.12513 |
| stressed impact multiplier | `m_L` | environment (§8.1) | 1.0-2.0 | 1.5 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| maximum one-round absolute return | `r_max` | environment (§8.3) | 5%-10% | 8% | FSB (2020), https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/ |
| normalized price domain | `[P_min,P_max]` | environment (§8.1) | [20, 150] units | [30, 120] | FSB (2020) stress-arc calibration, https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/ |
| base price impact | `lambda` | environment (§8.1) | 0.02-0.10 per normalised net-order unit | 0.08 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| liquidity decay | `delta_L` | environment (§8.3) | 0.05-0.20 per stressed round | 0.10 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| liquidity recovery | `rho_L` | environment (§8.3) | 0.02-0.10 per quiet round | 0.05 | FSB (2020), https://www.fsb.org/2020/11/holistic-review-of-the-march-market-turmoil/ |
| target volatility | `sigma*` | risk-parity-fund | 1.5-3.0 units | 2.0 | Moreira & Muir (2017), https://doi.org/10.1111/jofi.12513 |
| leverage multiplier | `ell` | leveraged-hedge-fund | 1.5-3.0 | 2.0 | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098 |
| rebalancing frequency | `T_R` | passive-investor | 10-30 rounds | 20 | Duffie (2010), https://doi.org/10.1111/j.1540-6261.2010.01569.x |
| panic threshold | `d_P` | panic-seller | 3%-12% drawdown | 5% | Kahneman & Tversky (1979), https://doi.org/10.2307/1914185 |
| bottom-fishing threshold | `d_B` | bottom-fisher | 8%-30% discount | 8% | Lakonishok et al. (1994), https://doi.org/10.1111/j.1540-6261.1994.tb04772.x |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≥1 sentence) |
|---|---|---|
| Rule | Yes | Provides the deterministic, mechanism-isolating baseline required by all four research goals. |
| LLM | Yes | Tests whether unconstrained persona reasoning preserves the crash sequence in research goal 4. |
| RuleLLM | Yes | Tests whether explicit guardrails improve behavioural fidelity while retaining model-based reasoning. |
| Rag | Yes | Grounds decisions in the March 2020 anchor and supports the cross-variant comparison in research goal 4. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|---|---|
| All §5 stylized facts reproduced within their ranges | green |
| Every §3 research question answerable from analysis | green |
| Ablating any §7 agent produces a measurable change | green |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green |
