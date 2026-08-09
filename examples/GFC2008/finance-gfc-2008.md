# GFC2008

## §1 Meta

| Field       | Content                                                                                                                                                         |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | GFC2008                                                                                                                                                         |
| Domain      | finance                                                                                                                                                         |
| Phenomenon  | Securitized-credit fire-sale cascade: constant MBS supply and inflated ratings sustain a bubble, then leverage-driven forced selling triggers a systemic crash. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                                                      |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)                                                                                                         |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins with a market where structured-credit securities are being distributed at inflated valuations sustained by rating-driven demand. A moderate downward shock — cumulative supply from originators combined with a noise perturbation — pushes price below the rating-inflated fundamental, exposing leveraged holders to mark-to-market losses. The fundamental value is held constant so the collapse comes from balance-sheet and rating dynamics rather than a cash-flow shock.

### §2.2 Mechanism

The core mechanism is a securitized-credit fire-sale cascade. MBS originators steadily distribute inventory regardless of price, rating agencies buy against an inflated fundamental, and leveraged investors hold large positions that unwind through 50% fire sales once deviation breaches the margin-call threshold. Each fire-sale wave deepens the deviation, reactivating the margin trigger in later rounds and generating a cascade. Distressed buyers and a probabilistic regulator provide partial stabilization at deep discounts.

### §2.3 Participants

The causally relevant participants are MBS originators, rating agencies, leveraged investors, distressed buyers, and regulators. Originators supply persistent sell pressure; rating agencies sustain bubble demand; leveraged investors amplify the crash via forced fire sales; distressed buyers partially absorb the cascade below a discount threshold; the regulator is a probabilistic large buyer at extreme deviation. The market coordinator aggregates orders and updates the index price.

### §2.4 Resolution

The crash stops when leveraged inventory is exhausted by successive 50% fire sales, distressed buyers absorb enough supply at deep discounts, and the regulator's stochastic large-buy intervention lifts price back above the deepest thresholds. The resolution is a partial stabilization at a discount, not a full reversion to fundamental, because the constant originator supply and finite stabilizing capital prevent full recovery inside the round budget.

## §3 Research Goals

1. Measure whether constant originator supply plus rating-inflated demand plus 50% leveraged fire sales reproduces a systemic drawdown consistent with the 2008 −40% to −60% peak-to-trough range.
2. Test by ablation whether removing leveraged investors, rating agencies, or the regulator materially changes crash depth, cascade length, and residual mispricing after intervention.
3. Sweep `origination_rate`, `overrating_bias`, `margin_call_trigger`, and `rescue_probability` to map the boundary between bubble persistence, cascade escalation, and stabilized recovery.
4. Compare Rule, LLM, RuleLLM, and Rag variants to see whether persona reasoning or retrieved crisis literature shortens the bubble, dampens the cascade, or increases stabilizing demand timing.

## §4 Theoretical Anchors

### §4.1 Originate-to-distribute moral hazard

| Field                     | Content                                                                                                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Keys, B. J., Mukherjee, T., Seru, A., & Vig, V. (2010). Did securitization lead to lax screening? *Quarterly Journal of Economics*, 125(1), 307-362. https://doi.org/10.1162/qjec.2010.125.1.307 |
| Key mechanism (≤30 words) | Fee-income originators distribute securitized inventory at a constant rate regardless of price, creating persistent sell pressure independent of fundamentals.                                   |
| Key equation              | `sell_qty = int(position * origination_rate)` every round while position > 0.                                                                                                                    |
| Motivates agent           | mbs-originator                                                                                                                                                                                   |
| Parameter implication     | `origination_rate` 0.05-0.20 and `initial_position` 2000-10000 in §9.                                                                                                                            |

### §4.2 Rating agency conflict of interest

| Field                     | Content                                                                                                                                                                 |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Bolton, P., Freixas, X., & Shapiro, J. (2012). The credit ratings game. *Journal of Finance*, 67(1), 85-111. https://doi.org/10.1111/j.1540-6261.2011.01708.x           |
| Key mechanism (≤30 words) | Issuer-pays rating agencies inflate their perceived fundamental and buy structured securities whenever price is below the inflated benchmark, sustaining bubble demand. |
| Key equation              | `buy_qty = min(300, cash / price)` when `price < fundamental * (1 + overrating_bias) * 0.95`.                                                                           |
| Motivates agent           | rating-agency                                                                                                                                                           |
| Parameter implication     | `overrating_bias` 0.10-0.40 with candidate default 0.20 in §9.                                                                                                          |

### §4.3 Leverage cycle and margin-spiral fire sales

| Field                     | Content                                                                                                                                                                          |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098       |
| Key mechanism (≤30 words) | Leveraged holders forced-sell half of their remaining position when deviation breaches the margin trigger, deepening the deviation and re-arming the trigger for the next round. |
| Key equation              | `fire_sale_qty = int(position * 0.50)` when `deviation < -margin_call_trigger`.                                                                                                  |
| Motivates agent           | leveraged-investor                                                                                                                                                               |
| Parameter implication     | `margin_call_trigger` 0.05-0.20 with candidate default 0.10 in §9.                                                                                                               |

### §4.4 Distressed-capital price floor

| Field                     | Content                                                                                                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Griffin, J. M., & Xu, J. (2009). How smart are the smart guys? A unique view from hedge fund stock holdings. *Review of Financial Studies*, 22(7), 2531-2570. https://doi.org/10.1093/rfs/hhp003 |
| Key mechanism (≤30 words) | Distressed buyers deploy a bounded share of cash into deeply discounted structured credit once deviation crosses their discount threshold.                                                       |
| Key equation              | `buy_qty = min(1000, int(cash * 0.30 / price))` when `deviation < -discount_threshold`.                                                                                                          |
| Motivates agent           | distressed-buyer                                                                                                                                                                                 |
| Parameter implication     | `discount_threshold` 0.10-0.30 with candidate default 0.20 in §9.                                                                                                                                |

### §4.5 Probabilistic lender-of-last-resort intervention

| Field                     | Content                                                                                                                                                                |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002             |
| Key mechanism (≤30 words) | A public backstop enters with a large fixed buy only under extreme deviation and only with probability less than one, capturing political uncertainty around bailouts. |
| Key equation              | `buy rescue_size` when `deviation < -intervention_threshold` and `Uniform() < rescue_probability`.                                                                     |
| Motivates agent           | regulator                                                                                                                                                              |
| Parameter implication     | `intervention_threshold` 0.15-0.60, `rescue_size` 100-3000, `rescue_probability` 0.20-0.60 in §9.                                                                      |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                              | Quantitative range                  | Citation                                                        | Acceptance metric                                               |
|----|----------------------------------------------------------------------------------|-------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|
| F1 | The simulated index experiences a crisis-scale drawdown.                         | 30% <= max drawdown <= 60%          | Brunnermeier (2009), https://doi.org/10.1257/jep.23.1.77        | `analysis.py: _compute_max_drawdown()` in [30, 60]              |
| F2 | Leveraged fire sales dominate cascade-round sell volume.                         | leveraged sell share >= 40%         | Adrian & Shin (2010), https://doi.org/10.1016/j.jfi.2008.12.002 | `analysis.py: agent_vwap` leveraged-investor sell share >= 0.40 |
| F3 | Bubble phase maintains positive deviation from fundamental before the cascade.   | mean pre-cascade deviation >= 5%    | Gorton (2010)                                                   | `analysis.py: _compute_pre_cascade_deviation()` >= 0.05         |
| F4 | Regulator intervention produces a discrete recovery footprint when it activates. | recovery jump >= 3% within 5 rounds | Bernanke (2015), *The Courage to Act*                           | `analysis.py: _compute_intervention_rebound()` >= 0.03          |

## §6 Historical / Empirical Anchors

### §6.1 Lehman Brothers bankruptcy and post-Lehman credit freeze

| Field             | Content                                                                                                                                                                                                                  |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Lehman Brothers bankruptcy, 2008-09-15; subsequent global credit-market freeze through Q4 2008.                                                                                                                          |
| Trigger           | Repo counterparties refused to roll over Lehman's overnight funding as MBS collateral values fell, triggering the largest US bankruptcy on record.                                                                       |
| Quantitative arc  | S&P 500 fell roughly 40% from September 2008 to March 2009; TED spread spiked by more than 300 bps; global commercial-paper market contracted sharply within one week.                                                   |
| Agent mapping     | mbs-originator maps to continued distribution into declining prices; leveraged-investor maps to Lehman-like forced fire sales; regulator maps to TARP-era interventions with realized rescue_probability well below one. |
| Primary source(s) | Gorton (2010), *Slapped by the Invisible Hand: The Panic of 2007*, Oxford University Press.                                                                                                                              |

### §6.2 Rating-inflated MBS bubble 2004-2007

| Field             | Content                                                                                                                                                                                 |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Systematic AAA rating of subprime CDOs, 2004-2007.                                                                                                                                      |
| Trigger           | Issuer-pays incentives and complex tranche opacity drove sustained rating inflation on structured pools of subprime mortgages.                                                          |
| Quantitative arc  | Approximately 1.3 trillion USD in CDO issuance over 2004-2007; more than 90% of subprime CDO tranches rated AAA; realized loss rates of 40-60% in high-stress scenarios.                |
| Agent mapping     | rating-agency maps to demand at an inflated fundamental; mbs-originator maps to constant supply; together they sustain positive deviation before the leveraged-investor cascade begins. |
| Primary source(s) | Bolton, Freixas, & Shapiro (2012), https://doi.org/10.1111/j.1540-6261.2011.01708.x                                                                                                     |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart       | Theory family (§4 anchor)                   | Domain role   | Primary signals                     | Intent line                                                                    | Expected pool match                               |
|--------------------|------------------------------|---------------------------------------------|---------------|-------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------|
| mbs-originator     | securitization desk / bank   | Fee-income / Originate-to-distribute (§4.1) | Destabilising | position, origination_rate          | Exists to distribute securitized inventory at a constant rate.                 | masim/agents/defines/finance/mbs-originator.md     |
| rating-agency      | credit rating agency         | Rating inflation / Issuer-pays (§4.2)       | Destabilising | price, fundamental, overrating_bias | Exists to buy against an inflated fundamental until price is well below it.    | masim/agents/defines/finance/rating-agency.md      |
| leveraged-investor | hedge fund / investment bank | Leverage cycle / Margin spiral (§4.3)       | Destabilising | price, deviation, position          | Exists to fire-sell half of remaining position when deviation crosses trigger. | masim/agents/defines/finance/leveraged-investor.md |
| distressed-buyer   | distressed / vulture fund    | Distressed-capital floor (§4.4)             | Stabilising   | price, deviation, cash              | Exists to buy deep-discount inventory once deviation crosses discount level.   | masim/agents/defines/finance/distressed-buyer.md   |
| regulator          | central bank / Treasury      | Lender-of-last-resort / Backstop (§4.5)     | Stabilising   | deviation, rng_state, rescue_size   | Exists to inject probabilistic large purchases at extreme deviation.           | masim/agents/defines/finance/regulator.md          |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a single-price structured-credit market. Price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where `D(t)` is buy quantity minus sell quantity. The price-impact coefficient is moderate to represent an illiquid structured-credit market, and mean reversion is slow so cascade dynamics dominate short-run price formation.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, and `round`. These signals are sufficient for the constant-rate origination, inflated-fundamental buying, margin-trigger fire sales, discount-threshold buying, and probabilistic-intervention mechanisms.

### §8.3 Constraints and Frictions

There is no circuit breaker. Agents are constrained by cash, inventory, base order size, and per-round buy caps (rating-agency: 300; distressed-buyer: 1000; regulator: rescue_size). The market applies a constant fundamental value so the crash comes from balance-sheet and rating mechanics rather than a cash-flow shock.

### §8.4 Round Granularity

One round represents a short trading window in which supply, demand, and forced-liquidation orders are aggregated. The default round budget is calibrated to cover a bubble phase, cascade escalation, distressed absorption, and probabilistic regulator interventions, in analogy with the 2008 acute-crisis timeline compressed into a fixed-length simulation.

## §9 Parameter Seeds

| Parameter              | Symbol       | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                                                             |
|------------------------|--------------|----------------------------------|-----------------|-------------------|-------------------------------------------------------------------------------------------------------------|
| origination rate       | `r_orig`     | mbs-originator (§7)              | 0.05-0.20       | 0.08              | Keys, Mukherjee, Seru, & Vig (2010), https://doi.org/10.1162/qjec.2010.125.1.307                            |
| overrating bias        | `b_rate`     | rating-agency (§7)               | 0.10-0.40       | 0.20              | Bolton, Freixas, & Shapiro (2012), https://doi.org/10.1111/j.1540-6261.2011.01708.x                         |
| margin-call trigger    | `theta_mc`   | leveraged-investor (§7)          | 0.05-0.20       | 0.10              | Brunnermeier & Pedersen (2009), https://doi.org/10.1093/rfs/hhn098                                          |
| discount threshold     | `theta_disc` | distressed-buyer (§7)            | 0.10-0.30       | 0.20              | Griffin & Xu (2009), https://doi.org/10.1093/rfs/hhp003                                                     |
| intervention threshold | `theta_int`  | regulator (§7)                   | 0.15-0.60       | 0.50              | Adrian & Shin (2010), https://doi.org/10.1016/j.jfi.2008.12.002                                             |
| rescue size            | `q_rescue`   | regulator (§7)                   | 100-3000        | 500               | Bernanke (2015), *The Courage to Act*                                                                       |
| rescue probability     | `p_rescue`   | regulator (§7)                   | 0.20-0.60       | 0.60              | Political-economy uncertainty of bailout timing                                                             |
| price impact           | `lambda`     | environment (§8.1)               | 0.001-0.050     | 0.04              | Kyle (1985), https://doi.org/10.2307/1913210                                                                |
| mean reversion         | `gamma`      | environment (§8.1)               | 0.005-0.05      | 0.005             | Slow mean-reversion in crisis; Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| noise std              | `sigma`      | environment (§8.1)               | 0.005-0.030     | 0.015             | Roll (1984), https://doi.org/10.1111/j.1540-6261.1984.tb03897.x                                             |
| fundamental value      | `F`          | environment (§8.1)               | 60-100          | 100.0             | Source: normalization                                                                                       |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                                                    |
|---------|--------|----------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the securitized-credit fire-sale cascade.                                              |
| LLM     | Yes    | Tests whether persona reasoning delays the bubble or dampens the cascade relative to the deterministic baseline.           |
| RuleLLM | Yes    | Tests whether explicit rule prompts preserve the cascade dynamics under model reasoning.                                   |
| Rag     | Yes    | Tests whether retrieved crisis literature (Gorton 2010, Brunnermeier 2009) changes bubble persistence or intervention use. |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
