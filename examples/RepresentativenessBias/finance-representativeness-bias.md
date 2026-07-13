# RepresentativenessBias — Scenario Target

## §1 Meta

| Field       | Content                                                                  |
|-------------|--------------------------------------------------------------------------|
| Name        | RepresentativenessBias                                                   |
| Domain      | finance                                                                  |
| Produced By | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Claude Code) |
| Created     | 2026-07-07                                                               |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                               |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                  |

| CHANGELOG  |                                                                                                                                                                                        |
|------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-07-07 | Polish Step 0: target file produced from `simulation-bases.md` and `analysis-bases.md` downstream artefacts via define-skill end-to-end invocation (Case B, pre-filled from existing). |

## §2 Phenomenon Statement

### §2.1 Trigger
The scenario begins with a sequence of recent price movements that form an identifiable pattern — a short run of same-direction returns, or a price trajectory that resembles a recent success story. Representativeness-biased agents observe this small sample and extrapolate it as representative of a broader regime shift. A short sequence of, say, three positive consecutive returns triggers a category-overgeneralising agent to trade as if the asset has entered a sustained bull regime.

### §2.2 Mechanism
Representativeness bias drives agents to judge probability by similarity to a prototype rather than by base rates. Pattern-matching agents identify recent return sequences as resembling known patterns (trends, reversals, boom-bust cycles) and trade on the perceived prototype. Category-overgeneralising agents classify assets into good or bad categories based on recent performance, ignoring the statistical base rate of such sequences. This creates excess demand or supply not justified by fundamental probability, which the market's price impact converts into price movement. Bayesian updaters and contrarian-statistical agents provide the rational benchmark. Noise traders add uninformed background flow.

### §2.3 Participants
The core participant classes are pattern-matching representativeness traders, category-overgeneralising classifiers, Bayesian-rational updaters, statistical contrarian traders, and background noise traders. Pattern-matchers and category-overgeneralizers provide bias-driven directional flow. Bayesian updaters supply the rational base-rate benchmark. Statistical contrarians exploit representativeness-driven mispricing. Noise traders add uninformed liquidity.

### §2.4 Resolution
Representativeness-driven positions unwind when the recent return sequence fails to sustain the expected regime pattern, or when statistical-contrarian offsetting flow exceeds biased demand. Bayesian updaters, trading on base rates rather than prototypes, gradually absorb the mispricing. The effect weakens as the small-sample pattern ages and new observations fail to confirm the extrapolated regime.

## §3 Research Goals

1. **Base-rate neglect signature.** Can the simulation generate pattern-matcher and category-overgeneralizer order imbalances that deviate from Bayesian-rational benchmark levels?
2. **Regime-extrapolation dynamics.** Do representativeness-biased agents increase position size when recent return sequences resemble known prototypes, consistent with Kahneman and Tversky (1972) predictions?
3. **Contrarian correction.** Does contrarian-statistical order flow increase after representativeness-driven deviations, providing the corrective benchmark response?
4. **Ablation.** If the pattern-matcher is removed, does the deviation from base-rate-rational order flow fall relative to the full model?
5. **Parameter sweep and variant comparison.** How do the pattern-similarity threshold and recency-weight parameters change bias strength, and how do LLM-driven agents differ from the deterministic Rule baseline in representativeness reasoning?

## §4 Theoretical Anchors

### §4.1 Representativeness Heuristic

| Field                     | Content                                                                                                                                                                           |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454. https://doi.org/10.1016/0010-0285(72)90016-3 |
| Key mechanism (≤30 words) | People judge probability by similarity to a prototype or stereotype, neglecting base rates and sample size.                                                                       |
| Key equation              | Perceived regime probability = f(similarity(recent_sequence, prototype_pattern)); trade when similarity > threshold.                                                              |
| Motivates agent           | pattern-matcher (§7), category-overgeneralizer (§7)                                                                                                                               |
| Parameter implication     | similarity_threshold range 0.3 to 0.8, default 0.5; recency_weight range 0.5 to 0.95, default 0.80.                                                                               |

### §4.2 Base-Rate Neglect in Financial Contexts

| Field                     | Content                                                                                                                                                                        |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Grether, D. M. (1980). Bayes' rule as a descriptive model: The representativeness heuristic. *Quarterly Journal of Economics*, 95(3), 537-557. https://doi.org/10.2307/1885092 |
| Key mechanism (≤30 words) | Experimental evidence shows systematic neglect of prior probabilities when individuating evidence is presented, even when base rates are explicitly stated.                    |
| Key equation              | Bayesian posterior = (likelihood * prior) / evidence; representativeness agent uses likelihood_only = similarity(recent, prototype).                                           |
| Motivates agent           | bayesian-updater (§7) as rational benchmark                                                                                                                                    |
| Parameter implication     | base_rate_belief range 0.05 to 0.30 (probability of genuine regime shift), default 0.10; bayesian uses full posterior vs representativeness uses similarity-only.              |

### §4.3 Regime-Shift Extrapolation in Asset Prices

| Field                     | Content                                                                                                                                                                         |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 |
| Key mechanism (≤30 words) | Investors switch between mean-reversion and trend regimes based on recent evidence, overreacting to short sequences and underreacting to long-run base rates.                   |
| Key equation              | Regime belief evolves per Barberis-Shleifer-Vishny switching: if recent returns consistent with trend regime, increase trend-regime probability weight.                         |
| Motivates agent           | pattern-matcher (§7), category-overgeneralizer (§7)                                                                                                                             |
| Parameter implication     | regime_switch_speed range 0.05 to 0.25, default 0.12; trend_regime_prior range 0.05 to 0.25, default 0.10.                                                                      |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                               | Quantitative range                                           | Citation                                                                          | Acceptance metric                                           |
|----|-------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------|
| F1 | Pattern-matcher order imbalance deviates from Bayesian-rational benchmark in direction of recent return sequence. | correlation(pattern_matcher_imbalance, recent_return) > 0.30 | Kahneman & Tversky (1972), https://doi.org/10.1016/0010-0285(72)90016-3           | `analysis.py: _pattern_bias_correlation()` > 0.30           |
| F2 | Category-overgeneralizer position size increases after observing prototype-matching return sequences.             | avg_position_after_match > avg_position_baseline             | Grether (1980), https://doi.org/10.2307/1885092                                   | `analysis.py: _category_overgeneralization_ratio()` > 1.0   |
| F3 | Bayesian updater order flow is less volatile than representativeness-biased agent flow.                           | std(bayesian_quantity) < std(pattern_matcher_quantity)       | Grether (1980), https://doi.org/10.2307/1885092                                   | `analysis.py: _bayesian_vs_biased_volatility_ratio()` < 1.0 |
| F4 | Contrarian-statistical order flow increases when price deviates from Bayesian-implied value.                      | contrarian_volume_share rising with abs(bias_deviation)      | Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0 | `analysis.py: contrarian_vs_bias_correlation()` > 0         |
| F5 | Regime-extrapolation strength decays as the matching pattern ages without confirmation.                           | order_imbalance_t+10 < order_imbalance_t after match         | Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0 | `analysis.py: _pattern_decay_ratio()` < 1.0                 |

## §6 Historical / Empirical Anchors

### §6.1 Dot-Com Era Regime Extrapolation (1998-2000)

| Field             | Content                                                                                                                                                                                                                                                                                                                                               |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Dot-com bubble and technology-stock regime extrapolation, 1998-2000.                                                                                                                                                                                                                                                                                  |
| Trigger           | A sequence of strong technology-stock returns led investors to extrapolate a "new economy" regime where traditional valuation metrics no longer applied.                                                                                                                                                                                              |
| Quantitative arc  | NASDAQ rose from roughly 1,500 in late 1998 to over 5,000 by March 2000, then fell to roughly 1,100 by October 2002. The regime-extrapolation narrative dominated through 1999 and early 2000 before base-rate reality reasserted.                                                                                                                    |
| Agent mapping     | `pattern-matcher` maps to investors who extrapolated recent tech returns as a permanent regime shift; `category-overgeneralizer` maps to those who classified all tech stocks as "winners"; `bayesian-updater` maps to value investors who maintained base-rate discipline; `contrarian-statistical` maps to short-sellers who bet on mean reversion. |
| Primary source(s) | Shiller (2000), *Irrational Exuberance*; Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0                                                                                                                                                                                                                            |

## §7 Agent Roster

| Agent name (kebab)       | Real-world counterpart                                                 | Theory family (§4 anchor)                                 | Domain role       | Primary signals               | Intent line                                                                                                         | Expected pool match                              |
|--------------------------|------------------------------------------------------------------------|-----------------------------------------------------------|-------------------|-------------------------------|---------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| pattern-matcher          | technical analyst or chart-pattern trader                              | Representativeness (§4.1) and Regime Extrapolation (§4.3) | Destabilising     | price, return                 | "Exists to identify recent return sequences as matching known prototypes and trade on the perceived regime."        | (none — likely new)                              |
| category-overgeneralizer | retail investor classifying stocks into simplistic good/bad categories | Representativeness (§4.1) and Regime Extrapolation (§4.3) | Destabilising     | price, return, deviation      | "Exists to classify assets into winner or loser categories based on recent performance, ignoring base rates."       | (none — likely new)                              |
| bayesian-updater         | quantitatively disciplined institutional investor or rational analyst  | Base-Rate Neglect (§4.2)                                  | Stabilising       | price, fundamental, deviation | "Exists to update beliefs using full posterior probabilities and base rates, serving as the rationality benchmark." | examples/AGENT_POOL/finance/rational-updater.md  |
| contrarian-statistical   | statistical arbitrage fund or quant mean-reversion strategist          | Regime Extrapolation (§4.3) corrective                    | Stabilising       | price, deviation              | "Exists to exploit representativeness-driven mispricing by trading toward statistical expectations."                | examples/AGENT_POOL/finance/contrarian-trader.md |
| noise-trader             | uninformed retail liquidity provider                                   | Noise Trading (Black 1986 context)                        | Context-dependent | price, cash, position         | "Exists to add background liquidity and non-informational volatility."                                              | examples/AGENT_POOL/finance/noise-trader.md      |

Diversity notes: two destabilising agents (pattern-matcher, category-overgeneralizer), two stabilising agents (bayesian-updater, contrarian-statistical), and one context-dependent liquidity provider. Theory families span representativeness, base-rate neglect, regime extrapolation, and noise trading.

## §8 Environment Specification

### §8.1 Price Formation

`P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 1.0)`, with constant fundamental `F`, price impact `lambda`, mean reversion `gamma`, and Gaussian noise with standard deviation `sigma`.

### §8.2 Information Broadcast

| Field         | Type  | Definition                             | Rationale                                                 |
|---------------|-------|----------------------------------------|-----------------------------------------------------------|
| `price`       | float | Current market price.                  | Primary state signal.                                     |
| `fundamental` | float | Constant fundamental value.            | Required for base-rate value anchoring.                   |
| `deviation`   | float | `(price - fundamental) / fundamental`. | Primary signal for contrarian and value agents.           |
| `return`      | float | `(price - prev_price) / prev_price`.   | Required for pattern matching on recent return sequences. |
| `volume`      | float | Total trading volume proxy.            | Phase diagnostics.                                        |
| `round`       | int   | Current round number.                  | Phase tracking.                                           |

### §8.3 Constraints and Frictions

| Item                  | Yes / No | Rationale                                  |
|-----------------------|----------|--------------------------------------------|
| Short-selling allowed | Yes      | Required for contrarian-statistical agent. |
| Price floor           | Yes      | Floor at 1.0 prevents non-positive prices. |
| Transaction costs     | No       | Abstracted from baseline.                  |

### §8.4 Round Granularity

One round approximates one trading day. A 200-round run covers pattern identification, regime extrapolation, contrarian offset, and pattern-age decay phases.

## §9 Parameter Seeds

| Parameter                | Symbol     | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                                   |
|--------------------------|------------|----------------------------------|-----------------|-------------------|-----------------------------------------------------------------------------------|
| initial price            | P(0)       | environment (§8.1)               | normalised      | 100.0             | Source: normalization                                                             |
| fundamental value        | F          | environment (§8.1)               | normalised      | 100.0             | Source: normalization                                                             |
| price impact             | lambda     | environment (§8.1)               | 0.03 to 0.12    | 0.06              | Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0 |
| mean reversion           | gamma      | environment (§8.1)               | 0.005 to 0.03   | 0.01              | Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0 |
| noise standard deviation | sigma      | environment (§8.1)               | 0.10 to 0.50    | 0.25              | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                  |
| similarity threshold     | theta_sim  | pattern-matcher (§7)             | 0.30 to 0.80    | 0.50              | Kahneman & Tversky (1972), https://doi.org/10.1016/0010-0285(72)90016-3           |
| recency weight           | w_rec      | pattern-matcher (§7)             | 0.50 to 0.95    | 0.80              | Kahneman & Tversky (1972), https://doi.org/10.1016/0010-0285(72)90016-3           |
| base-rate belief         | pi_base    | bayesian-updater (§7)            | 0.05 to 0.30    | 0.10              | Grether (1980), https://doi.org/10.2307/1885092                                   |
| regime switch speed      | eta_switch | category-overgeneralizer (§7)    | 0.05 to 0.25    | 0.12              | Barberis, Shleifer & Vishny (1998), https://doi.org/10.1016/S0304-405X(98)00027-0 |
| noise trade probability  | p_noise    | noise-trader (§7)                | 0.10 to 0.50    | 0.30              | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                  |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale                                                                                                          |
|---------|--------|--------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline for pattern-matching and base-rate-neglect signatures.                                      |
| LLM     | Yes    | Tests whether persona-driven representativeness reasoning amplifies or moderates pattern extrapolation.            |
| RuleLLM | Yes    | Tests whether explicit representativeness rules inside LLM reasoning preserve bias structure.                      |
| Rag     | Yes    | Tests whether retrieved judgment-and-decision-making literature changes classification or extrapolation behaviour. |

### §10.2 Pass / Fail Criteria

| Criterion                                                                                                                                                | Status when satisfied |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|
| Deterministic variant initializes, runs, writes records, and completes without uncaught exceptions.                                                      | green                 |
| At least one representativeness mechanism activates: pattern-match trading, category overgeneralization, or base-rate deviation from Bayesian benchmark. | green                 |
| Analysis loads records and computes core metrics from §5.                                                                                                | green                 |
| All four variants declared Yes in §10.1 build and produce required output artefacts.                                                                     | green                 |
