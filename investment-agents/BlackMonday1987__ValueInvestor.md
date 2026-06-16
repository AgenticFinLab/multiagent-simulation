# BlackMonday1987 / Value Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | BlackMonday1987 |
| Agent type | Value Investor |
| Canonical class | `ValueInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The ValueInvestor is a patient institutional buyer -- modeled on Graham-style value investing as practiced by firms like Berkshire Hathaway -- who stands ready to buy when prices fall significantly below intrinsic value. The ValueInvestor's defining characteristic is the margin of safety: a predetermined discount to fundamental value (15% below fair value) below which equities are considered attractively priced regardless of near-term momentum. The ValueInvestor is the simulation's sole stabilizing force during the crash: when deviation crosses -0.15, it begins absorbing the supply from portfolio insurers and program traders, providing the price floor that prevents complete market collapse.

## Financial Theory / Theoretical Basis

### Rule / `ValueInvestor`
- Theory: simulation-bases.md Section 4.4 -- ValueInvestor
- Theoretical basis: Graham (1949) value investing with margin of safety;

### LLM / `LLMValueInvestor`
- LLM-driven value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMValueInvestor`
- RuleLLM-driven value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMValueInvestor`
- RAG-augmented value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.BlackMonday1987.LLM.prompts:LLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_VALUE_INVESTOR_SYS', 'user_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.BlackMonday1987.Rag.prompts:RAG_VALUE_INVESTOR_SYS', 'user_message': 'examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| value_discount | Rule: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_investor | Value Investor | `ValueInvestor` | 1 | `examples/BlackMonday1987/Rule/players.py` |
| LLM | value_investor | Value Investor | `LLMValueInvestor` | 1 | `examples/BlackMonday1987/LLM/players.py` |
| RuleLLM | value_investor | Value Investor | `RuleLLMValueInvestor` | 1 | `examples/BlackMonday1987/RuleLLM/players.py` |
| Rag | ragllm_value_investor | RAG Value Investor | `RagLLMValueInvestor` | 1 | `examples/BlackMonday1987/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ValueInvestor

#### 4.4.1  Summary

The ValueInvestor is a patient institutional buyer -- modeled on Graham-style value investing as practiced by firms like Berkshire Hathaway -- who stands ready to buy when prices fall significantly below intrinsic value. The ValueInvestor's defining characteristic is the margin of safety: a predetermined discount to fundamental value (15% below fair value) below which equities are considered attractively priced regardless of near-term momentum. The ValueInvestor is the simulation's sole stabilizing force during the crash: when deviation crosses -0.15, it begins absorbing the supply from portfolio insurers and program traders, providing the price floor that prevents complete market collapse.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Margin of Safety and Value Investing (Graham)**
- Theory / Study: Security Analysis -- margin of safety concept
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. Full theoretical treatment: Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley.
- Core Insight: Graham's margin of safety principle states that an investment should only be made when the purchase price is sufficiently below the estimated intrinsic value to provide a buffer against estimation error. For equity portfolios, Graham recommended 20-33% discount to intrinsic value for common stock purchases. This principle creates a price floor: when a sufficient fraction of market participants share value-investing discipline, prices cannot fall indefinitely below fundamental value.
- Mathematical Formulation: Buy signal: P < F x (1 - MoS), where MoS = margin_of_safety. With F = 250 and MoS = 0.15: buy when P < 212.5. Sell signal: P > F x (1 + MoS), i.e., P > 287.5. Fixed order size: Q = base_size (not deviation-scaled), reflecting Graham's emphasis on predetermined, non-speculative position sizing.
- Empirical Evidence: Historical studies of value investing returns document that buying at 15-25% discounts to NAV generates significantly positive risk-adjusted returns. Greenwald et al. (2001) document average excess return of 6-8% annualized for deep-value strategies with 15%+ discount triggers. Warren Buffett publicly disclosed major equity purchases during and after the 1987 crash, consistent with MoS = 15-20%.
- Relevance to This Investor: value_discount = 0.15, base_size = 40 calibrated to model a single large institutional buyer who activates at the Graham margin of safety threshold and buys fixed-size lots.

**Theory 2: Limits of Arbitrage and Stabilizing Speculation**
- Theory / Study: Rational destabilization vs. stabilizing arbitrage
- Citation: Friedman, M. (1953). "The case for flexible exchange rates." In *Essays in Positive Economics*. University of Chicago Press. Also: Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35-55. DOI: 10.2307/2329555
- Core Insight: Friedman (1953) argued that destabilizing speculation is self-eliminating because speculators who buy high and sell low will eventually lose money and exit. Stabilizing speculators (who buy low and sell high) survive and earn profits. The ValueInvestor instantiates Friedman's stabilizing speculator: it buys at deep discounts and sells at premiums. However, Shleifer & Vishny (1997) note that even rational stabilizing speculators face capital constraints that limit their ability to prevent crashes -- the "limits of arbitrage" means ValueInvestor cannot fully absorb the crash.
- Mathematical Formulation: Stabilizing condition: buying at P < F x (1 - MoS) generates expected profit = F - P - transaction_cost > 0. However, capital constraint Q_max = cash / P limits total absorption capacity. If PortfolioInsurer + ProgramTrader sell > ValueInvestor's cash / price per round, ValueInvestor cannot arrest the decline alone.
- Empirical Evidence: Shleifer & Vishny (1997) document that large-scale arbitrage funds reduce but do not eliminate mispricings; in practice, the stabilizing effect is partial. During the 1987 crash, value-oriented buyers were active but insufficient to arrest the one-day decline; recovery required Fed intervention (liquidity guarantee on October 20).
- Relevance to This Investor: The ValueInvestor provides a partial floor -- it absorbs some supply at deep discounts -- but the simulation is calibrated so that cascade selling exceeds ValueInvestor's absorption capacity during peak crash, consistent with the Shleifer-Vishny limits-of-arbitrage framework.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Provide the crash's price floor mechanism -- model the patient buyers who step in at deep discounts, arresting (but not reversing) the immediate cascade. Without ValueInvestor, prices would collapse to near-zero; with it, a realistic crash floor emerges.

**Activation Scenarios**:
- Scenario A (Moderate decline, -5% to -14%): ValueInvestor inactive -- deviation does not yet meet the margin of safety threshold. This models Graham's discipline: buying too early (at only a 5% discount) is not value investing.
- Scenario B (Threshold crossed, deviation < -15%): ValueInvestor activates -- buys fixed base_size (40 shares) each round. Provides sustained buying that partially offsets cascade selling. At peak crash (deviation ≈ -20%), net D(t) is still negative but less extreme.
- Scenario C (Recovery, deviation > +15%): ValueInvestor begins selling -- takes profit at the same margin of safety threshold above fair value. This is the symmetric realization of the value investing principle.

**Market Contribution**: Stabilizing -- the only consistent buyer during the crash. Activates at deviation < -15%, creating a floor effect. At base_size = 40, ValueInvestor adds up to +40 to D(t) per round -- partially offsetting the combined PortfolioInsurer + ProgramTrader selling but typically insufficient to fully reverse the cascade.

**Interaction with other agents**: Directly opposes PortfolioInsurer and ProgramTrader (buys what they sell); IndexArbitrageur may also buy at deep discounts, creating an alliance of stabilizing buyers; NoiseTrader's random buying occasionally reinforces the floor.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Decision Information Set**
- `deviation`: Primary signal -- triggers buy (< -value_discount) and sell (> +value_discount); consistent with relative-value investing where the decision is based on the discount to intrinsic value, not the absolute price level.
- `cash`: Constrains buying -- cannot buy more than available cash; realistic capital constraint on the stabilizing effect.
- `price`: Used for order sizing (cash / price to compute max buyable quantity) and for order submission.
- Does NOT use volume, momentum, or other agents' signals -- consistent with Graham's principle that the value investor ignores market psychology and focuses solely on the relationship between price and intrinsic value.

**4.4.4.2  Core Behavioral Mechanism**
1. Each round, ValueInvestor observes `deviation`.
2. If deviation < -value_discount (-0.15): price is at or below the margin of safety -> buy `base_size` shares. Cash-constrained: if cost = base_size x price > cash, buy min(base_size, int(cash / price)) shares.
3. If deviation > +value_discount (+0.15): price is above the sell-at-premium threshold -> sell `base_size` shares from position.
4. If |deviation| <= 0.15: price is within fair value range -> hold. No action needed.
5. Order size is fixed by `base_size` (40 shares) -- not deviation-scaled. This reflects Graham's predetermined position sizing rather than dynamic sizing.

**4.4.4.3  Mathematical Model**
- Decision variable: Q*(t) = fixed base_size or cash-constrained minimum
- Trigger function: buy if δ(t) < -m; sell if δ(t) > +m; where m = value_discount = 0.15
- Buy sizing: Q*_buy = min(base_size, floor(cash / price))
- Sell sizing: Q*_sell = min(base_size, position)
- State variables: cash, position (updated each trade)

| Parameter      | Value  | Meaning                                        | Config Path                                         | Source                              |
|----------------|--------|------------------------------------------------|-----------------------------------------------------|-------------------------------------|
| value_discount | 0.15   | Margin of safety threshold (deviation trigger) | `BlackMonday1987/Rule/config.yaml -> value_investor` | Graham (1949); Graham & Dodd (1934) |
| base_size     | 40     | Fixed shares per value buy/sell                | `BlackMonday1987/Rule/config.yaml -> value_investor` | Normalization (institutional scale) |
| initial_cash   | 500000 | Cash reserves for crash buying                 | `BlackMonday1987/Rule/config.yaml -> value_investor` | Normalization (large reserve)       |

**4.4.4.4  Behavioral Properties**
- Time horizon: Long-term -- ValueInvestor is not concerned with round-to-round price moves; activates only when the margin of safety is present; patient
- Risk tolerance: High -- deliberately buys during worst drawdowns when other agents are selling; counterintuitive from a momentum perspective but rational from a value perspective
- Information asymmetry: None -- uses only publicly available price and fundamental; consistent with Graham's emphasis on publicly available financial data
- Psychological profile: Patient, contrarian, high conviction. Immune to short-term panic. In LLM variants, the "be greedy when others are fearful" persona (Buffett's maxim) is the key behavioral prompt

#### 4.4.5  Decision Process Walkthrough

Given: price = 207.5, fundamental = 250.0, deviation = -0.17, base_size = 40, cash = 450000

Step 1: Observe deviation = -0.17. Is -0.17 < -0.15 (value_discount)theta YES -> buy.
Step 2: Compute cost: 40 x 207.5 = 8300. Is 8300 <= 450000 cashtheta YES -> full order.
Step 3: Buy quantity: Q = 40 shares.
Step 4: Send order: action=buy, quantity=40, bid_price=207.5.
Step 5: Net market impact: +40 shares in D(t); upward price pressure of lambda x 40 = 0.05 x 40 = 2.0 price units.

Note: In the same round, PortfolioInsurer might sell 125 + ProgramTrader 260 = 385 combined. ValueInvestor's +40 partially offsets the combined automated selling, creating net positive demand and partial price stabilization. This is the price floor mechanism operating.

#### 4.4.6  Worked Numerical Example

Market state: price = 195.0, fundamental = 250.0, deviation = -0.22, base_size = 40, cash = 384000, position = 2400

Trigger check: -0.22 < -0.15 -> buy condition active.
Cost: 40 x 195 = 7800. Is 7800 <= 384000theta YES.
Buy quantity: Q = 40.
Updated cash: 384000 - 7800 = 376200. Updated position: 2400 + 40 = 2440.
Order sent: action=buy, quantity=40, bid_price=195.0.
Rationale: A 22% discount to fundamental (below the 15% margin of safety) triggers the Graham-style buy. The fixed base_size reflects predetermined position sizing discipline -- buying the same quantity regardless of how extreme the discount is, avoiding the behavioral trap of "doubling down" during panic.

#### 4.4.7  Academic References

| # | Citation                                                                                                                     | Notes                                                                                       |
|---|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                             | Original formulation of margin of safety concept; basis for value_discount = 0.15           |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                            | Popularization of margin of safety for equity portfolios; base_size fixed sizing principle |
| 3 | Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35-55. DOI: 10.2307/2329555    | Why ValueInvestor provides partial but incomplete floor; capital constraint analysis        |
| 4 | Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley. | Empirical documentation of value_discount calibration; historical return evidence           |


---

## Source Docstring Excerpts

### Rule / `ValueInvestor`

```text
Buys when price falls below intrinsic value (stabilizing).

Theory: simulation-bases.md Section 4.4 -- ValueInvestor
Theoretical basis: Graham (1949) value investing with margin of safety;
purchases equities at deep discount to fundamental value.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMValueInvestor`

```text
LLM-driven value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMValueInvestor`

```text
RuleLLM-driven value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMValueInvestor`

```text
RAG-augmented value investor -- buys at deep discount to fundamentals. Theory: simulation-bases.md Section 4.4.
```
