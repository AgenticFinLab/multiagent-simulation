# DotComBubble Simulation Bases

## §1 Phenomenon

**Dot-Com Bubble (1995–2001)**: NASDAQ Composite Index rose approximately 400% from 1995 to peak in March 2000, then fell 78% by October 2002. The bubble was driven by speculative investment in internet companies, narrative economics, IPO frenzy, and disconnection from fundamental valuation metrics. It represents the canonical example of technology-driven speculative excess with subsequent market crash.

**Core stylized facts**:
- NASDAQ rose from ~750 (1995) to ~5,048 (March 2000)
- Peak-to-trough decline: 78% over 30 months
- Average dot-com IPO first-day return: 89% (1999)
- P/E ratios for tech stocks exceeded 100× (vs. historical average ~15×)

## §2 Theory

### Primary: Narrative Economics (Shiller, 2000; 2019)

Speculative bubbles are driven by compelling stories that capture public imagination — "the internet changes everything." Narrative contagion spreads investor enthusiasm beyond what fundamentals support.

DOI: Shiller (2000) *Irrational Exuberance* — https://doi.org/10.1515/9781400865536

### IPO Dynamics (Ofek & Richardson, 2003)

Internet IPOs exhibited extreme initial underpricing (+89% average first-day returns in 1999). Lock-up expiration created predictable selling pressure. Flipper behavior amplified initial volatility.

DOI: https://doi.org/10.1111/1540-6261.00530

### Limits to Arbitrage / Synchronization Risk (Abreu & Brunnermeier, 2003)

Rational arbitrageurs (short sellers) who correctly identify the bubble cannot coordinate timing of their attacks. Each waits for others to act first, allowing the bubble to persist far beyond fundamental value. Momentum traders exploit this delay.

DOI: https://doi.org/10.1111/1468-0262.00401

### Momentum Trading (Jegadeesh & Titman, 1993)

Short-term price continuation: stocks that performed well recently continue to perform well over 3–12 months. During bubbles, momentum followers amplify upward price moves by buying recent winners.

DOI: https://doi.org/10.1111/j.1540-6261.1993.tb04702.x

### Value Investing (Graham, 1949)

Fundamental investors avoid overvalued assets and wait for price to revert to intrinsic value. During bubbles, value investors are "too early" and face prolonged drawdowns before vindication.

Reference: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.

## §3 Market Design

**Price Formation**:
```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
```
Where:
- λ = price impact coefficient (0.01)
- γ = mean reversion rate (0.005, weaker than typical — bubble persistence)
- F(t) = fundamental value (100.0)
- ε(t) ~ N(0, σ²) with σ = noise_std

**Weak mean reversion** (γ = 0.005) allows bubble to persist for many rounds before collapsing — calibrated to dot-com bubble's multi-year duration. Market broadcasts `{price, fundamental, deviation, round}`.

## §4 Investor Taxonomy

### §4.1 NewEconomyEvangelist

**Role**: Primary bubble driver — narrative-driven buyer ignoring traditional valuation.

**Economic Archetype**: Retail and institutional investor swept up in "new economy" narrative; dismisses P/E ratios as irrelevant to internet companies.

**Theoretical Basis**: Shiller (2000) narrative economics; Shiller (2019) *Narrative Economics* — stories spread virally and drive collective investment behavior.

**Decision Logic**:
- Buy `order_size (600)` when `deviation > −0.20` (buys even when overvalued)
- Only sell at `deviation < −0.30` (sells only at extreme crash)

**Key Parameters**:
- `order_size = 600`
- Sell threshold: `−0.30` (only capitulates in extreme crash)

**Market Impact**: Persistent buyer at almost any price — primary force inflating the bubble.

**Performance**: Expected to peak during bubble and crash severely in post-bubble collapse.

---

### §4.2 IPOFlipper

**Role**: Short-term profit-taker exploiting IPO underpricing.

**Economic Archetype**: Institutional allocatee or retail investor who participates in IPOs for first-day pop profit; quickly sells after listing.

**Theoretical Basis**: Ofek & Richardson (2003) IPO dynamics; Ritter (1991) IPO underpricing — first-day returns average 89% in 1999.

**Decision Logic**:
- Sell `order_size (700)` when `deviation > flip_threshold (0.05)` — flip after pop
- Buy when `deviation < 0` — accumulate for next flip opportunity

**Key Parameters**:
- `order_size = 700`
- `flip_threshold = 0.05` (flip when 5% above fundamental)

**Market Impact**: Creates selling pressure above fundamental; adds buying pressure at dips. Amplifies volatility.

**Performance**: Expected positive returns from flipping but exposed to post-bubble downdraft on held positions.

---

### §4.3 MomentumFollower

**Role**: Trend-chasing amplifier that rides the bubble higher.

**Economic Archetype**: Technical trader or trend-following algorithm that buys recent winners and sells recent losers.

**Theoretical Basis**: Abreu & Brunnermeier (2003) synchronization — momentum traders exploit arbitrageurs' hesitation; Jegadeesh & Titman (1993) momentum returns.

**Decision Logic**:
- Compute 1-period momentum: `m = (P[-1] − P[-2]) / P[-2]`
- Buy `order_size (500)` when `m > momentum_threshold (0.02)`
- Sell when `m < −momentum_threshold`

**Key Parameters**:
- `order_size = 500`
- `momentum_threshold = 0.02` (2% price change triggers trend-follow)

**Market Impact**: Amplifies both up and down moves; extends bubble duration during uptrend; accelerates crash during downtrend.

**Performance**: Profitable during bubble ascent; heavy losses if trend reversal is missed.

---

### §4.4 SkepticalValueInvestor

**Role**: Stabilizing fundamental investor who waits for overvaluation correction.

**Economic Archetype**: Graham-style value investor who correctly identifies bubble but cannot time the top.

**Theoretical Basis**: Graham (1949) value investing — buy below intrinsic value, sell above; Abreu & Brunnermeier (2003) — rational arbitrageurs are correct but early.

**Decision Logic**:
- Buy `order_size (400)` when `deviation < value_buy_threshold (−0.10)` — post-crash value buying
- Sell `order_size` when `deviation > value_sell_threshold (0.20)` — exits extreme overvaluation

**Key Parameters**:
- `order_size = 400`
- `value_buy_threshold = −0.10` (buy after 10% crash)
- `value_sell_threshold = 0.20` (sell at 20% overvaluation)

**Market Impact**: Stabilizing — provides fundamental anchor through value-based trading.

**Performance**: Underperforms during bubble peak (sells too early); outperforms post-crash.

---

### §4.5 ShortSeller

**Role**: Bet-against-overvaluation agent constrained by squeeze risk.

**Economic Archetype**: Hedge fund short seller who correctly identifies overvaluation but faces mark-to-market losses and position limits.

**Theoretical Basis**: Abreu & Brunnermeier (2003) limits to arbitrage — short sellers face synchronization risk; cannot sustain short positions indefinitely.

**Decision Logic**:
- Sell `order_size (400)` when `deviation > short_threshold (0.15)` — short overvalued assets
- Buy (cover shorts) when `deviation < cover_threshold (−0.05)` — cover as price falls

**Key Parameters**:
- `order_size = 400`
- `short_threshold = 0.15` (short when 15% above fundamental)
- `cover_threshold = −0.05` (cover when 5% below fundamental)

**Market Impact**: Selling pressure limits bubble height; but insufficient to prevent extreme overvaluation.

**Performance**: Losses during bubble ascent (short squeeze); profits at crash.

---

## §5 Agent Diversity

| Investor               | Theoretical Archetype                            | Bubble Role   | Key Mechanism          |
|------------------------|--------------------------------------------------|---------------|------------------------|
| NewEconomyEvangelist   | Narrative economics (Shiller, 2000)              | Destabilizing | Ignores valuation      |
| IPOFlipper             | IPO dynamics (Ofek & Richardson, 2003)           | Destabilizing | Short-term flip profit |
| MomentumFollower       | Momentum (Jegadeesh & Titman, 1993)              | Destabilizing | Trend amplification    |
| SkepticalValueInvestor | Value investing (Graham, 1949)                   | Stabilizing   | Fundamental anchor     |
| ShortSeller            | Limits to arbitrage (Abreu & Brunnermeier, 2003) | Stabilizing   | Short overvaluation    |

## §6 Parameter Table

| Parameter                           | Default | Description                                      |
|-------------------------------------|---------|--------------------------------------------------|
| `initial_price`                     | 100.0   | Starting market price                            |
| `fundamental_value`                 | 100.0   | Long-run fundamental (P/E fair value)            |
| `price_impact`                      | 0.01    | λ in price equation                              |
| `mean_reversion`                    | 0.005   | γ in price equation (low for bubble persistence) |
| `noise_std`                         | 1.0     | σ for Gaussian noise                             |
| `order_size` (NewEconomyEvangelist) | 600     | Buy quantity per round                           |
| `order_size` (IPOFlipper)           | 700     | Flip quantity per round                          |
| `flip_threshold`                    | 0.05    | δ above which IPOFlipper sells                   |
| `order_size` (MomentumFollower)     | 500     | Trend-following quantity                         |
| `momentum_threshold`                | 0.02    | 1-period return trigger for momentum             |
| `value_buy_threshold`               | −0.10   | SkepticalValueInvestor buy trigger               |
| `value_sell_threshold`              | 0.20    | SkepticalValueInvestor sell trigger              |
| `short_threshold`                   | 0.15    | ShortSeller short trigger                        |
| `cover_threshold`                   | −0.05   | ShortSeller cover trigger                        |

## §7 Round Structure

1. **Market.perceive()**: Collects all investor orders.
2. **Market.decide()**: Computes net demand; applies price equation; records price history.
3. **Market.act()**: Broadcasts `{price, fundamental, deviation, round}` to all investors.
4. **Investor.perceive()**: Updates `market_data`; appends to `price_history`.
5. **Investor.decide()**: Applies investor-specific logic; returns `{action, quantity}`.
6. **Investor.act()**: Executes trade — updates `cash`, `position`.

## §8 Historical Cases

### NASDAQ Dot-Com Bubble (1995–2001)

NASDAQ rose from 750 to 5,048 (+573%) peak in March 2000. Then fell to 1,114 (−78%) by October 2002. By 2015, NASDAQ had finally recovered to 2000 levels. Companies like Pets.com, Webvan, and Kozmo raised hundreds of millions before collapse. Short sellers like Julian Robertson (Tiger Management) and David Einhorn correctly called bubble but suffered massive losses before the crash.

### IPO Market 1999

489 IPOs in 1999; average first-day return 89%. VA Linux up 698% on day 1. Goldman Sachs IPO: 71% first-day gain. Many companies had no revenue.

### Short Sellers

Abreu & Brunnermeier (2003) shows arbitrageurs face synchronization risk — each rational short seller waits for others to short first, allowing the bubble to persist. When bubble eventually deflates, shorts profit but many had already been squeezed out.

## §9 Variant Comparison

| Aspect                | Rule                                   | LLM                                                    | RuleLLM                     | Rag                                               |
|-----------------------|----------------------------------------|--------------------------------------------------------|-----------------------------|---------------------------------------------------|
| Bubble height         | Mechanical; ≈ 15–25% above fundamental | Variable; LLM narrative conviction drives higher peaks | Close to Rule               | RAG historical cases moderate extreme conviction  |
| Crash timing          | Parameter-driven                       | LLM may anticipate or delay crash via reasoning        | Rule-anchored               | RAG may identify crash patterns from 1929 or 2000 |
| Short seller behavior | Threshold-based                        | LLM may exhibit squeeze panic                          | Rule threshold preserved    | RAG synchronization risk knowledge affects timing |
| Momentum              | 1-period return signal                 | LLM trend-following may use longer context             | Embedded signal + LLM       | RAG momentum research informs trend behavior      |
| Research value        | Mechanism baseline                     | LLM narrative realism                                  | Rule compliance + reasoning | Historical bubble knowledge integration           |
