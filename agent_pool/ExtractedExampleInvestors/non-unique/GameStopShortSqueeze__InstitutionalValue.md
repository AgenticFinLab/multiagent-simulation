# GameStopShortSqueeze / Institutional Value

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GameStopShortSqueeze |
| Agent type | Institutional Value |
| Canonical class | `InstitutionalValue` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`InstitutionalValue` represents a fundamental investor that sells into extreme overvaluation. It is the main stabilizing seller, but its inventory is finite.

## Financial Theory / Theoretical Basis

### Rule / `InstitutionalValue`
- Theory: simulation-bases.md Section 4.4 -- InstitutionalValue
- Theoretical basis: Fundamental valuation (Shleifer & Vishny, 1997).

### LLM / `LLMInstitutionalValue`
- LLM-driven institutional value investor. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMInstitutionalValue`
- RuleLLM-driven institutional value investor. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMInstitutionalValue`
- RagLLM-driven institutional value investor: trades on fundamentals, fades the squeeze. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400` | Rule |
| buy_threshold | Rule: `-0.1` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `2000`<br>LLM: `2000`<br>RuleLLM: `2000`<br>Rag: `2000` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `20.0`<br>LLM: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_INSTITUTIONAL_VALUE_SYS', 'user_message': 'examples.GameStopShortSqueeze.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_INSTITUTIONAL_VALUE_SYS', 'user_message': 'examples.GameStopShortSqueeze.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAGLLM_INSTITUTIONAL_VALUE_SYS', 'user_message': 'examples.GameStopShortSqueeze.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_threshold | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | institutionalvalue | InstitutionalValue | `InstitutionalValue` | 1 | `examples/GameStopShortSqueeze/Rule/players.py` |
| LLM | institutionalvalue | InstitutionalValue | `LLMInstitutionalValue` | 1 | `examples/GameStopShortSqueeze/LLM/players.py` |
| RuleLLM | institutionalvalue | InstitutionalValue | `RuleLLMInstitutionalValue` | 1 | `examples/GameStopShortSqueeze/RuleLLM/players.py` |
| Rag | institutionalvalue | InstitutionalValue | `RagLLMInstitutionalValue` | 1 | `examples/GameStopShortSqueeze/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 InstitutionalValue

#### Section 4.4.1 Summary

`InstitutionalValue` represents a fundamental investor that sells into extreme overvaluation. It is the main stabilizing seller, but its inventory is finite.

#### Section 4.4.2 Theoretical and Empirical Foundation

The basis is fundamental-value investing and Shleifer and Vishny (1997) on limits to arbitrage: rational sellers can be overwhelmed by speculative pressure and capital constraints.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation > sell_threshold` and position > 0 | sell | provides valuation anchor | Section 2 Theory 1 |
| otherwise | hold | overvaluation not high enough or inventory exhausted | Section 2 Theory 1 |

#### Section 4.4.4 Behavioral Framework

```
if deviation > sell_threshold:
    sell min(1000, position)
else:
    hold
```

#### Section 4.4.5 Decision Process Walkthrough

With deviation 40% and `sell_threshold = 0.30`, the institutional value investor sells because price is far above fundamental.

#### Section 4.4.6 Worked Numerical Example

With 2,000 shares, the first sell order is capped at 1,000 shares.

#### Section 4.4.7 Academic References

Shleifer & Vishny (1997); Graham and Dodd value-investing tradition.

## Source Docstring Excerpts

### Rule / `InstitutionalValue`

```text
Theory: simulation-bases.md Section 4.4 -- InstitutionalValue

Theoretical basis: Fundamental valuation (Shleifer & Vishny, 1997).
Fundamental value investor: sells aggressively when price is extremely overvalued.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMInstitutionalValue`

```text
LLM-driven institutional value investor. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMInstitutionalValue`

```text
RuleLLM-driven institutional value investor. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMInstitutionalValue`

```text
RagLLM-driven institutional value investor: trades on fundamentals, fades the squeeze. Theory: simulation-bases.md Section 4.4.
```
