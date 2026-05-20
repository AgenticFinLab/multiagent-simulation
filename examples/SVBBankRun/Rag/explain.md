# SVBBankRun Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | March 2023 SVB collapse - $42B deposit outflow in one day triggered by social media panic |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Silicon Valley Bank run simulation with social media-accelerated deposit flight and duration risk |
| **Academic Value** | Understanding march 2023 svb collapse - $42b deposit outflow in one day triggered by social media panic through multi-agent simulation |

## §2 Theoretical Foundation

- Diamond & Dybvig (1983): Bank runs, deposit insurance, and liquidity
- Iyer & Puri (2012): Social networks in bank runs
- Duffie et al. (2023): SVB failure analysis

## §3 Agent Descriptions

### Depositor
**Theoretical Basis**: Diamond-Dybvig bank run model
**Market Role**: destabilizing
**Description**: Decides whether to withdraw deposits based on bank health and others' actions
**Parameters**: deposit_amount=1000000, withdrawal_threshold=0.1, social_influence=0.6

### SocialMediaInfluencer
**Theoretical Basis**: Social media amplification
**Market Role**: destabilizing
**Description**: Amplifies panic signals to accelerate bank run
**Parameters**: follower_count=10000, amplification_factor=3.0, panic_threshold=0.05

### BankManager
**Theoretical Basis**: Asset-liability management
**Market Role**: neutral
**Description**: Manages bank's duration risk and attempts to stabilize
**Parameters**: duration_gap=6.0, htm_ratio=0.6, capital_ratio=0.08

### Regulator
**Theoretical Basis**: Deposit insurance and lender of last resort
**Market Role**: stabilizing
**Description**: May intervene with guarantees or liquidity support
**Parameters**: intervention_threshold=0.3, guarantee_probability=0.7

### BondTrader
**Theoretical Basis**: Fixed income trading
**Market Role**: neutral
**Description**: Trades bonds based on interest rate expectations
**Parameters**: duration_target=5.0, position_size=10000


## §4 Usage

### Rule Variant
```bash
python examples/SVBBankRun/Rule/run_svbbankrun.py \
    -c configs/SVBBankRun/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/SVBBankRun/LLM/run_svbbankrun_llm.py \
    -c configs/SVBBankRun/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/SVBBankRun/RuleLLM/run_svbbankrun_rulellm.py \
    -c configs/SVBBankRun/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/SVBBankRun/Rag/run_svbbankrun_rag.py \
    -c configs/SVBBankRun/Rag/simulation.yml
```

## §5 References

- Diamond & Dybvig (1983): Bank runs, deposit insurance, and liquidity
- Iyer & Puri (2012): Social networks in bank runs
- Duffie et al. (2023): SVB failure analysis
