# LUNACollapse / Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LUNACollapse |
| Agent type | Arbitrageur |
| Canonical class | `Arbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A trader exploiting UST/LUNA-style arbitrage, amplifying the spiral when the gap is large.

## Financial Theory / Theoretical Basis

### Rule / `Arbitrageur`
- Theory: simulation-bases.md Section 4.2 -- Arbitrageur
- Theoretical Basis: Algorithmic stablecoin arbitrage mechanism

### LLM / `LLMArbitrageur`
- LLM-driven arbitrage amplifier. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMArbitrageur`
- RuleLLM arbitrage amplifier. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMArbitrageur`
- RAG arbitrage amplifier. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| arb_threshold | Rule: `0.02`<br>LLM: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | LLM, Rag, Rule, RuleLLM |
| base_size | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LUNACollapse.LLM.prompts:LLM_ARBITRAGEUR_PROMPT', 'user_message': 'examples.LUNACollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_ARBITRAGEUR_PROMPT', 'user_message': 'examples.LUNACollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LUNACollapse.Rag.prompts:RAG_ARBITRAGEUR_PROMPT', 'user_message': 'examples.LUNACollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | arbitrageur | Arbitrageur | `Arbitrageur` | 2 | `examples/LUNACollapse/Rule/players.py` |
| LLM | arbitrageur | Arbitrageur | `LLMArbitrageur` | 2 | `examples/LUNACollapse/LLM/players.py` |
| RuleLLM | arbitrageur | Arbitrageur | `RuleLLMArbitrageur` | 2 | `examples/LUNACollapse/RuleLLM/players.py` |
| Rag | arbitrageur | Arbitrageur | `RagLLMArbitrageur` | 2 | `examples/LUNACollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 Arbitrageur

**Summary**: A trader exploiting UST/LUNA-style arbitrage, amplifying the spiral
when the gap is large.

**Theoretical and Empirical Basis**: Arbitrage is intended to stabilize an
algorithmic peg but can increase base-token pressure during runs.

**Design Purpose**: Encode the arbitrage channel that scales with mispricing.

**Behavioral Framework**: Trades when absolute deviation exceeds
`arb_threshold`.

**Decision Process**: Quantity scales with `abs(deviation) * 100000`, capped at
5000 and constrained by cash or position.

**Worked Numerical Example**: With `deviation = -0.08`, target quantity is 5000;
the arbitrageur buys if cash allows.

**Academic References**: Klages-Mundt et al. (2020); Terra/LUNA postmortem
analyses.

## Source Docstring Excerpts

### Rule / `Arbitrageur`

```text
Arbitrage between stablecoin and base token amplifies the death spiral.

Theory: simulation-bases.md Section 4.2 -- Arbitrageur
Theoretical Basis: Algorithmic stablecoin arbitrage mechanism
Market Role: destabilizing -- arbitrage activity amplifies price collapse
```

### LLM / `LLMArbitrageur`

```text
LLM-driven arbitrage amplifier. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMArbitrageur`

```text
RuleLLM arbitrage amplifier. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMArbitrageur`

```text
RAG arbitrage amplifier. Theory: simulation-bases.md Section 4.2.
```
