# AvailabilityBias / Value Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AvailabilityBias |
| Agent type | Value Trader |
| Canonical class | `ValueTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The ValueTrader is a patient, fundamental-focused investor who trades only when the price-fundamental gap is large enough to represent a clear margin of safety. Unlike the SystematicAnalyst (who responds to 3% deviations), the ValueTrader requires a 5% deviation before acting -- a higher bar that ensures it is not distracted by the smallest noise-level mispricings. The ValueTrader embodies Graham's value investing discipline applied to a market distorted by cognitive bias: it waits for bias-driven overreaction to create meaningful bargains (deviation < -5%) or clear overvaluation (deviation > +5%) and then acts with fixed position sizing.

## Financial Theory / Theoretical Basis

### Rule / `ValueTrader`
- Theory: simulation-bases.md Section 4.4 -- ValueTrader
- Theoretical basis: Graham (1949); Baker & Wurgler (2007) -- Value investing discipline.

### LLM / `LLMValueTrader`
- LLM-driven value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMValueTrader`
- RuleLLM value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMValueTrader`
- RAG-augmented value trader -- fundamentals only. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| deviation_threshold | Rule: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AvailabilityBias.LLM.prompts:LLM_VALUE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_VALUE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AvailabilityBias.Rag.prompts:RAG_VALUE_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `300.0`<br>RuleLLM: `300.0`<br>Rag: `300.0` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_trader | Value Trader | `ValueTrader` | 2 | `examples/AvailabilityBias/Rule/players.py` |
| LLM | llm_value_trader | LLM Value Trader | `LLMValueTrader` | 2 | `examples/AvailabilityBias/LLM/players.py` |
| RuleLLM | rulellm_value_trader | RuleLLM Value Trader | `RuleLLMValueTrader` | 2 | `examples/AvailabilityBias/RuleLLM/players.py` |
| Rag | ragllm_value_trader | RAG Value Trader | `RagLLMValueTrader` | 2 | `examples/AvailabilityBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Investor: ValueTrader

#### 4.4.1  Summary

The ValueTrader is a patient, fundamental-focused investor who trades only when the price-fundamental gap is large enough to represent a clear margin of safety. Unlike the SystematicAnalyst (who responds to 3% deviations), the ValueTrader requires a 5% deviation before acting -- a higher bar that ensures it is not distracted by the smallest noise-level mispricings. The ValueTrader embodies Graham's value investing discipline applied to a market distorted by cognitive bias: it waits for bias-driven overreaction to create meaningful bargains (deviation < -5%) or clear overvaluation (deviation > +5%) and then acts with fixed position sizing.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Value Investing and Margin of Safety (Graham)**
- Theory / Study: Margin of safety as the core principle of value investing
- Citation: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. Also: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.
- Core Insight: Graham's margin of safety principle requires buying at a substantial discount to intrinsic value to guard against error and uncertainty. In an availability-biased market, media-driven and recency-biased agents create transient mispricings that are not genuine fundamental changes. The ValueTrader sets deviation_threshold = 0.05 to distinguish meaningful mispricing from routine fluctuations.
- Empirical Evidence: Graham recommended a large margin of safety for common stocks; in the simulation context of a normalized single-asset market, 5% is a meaningful margin that lets value trading appear within 200 rounds without dominating every small fluctuation. Fixed order sizing (position_size = 300 shares) reflects Graham's predetermined discipline.
- Relevance to This Investor: deviation_threshold = 0.05 calibrated to activate only on meaningful availability-bias-driven mispricings; position_size = 300 is fixed and not deviation-scaled, reflecting Graham's non-speculative position sizing discipline.

**Theory 2: Long-Horizon Return Predictability and Value Premium**
- Theory / Study: Value factor -- long-run return predictability from price-to-book ratios
- Citation: Fama, E. F., & French, K. R. (1992). "The cross-section of expected stock returns." *Journal of Finance*, 47(2), 427-465. DOI: 10.2307/2329112. Also: Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129-151. DOI: 10.1257/jep.21.2.129
- Core Insight: Fama & French (1992) document a persistent value premium -- stocks with high book-to-market ratios (more undervalued) earn significantly higher subsequent returns. Baker & Wurgler (2007) show that this premium is highest following high-sentiment periods, consistent with availability-biased overreaction creating the mispricings that value investors subsequently profit from.
- Empirical Evidence: Fama & French (1992) document average value premium of 4-6% annually. Baker & Wurgler (2007) find that high-sentiment periods predict lower subsequent returns for growth stocks, consistent with the value investor providing the corrective force after availability-biased periods.
- Relevance to This Investor: ValueTrader embodies the mechanism behind the value premium -- patient buying at deep discounts created by sentiment-/bias-driven selling, with subsequent return as mean reversion restores prices to fundamental.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Provide a patient stabilizing force -- activating only when availability-biased agents have created a meaningful >=5% mispricing. ValueTrader is the price floor for undervaluation and ceiling for overvaluation in the simulation.

**Activation Scenarios**:
- Scenario A (Bias creates moderate mispricing, |deviation| < 5%): Hold. Availability bias fluctuations are insufficient to meet ValueTrader's margin of safety threshold.
- Scenario B (Undervaluation, deviation < -5%): Buy 300 shares, cash-constrained. ValueTrader's buying begins arresting the decline.
- Scenario C (Overvaluation, deviation > +5%): Sell 300 shares, position-constrained. Availability-biased momentum buying has pushed prices to a premium; ValueTrader takes profit and provides corrective selling.

**Market Contribution**: Stabilizing floor/ceiling mechanism. When active, adds up to 300 shares to buy or sell side regardless of deviation magnitude, providing a discrete stabilizing shock.

**Interaction with other agents**: Counters both RecentEventOverweighter and MediaInfluencedTrader when they collectively drive deviation beyond 5%; aligns with SystematicAnalyst (both stabilizing, different thresholds); provides a price floor/ceiling against availability-driven extremes.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Sole decision signal -- the objective price-fundamental gap. Higher threshold (0.05) than SystematicAnalyst (0.03) means ValueTrader filters out smaller bias episodes.
- `cash`, `position`: Constraint variables; cash must cover position_size x price for buying.

**4.4.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation < -deviation_threshold (-0.05): buy position_size = 300 shares (cash-constrained).
3. If deviation > +deviation_threshold (+0.05): sell position_size = 300 shares (position-constrained).
4. Hold if |deviation| <= 0.05.

**4.4.4.3  Mathematical Model**
- Trigger function: buy if δ < -m; sell if δ > +m; where m = deviation_threshold = 0.05
- Sizing: Q*(t) = min(position_size, floor(cash / price)) for buys; min(position_size, position) for sells
- Fixed size: position_size = 300 (no deviation-proportional scaling)
- State variables: cash, position

| Parameter           | Value | Meaning                                    | Config Path                                        | Source                                                     |
|---------------------|-------|--------------------------------------------|----------------------------------------------------|------------------------------------------------------------|
| deviation_threshold | 0.05  | Minimum deviation to trigger value trading | `configs/AvailabilityBias/Rule/players.yml -> value_trader` | Graham (1949); calibrated to availability-bias episodes |
| position_size       | 300   | Fixed shares per value trade               | `configs/AvailabilityBias/Rule/players.yml -> value_trader` | Graham (1949) fixed sizing discipline                   |
| initial_cash        | 10000 | Starting cash                              | `configs/AvailabilityBias/Rule/players.yml -> value_trader` | Normalization                                           |
| initial_position    | 0     | Starting position                          | `configs/AvailabilityBias/Rule/players.yml -> value_trader` | Normalization                                           |

**4.4.4.4  Behavioral Properties**
- Time horizon: Long-term -- activates only at deep mispricings; patient between activations
- Risk tolerance: High -- deliberately buys during periods when biased agents are selling heavily; contrarian conviction
- Information asymmetry: None -- same public information as all agents; advantage is patient, unbiased processing
- Psychological profile: Patient, conviction-driven, immune to availability bias. In LLM variants, persona emphasizes: "I ignore media noise and recent price drama. I act only when the fundamental gap is undeniable."

#### 4.4.5  Decision Process Walkthrough

Given: price = 95.0, fundamental = 100.0, deviation = -0.05, deviation_threshold = 0.05, position_size = 300, cash = 10000

Step 1: deviation = -0.05. The rule activates when deviation is below -0.05; at exactly -0.05 it holds.
Step 2: If price falls to 94.0 (deviation = -0.06), buy quantity = min(300, 10000 / 94.0) = 106.38 shares.
Step 3: Send order: action=buy, quantity≈106.38, bid_price=94.
Result: stabilizing buying appears only after the gap exceeds the 5% threshold.

#### 4.4.6  Worked Numerical Example

Market state: price = 106.0, fundamental = 100.0, deviation = +0.06, position = 300

Trigger: +0.06 > +0.05 -> sell.
Quantity: min(300, 300) = 300.
Order: action=sell, quantity=300, bid_price=106.
Rationale: Availability-biased agents have driven price above fundamental through recency and media overreaction. ValueTrader sells 300 shares -- the fixed-size Graham discipline prevents speculative over-selling while correcting a meaningful bias-driven premium.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                 | Notes                                                                                                        |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| 1 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                        | deviation_threshold calibration; fixed position_size principle                                               |
| 2 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                         | Original margin of safety concept                                                                            |
| 3 | Fama, E. F., & French, K. R. (1992). "The cross-section of expected stock returns." *Journal of Finance*, 47(2), 427-465. DOI: 10.2307/2329112           | Value premium evidence; return predictability from deep undervaluation                                       |
| 4 | Baker, M., & Wurgler, J. (2007). "Investor sentiment in the stock market." *Journal of Economic Perspectives*, 21(2), 129-151. DOI: 10.1257/jep.21.2.129 | Sentiment-created mispricings that ValueTrader corrects; empirical basis for availability bias market impact |


---

## Source Docstring Excerpts

### Rule / `ValueTrader`

```text
Value trader -- trades on fundamentals, ignores media narratives.

Theory: simulation-bases.md Section 4.4 -- ValueTrader
Theoretical basis: Graham (1949); Baker & Wurgler (2007) -- Value investing discipline.
Trades when deviation exceeds deviation_threshold with fixed position_size.
See simulation-bases.md Section 4.4.4.3 for mathematical model.
```

### LLM / `LLMValueTrader`

```text
LLM-driven value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMValueTrader`

```text
RuleLLM value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMValueTrader`

```text
RAG-augmented value trader -- fundamentals only. Theory: simulation-bases.md Section 4.4.
```
