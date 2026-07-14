# GameStopShortSqueeze

## §0 Meta CHANGELOG

| Date | Step | Evidence |
|------|------|----------|
| 2026-07-20 | Step 2 icon-completeness | Generated 5 PNGs (`finance-retail-coordinated.png`, `finance-short-seller-hf.png`, `finance-market-maker-gamma.png`, `finance-institutional-value.png`, `finance-momentum-retail.png`); added mapping rows #94–#98 to `agent_images/design.md`; verified Icon rows in all 5 pool profiles (`retail-coordinated.md`, `short-seller-hf.md`, `market-maker-gamma.md`, `institutional-value.md`, `momentum-retail.md`). |
| 2026-07-20 | Step 4 py_compile+import | `py_compile` clean on `Rule/players.py`, `LLM/players.py`, `RuleLLM/players.py`, `Rag/players.py` plus all `analysis.py`; `import examples.GameStopShortSqueeze.{Rule,LLM,RuleLLM,Rag}.players` all pass. |
| 2026-07-20 | Steps 5-10 smoke | Rule: `GeneralSimulator.setup()+run()+shutdown()` with `total_rounds=5` — PASS (no uncaught exceptions). LLM/RuleLLM/Rag: `setup()+shutdown()` — PASS. |
| 2026-07-20 | Closeout | Status `locked → released`. Traceability matrix resolved; 5 agents × 4 icon checks = 20 checks green. |
| 2026-07-20 | Round 2 re-audit | Icon-completeness 20/20 green; py_compile 8/8 (4 players + 4 analysis); import smoke 4/4; Rule 5-round e2e PASS; LLM/RuleLLM/Rag setup-only PASS. No defects found. |

## §1 Meta

| Field       | Content                                                                                                                                                                              |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | GameStopShortSqueeze                                                                                                                                                                 |
| Domain      | finance                                                                                                                                                                              |
| Status      | released                                                                                                                                                                             |
| Phenomenon  | Coordinated retail buying combined with forced short covering and options-driven gamma hedging generates a three-way self-reinforcing squeeze that overwhelms institutional selling. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                                                                           |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)                                                                                                                              |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins with a heavily shorted stock at fundamental value and a large coordinated retail cohort holding sufficient cash to press the market. Coordinated buying by the retail agent pushes price above the short seller's covering threshold, initiating the squeeze cascade. The fundamental value is held constant so the +1,700% magnitude derives from balance-sheet and hedging mechanics rather than any cash-flow revision.

### §2.2 Mechanism

The core mechanism is a three-way buying coalition against a finite institutional seller. Coordinated retail buys aggressively while cash capacity remains high; the short seller is forced to cover once deviation exceeds its pain threshold, adding mechanical buying pressure; the options market maker delta-hedges against rising price and adds gamma-scaled buying that grows non-linearly with deviation. The FOMO cohort activates once deviation crosses a visibility threshold. The institutional value seller provides stabilizing supply once overvaluation crosses its sell threshold, but is overwhelmed because its inventory is finite while the buying coalition self-reinforces.

### §2.3 Participants

The causally relevant participants are coordinated retail buyers, short-selling hedge funds with pre-existing short exposure, options market makers with short-gamma books, institutional value sellers, and late-cycle FOMO retail buyers. The market coordinator aggregates orders and updates the index price.

### §2.4 Resolution

The squeeze halts when the coordinated retail cohort's cash falls below the coordination threshold, the short-seller's remaining short exposure is exhausted through successive 50% covers, and the institutional value seller absorbs enough of the peak. Because gamma exposure is fixed and mean reversion is slow, the resolution is a partial retracement rather than a full reversion to fundamental within the round budget.

## §3 Research Goals

1. Measure whether the three-way buying coalition reproduces a squeeze magnitude consistent with the GameStop 2021 +1,700% peak or the Volkswagen 2008 +380% event.
2. Test by ablation whether removing the short seller, the gamma market maker, or the coordinated retail agent materially changes squeeze peak, cascade duration, and residual mispricing.
3. Sweep `buy_pressure`, `cover_threshold`, `gamma_exposure`, and `sell_threshold` to map the boundary between contained overshoot, sustained squeeze, and extreme mispricing.
4. Compare Rule, LLM, RuleLLM, and Rag variants to see whether persona reasoning or retrieved squeeze literature reduces peak deviation or shortens the squeeze.

## §4 Theoretical Anchors

### §4.1 Short-sale constraint and forced-cover cascade

| Field                     | Content                                                                                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jones, C. M., & Lamont, O. A. (2002). Short-sale constraints and stock returns. *Journal of Financial Economics*, 66(2-3), 207-239. https://doi.org/10.1016/S0304-405X(02)00224-6 |
| Key mechanism (≤30 words) | Constrained short sellers are forced to cover half of their remaining short exposure when deviation exceeds the cover threshold, adding buy pressure that re-arms the trigger.    |
| Key equation              | `cover_qty = int(abs(position) * 0.5)` when `position < 0` and `deviation > cover_threshold`.                                                                                     |
| Motivates agent           | short-seller-hf                                                                                                                                                                   |
| Parameter implication     | `initial_position` −200 to −1000 with default −1000 and `cover_threshold` 0.05-0.50 with default 0.05 in §9.                                                                      |

### §4.2 Options gamma squeeze and market-maker hedging

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Jarrow, R. A., & Li, S. (2021). Short squeeze risk. *Annals of Finance*, 17, 635-659. https://doi.org/10.1007/s10436-021-00394-2                                           |
| Key mechanism (≤30 words) | Short-gamma market makers must buy the underlying at a rate proportional to deviation to stay delta-neutral, adding non-linear buying pressure that grows with mispricing. |
| Key equation              | `hedge_qty = int(abs(deviation) * gamma_exposure * 5000)`; buy `min(hedge_qty, cash / price)` when `deviation > 0`.                                                        |
| Motivates agent           | market-maker-gamma                                                                                                                                                         |
| Parameter implication     | `gamma_exposure` 0.30-2.00 with default 0.30 in §9, calibrated against Hu et al. (2021) options-flow amplification.                                                        |

### §4.3 Social-coordination retail buying

| Field                     | Content                                                                                                                                                                                         |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Lyocsa, S., Baumohl, E., & Vyrost, T. (2022). YOLO trading: Riding with the herd during the GameStop episode. *Finance Research Letters*, 47, 102785. https://doi.org/10.1016/j.frl.2022.102785 |
| Key mechanism (≤30 words) | A coordinated retail cohort deploys a bounded share of its cash into aggressive buying whenever collective cash capacity per unit of price remains large enough to move the market.             |
| Key equation              | `buy_qty = min(int(cash * buy_pressure / price), 500)` when `cash > price * 50`.                                                                                                                |
| Motivates agent           | retail-coordinated                                                                                                                                                                              |
| Parameter implication     | `buy_pressure` 0.10-0.50 with default 0.12 in §9.                                                                                                                                               |

### §4.4 Fundamental-value selling and limits to arbitrage

| Field                     | Content                                                                                                                                                      |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x        |
| Key mechanism (≤30 words) | A finite-inventory fundamental seller sells at extreme overvaluation but is overwhelmed by the self-reinforcing buying coalition once inventory is depleted. |
| Key equation              | `sell_qty = min(1000, position)` when `position > 0` and `deviation > sell_threshold`.                                                                       |
| Motivates agent           | institutional-value                                                                                                                                          |
| Parameter implication     | `sell_threshold` 0.30-1.00 with default 0.30 and `initial_position` +500 to +2000 with default +2000 in §9.                                                  |

### §4.5 Attention-driven FOMO momentum

| Field                     | Content                                                                                                                                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Barber, B. M., Huang, X., Odean, T., & Schwarz, C. (2022). Attention-induced trading and returns: Evidence from Robinhood users. *Journal of Finance*, 77(6), 3141-3190. https://doi.org/10.1111/jofi.13183 |
| Key mechanism (≤30 words) | Late-arriving retail buys once deviation is large enough to attract social-media attention, adding a small, capped momentum flow that extends the squeeze.                                                  |
| Key equation              | `buy_qty = min(50, cash / price)` when `deviation > fomo_threshold`.                                                                                                                                        |
| Motivates agent           | momentum-retail                                                                                                                                                                                             |
| Parameter implication     | `fomo_threshold` 0.05-0.30 with default 0.05 in §9.                                                                                                                                                         |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                       | Quantitative range                 | Citation                                                                     | Acceptance metric                                                      |
|----|-------------------------------------------------------------------------------------------|------------------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------|
| F1 | The simulated index experiences an extreme upward peak versus fundamental.                | max deviation >= 100%              | Lyocsa et al. (2022), https://doi.org/10.1016/j.frl.2022.102785              | `analysis.py: _compute_max_deviation()` >= 1.00                        |
| F2 | Short-covering buys dominate the initial squeeze rounds.                                  | short-seller buy share >= 30%      | Jones & Lamont (2002), https://doi.org/10.1016/S0304-405X(02)00224-6         | `analysis.py: agent_vwap` short-seller-hf buy share >= 0.30 in squeeze |
| F3 | Gamma-hedging buys scale with deviation once price is above fundamental.                  | correlation(hedge_qty, dev) >= 0.5 | Jarrow & Li (2021), https://doi.org/10.1007/s10436-021-00394-2               | `analysis.py: _compute_gamma_scaling()` >= 0.50                        |
| F4 | Institutional value selling is insufficient to reverse the squeeze before inventory ends. | residual deviation at peak >= 50%  | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | `analysis.py: _compute_residual_peak_deviation()` >= 0.50              |

## §6 Historical / Empirical Anchors

### §6.1 GameStop short squeeze January 2021

| Field             | Content                                                                                                                                                                                                                              |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | GameStop (GME) short squeeze, 2021-01-13 to 2021-02-05.                                                                                                                                                                              |
| Trigger           | WallStreetBets-coordinated retail buying against a 140%-of-float short interest, combined with heavy retail purchases of out-of-the-money call options.                                                                              |
| Quantitative arc  | GME rose from about 20 USD to 483 USD (+1,700%) in fourteen trading days; Melvin Capital lost roughly 53% in January 2021; peak market capitalization exceeded 30 billion USD versus a fundamental estimate near 1 billion USD.      |
| Agent mapping     | retail-coordinated maps to WSB buyers; short-seller-hf maps to Melvin-style forced covering; market-maker-gamma maps to CBOE dealers hedging short-gamma books; institutional-value maps to fundamental sellers overwhelmed at peak. |
| Primary source(s) | Lyocsa, Baumohl, & Vyrost (2022), https://doi.org/10.1016/j.frl.2022.102785                                                                                                                                                          |

### §6.2 Volkswagen October 2008 short squeeze

| Field             | Content                                                                                                                                                                                                                      |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Volkswagen AG (VW) short squeeze, 2008-10-28 to 2008-10-29.                                                                                                                                                                  |
| Trigger           | Porsche disclosed a 74.1% economic ownership stake in VW while short interest stood near 12% of a float that shrank to under 6%, leaving short sellers with essentially no borrowable stock.                                 |
| Quantitative arc  | VW ordinary shares rose from about 210 EUR to about 1,005 EUR in two trading days (+380%); estimated hedge-fund losses exceeded 30 billion EUR.                                                                              |
| Agent mapping     | short-seller-hf maps to trapped European hedge funds forced to cover into a shrinking float; institutional-value maps to a strategic holder whose position eliminates the corrective mechanism rather than providing supply. |
| Primary source(s) | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098                                                   |

## §7 Agent Roster

| Agent name (kebab)  | Real-world counterpart         | Theory family (§4 anchor)                      | Domain role   | Primary signals                 | Intent line                                                                      | Expected pool match                                |
|---------------------|--------------------------------|------------------------------------------------|---------------|---------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------|
| retail-coordinated  | WSB retail cohort              | Social coordination / attention (§4.3)         | Destabilising | cash, price, buy_pressure       | Exists to deploy coordinated cash into aggressive buying while capacity holds.   | examples/AGENT_POOL/finance/retail-coordinated.md  |
| short-seller-hf     | Melvin-style short hedge fund  | Short-sale constraint / forced cover (§4.1)    | Destabilising | position, deviation             | Exists to cover half of remaining short exposure once deviation crosses trigger. | examples/AGENT_POOL/finance/short-seller-hf.md     |
| market-maker-gamma  | Options market-maker desk      | Gamma squeeze / delta hedging (§4.2)           | Destabilising | deviation, gamma_exposure, cash | Exists to buy underlying to stay delta-neutral against short-gamma exposure.     | examples/AGENT_POOL/finance/market-maker-gamma.md  |
| institutional-value | Fundamental long-only investor | Fundamental value / limits to arbitrage (§4.4) | Stabilising   | deviation, position             | Exists to sell into extreme overvaluation until inventory is depleted.           | examples/AGENT_POOL/finance/institutional-value.md |
| momentum-retail     | Robinhood-style FOMO retail    | Attention-driven momentum (§4.5)               | Destabilising | deviation, cash                 | Exists to buy small FOMO clips once deviation crosses the attention threshold.   | examples/AGENT_POOL/finance/momentum-retail.md     |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a single-price equity market. Price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where `D(t)` is buy quantity minus sell quantity. The price-impact coefficient is moderate to represent an illiquid heavily-shorted small-cap stock, and mean reversion is intentionally slow so squeeze dynamics dominate short-run price formation.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, and `round`. These signals are sufficient for the cash-threshold coordinated buying, forced-cover triggers, gamma-scaled hedging, threshold-based fundamental selling, and FOMO-threshold late buying mechanisms.

### §8.3 Constraints and Frictions

There is no circuit breaker. Agents are constrained by cash, inventory, base order size, and per-round buy caps (retail-coordinated: 500; short-seller-hf: half of remaining short; institutional-value: 1000; momentum-retail: 50). ShortSellerHF begins with a negative position of −1,000 shares; InstitutionalValue begins with +2,000 long shares. The fundamental is held constant so the squeeze magnitude comes from coordination and hedging mechanics rather than a fundamental revision.

### §8.4 Round Granularity

One round represents a short trading window in which coordinated retail orders, forced covering, gamma-hedging orders, and stabilizing supply are aggregated. The default round budget is calibrated to cover the initial coordinated push, the multi-round short-cover cascade, gamma amplification, and the exhaustion of institutional supply, in analogy with the compressed fourteen-day GameStop squeeze.

## §9 Parameter Seeds

| Parameter                        | Symbol       | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                                                              |
|----------------------------------|--------------|----------------------------------|-----------------|-------------------|--------------------------------------------------------------------------------------------------------------|
| buy pressure                     | `p_buy`      | retail-coordinated (§7)          | 0.10-0.50       | 0.12              | Lyocsa, Baumohl, & Vyrost (2022), https://doi.org/10.1016/j.frl.2022.102785                                  |
| cover threshold                  | `theta_cov`  | short-seller-hf (§7)             | 0.05-0.50       | 0.05              | Jones & Lamont (2002), https://doi.org/10.1016/S0304-405X(02)00224-6                                         |
| gamma exposure                   | `gamma_exp`  | market-maker-gamma (§7)          | 0.30-2.00       | 0.30              | Jarrow & Li (2021), https://doi.org/10.1007/s10436-021-00394-2                                               |
| sell threshold                   | `theta_sell` | institutional-value (§7)         | 0.30-1.00       | 0.30              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                                 |
| fomo threshold                   | `theta_fomo` | momentum-retail (§7)             | 0.05-0.30       | 0.05              | Barber, Huang, Odean, & Schwarz (2022), https://doi.org/10.1111/jofi.13183                                   |
| initial short position (ShortHF) | `pos0_short` | short-seller-hf (§7)             | −200 to −1000   | −1000             | GME 140%-of-float short-interest analog                                                                      |
| initial long position (InstVal)  | `pos0_long`  | institutional-value (§7)         | +500 to +2000   | +2000             | Institutional long-inventory analog                                                                          |
| price impact                     | `lambda`     | environment (§8.1)               | 0.001-0.050     | 0.04              | Kyle (1985), https://doi.org/10.2307/1913210                                                                 |
| mean reversion                   | `gamma`      | environment (§8.1)               | 0.001-0.050     | 0.01              | Slow mean-reversion in squeeze; Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| noise std                        | `sigma`      | environment (§8.1)               | 0.005-0.050     | 0.02              | Roll (1984), https://doi.org/10.1111/j.1540-6261.1984.tb03897.x                                              |
| fundamental value                | `F`          | environment (§8.1)               | 10-30           | 20.0              | GME fundamental analog                                                                                       |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                                                                          |
|---------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the three-way squeeze coalition against a finite institutional seller.                                       |
| LLM     | Yes    | Tests whether persona reasoning across coordinated retail and short-seller personas modulates squeeze magnitude.                                 |
| RuleLLM | Yes    | Tests whether explicit rule prompts preserve the squeeze mechanics under model reasoning.                                                        |
| Rag     | Yes    | Tests whether retrieved precedents (GameStop 2021, Volkswagen 2008, Hunt Brothers 1980) reduce momentum-retail activation or short-seller entry. |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
