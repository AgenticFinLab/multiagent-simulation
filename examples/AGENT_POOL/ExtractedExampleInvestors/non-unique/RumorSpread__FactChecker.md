# RumorSpread / Fact Checker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RumorSpread |
| Agent type | Fact Checker |
| Canonical class | `FactChecker` |
| Catalog category | Non-financial/social-propagation participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Professional verifier that actively debunks false or distorted claims. **Theoretical and Empirical Foundation**: Active rumor denial and misinformation correction research. **Design Purpose and Activation Scenarios**: Corrects when public belief is large enough to matter, with stronger action when distortion makes errors easier to identify. **Behavioral Framework**: Belief moves strongly toward truth; correction intensity equals `fact_check_strength * (1 - my_belief) * (1 + distortion_sensitivity * distortion) * credibility_discount`. **Decision Process Walkthrough**: If environment belief exceeds `0.3`, compute discounted correction; otherwise ignore. **Worked Numerical Example**: Strength `0.8`, belief `0.1`, distortion `0.5`, sensitivity `0.5`, and discount `0.6` yield `0.54`. **Academic References**: DiFonzo and Bordia (2007); Lewandowsky et al. (2012).

## Financial Theory / Theoretical Basis

### Rule / `FactChecker`
- Theory: simulation-bases.md Section 4.4 -- FactChecker
- Theory: DiFonzo & Bordia (2004, 2007) -- Rumor correction and denial
- corrections travel slower than rumors (the "implied truth effect").
- Behavior:
- - Very low credulity: requires verified evidence
- - Actively corrects misinformation with high credibility
- - Corrections are less contagious than rumors (slower spread)
- - More effective when distortion is high (obvious falsehoods)
- Effect: STRONGLY STABILIZING -- Primary correction mechanism
- Formula:

### LLM / `LLMFactChecker`
- Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMFactChecker`
- Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMFactChecker`
- Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| credibility_discount | Rule: `0.6` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| distortion_sensitivity | Rule: `0.5` | Rule |
| fact_check_strength | Rule: `0.8` | Rule |
| initial_belief | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| initial_credibility | Rule: `0.9`<br>LLM: `0.9`<br>RuleLLM: `0.9`<br>Rag: `0.9` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RumorSpread.LLM.prompts:LLM_FACTCHECKER_SYS', 'user_message': 'examples.RumorSpread.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_FACTCHECKER_SYS', 'user_message': 'examples.RumorSpread.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.RumorSpread.Rag.prompts:RAG_FACTCHECKER_SYS', 'user_message': 'examples.RumorSpread.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fact_checker | Fact Checker | `FactChecker` | 2 | `examples/RumorSpread/Rule/players.py` |
| LLM | llm_fact_checker | LLM Fact Checker | `LLMFactChecker` | 2 | `examples/RumorSpread/LLM/players.py` |
| RuleLLM | rulellm_fact_checker | RuleLLM Fact Checker | `RuleLLMFactChecker` | 2 | `examples/RumorSpread/RuleLLM/players.py` |
| Rag | ragllm_fact_checker | RAG Fact Checker | `RagLLMFactChecker` | 2 | `examples/RumorSpread/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 FactChecker

**Summary**: Professional verifier that actively debunks false or distorted
claims.
**Theoretical and Empirical Foundation**: Active rumor denial and misinformation
correction research.
**Design Purpose and Activation Scenarios**: Corrects when public belief is
large enough to matter, with stronger action when distortion makes errors easier
to identify.
**Behavioral Framework**: Belief moves strongly toward truth; correction
intensity equals `fact_check_strength * (1 - my_belief) * (1 +
distortion_sensitivity * distortion) * credibility_discount`.
**Decision Process Walkthrough**: If environment belief exceeds `0.3`, compute
discounted correction; otherwise ignore.
**Worked Numerical Example**: Strength `0.8`, belief `0.1`, distortion `0.5`,
sensitivity `0.5`, and discount `0.6` yield `0.54`.
**Academic References**: DiFonzo and Bordia (2007); Lewandowsky et al. (2012).

## Source Docstring Excerpts

### Rule / `FactChecker`

```text
Fact-checker who actively investigates claims and broadcasts corrections.

Theory: simulation-bases.md Section 4.4 -- FactChecker
Theory: DiFonzo & Bordia (2004, 2007) -- Rumor correction and denial
    Effective rumor control requires active, credible denial. Fact-checking
    reduces belief by providing verified counter-information. However,
    corrections travel slower than rumors (the "implied truth effect").

Behavior:
    - Very low credulity: requires verified evidence
    - Actively corrects misinformation with high credibility
    - Corrections are less contagious than rumors (slower spread)
    - More effective when distortion is high (obvious falsehoods)

Effect: STRONGLY STABILIZING -- Primary correction mechanism

Formula:
    belief_update = strong_skepticism * (truth_value - my_belief)
    correction_intensity = fact_check_strength * (1 - belief) * (1 + distortion_bonus)
    correction_effectiveness = intensity * credibility_discount

Parameters from config extras:
    - fact_check_strength, credibility_discount, distortion_sensitivity
```

### LLM / `LLMFactChecker`

```text
LLM fact checker.

Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMFactChecker`

```text
Hybrid fact checker.

Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMFactChecker`

```text
RAG-augmented fact checker.

Theory: simulation-bases.md Section 4.4
```
