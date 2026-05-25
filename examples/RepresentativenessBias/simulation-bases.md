# RepresentativenessBias Simulation Bases

## §1 Phenomenon Definition

Representativeness bias is the tendency to judge probabilities by similarity to
a salient prototype while underweighting base rates and sample size. In markets,
this creates extrapolative buying after a short streak, category-driven selling
after a visible decline, and temporary mispricing that disciplined Bayesian or
contrarian agents can correct.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Kahneman and Tversky (1972) introduced representativeness as a judgment
heuristic: people assess likelihood by resemblance rather than by statistical
frequency. Tversky and Kahneman (1974) connected the same mechanism to broader
errors under uncertainty, including base-rate neglect and insensitivity to
sample size. Grether (1980) then showed in an experimental market-style setting
that subjects systematically deviate from Bayesian updating when salient
signals conflict with prior probabilities.

Financial economics later translated this cognitive mechanism into market
pricing. Barberis, Shleifer, and Vishny (1998) model investors who overreact
when firms appear to belong to a salient growth or reversal category, while
Daniel, Hirshleifer, and Subrahmanyam (1998) explain how biased inference and
overconfidence can push prices away from fundamentals before correction.
This simulation isolates the representativeness channel: biased agents trade on
prototype/category resemblance, while Bayesian and contrarian agents use base
rates as stabilizing benchmarks.

#### §1.1.2 Real-World Event Catalogue

| Event | Period | Quantitative Magnitude | Agent Correspondence |
|---|---|---|---|
| Dot-com glamour extrapolation | 1998-2000 | NASDAQ rose about 86% in 1999 before falling about 78% by 2002 | `PatternMatcher`, `CategoryOvergeneralizer` |
| Nifty Fifty growth categorization | 1970-1974 | Many favored growth stocks lost more than 50% after peak valuation compression | `CategoryOvergeneralizer`, `ContrarianStatistical` |
| Post-earnings announcement drift | recurring | Bernard and Thomas (1989) document delayed reaction to earnings signals | `PatternMatcher`, `BayesianUpdater` |
| Meme-stock prototype trading | 2021 | GameStop rose from under $20 to an intraday high above $480 before reversal | `PatternMatcher`, `NoiseTrader` |

#### §1.1.3 Book and Practitioner Literature

| Source | Relevance |
|---|---|
| Kahneman, *Thinking, Fast and Slow* (2011) | Practitioner-accessible account of representativeness, base-rate neglect, and small-sample errors |
| Shleifer, *Inefficient Markets* (2000) | Explains why biased beliefs can persist when arbitrage is limited |
| Montier, *Behavioural Investing* (2007) | Practitioner examples of category extrapolation and narrative-driven valuation |

## §2 Theoretical Foundation

### §2.1 Representativeness Heuristic

**Citation**: Kahneman, D., and Tversky, A. (1972). Subjective probability: A
judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454.
doi:10.1016/0010-0285(72)90016-3.

**Mechanism**: Investors infer that a current pattern belongs to a familiar
class, such as "breakout winner" or "falling knife", even when the base rate of
that class is low. This leads to overreaction to short streaks and salient
visual patterns.

**Formalization**: A biased belief can be written as
`belief_biased = w * prototype_signal + (1 - w) * base_rate`, with
`w > 0.5` for representativeness-biased agents.

**Empirical evidence**: The original experiments document systematic neglect
of prior probabilities when descriptions resemble stereotypes.

**Relevance**: Defines `PatternMatcher` (§4.1) and partially drives
`CategoryOvergeneralizer` (§4.2).

### §2.2 Base-Rate Neglect And Bayesian Correction

**Citation**: Grether, D. M. (1980). Bayes rule as a descriptive model: The
representativeness heuristic. *Quarterly Journal of Economics*, 95(3), 537-557.
doi:10.2307/1885092.

**Mechanism**: Subjects update beliefs in the right direction but place too much
weight on vivid samples and too little weight on prior probabilities. A
Bayesian benchmark corrects this by explicitly weighting base rates.

**Formalization**: `belief_bayes = alpha * base_rate + (1 - alpha) * signal`,
where higher `alpha` gives stronger prior discipline.

**Empirical evidence**: Grether finds persistent deviations from Bayesian
posterior probabilities in controlled experiments.

**Relevance**: Defines `BayesianUpdater` (§4.3) and the corrective half of
`ContrarianStatistical` (§4.4).

### §2.3 Investor Sentiment And Limits To Arbitrage

**Citation**: Barberis, N., Shleifer, A., and Vishny, R. (1998). A model of
investor sentiment. *Journal of Financial Economics*, 49(3), 307-343.
doi:10.1016/S0304-405X(98)00027-0.

**Mechanism**: Investors switch between salient regimes and extrapolate recent
evidence into category narratives. Arbitrageurs may correct mispricing, but
only after deviations are large enough to compensate for risk and capital
limits.

**Formalization**: Biased demand is increasing in category signal strength,
while contrarian demand activates only when `abs(deviation)` exceeds a
threshold.

**Empirical evidence**: The model explains underreaction, overreaction, and
subsequent correction patterns found in return predictability.

**Relevance**: Defines `CategoryOvergeneralizer` (§4.2) and
`ContrarianStatistical` (§4.4).

## §3 Market Design

The market uses a single risky asset with fixed fundamental value `F`. Every
round, the market broadcasts price, fundamental value, and deviation:

```text
deviation_t = (P_t - F) / F
P_{t+1} = max(0.01, P_t + lambda * NetDemand_t + gamma * (F - P_t) + epsilon_t)
```

Biased agents buy positive salient deviations and sell negative salient
deviations. Bayesian and contrarian agents trade against sufficiently large
mispricing. Noise traders provide stochastic background liquidity.

## §4 Investor Taxonomy

### §4.1 PatternMatcher

**Summary**: A destabilizing investor that treats short price deviations as
evidence of a familiar prototype. It amplifies recent patterns and underweights
base rates.

**Theoretical and Empirical Foundation**: Based on Kahneman and Tversky (1972,
doi:10.1016/0010-0285(72)90016-3) and Tversky and Kahneman (1974,
doi:10.1126/science.185.4157.1124).

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.02`; buys positive deviations and sells negative deviations.

**Behavioral Framework**: `pattern_sensitivity` and `base_rate_ignore` define
the tendency to convert a deviation into prototype-confirming order flow.
Quantity is `min(800, int(abs(deviation) * 5000))`.

**Decision Process Walkthrough**: Read market deviation, classify the pattern as
breakout or breakdown, cap quantity by cash or position, and submit the order.

**Worked Numerical Example**: With price 104, fundamental 100, deviation 0.04,
quantity is `min(800, int(0.04 * 5000)) = 200`; the agent buys up to 200 shares.

**Academic References**: Kahneman and Tversky (1972); Tversky and Kahneman
(1974).

### §4.2 CategoryOvergeneralizer

**Summary**: A destabilizing investor that maps a small sample of recent price
movement into a dramatic category such as "growth star" or "falling knife".

**Theoretical and Empirical Foundation**: Based on representativeness and
insensitivity to sample size in Tversky and Kahneman (1974) plus investor
sentiment regime switching in Barberis et al. (1998, doi:10.1016/S0304-405X(98)00027-0).

**Design Purpose and Activation Scenarios**: Activates on deviations above 2%
and reinforces the assigned category, generating overreaction from thin
evidence.

**Behavioral Framework**: `category_weight` controls category strength and
`sample_bias` controls overgeneralization from small samples. Quantity matches
the PatternMatcher formula to isolate the category narrative channel.

**Decision Process Walkthrough**: Read deviation, assign a positive or negative
category, trade in the category direction, and cap by cash or holdings.

**Worked Numerical Example**: A -3% deviation is classified as a falling-knife
category; quantity is `min(800, int(0.03 * 5000)) = 150`; the agent sells up to
150 shares.

**Academic References**: Tversky and Kahneman (1974); Barberis et al. (1998).

### §4.3 BayesianUpdater

**Summary**: A stabilizing benchmark that combines prior/base-rate information
with observed evidence. It corrects overreaction when price deviates materially
from fundamental value.

**Theoretical and Empirical Foundation**: Based on Grether (1980,
doi:10.2307/1885092) and Bayesian decision theory.

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.05`; buys undervaluation and sells overvaluation.

**Behavioral Framework**: `base_rate_weight` and `evidence_weight` define how
strongly the agent disciplines new signals with priors. Quantity is
`min(500, int(abs(deviation) * 3000))`.

**Decision Process Walkthrough**: Compute deviation, compare it to the 5%
evidence threshold, trade toward fundamental when the signal is strong enough.

**Worked Numerical Example**: Price 94 and fundamental 100 gives deviation
-0.06. Quantity is `min(500, int(0.06 * 3000)) = 180`; the agent buys.

**Academic References**: Grether (1980).

### §4.4 ContrarianStatistical

**Summary**: A stabilizing arbitrageur that trades against pattern-driven
mispricing. It is inactive for small deviations but corrects large biased
pressure.

**Theoretical and Empirical Foundation**: Based on Barberis et al. (1998) and
limits-to-arbitrage logic in Shleifer (2000).

**Design Purpose and Activation Scenarios**: Activates when
`abs(deviation) > 0.05`; buys underpricing and sells overpricing.

**Behavioral Framework**: `contrarian_threshold` and `position_size` define
when correction starts and how much capital can be committed.

**Decision Process Walkthrough**: Detect mispricing, take the opposite side of
representativeness-driven order flow, and cap quantity by cash/position.

**Worked Numerical Example**: Price 108 and fundamental 100 gives deviation
0.08. Quantity is `min(500, int(0.08 * 3000)) = 240`; the agent sells.

**Academic References**: Barberis et al. (1998); Shleifer (2000).

### §4.5 NoiseTrader

**Summary**: A neutral liquidity provider that trades without information. It
prevents deterministic synchronization and supplies baseline market activity.

**Theoretical and Empirical Foundation**: Based on Black (1986), Noise.
*Journal of Finance*, 41(3), 529-543. doi:10.1111/j.1540-6261.1986.tb04513.x.

**Design Purpose and Activation Scenarios**: Activates according to
`trade_probability`; otherwise holds.

**Behavioral Framework**: Randomly chooses buy or sell and samples a quantity
between 100 and 500, capped by cash or position.

**Decision Process Walkthrough**: Draw a random trade indicator; if active,
draw action and quantity; otherwise return hold.

**Worked Numerical Example**: With `trade_probability = 0.3`, a random draw of
0.18 triggers trading; a second draw selects buy; sampled quantity 250 is capped
by available cash.

**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The scenario intentionally combines destabilizing representativeness agents
(`PatternMatcher`, `CategoryOvergeneralizer`), stabilizing statistical agents
(`BayesianUpdater`, `ContrarianStatistical`), and neutral liquidity
(`NoiseTrader`). This mix allows the simulation to produce bias-driven
mispricing and correction rather than one-directional drift.

## §6 Parameter Table

| Parameter | Value | Used By | Source / Rationale |
|---|---:|---|---|
| `pattern_sensitivity` | 1.0 | PatternMatcher | High prototype weight from representativeness experiments |
| `base_rate_ignore` | 0.7 | PatternMatcher | Strong prior underweighting from Grether-style deviations |
| `category_weight` | 1.2 | CategoryOvergeneralizer | Amplifies salient category narratives |
| `sample_bias` | 0.7 | CategoryOvergeneralizer | Small-sample extrapolation strength |
| `base_rate_weight` | 0.7 | BayesianUpdater | Partial prior discipline |
| `evidence_weight` | 0.4 | BayesianUpdater | Bounded evidence response after prior weighting |
| `contrarian_threshold` | 0.04-0.05 | ContrarianStatistical | Minimum deviation needed to overcome arbitrage risk |
| `trade_probability` | 0.3 | NoiseTrader | Background liquidity rate |

## §7 Communication And Round Structure

Each round: Market clears inbound orders, updates price, broadcasts market
state; investors perceive market state, form biased or statistical beliefs,
return canonical orders, and update internal cash/position state.

## §8 Historical Case Studies

### §8.1 Dot-Com Glamour Stock Extrapolation

**Event Profile**: 1998-2002 technology shares were classified as a "new
economy" growth category. NASDAQ rose about 86% in 1999 and then fell about 78%
from peak to trough.

**Agent Mapping**: PatternMatcher and CategoryOvergeneralizer buy the positive
prototype; ContrarianStatistical sells after deviation becomes large.

**Calibration Lesson**: Positive deviations above 2% should trigger biased
buying before 5% correction thresholds activate.

### §8.2 Nifty Fifty Valuation Compression

**Event Profile**: Early-1970s growth stocks were treated as one-decision
quality franchises. Many later lost more than half their value as valuation
multiples compressed.

**Agent Mapping**: CategoryOvergeneralizer maps surface quality into a durable
category; BayesianUpdater tempers this with base rates.

**Calibration Lesson**: Category weight must be strong enough to create
overpricing, but contrarian thresholds prevent unbounded price drift.

### §8.3 Meme-Stock Prototype Trading

**Event Profile**: In January 2021, GameStop rose from under $20 to an intraday
high above $480 before reversing. Traders used squeeze/prototype narratives
despite shifting base conditions.

**Agent Mapping**: PatternMatcher and NoiseTrader amplify salient narrative
pressure; BayesianUpdater and ContrarianStatistical provide correction.

**Calibration Lesson**: Noise and biased pattern volume should be separable in
analysis so prototype-driven volume can be measured.

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Expected Effect |
|---|---|---|
| Rule | Deterministic thresholds from §4 | Clean baseline for bias and correction |
| LLM | Persona-only market reasoning | More varied but still prototype-sensitive behavior |
| RuleLLM | Persona plus explicit rules | Rule-like direction with language variation |
| Rag | RuleLLM plus retrieved behavioral-finance context | Potentially lower base-rate neglect if retrieval surfaces statistical cautions |
