# EndowmentEffect — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-15  Polish target-file gate (Case B): reverse-reconstructed from existing simulation-bases.md, analysis-bases.md, and implementation artefacts. Locked for audit.
- 2026-07-15  Polish run against skill baseline (define/agent-design/implement). Step 0 (target-file gate): Case B reverse-reconstructed seed, §11 three-PASS structural gates green. Step 1 (research audit): DOI-resolution PASS on all 3 §4 anchors; six-field Theory completeness PASS on 3 Theory blocks; bidirectional target-anchor coverage PASS. Step 2 (agent + env): 5 archetypes rank-precedence green (Rank-1 kebab = Rank-2 target row = Rank-3 class name across Rule/LLM/RuleLLM/Rag); AGENT_POOL three-stage match outcome `reuse` for all 5 (pool profiles are stubs — shared-fabric ownership, not expanded during polish); icon-resolution gate PASS after generating 3 missing PNGs (endowed-holder, status-quo-seller, new-buyer) and adding mapping rows #68–#70 to design.md; §3 environment + §5 diversity + §7 communication PASS. Step 3 (config audit): all 4 variants polished; `# Source:` traceability coverage added to Rule (36 annotations), LLM (54 annotations), RuleLLM (54 annotations); Rag already had 65 annotations. Step 4 (impl audit): py_compile PASS all 4 variants; import smoke PASS all 4 variants; no-defaults rule PASS; RuleLLM dual-section prompt invariant PASS (5 × == PERSONA == + == DECISION RULES ==); _RAG_FALLBACK define+reference PASS; explain.md §2 and analysis.md §2 bidirectional completeness PASS. Steps 5-10 (review + smoke): Rule variant 5-round end-to-end smoke PASS; LLM/RuleLLM/Rag setup-only smoke PASS. Closeout: traceability matrix resolved; status locked → released.

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | EndowmentEffect                                        |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (reverse-reconstruction) |
| Created       | 2026-07-11                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md       |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts when an investor acquires ownership of an asset. The act of owning — not the act of rational valuation — shifts the investor's reference point so that selling registers as a loss. This ownership-induced reference-point shift creates a wedge between the minimum acceptable sale price (WTA) and the maximum willingness to pay (WTP) for the same asset.

### §2.2 Mechanism

The core mechanism is loss aversion applied to ownership: owned assets feel more valuable than identical unowned assets. Sellers demand a price premium above fundamental value (WTA > WTP), suppressing trading volume and holding transaction prices above fair value. Status quo bias amplifies the effect by adding cognitive switching costs that further reduce selling propensity.

### §2.3 Participants

The causal participants are endowed holders (maximum ownership attachment), status-quo-biased sellers (inertia resistance), rational arbitrageurs (corrective force), new buyers (unbiased WTP), and noise traders (background liquidity). Endowed holders and status-quo sellers form a two-layer resistance structure that sustains overvaluation; rational arbitrageurs and new buyers provide incomplete correction.

### §2.4 Resolution

The endowment effect resolves slowly as rational arbitrage pressure gradually erodes the ownership premium. Mean reversion in the price formation model provides a restoring force, but the resistance layer (endowed holders + status-quo sellers) sustains prices 5-20% above fundamental for extended periods before correction completes.

## §3 Research Goals

1. Does the endowment effect create persistent overvaluation above fundamental (5-15% for extended periods)?
2. How much does ownership bias suppress trading volume versus a rational baseline (target: 40-60% suppression)?
3. How does the endowment premium magnitude affect price correction speed (half-life 15-50 rounds)?
4. Do all four variants reproduce the volume-suppression signature?
5. How does agent portfolio performance differ across investor types (RationalArbitrageur outperforms EndowedHolder)?

## §4 Theoretical Anchors

### §4.1 Endowment Effect and Loss Aversion

| Field | Content |
|-------|---------|
| Full citation | Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. *Journal of Political Economy*, 98(6), 1325-1348. https://doi.org/10.1086/261737 |
| Key mechanism | Ownership increases subjective value above market price; WTA/WTP ratio of 2-7 for identical objects. |
| Key equation | `WTA = P * lambda^(1/alpha)` where lambda = 2.25, alpha = 0.88 |
| Motivates agent | endowed-holder, status-quo-seller |
| Parameter implication | `endowment_premium` in [0.10, 0.25]; `sell_reluctance` in [0.20, 0.40] |

### §4.2 Status Quo Bias

| Field | Content |
|-------|---------|
| Full citation | Samuelson, W., & Zeckhauser, R. (1988). Status quo bias in decision making. *Journal of Risk and Uncertainty*, 1(1), 7-59. https://doi.org/10.1007/BF00055564 |
| Key mechanism | Systematic preference for current state over alternatives, even when switching is objectively beneficial. |
| Key equation | `E[U(sell)] - delta > E[U(hold)]` where delta is the cognitive switching cost |
| Motivates agent | status-quo-seller |
| Parameter implication | `status_quo_threshold` in [0.10, 0.25] |

### §4.3 Rational Expectations and Arbitrage Limits

| Field | Content |
|-------|---------|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism | Rational traders identify overvaluation but cannot fully correct it under funding limits and noise trader risk. |
| Key equation | `sell if (P - F)/F > tau_r; buy if (P - F)/F < -tau_r` |
| Motivates agent | rational-arbitrageur, new-buyer |
| Parameter implication | `arb_threshold` in [0.02, 0.10]; `buy_threshold` in [0.0, 0.05] |

## §5 Stylized Facts

| # | Fact | Quantitative range | Acceptance metric | Source |
|---|------|-------------------|-------------------|--------|
| F1 | WTA/WTP ratio of 2:1 to 7:1 | ratio in [2.0, 7.0] | endowment_premium_capture_rate > 0.65 | Kahneman et al. (1990) doi:10.1086/261737 |
| F2 | Trading volume 40-60% of rational benchmark | VSR in [0.40, 0.65] | volume_suppression_ratio | Plott & Zeiler (2005) doi:10.1257/aer.95.3.530 |
| F3 | Endowment-driven price premiums 5-20% above fundamental | MAD in [0.03, 0.12] | mean_absolute_deviation | Genesove & Mayer (2001) doi:10.1162/003355301753265561 |
| F4 | Loss-averse sellers demand 25-35% higher list prices | endowment_premium in [0.15, 0.35] | price_deviation time-series | Genesove & Mayer (2001) doi:10.1162/003355301753265561 |
| F5 | Retail investors hold losing positions 2x longer than winners | DPHL in [15, 50] rounds | deviation_half_life | Grinblatt & Keloharju (2001) doi:10.1111/0022-1082.00353 |

## §6 Historical / Empirical Anchors

| # | Event | Period | Geography | Key metric | Source |
|---|-------|--------|-----------|------------|--------|
| H1 | Cornell mug experiment | 1990 | USA (lab) | WTA/WTP = 2.5x; volume = 20% of equilibrium | Kahneman et al. (1990) doi:10.1086/261737 |
| H2 | Boston housing market post-peak | 1989-1992 | USA | Loss-averse sellers listed 25-35% above market | Genesove & Mayer (2001) doi:10.1162/003355301753265561 |
| H3 | Japanese equity portfolio holding | 2000-2002 | Japan | Retail held losing positions 18 months longer | Grinblatt & Keloharju (2001) doi:10.1111/0022-1082.00353 |

## §7 Agent Roster

| # | Archetype (kebab) | Theory family | Market role | Time horizon | Risk tolerance | Primary signals |
|---|-------------------|---------------|-------------|--------------|----------------|-----------------|
| 1 | endowed-holder | Behavioral (Kahneman et al. 1990) | Destabilising | Long | Low | price, fundamental, deviation |
| 2 | status-quo-seller | Behavioral (Samuelson & Zeckhauser 1988) | Destabilising | Long | Low | price, fundamental, deviation |
| 3 | rational-arbitrageur | Rational expectations (Shleifer & Vishny 1997) | Stabilising | Medium | Moderate | price, fundamental, deviation |
| 4 | new-buyer | Rational WTP (Kahneman et al. 1990) | Stabilising | Short | Moderate | price, fundamental, deviation |
| 5 | noise-trader | Noise trading (Black 1986) | Neutral | Random | Random | none (random) |

## §8 Environment Specification

### §8.1 Price Formation

`P(t+1) = P(t) + lambda * NetDemand(t) + gamma * (F - P(t)) + epsilon(t)` where lambda is price impact, gamma is mean-reversion rate, F is fundamental value, epsilon ~ N(0, sigma^2).

### §8.2 Information Broadcast

Market broadcasts `{price, fundamental, deviation, round}` to all investors each round.

### §8.3 Constraints and Frictions

- No short selling (position >= 0)
- Cash constraint (cannot spend more than available)
- Position constraint (cannot sell more than held)

### §8.4 Round Granularity

One simulation round per market update. Market collects orders, updates price, broadcasts state. 200 rounds per run.

## §9 Parameter Seeds

| # | Parameter | Default | Belongs to | Empirical range | Source citation |
|---|-----------|---------|------------|-----------------|----------------|
| 1 | initial_price | 100.0 | Environment | normalization | Muth (1961) |
| 2 | fundamental_value | 100.0 | Environment | normalization | Muth (1961) |
| 3 | price_impact | 0.02 | Environment | [0.001, 0.05] | Calibration |
| 4 | mean_reversion | 0.05 | Environment | [0.01, 0.10] | Calibration |
| 5 | noise_std | 0.01 | Environment | [0.005, 0.05] | Calibration |
| 6 | endowment_premium | 0.15 | endowed-holder | [0.10, 0.25] | Kahneman et al. (1990) doi:10.1086/261737 |
| 7 | sell_reluctance | 0.30 | endowed-holder | [0.20, 0.40] | Shefrin & Statman (1985) doi:10.1111/j.1540-6261.1985.tb05002.x |
| 8 | status_quo_threshold | 0.20 | status-quo-seller | [0.10, 0.25] | Samuelson & Zeckhauser (1988) doi:10.1007/BF00055564 |
| 9 | arb_threshold | 0.05 | rational-arbitrageur | [0.02, 0.10] | Muth (1961) doi:10.2307/1905537 |
| 10 | buy_threshold | 0.03 | new-buyer | [0.0, 0.05] | Kahneman et al. (1990) doi:10.1086/261737 |
| 11 | trade_probability | 0.30 | noise-trader | [0.20, 0.40] | Black (1986) doi:10.1111/j.1540-6261.1986.tb04513.x |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---------|--------|-----------|
| Rule | Yes | Deterministic baseline — cleanest endowment-effect signal |
| LLM | Yes | LLM persona reasoning about ownership attachment |
| RuleLLM | Yes | Hybrid: explicit threshold rules guide LLM decisions |
| Rag | Yes | RAG retrieval from endowment-effect literature |

### §10.2 Pass / Fail Criteria

| # | Criterion | Metric | Target |
|---|-----------|--------|--------|
| 1 | Persistent overvaluation | MAD | 0.03-0.12 |
| 2 | Volume suppression | VSR | 0.40-0.65 |
| 3 | Correction persistence | DPHL | 15-50 rounds |
| 4 | Endowment premium capture | EPCR | > 0.65 for EndowedHolder |
| 5 | Rational outperformance | PWR(RationalArbitrageur) | > 1.05 |
