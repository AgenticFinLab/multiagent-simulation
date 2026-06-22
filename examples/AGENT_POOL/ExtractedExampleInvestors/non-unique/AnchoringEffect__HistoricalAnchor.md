# AnchoringEffect / Historical Anchor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Historical Anchor |
| Canonical class | `HistoricalAnchor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

HistoricalAnchor represents the sophisticated analyst or institutional investor who anchors to a long-run price average rather than a fixed first-observation point. This agent models the "reversion to historical mean" heuristic: it uses 60 rounds of price history as its reference, dampening its perceived deviation from that average by `(1 - anchor_weight)`. When a new price regime begins -- for instance, when fundamental value shifts -- HistoricalAnchor's 60-round historical average takes many rounds to update, creating a regime-transition anchoring effect that resists the new equilibrium for an extended period.

## Financial Theory / Theoretical Basis

### Rule / `HistoricalAnchor`
- Theoretical basis: simulation-bases.md Section 2.2 (Northcraft & Neale, 1987).
- Decision rule (simulation-bases.md Section 4.2 -- Rule-Based Behavior):

### LLM / `LLMHistoricalAnchor`
- LLM-driven historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.

### RuleLLM / `RuleLLMHistoricalAnchor`
- RuleLLM historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.

### Rag / `RagLLMHistoricalAnchor`
- RAG-augmented historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| anchor_weight | Rule: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | Rag, Rule, RuleLLM |
| base_position_size | Rule: `20.0`<br>RuleLLM: `20.0`<br>Rag: `20.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AnchoringEffect.LLM.prompts:LLM_HISTORICAL_ANCHOR_SYS', 'user_message': 'examples.AnchoringEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_HISTORICAL_ANCHOR_SYS', 'user_message': 'examples.AnchoringEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AnchoringEffect.Rag.prompts:RAG_HISTORICAL_ANCHOR_SYS', 'user_message': 'examples.AnchoringEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| lookback | Rule: `60`<br>RuleLLM: `60`<br>Rag: `60` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_threshold | Rag: `0.03` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | historical_anchor | Historical Anchor | `HistoricalAnchor` | 2 | `examples/AnchoringEffect/Rule/players.py` |
| LLM | historical_anchor | Historical Anchor | `LLMHistoricalAnchor` | 2 | `examples/AnchoringEffect/LLM/players.py` |
| RuleLLM | rulellm_historical | RuleLLM Historical Anchor | `RuleLLMHistoricalAnchor` | 2 | `examples/AnchoringEffect/RuleLLM/players.py` |
| Rag | ragllm_historical | RAG Historical Anchor | `RagLLMHistoricalAnchor` | 2 | `examples/AnchoringEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 HistoricalAnchor

#### 4.2.1  Summary

HistoricalAnchor represents the sophisticated analyst or institutional investor who anchors to a long-run price average rather than a fixed first-observation point. This agent models the "reversion to historical mean" heuristic: it uses 60 rounds of price history as its reference, dampening its perceived deviation from that average by `(1 - anchor_weight)`. When a new price regime begins -- for instance, when fundamental value shifts -- HistoricalAnchor's 60-round historical average takes many rounds to update, creating a regime-transition anchoring effect that resists the new equilibrium for an extended period.

#### 4.2.2  Theoretical and Empirical Foundation

**Expert Anchoring to Historical Prices**:
- Theory / Study: Anchoring Effects in Expert Valuation
- Citation: Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective. *Organizational Behavior and Human Decision Processes*, 39(1), 84-97. https://doi.org/10.1016/0749-5978(87)90046-X
- Core Insight: Expert appraisers anchor to historical comparable prices ("comps") when estimating current value. Their adjustments from this historical anchor toward current market conditions are systematically insufficient. Expert anchoring (12% toward anchor) is real but weaker than novice anchoring (21%).
- Mathematical Formulation: `perceived_dev = (price - hist_avg) / hist_avg x (1 - anchor_weight)`. With anchor_weight = 0.5, only 50% of the raw deviation from historical average is perceived -- the rest is dismissed as noise.
- Empirical Evidence: In financial markets, mean-reversion traders (analysts who anchor to historical P/E averages) systematically under-react to regime changes in fundamental value, as documented by Lakonishok, Shleifer & Vishny (1994) who find that "value traps" form when analysts anchor to historical high-P/E and ignore structural deterioration.
- Relevance to This Investor: `anchor_weight = 0.5` calibrated to Northcraft & Neale's professional expert anchoring magnitude (~12% toward anchor, vs. 50% for `anchor_weight`); `lookback = 60` represents ~60 trading days (one quarter), consistent with the "current quarter vs. prior quarter" anchoring documented in Campbell & Sharpe (2009).

**Mean Reversion Heuristic and Its Failure**:
- Theory / Study: Mean Reversion as Anchoring to Historical Average
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreacttheta *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Investors overreact to recent events and anchor to the belief that prices will revert to historical averages. "Winner" stocks (with recent gains) are sold because they are expected to mean-revert, while "loser" stocks are bought in expectation of recovery. This creates excess return predictability that contradicts the efficient market hypothesis.
- Mathematical Formulation: `hist_avg = (1/lookback) x Σ_{t-lookback}^{t} P(t)` -- rolling arithmetic average as the mean-reversion anchor. `perceived_dev = (price - hist_avg) / hist_avg x (1 - anchor_weight)`.
- Empirical Evidence: De Bondt & Thaler (1985) find that portfolios of extreme losers outperform extreme winners by 25% over 3 years, consistent with historical-mean anchoring causing systematic overreaction that is later corrected.
- Relevance to This Investor: HistoricalAnchor's 60-round rolling average embodies the De Bondt-Thaler mean-reversion belief; in a regime where prices are persistently above F, the rolling average itself becomes anchored above F, creating a self-reinforcing anchoring cycle.

#### 4.2.3  Design Purpose and Activation Scenarios

Purpose: HistoricalAnchor introduces regime-dependent anchoring -- its resistance to correction depends on how long prices have been elevated. In the early rounds (before history fills with above-fundamental prices), it anchors to its initial price history; after many rounds of above-F prices, its average drifts up, reducing its corrective force and sustaining mispricings.

Activation Scenarios:
- Price below historical average by > 3%: Buys; interprets recent decline as a deviation from the "correct" long-run level.
- Price above historical average by > 3%: Sells; interprets recent rise as mean-reversion opportunity.
- Within ±3% of historical average: Holds.

Market Contribution: **Destabilising** -- creates regime-dependent price stickiness. When the market has been elevated for many rounds, HistoricalAnchor's rolling average rises with it, reducing its selling pressure and allowing the mispricing to persist.

Interaction with other agents: Complements AnchoredTrader (both resist correction but from different anchor types); opposes RationalUpdater; MomentumTrader may temporarily align with HistoricalAnchor when historical average and momentum point in the same direction.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                                                                                           |
|----------------------------------|------------|---------------------------------------------------------------------------------------------------------------------|
| `price`                          | Continuous | Current price; compared to historical average                                                                       |
| `price_history` (last 60 rounds) | Series     | Required for rolling average calculation; the longer the history, the more it encapsulates the sustained mispricing |

Does NOT use: `fundamental`, `deviation`. HistoricalAnchor ignores the true fundamental entirely -- its reference is historical price, not intrinsic value. This is the defining feature of its anchoring type.

**4.2.4.2  Core Behavioral Mechanism**

1. Maintains a rolling list of past prices (up to `lookback = 60` rounds).
2. Each round: computes `hist_avg = mean(price_history[-60:])`.
3. Computes perceived deviation: `perceived_dev = (price - hist_avg) / hist_avg x (1 - anchor_weight)`. The `(1 - 0.5) = 0.5` factor means only half of the raw price deviation from historical average is perceived.
4. If `perceived_dev < -0.03`: buys (price seems cheap vs. history).
5. If `perceived_dev > +0.03`: sells (price seems expensive vs. history).
6. Hold if within threshold.

**4.2.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  hist_avg(t)     = mean(price_history[-lookback:])   lookback = 60
  raw_dev(t)      = (P(t) - hist_avg(t)) / hist_avg(t)
  perceived_dev(t) = raw_dev(t) x (1 - anchor_weight)  anchor_weight = 0.5
  Buy:  perceived_dev(t) < -0.03
  Sell: perceived_dev(t) > +0.03
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(perceived_dev(t)) x 1000)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `price_history` -- rolling list of last 60 prices; updated each round
- Parameter definitions:

| Symbol              | Meaning                                                 | Config Path                    | Source                                                                                  |
|---------------------|---------------------------------------------------------|--------------------------------|-----------------------------------------------------------------------------------------|
| anchor_weight = 0.5 | Dampening factor; how strongly agent anchors to history | players.yml -> HistoricalAnchor | Campbell & Sharpe (2009): ~50% under-revision from historical baseline                  |
| lookback = 60       | Rolling average window                                  | players.yml -> HistoricalAnchor | One quarter (60 trading days); consistent with quarterly anchoring in Campbell & Sharpe |

**4.2.4.4  Behavioral Properties**

- Time horizon: Long-term -- 60-round lookback means history dominates current-price signal; regime changes take many rounds to register
- Risk tolerance: Medium -- trades at 3% perceived threshold; bounded position sizes
- Information asymmetry: None about fundamentals; has unique "memory" of price history that other agents lack
- Psychological profile: Representativeness heuristic (Tversky & Kahneman, 1974) -- uses historical average as representative of "normal" price; De Bondt & Thaler (1985) contrarian psychology -- buys underperformers, sells outperformers relative to historical mean

#### 4.2.5  Decision Process Walkthrough

```
Given:  price = 102.0,  hist_avg (last 60 rounds) = 104.5,  anchor_weight = 0.5

Step 1: Compute raw deviation
        raw_dev = (102.0 - 104.5) / 104.5 = -0.0239

Step 2: Apply anchor dampening
        perceived_dev = -0.0239 x (1 - 0.5) = -0.0120

Step 3: Compare to threshold
        |-0.0120| < 0.03 -> below threshold; HOLD

Result: Despite price being 2.4% below historical average, HistoricalAnchor perceives
        only 1.2% deviation after dampening -- insufficient to trigger a trade.
        This is how anchor_weight dampens corrective action.
```

#### 4.2.6  Worked Numerical Example

```
Market state:  price = 97.0,  hist_avg (60-round rolling) = 104.5

Calculation:
  raw_dev       = (97.0 - 104.5) / 104.5 = -0.0718
  perceived_dev = -0.0718 x 0.5 = -0.0359  (<-0.03 -> buy condition)
  Q*            = min(20.0, 0.0359 x 1000) = min(20.0, 35.9) = 20 shares (capped)

Decision: action = buy, quantity = 20, bid_price = 97.0

Rationale: Price has fallen 7.2% below historical average. HistoricalAnchor perceives this as
a 3.6% buying opportunity (50% of raw signal). Despite price being 3% BELOW true fundamental (100),
HistoricalAnchor buys because its reference is historical average (104.5), not fundamental (100).
This illustrates how historical anchoring can support prices even below fundamental value.
```

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                                                         | Notes                                                                          |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1 | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate. *OBHDP*, 39(1), 84-97. https://doi.org/10.1016/0749-5978(87)90046-X                                                | Core foundation; calibrates anchor_weight = 0.5 and expert anchoring magnitude |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts. *JFQA*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127                                                | Calibrates lookback = 60 (quarterly horizon) and persistence                   |
| 3 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreacttheta *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x                            | Grounds historical-mean anchoring in documented over/under-reaction cycle      |
| 4 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Documents anchoring to historical valuation ratios in institutional investors  |

---

## Source Docstring Excerpts

### Rule / `HistoricalAnchor`

```text
Anchors to historical average price, adjusts insufficiently.

Implements simulation-bases.md Section 4.2 -- HistoricalAnchor.
Theoretical basis: simulation-bases.md Section 2.2 (Northcraft & Neale, 1987).

Decision rule (simulation-bases.md Section 4.2 -- Rule-Based Behavior):
    hist_avg = mean of last `lookback` prices (rolling window)
    perceived_dev = (price - hist_avg) / hist_avg * (1 - anchor_weight)
    if abs(perceived_dev) > 0.03: trade in corrective direction
    quantity = min(base_position_size, abs(perceived_dev) * 1000)

Parameters (simulation-bases.md Section 6):
    anchor_weight: 0.5 (dampening factor; higher = stronger anchoring)
    lookback: 60 rounds (rolling window for historical average)
    base_position_size: loaded from extras["base_position_size"]
```

### LLM / `LLMHistoricalAnchor`

```text
LLM-driven historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
```

### RuleLLM / `RuleLLMHistoricalAnchor`

```text
RuleLLM historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
```

### Rag / `RagLLMHistoricalAnchor`

```text
RAG-augmented historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
```
