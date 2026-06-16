# LTCMCollapse / Convergence Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LTCMCollapse |
| Agent type | Convergence Arbitrageur |
| Canonical class | `ConvergenceArbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `ConvergenceArbitrageur` represents an LTCM-style relative-value trader that sees deviations from fundamental value as convergence opportunities. It is destabilizing when the trade is leveraged because buying into widening discounts or selling overvalued prices increases exposure while the market can continue moving against the position.

## Financial Theory / Theoretical Basis

### Rule / `ConvergenceArbitrageur`
- Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur
- Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage.

### LLM / `LLMConvergenceArbitrageur`
- Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur.

### RuleLLM / `RuleLLMConvergenceArbitrageur`
- Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur.

### Rag / `RagLLMConvergenceArbitrageur`
- RAG leveraged spread convergence trader. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_spread | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `2000000.0`<br>LLM: `2000000.0`<br>RuleLLM: `2000000.0`<br>Rag: `2000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| leverage | Rule: `15`<br>LLM: `15`<br>RuleLLM: `15`<br>Rag: `15` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LTCMCollapse.LLM.prompts:LLM_CONVERGENCEARBITRAGEUR_PROMPT', 'user_message': 'examples.LTCMCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_CONVERGENCEARBITRAGEUR_PROMPT', 'user_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LTCMCollapse.Rag.prompts:RAG_CONVERGENCEARBITRAGEUR_PROMPT', 'user_message': 'examples.LTCMCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_position | Rule: `5000`<br>LLM: `5000`<br>RuleLLM: `5000`<br>Rag: `5000` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | convergencearbitrageur | ConvergenceArbitrageur | `ConvergenceArbitrageur` | 2 | `examples/LTCMCollapse/Rule/players.py` |
| LLM | convergencearbitrageur | ConvergenceArbitrageur | `LLMConvergenceArbitrageur` | 2 | `examples/LTCMCollapse/LLM/players.py` |
| RuleLLM | convergencearbitrageur | ConvergenceArbitrageur | `RuleLLMConvergenceArbitrageur` | 2 | `examples/LTCMCollapse/RuleLLM/players.py` |
| Rag | convergencearbitrageur | ConvergenceArbitrageur | `RagLLMConvergenceArbitrageur` | 2 | `examples/LTCMCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 ConvergenceArbitrageur

#### Section 4.1.1 Summary

The `ConvergenceArbitrageur` represents an LTCM-style relative-value trader that sees deviations from fundamental value as convergence opportunities. It is destabilizing when the trade is leveraged because buying into widening discounts or selling overvalued prices increases exposure while the market can continue moving against the position.

The simulation uses this investor to model the central LTCM hypothesis: sophisticated arbitrage can be correct in the long run and still fragile under short-run funding pressure.

#### Section 4.1.2 Theoretical and Empirical Foundation

Primary theory is limits to arbitrage (Section 2.1). The agent uses `entry_spread`, `leverage`, and `max_position` to translate deviations into leveraged order size. Empirically, LTCM's convergence trades were exposed to spread widening after the Russian default, making the strategy a natural mapping to this agent.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `abs(deviation) <= entry_spread` | Hold | No spread opportunity | Section 2.1 |
| `deviation < -entry_spread` | Buy up to leveraged cash and cap | Attempts convergence, absorbs supply but increases exposure | Section 2.1 |
| `deviation > entry_spread` | Sell existing holdings | Bets on downward convergence | Section 2.1 |

#### Section 4.1.4 Behavioral Framework

Information set: `price`, `fundamental`, `deviation`, `cash`, `position`. Trigger function: `abs(deviation) > entry_spread`. Sizing function:

```
Q(t) = min(floor(cash(t) * leverage * |deviation(t)| / P(t)), max_position)
```

State variables are cash and position. Position is updated after order execution.

#### Section 4.1.5 Decision Process Walkthrough

If price is 95 and fundamental is 100, then `deviation = -0.05`. With `entry_spread = 0.03`, `leverage = 15`, and positive cash, the agent buys because the discount exceeds its entry threshold.

#### Section 4.1.6 Worked Numerical Example

With cash 2,000,000, price 95, deviation -0.05, and leverage 15:

```
raw_quantity = floor(2,000,000 * 15 * 0.05 / 95) = 15,789
quantity = min(15,789, 5,000) = 5,000
```

#### Section 4.1.7 Academic References

Shleifer & Vishny (1997); Jorion (2000); Lowenstein (2000), *When Genius Failed*.

## Source Docstring Excerpts

### Rule / `ConvergenceArbitrageur`

```text
Bets on spread convergence between related securities using high leverage.

Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur
Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMConvergenceArbitrageur`

```text
LLM-driven leveraged spread convergence trader.

Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur.
```

### RuleLLM / `RuleLLMConvergenceArbitrageur`

```text
RuleLLM leveraged spread convergence trader.

Theory: simulation-bases.md Section 4.1 -- ConvergenceArbitrageur.
```

### Rag / `RagLLMConvergenceArbitrageur`

```text
RAG leveraged spread convergence trader. Theory: simulation-bases.md Section 4.1.
```
