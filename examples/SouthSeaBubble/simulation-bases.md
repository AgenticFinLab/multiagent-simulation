# SouthSeaBubble Simulation Bases

## §1 Phenomenon Definition

SouthSeaBubble models a narrative-driven speculative bubble fueled by insider
advantage, promotional monopoly stories, social proof, skeptical analysis,
arbitrage pressure, and noise trading.

## §2 Theoretical Foundation

### §2.1 Speculative Bubbles

Bubbles arise when prices detach from fundamentals due to extrapolation,
narratives, and resale expectations.

### §2.2 Insider Advantage

Privileged information and political connections can enable early accumulation
and exit.

### §2.3 Narrative Economics

Compelling stories can coordinate investor beliefs even when cash-flow evidence
is weak.

## §3 Market Mechanism

The market tracks price, fundamental value, and narrative pressure. Narrative
believers and insiders push price up; skeptical analysts and arbitrageurs oppose
mispricing.

## §4 Investor Archetypes

### §4.1 InsiderAdvantaged

**Summary**: Trades using privileged information and political connections.
**Theoretical and Empirical Basis**: Insider advantage in early bubbles.
**Design Purpose**: Model early informed accumulation and exit.
**Behavioral Framework**: Uses information advantage and timing.
**Decision Process**: Buy early, reduce exposure when bubble risk is high.
**Worked Numerical Example**: Insider buys before narrative peak and sells near
overvaluation.
**Academic References**: Historical South Sea Bubble accounts.

### §4.2 NarrativeBeliever

**Summary**: Believes promotional monopoly narratives.
**Theoretical and Empirical Basis**: Narrative economics.
**Design Purpose**: Generate bubble demand.
**Behavioral Framework**: Trades on narrative strength.
**Decision Process**: Buy as narrative pressure increases.
**Worked Numerical Example**: Strong promotional story triggers buy despite weak
fundamental value.
**Academic References**: Shiller (2017); bubble histories.

### §4.3 SkepticalAnalyst

**Summary**: Values actual cash flows and ignores promotional hype.
**Theoretical and Empirical Basis**: Fundamental analysis.
**Design Purpose**: Provide rational skepticism.
**Behavioral Framework**: Compares price to fundamental value.
**Decision Process**: Sell/avoid buying when price far exceeds fundamental.
**Worked Numerical Example**: Price at twice fundamental triggers sell.
**Academic References**: Fundamental valuation literature.

### §4.4 Arbitrageur

**Summary**: Exploits gap between narrative price and fundamental value.
**Theoretical and Empirical Basis**: Limits of arbitrage.
**Design Purpose**: Add correction pressure.
**Behavioral Framework**: Trades when mispricing is large enough.
**Decision Process**: Sell overpricing or buy underpricing when threshold is
met.
**Worked Numerical Example**: Large premium creates short/sell pressure.
**Academic References**: Shleifer and Vishny (1997).

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add stochastic volume.
**Behavioral Framework**: Random low-intensity orders.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: Random buy adds to bubble by chance.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population includes insiders, narrative believers, skeptical analysts,
arbitrageurs, and noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| narrative strength | Promotional belief pressure | NarrativeBeliever | High |
| information advantage | Insider timing edge | InsiderAdvantaged | High |
| valuation threshold | Skeptical sell trigger | SkepticalAnalyst | Medium |
| arbitrage threshold | Mispricing trigger | Arbitrageur | Medium |
| noise intensity | Random order flow | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts price, fundamental, and narrative state; agents trade on
insider timing, narrative, valuation, arbitrage, or noise; market updates price.

## §8 Historical Case Studies

### §8.1 South Sea Bubble, 1720

Promotional claims and political connections pushed prices far beyond
fundamental prospects before collapse.

### §8.2 Mississippi Bubble

A similar early-modern narrative and monopoly-rights bubble showed how public
enthusiasm can overwhelm valuation.

## §9 Variant Comparison Preview

Rule encodes narrative and valuation thresholds. LLM may strengthen story-based
reasoning. RuleLLM anchors narrative behavior to explicit rules. Rag may
retrieve historical bubble context.
