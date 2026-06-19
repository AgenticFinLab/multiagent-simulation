# RepresentativenessBias / Contrarian Statistical

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RepresentativenessBias |
| Agent type | Contrarian Statistical |
| Canonical class | `ContrarianStatistical` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A stabilizing arbitrageur that trades against pattern-driven mispricing. It is inactive for small deviations but corrects large biased pressure.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianStatistical`
- Theory: simulation-bases.md Section 4.4 -- ContrarianStatistical
- Theoretical basis: statistical arbitrage against biased beliefs.

### LLM / `LLMContrarianStatistical`
- LLM-driven contrarian arbitrageur -- exploits biased mispricing. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMContrarianStatistical`
- RuleLLM contrarian arbitrageur -- rule-guided correction. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMContrarianStatistical`
- RagLLM contrarian arbitrageur -- correction with retrieved context. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| contrarian_threshold | Rule: `0.04`<br>LLM: `0.04`<br>RuleLLM: `0.04`<br>Rag: `0.04` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_CONTRARIAN_STATISTICAL_PROMPT', 'user_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_CONTRARIAN_STATISTICAL_SYS', 'user_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.RepresentativenessBias.Rag.prompts:RULELLM_CONTRARIAN_STATISTICAL_SYS', 'user_message': 'examples.RepresentativenessBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| position_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarianstatistical | ContrarianStatistical | `ContrarianStatistical` | 1 | `examples/RepresentativenessBias/Rule/players.py` |
| LLM | contrarianstatistical | ContrarianStatistical | `LLMContrarianStatistical` | 1 | `examples/RepresentativenessBias/LLM/players.py` |
| RuleLLM | contrarianstatistical | ContrarianStatistical | `RuleLLMContrarianStatistical` | 1 | `examples/RepresentativenessBias/RuleLLM/players.py` |
| Rag | contrarianstatistical | ContrarianStatistical | `RagLLMContrarianStatistical` | 1 | `examples/RepresentativenessBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ContrarianStatistical

**Summary**: A stabilizing arbitrageur that trades against pattern-driven
mispricing. It is inactive for small deviations but corrects large biased
pressure.

**Theoretical and Empirical Foundation**: Based on Barberis et al. (1998) and
limits-to-arbitrage logic in Shleifer (2000).

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.05`; buys underpricing and sells overpricing.

**Behavioral Framework**: `contrarian_threshold` and `position_size` define
when correction starts and how much capital can be committed.

**Decision Process Walkthrough**: Detect mispricing, take the opposite side of
representativeness-driven order flow, and cap quantity by cash/position.

**Worked Numerical Example**: Price 108 and fundamental 100 gives deviation
0.08. Quantity is `min(500, int(0.08 * 3000)) = 240`; the agent sells.

**Academic References**: Barberis et al. (1998); Shleifer (2000).

## Source Docstring Excerpts

### Rule / `ContrarianStatistical`

```text
Trades against pattern-matching mispricing and base-rate deviations.

Theory: simulation-bases.md Section 4.4 -- ContrarianStatistical
Theoretical basis: statistical arbitrage against biased beliefs.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMContrarianStatistical`

```text
LLM-driven contrarian arbitrageur -- exploits biased mispricing. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMContrarianStatistical`

```text
RuleLLM contrarian arbitrageur -- rule-guided correction. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMContrarianStatistical`

```text
RagLLM contrarian arbitrageur -- correction with retrieved context. Theory: simulation-bases.md Section 4.4.
```
