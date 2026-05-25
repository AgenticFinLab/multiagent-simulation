# AvailabilityBias — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Availability Bias in Financial Markets                                                                                                                                                                                                              |
| Category           | Cognitive bias / behavioral finance / heuristic-driven overreaction                                                                                                                                                                                 |
| Core Mechanism     | Investors overweight information that is cognitively "available" — i.e., recent, vivid, or heavily covered in media — relative to its actual statistical relevance. This distorts price signals, creating systematic overreaction to salient events |
| Real-World Origin  | Documented in post-crash surveys (Shiller, 1987), earnings-announcement overreactions (Bernard & Thomas, 1989), and media-driven return predictability (Tetlock, 2007)                                                                              |
| Research Relevance | Isolates how cognitive salience (not just information) drives price distortion; contrasts availability-biased agents with rational benchmarks (SystematicAnalyst, ValueTrader) to quantify the bias's market impact                                 |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Availability bias enters financial-market modeling through a chain from cognitive psychology to behavioral asset pricing. Tversky and Kahneman (1973) identify availability as a probability-judgment heuristic: people use ease of recall as evidence about frequency or likelihood. In a market, recent and vivid price moves therefore become decision inputs even when the public fundamental value is unchanged.

The finance link is the overreaction literature. De Bondt and Thaler (1985) show that dramatic past winners and losers later reverse, consistent with salient events being overweighted relative to fundamentals. Tetlock (2007) adds the media channel: repeated public narratives can make market conditions feel more important and persistent than objective signals justify.

This simulation operationalizes that lineage as two destabilizing channels and two stabilizing benchmarks. RecentEventOverweighter represents recent-event salience, MediaInfluencedTrader represents media/social salience, SystematicAnalyst represents objective weighting, and ValueTrader represents fundamental anchoring.

#### §1.1.2 Real-World Event Catalogue

| Event | Quantitative Magnitude | Availability Channel | Simulation Agent Correspondence |
|---|---|---|---|
| Post-earnings announcement drift | abnormal drift over roughly 60 trading days after earnings surprises (Bernard & Thomas 1989, DOI: 10.2307/2491062) | recent salient corporate news | RecentEventOverweighter, SystematicAnalyst |
| September 11 market reopening | S&P 500 fell about 14.3% after the four-day closure, then recovered much of the loss within weeks | vivid catastrophic event and continuous media coverage | RecentEventOverweighter, MediaInfluencedTrader, ValueTrader |
| COVID-19 crash | S&P 500 fell about 34% from 2020-02-19 to 2020-03-23 and recovered by August 2020 | salient daily losses plus intensive media/social amplification | MediaInfluencedTrader, RecentEventOverweighter, SystematicAnalyst |

#### §1.1.3 Book and Practitioner Literature

| Source | Role in Scenario Design |
|---|---|
| Kahneman, D. (2011). *Thinking, Fast and Slow*. | Practitioner-facing account of availability and System 1 salience. |
| Graham, B. (1949). *The Intelligent Investor*. | Practitioner foundation for the ValueTrader's fundamental anchor. |
| Shiller, R. J. (2000). *Irrational Exuberance*. | Market narrative and salience account linking public attention to mispricing. |


## §2 Theoretical Foundation

### 2.1 The Availability Heuristic (Tversky & Kahneman)

- **Citation**: Tversky, A., & Kahneman, D. (1973). "Availability: A heuristic for judging frequency and probability." *Cognitive Psychology*, 5(2), 207–232. DOI: 10.1016/0010-0285(73)90033-9
- **Core Insight**: People estimate the probability of an event by how easily examples come to mind — "availability" as a mental shortcut. In markets, events that are recent, emotionally charged, or heavily covered become cognitively salient, leading investors to overestimate their recurrence probability. A dramatic market decline last round is weighted more heavily than its long-run base rate would justify.
- **Mathematical Formulation**: The availability heuristic can be represented as a biased signal-weighting function. In operational form: perceived_signal = recency_weight × recent_return + (1 − recency_weight) × deviation. With recency_weight = 0.70, the most recent return receives most of the signal weight while the objective deviation receives only 30%.
- **Empirical Evidence**: Tversky & Kahneman (1973) document that subjects overestimate event frequencies for salient, easily recalled examples across domains. In financial contexts: De Bondt & Thaler (1985) show that stocks with dramatic recent returns (large positive or negative) are subsequently overpriced or underpriced, consistent with availability-driven overreaction.
- **Relevance to Investor Taxonomy**: The RecentEventOverweighter agent directly operationalizes this: it computes `perceived_signal = 0.70 × return_pct + 0.30 × deviation` and trades when this exceeds `salience_threshold = 0.02`. The 70% recent-return weight makes the most available event dominate the objective price-fundamental signal.

### 2.2 Ease of Retrieval and Media Salience (Schwarz et al.)

- **Citation**: Schwarz, N., Bless, H., Strack, F., Klumpp, G., Rittenauer-Schatka, H., & Simons, A. (1991). "Ease of retrieval as information: Another look at the availability heuristic." *Journal of Personality and Social Psychology*, 61(2), 195–202. DOI: 10.1037/0022-3514.61.2.195. Also: Tetlock, P. C. (2007). "Giving content to investor sentiment: The role of media in the stock market." *Journal of Finance*, 62(3), 1139–1168. DOI: 10.1111/j.1540-6261.2007.01232.x
- **Core Insight**: Schwarz et al. (1991) demonstrate that the *ease* of retrieving information — not just its frequency — drives judgment. Information that is widely publicized (high media saturation) is retrieved easily and thus perceived as more probable or important than less-covered information. Tetlock (2007) provides direct financial evidence: high media coverage of a stock predicts subsequent return reversal, consistent with media-driven overreaction followed by correction.
- **Mathematical Formulation**: Media-amplified signal: amplified_signal = media_weight × deviation × social_amplification. With media_weight = 0.80 and social_amplification = 1.50: amplified_signal = 1.20 × deviation. This means a deviation must be salient enough to cross the 3% amplified-signal threshold before the media-influenced trader acts.
- **Empirical Evidence**: Tetlock (2007) documents that abnormal media coverage predicts return reversals within 2–3 weeks, with initial price response larger than fundamentals alone would justify. The current calibration uses social_amplification = 1.50 with a conservative 0.80 media weight.
- **Relevance to Investor Taxonomy**: The MediaInfluencedTrader operationalizes media-driven availability: its `amplified_signal = media_weight × deviation × social_amplification` captures how media framing multiplies the perceived importance of fundamental signals beyond their informational content.

### 2.3 Memory-Based Bounded Rationality (Mullainathan)

- **Citation**: Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735–774. DOI: 10.1162/003355302760193887
- **Core Insight**: Mullainathan formalizes how memory retrieval constraints create systematic, predictable deviations from Bayesian rationality. Agents with limited memory capacity are more likely to recall events that were emotionally salient (crashes, spikes) than routine fluctuations — creating a biased sample from which they estimate probabilities. This memory bias produces overreaction to extreme events and underreaction to gradual trends.
- **Mathematical Formulation**: Bayesian posterior: P(signal | history) = Σ_t w_t × signal_t / Σ_t w_t where w_t = 1 for all t (rational). Memory-biased: w_t = e^{α × |signal_t|} (salience weighting), creating overweighting of large past signals. In simulation form: SystematicAnalyst uses flat weights (rational benchmark); biased agents use elevated recency/media weights.
- **Relevance to Investor Taxonomy**: The SystematicAnalyst is the rational benchmark implied by Mullainathan's model: it weighs all signals by objective relevance (deviation only, no recency amplification). The contrast between SystematicAnalyst and availability-biased agents quantifies the memory-bias premium.

### 2.4 Investor Sentiment and Fundamental Anchoring

- **Citation**: Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129–151. DOI: 10.1257/jep.21.2.129. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.
- **Core Insight**: Baker & Wurgler (2007) document systematic return predictability from investor sentiment proxies, consistent with availability-biased investors collectively driving prices away from fundamentals. Sentiment episodes persist long enough to create measurable mispricing. The stabilizing counterforce is fundamental anchoring — investors who ignore sentiment and trade on price-to-fundamental ratios.
- **Empirical Evidence**: Baker & Wurgler (2007) find that high-sentiment periods predict low subsequent returns for difficult-to-value stocks, consistent with availability bias driving speculative overreaction. Effect size: overvaluation of 5–15% during peak sentiment episodes.
- **Relevance to Investor Taxonomy**: ValueTrader embodies Graham's fundamental anchoring principle — deviation_threshold = 0.05 means it ignores smaller price movements and trades only when the price-fundamental gap is clearly large enough for a value response, immune to availability-biased sentiment.


## §3 Market Design Principles

### 3.1 Price Formation Model

Formula: **P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)**

| Symbol     | Meaning                    | Value           | Economic Justification                                                                                                                       | Calibration Source                                                |
|------------|----------------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| P(t)       | Current market price       | starts at 100.0 | Normalized; scale-neutral                                                                                                                    | —                                                                 |
| D(t)       | Net demand (buy − sell)    | computed        | Aggregate order imbalance from all agents each round                                                                                         | —                                                                 |
| F          | Fundamental value          | 100.0           | Constant — isolates cognitive bias from fundamental news. Availability bias is a perceptual distortion, not an information advantage         | Normalization                                                     |
| λ (lambda) | Price impact coefficient   | 0.02            | MODERATE — reflects a liquid market where bias causes meaningful but not extreme price movements; enough for measurable overreaction         | Calibrated to behavioral overreaction magnitude in Tetlock (2007) |
| γ (gamma)  | Mean-reversion coefficient | 0.03            | Moderate — fundamental gravity gradually corrects availability-biased mispricing; not too fast (which would prevent observable bias effects) | Baker & Wurgler (2007) sentiment persistence                      |
| ε(t)       | Gaussian noise ~ N(0, σ²)  | σ = 0.5         | Moderate noise — less noisy than crash simulations; bias effects should be distinguishable from random fluctuations                          | Standard calibration                                              |

**Design Rationale**:
- λ = 0.02 is moderate: availability bias creates measurable mispricings but not catastrophic cascades. This is appropriate for a cognitive bias simulation where the phenomenon is persistent overreaction, not acute crash dynamics.
- γ = 0.03 creates a mean-reversion force that competes with the bias: the simulation's key question is whether biased agents' collective selling/buying dominates γ-mean-reversion, producing persistent mispricing, or whether mean reversion quickly corrects the bias.
- Constant F = 100.0 is essential: availability bias is a *perceptual* distortion of the same publicly available information. If F changed, we could not isolate the bias from rational responses to genuine news.
- Market also broadcasts `prev_price` and `return_pct` because availability-biased agents (particularly RecentEventOverweighter) require the most recent return as their salience signal.

### 3.2 Additional Market Mechanisms

- **Price floor**: `max(price, 0.01)` — prevents numerical collapse.
- **prev_price broadcasting**: Unlike other simulations, the Market broadcasts `prev_price` and `return_pct` each round. This is required by RecentEventOverweighter, whose perceived signal depends on the most recent return (the "available" event).

### 3.3 Information Broadcast Design

Each round, the Market sends to all investors:

| Field         | Value / Formula          | Rationale                                                                                                                            |
|---------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `price`       | P(t)                     | Current market price                                                                                                                 |
| `prev_price`  | P(t−1)                   | Required by RecentEventOverweighter for recency signal computation; embodies the "most available" recent data point                  |
| `fundamental` | 100.0 (constant)         | True intrinsic value; used by SystematicAnalyst and ValueTrader; known to all but overridden by availability in biased agents        |
| `deviation`   | (P(t) − F) / F           | Primary signal for SystematicAnalyst, ValueTrader, MediaInfluencedTrader; objective mispricing measure                               |
| `return_pct`  | (P(t) − P(t−1)) / P(t−1) | Most recent return; the "available" salient signal for RecentEventOverweighter; central to availability heuristic operationalization |
| `round`       | t                        | Simulation round; used for logging and phase analysis                                                                                |


## §4 Investor Taxonomy

### Investor: RecentEventOverweighter

#### 4.1.1  Summary

The RecentEventOverweighter is a retail or semi-institutional investor who gives disproportionate weight to the most recent market event in forming their outlook. When the market has just moved sharply (large `return_pct`), this investor perceives the current moment as abnormally significant — a directionally important signal — and trades accordingly, regardless of whether the recent move reflects any genuine change in fundamental value. This investor embodies the availability heuristic in its purest market form: the "available" event (the salient recent return) dominates the objective signal (fundamental deviation). In equilibrium, this creates systematic overreaction to recent price moves and underreaction to slow-developing fundamental trends.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Availability Heuristic (Tversky & Kahneman)**
- Theory / Study: Availability heuristic in probability estimation
- Citation: Tversky, A., & Kahneman, D. (1973). "Availability: A heuristic for judging frequency and probability." *Cognitive Psychology*, 5(2), 207–232. DOI: 10.1016/0010-0285(73)90033-9
- Core Insight: Recent, dramatic events are retrieved from memory more easily than routine events, creating the illusion that they are more probable. Applied to markets: a large price move last round creates a salient mental template that is overweighted in forming the next trading decision.
- Mathematical Formulation: Biased signal weighting: perceived_signal = recency_weight × return_pct + (1 − recency_weight) × deviation. With recency_weight = 0.70, the most recent return receives 70% of the perceived signal and the objective deviation receives 30%.
- Empirical Evidence: De Bondt & Thaler (1985) document a 3-year reversal following extreme past returns — consistent with availability-driven overreaction creating mispricing that mean-reverts. The simulation calibrates this channel as a high, but bounded, 70% weight on the most recent return.
- Relevance to This Investor: `perceived_signal = 0.70 × return_pct + 0.30 × deviation`. This creates a situation where a large recent return dominates the objective deviation signal — the core availability distortion.

**Theory 2: Overreaction and Return Reversal (De Bondt & Thaler)**
- Theory / Study: Mean reversion following extreme past returns — availability-driven overreaction
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreact?" *Journal of Finance*, 40(3), 793–805. DOI: 10.2307/2327804
- Core Insight: Investors systematically overreact to dramatic recent news, pushing prices beyond fundamentals; subsequent return reversal is the correction. De Bondt & Thaler (1985) find that portfolios of "extreme loser" stocks over 3–5 years outperform "extreme winner" stocks by 24.6% over the subsequent 3 years — the reversal confirming prior overreaction.
- Empirical Evidence: The 24.6% three-year reversal documented by De Bondt & Thaler (1985) implies a meaningful initial overreaction before later correction. In simulation terms, a 70% recent-return weight makes short-run returns dominate the signal while keeping the response bounded.
- Relevance to This Investor: salience_threshold = 0.02 (2%) is calibrated so that RecentEventOverweighter activates on meaningful recent moves, creating the directional overreaction documented by De Bondt & Thaler; the simulation tests whether this overreaction is self-correcting or persistent.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Model the availability-heuristic channel by which recent dramatic price moves are amplified into continued overreaction. Without RecentEventOverweighter, the simulation cannot generate the self-reinforcing overreaction dynamic where a salient price move triggers further over-trading in the same direction.

**Activation Scenarios**:
- Scenario A (Positive perceived signal > 0.02): buy. Chases recent positive momentum, driving prices further above fundamental.
- Scenario B (Negative perceived signal < -0.02): sell. Panic sells following a salient decline, amplifying the decline beyond what fundamentals warrant.
- Scenario C (Small perceived signal): hold. Most rounds are holds — activation requires a salient event.

**Market Contribution**: Destabilizing — amplifies recent directional moves. Creates momentum (positive autocorrelation in returns during salient-event episodes). The key question is whether this overreaction is large enough to produce measurable persistent mispricing.

**Interaction with other agents**: Amplifies noise-driven moves that MediaInfluencedTrader may also amplify; countered by SystematicAnalyst (which uses objective deviation) and ValueTrader (which requires extreme deviation before acting); may reinforce itself across rounds as its own buying/selling creates the salient returns that trigger the next round's activation.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `return_pct`: The primary "available" signal — the most recent price return. This is the cognitively salient input that the availability heuristic overweights. recency_weight = 0.70 gives this signal most of the perceived-signal weight.
- `deviation`: Secondary objective signal — the objective price-to-fundamental gap. Present in the perceived_signal formula with weight 0.30.
- Does NOT separately maintain a history buffer of returns for multi-period weighting — uses only the single most recent return_pct, consistent with availability heuristic's emphasis on the *most* recently available event.

**4.1.4.2  Core Behavioral Mechanism**
1. Each round, observe `return_pct` and `deviation` from market broadcast.
2. Compute: perceived_signal = recency_weight × return_pct + (1 − recency_weight) × deviation = 0.70 × return_pct + 0.30 × deviation.
3. If |perceived_signal| > salience_threshold (0.02): trade.
4. If perceived_signal > 0 (net positive signal): buy. Quantity = min(300, |perceived_signal| × 5000). Cash-constrained.
5. If perceived_signal < 0 (net negative signal): sell. Quantity = min(300, |perceived_signal| × 5000). Position-constrained.
6. Hold if |perceived_signal| ≤ 0.02.
7. The sizing formula (|perceived_signal| × 5000) means a perceived_signal of 0.06 produces quantity = 300 shares — maximum; a signal of 0.02 would produce 100 shares.

**4.1.4.3  Mathematical Model**
- Decision variable: Q*(t) in shares
- Perceived signal: s̃(t) = ρ × r(t) + (1 − ρ) × δ(t), where ρ = recency_weight = 0.70, r = return_pct, δ = deviation
- Trigger function: trade if |s̃(t)| > θ (θ = salience_threshold = 0.02)
- Sizing: Q*(t) = min(Q_max, |s̃(t)| × 5000), where Q_max = 300
- Direction: buy if s̃(t) > 0; sell if s̃(t) < 0
- State variables: cash, position (updated each trade)

| Parameter          | Value | Meaning                                     | Config Path                                                     | Source                                              |
|--------------------|-------|---------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------|
| recency_weight     | 0.70  | Weight on most recent return                | `configs/AvailabilityBias/Rule/players.yml → recent_event_overweighter` | Tversky & Kahneman (1973); De Bondt & Thaler (1985) |
| salience_threshold | 0.02  | Perceived signal threshold for trading      | `configs/AvailabilityBias/Rule/players.yml → recent_event_overweighter` | Calibrated to 2% salience filter                    |
| initial_cash       | 10000 | Starting cash reserves                      | `configs/AvailabilityBias/Rule/players.yml → recent_event_overweighter` | Normalization                                       |
| initial_position   | 0     | Starting share position                     | `configs/AvailabilityBias/Rule/players.yml → recent_event_overweighter` | Normalization                                       |

**4.1.4.4  Behavioral Properties**
- Time horizon: Short-term — reacts to each round's most recent return; no multi-period horizon
- Risk tolerance: High — chases momentum signals without considering fundamental value; would buy into bubbles and sell into crashes
- Information asymmetry: None — uses publicly broadcast return_pct; the "advantage" is perceptual distortion, not private information
- Psychological profile: Reactive, momentum-following, availability-biased. Prone to chasing recent winners and fleeing recent losers. In LLM variants, the persona emphasizes "I was impressed by last round's dramatic move" as the primary decision driver.

#### 4.1.5  Decision Process Walkthrough

Given: price = 103.0, fundamental = 100.0, deviation = +0.03, prev_price = 100.0, return_pct = +0.03, recency_weight = 0.70, salience_threshold = 0.02, cash = 10000, position = 0

Step 1: Compute perceived_signal = 0.70 × 0.03 + 0.30 × 0.03 = 0.03.
Step 2: Is |0.03| > 0.02? YES → buy.

Revised example with larger return:
Given: return_pct = +0.025, deviation = +0.03

Step 1: perceived_signal = 0.70 × 0.025 + 0.30 × 0.03 = 0.0265. Salient enough to trade.

Example with salient return:
Given: return_pct = +0.04, deviation = +0.03

Step 1: perceived_signal = 0.70 × 0.04 + 0.30 × 0.03 = 0.037.
Step 2: |0.037| > 0.02? YES → trade (buy, since signal > 0).
Step 3: Quantity = min(300, 0.037 × 5000) = min(300, 185) = 185 shares.
Step 4: Cost check: 185 × 103 = 19055, so cash-constrained quantity is 97.09 shares when starting cash is 10000.
Step 5: Send order: action=buy, quantity≈97.09, bid_price=103.
Result: upward price pressure of λ × 97.09 ≈ 1.94 price units. Overreaction to a 4% recent return creates additional buying that drives price further above fundamental.

#### 4.1.6  Worked Numerical Example

Market state: price = 98.0, fundamental = 100.0, deviation = −0.02, prev_price = 102.0, return_pct = −0.039 (−3.9% decline last round), recency_weight = 0.70, salience_threshold = 0.02

Perceived signal: s̃ = 0.70 × (−0.039) + 0.30 × (−0.02) = −0.0333.
|−0.0333| > 0.02 → sell.
Quantity: min(300, 0.0333 × 5000) = 166.5 shares, then constrained by current position.
Order: action=sell, quantity=166.5 if the investor has sufficient position, bid_price=98.
Rationale: The dramatic -3.9% decline last round is cognitively "available" — the investor perceives this as a strong negative signal because recent return receives 70% of the perceived-signal weight. Despite the objective deviation being only -2% (a mild undervaluation that a rational investor would buy), the availability-biased investor sells if it has inventory, amplifying the decline. This is De Bondt & Thaler's overreaction mechanism in action.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                               |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1973). "Availability: A heuristic for judging frequency and probability." *Cognitive Psychology*, 5(2), 207–232. DOI: 10.1016/0010-0285(73)90033-9 | Core theoretical basis; recency_weight calibration                  |
| 2 | De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreact?" *Journal of Finance*, 40(3), 793–805. DOI: 10.2307/2327804                                       | Empirical overreaction and reversal; salience_threshold calibration |
| 3 | Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.                                                                                                      | System 1 vs. System 2; availability bias as System 1 default        |


---

### Investor: MediaInfluencedTrader

#### 4.2.1  Summary

The MediaInfluencedTrader is an investor whose perceptions of market conditions are shaped by media framing and social signal amplification rather than direct observation of price-fundamental relationships. When the media covers a market event intensively (proxied by the deviation signal being amplified by media_weight × social_amplification), this investor perceives the event as more significant than it is. This investor does not overweight recent returns (unlike RecentEventOverweighter) but instead overweights the magnitude of any current deviation — treating deviation as a media-salient signal with 1.2× perceived intensity. This creates a distinct channel: availability through media salience rather than temporal recency.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Media Influence on Asset Prices (Tetlock)**
- Theory / Study: Media coverage as a driver of investor sentiment and return predictability
- Citation: Tetlock, P. C. (2007). "Giving content to investor sentiment: The role of media in the stock market." *Journal of Finance*, 62(3), 1139–1168. DOI: 10.1111/j.1540-6261.2007.01232.x
- Core Insight: Tetlock (2007) finds that media pessimism (negative language in Wall Street Journal columns) predicts downward pressure on Dow Jones next day and subsequent reversal within 1–2 weeks. The initial price impact is driven by sentiment-influenced retail investors (the MediaInfluencedTrader archetype); the subsequent reversal reflects rational correction. The effect is linear in media intensity.
- Mathematical Formulation: Tetlock (2007) estimates a 1 standard deviation increase in media pessimism predicts a −0.5% market return, with reversal within 3–5 days. Extrapolated to simulation: media_weight × deviation × social_amplification = 0.80 × deviation × 1.50 = 1.20 × deviation.
- Empirical Evidence: Tetlock (2007) Table 2 shows that media pessimism explains 11–18% of next-day return variance for high-coverage stocks. Amplification consistent with social_amplification = 1.5 (50% additional amplification from social/network effects beyond direct media).
- Relevance to This Investor: amplified_signal = 0.80 × deviation × 1.50 = 1.20 × deviation. The signal threshold of 0.03 means the MediaInfluencedTrader activates at |deviation| > 0.025.

**Theory 2: Social Amplification of Risk (Schwarz et al.; Kasperson et al.)**
- Theory / Study: Social amplification creating cascade effects in perceived risk
- Citation: Schwarz, N., et al. (1991). "Ease of retrieval as information." *Journal of Personality and Social Psychology*, 61(2), 195–202. DOI: 10.1037/0022-3514.61.2.195. Also: Kasperson, R. E., et al. (1988). "The social amplification of risk: A conceptual framework." *Risk Analysis*, 8(2), 177–187. DOI: 10.1111/j.1539-6924.1988.tb01168.x
- Core Insight: Schwarz et al. (1991) show that information delivered through high-profile channels (more "available" due to broadcast intensity) is perceived as more important even when the underlying content is identical to less-publicized information. Kasperson et al. (1988) develop the Social Amplification of Risk Framework (SARF) showing how social networks multiply the perceived importance of risk signals. Applied to markets: social_amplification captures the multiplicative effect of network-based information spread.
- Empirical Evidence: Kasperson et al.'s SARF documents amplification factors of 1.5–3.0 across different risk domains; social_amplification = 1.5 is at the conservative end of this range, consistent with mature financial markets with professional investor participation.
- Relevance to This Investor: social_amplification = 1.5 is the network amplification factor applied on top of the direct media weight; the two combined (media_weight × social_amplification = 1.20) represent the total perceived signal inflation from media coverage.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the media-salience channel of availability bias — where the *intensity of coverage* (not the recency of an event) amplifies the perceived importance of fundamental signals. Creates overreaction to current fundamental deviations that are heavily covered.

**Activation Scenarios**:
- Scenario A (Small deviation, |deviation| < 0.025): |amplified_signal| < 0.03 → hold. Even media amplification is insufficient to trigger trading.
- Scenario B (Moderate deviation, 0.025 < |deviation| < 0.05): |amplified_signal| = 0.03–0.06 → trade proportionally. Media is covering the deviation intensively; investor reacts more strongly than objective analysis alone would justify.
- Scenario C (Large deviation, |deviation| > 0.05): |amplified_signal| > 0.06 → trade with larger proportional size. Intensive media coverage of a significant fundamental gap triggers stronger activation.

**Market Contribution**: Destabilizing — amplifies fundamental deviations into larger price moves than rational analysis would produce. Unlike RecentEventOverweighter (which amplifies momentum), MediaInfluencedTrader amplifies level-based deviations — a different and potentially complementary destabilizing mechanism.

**Interaction with other agents**: Amplifies the same deviations that SystematicAnalyst is correcting (both respond to deviation, but MediaInfluencedTrader overreacts); may amplify the same direction as RecentEventOverweighter when a large deviation was preceded by a dramatic return.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary signal — multiplied by media_weight × social_amplification to produce the amplified_signal. This represents media coverage intensity as a function of current mispricing.
- `price`: Used for order submission and cash constraint calculation.
- Does NOT use `return_pct` — the MediaInfluencedTrader responds to media framing of *current state* (deviation level), not recent event salience. This is distinct from RecentEventOverweighter.

**4.2.4.2  Core Behavioral Mechanism**
1. Each round, observe `deviation` from market broadcast.
2. Compute: amplified_signal = media_weight × deviation × social_amplification = 0.80 × deviation × 1.50 = 1.20 × deviation.
3. If |amplified_signal| > 0.03: trade. (Equivalent to |deviation| > 0.025.)
4. If amplified_signal > 0 (market above fundamental; media narrative amplifies optimism): buy. Quantity = min(300, amplified_signal × 5000). Cash-constrained.
5. If amplified_signal < 0 (market below fundamental; media narrative amplifies pessimism): sell. Quantity = min(300, |amplified_signal| × 5000). Position-constrained.
6. Hold if |amplified_signal| ≤ 0.03.
7. The media-amplified signal is directional with respect to deviation: it buys into positive media salience and sells into negative media salience, making the reaction destabilizing when media framing reinforces the current mispricing.

**4.2.4.3  Mathematical Model**
- Decision variable: Q*(t) in shares
- Amplified signal: ã(t) = m_w × δ(t) × s_a, where m_w = media_weight = 0.80, s_a = social_amplification = 1.50, δ = deviation
- Trigger: trade if |ã(t)| > 0.03 (implicitly, |δ| > 0.025)
- Sizing: Q*(t) = min(Q_max, |ã(t)| × 5000), where Q_max = 300
- Direction: buy if ã(t) > 0; sell if ã(t) < 0
- State variables: cash, position

| Parameter            | Value | Meaning                                           | Config Path                                                   | Source                  |
|----------------------|-------|---------------------------------------------------|---------------------------------------------------------------|-------------------------|
| media_weight         | 0.80  | Media intensity amplification of deviation signal | `configs/AvailabilityBias/Rule/players.yml → media_influenced_trader` | Tetlock (2007)          |
| social_amplification | 1.5   | Social network additional amplification factor    | `configs/AvailabilityBias/Rule/players.yml → media_influenced_trader` | Kasperson et al. (1988) |
| initial_cash         | 10000 | Starting cash reserves                            | `configs/AvailabilityBias/Rule/players.yml → media_influenced_trader` | Normalization           |
| initial_position     | 0     | Starting share position                           | `configs/AvailabilityBias/Rule/players.yml → media_influenced_trader` | Normalization           |

**4.2.4.4  Behavioral Properties**
- Time horizon: Short-to-medium term — responds to current deviation level; position held until deviation corrects
- Risk tolerance: Medium — overreacts to media signals but with appropriate direction (contrarian to deviation); less momentum-driven than RecentEventOverweighter
- Information asymmetry: None — responds to publicly broadcast deviation, but with distorted magnitude perception
- Psychological profile: Media-driven, social-signal-dependent. Treats media consensus as a signal multiplier. In LLM variants, the persona references news headlines and social chatter as primary inputs.

#### 4.2.5  Decision Process Walkthrough

Given: price = 103.0, fundamental = 100.0, deviation = +0.03, media_weight = 0.80, social_amplification = 1.50, cash = 10000

Step 1: Compute amplified_signal = 0.80 × 0.03 × 1.50 = 0.036.
Step 2: |0.036| > 0.03? YES → trade (buy, since positive media salience reinforces optimism).
Step 3: Quantity = min(300, 0.036 × 5000) = 180 shares, then cash-constrained to 97.09 shares at price 103.
Step 4: Send order: action=buy, quantity≈97.09, bid_price=103.
Result: media-driven buying amplifies a positive deviation and pushes price further above fundamental.

#### 4.2.6  Worked Numerical Example

Market state: price = 97.0, fundamental = 100.0, deviation = −0.03, media_weight = 0.80, social_amplification = 1.50, position = 200

Amplified signal: ã = 0.80 × (−0.03) × 1.50 = −0.036.
|−0.036| > 0.03 → sell (negative media salience reinforces pessimism).
Quantity: min(300, 0.036 × 5000) = 180 shares, then position-constrained to 180.
Order: action=sell, quantity=180, bid_price=97.
Rationale: The media is amplifying the negative deviation into a salient pessimistic signal. The investor overreacts by selling into an already undervalued market, creating the destabilizing media-availability channel.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                        | Notes                                                                               |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| 1 | Tetlock, P. C. (2007). "Giving content to investor sentiment." *Journal of Finance*, 62(3), 1139–1168. DOI: 10.1111/j.1540-6261.2007.01232.x                    | media_weight and social_amplification calibration; return predictability from media |
| 2 | Schwarz, N., et al. (1991). "Ease of retrieval as information." *Journal of Personality and Social Psychology*, 61(2), 195–202. DOI: 10.1037/0022-3514.61.2.195 | Ease of retrieval as signal amplifier; basis for media availability channel         |
| 3 | Kasperson, R. E., et al. (1988). "The social amplification of risk." *Risk Analysis*, 8(2), 177–187. DOI: 10.1111/j.1539-6924.1988.tb01168.x                    | social_amplification calibration; network effects in risk perception                |


---

### Investor: SystematicAnalyst

#### 4.3.1  Summary

The SystematicAnalyst is the rational benchmark — an institutional investor who processes all available information using objective, evidence-based methods without availability bias. Unlike RecentEventOverweighter (who overweights recent returns) and MediaInfluencedTrader (who overweights media-amplified signals), the SystematicAnalyst responds only to the objective fundamental deviation: the actual gap between price and intrinsic value. This investor represents the Bayesian ideal of flat-weighted information processing, where no event is given disproportionate cognitive salience. The SystematicAnalyst's behavior defines the counterfactual: what prices would look like if availability bias did not exist.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Rational Information Processing (Mullainathan)**
- Theory / Study: Bounded rationality with memory — the rational limit
- Citation: Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735–774. DOI: 10.1162/003355302760193887
- Core Insight: Mullainathan's model identifies the rational benchmark as flat-weighted processing: all past signals are weighted equally, with no primacy for recent or salient events. The SystematicAnalyst approximates this benchmark by responding only to the current deviation — the objectively most informative signal for a mean-reverting market — without availability distortion.
- Mathematical Formulation: Rational signal: s_rational(t) = δ(t) (deviation only). Sizing: Q_rational = min(Q_max, |δ(t)| × 5000). Direction: buy if δ < 0 (undervalued); sell if δ > 0 (overvalued). No recency or media weighting.
- Empirical Evidence: Institutional investors with systematic, quantitative mandates (factor-model portfolios, quant funds) approximate rational information processing. Their Sharpe ratios systematically exceed retail/discretionary investors, consistent with the rational advantage predicted by Mullainathan's model.
- Relevance to This Investor: SystematicAnalyst's `deviation` threshold of 0.03 (3%) captures the signal-to-noise threshold below which fundamental signals are indistinguishable from random fluctuations; consistent with the evidence_threshold concept in Mullainathan's model.

**Theory 2: Fundamental Analysis and Market Efficiency (Fama)**
- Theory / Study: Efficient markets and rational information processing
- Citation: Fama, E. F. (1970). "Efficient capital markets: A review of empirical work." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486. Also: Grossman, S. J., & Stiglitz, J. E. (1980). "On the impossibility of informationally efficient markets." *American Economic Review*, 70(3), 393–408.
- Core Insight: In Fama's framework, rational investors who process all available information efficiently constitute the stabilizing force in markets. Grossman & Stiglitz (1980) show that some informed agents must earn positive returns to incentivize information gathering — the SystematicAnalyst represents these informed agents who keep prices tethered to fundamentals.
- Relevance to This Investor: SystematicAnalyst's deviation-triggered contrarian trading (buy undervalued, sell overvalued) provides the mean-reversion force that limits the extent to which availability-biased agents can push prices from fundamentals. Its activity is the empirical validation test: if SystematicAnalyst's volume is sufficient to correct bias-driven mispricings, the simulation produces a near-efficient market; if insufficient, persistent mispricings emerge.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide the rational stabilizing benchmark — the force that corrects availability-biased mispricings and limits the magnitude of systematic deviation from fundamentals.

**Activation Scenarios**:
- Scenario A (Fundamental deviation < 3%): Hold. Noise-level deviations do not warrant action; consistent with the rational agent's evidence threshold.
- Scenario B (Undervaluation, deviation < −3%): Buy proportionally. Corrects downward bias from availability-driven panic selling.
- Scenario C (Overvaluation, deviation > +3%): Sell proportionally. Corrects upward bias from availability-driven momentum buying.

**Market Contribution**: Stabilizing — directly counters availability-biased overreaction by trading in the opposite direction. The balance between SystematicAnalyst's stabilizing volume and biased agents' destabilizing volume determines the equilibrium mispricing magnitude.

**Interaction with other agents**: Directly opposes RecentEventOverweighter and MediaInfluencedTrader when they push price away from fundamental; aligns with ValueTrader (both stabilizing but at different thresholds — SystematicAnalyst at 3%, ValueTrader at 5%).

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole trading signal — the objective gap between price and fundamental value. No recency weighting; no media amplification. Consistent with Mullainathan's rational benchmark of flat-weighted processing.
- `price`: For order sizing (cash / price) and submission.
- `cash`, `position`: Constraint variables.

**4.3.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If |deviation| > 0.03: trade.
3. If deviation < −0.03: buy. Quantity = min(300, |deviation| × 5000). Cash-constrained.
4. If deviation > +0.03: sell. Quantity = min(300, deviation × 5000). Position-constrained.
5. Hold if |deviation| ≤ 0.03.

**4.3.4.3  Mathematical Model**
- Trigger function: trade if |δ(t)| > 0.03
- Sizing: Q*(t) = min(300, |δ(t)| × 5000)
- Direction: buy if δ < 0; sell if δ > 0 (contrarian to deviation)
- State variables: cash, position

| Parameter          | Value | Meaning                                           | Config Path                                              | Source                       |
|--------------------|-------|---------------------------------------------------|----------------------------------------------------------|------------------------------|
| evidence_threshold | 0.03  | Minimum deviation to trigger rational trading     | `configs/AvailabilityBias/Rule/players.yml → systematic_analyst` | Mullainathan (2002)          |
| weight_decay       | 0.80  | Historical signal weight decay (reserved for multi-period variants) | `configs/AvailabilityBias/Rule/players.yml → systematic_analyst` | Bayesian updating convention |
| initial_cash       | 10000 | Starting cash                                     | `configs/AvailabilityBias/Rule/players.yml → systematic_analyst` | Normalization                |
| initial_position   | 0     | Starting position                                 | `configs/AvailabilityBias/Rule/players.yml → systematic_analyst` | Normalization                |

**4.3.4.4  Behavioral Properties**
- Time horizon: Medium-term — responds to current deviation without momentum consideration
- Risk tolerance: Medium — trades on fundamental signals but with limited position sizing; not a deep-value investor
- Information asymmetry: None — uses only publicly available deviation signal; advantage is processing quality, not information advantage
- Psychological profile: Analytical, unemotional, model-driven. In LLM variants, the persona emphasizes "I focus on the objective fundamental gap, ignoring recent noise or media coverage."

#### 4.3.5  Decision Process Walkthrough

Given: price = 103.5, fundamental = 100.0, deviation = +0.035, cash = 10000, position = 200

Step 1: deviation = +0.035. Is |0.035| > 0.03? YES → sell (price above fundamental).
Step 2: Quantity = min(300, 0.035 × 5000) = min(300, 175) = 175 shares.
Step 3: Position check: min(175, 200) = 175 → valid.
Step 4: Send order: action=sell, quantity=175, bid_price=103.5.
Result: -175 shares in D(t); systematic correction of 3.5% overvaluation. Contrast: MediaInfluencedTrader would buy into the positive media-salient deviation, showing the destabilizing direction of that bias channel.

#### 4.3.6  Worked Numerical Example

Market state: price = 96.5, fundamental = 100.0, deviation = -0.035, cash = 10000, position = 0

Trigger: |−0.035| > 0.03 → buy.
Quantity: min(300, 0.035 × 5000) = min(300, 175) = 175 shares.
Cost: 175 × 96.5 = 16887.5, so cash-constrained quantity is 103.63 shares with starting cash 10000.
Order: action=buy, quantity≈103.63, bid_price=96.5.
Rationale: 3.5% undervaluation triggers a rational proportional buy — the systematically correct response. RecentEventOverweighter at the same deviation with a recent -3% return would compute perceived_signal = 0.70 × (-0.03) + 0.30 × (-0.035) = -0.0315, producing availability-driven selling instead of rational buying if it has inventory.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                   | Notes                                                                                  |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| 1 | Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735–774. DOI: 10.1162/003355302760193887 | Rational benchmark; evidence_threshold calibration                                     |
| 2 | Fama, E. F. (1970). "Efficient capital markets: A review of empirical work." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486                    | Rational information processing benchmark; basis for contrarian deviation response     |
| 3 | Grossman, S. J., & Stiglitz, J. E. (1980). "On the impossibility of informationally efficient markets." *American Economic Review*, 70(3), 393–408.        | Role of rational agents in maintaining near-efficiency; stabilizing speculation theory |


---

### Investor: ValueTrader

#### 4.4.1  Summary

The ValueTrader is a patient, fundamental-focused investor who trades only when the price-fundamental gap is large enough to represent a clear margin of safety. Unlike the SystematicAnalyst (who responds to 3% deviations), the ValueTrader requires a 5% deviation before acting — a higher bar that ensures it is not distracted by the smallest noise-level mispricings. The ValueTrader embodies Graham's value investing discipline applied to a market distorted by cognitive bias: it waits for bias-driven overreaction to create meaningful bargains (deviation < -5%) or clear overvaluation (deviation > +5%) and then acts with fixed position sizing.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Value Investing and Margin of Safety (Graham)**
- Theory / Study: Margin of safety as the core principle of value investing
- Citation: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. Also: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.
- Core Insight: Graham's margin of safety principle requires buying at a substantial discount to intrinsic value to guard against error and uncertainty. In an availability-biased market, media-driven and recency-biased agents create transient mispricings that are not genuine fundamental changes. The ValueTrader sets deviation_threshold = 0.05 to distinguish meaningful mispricing from routine fluctuations.
- Empirical Evidence: Graham recommended a large margin of safety for common stocks; in the simulation context of a normalized single-asset market, 5% is a meaningful margin that lets value trading appear within 200 rounds without dominating every small fluctuation. Fixed order sizing (position_size = 300 shares) reflects Graham's predetermined discipline.
- Relevance to This Investor: deviation_threshold = 0.05 calibrated to activate only on meaningful availability-bias-driven mispricings; position_size = 300 is fixed and not deviation-scaled, reflecting Graham's non-speculative position sizing discipline.

**Theory 2: Long-Horizon Return Predictability and Value Premium**
- Theory / Study: Value factor — long-run return predictability from price-to-book ratios
- Citation: Fama, E. F., & French, K. R. (1992). "The cross-section of expected stock returns." *Journal of Finance*, 47(2), 427–465. DOI: 10.2307/2329112. Also: Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129–151. DOI: 10.1257/jep.21.2.129
- Core Insight: Fama & French (1992) document a persistent value premium — stocks with high book-to-market ratios (more undervalued) earn significantly higher subsequent returns. Baker & Wurgler (2007) show that this premium is highest following high-sentiment periods, consistent with availability-biased overreaction creating the mispricings that value investors subsequently profit from.
- Empirical Evidence: Fama & French (1992) document average value premium of 4–6% annually. Baker & Wurgler (2007) find that high-sentiment periods predict lower subsequent returns for growth stocks, consistent with the value investor providing the corrective force after availability-biased periods.
- Relevance to This Investor: ValueTrader embodies the mechanism behind the value premium — patient buying at deep discounts created by sentiment-/bias-driven selling, with subsequent return as mean reversion restores prices to fundamental.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Provide a patient stabilizing force — activating only when availability-biased agents have created a meaningful >=5% mispricing. ValueTrader is the price floor for undervaluation and ceiling for overvaluation in the simulation.

**Activation Scenarios**:
- Scenario A (Bias creates moderate mispricing, |deviation| < 5%): Hold. Availability bias fluctuations are insufficient to meet ValueTrader's margin of safety threshold.
- Scenario B (Undervaluation, deviation < -5%): Buy 300 shares, cash-constrained. ValueTrader's buying begins arresting the decline.
- Scenario C (Overvaluation, deviation > +5%): Sell 300 shares, position-constrained. Availability-biased momentum buying has pushed prices to a premium; ValueTrader takes profit and provides corrective selling.

**Market Contribution**: Stabilizing floor/ceiling mechanism. When active, adds up to 300 shares to buy or sell side regardless of deviation magnitude, providing a discrete stabilizing shock.

**Interaction with other agents**: Counters both RecentEventOverweighter and MediaInfluencedTrader when they collectively drive deviation beyond 5%; aligns with SystematicAnalyst (both stabilizing, different thresholds); provides a price floor/ceiling against availability-driven extremes.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Sole decision signal — the objective price-fundamental gap. Higher threshold (0.05) than SystematicAnalyst (0.03) means ValueTrader filters out smaller bias episodes.
- `cash`, `position`: Constraint variables; cash must cover position_size × price for buying.

**4.4.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < -deviation_threshold (-0.05): buy position_size = 300 shares (cash-constrained).
3. If deviation > +deviation_threshold (+0.05): sell position_size = 300 shares (position-constrained).
4. Hold if |deviation| ≤ 0.05.

**4.4.4.3  Mathematical Model**
- Trigger function: buy if δ < -m; sell if δ > +m; where m = deviation_threshold = 0.05
- Sizing: Q*(t) = min(position_size, floor(cash / price)) for buys; min(position_size, position) for sells
- Fixed size: position_size = 300 (no deviation-proportional scaling)
- State variables: cash, position

| Parameter           | Value | Meaning                                    | Config Path                                        | Source                                                     |
|---------------------|-------|--------------------------------------------|----------------------------------------------------|------------------------------------------------------------|
| deviation_threshold | 0.05  | Minimum deviation to trigger value trading | `configs/AvailabilityBias/Rule/players.yml → value_trader` | Graham (1949); calibrated to availability-bias episodes |
| position_size       | 300   | Fixed shares per value trade               | `configs/AvailabilityBias/Rule/players.yml → value_trader` | Graham (1949) fixed sizing discipline                   |
| initial_cash        | 10000 | Starting cash                              | `configs/AvailabilityBias/Rule/players.yml → value_trader` | Normalization                                           |
| initial_position    | 0     | Starting position                          | `configs/AvailabilityBias/Rule/players.yml → value_trader` | Normalization                                           |

**4.4.4.4  Behavioral Properties**
- Time horizon: Long-term — activates only at deep mispricings; patient between activations
- Risk tolerance: High — deliberately buys during periods when biased agents are selling heavily; contrarian conviction
- Information asymmetry: None — same public information as all agents; advantage is patient, unbiased processing
- Psychological profile: Patient, conviction-driven, immune to availability bias. In LLM variants, persona emphasizes: "I ignore media noise and recent price drama. I act only when the fundamental gap is undeniable."

#### 4.4.5  Decision Process Walkthrough

Given: price = 95.0, fundamental = 100.0, deviation = -0.05, deviation_threshold = 0.05, position_size = 300, cash = 10000

Step 1: deviation = -0.05. The rule activates when deviation is below -0.05; at exactly -0.05 it holds.
Step 2: If price falls to 94.0 (deviation = -0.06), buy quantity = min(300, 10000 / 94.0) = 106.38 shares.
Step 3: Send order: action=buy, quantity≈106.38, bid_price=94.
Result: stabilizing buying appears only after the gap exceeds the 5% threshold.

#### 4.4.6  Worked Numerical Example

Market state: price = 106.0, fundamental = 100.0, deviation = +0.06, position = 300

Trigger: +0.06 > +0.05 → sell.
Quantity: min(300, 300) = 300.
Order: action=sell, quantity=300, bid_price=106.
Rationale: Availability-biased agents have driven price above fundamental through recency and media overreaction. ValueTrader sells 300 shares — the fixed-size Graham discipline prevents speculative over-selling while correcting a meaningful bias-driven premium.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                 | Notes                                                                                                        |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| 1 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                        | deviation_threshold calibration; fixed position_size principle                                               |
| 2 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                         | Original margin of safety concept                                                                            |
| 3 | Fama, E. F., & French, K. R. (1992). "The cross-section of expected stock returns." *Journal of Finance*, 47(2), 427–465. DOI: 10.2307/2329112           | Value premium evidence; return predictability from deep undervaluation                                       |
| 4 | Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129–151. DOI: 10.1257/jep.21.2.129 | Sentiment-created mispricings that ValueTrader corrects; empirical basis for availability bias market impact |


---

### Investor: NoiseTrader

#### 4.5.1  Summary

The NoiseTrader is a random, uninformed participant whose trades are unconnected to any market signal — fundamental or cognitive bias. In the availability bias context, the NoiseTrader models background retail investors who trade based on personal liquidity needs, random news interpretation, or behavioral impulses unrelated to either fundamentals or the specific availability heuristic being studied. Its primary role is to ensure the simulation does not converge to a perfectly deterministic price path, enabling meaningful statistical analysis across runs.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading Theory (Black)**
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- Core Insight: Noise traders provide liquidity without which informed and systematic traders could not execute. Their stochastic behavior ensures market prices are not perfectly determined by the modeled agents, adding realistic variance. trade_probability = 0.30 (30% per round) is higher than the BlackMonday1987 simulation (5%) because availability bias episodes are subtler and require more background noise to prevent the simulation from being too mechanically predictable.
- Empirical Evidence: Black (1986) estimates noise traders account for 20–40% of daily volume. trade_probability = 0.30 consistent with a higher retail participation rate typical of behavioral-bias-driven episodes (vs. institutional-dominated crisis simulations).

**Theory 2: Retail Investor Behavior (Odean)**
- Citation: Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773–806. DOI: 10.1111/j.1540-6261.2000.tb04002.x
- Core Insight: Retail investors trade excessively and in directions uncorrelated with fundamental value, consistent with the noise trader model. Barber & Odean find retail trading volume negatively predicts subsequent returns, consistent with uninformed noise trading.
- Empirical Evidence: Average retail investor trades approximately 75% of portfolio per year — equivalent to trading probability of ~0.3% per day. In simulation rounds of longer time horizon, 30% per round is calibrated to match retail turnover.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Add stochastic variation — ensure that each simulation run produces a unique price path, enabling statistical comparison of bias effects across runs. Also models the genuine background retail order flow in availability-bias-driven markets.

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**
- No signals used — purely random. Does not observe any market data.

**4.5.4.2  Core Behavioral Mechanism**
1. Draw r ~ Uniform(0, 1). If r < 0.30: trade.
2. If trading: draw direction (buy/sell, 50/50); draw quantity ~ Uniform(100, 500).
3. Execute. Hold otherwise.

**4.5.4.3  Mathematical Model**
- Trade probability: P(trade) = 0.30 per round
- Direction: P(buy | trade) = P(sell | trade) = 0.5
- Sizing: Q ~ Uniform(100, 500)

| Parameter         | Value | Meaning                                 | Config Path                                        | Source          |
|-------------------|-------|-----------------------------------------|----------------------------------------------------|-----------------|
| trade_probability | 0.30  | Probability of trading in a given round | `configs/AvailabilityBias/Rule/players.yml → noise_trader` | Black (1986)    |
| min_order         | 100   | Minimum random trade quantity           | `configs/AvailabilityBias/Rule/players.yml → noise_trader` | Retail lot size |
| max_order         | 500   | Maximum random trade quantity           | `configs/AvailabilityBias/Rule/players.yml → noise_trader` | Retail lot size |

**4.5.4.4  Behavioral Properties**
- Time horizon: Random
- Risk tolerance: Medium (unoptimized)
- Information asymmetry: None
- Psychological profile: Random, uninformed. In LLM variants, the persona uses varied language with no systematic strategy — "I trade based on gut feeling and personal circumstances."

#### 4.5.5  Decision Process Walkthrough

Random draw r = 0.18 < 0.30 → trade. Direction: sell. Quantity: 250. Order: sell 250 at current price.

#### 4.5.6  Worked Numerical Example

r = 0.42 ≥ 0.30 → hold. No order sent this round.

r = 0.07 < 0.30 → trade. Direction: buy. Quantity: 180. Order: buy 180 at current price. Net contribution: +180 to D(t); partially offsets any bias-driven selling in the same round by coincidence.

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                | Notes                                            |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481                                                                   | Theoretical basis; trade_probability calibration |
| 2 | Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773–806. DOI: 10.1111/j.1540-6261.2000.tb04002.x | Retail overtrading; trade frequency calibration  |


## §5 Agent Diversity Verification

Diversity Check:
- Different bias channels: RecentEventOverweighter (recency/temporal availability); MediaInfluencedTrader (media/social availability); SystematicAnalyst (rational baseline); ValueTrader (deep value, high threshold); NoiseTrader (random)
- Different signals: RecentEventOverweighter uses `return_pct` + `deviation`; MediaInfluencedTrader uses `deviation` × amplification; SystematicAnalyst uses `deviation` alone; ValueTrader uses `deviation` with higher threshold; NoiseTrader uses nothing
- Conflicting incentives: Both biased agents can overreact in the same or opposite direction; SystematicAnalyst and ValueTrader counter both; genuine tension between availability amplification and systematic correction
- Different activation thresholds: NoiseTrader (30% probability); MediaInfluencedTrader (|deviation| > 2.5%); SystematicAnalyst (|deviation| > 3%); RecentEventOverweighter (|perceived_signal| > 2%); ValueTrader (|deviation| > 5%)
- Two distinct availability channels: temporal recency (RecentEventOverweighter) vs. media salience (MediaInfluencedTrader) — enables isolation of channel effects across variants


## §6 Parameter Table

| Parameter            | Value | Source Citation                                     | Description                                                    | Sensitivity                                            |
|----------------------|-------|-----------------------------------------------------|----------------------------------------------------------------|--------------------------------------------------------|
| initial_price        | 100.0 | Normalization                                       | Starting market price                                          | Low — scale only                                       |
| fundamental_value    | 100.0 | Normalization                                       | Constant intrinsic value; isolates bias from fundamental news  | Medium — sets deviation magnitude                      |
| price_impact (λ)     | 0.02  | Tetlock (2007) calibrated                           | Price response per unit net demand                             | High — controls bias-to-price-move translation         |
| mean_reversion (γ)   | 0.03  | Baker & Wurgler (2007)                              | Fundamental gravity; limits bias-driven persistent deviation   | Medium — decrease → more persistent mispricing         |
| noise_std (σ)        | 0.5   | Standard calibration                                | Background order flow noise                                    | Medium — increase → harder to distinguish bias effects |
| recency_weight       | 0.70  | Tversky & Kahneman (1973); De Bondt & Thaler (1985) | RecentEventOverweighter: recent-return weight in perceived signal | High — controls overreaction magnitude                 |
| salience_threshold   | 0.02  | Calibrated to 2% salience filter                    | RecentEventOverweighter: perceived signal activation level     | Medium — decrease → more frequent activation           |
| media_weight         | 0.80  | Tetlock (2007)                                      | MediaInfluencedTrader: media intensity multiplier              | High — controls media-driven overreaction              |
| social_amplification | 1.5   | Kasperson et al. (1988)                             | MediaInfluencedTrader: social network multiplier               | Medium — combined with media_weight = 3× total         |
| evidence_threshold   | 0.03  | Mullainathan (2002)                                 | SystematicAnalyst: minimum deviation to trigger rational trade | Medium — decrease → more corrective activity           |
| deviation_threshold  | 0.05  | Graham (1949); Baker & Wurgler (2007)               | ValueTrader: margin of safety threshold                        | Medium — increase → deeper floor/ceiling               |
| position_size        | 300   | Graham (1949) discipline                            | ValueTrader: fixed trade size                                  | Medium — increase → stronger floor/ceiling             |
| trade_probability    | 0.30  | Black (1986)                                        | NoiseTrader: per-round trade probability                       | Low — adds stochastic variation                        |


## §7 Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, prev_price, fundamental, deviation, return_pct, round}
  2. Each investor:
     a. perceive() — extract and store market data
     b. decide()   — apply strategy (rule / LLM call)
     c. act()      — send order to Market
  3. Market:
     a. perceive() — collect all orders; compute net_demand
     b. decide()   — apply price formula P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε
     c. act()      — broadcast new state
  4. Logging and state persistence
```

Key difference from other simulations: the Market broadcasts `prev_price` and `return_pct` in addition to the standard fields, because RecentEventOverweighter requires the most recent return as its primary salience signal.


## §8 Historical Case Studies

### Event 1: Post-Earnings Announcement Drift and Overreaction (Bernard & Thomas, 1989)

**Documented Pattern**: Bernard, V. L., & Thomas, J. K. (1989). "Post-earnings-announcement drift: Delayed price response or risk premium?" *Journal of Accounting Research*, 27 (Supplement), 1–36. DOI: 10.2307/2491062
**Core Dynamic**: Companies announcing large positive (negative) earnings surprises show initial price overreaction followed by drift in the original direction — consistent with availability-biased investors overweighting the recent earnings "event" as a trend signal. Post-announcement returns continue in the same direction for approximately 60 trading days, suggesting the initial overreaction is gradually corrected.
**Availability Mechanism**: Dramatic earnings announcements are cognitively salient (available) events; investors overweight their forward-looking implications through the 70% recent-return weight, creating initial overreaction.
**Agent Mapping**: RecentEventOverweighter → overreacts to the "event" of the announcement; SystematicAnalyst → corrects gradually; ValueTrader → may activate if overreaction exceeds 5%.

### Event 2: Market Impact of 9/11 and Subsequent Recovery (2001)

**Documented Pattern**: After September 11, 2001, the US stock market closed for 4 trading days and fell 14.3% on reopening. The market recovered most losses within 30 trading days — consistent with initial availability-bias-driven panic (the salient catastrophic event was overweighted as a permanent economic shock) followed by rational correction.
**Availability Mechanism**: The 9/11 attack was maximally salient (vivid, emotionally charged, heavily covered) — exactly the kind of event the availability heuristic would overweight. Media coverage was 24/7 for weeks, consistent with positive media salience and social amplification.
**Agent Mapping**: RecentEventOverweighter → panic sells on highly available catastrophic event; MediaInfluencedTrader → amplifies media coverage of crisis; ValueTrader → activates at deep undervaluation during the initial panic; SystematicAnalyst → recognizes fundamental overreaction and gradually corrects.

### Event 3: COVID-19 Market Crash and Recovery (February–April 2020)

**Documented Pattern**: The S&P 500 fell 34% from February 19 to March 23, 2020 — the fastest bear market in history. It recovered fully by August 2020. The initial crash showed characteristics of extreme availability bias: vivid, constant media coverage; dramatic daily price moves creating highly salient recent events; rapid spread of fear via social media.
**Availability Mechanism**: COVID-19 was maximally salient and media-amplified: social_amplification was extremely high (social media made every daily death toll count maximally available). The rapid recovery (5 months vs. years for typical bear markets) is consistent with the availability bias being the primary driver — once media salience declined, rational valuation reasserted.
**Agent Mapping**: MediaInfluencedTrader → extreme amplification of media coverage; RecentEventOverweighter → large negative daily returns (−5% to −10% per day) created maximally salient availability signals; ValueTrader → activated at −34% undervaluation; SystematicAnalyst → provided gradual correction during recovery.
**Lesson for Simulation**: The COVID crash demonstrates that when both availability bias channels (recency and media) are active simultaneously, the combined effect (RecentEventOverweighter + MediaInfluencedTrader both selling) can produce crash dynamics approaching those of structural crises (ArchegosCollapse, BlackMonday1987) even in the absence of fundamental damage.


## §9 Variant Comparison Preview

| Aspect            | Rule                                                  | LLM                                                   | RuleLLM                                       | Rag                                                           |
|-------------------|-------------------------------------------------------|-------------------------------------------------------|-----------------------------------------------|---------------------------------------------------------------|
| Decision Logic    | Formula-based perceived signal + amplified signal     | Persona + LLM reasoning about availability heuristic  | Formula-anchored LLM with bias quantification | RAG-augmented LLM with historical overreaction examples       |
| Determinism       | Deterministic (modulo NoiseTrader)                    | Stochastic — LLM may vary bias intensity              | Semi-deterministic                            | Stochastic — depends on retrieved context                     |
| Bias Magnitude    | Exact recency_weight/media_weight as set              | Variable — LLM may over- or under-apply bias          | Near-exact but ±20% quantity variation        | Modified by historical bias episodes in RAG context           |
| Research Question | Do these bias formulas produce measurable mispricing? | Do LLM personas replicate availability bias dynamics? | Does formula anchoring constrain LLM bias?    | Does historical overreaction evidence change biased behavior? |
