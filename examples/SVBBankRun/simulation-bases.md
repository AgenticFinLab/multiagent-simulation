# SVBBankRun — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Silicon Valley Bank-style rapid bank run represented through a bank-health/security-price proxy market. |
| Category | Bank run, duration mismatch, information contagion, policy intervention. |
| Core Mechanism | Long-duration asset losses weaken perceived bank health. Depositors and information amplifiers coordinate withdrawal pressure; bank managers and regulators add support; bond traders transmit duration-loss signals. Net pressure moves the bank-health proxy price. |
| Real-World Origin | Silicon Valley Bank failed in March 2023 after unrealized securities losses, uninsured depositor concentration, and rapid withdrawal coordination. |
| Research Relevance | The scenario tests how coordination, social amplification, balance-sheet support, and policy intervention interact in an agent-based crisis market. |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

The classic bank-run mechanism begins with Diamond and Dybvig's model of
maturity transformation: banks hold illiquid long-term assets while issuing
short-term withdrawable liabilities. A run can become self-fulfilling because
early withdrawal is individually rational when depositors expect others to run.

The SVB episode adds two modern channels. First, rising interest rates reduced
the market value of long-duration securities and exposed unrealized losses.
Second, concentrated uninsured depositors coordinated rapidly through venture
capital networks, digital communication, and social-media signals. The simulation
therefore combines bank-run coordination with a duration-loss balance-sheet shock
and information amplification.

This implementation represents the bank as a tradable bank-health/security-price
proxy rather than a literal deposit ledger. `sell` orders represent withdrawal,
panic, or confidence loss; `buy` orders represent balance-sheet support,
confidence provision, or regulatory stabilization. This proxy keeps the four
variants comparable inside the existing market/order architecture while still
preserving the causal interpretation of a bank run.

#### §1.1.2 Real-World Event Catalogue

| Event Name | Date(s) | Market / Asset | Trigger | Magnitude | Duration | Correspondence to Simulation | Primary Source |
|---|---|---|---|---|---|---|---|
| Silicon Valley Bank failure | March 8-10, 2023 | U.S. regional banking | Securities-loss disclosure and uninsured depositor withdrawal coordination | About $42B withdrawal request on March 9; FDIC receivership March 10 | Two trading days | Depositor sell pressure, social amplification, duration-loss signal, regulator support | Federal Reserve SVB review, 2023 |
| Continental Illinois run | May-July 1984 | U.S. commercial banking | Loan losses and wholesale funding flight | More than $10B emergency support package | Weeks | Depositor/wholesale funding pressure and regulator support | FDIC history, 1984/1997 |
| Northern Rock run | September 2007 | U.K. mortgage bank | Wholesale funding freeze after subprime stress | Public depositor queues; Bank of England emergency support | Days to months | Panic amplification and lender-of-last-resort intervention | U.K. Treasury and Bank of England reports, 2007-2008 |
| Washington Mutual failure | September 2008 | U.S. thrift banking | Mortgage losses and deposit outflows | About $16.7B deposits withdrawn over 10 days | Ten days | Depositor flight and regulatory resolution | OTS / FDIC crisis materials, 2008 |

#### §1.1.3 Book and Practitioner Literature

| Title | Author(s) | Year | Publisher | Relevance to This Simulation |
|---|---|---:|---|---|
| The Alchemists | Neil Irwin | 2013 | Penguin | Central-bank crisis response and lender-of-last-resort policy context. |
| The Courage to Act | Ben S. Bernanke | 2015 | W. W. Norton | Practitioner account of banking panic containment and emergency facilities. |
| Bank Failures in the Major Trading Countries of the World | Benton E. Gup | 1998 | Quorum | Comparative bank-failure mechanisms and regulatory response patterns. |

## §2 Theoretical Foundation

### §2.1 Bank-Run Coordination Theory

Diamond and Dybvig (1983), "Bank Runs, Deposit Insurance, and Liquidity,"
*Journal of Political Economy*, 91(3), 401-419, DOI:
https://doi.org/10.1086/261155.

Core model: depositors choose early withdrawal when expected late liquidation
value is dominated by the risk that others withdraw first. In this simulation,
the depositor's `withdrawal_threshold` maps that coordination concern to the
bank-health proxy deviation.

Formal proxy:
```
withdraw_i(t) = 1[deviation(t) < -withdrawal_threshold_i]
sell_qty_i(t) = min(position_i(t), withdrawal_cap)
```

Relevant agents: `Depositor` (§4.1), `Regulator` (§4.4).

### §2.2 Duration Mismatch And Mark-To-Market Losses

Duration theory links interest-rate changes to bond-price losses. A bank holding
long-duration assets and short-duration deposits becomes fragile when rising
rates reduce asset values while depositors can leave at par.

Formal proxy:
```
duration_loss ≈ -duration_gap × Δyield
bank_health_proxy(t+1) = bank_health_proxy(t) + λ × net_demand(t) + γ × [F - P(t)] + ε(t)
```

Relevant agents: `BankManager` (§4.3), `BondTrader` (§4.5).

### §2.3 Information Cascades And Social Amplification

Bikhchandani, Hirshleifer, and Welch (1992), "A Theory of Fads, Fashion,
Custom, and Cultural Change as Informational Cascades," *Journal of Political
Economy*, 100(5), 992-1026, DOI: https://doi.org/10.1086/261849.

The social channel converts weak private signals into public pressure. In the
simulation, negative deviation below a panic threshold is multiplied by
`amplification_factor` to produce additional sell pressure.

Formal proxy:
```
amplified_sell_qty(t) = min(|deviation(t)| × amplification_factor × 2000, position)
```

Relevant agent: `SocialMediaInfluencer` (§4.2).

### §2.4 Lender-Of-Last-Resort Stabilization

Bagehot-style crisis management recommends lending freely against good collateral
at penalty rates during panic. In this simulation, intervention is represented
as probabilistic support buying once bank-health deviation crosses a severe
threshold.

Formal proxy:
```
intervention(t) = 1[deviation(t) < -intervention_threshold] × Bernoulli(guarantee_probability)
support_qty(t) = intervention_size
```

Relevant agent: `Regulator` (§4.4).

## §3 Market Design

### §3.1 Proxy Price Formation

The market is a bank-health/security-price proxy, not a literal deposit ledger.

```
P(t+1) = max(0.01, P(t) + price_impact × net_demand(t)
                 + mean_reversion × [fundamental_value - P(t)] + ε(t))
```

| Symbol | Code variable | Config path | Meaning |
|---|---|---|---|
| `P(t)` | `price` | `market.extras.initial_price` | Bank-health proxy price. |
| `F` | `fundamental` | `market.extras.fundamental_value` | Stable-health reference value. |
| `λ` | `price_impact` | `market.extras.price_impact` | Sensitivity to net run/support pressure. |
| `γ` | `mean_reversion` | `market.extras.mean_reversion` | Stabilizing pull toward fundamental health. |
| `ε(t)` | `noise` | `market.extras.noise_std` | Exogenous state noise. |

### §3.2 Action Schema

All variants use `investor_order` payloads:

```json
{"action": "buy|sell|hold", "quantity": 0, "agent_type": "Depositor"}
```

Interpretation:
- `sell`: withdrawal, panic, confidence loss, or bond-loss pressure.
- `buy`: support, stabilization, or confidence provision.
- `hold`: no new pressure this round.

## §4 Investor Archetypes

### §4.1 Depositor

**Summary**: Withdraws when perceived bank health deteriorates.
**Theoretical and Empirical Foundation**: Diamond-Dybvig coordination-run logic.
**Design Purpose and Activation Scenarios**: Activates when `deviation < -withdrawal_threshold`.
**Behavioral Framework**: Risk-averse liquidity protection; sell pressure is the proxy for withdrawal.
**Mathematical Model**:
```
sell_qty = min(1000, position) if deviation < -withdrawal_threshold else 0
```
**Decision Process Walkthrough**: Observe deviation, compare to threshold, sell available proxy units if stress is severe.
**Worked Example**: With `withdrawal_threshold=0.1`, `deviation=-0.15`, and `position=600`, the depositor sells 600.
**References**: Diamond and Dybvig (1983).

### §4.2 SocialMediaInfluencer

**Summary**: Amplifies negative bank-health signals.
**Theoretical and Empirical Foundation**: Information cascades and social contagion.
**Design Purpose and Activation Scenarios**: Adds panic pressure when `deviation < -0.05`.
**Behavioral Framework**: Public-risk amplification rather than portfolio optimization.
**Mathematical Model**:
```
sell_qty = min(abs(deviation) × amplification_factor × 2000, position)
```
**Decision Process Walkthrough**: Convert negative deviation into proportional sell pressure.
**Worked Example**: `deviation=-0.08`, `amplification_factor=2.0`, `position=500` yields 320 sell units.
**References**: Bikhchandani, Hirshleifer, and Welch (1992).

### §4.3 BankManager

**Summary**: Provides stabilizing support when the proxy price is under stress.
**Theoretical and Empirical Foundation**: Asset-liability management under duration mismatch.
**Design Purpose and Activation Scenarios**: Buys when `deviation < -0.05`.
**Behavioral Framework**: Balance-sheet support constrained by available cash.
**Mathematical Model**:
```
buy_qty = min(500, floor(cash / price)) if deviation < -0.05 else 0
```
**Decision Process Walkthrough**: Observe stress, deploy limited support if affordable.
**Worked Example**: At price 95 and cash 3,000,000, stress triggers the cap of 500 buy units.
**References**: Duration-risk and asset-liability management literature.

### §4.4 Regulator

**Summary**: May intervene with large support when systemic stress is severe.
**Theoretical and Empirical Foundation**: Lender-of-last-resort and deposit-guarantee policy.
**Design Purpose and Activation Scenarios**: Activates when `deviation < -intervention_threshold`.
**Behavioral Framework**: Probabilistic policy response to severe distress.
**Mathematical Model**:
```
buy_qty = intervention_size if deviation < -intervention_threshold and U < guarantee_probability else 0
```
**Decision Process Walkthrough**: Detect severe run pressure, apply probabilistic support.
**Worked Example**: With threshold 0.5, `deviation=-0.6`, and probability 0.4, a successful draw buys 2000 units.
**References**: Bagehot lender-of-last-resort doctrine and modern deposit-guarantee practice.

### §4.5 BondTrader

**Summary**: Trades the proxy based on rate-sensitive asset valuation.
**Theoretical and Empirical Foundation**: Fixed-income duration and mark-to-market loss transmission.
**Design Purpose and Activation Scenarios**: Reacts when `abs(deviation) > 0.03`.
**Behavioral Framework**: Opportunistic rates specialist; buys undervaluation and sells overvaluation.
**Mathematical Model**:
```
qty = min(500, floor(abs(deviation) × 3000))
buy if deviation < 0, sell if deviation > 0
```
**Decision Process Walkthrough**: Convert valuation deviation into bounded directional pressure.
**Worked Example**: `deviation=-0.07` yields `qty=210`; the trader buys if cash permits.
**References**: Fixed-income duration and crisis mark-to-market literature.

## §5 Agent Diversity Verification

| Agent | Direction In Stress | Stabilizing? | Primary Mechanism |
|---|---|---|---|
| Depositor | Sell | No | Withdrawal coordination |
| SocialMediaInfluencer | Sell | No | Panic amplification |
| BankManager | Buy | Yes | Balance-sheet support |
| Regulator | Buy | Yes | Policy intervention |
| BondTrader | Buy or sell | Mixed | Duration-loss repricing |

## §6 Parameter Table

| Parameter | Config Path | Runtime Use | Source Rationale |
|---|---|---|---|
| `withdrawal_threshold` | depositor extras | Depositor run trigger | Coordination-run sensitivity. |
| `amplification_factor` | socialmediainfluencer extras | Panic-signal multiplier | Information cascade amplification. |
| `duration_gap` | bankmanager extras | ALM stress marker | Duration mismatch channel. |
| `intervention_threshold` | regulator extras | Policy response trigger | Severe-stress response threshold. |
| `guarantee_probability` | regulator extras | Intervention probability | Policy uncertainty. |
| `price_impact` | market extras | Net demand impact | Proxy-market run pressure. |
| `mean_reversion` | market extras | Stabilization pull | Fundamental health reference. |
| `noise_std` | market extras | Exogenous shock | Unmodeled banking news. |

## §7 Communication And Round Structure

1. Market broadcasts `price`, `fundamental`, `deviation`, `volume`, and `net_demand`.
2. Agents perceive the bank-health proxy state.
3. Rule agents compute deterministic proxy orders; API agents emit the same schema after parsing.
4. Market aggregates orders and updates the proxy price for the next round.

## §8 Historical Case Studies

### §8.1 Silicon Valley Bank, 2023

Maps to duration losses, uninsured depositor concentration, rapid withdrawal
coordination, and emergency regulatory action.

### §8.2 Northern Rock, 2007

Maps to panic visibility, depositor coordination, and lender-of-last-resort
support under funding-market stress.

### §8.3 Continental Illinois, 1984

Maps to wholesale funding pressure and regulatory stabilization of a large bank.

### §8.4 Washington Mutual, 2008

Maps to cumulative deposit outflows and regulatory resolution during mortgage
credit stress.

## §9 Variant Comparison Preview

| Variant | Expected Contribution |
|---|---|
| Rule | Deterministic threshold baseline for proxy bank-run pressure. |
| LLM | Tests whether persona-only reasoning changes timing and size of withdrawal/support actions. |
| RuleLLM | Tests whether explicit rules plus LLM reasoning stay aligned with the deterministic benchmark. |
| Rag | Tests whether historical bank-crisis retrieval changes panic sensitivity or support reasoning. |
