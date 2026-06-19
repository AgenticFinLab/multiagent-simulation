# Panic sellers, forced sellers, early-exit, and stop-loss agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Panic sellers, forced sellers, early-exit, and stop-loss agents |
| Merged profiles | 5 |
| Scenarios | FlashCrash, FlashCrash2010, LiquidityDryup, MarketCrash, TulipMania |
| Observed names | Early Exit Trader, Forced Seller, Panic Seller, Stop Loss Trader |

## Consolidated Definition and Goals

- **FlashCrash / Stop Loss Trader**: **Role:** Stop-loss cascade generator; forced seller at predetermined levels.
- **FlashCrash2010 / Stop Loss Trader**: **Role:** Stop-loss cascade generator; forced seller at pre-set level.
- **LiquidityDryup / Forced Seller**: Noise-trader LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.5
- **MarketCrash / Panic Seller**: **Summary**: A loss-sensitive investor that sells after drawdowns or sharp one-round drops. **Theoretical and Empirical Basis**: Behavioral loss aversion and feedback trading can amplify market declines. **Design Purpose**: Add discretionary crash amplification beyond mechanical deleveraging. **Behavioral Framework**: Uses loss threshold, crash trigger, and panic-sell fraction. **Decision Process**: Track price losses; if cumulative or one-round losses cross the trigger, sell a configured fraction of holdings. **Worked Numerical Example**: With a 10% loss threshold and 50% panic fraction, a 15% drawdown can trigger sale of half the current position. **Academic References**: Kahneman and Tversky (1979, DOI: 10.2307/1914185); Shiller (1984, DOI: 10.2307/2327670).
- **TulipMania / Early Exit Trader**: **Summary**: Participates tactically but exits when speculative excess becomes visible. **Theoretical and Empirical Basis**: Rational bubble riding and strategic liquidation before common exit pressure arrives. **Design Purpose**: Add peak-adjacent selling pressure without redesigning the market as a limit-order book. **Behavioral Framework**: Uses the same overvaluation signal as IntrinsicValueTrader but interprets the sell as early-exit timing. **Decision Process**: If `abs(deviation) > 0.05`, set `quantity = min(500, int(abs(deviation) * 3000))`; buy discounts and sell overvaluation subject to constraints. **Worked Numerical Example**: At price 130 and fundamental 100, deviation is 0.30, so the trader sells up to 500 units if inventory is available. **Academic References**: Historical bubble timing, rational bubble riding, and crash-precursor behavior.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.4 -- StopLossTrader
- Theoretical basis: Stop-loss cascade mechanism; pre-set exit triggers create
- LLM-driven stop-loss trader -- cascade selling triggers via LLM position management. Theory: simulation-bases.md Section 4.4.
- Hybrid: Stop-loss cascade rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
- RAG-augmented stop-loss trader -- cascade rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.
- Theoretical basis: Stop-loss cascade mechanism; fixed stop levels trigger
- LLM-driven stop-loss trader -- cascade selling via LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
- Hybrid: Stop-loss trigger rules + LLM risk management reasoning. Theory: simulation-bases.md Section 4.4.
- RAG-augmented stop-loss trader -- trigger rules + LLM risk management + retrieved knowledge. Theory: simulation-bases.md Section 4.4.
- Noise-trader LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.5
- Hybrid: NoiseTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.5
- RAG-augmented: ForcedSeller rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.5
- Theory: simulation-bases.md Section 4.5.
- LLM PanicSeller. Theory: simulation-bases.md Section 4.5.
- Hybrid PanicSeller. Theory: simulation-bases.md Section 4.5.
- RAG PanicSeller. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.4
- Theoretical Basis: Rational bubble riding (Thompson, 2007)

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| FlashCrash | Stop Loss Trader | [FlashCrash__StopLossTrader.md](../FlashCrash__StopLossTrader.md) |
| FlashCrash2010 | Stop Loss Trader | [FlashCrash2010__StopLossTrader.md](../FlashCrash2010__StopLossTrader.md) |
| LiquidityDryup | Forced Seller | [LiquidityDryup__ForcedSeller.md](../LiquidityDryup__ForcedSeller.md) |
| MarketCrash | Panic Seller | [MarketCrash__PanicSeller.md](../MarketCrash__PanicSeller.md) |
| TulipMania | Early Exit Trader | [TulipMania__EarlyExitTrader.md](../TulipMania__EarlyExitTrader.md) |

