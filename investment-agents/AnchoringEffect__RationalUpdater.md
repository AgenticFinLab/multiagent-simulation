# AnchoringEffect / Rational Updater

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Rational Updater |
| Canonical class | `RationalUpdater` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

RationalUpdater represents the Muth-rational agent who acts optimally on all available information -- the theoretical benchmark that every other agent in this simulation deviates from. It uses the true fundamental deviation directly, with no anchoring adjustment, and trades immediately when price differs from fundamental by more than 2%. RationalUpdater is the corrective force that prevents the anchoring-induced mispricing from growing without limit and provides the "rational expectations" baseline against which the bias magnitude of other agents can be measured.

## Financial Theory / Theoretical Basis

### Rule / `RationalUpdater`
- Theoretical basis: simulation-bases.md Section 2.4 (Muth, 1961 -- Rational Expectations).
- Decision rule (simulation-bases.md Section 4.3 -- Rule-Based Behavior):

### LLM / `LLMRationalUpdater`
- LLM-driven rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.

### RuleLLM / `RuleLLMRationalUpdater`
- RuleLLM rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.

### Rag / `RagLLMRationalUpdater`
- RAG-augmented rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `25.0`<br>RuleLLM: `25.0`<br>Rag: `25.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AnchoringEffect.LLM.prompts:LLM_RATIONAL_UPDATER_SYS', 'user_message': 'examples.AnchoringEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_RATIONAL_UPDATER_SYS', 'user_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AnchoringEffect.Rag.prompts:RAG_RATIONAL_UPDATER_SYS', 'user_message': 'examples.AnchoringEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_threshold | Rag: `0.02` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rational_updater | Rational Updater | `RationalUpdater` | 1 | `examples/AnchoringEffect/Rule/players.py` |
| LLM | rational_updater | Rational Updater | `LLMRationalUpdater` | 1 | `examples/AnchoringEffect/LLM/players.py` |
| RuleLLM | rulellm_rational | RuleLLM Rational Updater | `RuleLLMRationalUpdater` | 1 | `examples/AnchoringEffect/RuleLLM/players.py` |
| Rag | ragllm_rational | RAG Rational Updater | `RagLLMRationalUpdater` | 1 | `examples/AnchoringEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RationalUpdater

#### 4.3.1  Summary

RationalUpdater represents the Muth-rational agent who acts optimally on all available information -- the theoretical benchmark that every other agent in this simulation deviates from. It uses the true fundamental deviation directly, with no anchoring adjustment, and trades immediately when price differs from fundamental by more than 2%. RationalUpdater is the corrective force that prevents the anchoring-induced mispricing from growing without limit and provides the "rational expectations" baseline against which the bias magnitude of other agents can be measured.

#### 4.3.2  Theoretical and Empirical Foundation

**Rational Expectations and Fundamental-Based Trading**:
- Theory / Study: Rational Expectations Hypothesis
- Citation: Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315-335. https://doi.org/10.2307/1905537
- Core Insight: Rational agents form expectations using all available information optimally. Prices that deviate from fundamental value represent profit opportunities that rational agents immediately exploit, pushing prices toward fundamental. The speed of price discovery depends on the proportion of rational to anchoring agents.
- Mathematical Formulation: `trade if |deviation| > threshold; Q* ∝ |deviation| x base_size`; no anchoring, no history -- pure fundamental-gap exploitation.
- Empirical Evidence: Fama (1970) documents that professional traders provide near-immediate correction of public information-based mispricings. The failure of this correction mechanism to fully overcome anchoring is consistent with the limits-to-arbitrage literature (fewer rational agents than anchoring agents in this simulation).
- Relevance to This Investor: RationalUpdater acts as the simulation's "market efficiency engine" -- it provides the corrective force that prevents anchoring mispricings from becoming arbitrarily large.

**Market Microstructure and Informed Trading**:
- Theory / Study: Informed vs. Uninformed Trader Framework
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://www.jstor.org/stable/1805228
- Core Insight: For markets to be informationally efficient, informed traders (here, RationalUpdater) must earn returns sufficient to compensate for their information-gathering costs. The ratio of informed to uninformed traders determines the degree of market efficiency.
- Mathematical Formulation: In this simulation, 1 RationalUpdater out of 9 investor agents = ~11% informed trader proportion; Grossman-Stiglitz predicts incomplete information incorporation proportional to this share.
- Empirical Evidence: Chordia, Roll & Subrahmanyam (2005) show that informed institutional trading corrects public information-based mispricings in 0-5 days; consistent with RationalUpdater's immediate response to deviations.
- Relevance to This Investor: With only 3 instances (23% of agents), RationalUpdater provides significant but insufficient corrective force -- consistent with the Grossman-Stiglitz prediction that partial efficiency is the equilibrium with costly information.

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: RationalUpdater provides the corrective force that keeps the simulation's mispricing in a bounded range [3%, 10%] rather than growing without limit. It is the theoretical foil to the anchoring agents -- by observing how quickly it fails to correct the mispricing, we measure the strength of the anchoring effect.

Activation Scenarios:
- Price above fundamental by > 2% (price > 102): Sells; provides direct corrective downward pressure.
- Price below fundamental by > 2% (price < 98): Buys; prevents over-correction and provides support.
- Within ±2% of fundamental: Holds; consistent with a 2% minimum threshold required to cover transaction friction.

Market Contribution: **Stabilising** -- the only purely corrective agent type in the simulation. However, at 1 instance vs. 4 anchoring agents (2 AnchoredTrader + 2 HistoricalAnchor), its corrective force is intentionally weaker than the biased demand block, consistent with the Grossman-Stiglitz incomplete-efficiency prediction.

Interaction with other agents: Directly opposes AnchoredTrader (sells when AT buys) and HistoricalAnchor (sells when HA buys). Aligns with the gamma-term mean reversion in the price formula.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**

| Signal        | Type       | Rationale                                                               |
|---------------|------------|-------------------------------------------------------------------------|
| `price`       | Continuous | Current price; used directly in deviation formula                       |
| `fundamental` | Continuous | True F; the benchmark for rational valuation                            |
| `deviation`   | Continuous | Precomputed (price - F) / F; used directly for trade trigger and sizing |

Does NOT use: anchor, price_history, momentum, sentiment. RationalUpdater processes only the true fundamental deviation -- no cognitive biases or heuristics.

**4.3.4.2  Core Behavioral Mechanism**

1. Receives `deviation = (price - F) / F` from Market broadcast.
2. If `deviation > 0.02` (price above F by > 2%): sells; size proportional to deviation.
3. If `deviation < -0.02` (price below F by > 2%): buys; size proportional to deviation.
4. Holds otherwise.
5. No anchoring adjustment, no history, no cognitive bias -- pure rational exploitation of fundamental gap.

**4.3.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function: `|deviation(t)| > threshold = 0.02`
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(deviation(t)) x 1000)
  Buy when deviation < -0.02; sell when deviation > +0.02
  ```
- State variables: None -- each decision is independent of history
- Parameter definitions:

| Symbol                    | Meaning                              | Config Path                   | Source                                                                                 |
|---------------------------|--------------------------------------|-------------------------------|----------------------------------------------------------------------------------------|
| threshold = 0.02          | Minimum deviation (2%) before action | players.yml -> RationalUpdater | Muth (1961): efficient market threshold; Fama (1970): transaction costs typically 1-2% |
| base_position_size = 20.0 | Max trade size                       | players.yml -> RationalUpdater | Standardised                                                                           |

**4.3.4.4  Behavioral Properties**

- Time horizon: Short-term -- immediate response to any deviation > 2%
- Risk tolerance: Medium -- bounded position sizes; no leverage
- Information asymmetry: Fundamental-information informed -- uses F directly which anchoring agents cognitively discount
- Psychological profile: Muth-rational -- no cognitive biases; processes all information optimally; the "textbook" efficient-markets agent that behavioural finance literature contrasts with real investors

#### 4.3.5  Decision Process Walkthrough

```
Given:  price = 103.5,  fundamental = 100.0,  threshold = 0.02

Step 1: Compute deviation
        deviation = (103.5 - 100.0) / 100.0 = 0.035

Step 2: Compare to threshold
        0.035 > 0.02 -> sell condition satisfied

Step 3: Compute quantity
        Q* = min(20.0, 0.035 x 1000) = min(20.0, 35.0) = 20 shares

Step 4: Send order
        action = sell, quantity = 20, bid_price = 103.5

Result: Provides -20 to net demand D(t); contributes lambda x (-20) = -$0.20 downward pressure.
        This is the corrective force that (partially) counteracts the buying by AnchoredTrader.
```

#### 4.3.6  Worked Numerical Example

```
Market state:  price = 104.2,  fundamental = 100.0

Calculation:
  deviation = (104.2 - 100.0) / 100.0 = 0.042  (4.2% above fundamental)
  Q* = min(20.0, 0.042 x 1000) = min(20.0, 42.0) = 20 shares

Decision: action = sell, quantity = 20, bid_price = 104.2

Rationale: Price is 4.2% above fundamental. RationalUpdater sells immediately and aggressively.
However, AnchoredTrader's perceived_target is 103.5, so it would BUY at 104.2 only if
price dropped to ~100.4. The two agents are pulling in opposite directions -- RationalUpdater
sells while AnchoredTrader may hold or buy if price dips. This tug-of-war creates the
persistent deviation zone [100, 104] characteristic of the AnchoringEffect simulation.
```

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                    | Notes                                                                    |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| 1 | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315-335. https://doi.org/10.2307/1905537                | Core theoretical foundation for rational updating behaviour              |
| 2 | Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. *Journal of Finance*, 25(2), 383-417. https://doi.org/10.2307/2325486 | Grounds empirical basis for rational price-discovery mechanism           |
| 3 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408.           | Explains why 23% informed traders produces partial (not full) efficiency |

---

## Source Docstring Excerpts

### Rule / `RationalUpdater`

```text
Bayesian updater -- trades without anchoring bias (rational benchmark).

Implements simulation-bases.md Section 4.3 -- RationalUpdater.
Theoretical basis: simulation-bases.md Section 2.4 (Muth, 1961 -- Rational Expectations).

Decision rule (simulation-bases.md Section 4.3 -- Rule-Based Behavior):
    deviation = (price - fundamental) / fundamental  (from market broadcast)
    if abs(deviation) > 0.02: trade proportionally
    quantity = min(base_position_size, abs(deviation) * 1000)

Parameters (simulation-bases.md Section 6):
    threshold: 0.02 (2% deviation triggers trade)
    base_position_size: loaded from extras["base_position_size"]
```

### LLM / `LLMRationalUpdater`

```text
LLM-driven rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
```

### RuleLLM / `RuleLLMRationalUpdater`

```text
RuleLLM rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
```

### Rag / `RagLLMRationalUpdater`

```text
RAG-augmented rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
```
