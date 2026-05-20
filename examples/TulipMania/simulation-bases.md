# TulipMania Simulation Bases

## §1 Phenomenon Definition

TulipMania models a speculative mania in which rising prices, social proof, and
trend chasing push an asset far above intrinsic value before early exits,
skeptical valuation, and fading demand lead to collapse.

## §2 Theoretical Foundation

### §2.1 Speculative Mania

Manias occur when price appreciation itself becomes the reason to buy.

### §2.2 Social Proof

Investors infer value from the crowd's participation, reinforcing demand.

### §2.3 Intrinsic Value Constraint

Fundamental traders compare market price with use value and sell when the gap is
large.

## §3 Market Mechanism

The market tracks price, intrinsic value, and narrative/trend pressure.
TrendChaser and SocialProofFollower add bubble demand; IntrinsicValueTrader and
EarlyExitTrader provide correction pressure.

## §4 Investor Archetypes

### §4.1 TrendChaser

**Summary**: Buys because prices are rising.
**Theoretical and Empirical Basis**: Positive-feedback speculation.
**Design Purpose**: Generate bubble acceleration.
**Behavioral Framework**: Reacts to recent price trend.
**Decision Process**: Buy rising trends and sell after trend breaks.
**Worked Numerical Example**: Consecutive price increases trigger buy.
**Academic References**: Bubble and trend-following literature.

### §4.2 SocialProofFollower

**Summary**: Follows crowd participation into speculative assets.
**Theoretical and Empirical Basis**: Herding and social proof.
**Design Purpose**: Amplify mania through crowd validation.
**Behavioral Framework**: Uses perceived participation.
**Decision Process**: Buy when crowd demand is strong.
**Worked Numerical Example**: High observed buy volume triggers another buy.
**Academic References**: Herding literature.

### §4.3 IntrinsicValueTrader

**Summary**: Values assets by intrinsic utility.
**Theoretical and Empirical Basis**: Fundamental valuation.
**Design Purpose**: Provide rational anchor.
**Behavioral Framework**: Compares price with intrinsic value.
**Decision Process**: Sell when price exceeds intrinsic value by threshold.
**Worked Numerical Example**: Price ten times intrinsic value triggers sell.
**Academic References**: Fundamental valuation and bubble studies.

### §4.4 EarlyExitTrader

**Summary**: Recognizes speculative excess and exits before crash.
**Theoretical and Empirical Basis**: Strategic timing in bubbles.
**Design Purpose**: Model informed exit pressure near peak.
**Behavioral Framework**: Tracks bubble maturity and overvaluation.
**Decision Process**: Sell before trend fully reverses when excess is high.
**Worked Numerical Example**: Overvaluation plus slowing trend triggers exit.
**Academic References**: Bubble timing literature.

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add stochastic volume.
**Behavioral Framework**: Random low-intensity orders.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: Random buy adds to bubble pressure by chance.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population includes trend chasers, herd followers, fundamental skeptics,
early exiters, and noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| trend sensitivity | Response to rising prices | TrendChaser | High |
| social proof strength | Crowd-following intensity | SocialProofFollower | High |
| intrinsic threshold | Fundamental sell trigger | IntrinsicValueTrader | Medium |
| exit threshold | Early-exit trigger | EarlyExitTrader | High |
| noise intensity | Random order flow | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts price, intrinsic value, trend, and crowd state; agents trade
on trend, crowd, value, exit timing, or noise; market updates price.

## §8 Historical Case Studies

### §8.1 Dutch Tulip Mania

Tulip bulb prices rose rapidly amid speculative enthusiasm before collapsing.

### §8.2 Later Collectible And Asset Manias

Many manias share the same trend-chasing and social-proof structure despite
different assets.

## §9 Variant Comparison Preview

Rule encodes mania thresholds. LLM may amplify narrative enthusiasm. RuleLLM
keeps explicit bubble rules. Rag may retrieve historical mania context.
