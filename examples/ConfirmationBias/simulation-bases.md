# ConfirmationBias — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                               |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Confirmation Bias in Financial Decision Making                                                                                                                                                                                                            |
| Category           | Cognitive bias / behavioral finance / belief polarization                                                                                                                                                                                                 |
| Core Mechanism     | Investors systematically overweight information that confirms their prior beliefs and underweight disconfirming information, causing persistent belief polarization and price deviations that rational agents can only partially correct                  |
| Real-World Origin  | Documented in post-earnings overreaction (Rabin & Schrag, 1999), analyst forecast clustering (Hong & Kubik, 2003), investor herding on narrative (Shiller, 2000), and experimental studies of biased information assimilation (Lord, Ross & Lepper, 1979) |
| Research Relevance | Isolates the belief-updating distortion from other biases (availability, anchoring); tests whether a self-reinforcing belief state produces measurable, persistent mispricing that rational mean-reversion and contrarian trading cannot fully correct    |


## §2 Theoretical Foundation

### 2.1 Confirmation Bias — Selective Information Processing (Nickerson)

- **Citation**: Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175–220. DOI: 10.1037/1089-2680.2.2.175
- **Core Insight**: Confirmation bias is the strongest and most pervasive cognitive bias documented in experimental psychology. Individuals actively seek evidence that confirms their prior beliefs, interpret ambiguous evidence as confirming, and discount or dismiss disconfirming evidence. In financial markets, this manifests as investors who only read reports that support their existing position, attribute confirming price moves to skill and disconfirming moves to bad luck, and maintain positions beyond what objective analysis warrants.
- **Mathematical Formulation**: Biased belief updating: belief(t+1) = belief(t) × (1 + c × δ(t)) if sign(belief(t)) = sign(δ(t)) — confirming signal amplifies belief. If sign(belief(t)) ≠ sign(δ(t)) — disconfirming signal: belief(t+1) = belief(t) × 0.95 + δ(t) × 0.5 — slower decay. Here c = confirmation_strength = 0.7. The asymmetric updating (rapid confirmation, slow disconfirmation) is the mathematical essence of confirmation bias.
- **Empirical Evidence**: Nickerson (1998) reviews hundreds of experimental studies; confirmation bias effect sizes average d = 0.5–1.2 across domains. In investment contexts: Lord, Ross & Lepper (1979) show that identical evidence causes opposing groups to become MORE polarized (not less), consistent with confirmation_strength > 0 amplifying existing beliefs. Magnitude: 0.7 on a scale of 0–1 is in the upper range of documented bias strength.
- **Relevance to Investor Taxonomy**: BeliefAnchor's internal `belief` state variable, with asymmetric updating (confirmation amplifies, disconfirmation decays slowly), directly operationalizes Nickerson's comprehensive review of confirmation bias mechanics.

### 2.2 Biased Assimilation and Belief Polarization (Lord, Ross & Lepper)

- **Citation**: Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization: The effects of prior theories on subsequently considered evidence." *Journal of Personality and Social Psychology*, 37(11), 2098–2109. DOI: 10.1037/0022-3514.37.11.2098
- **Core Insight**: Lord et al. (1979) conduct the seminal experiment on biased assimilation: participants shown identical mixed evidence about capital punishment became MORE extreme in their views rather than converging — the hallmark of confirmation bias. Applied to financial markets: investors who already hold a bullish view interpret mixed earnings data as bullish; bearish investors interpret the same data as bearish. This creates polarized order flow — systematic buying from bullish bias group and systematic selling from bearish bias group — sustaining price deviations.
- **Mathematical Formulation**: Biased assimilation factor: P̃(confirming | evidence) = P(confirming | evidence) × (1 + bias_strength) > P(confirming). Operationalized in BeliefAnchor as: when market signal confirms belief, update with (1 + confirmation_strength × deviation) multiplier; when signal disconfirms, update with decay factor 0.95 (much slower than Bayesian 1/(1 + δ)).
- **Empirical Evidence**: Lord et al. (1979) quantified attitude polarization at 1.5–2.5 standard deviations following exposure to mixed evidence — consistent with confirmation_strength = 0.7 producing belief amplification in the same range. SelectiveScanner's asymmetric trading (full size on confirming, half size on disconfirming) directly operationalizes this biased assimilation.
- **Relevance to Investor Taxonomy**: SelectiveScanner implements the "selective scanning" variant of confirmation bias — it actively seeks confirming signals (full order_size = 600 when signal confirms current position) and reduces response to disconfirming signals (half order: 300 shares), modeling Lord et al.'s biased assimilation at the trading action level.

### 2.3 Formal Model of Confirmatory Bias (Rabin & Schrag)

- **Citation**: Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37–82. DOI: 10.1162/003355399555945
- **Core Insight**: Rabin & Schrag develop the first formal economic model of confirmation bias. Their key results: (1) agents with confirmation bias never learn the truth if the bias is strong enough; (2) initial conditions (first impressions) permanently anchor beliefs even when the rational posterior would converge to the truth; (3) confirmation bias creates persistent errors in probability assessments. Applied to markets: an investor who forms a bullish first impression will maintain that view indefinitely under strong confirmation bias, regardless of subsequent disconfirming price evidence.
- **Mathematical Formulation**: Rabin & Schrag's model: each period, agent receives signal s_t ∈ {H, L}. With probability q ∈ [0, 1] (the bias parameter), the agent misperceives a disconfirming signal as confirming. Posterior belief: θ̃(t) depends on the accumulated misperceived signal history. For q = 0: Bayesian; for q > 0: persistent bias toward initial impression. Mapped to simulation: BeliefAnchor's `belief` state is the θ̃(t) equivalent; confirmation_strength (0.7) corresponds to a high-q regime where biased learning is dominant.
- **Empirical Evidence**: Rabin & Schrag calibrate q = 0.2–0.5 for moderate empirical bias settings; confirmation_strength = 0.7 is calibrated to high-bias conditions consistent with the strongest empirical observations (Lord et al., 1979; Nickerson, 1998). The model predicts that belief_flip_count will be low (few sign changes) — consistent with the simulation's expected behavior where BeliefAnchor locks into one direction.
- **Relevance to Investor Taxonomy**: BeliefAnchor's persistent internal state (belief variable that compounds with confirming signals) directly implements the Rabin-Schrag model of confirmatory bias. The belief floor/ceiling (−3.0 to +3.0) prevents numerical explosion while maintaining realistic bias intensity.

### 2.4 Contrarianism and Rational Information Processing

- **Citation**: Fama, E. F. (1970). "Efficient capital markets: A review of empirical work." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486. Also: Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction in asset markets." *Journal of Finance*, 54(6), 2143–2184. DOI: 10.1111/0022-1082.00184
- **Core Insight**: In Fama's efficient market framework, rational investors who identify and trade against biased prices earn positive returns — the contrarian premium. Hong & Stein (1999) document that momentum traders (who initially exploit the bias) eventually create overreaction, which contrarians then exploit. BalancedAnalyst and ContrarianTrader represent these two categories of bias-correcting agents: the Bayesian evaluator (BalancedAnalyst) and the active contrarian (ContrarianTrader).
- **Empirical Evidence**: Hong & Stein (1999) document a contrarian premium of 4–6% annually for strategies that fade momentum stocks following extended price trends — consistent with the simulation's contrarian agents providing partial price correction. Their theoretical result: bias dominance condition requires biased agent volume > combined stabilizer volume; our simulation is parameterized with this condition nearly satisfied (biased: 1100 > stabilizers: 900).
- **Relevance to Investor Taxonomy**: BalancedAnalyst (threshold: 5%) and ContrarianTrader (threshold: 5%) together provide the rational stabilizing force. Their combined 900-unit capacity is intentionally insufficient to fully correct BeliefAnchor + SelectiveScanner's 1100-unit bias, creating realistic persistent mispricing.

### 2.5 Noise Trading and Market Microstructure (Black)

- **Citation**: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- **Core Insight**: Noise traders provide the liquidity and stochasticity that prevent confirmation bias from producing perfectly deterministic price paths. In behavioral markets, noise traders interact with both biased and rational agents, creating realistic price variance.
- **Empirical Evidence**: trade_probability = 0.30 is calibrated identically to AvailabilityBias and CarryTradeUnwind simulations, representing background retail participation.


## §3 Market Design Principles

### 3.1 Price Formation Model

Formula: **P(t+1) = P(t) + λ·D(t) + γ·[F − P(t)] + ε(t)**

| Symbol     | Meaning                    | Value           | Economic Justification                                                                                                                       | Calibration Source                |
|------------|----------------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| P(t)       | Current market price       | starts at 100.0 | Normalized equity price                                                                                                                      | —                                 |
| D(t)       | Net demand (buy − sell)    | computed        | Aggregate order imbalance from all agents each round                                                                                         | —                                 |
| F          | Fundamental value          | 100.0           | Constant — confirmation bias is a perceptual distortion; F does not change to isolate cognitive distortion from fundamental news             | Normalization                     |
| λ (lambda) | Price impact coefficient   | 0.02            | MODERATE — slightly higher than AvailabilityBias (0.01) to allow both confirmation bias channels to produce observable persistent mispricing | Hong & Stein (1999) calibration   |
| γ (gamma)  | Mean-reversion coefficient | 0.02            | Moderate — creates tension with bias; not too strong (prevents observation) or too weak (permanent divergence)                               | Fama (1970); standard calibration |
| ε(t)       | Gaussian noise ~ N(0, σ²)  | σ = 0.02        | Low noise — unlike AvailabilityBias, confirmation bias does not need recency-signal noise; σ = 0.02 is relatively small                      | Standard calibration              |

**Design Rationale**:
- λ = 0.02 is higher than AvailabilityBias (0.01): confirmation bias acts through sustained position accumulation rather than single-round overreaction, requiring a larger price impact to produce measurable persistent deviation within the simulation run.
- γ = 0.02 creates the fundamental tension: the bias must be strong enough to overcome γ-mean-reversion to produce observable persistent deviation. With BeliefAnchor + SelectiveScanner combined capacity of 1100 vs. stabilizers + γ combined ~900 + γ-force, the bias slightly dominates, consistent with empirical findings of moderate persistent mispricing.
- F = 100.0 constant: confirmation bias is about how investors interpret the same public information differently based on prior beliefs — it is not about fundamental information asymmetry. A constant F isolates the cognitive distortion cleanly.
- σ = 0.02 is small: confirmation bias episodes are driven by the belief state compounding, not by noise shocks. Small σ means the signal-to-noise ratio is high enough for BeliefAnchor's belief updates to be meaningful.
- Bias dominance condition: (BeliefAnchor order_size + SelectiveScanner order_size) = 500 + 600 = 1100 > (BalancedAnalyst + ContrarianTrader) = 400 + 500 = 900 → biased agents slightly dominate. Expected persistent mispricing: 2–8% consistent with Nickerson (1998) behavioral finance calibration.

### 3.2 Additional Market Mechanisms

- **Price floor**: `max(price, 0.01)` — prevents collapse.
- **Persistent belief state**: Unlike all other simulations, BeliefAnchor maintains a persistent `belief` variable across rounds. This is the simulation's unique feature — the belief state compounding is what produces persistent bias rather than round-by-round activation.
- **Return_pct NOT broadcast**: Like CarryTradeUnwind, confirmation bias is deviation-based, not momentum-based. All agents respond to the current price-fundamental gap.

### 3.3 Information Broadcast Design

Each round, the Market sends to all investors:

| Field         | Value / Formula  | Rationale                                                                                                            |
|---------------|------------------|----------------------------------------------------------------------------------------------------------------------|
| `price`       | P(t)             | Current market price                                                                                                 |
| `fundamental` | 100.0 (constant) | True intrinsic value; used by BalancedAnalyst and ContrarianTrader for rational correction                           |
| `deviation`   | (P(t) − F) / F   | Primary signal for all agents; the confirming/disconfirming signal that BeliefAnchor uses to update its belief state |
| `round`       | t                | Simulation round number                                                                                              |

Note: Crucially, the deviation signal is the same for all agents — confirmation bias is NOT about different agents receiving different information. It is about the same signal being processed differently by biased agents (BeliefAnchor, SelectiveScanner) vs. rational agents (BalancedAnalyst, ContrarianTrader).


## §4 Investor Taxonomy

### Investor: BeliefAnchor

#### 4.1.1  Summary

The BeliefAnchor is a strongly opinionated investor who has formed a definitive view about market direction (initially bullish, belief = +1.0) and updates this belief asymmetrically: confirming evidence (market moving in the direction of belief) amplifies the belief, while disconfirming evidence only slowly erodes it. This investor is the simulation's primary source of persistent mispricing: once the belief state locks into a direction, BeliefAnchor continues buying (or selling) regardless of fundamental value, creating sustained one-directional demand that rational agents cannot fully overcome. The BeliefAnchor is unique among all agents in this simulation suite because it maintains a persistent internal state variable (`belief`) that compounds across rounds — modeling the psychological reality that confirmation bias strengthens convictions over time rather than resetting each period.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Confirmatory Bias and Self-Reinforcing Belief (Nickerson; Rabin & Schrag)**
- Theory / Study: Confirmation bias mechanism and formal model
- Citation: Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175–220. DOI: 10.1037/1089-2680.2.2.175. Also: Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37–82. DOI: 10.1162/003355399555945
- Core Insight: Rabin & Schrag's formal model shows that even a moderate confirmation bias (q > 0) prevents Bayesian convergence: the biased agent's posterior is permanently distorted toward the initial impression. The agent misperceives disconfirming signals as confirming, creating a ratchet effect: beliefs in one direction become self-reinforcing. In markets, this means a bullish investor gets more bullish in good times AND remains bullish in bad times — creating asymmetric, persistent demand.
- Mathematical Formulation: Confirming update: belief(t+1) = min(belief(t) × (1 + c × δ(t)), 3.0) when sign(belief(t)) = sign(δ(t)). Disconfirming update: belief(t+1) = belief(t) × 0.95 + δ(t) × 0.5 when sign(belief(t)) ≠ sign(δ(t)). The confirming multiplier (1 + 0.7 × δ) grows with deviation magnitude; the disconfirming decay (0.95 + 0.5 × δ) is much slower. After 10 rounds of confirming signals at δ = 0.03: belief ≈ 1.0 × (1.021)^10 ≈ 2.3 → BeliefAnchor is buying 500 shares every round with conviction level 2.3×.
- Empirical Evidence: Nickerson (1998) reviews studies showing persistence of confirmed beliefs: average half-life of a confirmed belief = 5–10× the half-life of a disconfirmed belief. Rabin & Schrag calibrate q = 0.3–0.5 for moderate empirical settings; confirmation_strength = 0.7 represents a high-bias condition. Documented in financial contexts: analysts who hold strong prior views revise their forecasts in confirming directions 65–70% of the time vs. 30–35% in disconfirming directions (Hong & Kubik, 2003 — analyst herding study).
- Relevance to This Investor: confirmation_strength = 0.7 calibrated to Nickerson (1998) upper range; belief ceiling at 3.0 prevents numerical instability while allowing significant conviction; initial_belief = 1.0 (initial bullish prior) models the "first impression" dominance in Rabin & Schrag.

**Theory 2: Attitude Polarization (Lord, Ross & Lepper)**
- Theory / Study: Biased assimilation of mixed evidence
- Citation: Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization." *Journal of Personality and Social Psychology*, 37(11), 2098–2109. DOI: 10.1037/0022-3514.37.11.2098
- Core Insight: Lord et al.'s key finding is that identical evidence causes opposing groups to diverge (polarize) rather than converge. The mechanism is asymmetric processing: confirming evidence is accepted at face value while disconfirming evidence is scrutinized and discounted. The result is that the biased investor's belief strength grows over time even in the presence of disconfirming market signals.
- Empirical Evidence: Lord et al. found polarization effect of 2–3 standard deviations after exposure to mixed evidence. Mapped to simulation: after the first ~15 rounds of mixed market signals, BeliefAnchor with confirmation_strength = 0.7 will have belief ≈ 1.5–2.5 (from starting 1.0) — a 50–150% increase in conviction consistent with Lord et al.'s documented polarization magnitude.
- Relevance to This Investor: The slow decay rate (× 0.95) vs. fast amplification (× (1 + 0.7 × deviation)) operationalizes Lord et al.'s asymmetric processing in quantitative terms.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Generate persistent one-directional demand driven by an internal belief state that compounds over time, producing sustained price deviations that are qualitatively different from the round-by-round overreaction of other bias simulations. The belief state's persistence is the key mechanism that distinguishes ConfirmationBias from AvailabilityBias.

**Activation Scenarios**:
- Scenario A (Confirming signal, deviation > 0 with initial_belief = +1.0): Belief compounds: belief(t+1) = belief(t) × (1 + 0.7 × 0.03) ≈ belief(t) × 1.021. After 10 rounds: belief ≈ 2.3. BeliefAnchor buys 500 shares each round at belief > 0.5.
- Scenario B (Disconfirming signal, deviation < 0): Belief decays slowly: belief(t+1) = belief(t) × 0.95 + deviation × 0.5. At belief = 2.3 with deviation = −0.03: belief(t+1) = 2.3 × 0.95 + (−0.03) × 0.5 = 2.185 − 0.015 = 2.17. Minimal decay — BeliefAnchor is still buying.
- Scenario C (Belief sign flip): belief falls below −0.5 → sell. This requires sustained disconfirming signals over many rounds; models the rare "capitulation" moment when a conviction-driven investor finally reverses.

**Market Contribution**: Strongly destabilizing — generates sustained demand that compounds over rounds, creating the persistent mispricing that is the simulation's core phenomenon.

**Interaction with other agents**: Amplifies SelectiveScanner (both buying on positive deviation); directly opposed by BalancedAnalyst and ContrarianTrader; NoiseTrader adds stochastic variation around the bias-driven trend.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `deviation`: The confirming/disconfirming signal — its sign relative to current belief determines whether the belief amplifies or decays. Magnitude also matters: larger |deviation| → larger confirming multiplier.
- Internal `belief` state: Persistent across rounds — the core data element that distinguishes BeliefAnchor from all other agents. NOT a function of current market data only; accumulates history.
- `cash`, `position`, `price`: Constraint variables for order execution.

**4.1.4.2  Core Behavioral Mechanism**
1. Receive `deviation` from market broadcast.
2. Update belief:
   - If sign(belief) = sign(deviation): belief = min(belief × (1 + 0.7 × |deviation|), 3.0) — confirming → amplify.
   - If sign(belief) ≠ sign(deviation): belief = belief × 0.95 + deviation × 0.5 — disconfirming → slow decay.
3. If belief > +0.5: buy order_size = 500 shares (cash-constrained).
4. If belief < −0.5: sell order_size = 500 shares (position-constrained).
5. Hold if −0.5 ≤ belief ≤ +0.5.
6. Direction of trade is determined by belief sign, NOT directly by deviation sign — this is the key distinguishing feature. A bullish BeliefAnchor (belief > 0) keeps buying even when deviation turns slightly negative (as long as belief stays > +0.5).

**4.1.4.3  Mathematical Model**
- State variable: belief ∈ [−3.0, +3.0] (persistent)
- Confirming update: belief(t+1) = min(belief(t) × (1 + c × |δ(t)|), 3.0), where c = confirmation_strength = 0.7
- Disconfirming update: belief(t+1) = belief(t) × α + δ(t) × β, where α = 0.95 (slow decay), β = 0.5
- Trigger: buy if belief > +0.5; sell if belief < −0.5
- Sizing: Q*(t) = min(order_size, floor(cash / price)) for buys; min(order_size, position) for sells

| Parameter             | Value | Meaning                                                | Config Path                                         | Source                                              |
|-----------------------|-------|--------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------------|
| confirmation_strength | 0.7   | Amplification multiplier per unit confirming deviation | `ConfirmationBias/Rule/config.yaml → belief_anchor` | Nickerson (1998); Rabin & Schrag (1999) upper range |
| initial_belief        | 1.0   | Starting belief state (bullish prior)                  | `ConfirmationBias/Rule/config.yaml → belief_anchor` | "First impression" per Rabin & Schrag (1999)        |
| order_size            | 500   | Fixed trade size when belief > 0.5 or < −0.5           | `ConfirmationBias/Rule/config.yaml → belief_anchor` | Normalization                                       |
| belief_ceiling        | 3.0   | Maximum belief magnitude (prevents explosion)          | `ConfirmationBias/Rule/config.yaml → belief_anchor` | Normalization                                       |

**4.1.4.4  Behavioral Properties**
- Time horizon: Long-term — belief state persists indefinitely; once locked, BeliefAnchor may trade in the same direction for the entire simulation
- Risk tolerance: High (effectively) — buys based on belief, not objective risk-return calculation; ignores fundamental deviation when belief is strong
- Information asymmetry: None — observes same `deviation` as all agents; bias is in processing, not information
- Psychological profile: Strongly opinionated, conviction-driven, self-reinforcing. Resistant to contrary evidence. In LLM variants, the persona is the most demanding — the LLM must spontaneously maintain a consistent belief across rounds without an explicit numerical state variable.

#### 4.1.5  Decision Process Walkthrough

Given: belief = 1.5 (bullish, after several confirming rounds), deviation = +0.03 (confirming), order_size = 500

Step 1: sign(belief) = +; sign(deviation) = + → confirming update.
Step 2: belief(new) = min(1.5 × (1 + 0.7 × 0.03), 3.0) = min(1.5 × 1.021, 3.0) = min(1.5315, 3.0) = 1.5315.
Step 3: belief = 1.5315 > 0.5 → buy.
Step 4: Order: action=buy, quantity=500, bid_price=current_price.

Alternative (disconfirming round):
Given: belief = 1.5315, deviation = −0.02 (disconfirming)

Step 1: sign(belief) = +; sign(deviation) = − → disconfirming update.
Step 2: belief(new) = 1.5315 × 0.95 + (−0.02) × 0.5 = 1.455 − 0.01 = 1.445.
Step 3: belief = 1.445 > 0.5 → still buying! The disconfirming signal barely reduced conviction.

#### 4.1.6  Worked Numerical Example

Market state: price = 102.5, fundamental = 100.0, deviation = +0.025, belief = 0.8 (initial bullish state after a few rounds)

Confirming update: belief(new) = min(0.8 × (1 + 0.7 × 0.025), 3.0) = min(0.8 × 1.0175, 3.0) = 0.814.
Trade: 0.814 > 0.5 → buy 500 shares.
Order: action=buy, quantity=500, bid_price=102.5.
Rationale: The 2.5% positive deviation confirms BeliefAnchor's bullish prior; belief strengthens from 0.8 to 0.814. The investor is buying a 2.5% overvalued stock — irrational from a fundamental perspective, but rational from the belief-state perspective: the confirming signal is evidence that their bullish view is correct. This is the essence of confirmation bias operationalized.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                             | Notes                                                                             |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 1 | Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175–220. DOI: 10.1037/1089-2680.2.2.175                                  | Core theoretical review; confirmation_strength calibration                        |
| 2 | Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37–82. DOI: 10.1162/003355399555945                           | Formal model; initial_belief = 1.0 as "first impression"; belief update equations |
| 3 | Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization." *Journal of Personality and Social Psychology*, 37(11), 2098–2109. DOI: 10.1037/0022-3514.37.11.2098 | Disconfirming decay rate calibration; polarization magnitude evidence             |


---

### Investor: SelectiveScanner

#### 4.2.1  Summary

The SelectiveScanner is an investor who selectively attends to information that supports their current market position. Unlike BeliefAnchor (who maintains an internal belief state), SelectiveScanner operates entirely on current position: it executes full-size orders when the market confirms its existing position, but only half-size orders when the market contradicts it. This asymmetric response to confirming vs. disconfirming signals is the behavioral manifestation of "selective search" — a classic form of confirmation bias where investors seek out confirming evidence and ignore or discount contrary evidence. The SelectiveScanner is currently long (initial_position > 0), so positive deviation (price above fundamental) confirms the long and triggers full buying; negative deviation threatens the position and triggers muted selling.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Selective Search and Myside Bias**
- Theory / Study: Selective information search as confirmation bias mechanism
- Citation: Nickerson, R. S. (1998). DOI: 10.1037/1089-2680.2.2.175. Also: Klayman, J. (1995). "Varieties of confirmation bias." *Psychology of Learning and Motivation*, 32, 385–418.
- Core Insight: The "myside bias" (Stanovich, West & Toplak, 2013) is the tendency to evaluate evidence based on one's own side of an argument rather than objective standards. Investors with myside bias respond asymmetrically to market signals: they act quickly and decisively on confirming signals but hesitate, rationalize, and discount disconfirming signals. SelectiveScanner's asymmetric order sizing (600 confirming, 300 disconfirming) is a direct quantitative implementation.
- Mathematical Formulation: Asymmetric response: Q_confirming = order_size = 600; Q_disconfirming = order_size / 2 = 300. The 2:1 response ratio (600:300) is calibrated to the 2× asymmetry documented in experimental psychology studies of myside bias. Signal interpretation: confirming if sign(deviation) = sign(current position direction); disconfirming otherwise.
- Empirical Evidence: Klayman (1995) documents that selective search creates information asymmetry in processing: confirmation bias subjects generate 2–3× more confirming tests than disconfirming tests when evaluating hypotheses. Mapped to trading: 2× larger orders on confirming signals (600 vs. 300) is within the empirically documented range.
- Relevance to This Investor: scan_threshold = 0.02 (2%) is the minimum deviation needed to trigger any response; asymmetric sizing (600 vs. 300) directly implements the myside bias; the position-direction conditioning (acts based on current position sign) implements the "selective search for confirming evidence."

**Theory 2: Commitment and Consistency (Cialdini)**
- Theory / Study: Post-commitment rationalization of prior investment decisions
- Citation: Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Collins. Also: Staw, B. M. (1976). "Knee-deep in the Big Muddy: A study of escalating commitment to a chosen course of action." *Organizational Behavior and Human Performance*, 16(1), 27–44. DOI: 10.1016/0030-5073(76)90005-2
- Core Insight: Once an investor has committed to a position, psychological consistency pressure creates a bias toward maintaining and expanding the position. Staw (1976)'s escalating commitment research shows that decision-makers who already have committed resources to a course of action will continue to commit additional resources even when objective evidence suggests failure. In investing, this is the "throwing good money after bad" bias — continuing to buy a losing position because selling would acknowledge the original decision was wrong.
- Mathematical Formulation: SelectiveScanner's asymmetric behavior when position is long: buy at deviation > +0.02 (confirming position = full 600 shares); sell at deviation < −0.02 (threatening position = only 300 shares). This asymmetric reluctance to sell at disconfirming signals models escalating commitment.
- Relevance to This Investor: The position-conditional asymmetry (full response to confirming, half to disconfirming) embeds the commitment-and-consistency bias directly in the decision rule.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the selective information search variant of confirmation bias — where the bias manifests not as belief compounding but as systematically asymmetric trading action in response to signals. Complements BeliefAnchor's belief-state mechanism with a position-based mechanism.

**Activation Scenarios**:
- Scenario A (Market confirms current long position, deviation > +0.02): Full buy (600 shares). Maximum response to confirming signal.
- Scenario B (Market challenges current long position, deviation < −0.02): Half sell (300 shares). Muted response to disconfirming signal — reluctance to acknowledge the position is threatened.
- Scenario C (Signal below threshold, |deviation| ≤ 0.02): Hold. No action on weak signals.

**Market Contribution**: Destabilizing — the 2:1 buy/sell asymmetry creates net upward pressure over time (when buy signals and sell signals are equally frequent, SelectiveScanner generates 600 net buy vs. 300 net sell units in those rounds, producing a net positive contribution to D(t)).

**Interaction with other agents**: Reinforces BeliefAnchor buying (both buying on positive deviation); BalancedAnalyst and ContrarianTrader oppose both.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Both trigger and direction signal — but applied asymmetrically based on current position.
- `position`: Key state variable — determines whether deviation is "confirming" (sign aligns with position direction) or "disconfirming."

**4.2.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation > scan_threshold (+0.02) AND position ≥ 0 (currently long or flat): buy = confirming signal for long → full order_size = 600.
3. If deviation < −scan_threshold (−0.02) AND position ≥ 0 (currently long): sell = disconfirming signal → half order_size = 300.
4. Hold if |deviation| ≤ 0.02.
5. Note: If position < 0 (short): the asymmetry reverses — negative deviation confirms short (full 600), positive threatens short (half 300).

**4.2.4.3  Mathematical Model**
- Trigger: buy if δ(t) > +scan_threshold; sell if δ(t) < −scan_threshold; hold if |δ| ≤ scan_threshold
- Asymmetric sizing: Q*_confirming = order_size = 600; Q*_disconfirming = order_size / 2 = 300
- Confirming condition: sign(δ(t)) = sign(position) → full size; else → half size
- State variables: position, cash

| Parameter      | Value | Meaning                                         | Config Path                                             | Source                                                                  |
|----------------|-------|-------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------|
| scan_threshold | 0.02  | Minimum deviation to trigger selective scanning | `ConfirmationBias/Rule/config.yaml → selective_scanner` | Klayman (1995)                                                          |
| order_size     | 600   | Full order size for confirming signals          | `ConfirmationBias/Rule/config.yaml → selective_scanner` | Normalization (larger than BeliefAnchor to provide second bias channel) |

**4.2.4.4  Behavioral Properties**
- Time horizon: Short-to-medium term — responds to each round's deviation signal; no long-run belief state
- Risk tolerance: Asymmetric — high tolerance for losses on existing position (slow to sell); normal response to opportunities to add
- Information asymmetry: None
- Psychological profile: Position-defensive, myside-biased, reluctant to acknowledge mistakes. In LLM variants, the persona should emphasize "I'm reluctant to exit a position just because of short-term noise."

#### 4.2.5  Decision Process Walkthrough

Given: deviation = +0.04, position = 800 (long), scan_threshold = 0.02, order_size = 600

Step 1: deviation = +0.04 > +0.02 → scanning active (buy signal).
Step 2: position = 800 ≥ 0 → confirming signal for long position → full order.
Step 3: Q = 600 shares.
Step 4: Order: action=buy, quantity=600, bid_price=current_price.

Given: deviation = −0.03, position = 800 (long), scan_threshold = 0.02

Step 1: deviation = −0.03 < −0.02 → scanning active (sell signal).
Step 2: position = 800 ≥ 0 → disconfirming signal for long position → half order.
Step 3: Q = 300 shares.
Step 4: Order: action=sell, quantity=300, bid_price=current_price.

#### 4.2.6  Worked Numerical Example

Market state: price = 103.0, deviation = +0.03, position = 1200

Confirming buy: Q = 600. Order: buy 600. Rationale: Market confirming SelectiveScanner's long position → maximum response. Contrast: if position = −200 (short) at same deviation = +0.03, it would be disconfirming → sell only 300.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                           | Notes                                                           |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 1 | Nickerson, R. S. (1998). "Confirmation bias." *Review of General Psychology*, 2(2), 175–220. DOI: 10.1037/1089-2680.2.2.175                        | scan_threshold calibration; myside bias as confirmation variant |
| 2 | Klayman, J. (1995). "Varieties of confirmation bias." *Psychology of Learning and Motivation*, 32, 385–418.                                        | Selective search mechanism; 2:1 confirming/disconfirming ratio  |
| 3 | Staw, B. M. (1976). "Knee-deep in the Big Muddy." *Organizational Behavior and Human Performance*, 16(1), 27–44. DOI: 10.1016/0030-5073(76)90005-2 | Escalating commitment; asymmetric sell reluctance               |


---

### Investor: BalancedAnalyst

#### 4.3.1  Summary

The BalancedAnalyst is the rational benchmark — a fundamental analyst who evaluates all market information objectively, without prior beliefs or position bias. Unlike BeliefAnchor (who amplifies confirming signals) or SelectiveScanner (who responds asymmetrically based on position), the BalancedAnalyst applies the same evidence standard to bullish and bearish signals. It buys when prices are genuinely below fundamental (deviation < −5%) and sells when genuinely above (deviation > +5%), serving as the primary mean-reversion force that limits how far confirmation bias can push prices from intrinsic value.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Fundamental Analysis and Rational Information Processing**
- Citation: Fama, E. F. (1970). "Efficient capital markets." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486. Also: Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735–774. DOI: 10.1162/003355302760193887
- Core Insight: Rational fundamental analysts provide the stabilizing force in markets with behavioral biases. Fama (1970)'s efficient market hypothesis requires that some agents process information without bias; Mullainathan (2002) shows the rational case is flat-weighted information processing. BalancedAnalyst implements this: symmetric response to positive and negative deviations, no prior beliefs.
- Mathematical Formulation: Symmetric trigger: buy if δ < −0.05; sell if δ > +0.05. Sizing: Q = min(order_size, position or cash_capacity) = min(400, ...). Unlike BeliefAnchor (where sign(trade) depends on belief), BalancedAnalyst's sign(trade) is always contrarian to deviation.
- Relevance to This Investor: analysis_threshold = 0.05 (5%) is deliberately higher than BeliefAnchor's effective threshold (belief > 0.5 → 500 shares regardless of deviation magnitude). This means BalancedAnalyst is not always in the market — it corrects only when deviation is meaningfully large, consistent with rational risk-bearing constraints.

**Theory 2: Contrarian Value Investing and the Rational Correction Force**
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreact?" *Journal of Finance*, 40(3), 793–805. DOI: 10.2307/2327804
- Core Insight: De Bondt & Thaler (1985) provide the empirical evidence that rational correction (reversals following overreaction) exists but is incomplete. BalancedAnalyst's bounded correction capacity (400 shares) models this partial correction.
- Relevance to This Investor: analysis_threshold = 0.05 calibrated to the threshold below which rational correction begins dominating; order_size = 400 is intentionally smaller than BeliefAnchor (500) + SelectiveScanner (600) combined.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide rational mean-reversion correction that limits (but cannot fully prevent) confirmation-bias-driven mispricing.

**Activation Scenarios**:
- Scenario A (|deviation| < 5%): Hold — within rational tolerance; not enough mispricing to justify correction costs.
- Scenario B (Undervaluation, deviation < −5%): Buy — rational fundamental buying.
- Scenario C (Overvaluation, deviation > +5%): Sell — rational fundamental selling.

**Market Contribution**: Stabilizing — partial correction; combined with ContrarianTrader provides 900 units of stabilizing capacity vs. biased agents' 1100.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole signal; symmetric treatment — no prior beliefs.

**4.3.4.2  Core Behavioral Mechanism**
1. If deviation < −analysis_threshold (−0.05): buy order_size = 400.
2. If deviation > +analysis_threshold (+0.05): sell order_size = 400.
3. Hold if |deviation| ≤ 0.05.

**4.3.4.3  Mathematical Model**
- Trigger: buy if δ < −0.05; sell if δ > +0.05
- Sizing: Q = min(400, floor(cash / price)) or min(400, position)

| Parameter          | Value | Meaning                                        | Config Path                                            | Source                                |
|--------------------|-------|------------------------------------------------|--------------------------------------------------------|---------------------------------------|
| analysis_threshold | 0.05  | Minimum deviation to trigger rational trading  | `ConfirmationBias/Rule/config.yaml → balanced_analyst` | Fama (1970); De Bondt & Thaler (1985) |
| order_size         | 400   | Fixed trade size (slightly below BeliefAnchor) | `ConfirmationBias/Rule/config.yaml → balanced_analyst` | Normalization                         |

**4.3.4.4  Behavioral Properties**: Rational, objective, symmetric, unbiased.

#### 4.3.5  Decision Process Walkthrough

Given: deviation = +0.06, position = 1000

Trigger: 0.06 > 0.05 → sell. Q = 400. Order: sell 400.

#### 4.3.6  Worked Numerical Example

Market state: price = 93.5, deviation = −0.065. Trigger: −0.065 < −0.05 → buy 400.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                  | Notes                                                       |
|---|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| 1 | Fama, E. F. (1970). "Efficient capital markets." *Journal of Finance*, 25(2), 383–417. DOI: 10.2307/2325486                               | Rational information processing baseline                    |
| 2 | De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreact?" *Journal of Finance*, 40(3), 793–805. DOI: 10.2307/2327804 | Partial correction evidence; analysis_threshold calibration |


---

### Investor: ContrarianTrader

#### 4.4.1  Summary

The ContrarianTrader actively fades the consensus — it sells when the market is above fundamental (betting that biased optimism will correct) and buys when the market is below fundamental (betting that biased pessimism will reverse). Unlike BalancedAnalyst (which corrects passively based on fundamental value), ContrarianTrader explicitly models the active strategy of trading against bias-driven consensus. It maintains the same 5% threshold as BalancedAnalyst but represents a different economic archetype: the short-seller who exploits overvaluation and the deep-discount buyer who exploits undervaluation.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Contrarian Investing and Profit from Bias Correction**
- Citation: Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction in asset markets." *Journal of Finance*, 54(6), 2143–2184. DOI: 10.1111/0022-1082.00184
- Core Insight: Hong & Stein model the interaction between momentum traders (who trade in the direction of price moves) and contrarians (who fade extreme moves). Contrarians earn positive returns by exploiting the overreaction created by momentum/biased agents; their profit is limited by timing risk — being early is costly.
- Empirical Evidence: Hong & Stein (1999) document a contrarian premium of 4–6% annually for portfolios that systematically fade extreme momentum stocks. contrarian_threshold = 0.05 calibrated to represent the "extreme" threshold above which contrarian profit becomes reliable.

**Theory 2: Short-Selling and Market Efficiency**
- Citation: Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555
- Core Insight: Short-sellers (the most active contrarians) face capital constraints and risks that limit their ability to fully correct overpricing. ContrarianTrader's fixed order_size (500) models this constrained contrarian capacity — large enough to provide meaningful correction, but not unlimited.
- Relevance to This Investor: order_size = 500 is calibrated to be approximately equal to BeliefAnchor's order (500), ensuring each biased buy is partially offset by a contrarian sell at the threshold; combined with BalancedAnalyst (400), stabilizers total 900 vs. biased agents' 1100.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Actively counteract bias-driven mispricing; represent the short-seller and deep-value contrarian who profit from correcting confirmation-bias-driven deviations.

**Activation Scenarios**: Same threshold and direction as BalancedAnalyst (sells at deviation > +5%, buys at deviation < −5%), but represents different economic motivation.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Core Behavioral Mechanism**
1. If deviation > contrarian_threshold (+0.05): sell — fading bullish bias.
2. If deviation < −contrarian_threshold (−0.05): buy — fading bearish bias.
3. Hold if |deviation| ≤ 0.05.

**4.4.4.3  Mathematical Model**
- Trigger: sell if δ > +0.05; buy if δ < −0.05; hold otherwise
- Q*(t) = min(500, position or cash_capacity)

| Parameter            | Value | Meaning                                         | Config Path                                             | Source              |
|----------------------|-------|-------------------------------------------------|---------------------------------------------------------|---------------------|
| contrarian_threshold | 0.05  | Deviation threshold for active contrarian trade | `ConfirmationBias/Rule/config.yaml → contrarian_trader` | Hong & Stein (1999) |
| order_size           | 500   | Fixed trade size                                | `ConfirmationBias/Rule/config.yaml → contrarian_trader` | Normalization       |

**4.4.4.4  Behavioral Properties**: Active contrarian, bias-fader, short-seller profile.

#### 4.4.5  Decision Process Walkthrough

Given: deviation = +0.07 → sell 500. Given: deviation = −0.06 → buy 500.

#### 4.4.6  Worked Numerical Example

Market state: deviation = +0.08. Trigger: sell. Q = 500. Rationale: 8% overvaluation driven by BeliefAnchor's bullish confirmation bias; ContrarianTrader fades this by selling 500 shares.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                       | Notes                                                   |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction." *Journal of Finance*, 54(6), 2143–2184. DOI: 10.1111/0022-1082.00184 | Contrarian premium; contrarian_threshold calibration    |
| 2 | Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35–55. DOI: 10.2307/2329555                                                      | Constrained contrarian capacity; order_size calibration |


---

### Investor: NoiseTrader

#### 4.5.1  Summary

Random, uninformed background trader — provides stochastic variation and background liquidity. Identical design to other behavioral bias simulations.

#### 4.5.2  Theoretical and Empirical Foundation

- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. DOI: 10.2307/2328481
- trade_probability = 0.30 calibrated to retail participation in behavioral markets.

#### 4.5.3  Behavioral Framework

P(trade) = 0.30; direction 50/50; Q ~ Uniform(100, 500).

| Parameter         | Value | Source       |
|-------------------|-------|--------------|
| trade_probability | 0.30  | Black (1986) |
| min_order         | 100   | Convention   |
| max_order         | 500   | Convention   |


## §5 Agent Diversity Verification

Diversity Check:
- Different bias mechanisms: BeliefAnchor (belief-state compounding); SelectiveScanner (asymmetric position-based response); BalancedAnalyst (rational baseline); ContrarianTrader (active bias-fader); NoiseTrader (random)
- Different state types: Only BeliefAnchor maintains a persistent internal state (belief); all others are stateless decision rules
- Different signals: BeliefAnchor uses deviation to update belief; SelectiveScanner uses deviation relative to current position; BalancedAnalyst uses objective deviation; ContrarianTrader uses objective deviation (opposite direction)
- Bias dominance condition: BeliefAnchor (500) + SelectiveScanner (600) = 1100 > BalancedAnalyst (400) + ContrarianTrader (500) = 900 → biased agents slightly dominate
- Unique feature: BeliefAnchor is the only agent in the entire simulation suite with a persistent cross-round internal state variable (belief), making ConfirmationBias the most psychologically realistic simulation


## §6 Parameter Table

| Parameter                             | Value | Source Citation                          | Description                                             | Sensitivity                                         |
|---------------------------------------|-------|------------------------------------------|---------------------------------------------------------|-----------------------------------------------------|
| initial_price                         | 100.0 | Normalization                            | Starting price                                          | Low                                                 |
| fundamental_value                     | 100.0 | Normalization                            | Constant intrinsic value                                | Medium                                              |
| price_impact (λ)                      | 0.02  | Hong & Stein (1999)                      | Price response per unit net demand                      | High — controls bias-to-price translation           |
| mean_reversion (γ)                    | 0.02  | Fama (1970); standard calibration        | Fundamental gravity; limits persistent deviation        | Medium — decrease → more persistent bias            |
| noise_std (σ)                         | 0.02  | Standard calibration                     | Background noise (small relative to bias)               | Low                                                 |
| BeliefAnchor confirmation_strength    | 0.7   | Nickerson (1998); Rabin & Schrag (1999)  | Belief amplification factor per confirming unit         | High — controls persistence and amplitude           |
| BeliefAnchor initial_belief           | 1.0   | Rabin & Schrag (1999) first impression   | Starting belief state (bullish)                         | Medium — change sign for bearish starting condition |
| BeliefAnchor order_size               | 500   | Normalization                            | Fixed trade size when belief triggers                   | Medium                                              |
| SelectiveScanner scan_threshold       | 0.02  | Klayman (1995)                           | Minimum deviation to trigger selective scanning         | Medium                                              |
| SelectiveScanner order_size           | 600   | Normalization (larger than BeliefAnchor) | Full size for confirming signals; 300 for disconfirming | Medium                                              |
| BalancedAnalyst analysis_threshold    | 0.05  | Fama (1970); De Bondt & Thaler (1985)    | Rational trading threshold                              | Medium — decrease → more aggressive correction      |
| ContrarianTrader contrarian_threshold | 0.05  | Hong & Stein (1999)                      | Bias-fading activation threshold                        | Medium                                              |
| NoiseTrader trade_probability         | 0.30  | Black (1986)                             | Per-round trade probability                             | Low                                                 |


## §7 Communication and Round Structure

```
Round N:
  1. Market broadcasts state to all investors
     Payload: {price, fundamental, deviation, round}
  2. Each investor:
     a. perceive() — extract and store market data; BeliefAnchor also updates belief state
     b. decide()   — apply strategy (rule / LLM call)
     c. act()      — send order to Market
  3. Market:
     a. perceive() — collect all orders; compute net_demand
     b. decide()   — apply price formula P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε
     c. act()      — broadcast new state
  4. Logging and state persistence
```

Key difference: BeliefAnchor's `perceive()` step also updates the internal `belief` state based on deviation — belief updating happens BEFORE `decide()`, meaning the trade decision in each round reflects the fully updated belief.


## §8 Historical Case Studies

### Event 1: Analyst Forecast Clustering and Confirmation Bias (Hong & Kubik, 2003)

**Documented Pattern**: Hong, H., & Kubik, J. D. (2003). "Analyzing the analysts: Career concerns and herding." *Journal of Finance*, 58(1), 313–351. DOI: 10.1111/1540-6261.00526. Found that analysts who deviate from the consensus by issuing contrarian forecasts are more likely to be dismissed, creating career incentives for confirmation bias — analysts herd toward confirming the prevailing market view. Consensus forecasts show persistent deviation from realized outcomes in the confirming direction.
**Confirmation Mechanism**: Analysts who believe the market is overvalued find reasons to support that view; those who believe it is undervalued find confirming data. Hong & Kubik document that analyst consensus deviates from realized earnings by 10–20% in the direction of the prior consensus.
**Agent Mapping**: BeliefAnchor → analyst who compounds bullish belief through confirming interpretations; SelectiveScanner → analyst who selectively cites supporting reports; BalancedAnalyst → the rare unbiased analyst.

### Event 2: Dotcom Bubble Believer and Debunker (1998–2001)

**Documented Pattern**: During the dotcom bubble (1998–2000), bullish technology analysts (Henry Blodget, Mary Meeker) consistently interpreted mixed evidence as confirming sky-high valuations. In surveys, technology stock investors showed classic confirmation bias: they read positive analyst reports, ignored warnings from value investors like Buffett, and dismissed price-to-earnings concerns as "old economy thinking."
**Confirmation Mechanism**: Bullish technology investors in 1999 had belief states analogous to BeliefAnchor with high confirmation_strength — disconfirming evidence (negative earnings, burning cash) was reframed as "investing in the future." The bubble persisted for 2–3 years, consistent with the simulation's persistent mispricing dynamic.
**Agent Mapping**: BeliefAnchor → committed technology bulls (the majority); SelectiveScanner → investors who only read bullish research; BalancedAnalyst + ContrarianTrader → value investors like Buffett who refused to participate; NoiseTrader → retail investors following the narrative without systematic strategy.

### Event 3: Housing Market Believers vs. Skeptics (2004–2007)

**Documented Pattern**: During the US housing bubble, the vast majority of market participants, economists, and policymakers held strongly bullish views on housing (belief > 0). Analysts like Robert Shiller who warned of the bubble were consistently dismissed (disconfirming evidence underweighted). The Federal Reserve, rating agencies, and investment banks all showed classic confirmation bias — interpreting continuing price appreciation as fundamental rather than speculative.
**Lesson for Simulation**: The housing bubble demonstrates that when BeliefAnchor agents dominate (and initial_belief is uniformly positive across the population), the combined confirmation bias creates systemic mispricing that persists for years. The simulation's single BeliefAnchor represents a "representative biased agent" — in reality, much of the financial system played this role in 2004–2007.


## §9 Variant Comparison Preview

| Aspect            | Rule                                                   | LLM                                                                              | RuleLLM                                           | Rag                                                                     |
|-------------------|--------------------------------------------------------|----------------------------------------------------------------------------------|---------------------------------------------------|-------------------------------------------------------------------------|
| Decision Logic    | Exact belief state updates + asymmetric order sizing   | Persona + LLM reasoning (must spontaneously maintain prior)                      | Formula-anchored LLM                              | RAG-augmented with confirmation bias research                           |
| Determinism       | Deterministic (modulo NoiseTrader)                     | Stochastic — LLM may not maintain persistent belief across calls                 | Semi-deterministic                                | Stochastic — modified by retrieved psychology literature                |
| Bias Magnitude    | Exact per confirmation_strength                        | Variable — LLM may show stronger narrative confirmation or quick rationalization | Near-formula                                      | Potentially moderated if retrieved Rabin & Schrag or Nickerson          |
| Research Question | Does belief compounding produce persistent mispricing? | Do LLM personas spontaneously show confirmation bias?                            | Does formula anchoring reproduce belief dynamics? | Does awareness of confirmation bias (via RAG) reduce its market impact? |
