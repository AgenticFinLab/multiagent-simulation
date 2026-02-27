# LiquidityDryupLLM - LLM-Powered Liquidity Dry-up Simulation

## What is This?

| Item               | Description                                                                       |
|--------------------|-----------------------------------------------------------------------------------|
| **Phenomenon**     | 流动性枯竭 (Liquidity Dry-up) - LLM-driven market maker withdrawal cascade        |
| **Model**          | LLM-based investors with withdrawal psychology + Rule-based market                |
| **Key Feature**    | LLM market makers decide when to withdraw liquidity based on perceived risk       |
| **Academic Value** | Tests whether LLMs can reproduce Brunnermeier & Pedersen (2009) liquidity spirals |

## Rule-Based vs LLM Comparison

| Aspect          | Rule-Based (LiquidityDryup)   | LLM Version                        |
|-----------------|-------------------------------|------------------------------------|
| MM Withdrawal   | Formula-based inventory model | LLM reasons about risk conditions  |
| Cascade Trigger | Liquidity < threshold         | LLM observes "others withdrawing"  |
| Arbitrageur     | Deterministic entry           | LLM decides if "prime opportunity" |
| Emergence       | Predictable cascades          | Emergent withdrawal behavior       |

## LLM Provider

- **Provider**: ByteDance Doubao (豆包) via `lmbase.LangChainAPIInference`
- **Model**: `doubao-pro-256k`

## 5 LLM Investor Types

| Type               | Count | Role               | Key Behavior                        |
|--------------------|-------|--------------------|-------------------------------------|
| Market Maker       | 2     | Liquidity Provider | Withdraws when stressed             |
| Liquidity Demander | 2     | Liquidity Consumer | Adjusts trade size by liquidity     |
| Arbitrageur        | 1     | Crisis Opportunist | Provides liquidity when others flee |
| Value Investor     | 1     | Fundamental Anchor | Patient, ignores liquidity          |
| Forced Seller      | 1     | Cascade Trigger    | Must sell regardless of conditions  |

### Market Maker (Withdrawal Decision)

```
WITHDRAWAL CONDITIONS (provides_liquidity = 0):
- Liquidity < 50: Others withdrawing
- Liquidity factor > 1.5: Stressed
- Return > 3%: Too volatile

When ACTIVE: provides_liquidity = 20-40
```

### Arbitrageur (Crisis Opportunity)

```
STRATEGY:
- Liquidity < 40: Prime opportunity
- Price deviation > 5%: Trade opportunity
- PROVIDE liquidity when others withdraw
```

### Forced Seller (Cascade Trigger)

```
- Sell 10-20 shares per round regardless
- Accept price impact as cost
```

## Key Mechanism: Liquidity Spiral

```
                    Forced Selling
                         │
                         ▼
              ┌─────────────────────┐
              │   Price Impact      │
              │   (Low Liquidity)   │
              └──────────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ Volatility│   │   MM     │   │  Margin  │
   │   Spike   │   │ Withdraw │   │  Calls   │
   └────┬─────┘   └────┬─────┘   └────┬─────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │  Liquidity Dry-up   │
              │  (Self-Reinforcing) │
              └─────────────────────┘
```

## Theoretical Basis: Brunnermeier & Pedersen (2009)

**Market Liquidity and Funding Liquidity**:
- Market liquidity (ability to trade) and funding liquidity (ability to borrow) are mutually reinforcing
- Loss spiral: Asset losses → margin calls → forced selling → more losses
- Margin spiral: Volatility → higher margins → deleveraging → lower prices
- LLMs model market makers' rational withdrawal under funding constraints

## Files

| File          | Purpose                                            |
|---------------|----------------------------------------------------|
| `players.py`  | LLM investor implementations with withdrawal logic |
| `prompts.py`  | 5 system prompts defining withdrawal psychology    |
| `run_llm.py`  | LLM simulation runner                              |
| `analysis.py` | Liquidity and cascade metrics                      |

## Running

```bash
cd examples/LiquidityDryupLLM
python run_llm.py
```

## Expected LLM Behavior Patterns

1. **Coordinated Withdrawal**: LLM market makers observe others withdrawing and follow
2. **Liquidity Vacuum**: All MMs withdraw simultaneously → no bid-ask quotes
3. **Opportunistic Entry**: LLM arbitrageurs provide liquidity during panic
4. **Cascade Dynamics**: Forced selling triggers MM withdrawal triggers more selling
5. **Recovery**: Arbitrageurs' liquidity provision enables price recovery

## Research Questions

1. Do LLMs correctly perceive liquidity risk from market conditions?
2. Can LLMs reproduce the "liquidity spiral" without explicit programming?
3. Do LLM arbitrageurs time their entry correctly during dry-ups?
4. How does LLM market maker coordination compare to rule-based withdrawal?

## References

- Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. RFS.
- Kyle, A. S. (1985). Continuous Auctions and Insider Trading. Econometrica.
