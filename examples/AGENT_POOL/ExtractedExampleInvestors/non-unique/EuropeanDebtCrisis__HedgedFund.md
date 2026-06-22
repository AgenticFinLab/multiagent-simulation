# EuropeanDebtCrisis / Hedged Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EuropeanDebtCrisis |
| Agent type | Hedged Fund |
| Canonical class | `HedgedFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `HedgedFund` is a relative-value arbitrageur that buys undervalued peripheral bonds and sells when the spread closes. It partially stabilizes the market but is bounded by capital and timing risk.

## Financial Theory / Theoretical Basis

### Rule / `HedgedFund`
- Theory: simulation-bases.md Section 4.5 -- HedgedFund
- Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits

### LLM / `LLMHedgedFund`
- LLM-driven hedge fund -- relative-value spread arbitrage via LLM reasoning. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMHedgedFund`
- RuleLLM hedge fund -- spread arbitrage rules with LLM relative-value reasoning. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMHedgedFund`
- RAG-augmented hedge fund -- relative-value spread arbitrage with crisis literature. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| core_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.07` | Rule |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_HEDGED_FUND_SYS', 'user_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_HEDGED_FUND_SYS', 'user_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_HEDGED_FUND_SYS', 'user_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| spread_buy_threshold | LLM: `7.0`<br>RuleLLM: `7.0`<br>Rag: `7.0` | LLM, Rag, RuleLLM |
| spread_exit_threshold | LLM: `3.0`<br>RuleLLM: `3.0`<br>Rag: `3.0` | LLM, Rag, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hedgedfund | HedgedFund | `HedgedFund` | 1 | `examples/EuropeanDebtCrisis/Rule/players.py` |
| LLM | hedgedfund | HedgedFund | `LLMHedgedFund` | 1 | `examples/EuropeanDebtCrisis/LLM/players.py` |
| RuleLLM | hedgedfund | HedgedFund | `RuleLLMHedgedFund` | 1 | `examples/EuropeanDebtCrisis/RuleLLM/players.py` |
| Rag | hedgedfund | HedgedFund | `RagLLMHedgedFund` | 1 | `examples/EuropeanDebtCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 HedgedFund

#### Section 4.5.1 Summary

The `HedgedFund` is a relative-value arbitrageur that buys undervalued peripheral bonds and sells when the spread closes. It partially stabilizes the market but is bounded by capital and timing risk.

#### Section 4.5.2 Theoretical and Empirical Foundation

The basis is limits to arbitrage (Section 2.5). Shleifer and Vishny explain why rational arbitrage is not infinite during stress; Brunnermeier and Pedersen explain the funding-liquidity constraint.

#### Section 4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < -entry_threshold` | buy | stabilizes undervalued peripheral bond | Section 2.5 |
| `deviation > entry_threshold` | sell | exits after spread compression | Section 2.5 |

#### Section 4.5.4 Behavioral Framework

```
if deviation < -entry_threshold: buy min(500, cash / price)
elif deviation > entry_threshold: sell min(500, position)
else: hold
```

#### Section 4.5.5 Decision Process Walkthrough

At deviation -18% with `entry_threshold = 7%`, the hedge fund buys because the bond is cheap relative to fundamental value.

#### Section 4.5.6 Worked Numerical Example

With cash 1,000,000 and price 82, affordable quantity is above 500, so buy quantity is 500.

#### Section 4.5.7 Academic References

Shleifer & Vishny (1997); Brunnermeier & Pedersen (2009).

## Source Docstring Excerpts

### Rule / `HedgedFund`

```text
Takes relative value positions between core and periphery bonds.

Theory: simulation-bases.md Section 4.5 -- HedgedFund
Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
spread dislocations but constrained by margin calls and fund redemptions.
See simulation-bases.md Section 4.5 for mathematical model.
```

### LLM / `LLMHedgedFund`

```text
LLM-driven hedge fund -- relative-value spread arbitrage via LLM reasoning. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMHedgedFund`

```text
RuleLLM hedge fund -- spread arbitrage rules with LLM relative-value reasoning. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMHedgedFund`

```text
RAG-augmented hedge fund -- relative-value spread arbitrage with crisis literature. Theory: simulation-bases.md Section 4.5.
```
