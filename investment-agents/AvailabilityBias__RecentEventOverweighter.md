# AvailabilityBias / Recent Event Overweighter

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AvailabilityBias |
| Agent type | Recent Event Overweighter |
| Canonical class | `RecentEventOverweighter` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The RecentEventOverweighter is a retail or semi-institutional investor who gives disproportionate weight to the most recent market event in forming their outlook. When the market has just moved sharply (large `return_pct`), this investor perceives the current moment as abnormally significant -- a directionally important signal -- and trades accordingly, regardless of whether the recent move reflects any genuine change in fundamental value. This investor embodies the availability heuristic in its purest market form: the "available" event (the salient recent return) dominates the objective signal (fundamental deviation). In equilibrium, this creates systematic overreaction to recent price moves and underreaction to slow-developing fundamental trends.

## Financial Theory / Theoretical Basis

### Rule / `RecentEventOverweighter`
- Theory: simulation-bases.md Section 4.1 -- RecentEventOverweighter
- Theoretical basis: Tversky & Kahneman (1973) -- Availability heuristic recency channel.

### LLM / `LLMRecentEventOverweighter`
- LLM-driven trader who overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMRecentEventOverweighter`
- RuleLLM -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMRecentEventOverweighter`
- RAG-augmented -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AvailabilityBias.LLM.prompts:LLM_RECENT_EVENT_OVERWEIGHTER_SYS', 'user_message': 'examples.AvailabilityBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_RECENT_EVENT_OVERWEIGHTER_SYS', 'user_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AvailabilityBias.Rag.prompts:RAG_RECENT_EVENT_OVERWEIGHTER_SYS', 'user_message': 'examples.AvailabilityBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `300.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000.0` | Rule |
| recency_weight | Rule: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | Rag, Rule, RuleLLM |
| salience_threshold | Rule: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | recent_event_overweighter | Recent Event Overweighter | `RecentEventOverweighter` | 2 | `examples/AvailabilityBias/Rule/players.py` |
| LLM | llm_recent_event_overweighter | LLM Recent Event Overweighter | `LLMRecentEventOverweighter` | 2 | `examples/AvailabilityBias/LLM/players.py` |
| RuleLLM | rulellm_recent_event_overweighter | RuleLLM Recent Event Overweighter | `RuleLLMRecentEventOverweighter` | 2 | `examples/AvailabilityBias/RuleLLM/players.py` |
| Rag | ragllm_recent_event_overweighter | RAG Recent Event Overweighter | `RagLLMRecentEventOverweighter` | 2 | `examples/AvailabilityBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Investor: RecentEventOverweighter

#### 4.1.1  Summary

The RecentEventOverweighter is a retail or semi-institutional investor who gives disproportionate weight to the most recent market event in forming their outlook. When the market has just moved sharply (large `return_pct`), this investor perceives the current moment as abnormally significant -- a directionally important signal -- and trades accordingly, regardless of whether the recent move reflects any genuine change in fundamental value. This investor embodies the availability heuristic in its purest market form: the "available" event (the salient recent return) dominates the objective signal (fundamental deviation). In equilibrium, this creates systematic overreaction to recent price moves and underreaction to slow-developing fundamental trends.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Availability Heuristic (Tversky & Kahneman)**
- Theory / Study: Availability heuristic in probability estimation
- Citation: Tversky, A., & Kahneman, D. (1973). "Availability: A heuristic for judging frequency and probability." *Cognitive Psychology*, 5(2), 207-232. DOI: 10.1016/0010-0285(73)90033-9
- Core Insight: Recent, dramatic events are retrieved from memory more easily than routine events, creating the illusion that they are more probable. Applied to markets: a large price move last round creates a salient mental template that is overweighted in forming the next trading decision.
- Mathematical Formulation: Biased signal weighting: perceived_signal = recency_weight x return_pct + (1 - recency_weight) x deviation. With recency_weight = 0.70, the most recent return receives 70% of the perceived signal and the objective deviation receives 30%.
- Empirical Evidence: De Bondt & Thaler (1985) document a 3-year reversal following extreme past returns -- consistent with availability-driven overreaction creating mispricing that mean-reverts. The simulation calibrates this channel as a high, but bounded, 70% weight on the most recent return.
- Relevance to This Investor: `perceived_signal = 0.70 x return_pct + 0.30 x deviation`. This creates a situation where a large recent return dominates the objective deviation signal -- the core availability distortion.

**Theory 2: Overreaction and Return Reversal (De Bondt & Thaler)**
- Theory / Study: Mean reversion following extreme past returns -- availability-driven overreaction
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreacttheta" *Journal of Finance*, 40(3), 793-805. DOI: 10.2307/2327804
- Core Insight: Investors systematically overreact to dramatic recent news, pushing prices beyond fundamentals; subsequent return reversal is the correction. De Bondt & Thaler (1985) find that portfolios of "extreme loser" stocks over 3-5 years outperform "extreme winner" stocks by 24.6% over the subsequent 3 years -- the reversal confirming prior overreaction.
- Empirical Evidence: The 24.6% three-year reversal documented by De Bondt & Thaler (1985) implies a meaningful initial overreaction before later correction. In simulation terms, a 70% recent-return weight makes short-run returns dominate the signal while keeping the response bounded.
- Relevance to This Investor: salience_threshold = 0.02 (2%) is calibrated so that RecentEventOverweighter activates on meaningful recent moves, creating the directional overreaction documented by De Bondt & Thaler; the simulation tests whether this overreaction is self-correcting or persistent.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Model the availability-heuristic channel by which recent dramatic price moves are amplified into continued overreaction. Without RecentEventOverweighter, the simulation cannot generate the self-reinforcing overreaction dynamic where a salient price move triggers further over-trading in the same direction.

**Activation Scenarios**:
- Scenario A (Positive perceived signal > 0.02): buy. Chases recent positive momentum, driving prices further above fundamental.
- Scenario B (Negative perceived signal < -0.02): sell. Panic sells following a salient decline, amplifying the decline beyond what fundamentals warrant.
- Scenario C (Small perceived signal): hold. Most rounds are holds -- activation requires a salient event.

**Market Contribution**: Destabilizing -- amplifies recent directional moves. Creates momentum (positive autocorrelation in returns during salient-event episodes). The key question is whether this overreaction is large enough to produce measurable persistent mispricing.

**Interaction with other agents**: Amplifies noise-driven moves that MediaInfluencedTrader may also amplify; countered by SystematicAnalyst (which uses objective deviation) and ValueTrader (which requires extreme deviation before acting); may reinforce itself across rounds as its own buying/selling creates the salient returns that trigger the next round's activation.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `return_pct`: The primary "available" signal -- the most recent price return. This is the cognitively salient input that the availability heuristic overweights. recency_weight = 0.70 gives this signal most of the perceived-signal weight.
- `deviation`: Secondary objective signal -- the objective price-to-fundamental gap. Present in the perceived_signal formula with weight 0.30.
- Does NOT separately maintain a history buffer of returns for multi-period weighting -- uses only the single most recent return_pct, consistent with availability heuristic's emphasis on the *most* recently available event.

**4.1.4.2  Core Behavioral Mechanism**
1. Each round, observe `return_pct` and `deviation` from market broadcast.
2. Compute: perceived_signal = recency_weight x return_pct + (1 - recency_weight) x deviation = 0.70 x return_pct + 0.30 x deviation.
3. If |perceived_signal| > salience_threshold (0.02): trade.
4. If perceived_signal > 0 (net positive signal): buy. Quantity = min(300, |perceived_signal| x 5000). Cash-constrained.
5. If perceived_signal < 0 (net negative signal): sell. Quantity = min(300, |perceived_signal| x 5000). Position-constrained.
6. Hold if |perceived_signal| <= 0.02.
7. The sizing formula (|perceived_signal| x 5000) means a perceived_signal of 0.06 produces quantity = 300 shares -- maximum; a signal of 0.02 would produce 100 shares.

**4.1.4.3  Mathematical Model**
- Decision variable: Q*(t) in shares
- Perceived signal: s̃(t) = ρ x r(t) + (1 - ρ) x δ(t), where ρ = recency_weight = 0.70, r = return_pct, δ = deviation
- Trigger function: trade if |s̃(t)| > theta (theta = salience_threshold = 0.02)
- Sizing: Q*(t) = min(Q_max, |s̃(t)| x 5000), where Q_max = 300
- Direction: buy if s̃(t) > 0; sell if s̃(t) < 0
- State variables: cash, position (updated each trade)

| Parameter          | Value | Meaning                                     | Config Path                                                     | Source                                              |
|--------------------|-------|---------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------|
| recency_weight     | 0.70  | Weight on most recent return                | `configs/AvailabilityBias/Rule/players.yml -> recent_event_overweighter` | Tversky & Kahneman (1973); De Bondt & Thaler (1985) |
| salience_threshold | 0.02  | Perceived signal threshold for trading      | `configs/AvailabilityBias/Rule/players.yml -> recent_event_overweighter` | Calibrated to 2% salience filter                    |
| initial_cash       | 10000 | Starting cash reserves                      | `configs/AvailabilityBias/Rule/players.yml -> recent_event_overweighter` | Normalization                                       |
| initial_position   | 0     | Starting share position                     | `configs/AvailabilityBias/Rule/players.yml -> recent_event_overweighter` | Normalization                                       |

**4.1.4.4  Behavioral Properties**
- Time horizon: Short-term -- reacts to each round's most recent return; no multi-period horizon
- Risk tolerance: High -- chases momentum signals without considering fundamental value; would buy into bubbles and sell into crashes
- Information asymmetry: None -- uses publicly broadcast return_pct; the "advantage" is perceptual distortion, not private information
- Psychological profile: Reactive, momentum-following, availability-biased. Prone to chasing recent winners and fleeing recent losers. In LLM variants, the persona emphasizes "I was impressed by last round's dramatic move" as the primary decision driver.

#### 4.1.5  Decision Process Walkthrough

Given: price = 103.0, fundamental = 100.0, deviation = +0.03, prev_price = 100.0, return_pct = +0.03, recency_weight = 0.70, salience_threshold = 0.02, cash = 10000, position = 0

Step 1: Compute perceived_signal = 0.70 x 0.03 + 0.30 x 0.03 = 0.03.
Step 2: Is |0.03| > 0.02theta YES -> buy.

Revised example with larger return:
Given: return_pct = +0.025, deviation = +0.03

Step 1: perceived_signal = 0.70 x 0.025 + 0.30 x 0.03 = 0.0265. Salient enough to trade.

Example with salient return:
Given: return_pct = +0.04, deviation = +0.03

Step 1: perceived_signal = 0.70 x 0.04 + 0.30 x 0.03 = 0.037.
Step 2: |0.037| > 0.02theta YES -> trade (buy, since signal > 0).
Step 3: Quantity = min(300, 0.037 x 5000) = min(300, 185) = 185 shares.
Step 4: Cost check: 185 x 103 = 19055, so cash-constrained quantity is 97.09 shares when starting cash is 10000.
Step 5: Send order: action=buy, quantity≈97.09, bid_price=103.
Result: upward price pressure of lambda x 97.09 ≈ 1.94 price units. Overreaction to a 4% recent return creates additional buying that drives price further above fundamental.

#### 4.1.6  Worked Numerical Example

Market state: price = 98.0, fundamental = 100.0, deviation = -0.02, prev_price = 102.0, return_pct = -0.039 (-3.9% decline last round), recency_weight = 0.70, salience_threshold = 0.02

Perceived signal: s̃ = 0.70 x (-0.039) + 0.30 x (-0.02) = -0.0333.
|-0.0333| > 0.02 -> sell.
Quantity: min(300, 0.0333 x 5000) = 166.5 shares, then constrained by current position.
Order: action=sell, quantity=166.5 if the investor has sufficient position, bid_price=98.
Rationale: The dramatic -3.9% decline last round is cognitively "available" -- the investor perceives this as a strong negative signal because recent return receives 70% of the perceived-signal weight. Despite the objective deviation being only -2% (a mild undervaluation that a rational investor would buy), the availability-biased investor sells if it has inventory, amplifying the decline. This is De Bondt & Thaler's overreaction mechanism in action.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                               |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1973). "Availability: A heuristic for judging frequency and probability." *Cognitive Psychology*, 5(2), 207-232. DOI: 10.1016/0010-0285(73)90033-9 | Core theoretical basis; recency_weight calibration                  |
| 2 | De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreacttheta" *Journal of Finance*, 40(3), 793-805. DOI: 10.2307/2327804                                       | Empirical overreaction and reversal; salience_threshold calibration |
| 3 | Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.                                                                                                      | System 1 vs. System 2; availability bias as System 1 default        |


---

## Source Docstring Excerpts

### Rule / `RecentEventOverweighter`

```text
Overweights recent dramatic market events in decision-making.

Theory: simulation-bases.md Section 4.1 -- RecentEventOverweighter
Theoretical basis: Tversky & Kahneman (1973) -- Availability heuristic recency channel.
Perceived signal = recency_weight * recent_return + (1-recency_weight) * deviation.
Trades when perceived signal exceeds salience_threshold.
See simulation-bases.md Section 4.1.4.3 for mathematical model.
```

### LLM / `LLMRecentEventOverweighter`

```text
LLM-driven trader who overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMRecentEventOverweighter`

```text
RuleLLM -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMRecentEventOverweighter`

```text
RAG-augmented -- overweights recent dramatic market events. Theory: simulation-bases.md Section 4.1.
```
