# MentalAccounting / Rational Portfolio Manager

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MentalAccounting |
| Agent type | Rational Portfolio Manager |
| Canonical class | `RationalPortfolioManager` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

1. **Summary**: Uses whole-portfolio valuation and serves as the rational benchmark. It trades against price-fundamental deviations. 2. **Theoretical and Empirical Foundation**: Markowitz (1952) provides whole-portfolio optimization; Barberis & Huang (2001) motivates contrast with narrow framing. 3. **Design Purpose and Activation Scenarios**: Activates when absolute deviation exceeds the configured rational threshold. 4. **Behavioral Framework**: Uses `risk_aversion`, `base_size`, `quantity_scale`, and `deviation_threshold`. 5. **Decision Process Walkthrough**: Buy undervaluation, sell overvaluation, size by deviation and risk aversion. 6. **Worked Numerical Example**: With `deviation=-4%`, `risk_aversion=0.7`, `quantity_scale=3000`, raw quantity is 84 before caps. 7. **Academic References**: Markowitz (1952); Barberis & Huang (2001).

## Financial Theory / Theoretical Basis

### Rule / `RationalPortfolioManager`
- Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager

### LLM / `LLMRationalPortfolioManager`
- Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.

### RuleLLM / `RuleLLMRationalPortfolioManager`
- Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.

### Rag / `RagLLMRationalPortfolioManager`
- Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| deviation_threshold | Rule: `0.02`<br>LLM: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.MentalAccounting.LLM.prompts:LLM_RATIONAL_PORTFOLIO_PROMPT', 'user_message': 'examples.MentalAccounting.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_RATIONAL_PORTFOLIO_SYS', 'user_message': 'examples.MentalAccounting.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.MentalAccounting.Rag.prompts:RULELLM_RATIONAL_PORTFOLIO_SYS', 'user_message': 'examples.MentalAccounting.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `3000`<br>LLM: `3000`<br>RuleLLM: `3000`<br>Rag: `3000` | LLM, Rag, Rule, RuleLLM |
| risk_aversion | Rule: `0.7`<br>LLM: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rationalportfoliomanager | RationalPortfolioManager | `RationalPortfolioManager` | 1 | `examples/MentalAccounting/Rule/players.py` |
| LLM | rationalportfoliomanager | RationalPortfolioManager | `LLMRationalPortfolioManager` | 1 | `examples/MentalAccounting/LLM/players.py` |
| RuleLLM | rationalportfoliomanager | RationalPortfolioManager | `RuleLLMRationalPortfolioManager` | 1 | `examples/MentalAccounting/RuleLLM/players.py` |
| Rag | rationalportfoliomanager | RationalPortfolioManager | `RagLLMRationalPortfolioManager` | 1 | `examples/MentalAccounting/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RationalPortfolioManager

1. **Summary**: Uses whole-portfolio valuation and serves as the rational benchmark. It trades against price-fundamental deviations.
2. **Theoretical and Empirical Foundation**: Markowitz (1952) provides whole-portfolio optimization; Barberis & Huang (2001) motivates contrast with narrow framing.
3. **Design Purpose and Activation Scenarios**: Activates when absolute deviation exceeds the configured rational threshold.
4. **Behavioral Framework**: Uses `risk_aversion`, `base_size`, `quantity_scale`, and `deviation_threshold`.
5. **Decision Process Walkthrough**: Buy undervaluation, sell overvaluation, size by deviation and risk aversion.
6. **Worked Numerical Example**: With `deviation=-4%`, `risk_aversion=0.7`, `quantity_scale=3000`, raw quantity is 84 before caps.
7. **Academic References**: Markowitz (1952); Barberis & Huang (2001).

## Source Docstring Excerpts

### Rule / `RationalPortfolioManager`

```text
Optimizes entire portfolio without mental accounting.

Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager
Strategy specification: simulation-bases.md Section 4.3.4 -- Behavioral Framework
Parameters: simulation-bases.md Section 6

Parameters from config extras:
    - risk_aversion
```

### LLM / `LLMRationalPortfolioManager`

```text
LLM-driven RationalPortfolioManager.

Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.
Strategy specification: simulation-bases.md Section 4.3.4.
```

### RuleLLM / `RuleLLMRationalPortfolioManager`

```text
Hybrid: RationalPortfolioManager rules + LLM reasoning.

Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.
Strategy specification: simulation-bases.md Section 4.3.4.
```

### Rag / `RagLLMRationalPortfolioManager`

```text
RAG-augmented: RationalPortfolioManager rules + LLM + retrieved knowledge.

Theoretical basis: simulation-bases.md Section 4.3 -- RationalPortfolioManager.
Strategy specification: simulation-bases.md Section 4.3.4.
```
