# HindsightBias / Contrarian Skeptic

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HindsightBias |
| Agent type | Contrarian Skeptic |
| Canonical class | `ContrarianSkeptic` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Roese & Vohs (2012) narrative skepticism -- the agent resists post-hoc consensus narratives and trades against deviations with a higher threshold, acting as a second rational stabilizer at |deviation| > 0.05.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianSkeptic`
- Theory: simulation-bases.md Section 4.4 -- ContrarianSkeptic
- Theoretical basis: Narrative skepticism (Roese & Vohs, 2012).

### LLM / `LLMContrarianSkeptic`
- LLM-driven ContrarianSkeptic: distrusts post-hoc narratives, takes contrarian positions. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMContrarianSkeptic`
- RuleLLM ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMContrarianSkeptic`
- RAG ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.

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
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HindsightBias.LLM.prompts:LLM_CONTRARIANSKEPTIC_PROMPT', 'user_message': 'examples.HindsightBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_CONTRARIANSKEPTIC_PROMPT', 'user_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.HindsightBias.Rag.prompts:RAG_CONTRARIANSKEPTIC_PROMPT', 'user_message': 'examples.HindsightBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `3000` | Rule |
| skepticism_level | Rule: `0.6`<br>LLM: `0.6`<br>RuleLLM: `0.6`<br>Rag: `0.6` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarianskeptic | ContrarianSkeptic | `ContrarianSkeptic` | 1 | `examples/HindsightBias/Rule/players.py` |
| LLM | contrarianskeptic | ContrarianSkeptic | `LLMContrarianSkeptic` | 1 | `examples/HindsightBias/LLM/players.py` |
| RuleLLM | contrarianskeptic | ContrarianSkeptic | `RuleLLMContrarianSkeptic` | 1 | `examples/HindsightBias/RuleLLM/players.py` |
| Rag | contrarianskeptic | ContrarianSkeptic | `RagLLMContrarianSkeptic` | 1 | `examples/HindsightBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ContrarianSkeptic

**Summary**: Implements Roese & Vohs (2012) narrative skepticism -- the agent resists post-hoc consensus narratives and trades against deviations with a higher threshold, acting as a second rational stabilizer at |deviation| > 0.05.

**Theoretical and Empirical Basis**: Roese, N.J. & Vohs, K.D. (2012). *Perspectives on Psychological Science*, 7(5), 411-426. `doi:10.1177/1745691612454303`; De Bondt & Thaler (1985). `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Encode skepticism of "obvious in hindsight" narratives -- the agent refuses to be swept into consensus momentum and instead acts on the fundamental signal alone, providing a second correction force alongside ProcessEvaluator.

**Behavioral Framework**:

| Decision Variable  | Logic                                                  | Formula                                                             |
|--------------------|--------------------------------------------------------|---------------------------------------------------------------------|
| Activation         | Same threshold as ProcessEvaluator                     | `abs(deviation) > 0.05`                                             |
| Direction          | Contrarian -- trades against deviation                  | buy if dev < -0.05; sell if dev > 0.05                              |
| Quantity           | Scaled by deviation and skepticism parameter | `min(max_order, int(abs(dev) x quantity_scale x skepticism_level))` |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.05` -- if not, hold
3. If deviation > 0.05: narrative skeptic concludes "this isn't as obvious as market thinks" -> sell order
4. If deviation < -0.05: similarly -> buy order
5. Quantity = `min(max_order, int(abs(dev) x quantity_scale x skepticism_level))`

**Worked Example**: fundamental = 100, price = 107, deviation = +0.07, skepticism_level = 0.6, quantity_scale = 3000, max_order = 500 -> qty = min(500, int(0.07 x 3000 x 0.6)) = 126 shares sell order.

**Academic References**: `simulation-bases.md Section 2 Theory 3`; `doi:10.1177/1745691612454303`; Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x`

## Source Docstring Excerpts

### Rule / `ContrarianSkeptic`

```text
Theory: simulation-bases.md Section 4.4 -- ContrarianSkeptic

Theoretical basis: Narrative skepticism (Roese & Vohs, 2012).
Skeptic of post-hoc narratives, trades against hindsight-driven consensus.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMContrarianSkeptic`

```text
LLM-driven ContrarianSkeptic: distrusts post-hoc narratives, takes contrarian positions. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMContrarianSkeptic`

```text
RuleLLM ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMContrarianSkeptic`

```text
RAG ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.
```
