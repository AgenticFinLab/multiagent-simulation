# RumorSpread Simulation Bases

## §1 Phenomenon Definition

RumorSpread models social information diffusion rather than ordinary trading.
Unverified claims spread through gullible, distorting, skeptical, corrective,
and low-engagement participants. The key output is belief distortion and spread
dynamics, not buy/sell order flow.

## §2 Theoretical Foundation

### §2.1 Rumor Transmission

Rumors propagate when uncertainty and salience are high. Transmission can
increase belief even without truth.

### §2.2 Leveling And Sharpening

As claims are relayed, details can be dropped (leveling) and salient elements
exaggerated (sharpening).

### §2.3 Correction And Skepticism

Fact checking and skeptical evaluation can slow or reverse belief in false
claims, but corrections may lag spread.

## §3 Market Mechanism

The InformationEnvironment tracks belief, distortion, truth correction, and
rumor intensity. Agents send information actions such as spread, distort,
correct, evaluate, or ignore. This is a scenario-specific schema and should not
be forced into the canonical trading order format.

## §4 Investor Archetypes

### §4.1 InformationEnvironment

**Summary**: Central environment tracking rumor belief and distortion.
**Theoretical and Empirical Basis**: Information diffusion models.
**Design Purpose**: Maintain global rumor state.
**Behavioral Framework**: Uses `initial_belief`, `spread_impact`,
`leveling_rate`, `sharpening_rate`, `truth_correction`, and `noise_std`.
**Decision Process**: Aggregates inbound information actions and updates belief.
**Worked Numerical Example**: More spread actions increase belief; corrections
reduce it.
**Academic References**: Allport and Postman (1947); rumor diffusion studies.

### §4.2 GullibleSpreader

**Summary**: Believes and amplifies unverified claims.
**Theoretical and Empirical Basis**: Credulity and social contagion.
**Design Purpose**: Generate rapid rumor spread.
**Behavioral Framework**: Uses `credulity`, `spread_eagerness`, and
`distortion_amplification`.
**Decision Process**: Spread when belief exceeds personal skepticism threshold.
**Worked Numerical Example**: High credulity converts moderate rumor belief into
a strong spread action.
**Academic References**: Social contagion literature.

### §4.3 DistortingRelayer

**Summary**: Relays claims while introducing systematic distortion.
**Theoretical and Empirical Basis**: Leveling and sharpening.
**Design Purpose**: Increase rumor mutation.
**Behavioral Framework**: Uses `leveling_factor`, `sharpening_factor`,
`credulity`, and `relay_eagerness`.
**Decision Process**: Relay with distortion when engagement is high.
**Worked Numerical Example**: A claim is shortened and its most salient element
is amplified.
**Academic References**: Allport and Postman (1947).

### §4.4 SkepticalEvaluator

**Summary**: Evaluates claims before accepting or spreading.
**Theoretical and Empirical Basis**: Skepticism and critical reasoning.
**Design Purpose**: Slow rumor spread.
**Behavioral Framework**: Uses `skepticism`, `belief_threshold`, and
`correction_eagerness`.
**Decision Process**: Correct or refuse to spread when evidence is weak.
**Worked Numerical Example**: A high-skepticism agent sends correction instead
of spread.
**Academic References**: Misinformation correction research.

### §4.5 FactChecker

**Summary**: Investigates claims and broadcasts corrections.
**Theoretical and Empirical Basis**: Fact-checking and debunking.
**Design Purpose**: Provide truth-directed counterforce.
**Behavioral Framework**: Uses `fact_check_strength`,
`credibility_discount`, and `distortion_sensitivity`.
**Decision Process**: Correct false or distorted claims when distortion is high.
**Worked Numerical Example**: High distortion triggers a correction action.
**Academic References**: Misinformation correction literature.

### §4.6 UninformedBystander

**Summary**: Low-engagement participant with random participation.
**Theoretical and Empirical Basis**: Passive audience behavior.
**Design Purpose**: Add realistic low-intensity noise.
**Behavioral Framework**: Uses `engagement_probability` and
`spread_probability`.
**Decision Process**: Usually ignore; sometimes spread randomly.
**Worked Numerical Example**: A low-probability engagement draw produces a weak
spread.
**Academic References**: Information diffusion and social media participation
studies.

## §5 Agent Diversity Verification

The population includes amplifiers, mutators, skeptics, correctors, passive
bystanders, and an environment state keeper.

## §6 Parameter Table

| Parameter | Meaning | Used By | Sensitivity |
|---|---|---|---|
| `spread_impact` | Belief increase per spread action | InformationEnvironment | High |
| `truth_correction` | Correction strength | InformationEnvironment/FactChecker | High |
| `credulity` | Acceptance tendency | Spreaders/Relayers | High |
| `leveling_factor` | Detail loss | DistortingRelayer | Medium |
| `sharpening_factor` | Salience exaggeration | DistortingRelayer | Medium |
| `skepticism` | Resistance to belief | SkepticalEvaluator | High |

## §7 Communication And Round Structure

Environment broadcasts rumor state; agents decide whether to spread, distort,
correct, evaluate, or ignore; environment updates belief and distortion.

## §8 Historical Case Studies

### §8.1 Financial Market Rumors

Bank solvency, takeover, and regulatory rumors can spread rapidly and affect
belief before verification.

### §8.2 Social Media Misinformation

Online misinformation often exhibits rapid initial spread followed by delayed
correction.

## §9 Variant Comparison Preview

Rule uses explicit diffusion rules. LLM may generate richer rumor narratives.
RuleLLM uses explicit action schema with reasoning. Rag may retrieve correction
or historical misinformation context.
