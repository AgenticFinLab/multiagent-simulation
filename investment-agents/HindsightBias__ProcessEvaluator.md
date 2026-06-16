# HindsightBias / Process Evaluator

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HindsightBias |
| Agent type | Process Evaluator |
| Canonical class | `ProcessEvaluator` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Roese & Vohs (2012) process-oriented rationality -- the agent evaluates decisions on process quality independent of outcome narratives, acting as a contrarian stabilizer at larger deviations (|deviation| > 0.05).

## Financial Theory / Theoretical Basis

### Rule / `ProcessEvaluator`
- Theory: simulation-bases.md Section 4.3 -- ProcessEvaluator
- Theoretical basis: Process-oriented rationality (Roese & Vohs, 2012).

### LLM / `LLMProcessEvaluator`
- LLM-driven ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMProcessEvaluator`
- RuleLLM ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMProcessEvaluator`
- RAG ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| activation_threshold | Rule: `0.05` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HindsightBias.LLM.prompts:LLM_PROCESSEVALUATOR_PROMPT', 'user_message': 'examples.HindsightBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_PROCESSEVALUATOR_PROMPT', 'user_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.HindsightBias.Rag.prompts:RAG_PROCESSEVALUATOR_PROMPT', 'user_message': 'examples.HindsightBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| outcome_weight | Rule: `1.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| process_weight | Rule: `0.8`<br>LLM: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | LLM, Rag, Rule, RuleLLM |
| quantity_scale | Rule: `3000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | processevaluator | ProcessEvaluator | `ProcessEvaluator` | 2 | `examples/HindsightBias/Rule/players.py` |
| LLM | processevaluator | ProcessEvaluator | `LLMProcessEvaluator` | 2 | `examples/HindsightBias/LLM/players.py` |
| RuleLLM | processevaluator | ProcessEvaluator | `RuleLLMProcessEvaluator` | 2 | `examples/HindsightBias/RuleLLM/players.py` |
| Rag | processevaluator | ProcessEvaluator | `RagLLMProcessEvaluator` | 2 | `examples/HindsightBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 ProcessEvaluator

**Summary**: Implements Roese & Vohs (2012) process-oriented rationality -- the agent evaluates decisions on process quality independent of outcome narratives, acting as a contrarian stabilizer at larger deviations (|deviation| > 0.05).

**Theoretical and Empirical Basis**: Roese, N.J. & Vohs, K.D. (2012). "Hindsight Bias." *Perspectives on Psychological Science*, 7(5), 411-426. `doi:10.1177/1745691612454303`; Shleifer & Vishny (1997). `doi:10.1111/j.1540-6261.1997.tb03807.x`

**Design Purpose**: Encode the rational baseline that focuses on process rather than outcome -- when deviation exceeds 0.05, the agent concludes the process-based analysis indicates mispricing regardless of whether the narrative makes the move seem "obvious", acting as a contrarian correction force.

**Behavioral Framework**:

| Decision Variable | Logic                                                               | Formula                                                            |
|-------------------|---------------------------------------------------------------------|--------------------------------------------------------------------|
| Activation        | Higher threshold than biased agents -- requires large mispricing     | `abs(deviation) > 0.05`                                            |
| Direction         | Contrarian -- trades against deviation                               | buy if dev < -0.05; sell if dev > 0.05                             |
| Quantity          | Scaled by deviation magnitude and process/outcome weight parameters | `min(500, int(abs(dev) x 3000 x process_weight x outcome_weight))` |
| Cash constraint   | Cannot exceed available cash                                        | `buy_qty = min(qty, int(cash / price))`                            |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.05` -- if not, hold
3. If deviation > 0.05: price above fundamental -> sell order (correcting overpricing)
4. If deviation < -0.05: price below fundamental -> buy order (correcting underpricing)
5. Quantity = `min(500, int(abs(dev) x 3000 x process_weight x outcome_weight))`

**Worked Example**: fundamental = 100, price = 106, deviation = +0.06, process_weight = 1.0, outcome_weight = 1.0 -> qty = min(500, int(0.06 x 3000 x 1.0)) = min(500, 180) = 180 shares sell order.

**Academic References**: `simulation-bases.md Section 2 Theory 3`; `doi:10.1177/1745691612454303`; Pontiff (2006) `doi:10.1016/j.jfineco.2005.09.001`

## Source Docstring Excerpts

### Rule / `ProcessEvaluator`

```text
Theory: simulation-bases.md Section 4.3 -- ProcessEvaluator

Theoretical basis: Process-oriented rationality (Roese & Vohs, 2012).
Evaluates decisions by process quality, resists hindsight distortion.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMProcessEvaluator`

```text
LLM-driven ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMProcessEvaluator`

```text
RuleLLM ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMProcessEvaluator`

```text
RAG ProcessEvaluator: evaluates decisions by process quality. Theory: simulation-bases.md Section 4.3.
```
