# MentalAccounting Simulation Bases

## §1 Phenomenon Definition

MentalAccounting models investors who separate wealth into psychological
accounts instead of optimizing a unified portfolio. This causes local
gain/loss framing, house-money risk taking, sunk-cost holding, and divergence
from rational portfolio management.

## §2 Theoretical Foundation

### §2.1 Mental Accounting

Thaler's mental accounting theory explains how investors evaluate outcomes in
separate accounts rather than by total wealth.

### §2.2 House-Money Effect

After gains, investors may treat profits as less painful to lose and increase
risk taking.

### §2.3 Sunk-Cost Effect

Investors may continue holding losing positions because prior investment is
psychologically salient.

## §3 Market Mechanism

The market aggregates buy and sell orders into a price update using net demand,
mean reversion, and noise. Mental-accounting agents affect price by generating
biased order flow rather than by changing the market formula.

## §4 Investor Archetypes

### §4.1 MentalAccountant

**Summary**: Segregates portfolio outcomes into separate accounts.
**Theoretical and Empirical Basis**: Thaler's mental accounting.
**Design Purpose**: Produce account-level gain/loss decisions.
**Behavioral Framework**: Uses `num_accounts` and `loss_aversion_per_account`.
**Decision Process**: Reacts to account-local losses more strongly than total
portfolio outcomes.
**Worked Numerical Example**: A loss in one account can trigger selling even if
the total portfolio is profitable.
**Academic References**: Thaler (1985, 1999).

### §4.2 HouseMoneyTrader

**Summary**: Increases risk after gains and cuts risk after losses.
**Theoretical and Empirical Basis**: House-money effect in behavioral finance.
**Design Purpose**: Add asymmetric risk appetite after recent outcomes.
**Behavioral Framework**: Uses gain and loss risk multipliers.
**Decision Process**: Larger buy quantities after gains, smaller risk after
losses.
**Worked Numerical Example**: With `gain_risk_multiplier > 1`, a profitable
round increases next-round demand.
**Academic References**: Thaler and Johnson (1990).

### §4.3 RationalPortfolioManager

**Summary**: Optimizes at portfolio level without account segregation.
**Theoretical and Empirical Basis**: Mean-variance portfolio reasoning.
**Design Purpose**: Provide rational benchmark behavior.
**Behavioral Framework**: Uses `risk_aversion`.
**Decision Process**: Trades on aggregate risk-return rather than account-level
framing.
**Worked Numerical Example**: If total portfolio risk is high, reduces exposure
even if one account is profitable.
**Academic References**: Markowitz (1952).

### §4.4 SunkCostHolder

**Summary**: Holds losing positions because prior investment is salient.
**Theoretical and Empirical Basis**: Sunk-cost fallacy.
**Design Purpose**: Generate delayed selling and sticky losing positions.
**Behavioral Framework**: Anchors on invested cost rather than current expected
return.
**Decision Process**: Holds despite negative signal when sale would realize a
psychological loss.
**Worked Numerical Example**: A position down 20% remains held if the purchase
price is treated as recoverable.
**Academic References**: Arkes and Blumer (1985).

### §4.5 NoiseTrader

**Summary**: Random uninformed trader.
**Theoretical and Empirical Basis**: Noise-trader models.
**Design Purpose**: Add baseline liquidity and stochastic order flow.
**Behavioral Framework**: Uses `trade_probability`.
**Decision Process**: Random buy/sell/hold.
**Worked Numerical Example**: With 5% trade probability, most rounds are hold.
**Academic References**: Black (1986).

## §5 Agent Diversity Verification

The population includes biased account-level traders, outcome-dependent
risk-takers, rational benchmark managers, sticky loss holders, and noise
traders.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `num_accounts` | Number of psychological accounts | MentalAccountant | Medium |
| `loss_aversion_per_account` | Account-local loss sensitivity | MentalAccountant | High |
| `gain_risk_multiplier` | Risk increase after gains | HouseMoneyTrader | High |
| `loss_risk_multiplier` | Risk reduction after losses | HouseMoneyTrader | Medium |
| `risk_aversion` | Rational risk penalty | RationalPortfolioManager | Medium |
| `trade_probability` | Random trading frequency | NoiseTrader | Low |

## §7 Communication And Round Structure

Market broadcasts state; investors update psychological or rational state;
orders are routed back to market; price updates from net demand.

## §8 Historical Case Studies

### §8.1 Retail Portfolio Segmentation

Retail investors often separate retirement, speculative, and cash accounts,
leading to inconsistent risk decisions across accounts.

### §8.2 Casino And Trading Gains

House-money behavior is observed when recent gains increase willingness to take
additional risk.

## §9 Variant Comparison Preview

Rule expresses fixed behavioral rules. LLM expresses account framing through
persona reasoning. RuleLLM anchors the LLM to explicit formulas. Rag may inject
behavioral-finance context that changes explanations or strength of bias.
