# RepresentativenessBias / Pattern Matcher

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | RepresentativenessBias |
| Agent type | Pattern Matcher |
| Canonical class | `PatternMatcher` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: A destabilizing investor that treats short price deviations as evidence of a familiar prototype. It amplifies recent patterns and underweights base rates.

## Financial Theory / Theoretical Basis

### Rule / `PatternMatcher`
- Theory: simulation-bases.md Section 4.1 -- PatternMatcher
- Theoretical basis: representativeness heuristic; salient prototypes

### LLM / `LLMPatternMatcher`
- LLM-driven pattern matcher -- prototype-based trading. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMPatternMatcher`
- RuleLLM pattern matcher -- rule-guided prototype trading. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMPatternMatcher`
- RagLLM pattern matcher -- prototype trading with retrieved context. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_rate_ignore | Rule: `0.8` | Rule |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_PATTERN_MATCHER_PROMPT', 'user_message': 'examples.RepresentativenessBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_PATTERN_MATCHER_SYS', 'user_message': 'examples.RepresentativenessBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.RepresentativenessBias.Rag.prompts:RULELLM_PATTERN_MATCHER_SYS', 'user_message': 'examples.RepresentativenessBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| pattern_sensitivity | Rule: `1.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| streak_sensitivity | Rule: `2.0`<br>LLM: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | patternmatcher | PatternMatcher | `PatternMatcher` | 2 | `examples/RepresentativenessBias/Rule/players.py` |
| LLM | patternmatcher | PatternMatcher | `LLMPatternMatcher` | 2 | `examples/RepresentativenessBias/LLM/players.py` |
| RuleLLM | patternmatcher | PatternMatcher | `RuleLLMPatternMatcher` | 2 | `examples/RepresentativenessBias/RuleLLM/players.py` |
| Rag | patternmatcher | PatternMatcher | `RagLLMPatternMatcher` | 2 | `examples/RepresentativenessBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 PatternMatcher

**Summary**: A destabilizing investor that treats short price deviations as
evidence of a familiar prototype. It amplifies recent patterns and underweights
base rates.

**Theoretical and Empirical Foundation**: Based on Kahneman and Tversky (1972,
doi:10.1016/0010-0285(72)90016-3) and Tversky and Kahneman (1974,
doi:10.1126/science.185.4157.1124).

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.02`; buys positive deviations and sells negative deviations.

**Behavioral Framework**: `pattern_sensitivity` and `base_rate_ignore` define
the tendency to convert a deviation into prototype-confirming order flow.
Quantity is `min(800, int(abs(deviation) * 5000))`.

**Decision Process Walkthrough**: Read market deviation, classify the pattern as
breakout or breakdown, cap quantity by cash or position, and submit the order.

**Worked Numerical Example**: With price 104, fundamental 100, deviation 0.04,
quantity is `min(800, int(0.04 * 5000)) = 200`; the agent buys up to 200 shares.

**Academic References**: Kahneman and Tversky (1972); Tversky and Kahneman
(1974).

## Source Docstring Excerpts

### Rule / `PatternMatcher`

```text
Matches current price patterns to historical prototypes, ignoring base rates.

Theory: simulation-bases.md Section 4.1 -- PatternMatcher
Theoretical basis: representativeness heuristic; salient prototypes
dominate base-rate reasoning.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMPatternMatcher`

```text
LLM-driven pattern matcher -- prototype-based trading. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMPatternMatcher`

```text
RuleLLM pattern matcher -- rule-guided prototype trading. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMPatternMatcher`

```text
RagLLM pattern matcher -- prototype trading with retrieved context. Theory: simulation-bases.md Section 4.1.
```
