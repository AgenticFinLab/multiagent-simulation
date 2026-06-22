# BlackMonday1987 / Portfolio Insurer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | BlackMonday1987 |
| Agent type | Portfolio Insurer |
| Canonical class | `PortfolioInsurer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The PortfolioInsurer is a large institutional fund manager who has adopted the Leland-Rubinstein portfolio insurance strategy -- a dynamic hedging technique that mechanically reduces equity exposure as prices fall and rebuilds it as prices rise. In 1987, approximately $90-100 billion in institutional assets were managed under such strategies. The PortfolioInsurer's role in the simulation is to generate the primary cascade mechanism: each decline triggers selling that drives prices further down, which triggers more selling. The PortfolioInsurer is not acting irrationally -- it is following its mandate to protect capital -- but the collective behavior of many such agents creates a self-fulfilling crash.

## Financial Theory / Theoretical Basis

### Rule / `PortfolioInsurer`
- Theory: simulation-bases.md Section 4.1 -- PortfolioInsurer
- Theoretical basis: Leland & Rubinstein (1980) portfolio insurance; sells equities

### LLM / `LLMPortfolioInsurer`
- LLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMPortfolioInsurer`
- RuleLLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMPortfolioInsurer`
- RAG-augmented portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| hedge_ratio | Rule: `0.5`<br>RuleLLM: `0.5`<br>Rag: `0.5` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `1000.0`<br>LLM: `1000.0`<br>RuleLLM: `1000.0`<br>Rag: `1000.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.BlackMonday1987.LLM.prompts:LLM_PORTFOLIO_INSURER_SYS', 'user_message': 'examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_PORTFOLIO_INSURER_SYS', 'user_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.BlackMonday1987.Rag.prompts:RAG_PORTFOLIO_INSURER_SYS', 'user_message': 'examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rebalance_threshold | Rule: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | portfolio_insurer | Portfolio Insurer | `PortfolioInsurer` | 2 | `examples/BlackMonday1987/Rule/players.py` |
| LLM | portfolio_insurer | Portfolio Insurer | `LLMPortfolioInsurer` | 2 | `examples/BlackMonday1987/LLM/players.py` |
| RuleLLM | portfolio_insurer | Portfolio Insurer | `RuleLLMPortfolioInsurer` | 2 | `examples/BlackMonday1987/RuleLLM/players.py` |
| Rag | ragllm_portfolio_insurer | RAG Portfolio Insurer | `RagLLMPortfolioInsurer` | 2 | `examples/BlackMonday1987/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 PortfolioInsurer

#### 4.1.1  Summary

The PortfolioInsurer is a large institutional fund manager who has adopted the Leland-Rubinstein portfolio insurance strategy -- a dynamic hedging technique that mechanically reduces equity exposure as prices fall and rebuilds it as prices rise. In 1987, approximately $90-100 billion in institutional assets were managed under such strategies. The PortfolioInsurer's role in the simulation is to generate the primary cascade mechanism: each decline triggers selling that drives prices further down, which triggers more selling. The PortfolioInsurer is not acting irrationally -- it is following its mandate to protect capital -- but the collective behavior of many such agents creates a self-fulfilling crash.

#### 4.1.2  Theoretical and Empirical Foundation

**Theory 1: Portfolio Insurance via Dynamic Hedging (Leland & Rubinstein)**
- Theory / Study: Leland-Rubinstein Portfolio Insurance Strategy
- Citation: Leland, H. E. (1980). "Who should buy portfolio insurancetheta" *Journal of Finance*, 35(2), 581-594. DOI: 10.2307/2327419
- Core Insight: Portfolio insurance replicates a put option through delta-hedging: the hedge ratio Delta increases (more equity sold) as price falls below the insured level and decreases (equity bought back) as price recovers. The strategy guarantees a minimum portfolio value at the cost of reduced upside when prices rise.
- Mathematical Formulation: Delta(P, K, T) = N(d1) from Black-Scholes, where d1 = [ln(P/K) + (r + sigma²/2)T] / (sigma√T). As P falls below K (the protected level), Delta -> 0, meaning the entire position is sold. Simplified operational rule: sell_qty = hedge_ratio x |deviation| x |position| when deviation < -threshold.
- Empirical Evidence: Brady Commission (1988) documented that portfolio insurance selling represented ~$2 billion of NYSE sell orders on October 19, approximately 25-30% of total institutional selling. Rebalance thresholds in live strategies ranged from 2-5% deviation from peak.
- Relevance to This Investor: The PortfolioInsurer's sell condition (deviation < -0.02) and proportional sizing (hedge_ratio x |deviation| x position) directly operationalize the delta-hedging rule in discrete simulation rounds.

**Theory 2: Positive Feedback and Herd Behavior**
- Theory / Study: Systemic risk from correlated dynamic hedging strategies
- Citation: Shleifer, A., & Vishny, R. W. (1992). "The limits of arbitrage." *Journal of Finance*, 52(1), 35-55. DOI: 10.2307/2329555. Also: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Positive feedback investment strategies and destabilizing rational speculation." *Journal of Finance*, 45(2), 379-395. DOI: 10.2307/2328662
- Core Insight: When many traders follow momentum-based or delta-hedging rules, their collective behavior becomes a positive feedback loop: each agent's selling is individually rational, but the aggregate effect is a self-amplifying cascade. De Long et al. (1990) show that positive feedback traders can push prices far from fundamentals even when arbitrageurs know prices are wrong.
- Mathematical Formulation: With N insurers each selling S_i(t) ∝ |δ(t)|, total selling sumS_i(t) ∝ N x |δ(t)|. Price impact: δ(t+1) = δ(t) - lambda·N·k·|δ(t)| where k is the proportionality constant. This creates explosive dynamics when lambda·N·k > 1.
- Empirical Evidence: De Long et al. (1990) show that positive feedback strategies are destabilizing at scale; with $90B in portfolio insurance assets in 1987, the aggregate feedback coefficient lambda·N·k was estimated to exceed 1 during the cascade peak.
- Relevance to This Investor: The PortfolioInsurer's proportional selling formula is the building block of this aggregate positive feedback; the simulation with 2 selling agents (PortfolioInsurer + ProgramTrader) tests whether this feedback becomes explosive.

#### 4.1.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the primary cascade mechanism -- mechanical selling that depresses prices, triggering further selling, creating a self-reinforcing feedback loop. Without PortfolioInsurer, the simulation cannot reproduce a Black Monday-style crash.

**Activation Scenarios**:
- Scenario A (Small initial decline, -2% to -5%): PortfolioInsurer triggers at deviation = -0.02, sells proportionally small quantity; mild selling pressure initiates the cascade. This models the early-session portfolio insurance triggers on October 19.
- Scenario B (Deepening cascade, -5% to -15%): Selling quantity grows as |deviation| increases; PortfolioInsurer adds substantial downward pressure at each declining price level. Interacts with ProgramTrader which also activates at -1%.
- Scenario C (Extreme drawdown, > -15%): PortfolioInsurer may be buying back at small quantities (deviation > +0.02) during recovery; or exhausts cash and becomes inactive. Position constraints prevent infinite selling.

**Market Contribution**: Destabilizing -- primary driver of cascade initiation. Every 1% additional price decline increases PortfolioInsurer's sell quantity by (hedge_ratio x position) shares, creating convex downward pressure.

**Interaction with other agents**: Amplifies ProgramTrader (both sell on price declines; combined selling is greater than either alone); countered by ValueInvestor (which buys what PortfolioInsurer sells, but only at deep discounts); IndexArbitrageur may sell in parallel when prices exceed fair value, adding further pressure.

#### 4.1.4  Behavioral Framework

**4.1.4.1  Decision Information Set**
- `deviation`: Primary trigger and sizing signal -- PortfolioInsurer sells proportionally to |deviation| below threshold; consistent with delta-hedging where hedge ratio is an increasing function of price decline magnitude.
- `position`: Required for sell sizing -- can only sell what is owned; natural position limit on cascade contribution per agent instance.
- `cash`: Required for buy sizing -- constrains re-entry buying during recovery; consistent with institutional capital constraints.
- Does NOT use `price` level directly (only deviation); consistent with a relative-value framing where the insurance strategy is defined in terms of percentage decline from the insured level rather than an absolute price target.

**4.1.4.2  Core Behavioral Mechanism**
1. Each round, PortfolioInsurer observes `deviation = (price - fundamental) / fundamental`.
2. If deviation < -rebalance_threshold (-0.02): sell equity -- reduce exposure in proportion to deviation magnitude. This implements the delta-hedging rule: the further below the floor, the lower the target equity weight, the larger the required sell.
3. The sell quantity is `int(|deviation| x hedge_ratio x |position|)`, bounded below by 1. This proportionality means a -10% deviation triggers 5x the selling of a -2% deviation (for the same position size).
4. If deviation > +rebalance_threshold (+0.02): buy equity to rebuild exposure. Buy quantity: `int(deviation x hedge_ratio x cash / price)`, capped at 500 shares.
5. If |deviation| <= 0.02: no rebalance needed -- hold current position. This represents the "insurance" being within tolerance.
6. Position limit: PortfolioInsurer holds an initial_position of shares and initial_cash; cannot sell below zero shares or buy beyond cash constraint.

**4.1.4.3  Mathematical Model**
- Decision variable: sell/buy quantity Q*(t) in shares
- Trigger function: sell if δ(t) < -theta (theta = rebalance_threshold = 0.02); buy if δ(t) > +theta; hold otherwise
- Sell sizing function: Q*_sell(t) = int(|δ(t)| x h x |pos(t)|), where h = hedge_ratio = 0.5
- Buy sizing function: Q*_buy(t) = min(int(δ(t) x h x cash(t) / P(t)), 500)
- State variables: position (shares held, updated each round), cash (updated each trade)

| Parameter           | Value  | Meaning                                      | Config Path                                            | Source                                 |
|---------------------|--------|----------------------------------------------|--------------------------------------------------------|----------------------------------------|
| rebalance_threshold | 0.02   | Deviation below which selling is triggered   | `BlackMonday1987/Rule/config.yaml -> portfolio_insurer` | Leland (1980); Brady Commission (1988) |
| hedge_ratio         | 0.5    | Fraction of position sold per unit deviation | `BlackMonday1987/Rule/config.yaml -> portfolio_insurer` | Brady Commission (1988)                |
| initial_position    | 3000   | Starting share position                      | `BlackMonday1987/Rule/config.yaml -> portfolio_insurer` | Normalization                          |
| initial_cash        | 200000 | Starting cash reserves                       | `BlackMonday1987/Rule/config.yaml -> portfolio_insurer` | Normalization                          |

**4.1.4.4  Behavioral Properties**
- Time horizon: Short-term (rebalances every round in which threshold is crossed -- equivalent to continuous delta-hedging)
- Risk tolerance: Very Low -- capital protection mandate; the strategy exists precisely to limit losses; every sell is a risk-reduction action
- Information asymmetry: None -- uses only publicly observable price and fundamental; consistent with passive, rule-based execution
- Psychological profile: Mechanical and emotionally detached -- no discretion, no override. In LLM variants, the persona emphasizes rule adherence over narrative; consistent with De Long et al. (1990) positive-feedback strategy literature

#### 4.1.5  Decision Process Walkthrough

Given: price = 237.5, fundamental = 250.0, deviation = -0.05, position = 3000, cash = 200000

Step 1: Observe deviation = -0.05. Is -0.05 < -0.02 (rebalance_threshold)theta YES -> sell.
Step 2: Compute sell quantity: Q = int(|-0.05| x 0.5 x 1000) = int(0.05 x 0.5 x 1000) = int(25) = 25 shares.
Step 3: Position after sell: 1000 - 25 = 975 shares; cash after sell: 500000 + 25 x 237.5 = 505937.5.
Step 4: Send order: action=sell, quantity=25, bid_price=237.5.
Step 5: Net market impact: -25 shares added to D(t); partial contribution to downward price pressure of lambda x 25 = 0.05 x 25 = 1.25 price units.

Note: At deviation = -0.10 with same position (1000), Q = int(0.10 x 0.5 x 1000) = 50 -- double the sell quantity, illustrating the convex amplification.

#### 4.1.6  Worked Numerical Example

Market state: price = 227.5, fundamental = 250.0, deviation = -0.09, position = 975, cash = 505937.5

Trigger check: -0.09 < -0.02 -> sell condition active.
Sell quantity: Q = int(|-0.09| x 0.5 x 975) = int(0.09 x 0.5 x 975) = int(43) = 43 shares.
Updated position: 975 - 43 = 932. Updated cash: 505937.5 + 43 x 227.5 = 515720.0.
Order sent: action=sell, quantity=43, bid_price=227.5.
Rationale: A 9% price decline requires the insurer to reduce equity exposure by ~4.5% of position (hedge_ratio x deviation), consistent with the delta-hedging rule that demands lower equity weight at lower prices.

#### 4.1.7  Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | Leland, H. E. (1980). "Who should buy portfolio insurancetheta" *Journal of Finance*, 35(2), 581-594. DOI: 10.2307/2327419                                                                                               | Core theoretical basis for proportional selling rule and hedge ratio concept       |
| 2 | Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office.                                                                                              | Empirical calibration of rebalance_threshold, hedge_ratio; documented volume data  |
| 3 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Positive feedback investment strategies and destabilizing rational speculation." *Journal of Finance*, 45(2), 379-395. DOI: 10.2307/2328662 | Theoretical analysis of systemic risk from correlated positive-feedback strategies |


---

## Source Docstring Excerpts

### Rule / `PortfolioInsurer`

```text
Dynamic hedging -- sells as prices fall (destabilizing).

Theory: simulation-bases.md Section 4.1 -- PortfolioInsurer
Theoretical basis: Leland & Rubinstein (1980) portfolio insurance; sells equities
as prices fall to maintain a synthetic put, creating a positive feedback loop.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMPortfolioInsurer`

```text
LLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMPortfolioInsurer`

```text
RuleLLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMPortfolioInsurer`

```text
RAG-augmented portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
```
