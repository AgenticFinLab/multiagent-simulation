# Regulators, central banks, policy defenders, and rescue/backstop agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Regulators, central banks, policy defenders, and rescue/backstop agents |
| Merged profiles | 7 |
| Scenarios | AsianFinancialCrisis, CurrencyCrisis, EuropeanDebtCrisis, GFC2008, LTCMCollapse, SVBBankRun, SorosPound |
| Observed names | Central Bank, Central Bank Defender, ECB Intervenor, IMF Rescuer, Peg Defender, Regulator |

## Consolidated Definition and Goals

- **AsianFinancialCrisis / IMF Rescuer**: IMFRescuer represents the international public-sector rescue mechanism -- the IMF and associated bilateral lenders -- that provides emergency liquidity during severe currency crises. This agent models the two defining features of IMF crisis intervention: (1) very large financial firepower ($5M initial cash, representing the scale of sovereign rescue capacity relative to private investors), and (2) a high activation threshold (-5% deviation), reflecting the IMF's documented reluctance to intervene until the crisis is well-established. The result is a "deep pockets but slow trigger" rescue pattern: prices fall significantly before intervention, but once it begins, the scale of intervention provides meaningful price support.
- **CurrencyCrisis / Central Bank Defender**: **4.3.1 Economic Role**: Government/central bank defending the currency peg by purchasing domestic currency.
- **EuropeanDebtCrisis / ECB Intervenor**: The `ECBIntervenor` represents credible central-bank backstop purchases. It is the main crisis-resolution force when peripheral bond prices fall far below fundamental value.
- **GFC2008 / Regulator**: `Regulator` represents public-sector backstop capacity. It is stabilizing, probabilistic, and deliberately late: intervention occurs only when systemic stress is extremely deep.
- **LTCMCollapse / Central Bank**: The `CentralBank` represents official-sector or coordinated private-sector lender-of-last-resort intervention. It is not a literal central-bank asset purchase model; it abstracts the 1998 coordination role into a stabilizing liquidity injection.
- **SVBBankRun / Regulator**: **Summary**: May intervene with large support when systemic stress is severe. **Theoretical and Empirical Foundation**: Lender-of-last-resort and deposit-guarantee policy. **Design Purpose and Activation Scenarios**: Activates when `deviation < -intervention_threshold`. **Behavioral Framework**: Probabilistic policy response to severe distress. **Mathematical Model**: **Decision Process Walkthrough**: Detect severe run pressure, apply probabilistic support. **Worked Example**: With threshold 0.5, `deviation=-0.6`, and probability 0.4, a successful draw buys 2000 units. **References**: Bagehot lender-of-last-resort doctrine and modern deposit-guarantee practice.
- **SorosPound / Peg Defender**: **Summary**: A central-bank-style defender that intervenes to stabilize the currency proxy when deviation becomes large.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.3 -- IMFRescuer
- Theoretical Basis: International lender of last resort (Corsetti et al., 1999)
- LLM-driven IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.
- RuleLLM IMF rescuer with explicit intervention threshold rules. Theory: simulation-bases.md Section 4.3.
- RAG-augmented IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- CentralBankDefender
- Theoretical basis: Central bank defense mechanisms (Obstfeld, 1996); intervenes
- LLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
- RAG-augmented central bank defender -- buys domestic currency to defend peg. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.4 -- ECBIntervenor
- Theoretical basis: Draghi (2012) 'whatever it takes' backstop mechanism; credible
- LLM-driven ECB intervenor -- whatever-it-takes backstop logic via LLM reasoning. Theory: simulation-bases.md Section 4.4.
- RuleLLM ECB intervenor -- backstop threshold rules with LLM policy reasoning. Theory: simulation-bases.md Section 4.4.
- RAG-augmented ECB intervenor -- backstop purchases with monetary policy literature. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.5 -- Regulator
- Theoretical basis: Macroprudential regulation (Bernanke, 2015).
- LLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
- RuleLLM-driven Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
- RAG-augmented Regulator: monitors systemic risk and may intervene. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.5 -- CentralBank
- Theoretical basis: Bagehot (1873) lender of last resort.
- Theory: simulation-bases.md Section 4.5 -- CentralBank.
- RAG lender-of-last-resort intervention agent. Theory: simulation-bases.md Section 4.5.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AsianFinancialCrisis | IMF Rescuer | [AsianFinancialCrisis__IMFRescuer.md](../AsianFinancialCrisis__IMFRescuer.md) |
| CurrencyCrisis | Central Bank Defender | [CurrencyCrisis__CentralBankDefender.md](../CurrencyCrisis__CentralBankDefender.md) |
| EuropeanDebtCrisis | ECB Intervenor | [EuropeanDebtCrisis__ECBIntervenor.md](../EuropeanDebtCrisis__ECBIntervenor.md) |
| GFC2008 | Regulator | [GFC2008__Regulator.md](../GFC2008__Regulator.md) |
| LTCMCollapse | Central Bank | [LTCMCollapse__CentralBank.md](../LTCMCollapse__CentralBank.md) |
| SVBBankRun | Regulator | [SVBBankRun__Regulator.md](../SVBBankRun__Regulator.md) |
| SorosPound | Peg Defender | [SorosPound__PegDefender.md](../SorosPound__PegDefender.md) |

