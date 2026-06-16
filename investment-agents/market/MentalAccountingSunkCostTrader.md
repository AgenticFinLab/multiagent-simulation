# Mental-accounting, house-money, sunk-cost, and opportunity-cost agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Mental-accounting, house-money, sunk-cost, and opportunity-cost agents |
| Merged profiles | 6 |
| Scenarios | MentalAccounting, SunkCostFallacy |
| Observed names | Commitment Escalator, House Money Trader, Mental Accountant, Opportunity Cost Trader, Sunk Cost Holder |

## Consolidated Definition and Goals

- **MentalAccounting / House Money Trader**: 1. **Summary**: Takes more risk after gains and less after losses. This creates outcome-dependent order size. 2. **Theoretical and Empirical Foundation**: Thaler & Johnson (1990) document increased risk acceptance after prior gains. 3. **Design Purpose and Activation Scenarios**: Activates when price deviation exceeds the configured threshold and risk appetite depends on current P&L. 4. **Behavioral Framework**: Uses `gain_risk_multiplier`, `loss_risk_multiplier`, `base_size`, and `deviation_threshold`. 5. **Decision Process Walkthrough**: Compute P&L; choose risk factor; buy undervaluation or sell overvaluation when deviation is large enough. 6. **Worked Numerical Example**: With `base_size=400`, `pnl>0`, and `gain_risk_multiplier=2.0`, candidate size is 800 before cash/inventory constraints. 7. **Academic References**: Thaler & Johnson (1990); Barberis & Huang (2001).
- **MentalAccounting / Mental Accountant**: 1. **Summary**: Segregates current holdings into separate mental accounts and evaluates each account relative to entry price. This creates local realization behavior that can diverge from total-portfolio optimization. 2. **Theoretical and Empirical Foundation**: Thaler (1999) explains account coding; Odean (1998) and Shefrin & Statman (1985) document account-level realization patterns. 3. **Design Purpose and Activation Scenarios**: Activates when account-level P&L crosses gain or loss thresholds. 4. **Behavioral Framework**: Uses `num_accounts`, `loss_aversion_per_account`, current `position`, and `entry_price`. 5. **Decision Process Walkthrough**: Compute account P&L; sell 70% of one account after gains above 5%; reluctantly sell 20% of one account after loss threshold; otherwise hold. 6. **Worked Numerical Example**: With `position=600`, `num_accounts=3`, and `pnl=+8%`, per-account position is 200 and sell quantity is 140. 7. **Academic References**: Thaler (1985, 1999); Odean (1998); Shefrin & Statman (1985).
- **MentalAccounting / Sunk Cost Holder**: 1. **Summary**: Holds losing positions because past investment remains psychologically salient. It sells only after sufficiently large gains. 2. **Theoretical and Empirical Foundation**: Arkes & Blumer (1985) document sunk-cost persistence. 3. **Design Purpose and Activation Scenarios**: Creates sticky losing inventory and delayed selling. 4. **Behavioral Framework**: Uses `sunk_cost_weight`, entry price, current price, and position. 5. **Decision Process Walkthrough**: Compute P&L; sell a configured fraction only after gains exceed 10%; otherwise hold. 6. **Worked Numerical Example**: With `position=500`, `sunk_cost_weight=0.6`, and `pnl=+12%`, sell quantity is 300. 7. **Academic References**: Arkes & Blumer (1985); Shefrin & Statman (1985).
- **SunkCostFallacy / Commitment Escalator**: This investor represents decision makers who add resources to a failing position to justify prior choices.
- **SunkCostFallacy / Opportunity Cost Trader**: This investor compares current exposure with the best available use of capital.
- **SunkCostFallacy / Sunk Cost Holder**: This investor represents traders who keep a losing position because exiting would make the prior mistake explicit.

## Consolidated Financial Theory

- Takes more risk with recent gains (house money effect).
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader
- Theoretical basis: simulation-bases.md Section 4.2 -- HouseMoneyTrader.
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant
- Theoretical basis: simulation-bases.md Section 4.1 -- MentalAccountant.
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder
- Theoretical basis: simulation-bases.md Section 4.4 -- SunkCostHolder.
- Theory: simulation-bases.md Section 4.2 -- CommitmentEscalator
- Theoretical basis: escalation of commitment (Staw, 1976).
- LLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
- RuleLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
- RagLLM commitment escalator doubling down on losing positions. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.4 -- OpportunityCostTrader
- Theoretical basis: opportunity cost analysis.
- LLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
- RuleLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
- RagLLM opportunity cost trader reallocating from underperformers. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.1 -- SunkCostHolder
- Theoretical basis: sunk cost escalation (Arkes & Blumer, 1985).
- LLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.
- RuleLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.
- RagLLM sunk cost holder refusing to cut losing positions. Theory: simulation-bases.md Section 4.1.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| MentalAccounting | House Money Trader | [MentalAccounting__HouseMoneyTrader.md](../MentalAccounting__HouseMoneyTrader.md) |
| MentalAccounting | Mental Accountant | [MentalAccounting__MentalAccountant.md](../MentalAccounting__MentalAccountant.md) |
| MentalAccounting | Sunk Cost Holder | [MentalAccounting__SunkCostHolder.md](../MentalAccounting__SunkCostHolder.md) |
| SunkCostFallacy | Commitment Escalator | [SunkCostFallacy__CommitmentEscalator.md](../SunkCostFallacy__CommitmentEscalator.md) |
| SunkCostFallacy | Opportunity Cost Trader | [SunkCostFallacy__OpportunityCostTrader.md](../SunkCostFallacy__OpportunityCostTrader.md) |
| SunkCostFallacy | Sunk Cost Holder | [SunkCostFallacy__SunkCostHolder.md](../SunkCostFallacy__SunkCostHolder.md) |

