# AsianFinancialCrisis / Value Contrarian

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AsianFinancialCrisis |
| Agent type | Value Contrarian |
| Canonical class | `ValueContrarian` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

ValueContrarian represents the private-sector fundamental investor who seeks to exploit deep crisis-driven discounts to fundamental value. This agent models long-horizon institutional investors -- hedge funds, sovereign wealth funds, private equity -- who are willing to buy assets during crisis but require a larger discount than the IMF (which has sovereign backing and can tolerate lower expected returns). ValueContrarian provides the second layer of price floor support after IMFRescuer and eventually profits from crisis recovery.

## Financial Theory / Theoretical Basis

### Rule / `ValueContrarian`
- Theory: simulation-bases.md Section 4.4 -- ValueContrarian
- Theoretical Basis: Contrarian crisis investing (Radelet & Sachs, 1998 baseline)

### LLM / `LLMValueContrarian`
- LLM-driven value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMValueContrarian`
- RuleLLM value contrarian with explicit oversold/overbought threshold rules. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMValueContrarian`
- RAG-augmented value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_ratio | Rule: `0.2` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500.0`<br>LLM: `500.0`<br>RuleLLM: `500.0`<br>Rag: `500.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_VALUE_CONTRARIAN_SYS', 'user_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_VALUE_CONTRARIAN_SYS', 'user_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_VALUE_CONTRARIAN_SYS', 'user_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| overbought_threshold | Rule: `0.1` | Rule |
| oversold_threshold | Rule: `-0.08` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_ratio | Rule: `0.2` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_contrarian | Value Contrarian | `ValueContrarian` | 2 | `examples/AsianFinancialCrisis/Rule/players.py` |
| LLM | value_contrarian | Value Contrarian | `LLMValueContrarian` | 2 | `examples/AsianFinancialCrisis/LLM/players.py` |
| RuleLLM | value_contrarian | Value Contrarian | `RuleLLMValueContrarian` | 2 | `examples/AsianFinancialCrisis/RuleLLM/players.py` |
| Rag | ragllm_value_contrarian | RAG Value Contrarian | `RagLLMValueContrarian` | 2 | `examples/AsianFinancialCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ValueContrarian

#### 4.4.1  Summary

ValueContrarian represents the private-sector fundamental investor who seeks to exploit deep crisis-driven discounts to fundamental value. This agent models long-horizon institutional investors -- hedge funds, sovereign wealth funds, private equity -- who are willing to buy assets during crisis but require a larger discount than the IMF (which has sovereign backing and can tolerate lower expected returns). ValueContrarian provides the second layer of price floor support after IMFRescuer and eventually profits from crisis recovery.

#### 4.4.2  Theoretical and Empirical Foundation

**Crisis Investing and Fundamental Value Recovery**:
- Theory / Study: Contrarian Investing and Mean Reversion
- Citation: Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007-2008. *Journal of Economic Perspectives*, 23(1), 77-100. https://doi.org/10.1257/jep.23.1.77
- Core Insight: In severe liquidity crises, assets trade far below fundamental values due to fire-sale dynamics. Investors with long time horizons and adequate liquidity can earn substantial returns by absorbing forced sales, but they require deep discounts to compensate for execution risk and uncertainty about when prices will recover.
- Mathematical Formulation: `Buy when deviation < -0.08; sell when deviation > +0.10`. The asymmetric thresholds (-8% entry, +10% exit) reflect the recovery premium that contrarian investors require.
- Empirical Evidence: Post-crisis studies of 1997 Asian markets show that investors who entered Thai, Korean, and Indonesian equity markets at 40-60% discounts in Q1 1998 earned returns of 100-200% over the following 3 years (Brunnermeier, 2009; consistent with fundamentals-driven recovery).
- Relevance to This Investor: `oversold_threshold = -0.08` (8% below F) represents the minimum discount ValueContrarian requires before entering; `overbought_threshold = +0.10` (+10% above F) is the exit point capturing the post-crisis recovery premium.

**Limits to Arbitrage and Position Building**:
- Theory / Study: Patient Capital and Crisis Arbitrage
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Fundamental-value investors face capital constraints that prevent them from deploying unlimited capital into deep discounts. ValueContrarian's `buy_ratio = 0.20` reflects this constraint -- it deploys cautiously to avoid overcommitting before the crisis floor is established.
- Empirical Evidence: During 1997 Asian crisis, even well-capitalised funds deployed capital gradually across multiple rounds (weeks) rather than in a single decisive entry -- consistent with the 20% per-round deployment.
- Relevance to This Investor: Conservative capital deployment (20% per round) ensures ValueContrarian does not exhaust its buying power in the early crisis phase before prices bottom.

#### 4.4.3  Design Purpose and Activation Scenarios

Purpose: ValueContrarian provides the second floor (deeper than IMFRescuer) and eventual recovery-phase selling that normalises prices after the crisis.

Activation Scenarios:
- Deep crisis (deviation < -0.08): Buys; provides incremental buying support deeper in the crisis.
- Recovery overshoot (deviation > +0.10): Sells; prevents post-crisis overvaluation.
- Between thresholds (-0.08 to +0.10): Holds.

Market Contribution: **Stabilising** -- deepens the floor below IMFRescuer; provides the second rescue layer. Also provides recovery-phase selling that prevents over-correction.

#### 4.4.4  Behavioral Framework

- Trigger: `deviation < -0.08` (buy) or `deviation > +0.10` (sell)
- Sizing: `0.20 x cash / price` (buy) or `0.20 x position` (sell)
- Parameters: `oversold_threshold = -0.08` (Brunnermeier, 2009: private buyers enter at 8-15% below fundamental); `overbought_threshold = +0.10`

#### 4.4.5  Decision Process Walkthrough

```
Given:  deviation = -0.10,  cash = $1,000,000,  price = 90.0

Check: -0.10 < -0.08 -> buy condition
Q* = 0.20 x 1,000,000 / 90.0 = 2,222 shares

Decision: buy 2,222 shares; adds +$88.9 upward price pressure (at lambda = 0.04)
```

#### 4.4.6  Worked Numerical Example

```
Recovery phase: deviation = +0.11,  price = 111.0,  position = 3,200 shares
Check: +0.11 > +0.10 -> sell condition
Q* = 0.20 x 3,200 = 640 shares

Decision: sell 640 shares; prevents post-crisis overvaluation above fundamental + 10%
```

#### 4.4.7  Academic References

| # | Citation                                                                                                                                              | Notes                                                      |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch. *JEP*, 23(1), 77-100. https://doi.org/10.1257/jep.23.1.77                    | Grounds deep discount requirement for private value buyers |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Grounds 20% per-round capital deployment constraint        |

---

## Source Docstring Excerpts

### Rule / `ValueContrarian`

```text
Buys oversold regional assets when contagion pushes prices below fundamentals.

Theory: simulation-bases.md Section 4.4 -- ValueContrarian
Theoretical Basis: Contrarian crisis investing (Radelet & Sachs, 1998 baseline)
Market Role: stabilizing

Strategy:
    - When deviation < oversold_threshold: buy buy_ratio of cash
    - When deviation > overbought_threshold: sell sell_ratio of position
See simulation-bases.md Section 4.4.4.3 for mathematical model.
```

### LLM / `LLMValueContrarian`

```text
LLM-driven value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMValueContrarian`

```text
RuleLLM value contrarian with explicit oversold/overbought threshold rules. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMValueContrarian`

```text
RAG-augmented value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.
```
