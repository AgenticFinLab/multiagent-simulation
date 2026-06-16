# TulipMania / Social Proof Follower

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | TulipMania |
| Agent type | Social Proof Follower |
| Canonical class | `SocialProofFollower` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Enters the speculative trade because crowd participation validates the story. **Theoretical and Empirical Basis**: Herding, social proof, and informational cascades. **Design Purpose**: Amplify the same price move through a different behavioral channel than pure trend following. **Behavioral Framework**: Treats positive deviation as evidence that others are participating. **Decision Process**: Uses the same threshold and quantity formula as TrendChaser: `abs(deviation) > 0.02`, `quantity = min(800, int(abs(deviation) * 5000))`, buy on positive deviation and sell on negative deviation. **Worked Numerical Example**: A 10% premium to intrinsic value produces a 500-unit buy before portfolio constraints. **Academic References**: Herding and social-proof literature in financial markets and crowd psychology.

## Financial Theory / Theoretical Basis

### Rule / `SocialProofFollower`
- Theory: simulation-bases.md Section 4.2
- Theoretical Basis: Social proof and crowd psychology (Mackay, 1841)

### LLM / `LLMSocialProofFollower`
- LLM social proof follower joining speculative positions due to crowd behavior.
- Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMSocialProofFollower`
- Rule+LLM social proof follower joining speculative positions due to crowd behavior.
- Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMSocialProofFollower`
- RAG-augmented social proof follower joining speculative positions due to crowd behavior.
- Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| crowd_threshold | Rule: `0.3`<br>LLM: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| follow_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.TulipMania.LLM.prompts:LLM_SOCIAL_PROOF_FOLLOWER_SYS', 'user_message': 'examples.TulipMania.LLM.prompts:LLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_SOCIAL_PROOF_FOLLOWER_SYS', 'user_message': 'examples.TulipMania.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.TulipMania.Rag.prompts:RAGLLM_SOCIAL_PROOF_FOLLOWER_SYS', 'user_message': 'examples.TulipMania.Rag.prompts:RAG_USER_TEMPLATE', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'rag': {'from_global_index_dir': ['rag_index'], 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 3}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | socialprooffollower | SocialProofFollower | `SocialProofFollower` | 3 | `examples/TulipMania/Rule/players.py` |
| LLM | socialprooffollower | SocialProofFollower | `LLMSocialProofFollower` | 3 | `examples/TulipMania/LLM/players.py` |
| RuleLLM | socialprooffollower | SocialProofFollower | `RuleLLMSocialProofFollower` | 3 | `examples/TulipMania/RuleLLM/players.py` |
| Rag | socialprooffollower | SocialProofFollower | `RagLLMSocialProofFollower` | 3 | `examples/TulipMania/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 SocialProofFollower

**Summary**: Enters the speculative trade because crowd participation validates
the story.
**Theoretical and Empirical Basis**: Herding, social proof, and informational
cascades.
**Design Purpose**: Amplify the same price move through a different behavioral
channel than pure trend following.
**Behavioral Framework**: Treats positive deviation as evidence that others are
participating.
**Decision Process**: Uses the same threshold and quantity formula as
TrendChaser: `abs(deviation) > 0.02`,
`quantity = min(800, int(abs(deviation) * 5000))`, buy on positive deviation and
sell on negative deviation.
**Worked Numerical Example**: A 10% premium to intrinsic value produces a
500-unit buy before portfolio constraints.
**Academic References**: Herding and social-proof literature in financial
markets and crowd psychology.

## Source Docstring Excerpts

### Rule / `SocialProofFollower`

```text
Follows crowd into speculative positions because everyone else is doing it.

Theory: simulation-bases.md Section 4.2
Theoretical Basis: Social proof and crowd psychology (Mackay, 1841)
Market Role: destabilizing
```

### LLM / `LLMSocialProofFollower`

```text
LLM social proof follower joining speculative positions due to crowd behavior.

Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMSocialProofFollower`

```text
Rule+LLM social proof follower joining speculative positions due to crowd behavior.

Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMSocialProofFollower`

```text
RAG-augmented social proof follower joining speculative positions due to crowd behavior.

Theory: simulation-bases.md Section 4.2
```
