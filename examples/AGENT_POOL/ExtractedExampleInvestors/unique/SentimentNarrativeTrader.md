# SentimentNarrativeTrader

## Summary

| Field                        | Content                                                                                                                                                                                        |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype                    | Sentiment, narrative, media, and selective-attention traders                                                                                                                                   |
| Theory Family                | Behavioural Finance (sentiment, availability, confirmation bias); Narrative Economics; Information-Cascades                                                                                    |
| Market Role                  | **Destabilising** — amplifies recent and salient signals, drives bubble inflation and panic propagation; can be transiently stabilising for the `narrative_skeptic` sub-mode (not active here) |
| Time Horizon                 | very short (1–10 ticks); reactive to most recent salient observation                                                                                                                           |
| Risk Tolerance               | high (story-driven, not P&L-driven)                                                                                                                                                            |
| Information Asymmetry        | none (uses public price + media/sentiment proxy); over-weighting is the bias                                                                                                                   |
| Determinism                  | mostly deterministic given a `sentiment_score` input feed (one Bernoulli engagement draw per tick for `social_panic_amplifier`)                                                                |
| Merged profiles              | 7 (Sentiment Trader, Media Influenced Trader, Recent Event Overweighter, Selective Scanner, New Economy Evangelist, Social Media Influencer, Narrative Believer — across six scenarios)        |
| Source scenarios             | AssetBubble, AvailabilityBias, ConfirmationBias, DotComBubble, SVBBankRun, SouthSeaBubble                                                                                                      |
| Canonical sub-archetype enum | `sent_mode ∈ {sentiment_extrapolator, media_amplifier, recency_overweighter, selective_scanner, narrative_evangelist, social_panic_amplifier, narrative_believer}`                             |

## Definition and Goals

This agent models the **sentiment / narrative / media / selective-attention trader** family in the sense of [Real-World Counterpart §4 of `agent-design-finance.md`](../../../masim/format/agent-design-finance.md), and specifically the seven merged profiles whose decision input is a salient signal — recent return, media-amplified deviation, or a coherent story — rather than the fundamental gap. The seven modes span the LLM-style noise-trader sentiment extrapolator (Black 1986; Baker-Wurgler 2006), the media-amplification channel (Tetlock 2007), the recency-weighted availability trader (Tversky-Kahneman 1973), the asymmetric confirmation-biased selective scanner (Lord-Ross-Lepper 1979), the bubble-era narrative evangelist (Shiller 2000, 2017), the social-media panic amplifier (Bikhchandani-Hirshleifer-Welch 1992), and the historical narrative believer (Shiller 2017; South Sea Bubble case studies).

**Primary goals:**
1. Reproduce the empirical sentiment–return relation: high media tone → contemporaneous buying → short-horizon over-pricing followed by reversal (Tetlock 2007).
2. Reproduce the availability-heuristic recency overweighting: extreme recent returns produce disproportionate same-direction order flow (Tversky-Kahneman 1973).
3. Reproduce confirmation-biased asymmetric trading: confirming-signal trades are larger than contradicting-signal trades (Lord-Ross-Lepper 1979).
4. Permit ablation of single channels (sentiment-feed, media-weight, recency-weight, narrative-strength) to isolate which channel matters per scenario, in line with Baker-Wurgler (2006) factor-decomposition methodology.

**Non-goals:**
1. Does NOT solve a forward-looking utility-maximisation problem; trades are reactive to a salient signal, not optimised over a horizon.
2. Does NOT use the fundamental value `F_t` directly except to compute the deviation that the salient signal then amplifies.
3. Does NOT model the production of the sentiment / media / narrative signal — the signal is exogenous input from the environment (`sentiment_score`, `media_weight`, `social_amplification`).
4. Does NOT differentiate between rational and irrational sentiment per Baker-Wurgler (2006); all sentiment is treated as a behavioural input.

## Theoretical Foundation

### Theory 1 — Tetlock Media Sentiment

- **Theory/Study**: Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139–1168.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2007.01232.x
- **Core Insight**: Pessimistic media tone (measured via the WSJ "Abreast of the Market" column dictionary count) Granger-causes downward pressure on aggregate stock prices, with subsequent reversal. The media is not merely reporting — it is amplifying salient signals into trading flow.
- **Mathematical Formulation**: Decision signal `signal_t = (P_t − F_t)/F_t · (1 + media_weight · social_amplification)`. Order quantity proportional to `signal_t`. Reversion of the over-shoot occurs once attention shifts.
- **Empirical Evidence**: Tetlock (2007) Table 3 — 1-day VAR responses; Tetlock-Saar-Tsechansky-Macskassy (2008, JF DOI 10.1111/j.1540-6261.2008.01362.x) firm-specific evidence; Engelberg-Parsons (2011, JF DOI 10.1111/j.1540-6261.2010.01626.x) — local-media identification.
- **Relevance to This Agent**: Anchors the `media_amplifier` mode; provides the `media_weight × social_amplification` multiplier on the deviation signal.
- **Calibration Source**: Tetlock (2007); Engelberg-Parsons (2011).
- **Falsification Conditions**: If `media_weight = 0`, the agent collapses to a plain noise-trader on `(P_t − F_t)/F_t`; the media-amplification channel is silent.
- **Alternative Theories**: García (2013, JF) — newspaper-recession-period asymmetry; Loughran-McDonald (2011, JF DOI 10.1111/j.1540-6261.2010.01625.x) — finance-specific dictionary; Heston-Sinha (2017, FAJ) — news-aggregator vs. journalist-curated tone.

### Theory 2 — Tversky-Kahneman Availability Heuristic

- **Theory/Study**: Tversky, A. and Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207–232.
- **Citation+DOI**: https://doi.org/10.1016/0010-0285(73)90033-9
- **Core Insight**: People judge the probability of events by the ease with which instances come to mind. Recent and emotionally vivid events are mentally "available" and therefore over-weighted. In markets, a recent large return becomes the available reference, and traders over-react to it as if it were the new probability of future moves.
- **Mathematical Formulation**: Recency-weighted signal `signal_t = recency_weight · return_pct_t + (1 − recency_weight) · (P_t − F_t)/F_t`. With `recency_weight ∈ [0.5, 0.9]`, recent returns dominate. Order size `Q* ∝ signal_t`.
- **Empirical Evidence**: Tversky-Kahneman (1973); Barberis-Shleifer-Vishny (1998 JFE DOI 10.1016/S0304-405X(98)00027-0) — extrapolative beliefs evidence; Greenwood-Shleifer (2014, RFS DOI 10.1093/rfs/hht082) — survey extrapolation.
- **Relevance to This Agent**: Anchors the `recency_overweighter` mode; the `recency_weight` parameter controls the strength of availability.
- **Calibration Source**: Greenwood-Shleifer (2014); Barberis-Greenwood-Jin-Shleifer (2018, JFE DOI 10.1016/j.jfineco.2018.04.007).
- **Falsification Conditions**: If `recency_weight = 0`, the recency channel collapses; if `recency_weight = 1`, the agent never references the fundamental gap and behaves as a pure trend follower of returns.
- **Alternative Theories**: Hong-Stein (1999, JF DOI 10.1111/0022-1082.00184) — slow-information-diffusion alternative for under/over-reaction; Daniel-Hirshleifer-Subrahmanyam (1998, JF) — overconfidence-based alternative; De Bondt-Thaler (1985, JF DOI 10.1111/j.1540-6261.1985.tb05004.x) — long-horizon reversal channel.

### Theory 3 — Lord-Ross-Lepper Biased Assimilation

- **Theory/Study**: Lord, C. G., Ross, L. and Lepper, M. R. (1979). Biased assimilation and attitude polarization: The effects of prior theories on subsequently considered evidence. *Journal of Personality and Social Psychology*, 37(11), 2098–2109.
- **Citation+DOI**: https://doi.org/10.1037/0022-3514.37.11.2098
- **Core Insight**: People process information asymmetrically, accepting confirming evidence at face value while critically examining (or discounting) disconfirming evidence. In markets, an investor with an existing long position trades full-size on confirming bullish signals and only partial-size on contradicting bearish ones, leading to a one-sided participation pattern.
- **Mathematical Formulation**: Asymmetric multiplier `m(d_t, position_sign) = 1 if sign(d_t) = position_sign else α_disc`, with `α_disc ∈ [0.3, 0.6]`. Order size `Q* = base_size · m(d_t, position_sign) · |d_t|`.
- **Empirical Evidence**: Lord-Ross-Lepper (1979); Park-Konana-Gu-Kumar-Raghunathan (2013, MIS Quarterly) — confirmation bias in investor message boards; Cookson-Engelberg-Mullins (2023, RFS DOI 10.1093/rfs/hhac058) — political-belief-aligned trading.
- **Relevance to This Agent**: Anchors the `selective_scanner` mode; `α_disc` parameter controls the confirmation-bias asymmetry.
- **Calibration Source**: Cookson-Engelberg-Mullins (2023).
- **Falsification Conditions**: If `α_disc = 1.0`, the agent treats confirming and contradicting signals symmetrically and the bias is silent.
- **Alternative Theories**: Rabin-Schrag (1999, QJE DOI 10.1162/003355399555972) — first-impression-bias alternative model; Mullainathan-Shleifer (2005, AER DOI 10.1257/0002828054201477) — slant-supply news interpretation; Andries-Haddad (2020, JPE) — optimal-inattention rational alternative.

### Theory 4 — Shiller Narrative Economics

- **Theory/Study**: Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967–1004. Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press.
- **Citation+DOI**: https://doi.org/10.1257/aer.107.4.967 ; ISBN 978-0691050621
- **Core Insight**: Markets are driven not only by fundamentals but by spreading stories that justify behaviour. A narrative ("internet changes everything", "South-Sea Co. has a monopoly on the New World") propagates epidemic-style and produces persistent demand pressure that decouples price from fundamentals until the narrative is falsified or fades.
- **Mathematical Formulation**: Narrative-strength field `n_t ∈ [0, 1]`; while `n_t > θ_narrative`, the agent emits buy orders proportional to `n_t · base_size`, regardless of the magnitude of `(P_t − F_t)/F_t`. Decay `n_{t+1} = ρ_n · n_t + (1 − ρ_n) · 𝟙{narrative_event_t}`.
- **Empirical Evidence**: Shiller (2000); Shiller (2017); Pástor-Veronesi (2009, JF DOI 10.1111/j.1540-6261.2009.01493.x) — technological-revolution learning model; Greenwood-Nagel (2009, JFE DOI 10.1016/j.jfineco.2008.06.003) — young-fund-manager dot-com participation evidence.
- **Relevance to This Agent**: Anchors the `narrative_evangelist` and `narrative_believer` modes; provides the time-evolving narrative-strength input.
- **Calibration Source**: Pástor-Veronesi (2009); Greenwood-Nagel (2009).
- **Falsification Conditions**: If `n_t ≡ 0`, both narrative modes are silent; the bubble-period pattern of price-fundamental decoupling should not appear.
- **Alternative Theories**: Barberis-Greenwood-Jin-Shleifer (2018) — extrapolation-with-noise alternative; Pástor-Veronesi (2009) — rational-Bayesian-learning alternative; Frazzini-Pedersen (2014, JFE DOI 10.1016/j.jfineco.2013.10.005) — leverage-constrained-anomaly alternative.

### Theory 5 — Bikhchandani-Hirshleifer-Welch Information Cascades

- **Theory/Study**: Bikhchandani, S., Hirshleifer, D. and Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026.
- **Citation+DOI**: https://doi.org/10.1086/261849
- **Core Insight**: Sequential decision-making with public history can produce informational cascades in which agents rationally ignore their private signal and follow the crowd. Once started, cascades are fragile: small new public information can flip the cascade direction, producing the discontinuous panic / euphoria patterns seen in social-media-driven episodes.
- **Mathematical Formulation**: When `social_amplification > θ_cascade` and `d_t < 0`, sell pressure scales as `Q* = amplification_factor · |d_t| · base_size`, with `amplification_factor ∈ [1.5, 4.0]`.
- **Empirical Evidence**: Bikhchandani-Hirshleifer-Welch (1992); Banerjee (1992, QJE DOI 10.2307/2118364) — sequential-Bayesian cascades model; Cookson-Lu-Mullins-Niessner (2024, MS) — StockTwits cross-platform sentiment; Bradley-Hanousek-Jame-Xiao (2024 RFS) — Reddit social-cascade evidence.
- **Relevance to This Agent**: Anchors the `social_panic_amplifier` mode; `amplification_factor` controls cascade strength.
- **Calibration Source**: Cookson-Lu-Mullins-Niessner (2024); Bradley et al. (2024).
- **Falsification Conditions**: If `amplification_factor = 1`, social-cascade amplification disappears; the agent reduces to a plain noise trader during stress.
- **Alternative Theories**: Avery-Zemsky (1998, AER DOI 10.1257/aer.88.4.724) — multi-dimensional uncertainty cascade-fragility alternative; Cipriani-Guarino (2014, AEJ-Micro DOI 10.1257/mic.6.4.180) — laboratory-cascade evidence; Park-Sabourian (2011, Econometrica DOI 10.3982/ECTA8602) — herding-with-public-information.

### Theory 6 — Baker-Wurgler Investor Sentiment Index

- **Theory/Study**: Baker, M. and Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645–1680.
- **Citation+DOI**: https://doi.org/10.1111/j.1540-6261.2006.00885.x
- **Core Insight**: A composite sentiment index (closed-end fund discounts, IPO volume, equity-share-of-issuance, etc.) predicts the cross-section of returns: when sentiment is high, hard-to-arbitrage stocks earn lower subsequent returns. Sentiment is a real, measurable, economically significant input to the price-formation process.
- **Mathematical Formulation**: When `sentiment_score_t ∈ [−1, +1]` is supplied, baseline noise demand is shifted: `signal_t = (P_t − F_t)/F_t + γ_sent · sentiment_score_t`.
- **Empirical Evidence**: Baker-Wurgler (2006) Tables 4–7; Baker-Wurgler (2007, JEP DOI 10.1257/jep.21.2.129) — survey paper; Stambaugh-Yu-Yuan (2012, JFE DOI 10.1016/j.jfineco.2011.12.001) — sentiment and anomalies.
- **Relevance to This Agent**: Anchors the `sentiment_extrapolator` mode; provides the `γ_sent · sentiment_score` shifter.
- **Calibration Source**: Baker-Wurgler (2006); Stambaugh-Yu-Yuan (2012).
- **Falsification Conditions**: If `γ_sent = 0`, sentiment-channel disappears and the agent collapses to plain noise trader.
- **Alternative Theories**: Da-Engelberg-Gao (2015, RFS DOI 10.1093/rfs/hhu072) — FEARS Google-search-based alternative; Tetlock (2007) — media-tone alternative measure; Huang-Jiang-Tu-Zhou (2015, RFS DOI 10.1093/rfs/hhu080) — aligned-sentiment alternative.

## Design Purpose and Activation Triggers

| Trigger condition                                     | Activated mode           | Effect                                                     |
|-------------------------------------------------------|--------------------------|------------------------------------------------------------|
| `sentiment_score_t > θ_sent` (or `< −θ_sent`)         | `sentiment_extrapolator` | BUY (or SELL) proportional to sentiment                    |
| `media_weight · social_amplification > θ_media` AND ` | d_t                      | > θ_d`                                                     |
| `                                                     | return_pct_t             | > θ_recency`                                               |
| `sign(d_t) = sign(position)` AND `                    | d_t                      | > θ_conf`                                                  |
| `sign(d_t) ≠ sign(position)` AND `                    | d_t                      | > θ_conf`                                                  |
| `narrative_strength_t > θ_narrative`                  | `narrative_evangelist`   | BUY proportional to narrative strength (ignores valuation) |
| `narrative_strength_t > θ_narrative` AND `d_t > 0`    | `narrative_believer`     | BUY into rising over-pricing                               |
| `social_amplification > θ_cascade` AND `d_t < 0`      | `social_panic_amplifier` | Amplified SELL during stress                               |
| `<Default>`                                           | any mode                 | NO action                                                  |

**Prerequisite Signals:** price `P_t`, fundamental `F_t`, recent return `return_pct_t = (P_t − P_{t−1})/P_{t−1}`, exogenous `sentiment_score_t ∈ [−1, +1]`, `media_weight_t ∈ [0, 1]`, `social_amplification_t ∈ [1, ∞)`, `narrative_strength_t ∈ [0, 1]`.

**Missing-Signal Policy:** If `sentiment_score_t` is missing, treat as 0 (neutral). If `media_weight_t` or `social_amplification_t` are missing, treat as 1 (no amplification). If `narrative_strength_t` missing, treat as 0 (no narrative). If `F_t` missing, the agent uses a 200-tick rolling-mean fallback (consistent with NoiseTrader policy).

**Deactivation Conditions:** Wealth-based — if `cash + position · P_t < W_min`, agent stops new entries. Also deactivates if `narrative_falsified_flag` is set (e.g., for `narrative_evangelist` after a sustained drawdown of 30 ticks below `n_t < 0.2`).

Market Contribution by Regime:

| Regime         | Contribution            | Mechanism                                                                                                |
|----------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| Calm           | Mildly destabilising    | Sentiment-extrapolator and recency-overweighter add modest noise around the fundamental                  |
| Trending boom  | Strongly destabilising  | Narrative-evangelist and recency-overweighter amplify upside; social-amplification multiplies media tone |
| Trending crash | Strongly destabilising  | Social-panic-amplifier produces cascade selling; recency-overweighter compounds the downturn             |
| Reversal phase | Stabilising (transient) | Selective-scanner with opposite-side position resists reversal at half size, slowing turnaround          |
| Stress / Panic | Strongly destabilising  | All amplifier channels co-fire; cascade-driven liquidation persists below θ_cascade                      |

Interaction with other agents: amplifies signals from `MarketMakerLiquidityAgent` (consumes their liquidity), counteracted by `Arbitrageur` and `ContrarianReversalInvestor` who fade the over-shoot, fed by `SocialInformationAgents` cascade-events, and stress-amplified by `LeveragedFundInvestor.forced_unwind` flows that the social-panic-amplifier reads as additional negative deviation.

## Behavioural Framework

#### 3.6.1 State Variables

- `position`: float (+ long, − short)
- `cash`: float
- `last_return_pct`: float (1-tick lookback)
- `narrative_strength`: float ∈ [0, 1] (state, not pure observable)
- `sentiment_state`: float ∈ [−1, +1] (smoothed observable)
- `tick_index`: integer

#### 3.6.2 Decision Rule

```
on tick t:
    d_t = (P_t − F_t) / F_t                        # core deviation
    r_t = (P_t − P_{t−1}) / P_{t−1}                # recent return
    s_t = sentiment_score_t                        # exogenous input ∈ [−1,+1]
    m_t = media_weight_t · social_amplification_t  # exogenous input
    n_t = narrative_strength_t                     # state input ∈ [0,1]

    if sent_mode == sentiment_extrapolator:
        signal = d_t + γ_sent · s_t
        if |signal| > θ_act: emit MARKET sign(signal) of base_size · |signal|

    if sent_mode == media_amplifier:
        signal = d_t · (1 + media_weight · social_amplification)
        if |signal| > θ_act: emit MARKET sign(signal) of base_size · |signal|

    if sent_mode == recency_overweighter:
        signal = recency_weight · r_t + (1 − recency_weight) · d_t
        if |signal| > θ_act: emit MARKET sign(signal) of base_size · |signal|

    if sent_mode == selective_scanner:
        if sign(d_t) == sign(position):
            mult = 1.0                                  # confirming
        else:
            mult = α_disc                               # contradicting
        if |d_t| > θ_conf:
            emit MARKET sign(d_t) of base_size · mult · |d_t|

    if sent_mode == narrative_evangelist:
        if n_t > θ_narrative:
            emit MARKET buy of base_size · n_t        # always-buy under narrative
        # never sells unless narrative is falsified

    if sent_mode == narrative_believer:
        if n_t > θ_narrative and d_t > 0:
            emit MARKET buy of base_size · n_t · d_t
        elif d_t < −θ_d_neg:
            emit MARKET sell of base_size · |d_t|

    if sent_mode == social_panic_amplifier:
        if d_t < 0 and social_amplification > θ_cascade:
            emit MARKET sell of amplification_factor · |d_t| · base_size
        # only acts on negative deviation
```

#### 3.6.3 Narrative-Strength Update (state input for narrative modes)

```
on tick t:
    n_{t+1} = ρ_n · n_t + (1 − ρ_n) · 𝟙{narrative_event_t}
    if cum_drawdown_over(W_falsify ticks) < −θ_falsify:
        narrative_falsified_flag ← True
        n_{t+1} ← 0
```

#### 3.6.4 Determinism Contract and State-Update Rule

**Determinism contract:** Given `(P_t, F_t, r_t, sentiment_score_t, media_weight_t, social_amplification_t, narrative_strength_t, position, cash, sent_mode, RNG_seed)` the output `(action, Q*, T_life)` is a pure function modulo a single `Bernoulli(p_engage)` draw per tick for `social_panic_amplifier` and `media_amplifier` (engagement-probability proxy for attention). Heterogeneity comes from instantiation-time draws on `γ_sent, recency_weight, α_disc, θ_*, base_size`.

Does NOT use: `bid_ask_spread`, full order-book depth, traded volume, peer counter-party identity, options chain, fundamental cash flows, peers' inventory, or own forward P&L. The decision is taken from `(P_t, F_t, r_t, sentiment_score_t, media_weight_t, social_amplification_t, narrative_strength_t)` and the agent's own `(position, cash)` alone.

**State variables:**
- Pre-decide observables: `P_t`, `F_t`, `r_t`, `sentiment_score_t`, `media_weight_t`, `social_amplification_t`, `narrative_strength_t`.
- Internal: `position`, `cash`, `last_return_pct`, `narrative_strength`, `sentiment_state`, `tick_index`, `narrative_falsified_flag`.

**Update rule (post-fill, end of tick t):**
1. `position_{t+1} = position_t + filled_qty` (signed).
2. `cash_{t+1} = cash_t − filled_qty · fill_price`.
3. `last_return_pct_{t+1} = r_t`.
4. `narrative_strength_{t+1}` per 3.6.3.
5. `tick_index += 1`.

#### 3.6.5 Action Space

| Aspect dimension     | Rule                                                           |
|----------------------|----------------------------------------------------------------|
| Order types allowed  | MARKET (signal-driven, attention is short-lived)               |
| Price level rule     | Cross the spread; no limit price                               |
| Order quantity rule  | Per-mode (see 3.6.2); proportional to signal magnitude         |
| Order lifetime       | One tick (immediate-or-cancel)                                 |
| Cancellation policy  | Cancel-on-fill                                                 |
| Inventory constraint | Soft cap `                                                     |
| Wealth/leverage cap  | `cash + position · P_t ≥ W_min`; agent stops new entries below |
| Stop-loss/kill rule  | `narrative_falsified_flag = True` ⇒ deactivate narrative modes |

## Parameters

| Symbol                 | Name                          | Default | Range         | Units    | Source                     | Sensitivity | Notes                     |
|------------------------|-------------------------------|---------|---------------|----------|----------------------------|-------------|---------------------------|
| `γ_sent`               | Sentiment-shift coefficient   | 0.30    | [0.05, 1.00]  | none     | Baker-Wurgler (2006)       | High        | Scales sentiment input    |
| `recency_weight`       | Recency overweighting         | 0.70    | [0.30, 0.95]  | weight   | Tversky-Kahneman (1973)    | High        | 1.0 ⇒ pure trend          |
| `α_disc`               | Confirmation-bias asymmetry   | 0.50    | [0.20, 0.80]  | mult     | Cookson et al. (2023)      | High        | 1.0 ⇒ no bias             |
| `media_weight`         | Media-amplification base      | 0.50    | [0.0, 1.0]    | weight   | Tetlock (2007)             | High        | Per-tick exog input       |
| `social_amplification` | Social cascade multiplier     | 2.0     | [1.0, 5.0]    | mult     | Cookson et al. (2024)      | High        | `media_amplifier` channel |
| `θ_narrative`          | Narrative-strength trigger    | 0.40    | [0.10, 0.90]  | unitless | Shiller (2000)             | High        | Bubble-mode activation    |
| `ρ_n`                  | Narrative persistence         | 0.95    | [0.80, 0.99]  | rate     | Shiller (2017)             | Med         | AR(1) decay               |
| `θ_cascade`            | Cascade-amplification trigger | 1.5     | [1.0, 3.0]    | mult     | Bikhchandani et al. (1992) | High        | Social-panic activation   |
| `amplification_factor` | Cascade flow scale            | 2.0     | [1.0, 4.0]    | mult     | Cookson et al. (2024)      | High        | `social_panic_amplifier`  |
| `θ_act`                | Action threshold              | 0.005   | [0.001, 0.05] | return   | implementation             | Med         | Min `                     |
| `θ_conf`               | Confirmation activation       | 0.01    | [0.005, 0.05] | return   | implementation             | Med         | `selective_scanner`       |
| `θ_recency`            | Recency activation            | 0.005   | [0.001, 0.02] | return   | implementation             | Med         | `recency_overweighter`    |
| `θ_d_neg`              | Narrative-believer sell trig  | 0.05    | [0.02, 0.15]  | return   | scenario                   | Med         | Story-weakening cut       |
| `θ_falsify`            | Narrative falsification       | 0.30    | [0.10, 0.50]  | return   | scenario                   | Med         | Drawdown threshold        |
| `W_falsify`            | Falsification window          | 30      | [10, 100]     | ticks    | scenario                   | Low         | Look-back window          |
| `base_size`            | Per-trade scale               | 400     | [100, 2000]   | shares   | implementation             | High        | Order size unit           |
| `position_cap`         | Inventory cap                 | 5000    | [1000, 50000] | shares   | implementation             | Med         | Soft constraint           |
| `W_min`                | Min wealth                    | 0       | [−5e4, +5e4]  | currency | implementation             | Low         | Stop-trading floor        |
| `p_engage`             | Per-tick engagement prob      | 0.80    | [0.10, 1.00]  | prob     | implementation             | Low         | Attention proxy           |

## Population and Heterogeneity

```yaml
sent_mode_mixture:
  sentiment_extrapolator: 0.20
  media_amplifier: 0.15
  recency_overweighter: 0.20
  selective_scanner: 0.10
  narrative_evangelist: 0.10
  narrative_believer: 0.10
  social_panic_amplifier: 0.15
heterogeneity:
  gamma_sent: Lognormal(ln 0.30, 0.50)
  recency_weight: Beta(7, 3)               # mean ≈ 0.70
  alpha_disc: Beta(5, 5)                   # mean ≈ 0.50
  base_size: Lognormal(ln 400, 0.50)
  amplification_factor: Lognormal(ln 2.0, 0.30)
  rho_n: Beta(95, 5)                       # mean ≈ 0.95
```

The 0.20 fraction for `sentiment_extrapolator` and `recency_overweighter` reflects their role as the "default" retail-driven sentiment channels (consistent with Greenwood-Shleifer 2014 survey shares of extrapolative beliefs ≈ 30–40 % of households). The 0.15 social_panic_amplifier fraction matches social-media participation share documented in Bradley et al. (2024). The narrative modes (10 % each) correspond to the smaller "true believer" population observed in Pástor-Veronesi (2009).

## Worked Numerical Examples

**Case 1 — Recency overweighter on bear day (`sent_mode = recency_overweighter`)**: `r_t = −0.04, d_t = −0.01, recency_weight = 0.70, base_size = 400, θ_act = 0.005`.
- `signal = 0.70 · (−0.04) + 0.30 · (−0.01) = −0.028 − 0.003 = −0.031`. `|signal| = 0.031 > 0.005 = θ_act`.
- `Q* = 400 · 0.031 = 12.4 ≈ 12 shares`.
- Action: MARKET sell 12 shares.

**Case 2 — Media-amplifier with positive tone (`sent_mode = media_amplifier`)**: `d_t = 0.02, media_weight = 0.6, social_amplification = 2.5, base_size = 400`.
- `signal = 0.02 · (1 + 0.6 · 2.5) = 0.02 · 2.5 = 0.05`. `|signal| = 0.05 > 0.005`.
- `Q* = 400 · 0.05 = 20` shares.
- Action: MARKET buy 20 shares (deviation amplified 2.5×).

**Case 3 — Selective scanner with confirming long signal (`sent_mode = selective_scanner`, `position = +500`)**: `d_t = +0.03, α_disc = 0.5, base_size = 400, θ_conf = 0.01`.
- `sign(d_t) = +1 = sign(position)` ⇒ confirming. `mult = 1.0`. `|d_t| = 0.03 > θ_conf`.
- `Q* = 400 · 1.0 · 0.03 = 12` shares.
- Action: MARKET buy 12 shares (full size).

**Case 4 — Selective scanner with contradicting signal (same agent, next tick)**: `d_t = −0.03`.
- `sign(d_t) = −1 ≠ sign(position)` ⇒ contradicting. `mult = α_disc = 0.5`.
- `Q* = 400 · 0.5 · 0.03 = 6` shares.
- Action: MARKET sell 6 shares (only half the size — the asymmetry is the bias).

**Case 5 — Narrative evangelist in bubble (`sent_mode = narrative_evangelist`)**: `n_t = 0.80, θ_narrative = 0.40, base_size = 400, d_t = +0.15` (overpriced!).
- `n_t > θ_narrative` ⇒ narrative active. The agent ignores the +15 % overshoot.
- `Q* = 400 · 0.80 = 320` shares.
- Action: MARKET buy 320 — destabilising buy into already-overpriced market (canonical bubble dynamic).

**Edge case — Narrative falsification trigger**: `narrative_evangelist` accumulates a 30-tick drawdown of 35 % (i.e., `cum_drawdown_30 = −0.35 < −θ_falsify = −0.30`). `narrative_falsified_flag ← True`; `n_{t+1} ← 0`. From this tick on the agent emits no further buy orders. This reproduces the post-bubble exit pattern documented in Greenwood-Nagel (2009).

## Validation and Calibration

- **V1 — Tetlock media-tone reversal (Theory 1)**: Conditional on `media_weight · social_amplification > 1.5`, 1-day return reverses by 30–50 % within 5 ticks (Tetlock 2007 Table 3 magnitude). Ablation: set `media_weight = 0`.
- **V2 — Recency overweighting amplification (Theory 2)**: Cross-section regression of `Q*` on `r_t` should yield slope ≈ `recency_weight · base_size` with R² > 0.7 for the `recency_overweighter` sub-population (Greenwood-Shleifer 2014 calibration). Ablation: `recency_weight = 0`.
- **V3 — Confirmation-bias asymmetry (Theory 3)**: Mean `|Q*|` on confirming trades / contradicting trades equals `1/α_disc ≈ 2.0` for `selective_scanner` (Cookson et al. 2023 cross-sectional ratio). Ablation: `α_disc = 1.0`.
- **V4 — Narrative-driven decoupling (Theory 4)**: For `narrative_evangelist + narrative_believer` population fraction ≥ 0.20, expect persistent deviation `d_t > 0.05` for ≥ 50 ticks before falsification; mean lifetime `≈ 1/(1 − ρ_n) ≈ 20` ticks once falsification trigger fires (Pástor-Veronesi 2009 prediction). Ablation: `θ_narrative = ∞`.
- **V5 — Social cascade amplification (Theory 5)**: Conditional on `d_t < −0.02` and `social_amplification > θ_cascade`, the next-tick aggregate sell-flow is ≥ `amplification_factor` times the baseline (Cookson et al. 2024 magnitude). Ablation: `amplification_factor = 1.0`.
- **V6 — Sentiment-cross-section (Theory 6)**: Long-run correlation of population `Q*` with `sentiment_score_t` should equal `γ_sent · base_size · σ_sent` (Baker-Wurgler 2006 magnitude). Ablation: `γ_sent = 0`.

**Ablation Hooks**:
- `media_weight = 0` → disables Theory 1 (media channel).
- `recency_weight = 0` → disables Theory 2 (availability channel).
- `α_disc = 1` → disables Theory 3 (confirmation asymmetry).
- `θ_narrative = ∞` → disables Theory 4 (narrative channel).
- `amplification_factor = 1` → disables Theory 5 (cascade channel).
- `γ_sent = 0` → disables Theory 6 (sentiment-index channel).

## Academic References

1. Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139–1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
2. Tetlock, P. C., Saar-Tsechansky, M. and Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. *Journal of Finance*, 63(3), 1437–1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x
3. Loughran, T. and McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *Journal of Finance*, 66(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
4. Tversky, A. and Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207–232. https://doi.org/10.1016/0010-0285(73)90033-9
5. Barberis, N., Shleifer, A. and Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
6. Greenwood, R. and Shleifer, A. (2014). Expectations of returns and expected returns. *Review of Financial Studies*, 27(3), 714–746. https://doi.org/10.1093/rfs/hht082
7. Lord, C. G., Ross, L. and Lepper, M. R. (1979). Biased assimilation and attitude polarization. *Journal of Personality and Social Psychology*, 37(11), 2098–2109. https://doi.org/10.1037/0022-3514.37.11.2098
8. Cookson, J. A., Engelberg, J. E. and Mullins, W. (2023). Echo chambers. *Review of Financial Studies*, 36(2), 450–500. https://doi.org/10.1093/rfs/hhac058
9. Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967–1004. https://doi.org/10.1257/aer.107.4.967
10. Pástor, Ľ. and Veronesi, P. (2009). Technological revolutions and stock prices. *American Economic Review*, 99(4), 1451–1483. https://doi.org/10.1257/aer.99.4.1451
11. Greenwood, R. and Nagel, S. (2009). Inexperienced investors and bubbles. *Journal of Financial Economics*, 93(2), 239–258. https://doi.org/10.1016/j.jfineco.2008.06.003
12. Bikhchandani, S., Hirshleifer, D. and Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849
13. Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797–817. https://doi.org/10.2307/2118364
14. Baker, M. and Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of Finance*, 61(4), 1645–1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x
15. Da, Z., Engelberg, J. and Gao, P. (2015). The sum of all FEARS: Investor sentiment and asset prices. *Review of Financial Studies*, 28(1), 1–32. https://doi.org/10.1093/rfs/hhu072

## Design Provenance and Versioning

- **Source skeletons**: `examples/AGENT_POOL/ExtractedExampleInvestors/unique/SentimentNarrativeTrader.md` (legacy); seven merged scenario profiles from `AssetBubble`, `AvailabilityBias` (×2), `ConfirmationBias`, `DotComBubble`, `SVBBankRun`, `SouthSeaBubble`.
- **Standard reference**: [agent-design-skill.md](../../../masim/format/agent-design-skill.md) (12-section canonical handbook); [agent-design-finance.md](../../../masim/format/agent-design-finance.md) (finance addendum).
- **Authoring batch**: Batch 4.5 — universalised pilot-depth standardisation pass.
- **Version**: 1.0 (initial pilot-depth synthesis).
- **Date**: 2026-06-23.
