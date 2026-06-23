# SocialInformationAgents

## Summary

| Field                        | Content                                                                                                                                                                                                          |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Non-trading social-information participant (sentiment-feed source)                                                                                                                                               |
| Theory Family                | Opinion Dynamics; Informational Cascade; Echo Chamber and Group Polarisation; Rumor Transmission                                                                                                                 |
| Market Role                  | **Indirect — feed-only**: emits sentiment / belief signals consumed by sentiment-driven trading agents (e.g., `SentimentNarrativeTrader`, `HerdingCascadeAgent`, `NoiseTrader`); does not place orders directly. |
| Time Horizon                 | short (per-tick belief update)                                                                                                                                                                                   |
| Risk Tolerance               | not applicable (no financial position)                                                                                                                                                                           |
| Information Asymmetry        | high (social-graph signals only)                                                                                                                                                                                 |
| Determinism                  | mostly deterministic (one stochastic engagement draw per tick for `passive_drifter` and `uninformed_bystander` variants)                                                                                         |
| Merged profiles              | 11 (BridgeBuilder, Conformist, CriticalThinker, DistortingRelayer, FactChecker, GullibleSpreader, Ideologue, PassiveBystander, PassiveFollower, SkepticalEvaluator, UninformedBystander)                         |
| Source scenarios             | EchoChamber, RumorSpread                                                                                                                                                                                         |
| Canonical sub-archetype enum | `social_mode ∈ {polarizer, depolarizer, conformist, passive_drifter, rumor_spreader, fact_checker}`                                                                                                              |

## Definition and Goals

This agent models the **non-financial social-information participant** that contributes to the formation, transmission, and (de)polarisation of group beliefs. It is a *sentiment-feed source* — it does not place market orders. Its output is a per-tick scalar `signal_t ∈ [-1, +1]` (and an optional `belief_t ∈ [0, 1]` for rumor scenarios) consumed by trading-agent classes that read `sentiment_t` as part of their decision information set.

The class consolidates two distinct opinion-dynamics families:
- **EchoChamber family** (six profiles): polarisation–depolarisation dynamics in which the agent's `opinion_t ∈ [-1, +1]` interacts with the group's mean opinion `M_t` and polarisation level `polarisation_t`.
- **RumorSpread family** (five profiles): rumor-transmission dynamics in which the agent's `belief_t ∈ [0, 1]` interacts with environment belief `env_belief_t` and rumour distortion `distortion_t`.

**Primary goals:**
1. Reproduce the empirical group-polarisation pattern documented by Sunstein (2001) and Isenberg (1986): isolated groups become more extreme over time, while cross-cutting exposure depolarises.
2. Reproduce the rumor-transmission patterns of Allport-Postman (1947) and Vosoughi-Roy-Aral (2018): false rumours spread faster than corrections; distortion accumulates with sharpening and leveling.
3. Provide a sentiment / belief feed for downstream trading agents so that crisis-coupled sentiment swings can be exogenised.
4. Permit ablation of the polarisation channel (set fact-checker mass to 0 or to 1) to test causal contribution to bubbles, panics, and meme-driven rallies.

**Non-goals:**
1. **Does NOT trade.** It emits no LIMIT, MARKET, or any other order. It contributes only to the `sentiment_t` and `belief_t` feeds.
2. Does NOT model individual social-network topology; the only social-graph signal is the population mean and polarisation level.
3. Does NOT solve a Bayesian belief update; opinion dynamics are linear-update rules consistent with the DeGroot (1974) framework.
4. Does NOT model attention scarcity beyond the `engagement_probability` parameter.

## Theoretical Foundation

### Theory 1 — Sunstein Group Polarisation

- **Theory/Study**: Sunstein, C. R. (2002). The law of group polarization. *Journal of Political Philosophy*, 10(2), 175–195.
- **Citation+DOI**: https://doi.org/10.1111/1467-9760.00148
- **Core Insight**: When like-minded individuals deliberate together, their views become more extreme in the direction of the pre-deliberation tendency. Cross-cutting exposure produces the opposite effect.
- **Mathematical Formulation**: For ideologue `i` with same-sign group, `opinion_{t+1} = opinion_t + α · (M_t · k_extremity − opinion_t)` with `k_extremity > 1`; for cross-cutter, `opinion_{t+1} = opinion_t · (1 − β_centering)`.
- **Empirical Evidence**: Schkade-Sunstein-Hastie (2010, *California Law Review*) document jury polarisation; Bail et al. (2018, *PNAS*) document cross-platform polarisation experiments.
- **Relevance to This Agent**: Drives the `polarizer` (Ideologue) and `depolarizer` (BridgeBuilder/CriticalThinker) modes.
- **Calibration Source**: Schkade-Sunstein-Hastie (2010) effect-sizes; Bail et al. (2018) social-media polarisation experiments.
- **Falsification Conditions**: If group polarisation does not occur in the data, the model collapses to a simple opinion-mean drift.
- **Alternative Theories**: Isenberg (1986, *Psychological Bulletin*) — persuasive arguments theory; DellaVigna-Kaplan (2007, QJE) — Fox News effect; Boxell-Gentzkow-Shapiro (2017, *PNAS*) — Internet not the cause of polarisation.

### Theory 2 — Asch Conformity

- **Theory/Study**: Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In Guetzkow (ed.), *Groups, Leadership, and Men*. Carnegie Press.
- **Citation+DOI**: https://psycnet.apa.org/record/1952-00803-001
- **Core Insight**: Individuals conform to majority opinion even when they have privately observed the truth, with conformity rate ≈ 30–35% in the classic line-judgement experiments.
- **Mathematical Formulation**: `opinion_{t+1} = opinion_t + γ · (M_t − opinion_t)`, where `γ ∈ [0, 1]` is the conformity coefficient.
- **Empirical Evidence**: Asch (1951, 1956) line-judgement experiments; Bond-Smith (1996, *Psychological Bulletin*) cross-cultural meta-analysis.
- **Relevance to This Agent**: Drives the `conformist` mode and the social-pull component of every other mode.
- **Calibration Source**: Bond-Smith (1996) cross-cultural conformity coefficient distribution.
- **Falsification Conditions**: If conformity rate is zero in the population, the social channel is silent and only direct evidence matters.
- **Alternative Theories**: Sherif (1936) — autokinetic norm formation; Latané (1981) — social-impact theory; Cialdini (2001) — six principles of influence.

### Theory 3 — Bikhchandani-Hirshleifer-Welch Informational Cascades

- **Theory/Study**: Bikhchandani, S., Hirshleifer, D. and Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026.
- **Citation+DOI**: https://doi.org/10.1086/261849
- **Core Insight**: Rational Bayesian agents who observe predecessors' actions can rationally ignore their own private signal once the public belief is sufficiently extreme — leading to fragile herd behaviour.
- **Mathematical Formulation**: Bayesian update collapses; private signal weight goes to zero when `|public_log_odds| > θ_cascade`. Translated to our linear-update form: `weight_private_t = max(0, 1 − (|M_t| − θ_cascade) / (1 − θ_cascade))`.
- **Empirical Evidence**: Anderson-Holt (1997, AER) experimental cascades; Welch (1992, JF) IPO subscription cascades; Çelen-Kariv (2004, AER) urn experiments.
- **Relevance to This Agent**: Provides the rational-foundation justification for the conformist's mode-collapse onto the consensus opinion.
- **Calibration Source**: Anderson-Holt (1997) experimental cascade-formation rates.
- **Falsification Conditions**: If cascades do not form even at high `|M_t|`, the agents are not Bayesian and the update should remain linear without a switch.
- **Alternative Theories**: Banerjee (1992, QJE) — sequential herding under certainty; Avery-Zemsky (1998, AER) — multi-dimensional cascades; Smith-Sørensen (2000, ECMA) — confounded learning.

### Theory 4 — Allport-Postman Rumor Transmission

- **Theory/Study**: Allport, G. W. and Postman, L. (1947). *The Psychology of Rumor*. Henry Holt.
- **Citation+DOI**: https://psycnet.apa.org/record/1947-04173-000
- **Core Insight**: Rumors are subject to three transformations as they propagate: leveling (loss of detail), sharpening (selective emphasis of vivid details), and assimilation (alignment with pre-existing beliefs). Belief intensity grows with importance × ambiguity.
- **Mathematical Formulation**: `belief_{t+1} = belief_t · (1 + sharpening · distortion_t) − leveling · (belief_t − round(belief_t, 0.1))`; spread intensity `s_t = belief_t · relay_eagerness`.
- **Empirical Evidence**: Bartlett (1932) serial reproduction; DiFonzo-Bordia (2007, *Rumor Psychology*) review; Vosoughi-Roy-Aral (2018, *Science*) — false news spreads faster than true on Twitter.
- **Relevance to This Agent**: Drives `rumor_spreader` mode (GullibleSpreader + DistortingRelayer).
- **Calibration Source**: DiFonzo-Bordia (2007) parameters; Vosoughi-Roy-Aral (2018) Twitter empirical decay rates.
- **Falsification Conditions**: If empirical rumor-decay rates are not matched, sharpening/leveling must be re-calibrated.
- **Alternative Theories**: Shibutani (1966) — improvised news; Rosnow (1991) — anxiety-importance-credibility model; Berinsky (2017, *British Journal of Political Science*) — political rumor correction.

### Theory 5 — DiFonzo-Bordia / Lewandowsky Correction

- **Theory/Study**: Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N. and Cook, J. (2012). Misinformation and its correction. *Psychological Science in the Public Interest*, 13(3), 106–131.
- **Citation+DOI**: https://doi.org/10.1177/1529100612451018
- **Core Insight**: Misinformation persists even after correction; effective correction requires repetition, source credibility, and explicit alternative explanations. Continued-influence effect: traces of false belief remain after retraction.
- **Mathematical Formulation**: `belief_{t+1} = belief_t · (1 − fact_check_strength · (1 − belief_t) · (1 + distortion_sensitivity · distortion_t) · credibility_discount)`.
- **Empirical Evidence**: Lewandowsky et al. (2012) review; Ecker-Lewandowsky-Tang (2010, *Memory & Cognition*) continued-influence experiments; Nyhan-Reifler (2010, *Political Behavior*) backfire effects.
- **Relevance to This Agent**: Drives the `fact_checker` mode (FactChecker + SkepticalEvaluator).
- **Calibration Source**: Lewandowsky et al. (2012) review effect-sizes.
- **Falsification Conditions**: If corrections fully reset belief (no continued-influence), `credibility_discount` should equal 1.
- **Alternative Theories**: Nyhan-Reifler (2010) — backfire effect; Ecker et al. (2022, *Nature Reviews Psychology*) — psychological drivers of misinformation belief.

### Theory 6 — DeGroot Opinion Dynamics

- **Theory/Study**: DeGroot, M. H. (1974). Reaching a consensus. *Journal of the American Statistical Association*, 69(345), 118–121.
- **Citation+DOI**: https://doi.org/10.1080/01621459.1974.10480137
- **Core Insight**: A linear update rule `x_{t+1} = W · x_t` with row-stochastic weight matrix `W` converges to a consensus determined by the eigenvector of `W`. Provides a foundational mathematical model for all opinion-dynamics simulations.
- **Mathematical Formulation**: `opinion_{t+1} = w_self · opinion_t + Σ_j w_{ij} · opinion_j_t`, with `w_self + Σ w_{ij} = 1`.
- **Empirical Evidence**: Golub-Jackson (2010, *AEJ Microeconomics*) — DeGroot wisdom of crowds; Acemoglu-Ozdaglar (2011, ARE) — opinion-dynamics review.
- **Relevance to This Agent**: All sub-modes are special cases of this linear-update rule with mode-specific weights.
- **Calibration Source**: Golub-Jackson (2010) simulated convergence rates.
- **Falsification Conditions**: If empirical opinion dynamics are non-linear (saturating, threshold-based), DeGroot is misspecified and a non-linear extension is needed.
- **Alternative Theories**: Hegselmann-Krause (2002, JASSS) — bounded confidence; Friedkin-Johnsen (1990, *J Math Sociology*) — anchored opinions; Deffuant et al. (2000, *Adv Complex Syst*) — bounded confidence with mixing rule.

## Design Purpose and Activation Triggers

| Trigger condition                                            | Activated mode                    | Effect                                   |
|--------------------------------------------------------------|-----------------------------------|------------------------------------------|
| `                                                            | M_t                               | > 0.3` AND `sign(M_t) = sign(opinion_t)` |
| `polarisation_t > θ_polar (0.3)`                             | `depolarizer`                     | Pull self-opinion toward 0               |
| `                                                            | opinion_t                         | < θ_independent`                         |
| `engagement_t < θ_engage (0.3)`                              | `passive_drifter`                 | Drift toward `M_t` slowly                |
| `env_belief_t > θ_belief (0.2)` AND `belief_t > 0.2`         | `rumor_spreader`                  | Amplify and re-transmit                  |
| `env_belief_t > θ_correction (0.3)` AND mode is fact-checker | `fact_checker`                    | Emit correction signal                   |
| `<Default>`                                                  | `passive_drifter` (low intensity) | Weak drift                               |

**Prerequisite Signals:** Population mean opinion `M_t`, polarisation `polarisation_t = std(opinion_population)`, environment belief `env_belief_t`, distortion `distortion_t`, cluster separation `cluster_sep_t`, engagement `engagement_t`.

**Missing-Signal Policy:** If `M_t` missing, hold opinion constant. If `env_belief_t` missing, force `social_mode ∈ {polarizer, depolarizer, conformist, passive_drifter}` (i.e., disable rumor modes).

**Deactivation Conditions:** Engagement burnout: if the agent has emitted `K_max = 50` consecutive non-neutral signals, force `mode_state ← cooldown` for `T_cool = 100` ticks. Permanent deactivation never occurs (the agent always remains as a background sentiment source).

Market Contribution by Regime:

| Regime                | Contribution                                | Mechanism                                                                                       |
|-----------------------|---------------------------------------------|-------------------------------------------------------------------------------------------------|
| Calm                  | Neutral                                     | Most agents in `passive_drifter` mode; small sentiment swings                                   |
| Narrative-driven boom | Strongly destabilising (via sentiment feed) | `polarizer` and `rumor_spreader` modes amplify positive sentiment, feeding momentum traders     |
| Stress                | Strongly destabilising                      | Negative-sentiment cascades amplify panic-forced-seller and herding-cascade trading             |
| Recovery              | Stabilising                                 | `fact_checker` mode dominates as corrections accumulate; sentiment normalises                   |
| Echo-chamber          | Persistently destabilising                  | Polarisation locks in extreme sentiment; downstream traders see persistent directional pressure |

Interaction with other agents: the agent's `signal_t` and `belief_t` feeds are read by `SentimentNarrativeTrader`, `HerdingCascadeAgent`, `NoiseTrader`, `OverconfidenceAndRepresentativenessTrader`, `RetailCoordinatedTrader`, and `RumorSpreadInformationAgent` (this same class in the rumor-spread role). The agent does NOT consume any trading-agent state.

## Behavioral Framework

#### Action Space (Social-Signal Adaptation of the Finance Action-Space Schema)

| Aspect               | Specification                                                                                                                                                                  |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed  | NOT APPLICABLE — agent emits signals, not orders. Signal types: `{spread, correct, polarize, depolarize, neutral, ignore}`                                                     |
| Price level rule     | NOT APPLICABLE (no price). Replaced by **Signal-sign rule**: `sign(signal_t) = sign(opinion_t)` for polarizer/conformist; `-sign(opinion_t)` for fact_checker; `0` for neutral |
| Order quantity rule  | Replaced by **Signal-intensity rule**: `intensity_t = clip(magnitude_t, 0, 1)`, where `magnitude_t` is mode-specific (see §3.6.3)                                              |
| Order lifetime       | Replaced by **Signal-lifetime in social-graph**: `T_decay = 1` tick (signal feeds into next-tick `M_{t+1}` and `env_belief_{t+1}` computation)                                 |
| Cancellation policy  | Replaced by **Retraction policy**: agent never retracts a signal; corrections are emitted as new opposite-signed signals (`correct` signal type)                               |
| Inventory constraint | Replaced by **Belief-magnitude constraint**: `                                                                                                                                 |
| Wealth/leverage cap  | Replaced by **Engagement budget cap**: `consecutive_non_neutral ≤ K_max = 50` then forced cooldown                                                                             |
| Stop-loss/kill rule  | Replaced by **Burnout/disengagement rule**: cooldown `T_cool = 100` ticks after `K_max` consecutive non-neutral emissions                                                      |

The agent does NOT use: any trading order type (LIMIT, MARKET, etc.); the trading-action-space rows above are mapped to social-signal counterparts to preserve schema parity.

#### Decision Process

1. Observe `(M_t, polarisation_t, env_belief_t, distortion_t, cluster_sep_t, engagement_t)`.
2. Determine active mode (fixed at instantiation by the `social_mode` enum draw).
3. Apply mode-specific update rule (§3.6.3) to internal `opinion_t` and/or `belief_t`.
4. Compute output signal `(signal_type, signal_intensity)`.
5. Increment `consecutive_non_neutral_counter` if signal_type ≠ `neutral`/`ignore`; trigger cooldown if `K_max` reached.

#### Mathematical Model

`polarizer` (Ideologue):
```
if opinion_t · M_t > 0:
    opinion_{t+1} = opinion_t + α_polar · (k_extremity · M_t − opinion_t)
else:
    opinion_{t+1} = opinion_t + (1 − out_group_discount) · α_polar · (M_t − opinion_t)
if |opinion_{t+1}| > 0.3:
    signal_t = (polarize, |opinion_{t+1}| · spread_eagerness)
```

`depolarizer` (BridgeBuilder + CriticalThinker):
```
if cluster_sep_t > 0.5:
    signal_t = (depolarize, bridge_strength · min(cluster_sep_t, 1.0))
elif polarisation_t > 0.3:
    signal_t = (depolarize, evidence_sensitivity · polarisation_t)
else:
    signal_t = (neutral, 0)
opinion_{t+1} = opinion_t · (1 − β_center) + bridge_weight · (0 − opinion_t)
```

`conformist`:
```
opinion_{t+1} = opinion_t + γ_conform · (local_group_mean_t − opinion_t)
if |opinion_t| > group_proximity_threshold:
    signal_t = (polarize, |opinion_t| · conformity_eagerness)
else:
    signal_t = (neutral, 0)
```

`passive_drifter`:
```
opinion_{t+1} = opinion_t + drift_rate · (M_t − opinion_t)
if random() < engagement_probability:
    if |opinion_{t+1}| > 0.5:
        signal_t = (polarize, 0.2 · |opinion_{t+1}|)
    else:
        signal_t = (neutral, 0.05)
else:
    signal_t = (ignore, 0)
```

`rumor_spreader` (Gullible + DistortingRelayer):
```
sharpening_bias = sharpening_factor · distortion_t
belief_{t+1} = belief_t + credulity · (env_belief_t · (1 + sharpening_bias) − belief_t)
belief_{t+1} = belief_{t+1} − leveling · (belief_{t+1} − round(belief_{t+1}, 0.1))
if belief_{t+1} > 0.2:
    signal_t = (spread, belief_{t+1} · relay_eagerness · (1 + distortion_amp · distortion_t))
```

`fact_checker` (FactChecker + SkepticalEvaluator):
```
belief_{t+1} = skepticism · (truth_value − belief_t) + (1 − skepticism) · 0.1 · (env_belief_t − belief_t) + belief_t
if env_belief_t > 0.3:
    signal_t = (correct, fact_check_strength · (1 − belief_{t+1}) · (1 + distortion_sensitivity · distortion_t) · credibility_discount)
else:
    signal_t = (ignore, 0)
```

#### Determinism, State, and Update Rule

**Determinism contract:** Given `(M_t, polarisation_t, env_belief_t, distortion_t, cluster_sep_t, engagement_t, opinion_t, belief_t, social_mode, RNG_seed)` the output `(signal_type, signal_intensity)` is a pure function modulo a single `Bernoulli(engagement_probability)` draw per tick in `passive_drifter` mode.

Does NOT use: `P_t`, `F_t`, order-book depth, traded volume, peer trade flow, news content, options chain, or any latency / micro-structure observable. The decision is taken from `(M_t, polarisation_t, env_belief_t, distortion_t, cluster_sep_t, engagement_t)` alone — the social information layer is strictly upstream of price.

**State variables:**
- Pre-decide observables: `M_t`, `polarisation_t`, `env_belief_t`, `distortion_t`, `cluster_sep_t`, `engagement_t`.
- Internal: `opinion_t ∈ [-1, +1]` (echo-chamber modes), `belief_t ∈ [0, 1]` (rumor modes), `consecutive_non_neutral_counter_t`, `cooldown_left_t`, `mode_state_t ∈ {active, cooldown}`.

**Update rule (post-emission, end of tick t):**
1. Apply mode-specific opinion / belief update (§3.6.3).
2. Clip `opinion_{t+1} ∈ [-1, +1]`; `belief_{t+1} ∈ [0, 1]`.
3. Update `consecutive_non_neutral_counter_{t+1}`: increment if signal_type ∉ `{neutral, ignore}`, else reset to 0.
4. Mode-state transitions: if counter ≥ `K_max` ⇒ `mode_state ← cooldown`, set `cooldown_left = T_cool`. If `cooldown_left > 0` ⇒ decrement and force signal_type = `ignore`.

## Parameters

| Symbol                     | Name                         | Default     | Range        | Units                 | Source                         | Sensitivity | Notes                           |
|----------------------------|------------------------------|-------------|--------------|-----------------------|--------------------------------|-------------|---------------------------------|
| `social_mode`              | Sub-archetype                | Categorical | enum (6)     | —                     | §3.8 mixture                   | High        | Fixed at instantiation          |
| `α_polar`                  | Polarizer update rate        | 0.10        | [0.02, 0.30] | per tick              | Sunstein (2002)                | High        | Speed of in-group amplification |
| `k_extremity`              | Extremity boost              | 1.20        | [1.05, 1.50] | dimensionless         | Schkade-Sunstein-Hastie (2010) | Medium      | Group-mean amplifier            |
| `out_group_discount`       | Out-group weight             | 0.30        | [0.0, 0.7]   | fraction              | Sunstein (2002)                | Medium      | Echo-chamber rejection          |
| `β_center`                 | Centering rate               | 0.05        | [0.01, 0.20] | per tick              | Bail et al. (2018)             | Medium      | Bridge-builder pull-to-zero     |
| `γ_conform`                | Conformity coefficient       | 0.30        | [0.10, 0.60] | per tick              | Bond-Smith (1996)              | High        | Asch-style social pull          |
| `drift_rate`               | Passive drift rate           | 0.05        | [0.01, 0.15] | per tick              | Lazarsfeld-Merton (1954)       | Medium      | Background drift                |
| `engagement_probability`   | Engagement prob (passive)    | 0.10        | [0.02, 0.30] | per tick              | Calibration                    | Low         | Stochastic emission             |
| `bridge_strength`          | Depolarizer signal gain      | 0.80        | [0.30, 1.00] | dimensionless         | Calibration                    | Medium      | Cross-cluster signal            |
| `evidence_sensitivity`     | Critical-thinker gain        | 0.60        | [0.20, 1.00] | dimensionless         | Isenberg (1986)                | Medium      | Polarisation-aware              |
| `credulity`                | Rumor-believe rate           | 0.40        | [0.10, 0.80] | per tick              | Allport-Postman (1947)         | High        | Speed of belief uptake          |
| `sharpening_factor`        | Distortion amplifier         | 0.30        | [0.05, 0.60] | dimensionless         | Allport-Postman (1947)         | High        | Rumor-distortion gain           |
| `leveling`                 | Detail-loss rate             | 0.05        | [0.01, 0.20] | per tick              | Allport-Postman (1947)         | Low         | Rounding to 0.1                 |
| `relay_eagerness`          | Spread-signal gain           | 0.70        | [0.30, 1.00] | dimensionless         | Vosoughi-Roy-Aral (2018)       | Medium      | Re-transmission                 |
| `distortion_amplification` | Distortion-spread gain       | 0.30        | [0.10, 0.60] | dimensionless         | DiFonzo-Bordia (2007)          | Medium      | Sharpening output               |
| `fact_check_strength`      | Correction signal gain       | 0.80        | [0.30, 1.00] | dimensionless         | Lewandowsky et al. (2012)      | High        | Correction power                |
| `credibility_discount`     | Source credibility           | 0.60        | [0.20, 1.00] | fraction              | Nyhan-Reifler (2010)           | Medium      | Continued-influence             |
| `distortion_sensitivity`   | Fact-checker distortion gain | 0.50        | [0.10, 1.00] | dimensionless         | Ecker et al. (2022)            | Medium      | Detection ease                  |
| `truth_value`              | Ground-truth belief          | 0.0         | [0.0, 1.0]   | belief-units          | Scenario                       | High        | What "truth" is                 |
| `skepticism`               | Fact-checker truth weight    | 0.70        | [0.30, 1.00] | fraction              | Lewandowsky et al. (2012)      | Medium      | Trust in evidence               |
| `K_max`                    | Engagement budget            | 50          | [10, 200]    | consecutive emissions | Calibration                    | Low         | Burnout                         |
| `T_cool`                   | Cooldown after burnout       | 100         | [20, 500]    | ticks                 | Calibration                    | Low         | Re-engagement                   |
| `θ_polar`                  | Polarisation activation      | 0.3         | [0.1, 0.6]   | std-units             | Sunstein (2002)                | Medium      | Depolarizer gate                |
| `θ_belief`                 | Belief activation            | 0.2         | [0.05, 0.5]  | belief-units          | Vosoughi-Roy-Aral (2018)       | Medium      | Spread gate                     |

## Population and Heterogeneity

Default mixture (calibrated to social-information benchmarks):
`p_mode = {polarizer: 0.20, depolarizer: 0.15, conformist: 0.25, passive_drifter: 0.20, rumor_spreader: 0.10, fact_checker: 0.10}`

Within each mode:
- Truncated-Normal draws on `α_polar`, `γ_conform`, `credulity` (cv ≈ 25%).
- Uniform draws on `engagement_probability` ∈ [0.02, 0.30].
- LogNormal draws on `relay_eagerness`, `fact_check_strength` (σ_log ≈ 0.30).

Population-level invariants:
1. `passive_drifter` cohort ≥ 20% of population (background mass realism).
2. `fact_checker / rumor_spreader` ratio ≥ 1.0 in scenarios calibrated to "successful correction" outcome; ≤ 0.3 in scenarios with rumor-driven panic.
3. `polarizer / depolarizer` ratio determines whether echo chamber locks in (ratio > 1.5) or self-corrects (ratio < 0.7).

## Worked Numerical Examples

**Example 1 — Polarizer in same-sign group.** State: `social_mode=polarizer, opinion_t=+0.5, M_t=+0.4, polarisation_t=0.5`.
Step 1: `opinion_t · M_t = +0.20 > 0` → in-group amplification.
Step 2: `opinion_{t+1} = 0.5 + 0.10 · (1.20 · 0.4 − 0.5) = 0.5 + 0.10 · (0.48 − 0.5) = 0.5 + 0.10 · (-0.02) = 0.498` (here mean below opinion → tiny negative pull).
Step 3: |opinion| > 0.3 → emit `(polarize, 0.498 · 0.9 = 0.448)`.
Outcome: Strong polarization signal feeds into market sentiment.

**Example 2 — Bridge builder depolarises.** State: `social_mode=depolarizer, opinion_t=+0.3, cluster_sep_t=0.8`.
Step 1: `cluster_sep > 0.5` → activate.
Step 2: `signal_t = (depolarize, 0.80 · min(0.8, 1.0) = 0.64)`.
Step 3: `opinion_{t+1} = 0.3 · 0.95 + 0.10 · (0 − 0.3) = 0.285 − 0.030 = 0.255`.
Outcome: Centering signal sent; agent's own opinion drifts toward 0.

**Example 3 — Gullible rumor-spreader.** State: `social_mode=rumor_spreader, belief_t=0.4, env_belief_t=0.6, distortion_t=0.3`.
Step 1: `sharpening_bias = 0.30 · 0.3 = 0.09`.
Step 2: `belief_{t+1} = 0.4 + 0.40 · (0.6 · 1.09 − 0.4) = 0.4 + 0.40 · (0.654 − 0.4) = 0.4 + 0.102 = 0.502`.
Step 3: After leveling: `0.502 − 0.05 · (0.502 − 0.5) = 0.502 − 0.0001 ≈ 0.502`.
Step 4: `signal_t = (spread, 0.502 · 0.70 · (1 + 0.30 · 0.3) = 0.502 · 0.70 · 1.09 = 0.383)`.
Outcome: Strong rumor signal feeds into sentiment.

**Example 4 — Fact-checker corrects.** State: `social_mode=fact_checker, belief_t=0.10, env_belief_t=0.6, distortion_t=0.3, truth_value=0`.
Step 1: `belief_{t+1} = 0.70 · (0 − 0.10) + 0.30 · 0.1 · (0.6 − 0.10) + 0.10 = −0.07 + 0.015 + 0.10 = 0.045`.
Step 2: `signal_t = (correct, 0.80 · (1 − 0.045) · (1 + 0.50 · 0.3) · 0.60 = 0.80 · 0.955 · 1.15 · 0.60 = 0.527)`.
Outcome: Strong correction signal opposing the rumor.

**Example 5 — Edge case: burnout.** State: `social_mode=polarizer, consecutive_non_neutral_counter=50`.
Step 1: Counter ≥ K_max → `mode_state ← cooldown`; `cooldown_left = 100`.
Step 2: For next 100 ticks, force `signal_type = ignore` regardless of inputs.
Outcome: Engagement burnout enforces realistic intermittency in opinion-emission.

## Validation and Calibration

**Calibration objective:** Match opinion-dynamics and rumor-transmission stylised facts:
1. Sunstein (2002) group-polarisation: in pure-polarizer cohort, `mean(|opinion|)` increases by `≥ 30%` over 100 ticks.
2. Vosoughi-Roy-Aral (2018) rumor speed: rumor cascades reach `≥ 0.3` env_belief in `≤ 50 ticks`, ≥ 6× faster than truth.
3. Bond-Smith (1996) conformity rate: per-agent opinion-mean drift ≈ 0.30 in cross-cultural mixture.
4. Lewandowsky et al. (2012) continued-influence: after fact-check signal, residual belief `≥ 0.2` of pre-correction value.

**Stylised facts:**
- Group polarisation in same-sign cohorts (Sunstein 2002).
- Asymmetric spread of rumors vs. corrections (Vosoughi-Roy-Aral 2018).
- DeGroot consensus convergence in fully-connected network (Golub-Jackson 2010).
- Continued-influence effect after correction (Lewandowsky 2012).
- Cross-cutting depolarisation when bridge-builders are present (Bail 2018).

**Ablation hooks:**
1. Set `polarizer` cohort to 0 → no echo chamber; expected effect: opinions converge to centre.
2. Set `fact_checker` to 0 → no correction; expected effect: rumor lock-in.
3. Set `out_group_discount = 0` → no echo-chamber rejection; expected effect: convergence even in heterogeneous cohort.
4. Set `engagement_probability = 1` → no passive drift; expected effect: more polarised dynamics.
5. Force `social_mode ≡ passive_drifter` → no active polarisation; expected effect: model collapses to DeGroot consensus.

**Sensitivity bounds:** `α_polar ∈ [0.02, 0.30]`, `γ_conform ∈ [0.10, 0.60]`, `credulity ∈ [0.10, 0.80]`, `fact_check_strength ∈ [0.30, 1.00]`.

## Academic References

1. Allport, G. W. & Postman, L. (1947). *The Psychology of Rumor*. Henry Holt.
2. Asch, S. E. (1951). Effects of group pressure upon the modification and distortion of judgments. In Guetzkow (ed.), *Groups, Leadership, and Men*, 177–190. Carnegie Press.
3. Sherif, M. (1936). *The Psychology of Social Norms*. Harper.
4. DeGroot, M. H. (1974). Reaching a consensus. *Journal of the American Statistical Association*, 69(345), 118–121. https://doi.org/10.1080/01621459.1974.10480137
5. Isenberg, D. J. (1986). Group polarization: A critical review and meta-analysis. *Psychological Bulletin*, 50(6), 1141–1151. https://doi.org/10.1037/0033-2909.50.6.1141
6. Friedkin, N. E. & Johnsen, E. C. (1990). Social influence and opinions. *Journal of Mathematical Sociology*, 15(3-4), 193–206. https://doi.org/10.1080/0022250X.1990.9990069
7. Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849
8. Bond, R. & Smith, P. B. (1996). Culture and conformity. *Psychological Bulletin*, 119(1), 111–137. https://doi.org/10.1037/0033-2909.119.1.111
9. Anderson, L. R. & Holt, C. A. (1997). Information cascades in the laboratory. *American Economic Review*, 87(5), 847–862.
10. Sunstein, C. R. (2002). The law of group polarization. *Journal of Political Philosophy*, 10(2), 175–195. https://doi.org/10.1111/1467-9760.00148
11. DiFonzo, N. & Bordia, P. (2007). *Rumor Psychology*. American Psychological Association.
12. Nyhan, B. & Reifler, J. (2010). When corrections fail. *Political Behavior*, 32(2), 303–330. https://doi.org/10.1007/s11109-010-9112-2
13. Schkade, D., Sunstein, C. R. & Hastie, R. (2010). When deliberation produces extremism. *Critical Review*, 22(2-3), 227–252. https://doi.org/10.1080/08913811.2010.508634
14. Golub, B. & Jackson, M. O. (2010). Naïve learning in social networks and the wisdom of crowds. *American Economic Journal: Microeconomics*, 2(1), 112–149. https://doi.org/10.1257/mic.2.1.112
15. Acemoglu, D. & Ozdaglar, A. (2011). Opinion dynamics and learning in social networks. *Annual Review of Economics*, 3, 203–229. https://doi.org/10.1146/annurev-economics-061109-080324
16. Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N. & Cook, J. (2012). Misinformation and its correction. *Psychological Science in the Public Interest*, 13(3), 106–131. https://doi.org/10.1177/1529100612451018
17. Roese, N. J. & Vohs, K. D. (2012). Hindsight bias. *Perspectives on Psychological Science*, 7(5), 411–426. https://doi.org/10.1177/1745691612454303
18. Boxell, L., Gentzkow, M. & Shapiro, J. M. (2017). Greater Internet use is not associated with faster growth in political polarization. *Proceedings of the National Academy of Sciences*, 114(40), 10612–10617. https://doi.org/10.1073/pnas.1706588114
19. Bail, C. A. et al. (2018). Exposure to opposing views on social media can increase political polarization. *Proceedings of the National Academy of Sciences*, 115(37), 9216–9221. https://doi.org/10.1073/pnas.1804840115
20. Vosoughi, S., Roy, D. & Aral, S. (2018). The spread of true and false news online. *Science*, 359(6380), 1146–1151. https://doi.org/10.1126/science.aap9559
21. Ecker, U. K. H. et al. (2022). The psychological drivers of misinformation belief and its resistance to correction. *Nature Reviews Psychology*, 1(1), 13–29. https://doi.org/10.1038/s44159-021-00006-y

## Design Provenance and Versioning

- **Source skeleton:** [SocialInformationAgents.md (skeleton, v0)](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/examples/AGENT_POOL/ExtractedExampleInvestors/unique/SocialInformationAgents.md) — derived from 11 scenario profiles (EchoChamber + RumorSpread).
- **Standardisation references:** [agent-design-skill.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-skill.md), [agent-design-finance.md](file:///Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation/masim/format/agent-design-finance.md).
- **Authored:** Batch 3.3 of unique/ standardisation pass.
- **Version:** v1.0 (pilot-depth, social-signal adaptation).
- **Notes:** This is a non-trading agent. The Action Space rows are mapped from the canonical finance schema to social-signal counterparts to preserve schema parity with the rest of the unique/ catalogue. The agent's output is a per-tick `(signal_type, signal_intensity)` feed consumed by sentiment-driven trading agents.
- **Change log:** v1.0 — initial 11-section pilot-depth authoring; six `social_mode` sub-archetypes; six theory blocks with full nine-field structure; signal-only output (no order placement).
