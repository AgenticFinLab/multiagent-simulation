# HindsightBias / Outcome Learner

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HindsightBias |
| Agent type | Outcome Learner |
| Canonical class | `OutcomeLearner` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Fischhoff & Beyth (1975) outcome bias and Odean (1998) selective attribution -- the agent attributes gains to skill and losses to bad luck, producing asymmetric momentum that is stronger in bull phases.

## Financial Theory / Theoretical Basis

### Rule / `OutcomeLearner`
- Theory: simulation-bases.md Section 4.2 -- OutcomeLearner
- Theoretical basis: Outcome bias (Fischhoff & Beyth, 1975).

### LLM / `LLMOutcomeLearner`
- LLM-driven OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMOutcomeLearner`
- RuleLLM OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMOutcomeLearner`
- RAG OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| activation_threshold | Rule: `0.02` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| failure_discount | Rule: `1.0` | Rule |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HindsightBias.LLM.prompts:LLM_OUTCOMELEARNER_PROMPT', 'user_message': 'examples.HindsightBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_OUTCOMELEARNER_PROMPT', 'user_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.HindsightBias.Rag.prompts:RAG_OUTCOMELEARNER_PROMPT', 'user_message': 'examples.HindsightBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000` | Rule |
| success_attribution | Rule: `1.3`<br>LLM: `1.3`<br>RuleLLM: `1.3`<br>Rag: `1.3` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | outcomelearner | OutcomeLearner | `OutcomeLearner` | 3 | `examples/HindsightBias/Rule/players.py` |
| LLM | outcomelearner | OutcomeLearner | `LLMOutcomeLearner` | 3 | `examples/HindsightBias/LLM/players.py` |
| RuleLLM | outcomelearner | OutcomeLearner | `RuleLLMOutcomeLearner` | 3 | `examples/HindsightBias/RuleLLM/players.py` |
| Rag | outcomelearner | OutcomeLearner | `RagLLMOutcomeLearner` | 3 | `examples/HindsightBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 OutcomeLearner

**Summary**: Implements Fischhoff & Beyth (1975) outcome bias and Odean (1998) selective attribution -- the agent attributes gains to skill and losses to bad luck, producing asymmetric momentum that is stronger in bull phases.

**Theoretical and Empirical Basis**: Fischhoff & Beyth (1975). "'I Knew It Would Happen'." *OBHP*, 13(1), 1-16. `doi:10.1016/0030-5073(75)90002-1`; Odean (1998). `doi:10.1111/0022-1082.00259`

**Design Purpose**: Encode selective attribution -- `success_attribution` scales up confidence after gains, `failure_discount` reduces the downward update after losses, creating an asymmetric confidence trajectory that generates bull-phase momentum dominance (OBI > 1.0).

**Behavioral Framework**:

| Decision Variable   | Logic                                                    | Formula                                                                   |
|---------------------|----------------------------------------------------------|---------------------------------------------------------------------------|
| Activation          | Trades when deviation crosses threshold                  | `abs(deviation) > 0.02`                                                   |
| Direction           | Follows deviation (same as HindsightOverconfident)       | buy if dev > 0; sell if dev < 0                                           |
| Quantity            | Scaled by deviation magnitude and attribution parameters | `min(800, int(abs(dev) x 5000 x success_attribution x failure_discount))` |
| Cash constraint     | Cannot exceed available cash                             | `buy_qty = min(qty, int(cash / price))`                                   |
| Position constraint | Cannot sell beyond held shares                           | `sell_qty = min(qty, max(position, 0))`                                   |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.02` -- if not, hold
3. If deviation > 0: success attribution active -> buy with amplified confidence
4. If deviation < 0: failure discount reduces downward update -> still sells but with smaller position
5. Quantity = `min(800, int(abs(dev) x 5000 x success_attribution x failure_discount))`

**Worked Example**: fundamental = 100, price = 103.5, deviation = +0.035, success_attribution = 1.5, failure_discount = 0.5 -> qty = min(800, int(0.035 x 5000 x 1.5)) = min(800, 262) = 262 shares buy order. (In loss round: qty = min(800, int(0.035 x 5000 x 0.5)) = min(800, 87) = 87 shares sell order.)

**Academic References**: `simulation-bases.md Section 2 Theory 2`; `doi:10.1016/0030-5073(75)90002-1`; Barber & Odean (2000) `doi:10.1111/0022-1082.00226`

**Note**: Section 4.1 and Section 4.2 share the same directional rule, but branch-current defaults differentiate their scale: Section 4.1 uses `hindsight_inflation = 1.5`, while Section 4.2 uses `success_attribution = 1.3` for positive deviations and `failure_discount = 1.0` for negative deviations.

## Source Docstring Excerpts

### Rule / `OutcomeLearner`

```text
Theory: simulation-bases.md Section 4.2 -- OutcomeLearner

Theoretical basis: Outcome bias (Fischhoff & Beyth, 1975).
Learns only from outcomes not process, misattributes skill to luck.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMOutcomeLearner`

```text
LLM-driven OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMOutcomeLearner`

```text
RuleLLM OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMOutcomeLearner`

```text
RAG OutcomeLearner: judges decisions by outcomes, not process. Theory: simulation-bases.md Section 4.2.
```
