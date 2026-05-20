# SVBBankRun Simulation Bases

## §1 Phenomenon Definition

SVBBankRun models a modern bank run driven by asset-liability duration mismatch,
depositor withdrawal incentives, social-media amplification, regulatory
intervention expectations, and bond-market losses.

## §2 Theoretical Foundation

### §2.1 Bank Run Coordination

Diamond-Dybvig-style run models show that depositors may withdraw preemptively
when they expect others to withdraw.

### §2.2 Duration Mismatch

Rising rates reduce the value of long-duration securities, weakening bank
balance sheets when deposits are short-term.

### §2.3 Information Amplification

Social media accelerates coordination by transmitting panic signals rapidly.

## §3 Market Mechanism

The market tracks a bank-health/security-price proxy. Withdrawal, panic, bond
selling, and intervention-related orders affect net demand and therefore price.

## §4 Investor Archetypes

### §4.1 Depositor

**Summary**: Withdraws when perceived bank health deteriorates.
**Theoretical and Empirical Basis**: Bank run coordination theory.
**Design Purpose**: Model deposit flight.
**Behavioral Framework**: Uses `withdrawal_threshold`.
**Decision Process**: Withdraw/sell when health falls below threshold.
**Worked Numerical Example**: A health signal below threshold triggers deposit
exit.
**Academic References**: Diamond and Dybvig (1983).

### §4.2 SocialMediaInfluencer

**Summary**: Amplifies panic signals.
**Theoretical and Empirical Basis**: Information cascade and social contagion.
**Design Purpose**: Speed up run coordination.
**Behavioral Framework**: Uses `amplification_factor`.
**Decision Process**: Converts negative bank signals into stronger market
pressure.
**Worked Numerical Example**: A negative signal multiplied by amplification
factor creates larger sell/withdrawal pressure.
**Academic References**: Information cascade literature.

### §4.3 BankManager

**Summary**: Manages duration mismatch under stress.
**Theoretical and Empirical Basis**: Asset-liability management.
**Design Purpose**: Represent bank-side balance-sheet fragility.
**Behavioral Framework**: Uses `duration_gap`.
**Decision Process**: Larger duration gap increases vulnerability to rate
shocks.
**Worked Numerical Example**: A large duration gap makes a price decline more
severe when rates rise.
**Academic References**: Banking risk management literature.

### §4.4 Regulator

**Summary**: May intervene with guarantees or liquidity support.
**Theoretical and Empirical Basis**: Lender-of-last-resort and deposit
guarantee policy.
**Design Purpose**: Add stabilizing intervention channel.
**Behavioral Framework**: Uses `intervention_threshold` and
`guarantee_probability`.
**Decision Process**: Intervenes when health falls below threshold, probabilistic
guarantee support applies.
**Worked Numerical Example**: Severe stress activates possible support,
reducing sell pressure.
**Academic References**: Bagehot-style lender-of-last-resort theory.

### §4.5 BondTrader

**Summary**: Trades based on interest-rate expectations and bond losses.
**Theoretical and Empirical Basis**: Duration and mark-to-market losses.
**Design Purpose**: Connect rate shocks to bank-asset valuation.
**Behavioral Framework**: Reacts to price/health signals.
**Decision Process**: Sells when duration-loss expectations worsen.
**Worked Numerical Example**: Rising-rate shock causes bond trader to sell bank
exposure.
**Academic References**: Fixed-income duration literature.

## §5 Agent Diversity Verification

The scenario includes depositor exit, information amplification, bank balance
sheet management, policy stabilization, and bond-market repricing.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `withdrawal_threshold` | Depositor run trigger | Depositor | High |
| `amplification_factor` | Panic-signal multiplier | SocialMediaInfluencer | High |
| `duration_gap` | Asset-liability mismatch | BankManager | High |
| `intervention_threshold` | Policy response trigger | Regulator | Medium |
| `guarantee_probability` | Chance of support | Regulator | Medium |

## §7 Communication And Round Structure

Market broadcasts bank-health/price state; agents react with withdrawal,
selling, or support actions; market aggregates net pressure and updates state.

## §8 Historical Case Studies

### §8.1 Silicon Valley Bank, March 2023

SVB experienced rapid withdrawals after losses on long-duration securities and
confidence deterioration among concentrated uninsured depositors.

### §8.2 Classic Bank Runs

Historical bank runs show that depositor expectations can become
self-fulfilling when liquidity is limited.

## §9 Variant Comparison Preview

Rule uses explicit thresholds. LLM may alter depositor and influencer panic
timing. RuleLLM combines explicit thresholds with LLM judgment. Rag may use
retrieved banking-crisis context to alter intervention and panic reasoning.
