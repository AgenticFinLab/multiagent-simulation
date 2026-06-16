# BlackMonday1987 / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | BlackMonday1987 |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The NoiseTrader represents the heterogeneous mass of retail investors and smaller institutions who trade on perceived signals, rumors, or emotional reactions rather than systematic strategies. On October 19, 1987, retail participation was a small fraction of total volume (dominated by institutional program trading), but retail traders contributed to the liquidity drought by withdrawing buy-side orders. The NoiseTrader's role in the simulation is to add stochastic variation to net demand -- preventing the simulation from converging to a perfectly deterministic cascade and ensuring variance across simulation runs that is necessary for meaningful statistical analysis.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) -- noise makes markets possible; provides

### LLM / `LLMNoiseTrader`
- LLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMNoiseTrader`
- RuleLLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `100000.0`<br>LLM: `100000.0`<br>RuleLLM: `100000.0`<br>Rag: `100000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.BlackMonday1987.LLM.prompts:LLM_NOISE_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_NOISE_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.BlackMonday1987.Rag.prompts:RAG_NOISE_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `200.0`<br>RuleLLM: `200.0`<br>Rag: `200.0` | Rag, Rule, RuleLLM |
| min_order | Rule: `50.0`<br>RuleLLM: `50.0`<br>Rag: `50.0` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_probability | Rule: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/BlackMonday1987/Rule/players.py` |
| LLM | noise_trader | Noise Trader | `LLMNoiseTrader` | 2 | `examples/BlackMonday1987/LLM/players.py` |
| RuleLLM | noise_trader | Noise Trader | `RuleLLMNoiseTrader` | 2 | `examples/BlackMonday1987/RuleLLM/players.py` |
| Rag | ragllm_noise_trader | RAG Noise Trader | `RagLLMNoiseTrader` | 2 | `examples/BlackMonday1987/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

#### 4.5.1  Summary

The NoiseTrader represents the heterogeneous mass of retail investors and smaller institutions who trade on perceived signals, rumors, or emotional reactions rather than systematic strategies. On October 19, 1987, retail participation was a small fraction of total volume (dominated by institutional program trading), but retail traders contributed to the liquidity drought by withdrawing buy-side orders. The NoiseTrader's role in the simulation is to add stochastic variation to net demand -- preventing the simulation from converging to a perfectly deterministic cascade and ensuring variance across simulation runs that is necessary for meaningful statistical analysis.

#### 4.5.2  Theoretical and Empirical Foundation

**Theory 1: Noise Trading Theory (Black)**
- Theory / Study: The role of noise traders in market function and price discovery
- Citation: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481
- Core Insight: Black argues that noise traders -- who trade on noise as if it were information -- are paradoxically essential for market function: they provide liquidity that allows informed traders to execute their strategies. Without noise, markets would be too illiquid to function. In a crash, noise traders represent the background retail order flow that adds unpredictability to the institutional-dominated cascade.
- Mathematical Formulation: Noise trader behavior is modeled as stochastic: trade probability p_trade per round, with direction ∈ {buy, sell} with equal probability, and quantity ~ Uniform(min_order, max_order). This creates E[net_demand_noise] = 0 but Var[net_demand_noise] > 0, adding stochastic variation without systematic directional bias.
- Empirical Evidence: Black (1986) estimates noise traders account for 20-40% of daily trading volume in equilibrium. On October 19, retail volume was approximately 10-15% of NYSE volume (well below normal fraction), consistent with retail withdrawal behavior during extreme crashes. Trade probability calibration: 3-8% per round.
- Relevance to This Investor: trade_probability = 0.05 (5% per round) calibrated to slightly below normal retail participation, reflecting the withdrawal of retail buy orders during the crash; quantity range [100, 500] consistent with retail lot sizes.

**Theory 2: Sentiment and Retail Herding**
- Theory / Study: Investor sentiment and retail herding during market stress
- Citation: Shiller, R. J. (1987). "Investor behavior in the October 1987 stock market crash: Survey evidence." *NBER Working Paper* No. 2446. DOI: 10.3386/w2446. Also: Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773-806. DOI: 10.1111/j.1540-6261.2000.tb04002.x
- Core Insight: Shiller's post-crash survey found that retail investors on October 19 were primarily reacting to news of falling prices and other investors' behavior -- a classic herd dynamic -- rather than fundamental information. Barber & Odean (2000) document that retail investors trade excessively and often destructively relative to professional strategies.
- Empirical Evidence: Shiller (1987) survey data show 93% of individual investors on October 19 reported "gut feeling" as a primary decision input; only 28% could articulate a specific reason for trading. This is consistent with noise trading as modeled here -- random direction, not strategic.
- Relevance to This Investor: The random buy/sell direction (50/50 probability) with uniform quantity captures Shiller's documented retail behavior -- trading on gut feeling rather than systematic signals. Trade_probability = 5% per round calibrated to retail participation rate.

#### 4.5.3  Design Purpose and Activation Scenarios

**Purpose**: Add stochastic variation to the simulation -- ensure that each run produces slightly different price paths, enabling meaningful statistical comparison across variants. Without NoiseTrader, all runs with the same parameters would produce identical outcomes, eliminating the cross-variant comparison framework.

**Activation Scenarios**:
- Scenario A (Normal market): NoiseTrader trades with 5% probability each round in random direction; small positive or negative contribution to D(t). No systematic effect.
- Scenario B (Crash phase): Same behavior -- NoiseTrader does not change behavior during the crash, unlike all other agents. This is realistic: retail investors react with equal probability of panic selling and discount buying.
- Scenario C (Recovery): Same behavior -- maintains background stochasticity throughout simulation.

**Market Contribution**: Neutral on average -- E[net_demand_noise] = 0. Destabilizing or stabilizing on any given round depending on random draw.

**Interaction with other agents**: No strategic interaction -- purely stochastic. The noise term prevents exact determinism in rule-based simulations; in LLM variants, the NoiseTrader also introduces LLM stochasticity (different word choices producing slightly different actions each call).

#### 4.5.4  Behavioral Framework

**4.5.4.1  Decision Information Set**
- No market signals used -- purely random decision making. Does not observe `deviation`, `price`, or `fundamental`. Consistent with Black (1986)'s noise trading definition: "trading on noise as if it were a signal."

**4.5.4.2  Core Behavioral Mechanism**
1. Each round, draw a random number r ~ Uniform(0, 1).
2. If r < trade_probability (0.05): trade this round.
3. If trading: draw direction ~ Bernoulli(0.5); draw quantity ~ Uniform(min_order, max_order) = Uniform(100, 500).
4. Execute the random trade (buy or sell).
5. If r >= 0.05: hold -- no action this round. (95% of rounds are passes.)

**4.5.4.3  Mathematical Model**
- Decision variable: random action ∈ {buy, sell, hold}
- Trade probability: P(trade) = p = 0.05
- Direction: P(buy | trade) = P(sell | trade) = 0.5
- Sizing: Q ~ Uniform(100, 500) conditional on trading
- Expected contribution per round: E[D_noise] = 0; Var[D_noise] = p x (mean_Q² + var_Q) / 4 where mean_Q = 300, var_Q = 200²/12 ≈ 3333

| Parameter         | Value | Meaning                                 | Config Path                                       | Source                       |
|-------------------|-------|-----------------------------------------|---------------------------------------------------|------------------------------|
| trade_probability | 0.05  | Probability of trading in a given round | `BlackMonday1987/Rule/config.yaml -> noise_trader` | Black (1986); Shiller (1987) |
| min_order         | 100   | Minimum trade quantity                  | `BlackMonday1987/Rule/config.yaml -> noise_trader` | Retail lot size convention   |
| max_order         | 500   | Maximum trade quantity                  | `BlackMonday1987/Rule/config.yaml -> noise_trader` | Retail lot size convention   |

**4.5.4.4  Behavioral Properties**
- Time horizon: Short-term (random; no planning horizon)
- Risk tolerance: Medium (random; not optimizing risk-return tradeoff)
- Information asymmetry: None -- trades on noise, not information
- Psychological profile: Uncertain, reactive to perceived market conditions but without systematic strategy. In LLM variants, the persona provides varied responses that simulate gut-feeling retail investor behavior; the randomness is encoded in the LLM's natural language variability rather than explicit probability draws

#### 4.5.5  Decision Process Walkthrough

Given: Random draw r = 0.031 (< 0.05 -> trade); direction draw = 0 (-> sell); quantity draw = 320

Step 1: r = 0.031 < 0.05 -> trade this round.
Step 2: Direction = sell (random draw).
Step 3: Quantity = 320 shares (random draw from [100, 500]).
Step 4: Send order: action=sell, quantity=320, bid_price=current price.
Step 5: Net market impact: -320 shares in D(t).

Alternative (hold round): r = 0.72 >= 0.05 -> no trade; D_noise contribution = 0.

#### 4.5.6  Worked Numerical Example

Market state: price = 237.5, fundamental = 250.0, deviation = -0.05, random_r = 0.024

Trade trigger: r = 0.024 < 0.05 -> trade.
Direction: random = buy.
Quantity: random = 180 shares.
Order sent: action=buy, quantity=180, bid_price=237.5.
Rationale: This is noise -- the NoiseTrader has no view on the -5% deviation. The trade is purely random. It happens to add to D(t) as a buy (+180), partially counteracting selling from PortfolioInsurer, but this is coincidental. Over many rounds, NoiseTrader's net contribution to D(t) averages to zero.

#### 4.5.7  Academic References

| # | Citation                                                                                                                                                | Notes                                                                          |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.2307/2328481                                                                   | Core theoretical basis for noise trader concept; trade_probability calibration |
| 2 | Shiller, R. J. (1987). "Investor behavior in the October 1987 stock market crash." *NBER Working Paper* No. 2446. DOI: 10.3386/w2446                    | Empirical basis for retail direction randomness; post-crash survey data        |
| 3 | Barber, B. M., & Odean, T. (2000). "Trading is hazardous to your wealth." *Journal of Finance*, 55(2), 773-806. DOI: 10.1111/j.1540-6261.2000.tb04002.x | Retail investor trading behavior; overtrading and random direction evidence    |

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Random uninformed trader (neutral).

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) -- noise makes markets possible; provides
liquidity and baseline price variance independent of fundamentals.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMNoiseTrader`

```text
LLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
RuleLLM-driven noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented noise trader -- random uninformed liquidity provider. Theory: simulation-bases.md Section 4.5.
```
