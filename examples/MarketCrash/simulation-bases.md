# MarketCrash Simulation Bases

## §1 Phenomenon Definition

MarketCrash models an endogenous crash in which falling prices, rising
volatility, liquidity withdrawal, and forced deleveraging amplify one another.
The scenario is not driven by exogenous news; the main mechanism is internal
feedback between market state and heterogeneous investor reactions.

## §2 Theoretical Foundation

### §2.1 Volatility Targeting

Risk-managed portfolios reduce exposure when realized volatility rises. This
creates mechanical selling pressure after the market has already weakened.

### §2.2 Leverage And Margin Spirals

Leveraged investors facing margin constraints must deleverage into drawdowns,
which pushes prices lower and worsens balance-sheet stress.

### §2.3 Liquidity Withdrawal

Liquidity providers reduce activity when volatility is high. Price impact then
increases precisely when sell pressure is strongest.

### §2.4 Behavioral Panic And Contrarian Absorption

Some investors panic-sell after losses, while contrarian buyers only step in
after deep discounts. The timing mismatch determines whether the crash
stabilizes or cascades.

## §3 Market Mechanism

The coordinator receives investor orders each round and updates price with a
liquidity-sensitive impact equation plus mean reversion and noise.

- Rule variant: `examples/MarketCrash/Rule/players.py:Market`
  tracks `price`, `volatility`, `liquidity`, `volume`, `net_demand`, and
  `is_crash`.
- RuleLLM and Rag variants: their `Market` coordinators use explicit
  `provides_liquidity` flags from investor orders to measure available depth.
- LLM variant: its coordinator does not consume `provides_liquidity`; it uses
  internal liquidity state driven by net demand and volatility.

## §4 Investor Archetypes

### §4.1 RiskParityFund

**Summary**: A volatility-targeting institutional investor.  
**Design Purpose**: Add procyclical selling when volatility rises.  
**Implementation Ground Truth**: Rule uses `target_volatility=2.0`,
`vol_lookback=5`, `rebalance_speed=0.3`, `base_position=50.0`.

### §4.2 LeveragedHedgeFund

**Summary**: A leveraged investor subject to margin calls and liquidation.  
**Design Purpose**: Create forced deleveraging after losses.  
**Implementation Ground Truth**: Rule uses `initial_leverage=3.0`,
`margin_call_level=0.5`, `liquidation_level=0.3`,
`momentum_sensitivity=0.5`.

### §4.3 MarketMaker

**Summary**: A liquidity supplier that withdraws under stress.  
**Design Purpose**: Make crash severity depend on endogenous market depth.  
**Implementation Ground Truth**: Rule uses
`volatility_withdraw_threshold=5.0`, `inventory_limit=30.0`,
`normal_quote_size=20.0`, `spread_multiplier=0.02`.

### §4.4 PassiveInvestor

**Summary**: A slow stabilizing allocator that rebalances only occasionally.  
**Design Purpose**: Provide delayed, weak mean-reverting demand in the Rule
baseline.  
**Implementation Ground Truth**: Rule uses `rebalance_frequency=20`,
`target_position=30.0`.

### §4.5 PanicSeller

**Summary**: A loss-sensitive investor that sells after drawdowns or sharp
single-round drops.  
**Design Purpose**: Add discretionary crash amplification.  
**Implementation Ground Truth**: Rule uses `loss_threshold=0.10`,
`crash_trigger=-0.03`, `panic_sell_fraction=0.5`.

### §4.6 BottomFisher

**Summary**: A contrarian buyer that enters after large discounts.  
**Design Purpose**: Test whether opportunistic capital can absorb forced sales.  
**Implementation Ground Truth**: Rule uses `crash_buy_threshold=-0.03`,
`discount_threshold=0.10`, `buy_size=15.0`, `lookback=10`.

## §5 Agent Diversity Verification

The full Rule baseline contains six investor archetypes:
RiskParityFund, LeveragedHedgeFund, MarketMaker, PassiveInvestor, PanicSeller,
and BottomFisher.

The current API variants intentionally retain five archetypes:
PanicSeller, RiskParityFund, LeveragedFund, MarketMaker, and BottomFisher.
They omit PassiveInvestor in the configured player set. This is a runtime fact
that variant documentation must describe honestly rather than silently
normalizing away.

## §6 Parameter Table

| Parameter | Value | Used By | Role In Crash |
|---|---:|---|---|
| `base_price_impact` | 0.08 | Market | Base sensitivity of price to net demand |
| `mean_reversion` | 0.01 | Market | Pull toward fundamental value |
| `noise_std` | 0.5 | Market | Small exogenous disturbance |
| `target_volatility` | 2.0 | RiskParityFund | Volatility target for deleveraging |
| `margin_call_level` | 0.5 | LeveragedHedgeFund | Partial deleveraging trigger |
| `liquidation_level` | 0.3 | LeveragedHedgeFund | Forced liquidation trigger |
| `volatility_withdraw_threshold` | 5.0 | MarketMaker | Liquidity withdrawal trigger |
| `rebalance_frequency` | 20 | PassiveInvestor | Slow stabilizing rebalance cadence |
| `panic_sell_fraction` | 0.5 | PanicSeller | Fraction sold in panic state |
| `discount_threshold` | 0.10 | BottomFisher | Entry discount for contrarian buying |

## §7 Communication And Round Structure

Each round follows the same message flow:

1. The market broadcasts current state to all investors.
2. Investors decide order direction, quantity, and price.
3. Orders return to the market through `investor_bid`.
4. The market updates price, liquidity-relevant state, and aggregate records.

RuleLLM and Rag additionally require the canonical order schema field
`provides_liquidity` because their market coordinators distinguish liquidity
provision from directional demand.

## §8 Historical Case Studies

### §8.1 2008 Global Financial Crisis

The scenario draws on the interaction of leverage, funding stress, market-maker
withdrawal, and panic liquidation seen during the 2008 crash.

### §8.2 March 2020 Liquidity Shock

The scenario also resembles rapid liquidity evaporation episodes in which
volatility-targeting and dealer risk limits magnified large price moves.

## §9 Variant Comparison Preview

- **Rule**: six archetypes, deterministic policies, full baseline mechanism.
- **LLM**: five archetypes, persona-driven discretionary API decisions.
- **RuleLLM**: five archetypes, API decisions constrained by explicit rule text.
- **Rag**: five archetypes, RuleLLM-style prompts plus retrieved reference
  context recorded in run artifacts.
