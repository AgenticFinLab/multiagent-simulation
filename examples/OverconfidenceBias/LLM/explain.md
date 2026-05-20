# OverconfidenceBias Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Overconfidence bias causes traders to overestimate their precision, trade too much, and increase volatility |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Overconfidence bias simulation showing how excessive self-confidence leads to excessive trading and market instability |
| **Academic Value** | Understanding overconfidence bias causes traders to overestimate their precision, trade too much, and increase volatility through multi-agent simulation |

## §2 Theoretical Foundation

- Daniel, Hirshleifer & Subrahmanyam (1998): Investor psychology and security market under/overreactions
- Odean (1998): Volume, volatility, price, and profit when all traders are above average
- Barber & Odean (2001): Boys will be boys: Gender, overconfidence, and common stock investment

## §3 Agent Descriptions

### OverconfidentTrader
**Theoretical Basis**: Overconfidence bias (Daniel et al., 1998)
**Market Role**: destabilizing
**Description**: Overestimates signal precision, trades too frequently
**Parameters**: precision_overestimate=2.0, trade_frequency=high, position_size=800

### SelfAttributor
**Theoretical Basis**: Self-attribution bias
**Market Role**: destabilizing
**Description**: Attributes success to skill, failure to bad luck
**Parameters**: attribution_bias=0.7, confidence_boost=0.3

### CalibratedTrader
**Theoretical Basis**: Rational expectations
**Market Role**: stabilizing
**Description**: Correctly estimates signal precision, trades appropriately
**Parameters**: signal_precision=0.6, trade_threshold=0.02, position_size=500

### ContrarianInvestor
**Theoretical Basis**: Contrarian strategy
**Market Role**: stabilizing
**Description**: Trades against overconfident moves
**Parameters**: contrarian_threshold=0.05, patience=high

### NoiseTrader
**Theoretical Basis**: Black (1986)
**Market Role**: neutral
**Description**: Random uninformed trader
**Parameters**: trade_probability=0.05, min_order=100, max_order=500


## §4 Usage

### Rule Variant
```bash
python examples/OverconfidenceBias/Rule/run_overconfidencebias.py \
    -c configs/OverconfidenceBias/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/OverconfidenceBias/LLM/run_overconfidencebias_llm.py \
    -c configs/OverconfidenceBias/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/OverconfidenceBias/RuleLLM/run_overconfidencebias_rulellm.py \
    -c configs/OverconfidenceBias/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/OverconfidenceBias/Rag/run_overconfidencebias_rag.py \
    -c configs/OverconfidenceBias/Rag/simulation.yml
```

## §5 References

- Daniel, Hirshleifer & Subrahmanyam (1998): Investor psychology and security market under/overreactions
- Odean (1998): Volume, volatility, price, and profit when all traders are above average
- Barber & Odean (2001): Boys will be boys: Gender, overconfidence, and common stock investment

## §6 Expected Mechanism

The simulation is expected to show how LLM-driven agents express overconfidence
through aggressive interpretation of private signals, frequent trading, and
larger position changes. Calibrated and contrarian agents provide stabilizing
comparison groups, while noise traders maintain baseline market uncertainty.

## §7 Experimental Controls

- Prompts should preserve the overconfidence mechanism without changing the
  market role of each agent.
- LLM responses must use the configured trading action schema so market state
  updates remain comparable to other variants.
- The same fundamental value process and initial endowments should be used
  across variants.

## §8 Success Criteria

- The run completes the configured number of rounds without runtime errors.
- LLM outputs produce valid trading actions without requiring fallback holds.
- Price deviations, volatility, and trading volume can be compared with the Rule
  baseline to evaluate LLM-mediated overconfidence.

## §9 Notes

This variant relies on prompt-guided decisions. Any prompt revision should keep
the agent roles and trading schema stable unless the affected mode is scheduled
for rerun.
