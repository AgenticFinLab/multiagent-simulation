# SunkCostFallacy Simulation Bases

## §1 Phenomenon Definition

SunkCostFallacy models investors who continue holding or adding to losing
positions because prior investment is psychologically salient, despite
forward-looking alternatives.

## §2 Theoretical Foundation

### §2.1 Sunk-Cost Fallacy

Decision makers irrationally consider irrecoverable past costs when choosing
future action.

### §2.2 Escalation Of Commitment

Agents may increase commitment to a failing course of action to justify prior
choices.

### §2.3 Opportunity Cost Reasoning

Rational investors compare current capital allocation against the best
alternative use, ignoring sunk costs.

## §3 Market Mechanism

The market broadcasts price, fundamental, and loss state. Sunk-cost agents hold
or double down, while rational and opportunity-cost agents cut losses or
reallocate.

## §4 Investor Archetypes

### §4.1 SunkCostHolder

**Summary**: Holds losing positions because of prior investment.
**Theoretical and Empirical Basis**: Sunk-cost fallacy.
**Design Purpose**: Generate sticky losing positions.
**Behavioral Framework**: Treats realized loss avoidance as valuable.
**Decision Process**: Hold when selling would acknowledge prior loss.
**Worked Numerical Example**: A position down 30% remains held despite weak
future prospects.
**Academic References**: Arkes and Blumer (1985).

### §4.2 CommitmentEscalator

**Summary**: Doubles down on losers to justify prior commitment.
**Theoretical and Empirical Basis**: Escalation of commitment.
**Design Purpose**: Add destabilizing demand into declining assets.
**Behavioral Framework**: Increases exposure after losses.
**Decision Process**: Buy more when loss deepens but commitment remains high.
**Worked Numerical Example**: A 20% loss triggers an additional buy.
**Academic References**: Staw (1976).

### §4.3 RationalCutter

**Summary**: Cuts losses based on forward-looking assessment.
**Theoretical and Empirical Basis**: Rational choice.
**Design Purpose**: Provide benchmark discipline.
**Behavioral Framework**: Ignores past cost and evaluates expected return.
**Decision Process**: Sell if expected future value is poor.
**Worked Numerical Example**: A negative signal triggers sale regardless of
purchase price.
**Academic References**: Expected utility and portfolio choice literature.

### §4.4 OpportunityCostTrader

**Summary**: Reallocates capital from underperformers to better alternatives.
**Theoretical and Empirical Basis**: Opportunity cost reasoning.
**Design Purpose**: Counter sunk-cost holding.
**Behavioral Framework**: Compares current position with alternative return.
**Decision Process**: Sell underperformers when opportunity cost is high.
**Worked Numerical Example**: A low-return position is sold to fund a better
asset.
**Academic References**: Opportunity cost and capital allocation literature.

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add baseline stochastic order flow.
**Behavioral Framework**: Random low-intensity trading.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: Random draw creates a small order.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population includes sunk-cost holders, escalation buyers, rational cutters,
opportunity-cost reallocators, and noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| sunk-cost sensitivity | Strength of loss attachment | SunkCostHolder | High |
| commitment intensity | Double-down tendency | CommitmentEscalator | High |
| rational cut threshold | Forward-looking sell trigger | RationalCutter | Medium |
| opportunity cost threshold | Reallocation trigger | OpportunityCostTrader | Medium |
| noise intensity | Random order flow | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts state; agents evaluate losses, commitment, rational value, or
opportunity cost; orders are aggregated and price updates.

## §8 Historical Case Studies

### §8.1 Retail Averaging Down

Investors often add to losing positions to reduce average cost, consistent with
escalation of commitment.

### §8.2 Corporate Project Escalation

Firms sometimes continue failing projects because prior investment is salient.

## §9 Variant Comparison Preview

Rule encodes sunk-cost thresholds. LLM may rationalize holding or doubling down.
RuleLLM anchors explicit rules. Rag may retrieve behavioral evidence and alter
fallacy strength.
