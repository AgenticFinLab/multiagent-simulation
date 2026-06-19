# OverconfidenceBias / Contrarian Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | OverconfidenceBias |
| Agent type | Contrarian Investor |
| Canonical class | `ContrarianInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: ContrarianInvestor fades extreme overconfident moves. It is a stabilizing agent that opposes large deviations from fundamental value. 2. **Theoretical and Empirical Foundation**: De Bondt and Thaler (1985) support the overreaction-correction mechanism. 3. **Design Purpose and Activation Scenarios**: Activates only when `abs(deviation) > contrarian_threshold`. 4. **Behavioral Framework**: Sells overvaluation and buys undervaluation, with size capped by `base_size`, cash, and inventory. 5. **Decision Process Walkthrough**: Wait for a large deviation, trade against the direction, and provide mean-reversion pressure. 6. **Worked Numerical Example**: A 6% overvaluation with threshold 4% triggers a sell order up to the configured base size. 7. **Academic References**: De Bondt and Thaler (1985).

## Financial Theory / Theoretical Basis

### Rule / `ContrarianInvestor`
- Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.

### LLM / `LLMContrarianInvestor`
- Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.

### RuleLLM / `RuleLLMContrarianInvestor`
- Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.

### Rag / `RagLLMContrarianInvestor`
- Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
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
| llm | LLM: `{'sys_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_CONTRARIAN_INVESTOR_PROMPT', 'user_message': 'examples.OverconfidenceBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_CONTRARIAN_INVESTOR_SYS', 'user_message': 'examples.OverconfidenceBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.OverconfidenceBias.Rag.prompts:RULELLM_CONTRARIAN_INVESTOR_SYS', 'user_message': 'examples.OverconfidenceBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarianinvestor | ContrarianInvestor | `ContrarianInvestor` | 1 | `examples/OverconfidenceBias/Rule/players.py` |
| LLM | contrarianinvestor | ContrarianInvestor | `LLMContrarianInvestor` | 1 | `examples/OverconfidenceBias/LLM/players.py` |
| RuleLLM | contrarianinvestor | ContrarianInvestor | `RuleLLMContrarianInvestor` | 1 | `examples/OverconfidenceBias/RuleLLM/players.py` |
| Rag | contrarianinvestor | ContrarianInvestor | `RagLLMContrarianInvestor` | 1 | `examples/OverconfidenceBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ContrarianInvestor

1. **Summary**: ContrarianInvestor fades extreme overconfident moves. It is a
stabilizing agent that opposes large deviations from fundamental value.
2. **Theoretical and Empirical Foundation**: De Bondt and Thaler (1985) support
the overreaction-correction mechanism.
3. **Design Purpose and Activation Scenarios**: Activates only when
`abs(deviation) > contrarian_threshold`.
4. **Behavioral Framework**: Sells overvaluation and buys undervaluation, with
size capped by `base_size`, cash, and inventory.
5. **Decision Process Walkthrough**: Wait for a large deviation, trade against
the direction, and provide mean-reversion pressure.
6. **Worked Numerical Example**: A 6% overvaluation with threshold 4% triggers a
sell order up to the configured base size.
7. **Academic References**: De Bondt and Thaler (1985).

## Source Docstring Excerpts

### Rule / `ContrarianInvestor`

```text
Trades against overconfident moves.

Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.
Strategy specification: simulation-bases.md Section 4.4.4.
```

### LLM / `LLMContrarianInvestor`

```text
LLM-driven ContrarianInvestor.

Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.
Strategy specification: simulation-bases.md Section 4.4.4.
```

### RuleLLM / `RuleLLMContrarianInvestor`

```text
Hybrid: ContrarianInvestor rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.
Strategy specification: simulation-bases.md Section 4.4.4.
```

### Rag / `RagLLMContrarianInvestor`

```text
RAG-augmented ContrarianInvestor.

Theoretical basis: simulation-bases.md Section 4.4 -- ContrarianInvestor.
Strategy specification: simulation-bases.md Section 4.4.4.
```
