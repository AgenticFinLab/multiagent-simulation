# AvailabilityBias / Systematic Analyst

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AvailabilityBias |
| Agent type | Systematic Analyst |
| Canonical class | `SystematicAnalyst` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The SystematicAnalyst is the rational benchmark -- an institutional investor who processes all available information using objective, evidence-based methods without availability bias. Unlike RecentEventOverweighter (who overweights recent returns) and MediaInfluencedTrader (who overweights media-amplified signals), the SystematicAnalyst responds only to the objective fundamental deviation: the actual gap between price and intrinsic value. This investor represents the Bayesian ideal of flat-weighted information processing, where no event is given disproportionate cognitive salience. The SystematicAnalyst's behavior defines the counterfactual: what prices would look like if availability bias did not exist.

## Financial Theory / Theoretical Basis

### Rule / `SystematicAnalyst`
- Theory: simulation-bases.md Section 4.3 -- SystematicAnalyst
- Theoretical basis: Mullainathan (2002) -- Bayesian rational processing; absence of bias.

### LLM / `LLMSystematicAnalyst`
- LLM-driven systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMSystematicAnalyst`
- RuleLLM systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMSystematicAnalyst`
- RAG-augmented systematic analyst -- objective information weighting. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| evidence_threshold | Rule: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AvailabilityBias.LLM.prompts:LLM_SYSTEMATIC_ANALYST_SYS', 'user_message': 'examples.AvailabilityBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_SYSTEMATIC_ANALYST_SYS', 'user_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AvailabilityBias.Rag.prompts:RAG_SYSTEMATIC_ANALYST_SYS', 'user_message': 'examples.AvailabilityBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `300.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000.0` | Rule |
| weight_decay | Rule: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | systematic_analyst | Systematic Analyst | `SystematicAnalyst` | 1 | `examples/AvailabilityBias/Rule/players.py` |
| LLM | llm_systematic_analyst | LLM Systematic Analyst | `LLMSystematicAnalyst` | 1 | `examples/AvailabilityBias/LLM/players.py` |
| RuleLLM | rulellm_systematic_analyst | RuleLLM Systematic Analyst | `RuleLLMSystematicAnalyst` | 1 | `examples/AvailabilityBias/RuleLLM/players.py` |
| Rag | ragllm_systematic_analyst | RAG Systematic Analyst | `RagLLMSystematicAnalyst` | 1 | `examples/AvailabilityBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Investor: SystematicAnalyst

#### 4.3.1  Summary

The SystematicAnalyst is the rational benchmark -- an institutional investor who processes all available information using objective, evidence-based methods without availability bias. Unlike RecentEventOverweighter (who overweights recent returns) and MediaInfluencedTrader (who overweights media-amplified signals), the SystematicAnalyst responds only to the objective fundamental deviation: the actual gap between price and intrinsic value. This investor represents the Bayesian ideal of flat-weighted information processing, where no event is given disproportionate cognitive salience. The SystematicAnalyst's behavior defines the counterfactual: what prices would look like if availability bias did not exist.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Rational Information Processing (Mullainathan)**
- Theory / Study: Bounded rationality with memory -- the rational limit
- Citation: Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735-774. DOI: 10.1162/003355302760193887
- Core Insight: Mullainathan's model identifies the rational benchmark as flat-weighted processing: all past signals are weighted equally, with no primacy for recent or salient events. The SystematicAnalyst approximates this benchmark by responding only to the current deviation -- the objectively most informative signal for a mean-reverting market -- without availability distortion.
- Mathematical Formulation: Rational signal: s_rational(t) = δ(t) (deviation only). Sizing: Q_rational = min(Q_max, |δ(t)| x 5000). Direction: buy if δ < 0 (undervalued); sell if δ > 0 (overvalued). No recency or media weighting.
- Empirical Evidence: Institutional investors with systematic, quantitative mandates (factor-model portfolios, quant funds) approximate rational information processing. Their Sharpe ratios systematically exceed retail/discretionary investors, consistent with the rational advantage predicted by Mullainathan's model.
- Relevance to This Investor: SystematicAnalyst's `deviation` threshold of 0.03 (3%) captures the signal-to-noise threshold below which fundamental signals are indistinguishable from random fluctuations; consistent with the evidence_threshold concept in Mullainathan's model.

**Theory 2: Fundamental Analysis and Market Efficiency (Fama)**
- Theory / Study: Efficient markets and rational information processing
- Citation: Fama, E. F. (1970). "Efficient capital markets: A review of empirical work." *Journal of Finance*, 25(2), 383-417. DOI: 10.2307/2325486. Also: Grossman, S. J., & Stiglitz, J. E. (1980). "On the impossibility of informationally efficient markets." *American Economic Review*, 70(3), 393-408.
- Core Insight: In Fama's framework, rational investors who process all available information efficiently constitute the stabilizing force in markets. Grossman & Stiglitz (1980) show that some informed agents must earn positive returns to incentivize information gathering -- the SystematicAnalyst represents these informed agents who keep prices tethered to fundamentals.
- Relevance to This Investor: SystematicAnalyst's deviation-triggered contrarian trading (buy undervalued, sell overvalued) provides the mean-reversion force that limits the extent to which availability-biased agents can push prices from fundamentals. Its activity is the empirical validation test: if SystematicAnalyst's volume is sufficient to correct bias-driven mispricings, the simulation produces a near-efficient market; if insufficient, persistent mispricings emerge.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide the rational stabilizing benchmark -- the force that corrects availability-biased mispricings and limits the magnitude of systematic deviation from fundamentals.

**Activation Scenarios**:
- Scenario A (Fundamental deviation < 3%): Hold. Noise-level deviations do not warrant action; consistent with the rational agent's evidence threshold.
- Scenario B (Undervaluation, deviation < -3%): Buy proportionally. Corrects downward bias from availability-driven panic selling.
- Scenario C (Overvaluation, deviation > +3%): Sell proportionally. Corrects upward bias from availability-driven momentum buying.

**Market Contribution**: Stabilizing -- directly counters availability-biased overreaction by trading in the opposite direction. The balance between SystematicAnalyst's stabilizing volume and biased agents' destabilizing volume determines the equilibrium mispricing magnitude.

**Interaction with other agents**: Directly opposes RecentEventOverweighter and MediaInfluencedTrader when they push price away from fundamental; aligns with ValueTrader (both stabilizing but at different thresholds -- SystematicAnalyst at 3%, ValueTrader at 5%).

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole trading signal -- the objective gap between price and fundamental value. No recency weighting; no media amplification. Consistent with Mullainathan's rational benchmark of flat-weighted processing.
- `price`: For order sizing (cash / price) and submission.
- `cash`, `position`: Constraint variables.

**4.3.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If |deviation| > 0.03: trade.
3. If deviation < -0.03: buy. Quantity = min(300, |deviation| x 5000). Cash-constrained.
4. If deviation > +0.03: sell. Quantity = min(300, deviation x 5000). Position-constrained.
5. Hold if |deviation| <= 0.03.

**4.3.4.3  Mathematical Model**
- Trigger function: trade if |δ(t)| > 0.03
- Sizing: Q*(t) = min(300, |δ(t)| x 5000)
- Direction: buy if δ < 0; sell if δ > 0 (contrarian to deviation)
- State variables: cash, position

| Parameter          | Value | Meaning                                           | Config Path                                              | Source                       |
|--------------------|-------|---------------------------------------------------|----------------------------------------------------------|------------------------------|
| evidence_threshold | 0.03  | Minimum deviation to trigger rational trading     | `configs/AvailabilityBias/Rule/players.yml -> systematic_analyst` | Mullainathan (2002)          |
| weight_decay       | 0.80  | Historical signal weight decay (reserved for multi-period variants) | `configs/AvailabilityBias/Rule/players.yml -> systematic_analyst` | Bayesian updating convention |
| initial_cash       | 10000 | Starting cash                                     | `configs/AvailabilityBias/Rule/players.yml -> systematic_analyst` | Normalization                |
| initial_position   | 0     | Starting position                                 | `configs/AvailabilityBias/Rule/players.yml -> systematic_analyst` | Normalization                |

**4.3.4.4  Behavioral Properties**
- Time horizon: Medium-term -- responds to current deviation without momentum consideration
- Risk tolerance: Medium -- trades on fundamental signals but with limited position sizing; not a deep-value investor
- Information asymmetry: None -- uses only publicly available deviation signal; advantage is processing quality, not information advantage
- Psychological profile: Analytical, unemotional, model-driven. In LLM variants, the persona emphasizes "I focus on the objective fundamental gap, ignoring recent noise or media coverage."

#### 4.3.5  Decision Process Walkthrough

Given: price = 103.5, fundamental = 100.0, deviation = +0.035, cash = 10000, position = 200

Step 1: deviation = +0.035. Is |0.035| > 0.03theta YES -> sell (price above fundamental).
Step 2: Quantity = min(300, 0.035 x 5000) = min(300, 175) = 175 shares.
Step 3: Position check: min(175, 200) = 175 -> valid.
Step 4: Send order: action=sell, quantity=175, bid_price=103.5.
Result: -175 shares in D(t); systematic correction of 3.5% overvaluation. Contrast: MediaInfluencedTrader would buy into the positive media-salient deviation, showing the destabilizing direction of that bias channel.

#### 4.3.6  Worked Numerical Example

Market state: price = 96.5, fundamental = 100.0, deviation = -0.035, cash = 10000, position = 0

Trigger: |-0.035| > 0.03 -> buy.
Quantity: min(300, 0.035 x 5000) = min(300, 175) = 175 shares.
Cost: 175 x 96.5 = 16887.5, so cash-constrained quantity is 103.63 shares with starting cash 10000.
Order: action=buy, quantity≈103.63, bid_price=96.5.
Rationale: 3.5% undervaluation triggers a rational proportional buy -- the systematically correct response. RecentEventOverweighter at the same deviation with a recent -3% return would compute perceived_signal = 0.70 x (-0.03) + 0.30 x (-0.035) = -0.0315, producing availability-driven selling instead of rational buying if it has inventory.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                   | Notes                                                                                  |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| 1 | Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735-774. DOI: 10.1162/003355302760193887 | Rational benchmark; evidence_threshold calibration                                     |
| 2 | Fama, E. F. (1970). "Efficient capital markets: A review of empirical work." *Journal of Finance*, 25(2), 383-417. DOI: 10.2307/2325486                    | Rational information processing benchmark; basis for contrarian deviation response     |
| 3 | Grossman, S. J., & Stiglitz, J. E. (1980). "On the impossibility of informationally efficient markets." *American Economic Review*, 70(3), 393-408.        | Role of rational agents in maintaining near-efficiency; stabilizing speculation theory |


---

## Source Docstring Excerpts

### Rule / `SystematicAnalyst`

```text
Systematic analyst -- weighs all information by objective relevance (benchmark).

Theory: simulation-bases.md Section 4.3 -- SystematicAnalyst
Theoretical basis: Mullainathan (2002) -- Bayesian rational processing; absence of bias.
Trades on fundamental deviation without availability bias.
See simulation-bases.md Section 4.3.4.3 for mathematical model.
```

### LLM / `LLMSystematicAnalyst`

```text
LLM-driven systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMSystematicAnalyst`

```text
RuleLLM systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMSystematicAnalyst`

```text
RAG-augmented systematic analyst -- objective information weighting. Theory: simulation-bases.md Section 4.3.
```
