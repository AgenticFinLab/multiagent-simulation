# AsianFinancialCrisis / IMF Rescuer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AsianFinancialCrisis |
| Agent type | IMF Rescuer |
| Canonical class | `IMFRescuer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

IMFRescuer represents the international public-sector rescue mechanism -- the IMF and associated bilateral lenders -- that provides emergency liquidity during severe currency crises. This agent models the two defining features of IMF crisis intervention: (1) very large financial firepower ($5M initial cash, representing the scale of sovereign rescue capacity relative to private investors), and (2) a high activation threshold (-5% deviation), reflecting the IMF's documented reluctance to intervene until the crisis is well-established. The result is a "deep pockets but slow trigger" rescue pattern: prices fall significantly before intervention, but once it begins, the scale of intervention provides meaningful price support.

## Financial Theory / Theoretical Basis

### Rule / `IMFRescuer`
- Theory: simulation-bases.md Section 4.3 -- IMFRescuer
- Theoretical Basis: International lender of last resort (Corsetti et al., 1999)

### LLM / `LLMIMFRescuer`
- LLM-driven IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMIMFRescuer`
- RuleLLM IMF rescuer with explicit intervention threshold rules. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMIMFRescuer`
- RAG-augmented IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_ratio | Rule: `0.25` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `5000000.0`<br>LLM: `5000000.0`<br>RuleLLM: `5000000.0`<br>Rag: `5000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_IMF_RESCUER_SYS', 'user_message': 'examples.AsianFinancialCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_IMF_RESCUER_SYS', 'user_message': 'examples.AsianFinancialCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_IMF_RESCUER_SYS', 'user_message': 'examples.AsianFinancialCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| rescue_threshold | Rule: `-0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | imf_rescuer | IMF Rescuer | `IMFRescuer` | 1 | `examples/AsianFinancialCrisis/Rule/players.py` |
| LLM | imf_rescuer | IMF Rescuer | `LLMIMFRescuer` | 1 | `examples/AsianFinancialCrisis/LLM/players.py` |
| RuleLLM | imf_rescuer | IMF Rescuer | `RuleLLMIMFRescuer` | 1 | `examples/AsianFinancialCrisis/RuleLLM/players.py` |
| Rag | ragllm_imf_rescuer | RAG IMF Rescuer | `RagLLMIMFRescuer` | 1 | `examples/AsianFinancialCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 IMFRescuer

#### 4.3.1  Summary

IMFRescuer represents the international public-sector rescue mechanism -- the IMF and associated bilateral lenders -- that provides emergency liquidity during severe currency crises. This agent models the two defining features of IMF crisis intervention: (1) very large financial firepower ($5M initial cash, representing the scale of sovereign rescue capacity relative to private investors), and (2) a high activation threshold (-5% deviation), reflecting the IMF's documented reluctance to intervene until the crisis is well-established. The result is a "deep pockets but slow trigger" rescue pattern: prices fall significantly before intervention, but once it begins, the scale of intervention provides meaningful price support.

#### 4.3.2  Theoretical and Empirical Foundation

**IMF Conditionality and Crisis Resolution**:
- Theory / Study: IMF Conditionality and Lender of Last Resort
- Citation: Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigerstheta A model of the Asian crisis. *European Economic Review*, 43(7), 1211-1236. https://doi.org/10.1016/S0014-2921(98)00111-0
- Core Insight: IMF programs provide emergency liquidity but with conditionality (austerity, interest rate hikes) that may worsen short-term conditions. The program deployment threshold (requiring severe dislocation) creates a moral hazard and a crisis-deepening lag.
- Mathematical Formulation: `Activate when deviation(t) < -0.05; buy with 25% of cash reserves per rescue round`. The gradual deployment (25% per round) models the IMF's tranche-based disbursement structure.
- Empirical Evidence: Corsetti et al. (1999): Thailand IMF program ($17.2B) announced August 14, 1997, after baht had already depreciated ~15%; Indonesia program ($43B) November 1997 after 35% depreciation; Korea program ($58B) December 1997 after 25% won depreciation. Average activation after 15-35% depreciation -> calibrates `rescue_threshold = -0.05` as a conservative lower bound.
- Relevance to This Investor: `initial_cash = $5,000,000` and `buy_ratio = 0.25` implement the "deep pockets, gradual deployment" pattern; `rescue_threshold = -0.05` models the delayed activation documented in Corsetti et al.

**Lender of Last Resort Theory**:
- Theory / Study: International Lender of Last Resort
- Citation: Fischer, S. (1999). On the need for an international lender of last resort. *Journal of Economic Perspectives*, 13(4), 85-104. https://doi.org/10.1257/jep.13.4.85
- Core Insight: An international lender of last resort provides conditional liquidity to prevent self-fulfilling panics from destroying fundamentally sound economies. The lender's credibility depends on both its financial capacity and its willingness to deploy capital decisively. Fischer argues the IMF was the closest available institution but operated with insufficient speed and scale in 1997.
- Empirical Evidence: Fischer (1999) documents that the IMF's $17B Thailand package was insufficient to restore confidence; South Korea's $58B package (with additional bilateral commitments) was more effective because of its scale. The key lesson: lender of last resort effectiveness scales with firepower relative to the threatened market.
- Relevance to This Investor: `initial_cash = $5,000,000` (calibrated to be 6.25x larger than HotMoneyFunder's $800K, modelling sovereign vs. private capital asymmetry) provides a meaningful floor even against coordinated selling.

#### 4.3.3  Design Purpose and Activation Scenarios

Purpose: IMFRescuer provides the first floor in the crisis, activating at -5% deviation with large capital reserves. Its presence ensures the simulation has a realistic rescue mechanism that limits but does not prevent crisis depth.

Activation Scenarios:
- Pre-threshold (deviation > -0.05): Holds completely; IMF does not intervene before severe dislocation.
- Threshold crossed (deviation < -0.05): Deploys 25% of remaining cash reserves per round; provides sustained buying support.
- Recovery: Holds remaining position as passive stabiliser.

Market Contribution: **Strongly Stabilising** -- once activated, $5M in reserves at 25%/round provides meaningful buying support even against coordinated selling. However, the 5% threshold delay means crisis reaches -10% to -30% before IMF activates in many simulation runs.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**: `deviation` only -- threshold-based, consistent with IMF's public program announcement criteria.

**4.3.4.2  Core Behavioral Mechanism**: Hold until `deviation < -0.05`; then buy `buy_ratio x cash / price` each round until cash is exhausted or deviation recovers.

**4.3.4.3  Mathematical Model**

- Trigger: `deviation(t) < -rescue_threshold (-0.05)`
- Sizing: `Q*(t) = buy_ratio x cash / price(t) = 0.25 x cash / price`
- Parameter: `rescue_threshold = -0.05` (Corsetti et al., 1999); `buy_ratio = 0.25` (tranche-based disbursement)

**4.3.4.4  Behavioral Properties**

- Time horizon: Patient -- activates only after sustained crisis; deploys gradually
- Risk tolerance: Low -- risk is sovereign, not profit-motivated; willing to buy into falling market
- Psychological profile: Rule-based intervention; no fundamental valuation; pure crisis-floor provider

#### 4.3.5  Decision Process Walkthrough

```
Given:  deviation = -0.07,  cash = $5,000,000,  price = 93.0,  buy_ratio = 0.25

Step 1: Check threshold
        -0.07 < -0.05 -> rescue activated

Step 2: Compute buy quantity
        Q* = 0.25 x 5,000,000 / 93.0 = 13,440 shares

Step 3: Send order
        action = buy, quantity = 13,440, bid_price = 93.0

Result: Large buying wave; contributes lambda x 13,440 = 0.04 x 13,440 = +$537.60 upward price pressure;
        significantly counteracts selling by HotMoneyFunder and ContagionTrader.
```

#### 4.3.6  Worked Numerical Example

```
Market state (round 20, first IMF activation):  price = 92.0,  deviation = -0.08,  cash = $5,000,000

Q* = 0.25 x 5,000,000 / 92.0 = 13,587 shares
Decision: buy 13,587 shares

Round 21: cash now $3,750,000; price 93.5 (IMF buying partially arrested decline)
Q* = 0.25 x 3,750,000 / 93.5 = 10,027 shares -> continued support

Rationale: Gradual 25%/round deployment provides sustained multi-round buying pressure,
modelling the IMF's tranche disbursement structure documented by Corsetti et al. (1999).
```

#### 4.3.7  Academic References

| # | Citation                                                                                                                              | Notes                                                             |
|---|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| 1 | Corsetti, G., Pesenti, P., & Roubini, N. (1999). Paper tigerstheta *EER*, 43(7), 1211-1236. https://doi.org/10.1016/S0014-2921(98)00111-0 | Core reference; calibrates rescue_threshold = -0.05 and buy_ratio |
| 2 | Fischer, S. (1999). On the need for an international lender of last resort. *JEP*, 13(4), 85-104. https://doi.org/10.1257/jep.13.4.85 | Grounds IMF firepower asymmetry and speed-of-deployment design    |
| 3 | Radelet, S., & Sachs, J. (1998). The East Asian financial crisis. *Brookings Papers*, 1998(1), 1-90.                                  | Documents actual IMF program timelines and sizes for calibration  |

---

## Source Docstring Excerpts

### Rule / `IMFRescuer`

```text
Provides emergency liquidity packages conditional on structural reforms.

Theory: simulation-bases.md Section 4.3 -- IMFRescuer
Theoretical Basis: International lender of last resort (Corsetti et al., 1999)
Market Role: stabilizing

Strategy:
    - When deviation < rescue_threshold (severely oversold): buy buy_ratio of cash
See simulation-bases.md Section 4.3.4.3 for mathematical model.
```

### LLM / `LLMIMFRescuer`

```text
LLM-driven IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMIMFRescuer`

```text
RuleLLM IMF rescuer with explicit intervention threshold rules. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMIMFRescuer`

```text
RAG-augmented IMF rescuer -- stabilizing emergency liquidity provider. Theory: simulation-bases.md Section 4.3.
```
