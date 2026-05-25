# RumorSpread Simulation Bases

## §1 Phenomenon Definition

RumorSpread models false or weakly verified information diffusion in a social
financial environment. It is intentionally not an asset-order simulation:
participants send `social_action` messages whose payload describes whether they
spread, ignore, or correct a rumor. The central state is public belief in a
claim, accumulated distortion, correction activity, and the divergence between
belief and the ground-truth value.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Rumor research begins with the observation that ambiguous, salient information
travels through social channels faster than formal verification. Allport and
Postman's serial-transmission account describes how repeated retelling produces
leveling, sharpening, and assimilation, which map directly to the
`DistortingRelayer` and environment distortion equations.

Social-contagion and misinformation work extends this idea to large networks:
belief can rise because many peers repeat a claim, not because the claim is
true. The simulation therefore separates `truth_value` from `belief` and lets
spread actions move belief away from truth.

Correction research adds the stabilizing side of the design. Skeptical
evaluators and fact checkers do not trade assets; they emit corrective social
actions whose effect is discounted by the environment, representing the observed
lag between viral falsehoods and slower debunking.

#### §1.1.2 Real-World Event Catalogue

| Event | Period | Market / Platform | Magnitude | Correspondence |
|---|---|---|---|---|
| United Airlines bankruptcy rumor | September 2008 | Equity news wires / NASDAQ | UAUA fell more than 70% intraday before recovery | `GullibleSpreader` and `DistortingRelayer` amplify stale information; `FactChecker` represents delayed correction. |
| AP Twitter account fake White House explosion post | April 23, 2013 | US equities / social media | S&P 500 briefly lost about $136B in market value | Rapid `spread` actions raise belief before verification; correction restores state after lag. |
| Silicon Valley Bank social-media run narratives | March 2023 | Banking / venture networks | More than $40B attempted withdrawals in one day | High salience and social proof raise belief; professional correction arrives too late to fully prevent contagion. |

#### §1.1.3 Book and Practitioner Literature

| Source | Type | Relevance |
|---|---|---|
| Allport and Postman, *The Psychology of Rumor* (1947) | Book | Defines leveling, sharpening, and assimilation mechanisms used by relayers and the environment. |
| DiFonzo and Bordia, *Rumor Psychology* (2007) | Book | Motivates skeptical evaluation, active denial, and correction-lag design. |
| Vosoughi, Roy, and Aral (2018), *Science*, DOI: 10.1126/science.aap9559 | Empirical study | Documents faster diffusion of false news and motivates asymmetric spread/correction expectations. |

## §2 Theoretical Foundation

### §2.1 Rumor Transmission Under Ambiguity

**Citation and Status**: Allport and Postman (1947), foundational rumor
psychology; supported in online diffusion by Vosoughi, Roy, and Aral (2018),
DOI: 10.1126/science.aap9559.

**Mechanism**: When a claim is salient and uncertain, socially exposed agents
repeat it because repetition itself becomes evidence. In the simulation,
population belief increases with the net intensity of `spread` minus `correct`
actions.

**Formal Model**:

```text
belief(t+1) = clamp(belief(t)
    + spread_impact * (sum(spread intensity) - sum(correct intensity))
    + truth_correction * (truth_value - belief(t))
    + noise, 0, 1)
```

**Empirical Evidence**: False online news diffuses farther, faster, and more
broadly than true news in large social data (Vosoughi et al., 2018). Event
rumors in financial markets can trigger short-lived but material price or
liquidity shocks before correction.

**Relevance**: `GullibleSpreader` (§4.1) and `UninformedBystander` (§4.5)
embody unverified transmission pressure.

### §2.2 Leveling, Sharpening, And Assimilation

**Citation and Status**: Allport and Postman (1947), foundational; Bartlett's
serial-reproduction tradition motivates memory-based mutation of transmitted
content.

**Mechanism**: Repeated communication drops detail, amplifies vivid content, and
reshapes claims toward existing expectations. The simulation records this as a
bounded `distortion` state that rises with spreader count and decays through
leveling.

**Formal Model**:

```text
distortion(t+1) = clamp(
    distortion(t) - leveling_rate * distortion(t)
    + sharpening_rate * count(spread) * (1 - truth_value),
    0, 1)
```

**Empirical Evidence**: Serial reproduction studies show systematic content
loss and salience amplification; online misinformation analyses show narrative
mutation across reposts and retellings.

**Relevance**: `DistortingRelayer` (§4.2) is the direct agent embodiment, while
the environment applies the aggregate distortion equation.

### §2.3 Correction, Skepticism, And Continued Influence

**Citation and Status**: Lewandowsky et al. (2012), *Psychological Science in
the Public Interest*, DOI: 10.1177/1529100612451018; Ecker et al. (2022),
*Nature Reviews Psychology*, DOI: 10.1038/s44159-021-00006-y.

**Mechanism**: Corrections reduce belief when trusted agents identify the
belief-truth gap, but corrections often lag the original rumor and may not fully
erase residual belief. The simulation therefore discounts corrective action and
tracks correction lag.

**Formal Model**:

```text
correction_effect = sum(correct intensity)
truth_pull = truth_correction * (truth_value - belief)
```

**Empirical Evidence**: Continued-influence studies show that debunking reduces
but often does not eliminate misinformation effects. Accuracy interventions and
source warnings improve discernment but depend on attention and trust.

**Relevance**: `SkepticalEvaluator` (§4.3) and `FactChecker` (§4.4) generate
stabilizing correction pressure.

## §3 Environment Design

The coordinator is `InformationEnvironment`. It consumes special social-action
payloads, not trading orders:

```json
{
  "action_type": "spread|ignore|correct",
  "intensity": 0.0,
  "agent_role": "role name",
  "agent_id": "agent id",
  "reasoning": "optional for API variants",
  "analysis": "optional for API variants",
  "rag_context": "optional for Rag variant"
}
```

Each round follows this sequence: environment broadcasts rumor state, social
agents update personal belief and emit a `social_action`, then the environment
updates belief and distortion. The recorded state variables are `belief`,
`distortion`, `spread_count`, and `correction_count`.

## §4 Investor Taxonomy

### §4.1 GullibleSpreader

**Summary**: Highly credulous transmitter that amplifies unverified claims.
**Theoretical and Empirical Foundation**: Rumor transmission under ambiguity;
Allport and Postman (1947), Vosoughi et al. (2018).
**Design Purpose and Activation Scenarios**: Activates when personal belief
exceeds a low threshold and creates primary positive feedback.
**Behavioral Framework**: Information set is environment belief and distortion.
Personal belief moves toward public belief by `credulity`; spread intensity is
`my_belief * spread_eagerness * (1 + distortion_amplification * distortion)`.
**Decision Process Walkthrough**: Update belief, test `my_belief > 0.2`, then
emit `spread` with bounded intensity or `ignore`.
**Worked Numerical Example**: With belief `0.50`, eagerness `0.90`, distortion
`0.20`, and amplification `0.30`, intensity is `0.50 * 0.90 * 1.06 = 0.477`.
**Academic References**: Allport and Postman (1947); Vosoughi et al. (2018).

### §4.2 DistortingRelayer

**Summary**: Moderate believer that reshapes information while transmitting it.
**Theoretical and Empirical Foundation**: Leveling, sharpening, and assimilation
in serial transmission.
**Design Purpose and Activation Scenarios**: Raises both belief and distortion
when the claim is already moderately believed.
**Behavioral Framework**: Applies `sharpening_factor * distortion`, then
leveling toward rounded belief; emits `spread` when `my_belief > 0.25`.
**Decision Process Walkthrough**: Compute sharpening bias, update belief using
`credulity`, apply leveling, then relay with `my_belief * relay_eagerness`.
**Worked Numerical Example**: Belief `0.40` and relay eagerness `0.70` produce
base intensity `0.28`.
**Academic References**: Allport and Postman (1947); Bartlett-style serial
reproduction literature.

### §4.3 SkepticalEvaluator

**Summary**: Evidence-oriented participant that resists social proof.
**Theoretical and Empirical Foundation**: Correction and skepticism literature;
Lewandowsky et al. (2012), Ecker et al. (2022).
**Design Purpose and Activation Scenarios**: Provides stabilizing pressure when
personal belief remains below the correction threshold.
**Behavioral Framework**: Combines a truth pull with weak social pull:
`skepticism * (truth_value - my_belief) + (1 - skepticism) * 0.1 *
(env_belief - my_belief)`.
**Decision Process Walkthrough**: Update belief toward truth; if below
`belief_threshold`, emit `correct` with `(1 - my_belief) *
correction_eagerness`.
**Worked Numerical Example**: Belief `0.20` and correction eagerness `0.60`
produce correction intensity `0.48`.
**Academic References**: Lewandowsky et al. (2012); Ecker et al. (2022).

### §4.4 FactChecker

**Summary**: Professional verifier that actively debunks false or distorted
claims.
**Theoretical and Empirical Foundation**: Active rumor denial and misinformation
correction research.
**Design Purpose and Activation Scenarios**: Corrects when public belief is
large enough to matter, with stronger action when distortion makes errors easier
to identify.
**Behavioral Framework**: Belief moves strongly toward truth; correction
intensity equals `fact_check_strength * (1 - my_belief) * (1 +
distortion_sensitivity * distortion) * credibility_discount`.
**Decision Process Walkthrough**: If environment belief exceeds `0.3`, compute
discounted correction; otherwise ignore.
**Worked Numerical Example**: Strength `0.8`, belief `0.1`, distortion `0.5`,
sensitivity `0.5`, and discount `0.6` yield `0.54`.
**Academic References**: DiFonzo and Bordia (2007); Lewandowsky et al. (2012).

### §4.5 UninformedBystander

**Summary**: Low-engagement participant that adds background participation and
noise.
**Theoretical and Empirical Foundation**: Passive audience and minimal
engagement models.
**Design Purpose and Activation Scenarios**: Adds stochastic weak transmission
without systematic correction.
**Behavioral Framework**: Personal belief drifts weakly toward public belief.
With `engagement_probability`, the agent may spread with probability
`spread_probability`; otherwise it ignores.
**Decision Process Walkthrough**: Update belief by `0.1 * (env_belief -
my_belief)`, sample engagement, then emit weak `spread` or `ignore`.
**Worked Numerical Example**: Belief `0.25`, random spread multiplier `0.30`,
and engagement produce intensity `0.075`.
**Academic References**: Shibutani (1966); social-media participation studies.

## §5 Agent Diversity Verification

The population combines five gullible spreaders, three distorting relayers,
three skeptical evaluators, two fact checkers, and four uninformed bystanders.
This creates a deliberately asymmetric environment: destabilizing spreaders are
more numerous than professional correctors, so belief can rise before correction
pressure becomes visible.

## §6 Parameter Table

| Config Path | Value | Meaning | Source / Rationale |
|---|---:|---|---|
| `environment.extras.rumor_truth_value` | 0.1 | Ground-truth value for a mostly false claim | Synthetic low-truth rumor seed. |
| `environment.extras.initial_belief` | 0.3 | Starting public belief | Moderate seed belief before viral spread. |
| `environment.extras.spread_impact` | 0.15 | Action intensity impact on belief | Calibrated to make spread visible in 200 rounds. |
| `environment.extras.truth_correction` | 0.02 | Slow pull toward truth | Continued-influence correction lag. |
| `environment.extras.leveling_rate` | 0.01 | Distortion decay | Serial-transmission leveling. |
| `environment.extras.sharpening_rate` | 0.02 | Distortion growth per spreader | Serial-transmission sharpening. |
| `gullible_spreader.extras.credulity` | 0.8 | Fast belief adoption | High social-contagion sensitivity. |
| `distorting_relayer.extras.sharpening_factor` | 0.4 | Bias from current distortion | Narrative mutation. |
| `skeptical_evaluator.extras.skepticism` | 0.7 | Truth anchoring | Critical evaluation. |
| `fact_checker.extras.credibility_discount` | 0.6 | Correction travels slower than rumor | Misinformation correction lag. |
| `uninformed_bystander.extras.engagement_probability` | 0.3 | Occasional participation | Passive audience behavior. |

## §7 Communication And Round Structure

Round `t` begins with the environment broadcast containing belief, previous
belief, belief change, distortion, truth value, spreader count, corrector count,
and net spread intensity. Agents update personal belief and emit one
`social_action`. The environment aggregates all actions and writes the next
belief, distortion, spread-count, and correction-count histories.

## §8 Historical Cases

### §8.1 United Airlines Bankruptcy Rumor

An old bankruptcy story was redistributed as if current in September 2008,
briefly triggering a severe equity-price reaction. The case maps to
high-salience stale information, gullible retransmission, and delayed
correction.

### §8.2 AP Twitter Account Hack

A false social-media post about explosions at the White House briefly moved US
equity markets in April 2013. The case maps to fast `spread` actions, a belief
spike, and rapid but lagged professional correction.

### §8.3 Silicon Valley Bank Narrative Cascade

In March 2023, social-media and venture-network narratives accelerated belief
about bank fragility. The case maps to high social proof, distortion through
retelling, and corrective communication that could not fully offset speed.

## §9 Variant Comparison Preview

Rule encodes deterministic social-action formulas. LLM tests whether persona
reasoning alone produces coherent rumor actions. RuleLLM adds explicit decision
rules to isolate language reasoning around the same formulas. Rag extends
RuleLLM by injecting retrieved misinformation and correction context, then
records retrieval coverage through `rag_context` and `rag_stats.json`.
