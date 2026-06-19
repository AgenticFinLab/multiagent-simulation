# SVBBankRun / Social Media Influencer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | SVBBankRun |
| Agent type | Social Media Influencer |
| Canonical class | `SocialMediaInfluencer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Amplifies negative bank-health signals. **Theoretical and Empirical Foundation**: Information cascades and social contagion. **Design Purpose and Activation Scenarios**: Adds panic pressure when `deviation < -0.05`. **Behavioral Framework**: Public-risk amplification rather than portfolio optimization. **Mathematical Model**: ``` sell_qty = min(abs(deviation) x amplification_factor x 2000, position) ``` **Decision Process Walkthrough**: Convert negative deviation into proportional sell pressure. **Worked Example**: `deviation=-0.08`, `amplification_factor=2.0`, `position=500` yields 320 sell units. **References**: Bikhchandani, Hirshleifer, and Welch (1992).

## Financial Theory / Theoretical Basis

### Rule / `SocialMediaInfluencer`
- Theory: simulation-bases.md Section 4.2 -- SocialMediaInfluencer
- Theoretical basis: information cascade and social-contagion amplification.

### LLM / `LLMSocialMediaInfluencer`
- LLM-driven social media influencer amplifying panic signals. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMSocialMediaInfluencer`
- Hybrid Rule+LLM social media influencer with amplification rules. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMSocialMediaInfluencer`
- RAG-augmented social media influencer with amplification rules and retrieved knowledge. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| amplification_factor | Rule: `2.0`<br>LLM: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | LLM, Rag, Rule, RuleLLM |
| base_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.SVBBankRun.LLM.prompts:LLM_SOCIAL_MEDIA_INFLUENCER_SYS', 'user_message': 'examples.SVBBankRun.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_SOCIAL_MEDIA_INFLUENCER_SYS', 'user_message': 'examples.SVBBankRun.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.SVBBankRun.Rag.prompts:RAGLLM_SOCIAL_MEDIA_INFLUENCER_SYS', 'user_message': 'examples.SVBBankRun.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | socialmediainfluencer | SocialMediaInfluencer | `SocialMediaInfluencer` | 2 | `examples/SVBBankRun/Rule/players.py` |
| LLM | socialmediainfluencer | SocialMediaInfluencer | `LLMSocialMediaInfluencer` | 2 | `examples/SVBBankRun/LLM/players.py` |
| RuleLLM | socialmediainfluencer | SocialMediaInfluencer | `RuleLLMSocialMediaInfluencer` | 2 | `examples/SVBBankRun/RuleLLM/players.py` |
| Rag | socialmediainfluencer | SocialMediaInfluencer | `RagLLMSocialMediaInfluencer` | 2 | `examples/SVBBankRun/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 SocialMediaInfluencer

**Summary**: Amplifies negative bank-health signals.
**Theoretical and Empirical Foundation**: Information cascades and social contagion.
**Design Purpose and Activation Scenarios**: Adds panic pressure when `deviation < -0.05`.
**Behavioral Framework**: Public-risk amplification rather than portfolio optimization.
**Mathematical Model**:
```
sell_qty = min(abs(deviation) x amplification_factor x 2000, position)
```
**Decision Process Walkthrough**: Convert negative deviation into proportional sell pressure.
**Worked Example**: `deviation=-0.08`, `amplification_factor=2.0`, `position=500` yields 320 sell units.
**References**: Bikhchandani, Hirshleifer, and Welch (1992).

## Source Docstring Excerpts

### Rule / `SocialMediaInfluencer`

```text
Social media amplifier that converts weak stress signals into sell pressure.

Theory: simulation-bases.md Section 4.2 -- SocialMediaInfluencer
Theoretical basis: information cascade and social-contagion amplification.
See simulation-bases.md Section 4.2 for the amplification model.

Parameters from config extras:
    - amplification_factor
```

### LLM / `LLMSocialMediaInfluencer`

```text
LLM-driven social media influencer amplifying panic signals. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMSocialMediaInfluencer`

```text
Hybrid Rule+LLM social media influencer with amplification rules. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMSocialMediaInfluencer`

```text
RAG-augmented social media influencer with amplification rules and retrieved knowledge. Theory: simulation-bases.md Section 4.2.
```
