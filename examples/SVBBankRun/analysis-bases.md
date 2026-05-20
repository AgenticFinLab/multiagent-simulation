# SVBBankRun Analysis Bases

## §1 Analysis Objectives

The analysis verifies whether withdrawal pressure, information amplification,
duration losses, and policy intervention produce a recognizable bank-run
dynamic.

## §2 Metrics

### §2.1 Withdrawal Pressure

```python
def compute_withdrawal_pressure(orders: list[dict]) -> float
```

Measures depositor exit volume.

### §2.2 Panic Amplification

```python
def compute_panic_amplification(messages: list[dict]) -> float
```

Measures how strongly social signals amplify negative state.

### §2.3 Bank Health Drawdown

```python
def compute_health_drawdown(health_series: list[float]) -> float
```

Captures deterioration in bank-health proxy.

### §2.4 Intervention Timing

```python
def compute_intervention_round(events: list[dict]) -> int
```

Finds the first regulatory support action.

### §2.5 Bond-Loss Contribution

```python
def compute_bond_loss_contribution(orders: list[dict]) -> float
```

Attributes sell pressure to bond-related repricing.

### §2.6 Run Onset Round

```python
def compute_run_onset(health_series: list[float], threshold: float) -> int
```

Identifies when the bank run begins.

### §2.7 Stabilization Effect

```python
def compute_stabilization_effect(pre: list[float], post: list[float]) -> float
```

Compares bank health before and after intervention.

## §3 Analysis Dimensions

Deposit flight, social amplification, duration loss, regulatory response, and
stabilization.

## §4 Phase Analysis

Early rounds show latent duration risk. Middle rounds show depositor/influencer
coordination. Later rounds show intervention or collapse.

## §5 Cross-Variant Comparison

Rule provides threshold benchmark. LLM may accelerate or delay panic. RuleLLM
should stay threshold-aligned. Rag may cite bank-run precedents and change
support expectations.

## §6 Expected Results

Depositor and influencer pressure should dominate run onset; regulator action
should reduce or reverse pressure if activated.

## §7 Visualization Plan

Plot bank-health proxy, withdrawal volume, panic amplification, bond sell
pressure, and intervention markers across variants.
