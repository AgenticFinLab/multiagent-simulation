# OverconfidenceBias Simulation Bases

## §1 Phenomenon Definition

Overconfidence bias describes investors who overestimate the precision of their
signals, over-attribute favorable outcomes to skill, and trade more aggressively
than warranted by fundamentals. In financial markets this produces excess
turnover, large directional order flow, and volatility that is difficult to
explain with public information alone.

This scenario models a single risky asset with a stable fundamental anchor.
Overconfident and self-attributing agents create destabilizing order flow;
calibrated and contrarian agents provide benchmark discipline; noise traders
add background liquidity. The mechanism is intentionally local and transparent:
the bias appears through order frequency, order size, direction, and resulting
price deviations.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

The intellectual lineage starts with psychological calibration research showing
that people are often too certain about uncertain judgments. Behavioral finance
then connects overprecision to market trading: investors who believe their
signals are unusually accurate should trade too often, take larger positions,
and underweight the possibility that their signals are noise.

Daniel, Hirshleifer, and Subrahmanyam (1998) formalize investor overconfidence
and biased self-attribution as a source of market overreaction and subsequent
correction. Odean (1998) shows theoretically that when traders believe they are
above average, volume and volatility can rise even without superior information.
Barber and Odean (2001) connect the mechanism to household trading records and
show that groups expected to be more overconfident trade more and perform worse.

This simulation translates that lineage into agent roles. OverconfidentTrader
inflates perceived signal strength, SelfAttributor reinforces confidence after
favorable conditions, CalibratedTrader supplies the rational benchmark,
ContrarianInvestor fades bias-driven deviations, and NoiseTrader creates
uninformed background order flow.

#### §1.1.2 Real-World Event Catalogue

| Event | Magnitude | Agent Correspondence | Calibration Lesson |
|---|---:|---|---|
| Late-1990s retail internet-stock trading | NASDAQ rose about 86% in 1999 and fell about 78% from 2000 peak to 2002 trough | OverconfidentTrader, NoiseTrader, ContrarianInvestor | High confidence and frequent trading can amplify price-fundamental deviations. |
| Barber-Odean household brokerage sample | Men traded about 45% more than women and earned lower net returns | OverconfidentTrader, CalibratedTrader | Excess turnover is the primary empirical signature. |
| Day-trading waves in Taiwan equity markets | Empirical studies find persistent high turnover and poor average day-trader performance | OverconfidentTrader, SelfAttributor, NoiseTrader | Active traders can repeatedly attribute wins to skill while ignoring base rates. |
| Meme-stock retail surges in 2021 | GameStop rose more than 1,500% from early January lows to intramonth highs | SelfAttributor, NoiseTrader, ContrarianInvestor | Confidence, social reinforcement, and contrarian pressure can coexist. |

#### §1.1.3 Book and Practitioner Literature

Barber and Odean's investor-account studies are complemented by practitioner
accounts of day-trading booms and retail brokerage behavior. These accounts
emphasize the same operational mechanism used here: investors interpret recent
success as evidence of skill, increase trade frequency, and discover only later
that turnover costs and noise overwhelm perceived information.

Practitioner risk-management discussions after retail trading waves also
highlight contrarian and calibrated participants. They do not eliminate biased
flow, but they provide the stabilizing benchmark needed to diagnose whether
observed volume comes from overconfidence rather than from market-wide news.

## §2 Theoretical Foundation

### §2.1 Overconfidence and Biased Self-Attribution

**Citation**: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor
psychology and security market under- and overreactions. *Journal of Finance*.
DOI: `10.1111/0022-1082.00077`.

**Core Theoretical Mechanism**: Investors overestimate the precision of private
signals and update confidence asymmetrically. Positive outcomes are interpreted
as evidence of skill, while negative outcomes are discounted as bad luck or
transitory noise. This creates excessive conviction and can drive prices away
from fundamental value.

**Mathematical Formulation**: The simulation represents perceived signal as
`s_hat = precision_overestimate * deviation`, where `deviation = (P - F) / F`.
Self-attribution appears through a confidence multiplier applied to order size
when the trader holds inventory and current conditions are favorable.

**Empirical Evidence**: The theory is consistent with high trading frequency,
post-success risk escalation, and later reversal when exaggerated beliefs are
not validated by fundamentals.

**Relevance**: Directly motivates `§4.1 OverconfidentTrader` and `§4.2
SelfAttributor`.

### §2.2 Excess Trading From Overconfidence

**Citation**: Odean, T. (1998). Volume, volatility, price, and profit when all
traders are above average. *Journal of Finance*. DOI: `10.1111/0022-1082.00078`.

**Core Theoretical Mechanism**: Traders who think their signals are unusually
good trade even when the expected value of trading is low. Aggregated across
agents, this increases turnover and can increase volatility.

**Mathematical Formulation**: Order intensity rises with perceived signal
strength: `quantity = min(base_size, k * |s_hat|)`, subject to cash and
inventory constraints.

**Empirical Evidence**: Excess volume and lower net returns are recurring
evidence for overconfidence in retail and active-trader datasets.

**Relevance**: Calibrates `§4.1 OverconfidentTrader` and the excess-turnover
analysis metrics.

### §2.3 Household Trading Performance

**Citation**: Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender,
overconfidence, and common stock investment. *Quarterly Journal of Economics*.
DOI: `10.1162/003355301556400`.

**Core Theoretical Mechanism**: More overconfident investor groups trade more
and suffer lower net returns because the perceived informational edge does not
cover transaction and timing costs.

**Mathematical Formulation**: The performance comparison is represented as a
gap between biased-agent turnover and calibrated-agent turnover, plus the
portfolio-value difference across agent groups.

**Empirical Evidence**: Household brokerage records show higher turnover for
more overconfident groups and lower performance after costs.

**Relevance**: Motivates `§4.3 CalibratedTrader` as the benchmark.

### §2.4 Contrarian Correction

**Citation**: De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market
overreact? *Journal of Finance*. DOI: `10.1111/j.1540-6261.1985.tb05004.x`.

**Core Theoretical Mechanism**: Overreaction creates opportunities for
contrarian investors who buy excessive pessimism and sell excessive optimism.

**Mathematical Formulation**: Contrarian action triggers when
`|deviation| > contrarian_threshold` and trades opposite the deviation sign.

**Empirical Evidence**: Long-horizon reversal evidence motivates the idea that
extreme price moves can be partially corrected by patient value-oriented flow.

**Relevance**: Defines `§4.4 ContrarianInvestor`.

## §3 Market Design

The market uses a single risky asset with price `P_t`, fundamental value `F`,
and net demand `D_t`. Price evolves as:

`P_{t+1} = max(0.01, P_t + lambda * D_t + gamma * (F - P_t) + epsilon_t)`

where `lambda` is price impact, `gamma` is mean reversion, and `epsilon_t` is
Gaussian noise. The market broadcasts price, fundamental value, deviation,
round number, and receives canonical order payloads with action, bid price,
quantity, agent type, strategy, and reasoning.

## §4 Investor Taxonomy

### §4.1 OverconfidentTrader

1. **Summary**: OverconfidentTrader inflates perceived signal precision and
trades on deviations that calibrated traders might ignore. It is the primary
destabilizing role.
2. **Theoretical and Empirical Foundation**: Daniel et al. (1998) and Odean
(1998) support the signal-overprecision and excess-turnover mechanism.
3. **Design Purpose and Activation Scenarios**: Activates when the perceived
signal exceeds a low threshold. Its market purpose is to convert weak
mispricing into large order flow.
4. **Behavioral Framework**: Uses `signal = deviation * precision_overestimate`.
If `abs(signal) > 0.01`, it trades in the signal direction with size capped by
`base_size`, cash, and inventory.
5. **Decision Process Walkthrough**: Read price and fundamental, compute
deviation, inflate it, select buy/sell direction, cap quantity, and emit a
reasoned canonical order.
6. **Worked Numerical Example**: If deviation is `+2%` and
`precision_overestimate = 2.0`, perceived signal is `+4%`, crossing threshold
and producing a buy order subject to available cash.
7. **Academic References**: Daniel et al. (1998), Odean (1998), Barber and
Odean (2001).

### §4.2 SelfAttributor

1. **Summary**: SelfAttributor raises confidence after favorable conditions and
discounts negative evidence. It creates path-dependent risk taking.
2. **Theoretical and Empirical Foundation**: Biased self-attribution in Daniel
et al. (1998) and Gervais and Odean (2001, DOI `10.1093/rfs/14.1.1`) motivates
the role.
3. **Design Purpose and Activation Scenarios**: Activates when an existing
position and positive deviation make success feel skill-based, or when losses
trigger exposure trimming.
4. **Behavioral Framework**: Positive deviation with inventory increases buy
size by `confidence_boost`; negative deviation beyond a threshold can trigger a
sell.
5. **Decision Process Walkthrough**: Observe current inventory, read deviation,
apply confidence boost or loss trim, then cap order by cash/inventory.
6. **Worked Numerical Example**: With `base_size = 400` and
`confidence_boost = 0.5`, a positive state can request `600` shares before cash
constraints.
7. **Academic References**: Daniel et al. (1998), Gervais and Odean (2001).

### §4.3 CalibratedTrader

1. **Summary**: CalibratedTrader estimates signal precision correctly and trades
only when the deviation is meaningful. It is the rational benchmark.
2. **Theoretical and Empirical Foundation**: Grossman and Stiglitz (1980, DOI
`10.2307/1805228`) motivate disciplined information-based trading.
3. **Design Purpose and Activation Scenarios**: Activates only when
`abs(deviation) > trade_threshold`.
4. **Behavioral Framework**: Trades in the value direction: buy undervaluation
and sell overvaluation. Quantity scales with `signal_precision`.
5. **Decision Process Walkthrough**: Compare price to fundamental, verify the
threshold, compute bounded size, and emit a stabilizing order.
6. **Worked Numerical Example**: If price is 4% below fundamental and threshold
is 3%, it buys a bounded quantity proportional to signal precision.
7. **Academic References**: Grossman and Stiglitz (1980), Odean (1998).

### §4.4 ContrarianInvestor

1. **Summary**: ContrarianInvestor fades extreme overconfident moves. It is a
stabilizing agent that opposes large deviations from fundamental value.
2. **Theoretical and Empirical Foundation**: De Bondt and Thaler (1985) support
the overreaction-correction mechanism.
3. **Design Purpose and Activation Scenarios**: Activates only when
`abs(deviation) > contrarian_threshold`.
4. **Behavioral Framework**: Sells overvaluation and buys undervaluation, with
size capped by `base_size`, cash, and inventory.
5. **Decision Process Walkthrough**: Wait for a large deviation, trade against
the direction, and provide mean-reversion pressure.
6. **Worked Numerical Example**: A 6% overvaluation with threshold 4% triggers a
sell order up to the configured base size.
7. **Academic References**: De Bondt and Thaler (1985).

### §4.5 NoiseTrader

1. **Summary**: NoiseTrader contributes random uninformed order flow. It
prevents the market from being mechanically deterministic.
2. **Theoretical and Empirical Foundation**: Black (1986, DOI
`10.1111/j.1540-6261.1986.tb04513.x`) and De Long et al. (1990) motivate noise
trading.
3. **Design Purpose and Activation Scenarios**: Activates with configured
`trade_probability`.
4. **Behavioral Framework**: Randomly chooses buy, sell, or hold and uses
`noise_size` as the maximum random order size.
5. **Decision Process Walkthrough**: Draw a random activation, choose direction,
cap by cash/inventory, and emit a canonical order.
6. **Worked Numerical Example**: If the random activation fires and direction
is buy, it buys a random quantity up to `noise_size` if cash allows.
7. **Academic References**: Black (1986), De Long et al. (1990).

## §5 Agent Diversity Verification

The design includes destabilizing overprecision, path-dependent attribution,
calibrated rational trading, contrarian stabilization, and noise liquidity.
This diversity makes excess turnover attributable to overconfidence rather than
to missing counterparty flow or a one-sided market.

## §6 Parameter Table

| Parameter | Value | Source / Rationale | Used By |
|---|---:|---|---|
| `precision_overestimate` | 2.0 | Overprecision doubles perceived signal strength | OverconfidentTrader |
| `confidence_boost` | 0.5 | Post-success confidence amplification | SelfAttributor |
| `trade_threshold` | 0.03 | Calibrated trader ignores small deviations | CalibratedTrader |
| `signal_precision` | 1.0 | Benchmark signal scale | CalibratedTrader |
| `contrarian_threshold` | 0.04 | Requires wider deviation than calibrated trader | ContrarianInvestor |
| `trade_probability` | 0.3 | Background liquidity frequency | NoiseTrader |
| `noise_size` | 150 | Maximum random order size | NoiseTrader |
| `price_impact` | 0.02 | Converts net demand into price pressure | Market |
| `mean_reversion` | 0.01 | Fundamental anchor strength | Market |
| `noise_std` | 0.015 | Exogenous market noise | Market |

## §7 Communication And Round Structure

At each round the market broadcasts state, investors perceive price and
fundamental value, investors emit one canonical order, and the market aggregates
net demand. The next price is written to batch history together with
fundamental value and volume.

## §8 Historical Case Studies

### §8.1 Retail Brokerage Overtrading

| Field | Description |
|---|---|
| Event Profile | Household brokerage accounts studied by Barber and Odean |
| Quantitative Evidence | Men traded about 45% more than women and earned lower net returns |
| Agent Mapping | OverconfidentTrader and CalibratedTrader |
| Calibration Lesson | Excess turnover is a central observable target |

### §8.2 Day-Trading Boom

| Field | Description |
|---|---|
| Event Profile | High-frequency retail day-trading cohorts |
| Quantitative Evidence | Studies report high turnover and poor average net performance |
| Agent Mapping | OverconfidentTrader, SelfAttributor, NoiseTrader |
| Calibration Lesson | Repeated activity can persist even without superior information |

### §8.3 Dot-Com Retail Speculation

| Field | Description |
|---|---|
| Event Profile | Late-1990s internet-stock speculation |
| Quantitative Evidence | NASDAQ gained about 86% in 1999 and later fell about 78% from peak |
| Agent Mapping | OverconfidentTrader, NoiseTrader, ContrarianInvestor |
| Calibration Lesson | Bias-driven confidence can amplify deviations before correction |

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Difference |
|---|---|---|
| Rule | Deterministic formulas and config thresholds | Clean baseline for excess turnover and deviation |
| LLM | Persona-only model decisions | More variable confidence expression |
| RuleLLM | Explicit rules plus model reasoning | Preserves rule direction with textual rationale |
| Rag | RuleLLM plus retrieved behavioral-finance context | Adds auditable knowledge use through `rag_context` |
