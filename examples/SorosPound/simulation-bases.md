# SorosPound Simulation Bases

## §1 Phenomenon Definition

SorosPound models the 1992 sterling crisis as a speculative attack on an
unsustainable currency peg. Macro short sellers, opportunistic traders, peg
defenders, convergence traders, and noise traders interact around a policy
credibility constraint.

## §2 Theoretical Foundation

### §2.1 Speculative Attacks

Currency pegs can collapse when defending them becomes economically or
politically too costly.

### §2.2 Reflexive Macro Trading

Large informed speculators can coordinate pressure once fundamentals and policy
credibility diverge.

### §2.3 Peg Defense And Reserve Constraint

Central-bank intervention and rate hikes can defend a peg temporarily but may be
overwhelmed by market pressure.

## §3 Market Mechanism

The market tracks exchange-rate/peg pressure. Sell pressure against the currency
weakens the peg; defense actions offset pressure until credibility or reserves
are exhausted.

## §4 Investor Archetypes

### §4.1 MacroHedgeFund

**Summary**: Builds large short positions against an unsustainable peg.
**Theoretical and Empirical Basis**: Speculative attack theory.
**Design Purpose**: Provide informed attack pressure.
**Behavioral Framework**: Uses macro misalignment and peg credibility.
**Decision Process**: Short when peg defense appears unsustainable.
**Worked Numerical Example**: Falling credibility triggers larger short order.
**Academic References**: Krugman (1979); Obstfeld (1996).

### §4.2 PegDefender

**Summary**: Defends the peg through intervention and policy tightening.
**Theoretical and Empirical Basis**: Central-bank peg defense.
**Design Purpose**: Provide stabilizing but limited support.
**Behavioral Framework**: Uses intervention intensity and defense threshold.
**Decision Process**: Buy/support currency when pressure rises.
**Worked Numerical Example**: Pressure above threshold triggers support action.
**Academic References**: Exchange-rate crisis literature.

### §4.3 ConvergenceTrader

**Summary**: Bets that the peg will hold and loses when it breaks.
**Theoretical and Empirical Basis**: Convergence/arbitrage under policy risk.
**Design Purpose**: Add stabilizing capital that can reverse under stress.
**Behavioral Framework**: Trades toward peg value while credibility remains.
**Decision Process**: Buy under peg deviation until break risk dominates.
**Worked Numerical Example**: A small discount to peg triggers convergence buy.
**Academic References**: Currency arbitrage literature.

### §4.4 OpportunisticTrader

**Summary**: Joins the attack after momentum is visible.
**Theoretical and Empirical Basis**: Herding in speculative attacks.
**Design Purpose**: Amplify attack once it starts.
**Behavioral Framework**: Reacts to recent pressure and trend.
**Decision Process**: Sell after attack momentum crosses threshold.
**Worked Numerical Example**: Two rounds of peg weakness trigger short entry.
**Academic References**: Herding and currency crisis studies.

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add background liquidity and randomness.
**Behavioral Framework**: Random low-intensity orders.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: A random draw creates a small trade.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The scenario includes informed attackers, policy defenders, convergence buyers,
momentum joiners, and noise traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| peg credibility | Belief peg can hold | MacroHedgeFund/PegDefender | High |
| attack pressure | Aggregate sell pressure | Market | High |
| intervention strength | Defense capacity | PegDefender | High |
| momentum threshold | Opportunistic entry | OpportunisticTrader | Medium |
| convergence threshold | Peg-value entry | ConvergenceTrader | Medium |

## §7 Communication And Round Structure

Market broadcasts peg pressure and price; traders attack, defend, converge, or
join momentum; market updates peg stress.

## §8 Historical Case Studies

### §8.1 Black Wednesday, 1992

Sterling exited the ERM after speculative pressure overwhelmed defense.

### §8.2 Other Currency Peg Crises

Emerging-market peg collapses show similar reserve, credibility, and attack
dynamics.

## §9 Variant Comparison Preview

Rule encodes attack/defense thresholds. LLM may change confidence and
coordination. RuleLLM anchors macro logic. Rag may retrieve historical sterling
crisis context.
