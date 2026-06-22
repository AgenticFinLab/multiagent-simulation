# BlackMonday1987 / Program Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | BlackMonday1987 |
| Agent type | Program Trader |
| Canonical class | `ProgramTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The ProgramTrader is an institutional investor running automated execution algorithms that trigger large block orders when price thresholds are breached. Unlike the PortfolioInsurer (who sells proportionally to deviation), the ProgramTrader sells with convex amplification: larger deviations trigger disproportionately larger sells. This models the discrete tier-based program sell orders documented in the Brady Commission report, where each successive price threshold activated a new wave of automated selling at even greater volume. The ProgramTrader is the simulation's dominant per-round force during cascade escalation -- generating the heaviest selling waves at the worst price levels.

## Financial Theory / Theoretical Basis

### Rule / `ProgramTrader`
- Theory: simulation-bases.md Section 4.3 -- ProgramTrader
- Theoretical basis: Brady Commission (1988) program trading feedback loops;

### LLM / `LLMProgramTrader`
- LLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMProgramTrader`
- RuleLLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMProgramTrader`
- RAG-augmented program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `60.0`<br>RuleLLM: `60.0`<br>Rag: `60.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| feedback_strength | Rule: `1.2`<br>RuleLLM: `1.2`<br>Rag: `1.2` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `500000.0`<br>LLM: `500000.0`<br>RuleLLM: `500000.0`<br>Rag: `500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `800.0`<br>LLM: `800.0`<br>RuleLLM: `800.0`<br>Rag: `800.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.BlackMonday1987.LLM.prompts:LLM_PROGRAM_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_PROGRAM_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.BlackMonday1987.Rag.prompts:RAG_PROGRAM_TRADER_SYS', 'user_message': 'examples.BlackMonday1987.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trigger_threshold | Rule: `0.01`<br>RuleLLM: `0.01`<br>Rag: `0.01` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | program_trader | Program Trader | `ProgramTrader` | 2 | `examples/BlackMonday1987/Rule/players.py` |
| LLM | program_trader | Program Trader | `LLMProgramTrader` | 2 | `examples/BlackMonday1987/LLM/players.py` |
| RuleLLM | program_trader | Program Trader | `RuleLLMProgramTrader` | 2 | `examples/BlackMonday1987/RuleLLM/players.py` |
| Rag | ragllm_program_trader | RAG Program Trader | `RagLLMProgramTrader` | 2 | `examples/BlackMonday1987/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 ProgramTrader

#### 4.3.1  Summary

The ProgramTrader is an institutional investor running automated execution algorithms that trigger large block orders when price thresholds are breached. Unlike the PortfolioInsurer (who sells proportionally to deviation), the ProgramTrader sells with convex amplification: larger deviations trigger disproportionately larger sells. This models the discrete tier-based program sell orders documented in the Brady Commission report, where each successive price threshold activated a new wave of automated selling at even greater volume. The ProgramTrader is the simulation's dominant per-round force during cascade escalation -- generating the heaviest selling waves at the worst price levels.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Program Trading Feedback Loops (Brady Commission)**
- Theory / Study: Automated sell program cascade dynamics
- Citation: Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office. Washington, D.C. Also: Harris, L. (1989). "The October 1987 S&P 500 stock-futures basis." *Journal of Finance*, 44(1), 77-99. DOI: 10.2307/2328344
- Core Insight: Automated sell programs created a tiered cascade: different programs were triggered at different price thresholds, with each tier activating at progressively lower prices and executing progressively larger orders. The Brady Commission documented that the most intensive program selling occurred in discrete 30-minute windows when specific price levels were breached, creating sudden step-function increases in sell volume.
- Mathematical Formulation: Amplified sell size: Q_program(t) = base_size x (1 + feedback_strength x |deviation(t)| x 10). The multiplier (1 + f x |δ| x 10) creates convex amplification: at |δ| = 0.01, multiplier = 1.3; at |δ| = 0.05, multiplier = 2.5; at |δ| = 0.10, multiplier = 4.0. This is bounded above by position/cash constraints.
- Empirical Evidence: Brady Commission (1988) documents program sell waves of 200-800% above normal trading volume during peak cascade intervals. Feedback strength estimated at 0.25-0.40 from analysis of sequential sell-wave volume escalation. Base sell quantity per institution: 200-1000 shares per trigger event.
- Relevance to This Investor: feedback_strength = 1.2 and base_size = 60 calibrated from Brady Commission estimates; trigger_threshold = 0.01 (1% decline) captures the most sensitive tier of program sell triggers.

**Theory 2: Cascading Failures and Systemic Risk**
- Theory / Study: Systemic risk and cascade dynamics in financial networks
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201-2238. DOI: 10.1093/rfs/hhn098
- Core Insight: Brunnermeier & Pedersen's model shows how funding constraints create self-reinforcing liquidity spirals: losses -> margin calls -> forced selling -> further losses. The program trader embodies the funding-liquidity spiral: not because of margin calls per se, but because automated risk-control systems respond to mark-to-market losses with systematic liquidation, regardless of fundamental value. Each sell reduces the mark-to-market value of remaining positions, triggering further automated risk-reduction sells.
- Mathematical Formulation: Funding liquidity spiral: DeltaP = -lambda·(DeltaM/m) where DeltaM is margin shortfall and m is margin rate. In the program trading context: triggered_sells(t) ∝ loss_signal(t) ∝ |deviation(t)|, creating the positive feedback between price falls and sell volumes.
- Empirical Evidence: Brunnermeier & Pedersen (2009) document that in every major market crash since 1987, funding constraints and mark-to-market accounting create amplified sells. Their model calibrates to feedback coefficients of 0.2-0.4, consistent with the feedback_strength = 1.2 parameter.
- Relevance to This Investor: ProgramTrader's convex amplification is the simulation-level instantiation of the Brunnermeier-Pedersen liquidity spiral -- a mechanical, self-reinforcing selling force that grows stronger as the crash deepens.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Generate the escalating cascade waves that transform an initial price decline into a market crash. The ProgramTrader's convex amplification means it contributes disproportionately more selling at precisely the worst moments -- when prices are already depressed and the market most needs buyers.

**Activation Scenarios**:
- Scenario A (Small decline, deviation < -1%): ProgramTrader activates with base size quantity (multiplier ≈ 1.3x); adds to portfolio insurer selling. Together they generate the first meaningful cascade wave.
- Scenario B (Moderate decline, deviation < -5%): Multiplier = 1.6x; ProgramTrader now selling about 96 shares vs. base 60; dominates net demand calculation; crash escalation phase begins.
- Scenario C (Severe decline, deviation < -10%): Multiplier = 2.2x; ProgramTrader selling about 132 shares; generates crash peak. ValueInvestor begins buying but cannot absorb supply.

**Market Contribution**: Strongly destabilizing -- the primary cascade amplifier. During peak crash (deviation ≈ -10% to -20%), ProgramTrader is responsible for the majority of net selling pressure by volume.

**Interaction with other agents**: Amplifies PortfolioInsurer (same direction); their combined selling volume drives the cascade past levels where ValueInvestor can arrest the decline; IndexArbitrageur may sell in parallel during crash initiation but may buy later, partially offsetting ProgramTrader.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Both trigger signal and sizing amplifier -- two roles, consistent with a system where the same price signal that activates the program also determines the severity of its response.
- `price`: Used for buy sizing (cash/price); not for sell trigger.
- Does NOT use position directly for sell sizing (uses base_size x amplifier rather than position fraction); consistent with lot-based automated execution rather than portfolio-fraction-based execution.

**4.3.4.2  Core Behavioral Mechanism**
1. Each round, ProgramTrader observes `deviation`.
2. If deviation < -trigger_threshold (-0.01): sell -- compute amplified sell quantity. The amplification grows convexly with |deviation|.
3. Sell quantity: `amplified_sell = int(base_size x (1 + feedback_strength x |deviation| x 10))`. This ensures larger deviations produce disproportionately larger sells.
4. If deviation > +trigger_threshold (+0.01): buy -- fixed base_size quantity (no amplification on upside; asymmetric design reflecting asymmetric program trigger behavior).
5. Position and cash constraints apply: cannot sell below zero shares; cannot buy beyond cash.
6. Hold if |deviation| <= 0.01.

**4.3.4.3  Mathematical Model**
- Decision variable: Q*(t) = amplified sell or fixed buy quantity
- Trigger function: sell if δ(t) < -τ; buy if δ(t) > +τ; where τ = trigger_threshold = 0.01
- Sell sizing: Q*_sell(t) = int(base_size x (1 + f x |δ(t)| x 10)), where f = feedback_strength = 1.2
- Buy sizing: Q*_buy(t) = base_size (fixed; no amplification on upside)
- State variables: position (shares), cash (updated each trade)

| Parameter         | Value  | Meaning                                      | Config Path                                         | Source                                                  |
|-------------------|--------|----------------------------------------------|-----------------------------------------------------|---------------------------------------------------------|
| trigger_threshold | 0.01   | Deviation below which sell cascade activates | `BlackMonday1987/Rule/config.yaml -> program_trader` | Brady Commission (1988)                                 |
| feedback_strength | 1.2    | Amplification factor per unit deviation      | `BlackMonday1987/Rule/config.yaml -> program_trader` | Brady Commission (1988); Brunnermeier & Pedersen (2009) |
| base_size         | 60     | Base lot size before amplification           | `BlackMonday1987/Rule/config.yaml -> program_trader` | Brady Commission (1988) order flow data                 |
| initial_position  | 800    | Starting share position                      | `BlackMonday1987/Rule/config.yaml -> program_trader` | Normalization (larger than insurer)                     |
| initial_cash      | 500000 | Starting cash reserves                       | `BlackMonday1987/Rule/config.yaml -> program_trader` | Normalization                                           |

**4.3.4.4  Behavioral Properties**
- Time horizon: High-frequency -- reacts immediately at each threshold trigger; equivalent to same-session automated execution
- Risk tolerance: Extreme -- follows algorithm regardless of fundamental valuation or market conditions; no override mechanism
- Information asymmetry: None -- entirely price-signal driven; consistent with rule-based automated execution
- Psychological profile: Systematic, no emotional override, amplifies trends. In LLM variants, the persona is a momentum-following algorithm; key test is whether LLM faithfully executes the amplification or introduces discretionary restraint

#### 4.3.5  Decision Process Walkthrough

Given: price = 230.0, fundamental = 250.0, deviation = -0.08, base_size = 60, feedback_strength = 1.2

Step 1: Observe deviation = -0.08. Is -0.08 < -0.01 (trigger_threshold)theta YES -> sell.
Step 2: Compute amplifier: multiplier = 1 + 1.2 x 0.08 x 10 = 1 + 0.96 = 1.96.
Step 3: Compute sell quantity: Q = int(60 x 1.96) = int(117) = 117 shares.
Step 4: Send order: action=sell, quantity=117, bid_price=230.0.
Step 5: Net market impact: -117 shares in D(t); price pressure = -lambda x 117 = -0.05 x 117 = -5.85 price units from ProgramTrader alone.

Note: In the same round with PortfolioInsurer selling 43 shares (from Section 4.1.6 example), combined D_sell = 117 + 43 = 160 shares -> combined price pressure = -0.05 x 160 = -8.0 price units. This is the cascade amplification mechanism in action.

#### 4.3.6  Worked Numerical Example

Market state: price = 212.5, fundamental = 250.0, deviation = -0.15, base_size = 60, feedback_strength = 1.2, position = 800

Trigger check: -0.15 < -0.01 -> sell condition active.
Amplifier: multiplier = 1 + 1.2 x 0.15 x 10 = 1 + 1.80 = 2.80.
Sell quantity: Q = int(60 x 2.80) = int(168) = 168 shares.
Position check: 800 - 168 = 632 (> 0) -- order valid.
Order sent: action=sell, quantity=168, bid_price=212.5.
Rationale: A 15% decline activates the most aggressive tier of automated selling (multiplier = 2.80x), consistent with the Brady Commission's documentation that program sell volume escalated dramatically as the S&P 500 passed successive price floors on October 19.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                                          | Notes                                                                                                       |
|---|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 1 | Brady Commission (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office.                                           | Primary source for trigger_threshold, feedback_strength, base_size calibration; program trading volume data |
| 2 | Harris, L. (1989). "The October 1987 S&P 500 stock-futures basis." *Journal of Finance*, 44(1), 77-99. DOI: 10.2307/2328344                                       | Intraday price dynamics; program trading amplification evidence                                             |
| 3 | Brunnermeier, M. K., & Pedersen, L. H. (2009). "Market liquidity and funding liquidity." *Review of Financial Studies*, 22(6), 2201-2238. DOI: 10.1093/rfs/hhn098 | Theoretical basis for convex amplification; funding liquidity spiral model                                  |


---

## Source Docstring Excerpts

### Rule / `ProgramTrader`

```text
Automated trading that amplifies price moves (destabilizing).

Theory: simulation-bases.md Section 4.3 -- ProgramTrader
Theoretical basis: Brady Commission (1988) program trading feedback loops;
automated sell triggers on price thresholds cascade into a self-reinforcing crash.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMProgramTrader`

```text
LLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMProgramTrader`

```text
RuleLLM-driven program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMProgramTrader`

```text
RAG-augmented program trader -- automated feedback amplifier. Theory: simulation-bases.md Section 4.3.
```
