# ConfirmationBias / Selective Scanner

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ConfirmationBias |
| Agent type | Selective Scanner |
| Canonical class | `SelectiveScanner` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The SelectiveScanner is an investor who selectively attends to information that supports their current market position. Unlike BeliefAnchor (who maintains an internal belief state), SelectiveScanner operates entirely on current position: it executes full-size orders when the market confirms its existing position, but only half-size orders when the market contradicts it. This asymmetric response to confirming vs. disconfirming signals is the behavioral manifestation of "selective search" -- a classic form of confirmation bias where investors seek out confirming evidence and ignore or discount contrary evidence. The SelectiveScanner is currently long (initial_position > 0), so positive deviation (price above fundamental) confirms the long and triggers full buying; negative deviation threatens the position and triggers muted selling.

## Financial Theory / Theoretical Basis

### Rule / `SelectiveScanner`
- Theory: simulation-bases.md Section 4.2 -- SelectiveScanner
- Theoretical basis: Lord, Ross & Lepper (1979) biased assimilation; filters market

### LLM / `LLMSelectiveScanner`
- LLM-driven selective scanner -- seeks confirming information, ignores contradictions. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMSelectiveScanner`
- RuleLLM-driven selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMSelectiveScanner`
- RAG-augmented selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `25.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| ignore_contradiction | Rule: `0.6` | Rule |
| initial_cash | Rule: `50000.0`<br>LLM: `50000.0`<br>RuleLLM: `50000.0`<br>Rag: `50000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ConfirmationBias.LLM.prompts:LLM_SELECTIVE_SCANNER_SYS', 'user_message': 'examples.ConfirmationBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_SELECTIVE_SCANNER_SYS', 'user_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ConfirmationBias.Rag.prompts:RAG_SELECTIVE_SCANNER_SYS', 'user_message': 'examples.ConfirmationBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `600` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| scan_threshold | Rule: `0.02` | Rule |
| search_bias | Rule: `0.7` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | selective_scanner | Selective Scanner | `SelectiveScanner` | 2 | `examples/ConfirmationBias/Rule/players.py` |
| LLM | llm_selective_scanner | LLM Selective Scanner | `LLMSelectiveScanner` | 2 | `examples/ConfirmationBias/LLM/players.py` |
| RuleLLM | rulellm_selective_scanner | RuleLLM Selective Scanner | `RuleLLMSelectiveScanner` | 2 | `examples/ConfirmationBias/RuleLLM/players.py` |
| Rag | ragllm_selective_scanner | RAG Selective Scanner | `RagLLMSelectiveScanner` | 2 | `examples/ConfirmationBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 SelectiveScanner

#### 4.2.1  Summary

The SelectiveScanner is an investor who selectively attends to information that supports their current market position. Unlike BeliefAnchor (who maintains an internal belief state), SelectiveScanner operates entirely on current position: it executes full-size orders when the market confirms its existing position, but only half-size orders when the market contradicts it. This asymmetric response to confirming vs. disconfirming signals is the behavioral manifestation of "selective search" -- a classic form of confirmation bias where investors seek out confirming evidence and ignore or discount contrary evidence. The SelectiveScanner is currently long (initial_position > 0), so positive deviation (price above fundamental) confirms the long and triggers full buying; negative deviation threatens the position and triggers muted selling.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Selective Search and Myside Bias**
- Theory / Study: Selective information search as confirmation bias mechanism
- Citation: Nickerson, R. S. (1998). DOI: 10.1037/1089-2680.2.2.175. Also: Klayman, J. (1995). "Varieties of confirmation bias." *Psychology of Learning and Motivation*, 32, 385-418.
- Core Insight: The "myside bias" (Stanovich, West & Toplak, 2013) is the tendency to evaluate evidence based on one's own side of an argument rather than objective standards. Investors with myside bias respond asymmetrically to market signals: they act quickly and decisively on confirming signals but hesitate, rationalize, and discount disconfirming signals. SelectiveScanner's asymmetric order sizing (600 confirming, 300 disconfirming) is a direct quantitative implementation.
- Mathematical Formulation: Asymmetric response: Q_confirming = order_size = 600; Q_disconfirming = order_size / 2 = 300. The 2:1 response ratio (600:300) is calibrated to the 2x asymmetry documented in experimental psychology studies of myside bias. Signal interpretation: confirming if sign(deviation) = sign(current position direction); disconfirming otherwise.
- Empirical Evidence: Klayman (1995) documents that selective search creates information asymmetry in processing: confirmation bias subjects generate 2-3x more confirming tests than disconfirming tests when evaluating hypotheses. Mapped to trading: 2x larger orders on confirming signals (600 vs. 300) is within the empirically documented range.
- Relevance to This Investor: scan_threshold = 0.02 (2%) is the minimum deviation needed to trigger any response; asymmetric sizing (600 vs. 300) directly implements the myside bias; the position-direction conditioning (acts based on current position sign) implements the "selective search for confirming evidence."

**Theory 2: Commitment and Consistency (Cialdini)**
- Theory / Study: Post-commitment rationalization of prior investment decisions
- Citation: Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Collins. Also: Staw, B. M. (1976). "Knee-deep in the Big Muddy: A study of escalating commitment to a chosen course of action." *Organizational Behavior and Human Performance*, 16(1), 27-44. DOI: 10.1016/0030-5073(76)90005-2
- Core Insight: Once an investor has committed to a position, psychological consistency pressure creates a bias toward maintaining and expanding the position. Staw (1976)'s escalating commitment research shows that decision-makers who already have committed resources to a course of action will continue to commit additional resources even when objective evidence suggests failure. In investing, this is the "throwing good money after bad" bias -- continuing to buy a losing position because selling would acknowledge the original decision was wrong.
- Mathematical Formulation: SelectiveScanner's asymmetric behavior when position is long: buy at deviation > +0.02 (confirming position = full 600 shares); sell at deviation < -0.02 (threatening position = only 300 shares). This asymmetric reluctance to sell at disconfirming signals models escalating commitment.
- Relevance to This Investor: The position-conditional asymmetry (full response to confirming, half to disconfirming) embeds the commitment-and-consistency bias directly in the decision rule.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the selective information search variant of confirmation bias -- where the bias manifests not as belief compounding but as systematically asymmetric trading action in response to signals. Complements BeliefAnchor's belief-state mechanism with a position-based mechanism.

**Activation Scenarios**:
- Scenario A (Market confirms current long position, deviation > +0.02): Full buy (600 shares). Maximum response to confirming signal.
- Scenario B (Market challenges current long position, deviation < -0.02): Half sell (300 shares). Muted response to disconfirming signal -- reluctance to acknowledge the position is threatened.
- Scenario C (Signal below threshold, |deviation| <= 0.02): Hold. No action on weak signals.

**Market Contribution**: Destabilizing -- the 2:1 buy/sell asymmetry creates net upward pressure over time (when buy signals and sell signals are equally frequent, SelectiveScanner generates 600 net buy vs. 300 net sell units in those rounds, producing a net positive contribution to D(t)).

**Interaction with other agents**: Reinforces BeliefAnchor buying (both buying on positive deviation); BalancedAnalyst and ContrarianTrader oppose both.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Both trigger and direction signal -- but applied asymmetrically based on current position.
- `position`: Key state variable -- determines whether deviation is "confirming" (sign aligns with position direction) or "disconfirming."

**4.2.4.2  Core Behavioral Mechanism**
1. Observe `deviation`.
2. If deviation > scan_threshold (+0.02) AND position >= 0 (currently long or flat): buy = confirming signal for long -> full order_size = 600.
3. If deviation < -scan_threshold (-0.02) AND position >= 0 (currently long): sell = disconfirming signal -> half order_size = 300.
4. Hold if |deviation| <= 0.02.
5. Note: If position < 0 (short): the asymmetry reverses -- negative deviation confirms short (full 600), positive threatens short (half 300).

**4.2.4.3  Mathematical Model**
- Trigger: buy if δ(t) > +scan_threshold; sell if δ(t) < -scan_threshold; hold if |δ| <= scan_threshold
- Asymmetric sizing: Q*_confirming = order_size = 600; Q*_disconfirming = order_size / 2 = 300
- Confirming condition: sign(δ(t)) = sign(position) -> full size; else -> half size
- State variables: position, cash

| Parameter      | Value | Meaning                                         | Config Path                                             | Source                                                                  |
|----------------|-------|-------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------|
| scan_threshold | 0.02  | Minimum deviation to trigger selective scanning | `ConfirmationBias/Rule/config.yaml -> selective_scanner` | Klayman (1995)                                                          |
| order_size     | 600   | Full order size for confirming signals          | `ConfirmationBias/Rule/config.yaml -> selective_scanner` | Normalization (larger than BeliefAnchor to provide second bias channel) |

**4.2.4.4  Behavioral Properties**
- Time horizon: Short-to-medium term -- responds to each round's deviation signal; no long-run belief state
- Risk tolerance: Asymmetric -- high tolerance for losses on existing position (slow to sell); normal response to opportunities to add
- Information asymmetry: None
- Psychological profile: Position-defensive, myside-biased, reluctant to acknowledge mistakes. In LLM variants, the persona should emphasize "I'm reluctant to exit a position just because of short-term noise."

#### 4.2.5  Decision Process Walkthrough

Given: deviation = +0.04, position = 800 (long), scan_threshold = 0.02, order_size = 600

Step 1: deviation = +0.04 > +0.02 -> scanning active (buy signal).
Step 2: position = 800 >= 0 -> confirming signal for long position -> full order.
Step 3: Q = 600 shares.
Step 4: Order: action=buy, quantity=600, bid_price=current_price.

Given: deviation = -0.03, position = 800 (long), scan_threshold = 0.02

Step 1: deviation = -0.03 < -0.02 -> scanning active (sell signal).
Step 2: position = 800 >= 0 -> disconfirming signal for long position -> half order.
Step 3: Q = 300 shares.
Step 4: Order: action=sell, quantity=300, bid_price=current_price.

#### 4.2.6  Worked Numerical Example

Market state: price = 103.0, deviation = +0.03, position = 1200

Confirming buy: Q = 600. Order: buy 600. Rationale: Market confirming SelectiveScanner's long position -> maximum response. Contrast: if position = -200 (short) at same deviation = +0.03, it would be disconfirming -> sell only 300.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                           | Notes                                                           |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 1 | Nickerson, R. S. (1998). "Confirmation bias." *Review of General Psychology*, 2(2), 175-220. DOI: 10.1037/1089-2680.2.2.175                        | scan_threshold calibration; myside bias as confirmation variant |
| 2 | Klayman, J. (1995). "Varieties of confirmation bias." *Psychology of Learning and Motivation*, 32, 385-418.                                        | Selective search mechanism; 2:1 confirming/disconfirming ratio  |
| 3 | Staw, B. M. (1976). "Knee-deep in the Big Muddy." *Organizational Behavior and Human Performance*, 16(1), 27-44. DOI: 10.1016/0030-5073(76)90005-2 | Escalating commitment; asymmetric sell reluctance               |


---

## Source Docstring Excerpts

### Rule / `SelectiveScanner`

```text
Seeks information supporting current position, ignores contradictions.

Theory: simulation-bases.md Section 4.2 -- SelectiveScanner
Theoretical basis: Lord, Ross & Lepper (1979) biased assimilation; filters market
signals to amplify current position direction, reinforcing mispricing.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMSelectiveScanner`

```text
LLM-driven selective scanner -- seeks confirming information, ignores contradictions. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMSelectiveScanner`

```text
RuleLLM-driven selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMSelectiveScanner`

```text
RAG-augmented selective scanner -- seeks confirming info, ignores contradictions. Theory: simulation-bases.md Section 4.2.
```
