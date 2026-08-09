# LossAversion — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-16  Polish target-file gate (Case B): reconstructed this canonical target solely from the existing LossAversion scenario documents, configurations, and implementation. Five-agent roster and four-variant build matrix confirmed; status set to `locked`.
- 2026-07-16  Research audit: the Prospect Theory, Cumulative Prospect Theory, disposition-effect, momentum, and dealer-inventory DOI anchors were resolved against publisher or primary-paper records. Unsupported historical-market numbers were excluded from the canonical target.
- 2026-07-16  Polish Step 1 audit: `simulation-bases.md §2` rewritten as five complete six-field Theory blocks; Ho–Stoll DOI corrected to `10.1016/0304-405X(81)90020-9`; Odean sample and date range verified; scenario calibration values explicitly separated from empirical estimates.
- 2026-07-16  Polish Step 2 audit: five profile matches reuse existing canonical identities. Four incomplete handbooks were upgraded to conformant specifications; three missing canonical 512×512 PNGs were generated and registered as mapping rows #103–#105. Three consecutive handbook/icon checks and naming/parity audit PASS.
- 2026-07-16  Polish Step 3 audit: all 16 YAML files parse; all four required variant folders are complete; topology, variant prefixes, and canonical archetype parity PASS. Every numeric `extras.*` key has a resolvable `# Source:` annotation (final counts: Rule=53, LLM=63, RuleLLM=68, Rag=86), and two unused Rule-only compatibility keys were removed.
- 2026-07-16  Polish Step 4 audit: removed hard-coded behavioral thresholds and sizes; added seeded market shocks, weighted entry-price accounting, edge-triggered disposition realizations, hybrid rule/sign bounds, current-state persistence, and scenario-specific analysis. Fixed the absent `examples.standard_rule_analysis` import without modifying `masim/` source. py_compile/import, no-defaults, Rule behavior probes, RuleLLM dual-section, and Rag fallback gates PASS.
- 2026-07-16  Polish Steps 5–10: Rule/LLM/RuleLLM independent setup/shutdown PASS; Rag setup exceeded the 120-second knowledge-index window and was not formally executed, consistent with the current no-Rag run scope. Full Rule 200/200 run PASS. Analysis PASS with LAI=2.25, DEI=3.50 (3 gain and 3 loss realization events), BER=350.0, initial-wealth-normalized WPI=0.939, VAF=0.202 (counter-cyclical moderation), mean absolute deviation=5.85%, and max drawdown=19.17%. All five declared files written.
- 2026-07-16  Closeout: three-round structural/config/icon re-audit PASS; status changed `locked → released`.

## §1 Meta

| Field | Content |
|---|---|
| Name | LossAversion |
| Domain | finance |
| Requested By | Wenyou |
| Produced By | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Codex) |
| Created | 2026-07-16 |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Target Spec | masim/skills/define-simulation-scenario-skill.md |
| Status | released |

## §2 Phenomenon Statement

### §2.1 Trigger

A public price change moves an investor's marked position above or below its purchase-price reference point. Equal-sized gains and losses are therefore framed differently, while sufficiently deep losses activate an additional break-even motive.

### §2.2 Mechanism

Loss-averse investors realize a larger fraction of winning positions than losing positions. Break-even traders increase risk after material losses by averaging down. Rational value traders and inventory-constrained market makers trade against deviations from fundamental value, while momentum traders reinforce the current signed deviation. Their feasible orders jointly update the next public price.

### §2.3 Participants

The market contains loss-averse investors, break-even traders, rational traders, momentum traders, and market makers. The first two roles create the behavioral asymmetry; the other three provide valuation, trend-following, and liquidity/inventory channels needed to identify when the behavioral effect is amplified or offset.

### §2.4 Resolution

An episode resolves when price returns near the public fundamental or reference price, portfolio constraints prevent further escalation, and active signals fall below their thresholds. Resolution is endogenous: restoring demand and finite cash/inventory counteract biased demand, rather than forcing a terminal price.

## §3 Research Goals

1. Does the simulated loss-averse population realize a larger fraction of gains than losses, and does removing that population collapse the disposition-effect index?
2. Does the break-even population increase purchase size as loss depth grows, and does disabling it reduce downside order imbalance?
3. How do `loss_aversion_lambda` and `sell_gain_threshold` change the loss-aversion index, disposition-effect index, and wealth penalty?
4. Do Rule, LLM, RuleLLM, and Rag variants preserve the intended ordering of behavioral and corrective actions under the same public state?
5. Does a joint ablation of loss-averse and break-even agents reduce volatility amplification relative to the full population?

## §4 Theoretical Anchors

### §4.1 Prospect Theory and Loss Aversion

| Field | Content |
|---|---|
| Full citation | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185 |
| Key mechanism | Outcomes are evaluated around a reference point; losses receive more weight than equal gains. |
| Key equation | `v(x)=x^alpha` for `x>=0`; `v(x)=-lambda*(-x)^beta` for `x<0`, with `lambda>1`. |
| Motivates agent | loss-averse-investor |
| Parameter implication | `loss_aversion_lambda=2.25` and a positive gain-realization threshold create asymmetric sell fractions. |

### §4.2 Cumulative Prospect Theory and Break-Even Risk Seeking

| Field | Content |
|---|---|
| Full citation | Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5, 297–323. https://doi.org/10.1007/BF00122574 |
| Key mechanism | The value function is convex in the loss domain, supporting increased risk taking when below the reference point. |
| Key equation | `Q_buy=min(cash/P, floor(|pnl|*risk_increase_factor*sizing_scale))` when `pnl<-0.05`. |
| Motivates agent | break-even-trader |
| Parameter implication | `risk_increase_factor=2.0` scales the loss-domain escalation while cash bounds the order. |

### §4.3 Disposition Effect

| Field | Content |
|---|---|
| Full citation | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775–1798. https://doi.org/10.1111/0022-1082.00072 |
| Key mechanism | Brokerage-account investors realize winning positions more readily than losing positions. |
| Key equation | `DEI = realized_gain_rate / realized_loss_rate`; the configured rule uses gain/loss sell fractions `0.70/0.20`. |
| Motivates agent | loss-averse-investor |
| Parameter implication | The sell fractions imply a directional benchmark of `DEI≈3.5` conditional on both triggers firing. |

### §4.4 Value and Momentum Benchmarks

| Field | Content |
|---|---|
| Full citation | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism | Trend-following demand trades in the direction of recent performance; a value benchmark trades against public mispricing. |
| Key equation | Momentum: `sign(q)=sign((P-F)/F)` above `entry_threshold`; value: `sign(q)=-sign((P-F)/F)` above 3%. |
| Motivates agent | momentum-trader; rational-trader |
| Parameter implication | `entry_threshold=0.03` and `risk_aversion=0.7` separate amplifying and correcting demand. |

### §4.5 Inventory-Constrained Liquidity Provision

| Field | Content |
|---|---|
| Full citation | Ho, T., & Stoll, H. R. (1981). Optimal dealer pricing under transactions and return uncertainty. *Journal of Financial Economics*, 9(1), 47–73. https://doi.org/10.1016/0304-405X(81)90020-9 |
| Key mechanism | A dealer adjusts trading to manage risky inventory and supplies counter-cyclical liquidity within a finite limit. |
| Key equation | Trade against signed price deviation while `abs(position)<inventory_limit`, clipped by cash and inventory. |
| Motivates agent | market-maker |
| Parameter implication | `inventory_limit=2000` prevents unlimited stabilizing capacity. |

## §5 Stylized Facts

| # | Fact | Quantitative range | Citation | Acceptance metric |
|---|---|---|---|---|
| F1 | Equal-size losses carry more decision weight than gains. | `1.8 <= LAI <= 2.8` | Kahneman & Tversky (1979) | `loss_aversion_index` |
| F2 | Winners are realized more readily than losers. | `DEI > 1.0`; configured conditional benchmark `≈3.5` | Odean (1998) | `disposition_effect_index` |
| F3 | Risk-taking rises after a material loss. | `BER > 1.0` | Tversky & Kahneman (1992) | `break_even_risk_ratio` |
| F4 | Biased populations experience a lower terminal wealth ratio than rational/value benchmarks. | `WPI < 1.0` | Odean (1998) | `wealth_penalty_index` |
| F5 | Behavioral activity changes endogenous realized volatility without instability; values below one indicate counter-cyclical moderation by loss holding and break-even buying. | `0.1 < VAF < 4.0` | Prospect-theory mechanism in §4.1–§4.3 | `volatility_amplification_factor` |

## §6 Historical / Empirical Anchors

### §6.1 Odean Discount-Brokerage Account Study (1987–1993)

| Field | Content |
|---|---|
| Trigger | A held stock trades above or below its purchase-price reference point. |
| Quantitative arc | Trading records for 10,000 accounts show investors realize gains more readily than losses; the scenario uses the documented direction and a configured 70% versus 20% conditional sell-fraction benchmark rather than claiming those fractions were estimated by Odean. |
| Agent mapping | Brokerage customers map to loss-averse-investor; loss-domain escalation maps to break-even-trader; value, momentum, and dealer roles provide counterfactual market channels. |
| Primary source | Odean (1998), https://doi.org/10.1111/0022-1082.00072 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family | Domain role | Primary signals | Intent line | Expected pool match |
|---|---|---|---|---|---|---|
| loss-averse-investor | retail investor with disposition effect | §4.1, §4.3 | behavioral asymmetry | price, entry_price, cash, position | Realize gains more readily than losses. | masim/agents/defines/finance/loss-averse-investor.md |
| break-even-trader | loss-domain risk seeker | §4.2 | behavioral escalation | price, entry_price, cash, position | Increase exposure after a material loss. | masim/agents/defines/finance/break-even-trader.md |
| rational-trader | fundamental-value investor | §4.4 | stabilizing benchmark | price, fundamental, cash, position | Trade against material public mispricing. | masim/agents/defines/finance/rational-trader.md |
| momentum-trader | short-horizon trend follower | §4.4 | destabilizing amplifier | price, fundamental, cash, position | Trade with the signed deviation. | masim/agents/defines/finance/momentum-trader.md |
| market-maker | inventory-constrained dealer | §4.5 | stabilizing liquidity | price, fundamental, cash, position | Trade against imbalance within inventory limits. | masim/agents/defines/finance/market-maker.md |

## §8 Environment Specification

### §8.1 Price Formation

`P(t+1)=max(price_floor, P(t)+price_impact*net_demand+mean_reversion*(F-P(t))+epsilon+F*shock_return(t))`, where `epsilon` is seeded zero-mean Gaussian noise and the two scheduled public stimuli identify gain- and loss-domain responses.

### §8.2 Information Broadcast

Each round the market broadcasts current price, public fundamental value, signed deviation, and round number. Each trader also observes its own cash, position, and entry-price reference.

### §8.3 Constraints and Frictions

Buy orders are clipped by available cash; sell orders are clipped by non-negative inventory; price has a positive floor; market-maker activity is bounded by an inventory limit. Missing mandatory signals result in hold or an explicit validation failure.

### §8.4 Round Granularity

One round consists of order receipt, market update and broadcast, trader perception, feasible decision, state update, and record persistence. The configured experiment has 200 rounds.

## §9 Parameter Seeds

| Parameter | Belongs to | Type | Candidate default | Valid/calibration range | Source |
|---|---|---|---|---|---|
| `initial_price`, `fundamental_value` | market and all traders | float | 100.0 | `>0` | normalization |
| `price_impact` | market | float | 0.0002 | `>0` | simulation-bases.md §5 market calibration |
| `mean_reversion` | market | float | 0.01 | `[0,1]` | restoring-price mechanism |
| `noise_std` | market | float | 0.015 | `>=0` | bounded perturbation calibration |
| `loss_aversion_lambda` | loss-averse-investor | float | 2.25 | `[1.8,2.8]` | Kahneman & Tversky (1979) |
| `sell_gain_threshold` | loss-averse-investor | float | 0.05 | `(0,1)` | scenario trigger calibration |
| `base_size` | trader archetypes | int | 300–400 | `>0` | order-cap calibration |
| `risk_increase_factor` | break-even-trader | float | 2.0 | `[1,4]` | Tversky & Kahneman (1992) mechanism |
| `risk_aversion` | rational-trader | float | 0.7 | `(0,1]` | stabilizing response scale |
| `entry_threshold` | momentum-trader | float | 0.03 | `(0,1)` | Jegadeesh & Titman (1993) mechanism |
| `inventory_limit` | market-maker | int | 2000 | `>0` | Ho & Stoll (1981) mechanism |
| `gain_sell_fraction`, `loss_sell_fraction` | loss-averse-investor | float | 0.70, 0.20 | `[0,1]` | scenario disposition calibration |
| `loss_trigger`, `deviation_threshold` | behavioral/value traders | float | -0.05, 0.03 | `[-1,0)`, `(0,1)` | scenario activation calibration |
| `sizing_scale` | break-even, rational, momentum traders | float | 5000 or 3000 | `>0` | signal-to-order calibration |
| `random_seed` | market | int | 20260716 | non-negative integer | reproducible common market path |
| `price_floor` | market | float | 0.01 | `>0` | strictly positive price invariant |
| `shock_schedule` | market | round→return map | `{20: 0.06, 80: -0.20}` | bounded signed returns | controlled gain/loss identification stimuli |
| `quantity_tolerance` | RuleLLM and Rag traders | float | 0.20 | `[0,1]` | hybrid quantity adjustment band |
| `custom_state_hot_limit` | market | int | 3 | `>=1` | bounded in-memory record window |
| `temperature` | model-driven traders | float | 0.3–0.95 by role | `[0,2]` | model sampling calibration |
| `max_tokens` | model-driven traders | int | 600 | `>0` | bounded response budget |
| `chunk_size`, `chunk_overlap`, `top_k` | Rag retrieval | int | 512, 64, 5 | positive; overlap below size | retrieval calibration |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---|---|---|
| Rule | Yes | Deterministic calibration and causal baseline. |
| LLM | Yes | Persona-driven decisions under the common contract. |
| RuleLLM | Yes | Rule-bounded model reasoning and sign parity. |
| Rag | Yes | Retrieval-grounded rule/model reasoning with an explicit empty-retrieval sentinel. |

### §10.2 Pass / Fail Criteria

1. All five roster agents, canonical pool profiles, icons, configuration identities, and implementation classes resolve bidirectionally in every built variant.
2. Rule unit probes reproduce gain-sell, loss-sell, break-even buy, value correction, momentum amplification, and inventory-constrained liquidity directions.
3. Four variants pass configuration, import, setup, and bounded smoke gates appropriate to their capability class.
4. Rule analysis emits all five acceptance metrics in §5, a machine-readable `summary.json`, and the declared visualization files without missing required series.
5. A full 200-round Rule run and analysis complete without uncaught exceptions; deviations remain finite and price stays positive.
6. The ablation and parameter-sweep hooks described in §3 are explicit and reproducible from scenario-local configuration changes.
