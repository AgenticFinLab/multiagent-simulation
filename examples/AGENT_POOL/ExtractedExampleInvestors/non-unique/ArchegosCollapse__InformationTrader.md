# ArchegosCollapse / Information Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ArchegosCollapse |
| Agent type | Information Trader |
| Canonical class | `InformationTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`InformationTrader` represents informed short sellers who detect the onset of forced institutional selling -- front-runners who pick up signals of impending cascade and establish short positions before the main wave. In the Archegos event, several well-positioned traders reportedly detected unusual block trade flows and large single-name option activity before the public cascade began. This investor adds early price pressure at moderate deviations, contributing to cascade speed but also covering short positions and providing buying support when the cascade reverses. It is the most sophisticated participant in the simulation.

## Financial Theory / Theoretical Basis

### Rule / `InformationTrader`
- Theory: simulation-bases.md Section 4.5 -- InformationTrader
- Theoretical basis: Informed Trading / Front-Running (Kyle, 1985; Brunnermeier & Pedersen, 2005).

### LLM / `LLMInformationTrader`
- LLM-driven information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.

### RuleLLM / `RuleLLMInformationTrader`
- RuleLLM information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.

### Rag / `RagLLMInformationTrader`
- RAG-augmented information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| cover_size | Rule: `500` | Rule |
| cover_threshold | Rule: `-0.03` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| detection_ability | Rule: `0.5` | Rule |
| detection_threshold | Rule: `-0.05` | Rule |
| front_run_size | Rule: `1000` | Rule |
| fundamental_value | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `300000.0`<br>LLM: `300000.0`<br>RuleLLM: `300000.0`<br>Rag: `300000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000.0`<br>LLM: `1000.0`<br>RuleLLM: `1000.0`<br>Rag: `1000.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_INFORMATION_TRADER_SYS', 'user_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_INFORMATION_TRADER_SYS', 'user_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_INFORMATION_TRADER_SYS', 'user_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | information_trader | Information Trader | `InformationTrader` | 2 | `examples/ArchegosCollapse/Rule/players.py` |
| LLM | information_trader | Information Trader | `LLMInformationTrader` | 2 | `examples/ArchegosCollapse/LLM/players.py` |
| RuleLLM | information_trader | Information Trader | `RuleLLMInformationTrader` | 2 | `examples/ArchegosCollapse/RuleLLM/players.py` |
| Rag | ragllm_information_trader | RAG Information Trader | `RagLLMInformationTrader` | 2 | `examples/ArchegosCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 InformationTrader

#### 4.5.1 Summary

`InformationTrader` represents informed short sellers who detect the onset of forced institutional selling -- front-runners who pick up signals of impending cascade and establish short positions before the main wave. In the Archegos event, several well-positioned traders reportedly detected unusual block trade flows and large single-name option activity before the public cascade began. This investor adds early price pressure at moderate deviations, contributing to cascade speed but also covering short positions and providing buying support when the cascade reverses. It is the most sophisticated participant in the simulation.

#### 4.5.2 Theoretical and Empirical Foundation

**Theory/Study 1: Information-Based Trading and Price Discovery**

- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: Informed traders with private information strategically trade to extract profits while hiding their information from market makers. Their trading accelerates price discovery -- prices move toward true value faster than with uninformed trading alone. In the context of liquidation cascades, informed traders front-run anticipated forced selling.
- Mathematical Formulation: Kyle's lambda (lambda_kyle) measures price impact per unit of informed order flow: `DeltaP = lambda_kyle x (informed_order + noise_order)`. Informed traders size their orders to maximize expected profit given price impact: `Q_opt = (V - P) / (2 x lambda_kyle)`, where V is the informed trader's private value estimate.
- Empirical Evidence: Empirical estimates of Kyle's lambda for individual stocks range from 0.01-0.05 per unit of normalized order flow (Glosten & Harris, 1988, *Journal of Finance*, 43(1), 123-142). Information traders in distressed scenarios appear to act on signals 2-5 rounds before public events materialize.
- Relevance to This Investor: InformationTrader acts at deviation = -0.05 (earlier than any other agent), reflecting early detection of cascade signals. The `detection_ability = 0.50` models partial information -- it only detects the signal 50% of the time, consistent with the noisy nature of pre-cascade information.
- Parameter Calibration: detection_threshold = 0.05; detection_ability = 0.50 (coin-flip detection rate reflecting noisy signals).

**Theory/Study 2: Short Selling and Market Efficiency**

- Citation: Boehmer, E., Jones, C. M., & Zhang, X. (2008). Which shorts are informedtheta *Journal of Finance*, 63(2), 491-527. https://doi.org/10.1111/j.1540-6261.2008.01324.x
- Core Insight: Institutional short sellers are significantly more informed than retail short sellers. Stocks with high institutional short interest subsequently underperform by 1-2% per month, confirming that informed shorting accelerates price adjustment toward fundamental value.
- Empirical Evidence: Boehmer et al. (2008) find that institutional short sellers earn 20-day raw returns of -9.4% on their short positions (mean), consistent with exploiting anticipated price declines of 5-15%.
- Relevance to This Investor: InformationTrader's front-running behavior and short covering represent the empirically documented institutional short-selling cycle: establish short ahead of cascade, cover on stabilization.

#### 4.5.3 Design Purpose and Activation Scenarios

**Purpose**: Provide early downward price pressure, accelerating cascade onset, then provide stabilizing buying when short positions are covered during recovery.

| Market Condition                            | InformationTrader Response                       | Economic Effect                                                             | Theory                                        |
|---------------------------------------------|--------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------------|
| deviation < -0.05 AND random() < 0.50       | Short (sell): up to `min(1000, position)` shares | Adds to early downward pressure; accelerates threshold crossing             | Section 4.5.2 Theory 1: front-running informed trade |
| deviation > -0.03 AND short position exists | Buy to cover: up to 200 shares                   | Positive demand shock during recovery; partially offsets long recovery time | Short covering creates buying pressure        |
| All other conditions                        | Hold                                             | Neutral impact                                                              | No signal                                     |

**Market Contribution**: Neutral to Amplifying early; Stabilizing on recovery. Net effect on cascade depth is approximately neutral: short establishment amplifies the decline, but short covering amplifies the recovery.

#### 4.5.4 Behavioral Framework

##### 4.5.4.1 Mathematical Model

**Short Entry Trigger**:
```
Trigger when: δ(t) < -theta_detect  AND  U(0,1) < p_detect
where theta_detect = 0.05, p_detect = 0.50
Q_sell = min(front_run_size, position(t))  where front_run_size = 1000
```

**Short Cover Trigger**:
```
Trigger when: δ(t) > -theta_recovery  AND  short_position(t) > 0
where theta_recovery = 0.03
Q_buy = min(200, short_position)
```

**State Variables**:
| Variable       | Update Rule                                   |
|----------------|-----------------------------------------------|
| short_position | increments on each short; decrements on cover |

#### 4.5.5 Decision Process Walkthrough

Early cascade detection (round 3-5):
- deviation = -0.07 (below detection threshold of -0.05)
- random() = 0.38 < 0.50 -> signal detected
- Q_sell = min(1000, position) = min(1000, 2000) = 1000 shares
- Submit: sell 1000 @ current price -> accelerates cascade onset

Recovery phase:
- deviation rises to -0.025 (above -0.03 recovery threshold)
- short_position > 0 -> cover
- Q_buy = min(200, short_position) -> adds positive demand during recovery

#### 4.5.6 Worked Numerical Example

```
Round 4: P = 95.0, δ = -0.05, position = 2000, p_detect = 0.50
Trigger: -0.05 < -0.05 (border case; use strict <) -> use δ = -0.06 for illustration
random() = 0.42 < 0.50 -> detect
Q_sell = min(1000, 2000) = 1000 shares
Sell 1000 @ $95.00
DeltaP ≈ 0.03 x (-1000) = -$30; P -> $65.00 (before mean reversion)
This accelerates the cascade by pushing price below PrimeBroker1 threshold sooner.
```

#### 4.5.7 Academic References

| # | Full Citation                                                                                                                                                                     | Contribution                                                     |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| 1 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210                                                    | Information-based trading theory; front-running model            |
| 2 | Boehmer, E., Jones, C. M., & Zhang, X. (2008). Which shorts are informedtheta *Journal of Finance*, 63(2), 491-527. https://doi.org/10.1111/j.1540-6261.2008.01324.x                  | Empirical evidence for institutional short selling effectiveness |
| 3 | Glosten, L. R., & Harris, L. E. (1988). Estimating the components of the bid/ask spread. *Journal of Finance*, 43(1), 123-142. https://doi.org/10.1111/j.1540-6261.1988.tb02591.x | Kyle lambda empirical estimates for individual stocks            |

## Source Docstring Excerpts

### Rule / `InformationTrader`

```text
Front-running information trader detecting liquidation signals.

Theory: simulation-bases.md Section 4.5 -- InformationTrader
Theoretical basis: Informed Trading / Front-Running (Kyle, 1985; Brunnermeier & Pedersen, 2005).
Detects cascade signal when deviation < detection_threshold with
probability detection_ability. Sells front_run_size shares.
Covers short when deviation recovers above cover_threshold.
See simulation-bases.md Section 4.5.4.3 for mathematical model.
```

### LLM / `LLMInformationTrader`

```text
LLM-driven information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
```

### RuleLLM / `RuleLLMInformationTrader`

```text
RuleLLM information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
```

### Rag / `RagLLMInformationTrader`

```text
RAG-augmented information trader -- front-runs liquidation cascade. Theory: simulation-bases.md Section 4.5.
```
