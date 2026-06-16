# ConfirmationBias / Contrarian Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ConfirmationBias |
| Agent type | Contrarian Trader |
| Canonical class | `ContrarianTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The ContrarianTrader actively fades the consensus -- it sells when the market is above fundamental (betting that biased optimism will correct) and buys when the market is below fundamental (betting that biased pessimism will reverse). Unlike BalancedAnalyst (which corrects passively based on fundamental value), ContrarianTrader explicitly models the active strategy of trading against bias-driven consensus. It maintains the same 5% threshold as BalancedAnalyst but represents a different economic archetype: the short-seller who exploits overvaluation and the deep-discount buyer who exploits undervaluation.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianTrader`
- Theory: simulation-bases.md Section 4.4 -- ContrarianTrader
- Theoretical basis: Rabin & Schrag (1999) -- rational traders exploit systematic

### LLM / `LLMContrarianTrader`
- LLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMContrarianTrader`
- RuleLLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMContrarianTrader`
- RAG-augmented contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `40.0` | Rule |
| contrarian_threshold | Rule: `0.1` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `50000.0`<br>LLM: `50000.0`<br>RuleLLM: `50000.0`<br>Rag: `50000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ConfirmationBias.LLM.prompts:LLM_CONTRARIAN_TRADER_SYS', 'user_message': 'examples.ConfirmationBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_CONTRARIAN_TRADER_SYS', 'user_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ConfirmationBias.Rag.prompts:RAG_CONTRARIAN_TRADER_SYS', 'user_message': 'examples.ConfirmationBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `500` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarian_trader | Contrarian Trader | `ContrarianTrader` | 1 | `examples/ConfirmationBias/Rule/players.py` |
| LLM | llm_contrarian_trader | LLM Contrarian Trader | `LLMContrarianTrader` | 1 | `examples/ConfirmationBias/LLM/players.py` |
| RuleLLM | rulellm_contrarian_trader | RuleLLM Contrarian Trader | `RuleLLMContrarianTrader` | 1 | `examples/ConfirmationBias/RuleLLM/players.py` |
| Rag | ragllm_contrarian_trader | RAG Contrarian Trader | `RagLLMContrarianTrader` | 1 | `examples/ConfirmationBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ContrarianTrader

#### 4.4.1  Summary

The ContrarianTrader actively fades the consensus -- it sells when the market is above fundamental (betting that biased optimism will correct) and buys when the market is below fundamental (betting that biased pessimism will reverse). Unlike BalancedAnalyst (which corrects passively based on fundamental value), ContrarianTrader explicitly models the active strategy of trading against bias-driven consensus. It maintains the same 5% threshold as BalancedAnalyst but represents a different economic archetype: the short-seller who exploits overvaluation and the deep-discount buyer who exploits undervaluation.

#### 4.4.2  Theoretical and Empirical Foundation

**Theory 1: Contrarian Investing and Profit from Bias Correction**
- Citation: Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction in asset markets." *Journal of Finance*, 54(6), 2143-2184. DOI: 10.1111/0022-1082.00184
- Core Insight: Hong & Stein model the interaction between momentum traders (who trade in the direction of price moves) and contrarians (who fade extreme moves). Contrarians earn positive returns by exploiting the overreaction created by momentum/biased agents; their profit is limited by timing risk -- being early is costly.
- Empirical Evidence: Hong & Stein (1999) document a contrarian premium of 4-6% annually for portfolios that systematically fade extreme momentum stocks. contrarian_threshold = 0.05 calibrated to represent the "extreme" threshold above which contrarian profit becomes reliable.

**Theory 2: Short-Selling and Market Efficiency**
- Citation: Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35-55. DOI: 10.2307/2329555
- Core Insight: Short-sellers (the most active contrarians) face capital constraints and risks that limit their ability to fully correct overpricing. ContrarianTrader's fixed order_size (500) models this constrained contrarian capacity -- large enough to provide meaningful correction, but not unlimited.
- Relevance to This Investor: order_size = 500 is calibrated to be approximately equal to BeliefAnchor's order (500), ensuring each biased buy is partially offset by a contrarian sell at the threshold; combined with BalancedAnalyst (400), stabilizers total 900 vs. biased agents' 1100.

#### 4.4.3  Design Purpose and Activation Scenarios

**Purpose**: Actively counteract bias-driven mispricing; represent the short-seller and deep-value contrarian who profit from correcting confirmation-bias-driven deviations.

**Activation Scenarios**: Same threshold and direction as BalancedAnalyst (sells at deviation > +5%, buys at deviation < -5%), but represents different economic motivation.

#### 4.4.4  Behavioral Framework

**4.4.4.1  Core Behavioral Mechanism**
1. If deviation > contrarian_threshold (+0.05): sell -- fading bullish bias.
2. If deviation < -contrarian_threshold (-0.05): buy -- fading bearish bias.
3. Hold if |deviation| <= 0.05.

**4.4.4.3  Mathematical Model**
- Trigger: sell if δ > +0.05; buy if δ < -0.05; hold otherwise
- Q*(t) = min(500, position or cash_capacity)

| Parameter            | Value | Meaning                                         | Config Path                                             | Source              |
|----------------------|-------|-------------------------------------------------|---------------------------------------------------------|---------------------|
| contrarian_threshold | 0.05  | Deviation threshold for active contrarian trade | `ConfirmationBias/Rule/config.yaml -> contrarian_trader` | Hong & Stein (1999) |
| order_size           | 500   | Fixed trade size                                | `ConfirmationBias/Rule/config.yaml -> contrarian_trader` | Normalization       |

**4.4.4.4  Behavioral Properties**: Active contrarian, bias-fader, short-seller profile.

#### 4.4.5  Decision Process Walkthrough

Given: deviation = +0.07 -> sell 500. Given: deviation = -0.06 -> buy 500.

#### 4.4.6  Worked Numerical Example

Market state: deviation = +0.08. Trigger: sell. Q = 500. Rationale: 8% overvaluation driven by BeliefAnchor's bullish confirmation bias; ContrarianTrader fades this by selling 500 shares.

#### 4.4.7  Academic References

| # | Citation                                                                                                                                                                       | Notes                                                   |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Hong, H., & Stein, J. C. (1999). "A unified theory of underreaction, momentum trading, and overreaction." *Journal of Finance*, 54(6), 2143-2184. DOI: 10.1111/0022-1082.00184 | Contrarian premium; contrarian_threshold calibration    |
| 2 | Shleifer, A., & Vishny, R. W. (1997). "The limits of arbitrage." *Journal of Finance*, 52(1), 35-55. DOI: 10.2307/2329555                                                      | Constrained contrarian capacity; order_size calibration |


---

## Source Docstring Excerpts

### Rule / `ContrarianTrader`

```text
Looks for disconfirming evidence, trades against biased consensus.

Theory: simulation-bases.md Section 4.4 -- ContrarianTrader
Theoretical basis: Rabin & Schrag (1999) -- rational traders exploit systematic
bias errors; profits from mean-reversion when biased traders overshoot.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMContrarianTrader`

```text
LLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMContrarianTrader`

```text
RuleLLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMContrarianTrader`

```text
RAG-augmented contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
```
