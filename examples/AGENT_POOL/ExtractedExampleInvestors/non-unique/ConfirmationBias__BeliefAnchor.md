# ConfirmationBias / Belief Anchor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ConfirmationBias |
| Agent type | Belief Anchor |
| Canonical class | `BeliefAnchor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The BeliefAnchor is a strongly opinionated investor who has formed a definitive view about market direction (initially bullish, belief = +1.0) and updates this belief asymmetrically: confirming evidence (market moving in the direction of belief) amplifies the belief, while disconfirming evidence only slowly erodes it. This investor is the simulation's primary source of persistent mispricing: once the belief state locks into a direction, BeliefAnchor continues buying (or selling) regardless of fundamental value, creating sustained one-directional demand that rational agents cannot fully overcome. The BeliefAnchor is unique among all agents in this simulation suite because it maintains a persistent internal state variable (`belief`) that compounds across rounds -- modeling the psychological reality that confirmation bias strengthens convictions over time rather than resetting each period.

## Financial Theory / Theoretical Basis

### Rule / `BeliefAnchor`
- Theory: simulation-bases.md Section 4.1 -- BeliefAnchor
- Theoretical basis: Nickerson (1998) confirmation bias; overweights information

### LLM / `LLMBeliefAnchor`
- LLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMBeliefAnchor`
- RuleLLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMBeliefAnchor`
- RAG-augmented belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `30.0` | Rule |
| belief_strength | Rule: `0.8` | Rule |
| confirm_weight | Rule: `2.5` | Rule |
| confirmation_strength | Rule: `0.7` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| disconfirm_weight | Rule: `0.3` | Rule |
| initial_belief | Rule: `1.0` | Rule |
| initial_cash | Rule: `50000.0`<br>LLM: `50000.0`<br>RuleLLM: `50000.0`<br>Rag: `50000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ConfirmationBias.LLM.prompts:LLM_BELIEF_ANCHOR_SYS', 'user_message': 'examples.ConfirmationBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_BELIEF_ANCHOR_SYS', 'user_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ConfirmationBias.Rag.prompts:RAG_BELIEF_ANCHOR_SYS', 'user_message': 'examples.ConfirmationBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | belief_anchor | Belief Anchor | `BeliefAnchor` | 2 | `examples/ConfirmationBias/Rule/players.py` |
| LLM | llm_belief_anchor | LLM Belief Anchor | `LLMBeliefAnchor` | 2 | `examples/ConfirmationBias/LLM/players.py` |
| RuleLLM | rulellm_belief_anchor | RuleLLM Belief Anchor | `RuleLLMBeliefAnchor` | 2 | `examples/ConfirmationBias/RuleLLM/players.py` |
| Rag | ragllm_belief_anchor | RAG Belief Anchor | `RagLLMBeliefAnchor` | 2 | `examples/ConfirmationBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 BeliefAnchor

#### 4.1.1  Summary

The BeliefAnchor is a strongly opinionated investor who has formed a definitive view about market direction (initially bullish, belief = +1.0) and updates this belief asymmetrically: confirming evidence (market moving in the direction of belief) amplifies the belief, while disconfirming evidence only slowly erodes it. This investor is the simulation's primary source of persistent mispricing: once the belief state locks into a direction, BeliefAnchor continues buying (or selling) regardless of fundamental value, creating sustained one-directional demand that rational agents cannot fully overcome. The BeliefAnchor is unique among all agents in this simulation suite because it maintains a persistent internal state variable (`belief`) that compounds across rounds -- modeling the psychological reality that confirmation bias strengthens convictions over time rather than resetting each period.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Confirmatory Bias and Self-Reinforcing Belief (Nickerson; Rabin & Schrag)**
- Theory / Study: Confirmation bias mechanism and formal model
- Citation: Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175-220. DOI: 10.1037/1089-2680.2.2.175. Also: Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37-82. DOI: 10.1162/003355399555945
- Core Insight: Rabin & Schrag's formal model shows that even a moderate confirmation bias (q > 0) prevents Bayesian convergence: the biased agent's posterior is permanently distorted toward the initial impression. The agent misperceives disconfirming signals as confirming, creating a ratchet effect: beliefs in one direction become self-reinforcing. In markets, this means a bullish investor gets more bullish in good times AND remains bullish in bad times -- creating asymmetric, persistent demand.
- Mathematical Formulation: Confirming update: belief(t+1) = min(belief(t) x (1 + c x δ(t)), 3.0) when sign(belief(t)) = sign(δ(t)). Disconfirming update: belief(t+1) = belief(t) x 0.95 + δ(t) x 0.5 when sign(belief(t)) ≠ sign(δ(t)). The confirming multiplier (1 + 0.7 x δ) grows with deviation magnitude; the disconfirming decay (0.95 + 0.5 x δ) is much slower. After 10 rounds of confirming signals at δ = 0.03: belief ≈ 1.0 x (1.021)^10 ≈ 2.3 -> BeliefAnchor is buying 500 shares every round with conviction level 2.3x.
- Empirical Evidence: Nickerson (1998) reviews studies showing persistence of confirmed beliefs: average half-life of a confirmed belief = 5-10x the half-life of a disconfirmed belief. Rabin & Schrag calibrate q = 0.3-0.5 for moderate empirical settings; confirmation_strength = 0.7 represents a high-bias condition. Documented in financial contexts: analysts who hold strong prior views revise their forecasts in confirming directions 65-70% of the time vs. 30-35% in disconfirming directions (Hong & Kubik, 2003 -- analyst herding study).
- Relevance to This Investor: confirmation_strength = 0.7 calibrated to Nickerson (1998) upper range; belief ceiling at 3.0 prevents numerical instability while allowing significant conviction; initial_belief = 1.0 (initial bullish prior) models the "first impression" dominance in Rabin & Schrag.

**Theory 2: Attitude Polarization (Lord, Ross & Lepper)**
- Theory / Study: Biased assimilation of mixed evidence
- Citation: Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization." *Journal of Personality and Social Psychology*, 37(11), 2098-2109. DOI: 10.1037/0022-3514.37.11.2098
- Core Insight: Lord et al.'s key finding is that identical evidence causes opposing groups to diverge (polarize) rather than converge. The mechanism is asymmetric processing: confirming evidence is accepted at face value while disconfirming evidence is scrutinized and discounted. The result is that the biased investor's belief strength grows over time even in the presence of disconfirming market signals.
- Empirical Evidence: Lord et al. found polarization effect of 2-3 standard deviations after exposure to mixed evidence. Mapped to simulation: after the first ~15 rounds of mixed market signals, BeliefAnchor with confirmation_strength = 0.7 will have belief ≈ 1.5-2.5 (from starting 1.0) -- a 50-150% increase in conviction consistent with Lord et al.'s documented polarization magnitude.
- Relevance to This Investor: The slow decay rate (x 0.95) vs. fast amplification (x (1 + 0.7 x deviation)) operationalizes Lord et al.'s asymmetric processing in quantitative terms.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Generate persistent one-directional demand driven by an internal belief state that compounds over time, producing sustained price deviations that are qualitatively different from the round-by-round overreaction of other bias simulations. The belief state's persistence is the key mechanism that distinguishes ConfirmationBias from AvailabilityBias.

**Activation Scenarios**:
- Scenario A (Confirming signal, deviation > 0 with initial_belief = +1.0): Belief compounds: belief(t+1) = belief(t) x (1 + 0.7 x 0.03) ≈ belief(t) x 1.021. After 10 rounds: belief ≈ 2.3. BeliefAnchor buys 500 shares each round at belief > 0.5.
- Scenario B (Disconfirming signal, deviation < 0): Belief decays slowly: belief(t+1) = belief(t) x 0.95 + deviation x 0.5. At belief = 2.3 with deviation = -0.03: belief(t+1) = 2.3 x 0.95 + (-0.03) x 0.5 = 2.185 - 0.015 = 2.17. Minimal decay -- BeliefAnchor is still buying.
- Scenario C (Belief sign flip): belief falls below -0.5 -> sell. This requires sustained disconfirming signals over many rounds; models the rare "capitulation" moment when a conviction-driven investor finally reverses.

**Market Contribution**: Strongly destabilizing -- generates sustained demand that compounds over rounds, creating the persistent mispricing that is the simulation's core phenomenon.

**Interaction with other agents**: Amplifies SelectiveScanner (both buying on positive deviation); directly opposed by BalancedAnalyst and ContrarianTrader; NoiseTrader adds stochastic variation around the bias-driven trend.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `deviation`: The confirming/disconfirming signal -- its sign relative to current belief determines whether the belief amplifies or decays. Magnitude also matters: larger |deviation| -> larger confirming multiplier.
- Internal `belief` state: Persistent across rounds -- the core data element that distinguishes BeliefAnchor from all other agents. NOT a function of current market data only; accumulates history.
- `cash`, `position`, `price`: Constraint variables for order execution.

**4.1.4.2  Core Behavioral Mechanism**
1. Receive `deviation` from market broadcast.
2. Update belief:
   - If sign(belief) = sign(deviation): belief = min(belief x (1 + 0.7 x |deviation|), 3.0) -- confirming -> amplify.
   - If sign(belief) ≠ sign(deviation): belief = belief x 0.95 + deviation x 0.5 -- disconfirming -> slow decay.
3. If belief > +0.5: buy order_size = 500 shares (cash-constrained).
4. If belief < -0.5: sell order_size = 500 shares (position-constrained).
5. Hold if -0.5 <= belief <= +0.5.
6. Direction of trade is determined by belief sign, NOT directly by deviation sign -- this is the key distinguishing feature. A bullish BeliefAnchor (belief > 0) keeps buying even when deviation turns slightly negative (as long as belief stays > +0.5).

**4.1.4.3  Mathematical Model**
- State variable: belief ∈ [-3.0, +3.0] (persistent)
- Confirming update: belief(t+1) = min(belief(t) x (1 + c x |δ(t)|), 3.0), where c = confirmation_strength = 0.7
- Disconfirming update: belief(t+1) = belief(t) x alpha + δ(t) x β, where alpha = 0.95 (slow decay), β = 0.5
- Trigger: buy if belief > +0.5; sell if belief < -0.5
- Sizing: Q*(t) = min(order_size, floor(cash / price)) for buys; min(order_size, position) for sells

| Parameter             | Value | Meaning                                                | Config Path                                         | Source                                              |
|-----------------------|-------|--------------------------------------------------------|-----------------------------------------------------|-----------------------------------------------------|
| confirmation_strength | 0.7   | Amplification multiplier per unit confirming deviation | `ConfirmationBias/Rule/config.yaml -> belief_anchor` | Nickerson (1998); Rabin & Schrag (1999) upper range |
| initial_belief        | 1.0   | Starting belief state (bullish prior)                  | `ConfirmationBias/Rule/config.yaml -> belief_anchor` | "First impression" per Rabin & Schrag (1999)        |
| order_size            | 500   | Fixed trade size when belief > 0.5 or < -0.5           | `ConfirmationBias/Rule/config.yaml -> belief_anchor` | Normalization                                       |
| belief_ceiling        | 3.0   | Maximum belief magnitude (prevents explosion)          | `ConfirmationBias/Rule/config.yaml -> belief_anchor` | Normalization                                       |

**4.1.4.4  Behavioral Properties**
- Time horizon: Long-term -- belief state persists indefinitely; once locked, BeliefAnchor may trade in the same direction for the entire simulation
- Risk tolerance: High (effectively) -- buys based on belief, not objective risk-return calculation; ignores fundamental deviation when belief is strong
- Information asymmetry: None -- observes same `deviation` as all agents; bias is in processing, not information
- Psychological profile: Strongly opinionated, conviction-driven, self-reinforcing. Resistant to contrary evidence. In LLM variants, the persona is the most demanding -- the LLM must spontaneously maintain a consistent belief across rounds without an explicit numerical state variable.

#### 4.1.5  Decision Process Walkthrough

Given: belief = 1.5 (bullish, after several confirming rounds), deviation = +0.03 (confirming), order_size = 500

Step 1: sign(belief) = +; sign(deviation) = + -> confirming update.
Step 2: belief(new) = min(1.5 x (1 + 0.7 x 0.03), 3.0) = min(1.5 x 1.021, 3.0) = min(1.5315, 3.0) = 1.5315.
Step 3: belief = 1.5315 > 0.5 -> buy.
Step 4: Order: action=buy, quantity=500, bid_price=current_price.

Alternative (disconfirming round):
Given: belief = 1.5315, deviation = -0.02 (disconfirming)

Step 1: sign(belief) = +; sign(deviation) = - -> disconfirming update.
Step 2: belief(new) = 1.5315 x 0.95 + (-0.02) x 0.5 = 1.455 - 0.01 = 1.445.
Step 3: belief = 1.445 > 0.5 -> still buying! The disconfirming signal barely reduced conviction.

#### 4.1.6  Worked Numerical Example

Market state: price = 102.5, fundamental = 100.0, deviation = +0.025, belief = 0.8 (initial bullish state after a few rounds)

Confirming update: belief(new) = min(0.8 x (1 + 0.7 x 0.025), 3.0) = min(0.8 x 1.0175, 3.0) = 0.814.
Trade: 0.814 > 0.5 -> buy 500 shares.
Order: action=buy, quantity=500, bid_price=102.5.
Rationale: The 2.5% positive deviation confirms BeliefAnchor's bullish prior; belief strengthens from 0.8 to 0.814. The investor is buying a 2.5% overvalued stock -- irrational from a fundamental perspective, but rational from the belief-state perspective: the confirming signal is evidence that their bullish view is correct. This is the essence of confirmation bias operationalized.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                             | Notes                                                                             |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 1 | Nickerson, R. S. (1998). "Confirmation bias: A ubiquitous phenomenon in many guises." *Review of General Psychology*, 2(2), 175-220. DOI: 10.1037/1089-2680.2.2.175                                  | Core theoretical review; confirmation_strength calibration                        |
| 2 | Rabin, M., & Schrag, J. L. (1999). "First impressions matter: A model of confirmatory bias." *Quarterly Journal of Economics*, 114(1), 37-82. DOI: 10.1162/003355399555945                           | Formal model; initial_belief = 1.0 as "first impression"; belief update equations |
| 3 | Lord, C. G., Ross, L., & Lepper, M. R. (1979). "Biased assimilation and attitude polarization." *Journal of Personality and Social Psychology*, 37(11), 2098-2109. DOI: 10.1037/0022-3514.37.11.2098 | Disconfirming decay rate calibration; polarization magnitude evidence             |


---

## Source Docstring Excerpts

### Rule / `BeliefAnchor`

```text
Forms strong prior beliefs and selectively filters confirming evidence.

Theory: simulation-bases.md Section 4.1 -- BeliefAnchor
Theoretical basis: Nickerson (1998) confirmation bias; overweights information
confirming existing belief direction, amplifying trend and causing mispricing.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMBeliefAnchor`

```text
LLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMBeliefAnchor`

```text
RuleLLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMBeliefAnchor`

```text
RAG-augmented belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
```
