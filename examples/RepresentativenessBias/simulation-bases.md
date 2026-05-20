# RepresentativenessBias Simulation Bases

## §1 Phenomenon Definition

RepresentativenessBias models investors who classify current market patterns as
members of salient historical categories while underweighting base rates. The
result is pattern-driven overreaction, category extrapolation, and eventual
correction by Bayesian and contrarian agents.

## §2 Theoretical Foundation

### §2.1 Representativeness Heuristic

Representativeness is the tendency to judge probability by similarity to a
prototype rather than by statistical base rates.

### §2.2 Base-Rate Neglect

Investors may ignore long-run frequencies when a vivid pattern appears to match
a familiar story.

### §2.3 Statistical Arbitrage Against Biased Beliefs

Bayesian and contrarian traders can exploit prices pushed away from base-rate
consistent valuation.

## §3 Market Mechanism

The market broadcasts price, fundamental value, deviation, and recent pattern
signals. Biased agents submit orders based on pattern/category judgments;
Bayesian and contrarian agents offset mispricing.

## §4 Investor Archetypes

### §4.1 PatternMatcher

**Summary**: Matches current price patterns to salient prototypes.
**Theoretical and Empirical Basis**: Representativeness heuristic.
**Design Purpose**: Generate pattern-based overreaction.
**Behavioral Framework**: Uses `pattern_sensitivity` and `base_rate_ignore`.
**Decision Process**: Buy or sell when current pattern resembles a salient
prototype, underweighting base rates.
**Worked Numerical Example**: A short winning streak is treated as proof of a
growth-stock prototype, triggering a buy.
**Academic References**: Kahneman and Tversky (1972, 1974).

### §4.2 CategoryOvergeneralizer

**Summary**: Generalizes from small samples into dramatic categories.
**Theoretical and Empirical Basis**: Small-sample extrapolation.
**Design Purpose**: Amplify category narratives.
**Behavioral Framework**: Uses `category_weight` and `sample_bias`.
**Decision Process**: Trades according to assigned category even when evidence
is thin.
**Worked Numerical Example**: A few high returns classify the asset as a bubble
winner, increasing demand.
**Academic References**: Behavioral categorization and extrapolation studies.

### §4.3 BayesianUpdater

**Summary**: Correctly combines base rates and evidence.
**Theoretical and Empirical Basis**: Bayesian updating.
**Design Purpose**: Provide rational benchmark.
**Behavioral Framework**: Uses `base_rate_weight` and `evidence_weight`.
**Decision Process**: Updates belief by weighting prior/base rate and new
evidence.
**Worked Numerical Example**: A vivid signal is tempered by low base-rate
probability.
**Academic References**: Bayesian decision theory.

### §4.4 ContrarianStatistical

**Summary**: Trades against representativeness-driven mispricing.
**Theoretical and Empirical Basis**: Statistical arbitrage against behavioral
bias.
**Design Purpose**: Stabilize prices when base rates are ignored.
**Behavioral Framework**: Uses `contrarian_threshold` and `position_size`.
**Decision Process**: Buy undervalued or sell overvalued assets when price
deviation exceeds threshold.
**Worked Numerical Example**: If biased demand pushes price 20% above
fundamental, contrarian sells.
**Academic References**: Limits-of-arbitrage and behavioral asset pricing.

### §4.5 NoiseTrader

**Summary**: Random uninformed liquidity participant.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add background stochastic order flow.
**Behavioral Framework**: Uses `trade_probability`.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: A random draw below trade probability triggers a
small order.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population contrasts biased pattern/category traders with Bayesian and
contrarian correctors plus noise liquidity.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `pattern_sensitivity` | Strength of prototype matching | PatternMatcher | High |
| `base_rate_ignore` | Degree of base-rate neglect | PatternMatcher | High |
| `category_weight` | Category narrative strength | CategoryOvergeneralizer | High |
| `sample_bias` | Small-sample overgeneralization | CategoryOvergeneralizer | Medium |
| `base_rate_weight` | Bayesian prior weight | BayesianUpdater | Medium |
| `contrarian_threshold` | Statistical correction trigger | ContrarianStatistical | Medium |

## §7 Communication And Round Structure

Market broadcasts state; agents form biased or Bayesian beliefs; orders return
to market; market updates price from net demand.

## §8 Historical Case Studies

### §8.1 Glamour Stock Extrapolation

Investors often overpay for stocks that resemble a salient growth prototype
after a short run of strong returns.

### §8.2 Crash Analogy Overuse

Markets sometimes overreact when current patterns are judged similar to past
crashes despite different base conditions.

## §9 Variant Comparison Preview

Rule fixes bias parameters. LLM may create richer category narratives. RuleLLM
anchors the LLM to explicit base-rate rules. Rag may retrieve behavioral-finance
context and temper or reinforce pattern matching.
