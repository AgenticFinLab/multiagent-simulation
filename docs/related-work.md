# Related Work: LLM-Based Society and Financial Simulation

> **Research Domain**: Simulation of Society — social behaviors, financial market dynamics, economic events, emergent phenomena (panics, bubbles, contagion), information diffusion, opinion dynamics, cultural evolution, institutional behavior, policy impact  
> **Methodology/Tools**: Large Language Models (LLMs), LLM-based multi-agent systems, agent-based modeling (ABM) — these are the MEANS, not the END  
> **Research Target**: Repeat and Duplicate society events, finance behaviors, etc. directly to match the features of the real society  
> **Comparison Dimensions**: Simulation fidelity, scale, validation methodology, phenomena reproduced, grounding in real data, emergence quality

---

## Table of Contents

1. [Foundational: Believable Human Behavior Simulation](#1-foundational-believable-human-behavior-simulation)
2. [Community and Urban Simulation](#2-community-and-urban-simulation)
3. [Social Network and Information Diffusion](#3-social-network-and-information-diffusion)
4. [Opinion Dynamics and Polarization](#4-opinion-dynamics-and-polarization)
5. [Emergent Social Norms and Conventions](#5-emergent-social-norms-and-conventions)
6. [Cooperation, Trust, and Social Dilemmas](#6-cooperation-trust-and-social-dilemmas)
7. [Elections and Political Behavior Simulation](#7-elections-and-political-behavior-simulation)
8. [Financial Market Simulation](#8-financial-market-simulation)
9. [Consumer and Economic Behavior Simulation](#9-consumer-and-economic-behavior-simulation)
10. [Epidemic and Public Health Simulation](#10-epidemic-and-public-health-simulation)
11. [Disaster Response and Policy Simulation](#11-disaster-response-and-policy-simulation)
12. [Crime and Safety Simulation](#12-crime-and-safety-simulation)
13. [Cultural and Moral Evolution Simulation](#13-cultural-and-moral-evolution-simulation)
14. [Game-Theoretic and Strategic Interaction Simulation](#14-game-theoretic-and-strategic-interaction-simulation)
15. [Emergent Extreme Events in Multi-Agent Systems](#15-emergent-extreme-events-in-multi-agent-systems)
16. [Surveys and Position Papers](#16-surveys-and-position-papers)
17. [Synthesis: Landscape and Open Challenges](#17-synthesis-landscape-and-open-challenges)

---

## 1. Foundational: Believable Human Behavior Simulation

### 1.1 Generative Agents: Interactive Simulacra of Human Behavior (UIST 2023)

**[CAT: Foundational] [REL: Critical]**

**Paper**: "Generative Agents: Interactive Simulacra of Human Behavior"
**Link**: https://arxiv.org/abs/2304.03442
**Code**: https://github.com/joonspk-research/generative_agents

#### Summary
This landmark paper introduces generative agents — computational software agents that simulate believable human behavior using LLMs. Each agent maintains a comprehensive memory stream, retrieves relevant memories via recency/importance/relevance scoring, and reflects on observations to generate higher-level summaries. Twenty-five agents inhabit a virtual town (Smallville), producing emergent social behaviors including coordination, relationship formation, and information diffusion — the first demonstration that LLM-based agents can produce believable individual and social behaviors at community scale.

#### Core Motivation
Prior agent-based models relied on hand-crafted rules producing mechanical, stereotyped behavior. Rule-based agents cannot generalize to novel situations or exhibit nuanced decision-making. The authors asked: can we leverage the vast social knowledge encoded in LLMs to create agents that behave believably in open-ended social settings, without hand-coding every behavior?

#### Core Idea
```
LLM as "Brain" + Memory Architecture = Believable Agent

Traditional ABM:  Rules → Mechanical Behavior
Generative Agent:  Memory + Retrieval + Reflection + LLM → Believable Behavior
```

#### Core Method
```
┌──────────────────────────────────────────────────────────────┐
│                   Generative Agent Architecture              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Memory Stream: [obs_1, obs_2, ..., obs_n] (timestamped)   │
│    Each scored by: Recency (exp decay), Importance (LLM),   │
│                    Relevance (embedding similarity)           │
│         ↓                                                    │
│  Retrieval: Score = α·Recency + β·Importance + γ·Relevance  │
│         ↓                                                    │
│  Reflection: Periodically synthesize into higher-level       │
│    insights: "I am a scholarly person who values learning"   │
│         ↓                                                    │
│  Planning: Generate daily schedule → Replan as needed        │
│         ↓                                                    │
│  Action: Execute in environment → New observation            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

#### Example
```
Agent "John" at cafe overhears about an upcoming election:

Step 1 - Observation: "Sam is discussing the election at the cafe"
Step 2 - Memory Storage: Add to stream (importance: 5/10)
Step 3 - Retrieval: Sam's election discussion + John's prior interest in politics
Step 4 - Reflection: "I care about local politics and discuss it with Sam"
Step 5 - Action: John approaches Sam and engages in election discussion

→ Emergent behavior: Information about election spreads through social network
```

#### Relationship to Our Work

| Aspect         | Generative Agents               | Our Research Target                   |
|----------------|---------------------------------|---------------------------------------|
| Scale          | 25 agents in a small town       | Large-scale society simulation        |
| Memory         | Stream-based with retrieval     | May need scalable memory              |
| Validation     | Qualitative observation         | Quantitative matching of real society |
| Social Network | Implicit (physical proximity)   | Explicit network modeling needed      |
| Key Gap        | No validation against real data | Must match real societal features     |

---

### 1.2 Generative Agent Simulations of 1,000 People (2024)

**[CAT: Foundational] [REL: Critical]**

**Paper**: "Generative Agent Simulations of 1,000 People"
**Link**: https://arxiv.org/abs/2411.10109
**Code**: Null

#### Summary
Scales generative agents to simulate 1,052 real individuals by grounding each agent in a two-hour qualitative interview. Agent attitudes and behaviors validated against actual interviewees' responses, achieving 85% correlation on the General Social Survey (GSS) — comparable to human retest reliability. Published in Nature, this provides the first large-scale evidence that LLM-based agents can faithfully reproduce individual-level human attitudes and social behaviors at population scale.

#### Core Motivation
The original Generative Agents showed believable behavior but did not validate whether agents match specific real people's attitudes. Social science needs simulations that are empirically accurate, not just "believable" — do simulated agents think and act like their real-world counterparts?

#### Core Idea
```
Real Person Interview (2 hours) → Agent Persona → Simulated Behavior ≈ Real Behavior
Validation: Agent responses vs. Real survey responses (GSS)
Result: 85% correlation (comparable to human retest reliability ≈ 80-88%)
```

#### Core Method
```
Phase 1: 1,052 real people → 2-hour interviews each
Phase 2: Interview transcript → Persona description (demographics + beliefs + personality)
Phase 3: Present GSS questions to agents → Agent generates response using persona + LLM
Phase 4: Compare agent responses to actual GSS responses → 85% correlation
```

#### Example
```
Real Person: "I'm a 45-year-old teacher from Ohio. I vote Democrat."
GSS Question: "Should government reduce income differences?"
Agent Response: "Yes, I believe government has a role in fairness." → Match ✓
Validation across 1,052 individuals: 85% of responses match
```

#### Relationship to Our Work

| Aspect      | 1000-Person Sim                              | Our Research Target                  |
|-------------|----------------------------------------------|--------------------------------------|
| Grounding   | Interview transcripts                        | Financial/survey data needed         |
| Validation  | GSS survey comparison                        | Financial behavior validation needed |
| Domain      | Social attitudes                             | Finance and market behavior          |
| Key Advance | Proves LLM agents can match real individuals | Must extend to economic decisions    |

---

### 1.3 On the Limits of Agency in Agent-Based Models (AAMAS 2025)

**[CAT: Foundational] [REL: High]**

**Paper**: "On the Limits of Agency in Agent-Based Models"
**Authors**: Ayush Chopra, Shashank Kumar, Nurullah Giray-Kuru, Ramesh Raskar, Arnau Quera-Bofarull (MIT Media Lab)
**Venue**: AAMAS 2025
**Link**: https://arxiv.org/abs/2409.10568
**Code**: Null

#### Summary
Examines the fundamental limitations of LLM-based agents in agent-based modeling, arguing that current LLM agents lack true agency — the capacity for autonomous goal-setting, counterfactual reasoning, and genuine intentionality. Identifies key gaps between simulated agent behavior and real human agency, including the absence of embodied experience, intrinsic motivation, and the ability to form novel goals beyond training distribution. Proposes a framework for understanding when LLM agents are sufficient vs. when their agency limitations undermine simulation validity.

#### Core Motivation
LLM-based agents are increasingly used to simulate human behavior, but they operate within the constraints of their training data and prompting mechanisms. They lack genuine agency — the ability to set their own goals, reason about truly novel situations, and act from intrinsic motivation. Understanding these limits is critical for determining when LLM-based simulation produces valid results and when it systematically diverges from real human behavior.

#### Core Idea
```
LLM Agent Agency Limitations:
  SUFFICIENT:   Routine social behavior, pattern reproduction, opinion expression
  LIMITED:      Strategic planning, creative problem-solving, norm innovation
  INSUFFICIENT: Genuine goal-setting, counterfactual reasoning, embodied decisions

Rule: LLM agents simulate behavioral OUTPUTS but not the underlying AGENCY
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Agency Limitation Framework                       │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Level 1 — Behavioral Mimicry (Adequate):                 │
│    LLM reproduces surface-level behavioral patterns       │
│    Example: Agent expresses opinions like a real person   │
│                                                           │
│  Level 2 — Strategic Reasoning (Limited):                 │
│    LLM can plan within known scenarios but fails on novel │
│    Example: Agent trades stocks but cannot invent new     │
│             financial instruments                          │
│                                                           │
│  Level 3 — True Agency (Insufficient):                    │
│    LLM cannot set own goals or reason counterfactually    │
│    Example: Agent cannot decide to leave the market       │
│             for philosophical reasons                     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Market crash scenario:
  Human trader: "I'm quitting the market — this system is broken" (genuine agency)
  LLM agent: "I should sell more" (pattern-matched response from training data)
  → LLM agent cannot truly "opt out" or invent new market behaviors
  → Simulation may miss critical real-world responses to crises
```

#### Relationship to Our Work

| Aspect        | Agency Limits Framework             | Our Research Target                   |
|---------------|-------------------------------------|---------------------------------------|
| Scope         | Identifies LLM agent limitations    | Must design around these limitations  |
| Financial Sim | Agents may lack true market agency  | Need to validate against real traders |
| Validation    | Framework for when LLM sim is valid | Apply to determine valid use cases    |
| Key Insight   | Behavioral outputs ≠ true agency    | Must distinguish mimicry from genuine |

---

### 1.4 Out of One, Many: Using Language Models to Simulate Human Samples (Political Analysis 2023)

**[CAT: Foundational] [REL: High]**

**Paper**: "Out of One, Many: Using Language Models to Simulate Human Samples"
**Authors**: Lisa P. Argyle, Ethan C. Busby, Nancy Fulda, Joshua Gubler, David Wingate (BYU)
**Venue**: Political Analysis 31(3):337-351 (2023)
**Link**: https://arxiv.org/abs/2209.06899
**Code**: Null

#### Summary
Proposes using a single LLM to simulate a diverse sample of human respondents by generating multiple synthetic personas and having the model respond from each persona's perspective. Demonstrates that LLM-generated survey responses from simulated diverse populations can approximate the distribution of real human survey responses, providing a scalable method for pilot studies, survey design, and hypothesis generation before conducting expensive human subject research.

#### Core Motivation
Human subject studies are expensive, time-consuming, and subject to IRB constraints. If LLMs can approximate the distribution of human responses to surveys and scenarios, researchers can use LLM simulation for preliminary studies, survey design optimization, and hypothesis screening before committing resources to real human studies.

#### Core Idea
```
Single LLM + Multiple Personas = Simulated Human Sample

Traditional: Recruit 500 people → Survey → Analyze distribution
Silicon Sampling: Generate 500 personas → LLM responds as each → Analyze distribution
Result: Simulated distributions approximate real human response distributions
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Silicon Sampling Pipeline                          │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Step 1: Define target population demographics            │
│    → Generate N diverse persona descriptions              │
│                                                           │
│  Step 2: For each persona:                                │
│    → LLM responds to survey from persona's perspective    │
│    → Collect response + confidence score                   │
│                                                           │
│  Step 3: Aggregate responses across personas              │
│    → Compare distribution to real human survey data       │
│    → Assess approximation quality                         │
│                                                           │
│  Key Finding: Distributions match on aggregate but        │
│  miss tails and extreme responses                         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Political survey simulation:
  Generate 1,000 personas matching US census demographics
  Ask: "Do you support increased government spending?"
  LLM simulated: 52% support, 38% oppose, 10% unsure
  Real survey:   54% support, 36% oppose, 10% unsure
  → Close match on central tendencies, weaker on extremes
```

#### Relationship to Our Work

| Aspect      | Silicon Sampling                 | Our Research Target                     |
|-------------|----------------------------------|-----------------------------------------|
| Method      | LLM simulates population sample  | LLM agents simulate market participants |
| Validation  | Distribution matching            | Need behavioral + distribution matching |
| Scale       | 1,000 personas from single LLM   | Similar approach for investor personas  |
| Limitation  | Misses tail events and extremes  | Critical for financial crash simulation |
| Key Insight | Single LLM can produce diversity | Applicable to diverse investor modeling |

---

### 1.5 This Human Study Did Not Involve Human Subjects: Validating LLM Simulations as Behavioral Evidence (2026)

**[CAT: Foundational] [REL: High]**

**Paper**: "This Human Study Did Not Involve Human Subjects: Validating LLM Simulations as Behavioral Evidence"
**Authors**: Jessica Hullman, Danica Broska, Huaman Sun, Alex Shaw
**Link**: https://arxiv.org/abs/2602.15785
**Code**: Null

#### Summary
Systematically evaluates whether LLM simulations can serve as valid behavioral evidence by comparing LLM-generated experimental results against known human behavioral patterns from psychology and economics. Tests classic behavioral experiments (ultimatum game, prisoner's dilemma, anchoring effects) with LLM subjects, finding that LLMs reproduce many known behavioral biases but with important differences in magnitude and distribution. Establishes criteria for when LLM simulations can legitimately substitute for human subjects in behavioral research.

#### Core Motivation
If LLMs can faithfully reproduce known human behavioral patterns in controlled experiments, they could serve as a low-cost, high-throughput alternative for preliminary behavioral research. But validation against established human behavioral evidence is needed before LLM simulations can be trusted as behavioral evidence.

#### Core Idea
```
Classic Behavioral Experiments + LLM Subjects = Validation Framework

Test: Do LLMs show the same biases as humans?
  Anchoring effect:   LLM shows it ✓ (but weaker magnitude)
  Loss aversion:      LLM shows it ✓ (but different distribution)
  Framing effect:     LLM shows it ✓ (comparable magnitude)
  Ultimate question:  When is "close enough" good enough?
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          LLM Behavioral Validation Pipeline               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Step 1: Select established behavioral experiments        │
│    with known human results (replication benchmarks)      │
│                                                           │
│  Step 2: Run same experiments with LLM subjects           │
│    Multiple personas, multiple trials, controlled prompts │
│                                                           │
│  Step 3: Compare LLM results to human results             │
│    Effect sizes, distributions, statistical significance  │
│                                                           │
│  Step 4: Establish validity criteria                      │
│    When does LLM ≈ Human? When does LLM ≠ Human?         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Ultimatum game experiment:
  Human results: Proposers offer ~40%, responders reject <20%
  LLM results:   Proposers offer ~45%, responders reject <25%
  → Similar pattern but LLM is "more fair" (higher offers)
  → Suggests LLM has social desirability bias in economic games
```

#### Relationship to Our Work

| Aspect      | LLM Behavioral Validation             | Our Research Target                    |
|-------------|---------------------------------------|----------------------------------------|
| Domain      | Classic behavioral experiments        | Financial behavioral experiments       |
| Validation  | Known human behavioral benchmarks     | Real market behavior benchmarks        |
| Finding     | LLMs show biases but differ in degree | Must calibrate financial agent biases  |
| Key Insight | Validation criteria needed per domain | Need financial-domain validation first |

---

### 1.6 Centaur: A Foundation Model of Human Cognition (Nature 2025)

**[CAT: Foundational] [REL: Medium]**

**Paper**: "Centaur: A Foundation Model of Human Cognition"
**Authors**: Marcel Binz, Elif Akata, et al. (Helmholtz Munich)
**Venue**: Nature (2025)
**Link**: https://arxiv.org/abs/2410.20268
**Code**: Null

#### Summary
Introduces Centaur, a foundation model specifically designed to capture human cognitive processes including decision-making under uncertainty, learning, memory, and reasoning biases. Unlike general-purpose LLMs that simulate behavioral outputs, Centaur models the underlying cognitive mechanisms — how humans actually think, learn, and make decisions — providing a computational framework for simulating realistic cognitive processes. Demonstrates strong performance on cognitive psychology benchmarks including decision-making tasks, probability judgment, and reasoning under uncertainty.

#### Core Motivation
General-purpose LLMs produce human-like text but do not explicitly model cognitive processes like learning from feedback, belief updating under uncertainty, or cognitive bias mechanisms. A foundation model of cognition that captures these processes can produce more psychologically realistic agent behavior for simulation.

#### Core Idea
```
General LLM:    Language patterns → Behavioral output (surface-level)
Cognitive Model: Cognitive processes → Behavioral output (mechanism-level)

Centaur models:
  - Decision-making under uncertainty
  - Learning from feedback (reinforcement learning signals)
  - Memory formation and retrieval (cognitive architecture)
  - Reasoning biases (anchoring, availability, representativeness)
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│              Centaur Cognitive Architecture                 │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Perception: Environment observation → Cognitive encoding  │
│       ↓                                                   │
│  Memory: Working memory + Long-term memory + Episodic     │
│       ↓                                                   │
│  Reasoning: Probabilistic inference + Heuristic shortcuts  │
│       ↓                                                   │
│  Decision: Utility evaluation + Risk preferences           │
│       ↓                                                   │
│  Learning: Feedback → Belief update → Strategy adaptation  │
│                                                           │
│  Key: Models COGNITIVE PROCESSES, not just outputs        │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Investment decision under uncertainty:
  Centaur agent: Encodes market signal → Updates belief via Bayesian reasoning
    → Applies loss aversion heuristic → Decides to hold (not sell at loss)
  → Cognitive process matches real investor decision mechanism
  → More realistic than LLM text-based reasoning about trading
```

#### Relationship to Our Work

| Aspect         | Centaur                             | Our Research Target                         |
|----------------|-------------------------------------|---------------------------------------------|
| Approach       | Cognitive process modeling          | Need cognitive architecture for agents      |
| Decision Model | Mechanism-level (how humans think)  | Applicable to investor decision-making      |
| Validation     | Cognitive psychology benchmarks     | Financial psychology validation needed      |
| Key Advance    | Models cognition, not just behavior | Foundation for cognitively-realistic agents |

---

## 2. Community and Urban Simulation

### 2.1 AgentSociety: Large-Scale LLM-Driven Social Simulation (2025)

**[CAT: Social Simulation] [REL: High]**

**Paper**: "AgentSociety: Large-Scale Simulation of LLM-Driven Generative Agents Advances Understanding of Human Behaviors and Society"
**Link**: https://arxiv.org/abs/2502.08691
**Code**: https://github.com/tsinghua-fib-lab/agentsociety

#### Summary
AgentSociety is a large-scale social simulator integrating LLM-driven agents with a realistic societal environment and social network. It supports thousands of agents in urban environments with explicit spatial and social structures, providing tools for agent creation, social network definition, simulation execution, and emergent behavior analysis across four social domains: disaster response, epidemic spread, economic activity, and social influence.

#### Core Motivation
Existing LLM social simulations are small-scale (25-100 agents) and lack realistic environmental structures. Real societies feature complex spatial layouts, economic systems, social networks, and institutions that shape individual behavior. A scalable, comprehensive platform is needed.

#### Core Idea
```
LLM Agents + Realistic Environment + Social Network = Large-Scale Society Simulation

AgentSociety integrates:
  - Spatial map (buildings, roads)
  - Economic system (jobs, transactions)
  - Social network (friendship, information)
  - Event system (disasters, policies)
```

#### Core Method
```
┌──────────────────────────────────────────────────────────┐
│              AgentSociety Architecture                    │
├──────────────────────────────────────────────────────────┤
│  Agent Layer: 1000+ LLM agents with memory and persona   │
│       ↓                                                  │
│  Environment Layer: Spatial Map + Economy + Events        │
│       ↓                                                  │
│  Social Network Layer: Friendship + Info Flow + Trust     │
│       ↓                                                  │
│  Analysis Layer: Emergent behaviors, statistics           │
│  Validated on: Disaster response, epidemics, economics   │
└──────────────────────────────────────────────────────────┘
```

#### Example
```
Scenario: Earthquake hits downtown area
- Resident agents seek shelter, share info on social network
- Medical agents head to affected areas
- Government agents coordinate relief
→ Emergent: Information cascades, resource competition, self-organized rescue
```

#### Relationship to Our Work

| Aspect      | AgentSociety             | Our Research Target             |
|-------------|--------------------------|---------------------------------|
| Scale       | 1000+ agents             | Similar scale needed            |
| Environment | Urban physical           | Financial market environment    |
| Domains     | Disaster/epidemic/social | Financial crisis scenarios      |
| Key Feature | Integrated platform      | Finance-specific modules needed |

---

### 2.2 SocioVerse: A World Model for Social Simulation (2025)

**[CAT: Social Simulation] [REL: High]**

**Paper**: "SocioVerse: A World Model for Social Simulation Powered by LLM Agents"
**Link**: https://arxiv.org/abs/2504.10157
**Code**: Null

#### Summary
SocioVerse introduces an LLM-agent-driven world model with four alignment components: environment alignment, user alignment, interaction alignment, and rule alignment. With a user pool of 10 million real users, it simulates large-scale population dynamics while ensuring diversity and representativeness, reproducing real-world social phenomena across elections, economics, and social influence.

#### Core Motivation
Current simulations lack systematic alignment with real-world dynamics. Agents diverge from real populations because they lack grounding in actual demographics, social structures, and institutional rules. A "world model" approach ensures alignment at every layer.

#### Core Idea
```
Four-Layer Alignment:
  1. Environment Alignment: Simulated world ≈ Real world structure
  2. User Alignment: Agent demographics ≈ Real population (10M user pool)
  3. Interaction Alignment: Agent interactions ≈ Real social interactions
  4. Rule Alignment: Simulation rules ≈ Real institutional rules
```

#### Example
```
Election simulation: Sample 10K agents matching real voter demographics
→ Simulate media landscape, social network discussion, voting rules
→ Predicted vote shares match real results within 3%
```

#### Relationship to Our Work

| Aspect      | SocioVerse                       | Our Research Target             |
|-------------|----------------------------------|---------------------------------|
| Alignment   | Four-layer framework             | Need finance-specific alignment |
| User Pool   | 10M real users                   | Need financial participant data |
| Validation  | Election/social outcomes         | Financial market outcomes       |
| Key Advance | Systematic alignment methodology | Applicable to finance domain    |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 2.3 CitySim: Modeling Urban Behaviors and City Dynamics (EMNLP 2025)

**[CAT: Social Simulation] [REL: Medium]**

**Paper**: "CitySim: Modeling Urban Behaviors and City Dynamics with Large-Scale LLM-Driven Agent Simulation"
**Link**: https://arxiv.org/abs/2506.21805
**Code**: Null

#### Summary
CitySim is a scalable city simulation framework where LLM-powered agents autonomously generate daily schedules using a recursive value-driven approach that balances mandatory activities, personal habits, and situational context. It models realistic urban mobility patterns, social interactions, and daily activity sequences at city scale, demonstrating that LLM agents can produce human-like urban behavior patterns.

#### Core Motivation
Urban planning requires understanding how people move through and interact with cities. Traditional activity-based models use rigid rules and cannot capture the flexible, context-dependent nature of human daily schedules. LLM agents can generate more realistic, adaptive daily schedules.

#### Core Idea
```
Recursive Value-Driven Scheduling:
  Agent values + Current context → LLM → Next activity
  Balance: Mandatory (work) + Habits (gym) + Situational (weather, events)
```

#### Example
```
Agent "Lisa" (office worker, fitness enthusiast):
  Morning: Go to office (mandatory) → Lunch with colleague (social) 
  → Gym (habit) → Grocery shopping (situational: fridge empty)
→ Produces realistic urban mobility trajectory
```

#### Relationship to Our Work

| Aspect     | CitySim          | Our Research Target                  |
|------------|------------------|--------------------------------------|
| Domain     | Urban mobility   | Financial mobility (capital flows)   |
| Scheduling | Daily activities | Trading schedules, investment cycles |
| Validation | Urban patterns   | Financial patterns needed            |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

## 3. Social Network and Information Diffusion

### 3.1 S³: Social-network Simulation System (2023)

**[CAT: Information Diffusion] [REL: High]**

**Paper**: "S³: Social-network Simulation System with Large Language Model-Empowered Agents"
**Link**: https://arxiv.org/abs/2307.14984
**Code**: Null

#### Summary
S³ harnesses LLM capabilities in sensing, reasoning, and behaving to simulate social network dynamics. Each agent senses its local network context, reasons about social situations via LLM, and behaves accordingly. S³ demonstrates that LLM-empowered agents produce more realistic information diffusion and opinion dynamics than rule-based approaches, capturing trust assessment and credibility evaluation that fixed-rule models miss.

#### Core Motivation
Traditional social network simulations use fixed mathematical rules (SIR, threshold models) that cannot capture nuanced reasoning about trust, credibility, and emotional resonance that humans employ when deciding to share information.

#### Core Idea
```
Traditional:  Node + Fixed Rule → Propagation
S³:           Agent + LLM → Context-Aware Propagation
  Sense (read neighbors' states) → Reason (LLM decides) → Behave (act)
```

#### Example
```
Health misinformation: 
  Agent "Maria" (skeptical): Sensing → "Sounds too good to be true" → Does NOT share
  Agent "Alex" (trusting): Sensing → "Many people sharing, must be important" → SHARES
→ Heterogeneous adoption patterns matching real data
```

#### Relationship to Our Work

| Aspect      | S³                                  | Our Research Target                         |
|-------------|-------------------------------------|---------------------------------------------|
| Network     | Social information network          | Financial network (investors, institutions) |
| Propagation | Information/opinions                | Market sentiment, trading signals           |
| Agent       | LLM with sensing-reasoning-behaving | Need financial reasoning capability         |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 3.2 GA-S³: Comprehensive Social Network Simulation with Group Agents (ACL Findings 2025)

**[CAT: Information Diffusion] [REL: Medium]**

**Paper**: "GA-S³: Comprehensive Social Network Simulation with Group Agents"
**Link**: https://arxiv.org/abs/2506.03532
**Code**: https://github.com/AI4SS/GAS-3

#### Summary
GA-S³ extends S³ by introducing Group Agents that represent collective entities (organizations, communities, interest groups). Group Agents use hierarchical decision-making that aggregates members' preferences before producing group-level actions, enabling simulation of institutional communication and coordinated group behavior that individual-only models miss.

#### Core Idea
```
Individual Agent: Person → LLM → Action
Group Agent: Members → Aggregation → LLM → Group Action
  (CEO + PR + Legal → Consensus → Corporate statement)
```

#### Example
```
Company "TechCorp" decides on public statement:
  CEO: "Address quickly" (weight: 0.4) + PR: "Careful statement" (0.3) + Legal: "No liability" (0.3)
  → Aggregation → Cautious public acknowledgment issued
```

#### Relationship to Our Work

| Aspect     | GA-S³                    | Our Research Target                  |
|------------|--------------------------|--------------------------------------|
| Agent Type | Individuals + Groups     | Individual + Institutional investors |
| Decision   | Hierarchical aggregation | Investment committee decisions       |


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 3.3 OASIS: Open Agent Social Interaction Simulations with 1M Agents (2024)

**[CAT: Information Diffusion] [REL: High]**

**Paper**: "OASIS: Open Agent Social Interaction Simulations with One Million Agents"
**Link**: https://arxiv.org/abs/2411.11581
**Code**: https://github.com/camel-ai/oasis

#### Summary
OASIS is a scalable social media simulator using LLM agents to mimic behavior of up to one million users on Twitter/X and Reddit. It reproduces information diffusion, opinion polarization, and herd behavior at unprecedented scale with distributed architecture achieving linear scaling. Demonstrates S-curve viral adoption patterns matching real social media data.

#### Core Idea
```
Scalable Architecture = Distributed LLM Inference + Social Graph
  - Agent profile + recent interactions → LLM → Action (post/like/repost)
  - Distributed across GPU cluster for million-scale
  - Reproduces: viral spreading, echo chambers, herd behavior
```

#### Example
```
Viral content spread:
  T=0: Agent A posts → T=1: 10 followers see, 3 repost 
  → T=5: 5,000 engaged → T=10: 100,000+ → Full viral cascade
  OASIS reproduces S-curve adoption pattern from real viral events
```

#### Relationship to Our Work

| Aspect       | OASIS                      | Our Research Target                 |
|--------------|----------------------------|-------------------------------------|
| Scale        | 1M agents                  | Similar scale for market simulation |
| Phenomena    | Viral spread, polarization | Market panics, bubbles              |
| Architecture | Distributed sharding       | Applicable to market simulation     |


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 3.4 LLM-AIDSim: LLM-Enhanced Agent-Based Influence Diffusion Simulation (2025)

**[CAT: Information Diffusion] [REL: Medium]**

**Paper**: "LLM-AIDSim: LLM-Enhanced Agent-Based Influence Diffusion Simulation in Social Networks"
**Link**: https://www.mdpi.com/2079-8954/13/1/29
**Code**: Null

#### Summary
LLM-AIDSim integrates LLMs (Llama3:8b) into agent-based modeling for influence diffusion in social networks. Unlike traditional threshold-based influence models, LLM agents evaluate influence based on semantic understanding of message content and social context, enabling language-level responses and deeper influence dynamics modeling.

#### Core Motivation
Traditional influence diffusion models use binary adoption states and fixed thresholds, missing the nuanced reasoning about why someone is influenced. LLMs can model the cognitive process of influence acceptance/rejection based on message content, source credibility, and personal values.

#### Example
```
Influence attempt: "Invest in crypto, it's the future!"
  Agent A (tech-savvy): Evaluates content → "Innovation argument aligns with my values" → Accepts
  Agent B (conservative): Evaluates content → "Speculative, doesn't match risk tolerance" → Rejects
→ More realistic influence patterns than threshold models
```


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 3.5 SALM: A Multi-Agent Framework for LLM-Driven Social Network Simulation (2025)

**[CAT: Information Diffusion] [REL: Medium]**

**Paper**: "SALM: A Multi-Agent Framework for Language Model-Driven Social Network Simulation"
**Link**: https://arxiv.org/abs/2505.09081
**Code**: Null

#### Summary
SALM integrates LLMs with traditional social simulation through a hierarchical prompting architecture grounded in Habermas's theory of communicative action. It enables stable simulation beyond 4,000 timesteps while reducing token usage by 73%, producing more coherent long-term social dynamics than unconstrained LLM agent interactions.

#### Core Motivation
Unconstrained LLM agent interactions degenerate over long simulations — agents drift from personas, produce inconsistent behavior, or generate repetitive interactions. Theoretical framework needed to structure agent communication and maintain stability.

#### Core Idea
```
Habermas's Communicative Action → Structured Agent Discourse
  Unconstrained: Agent → LLM → Free-form response (unstable)
  SALM: Agent → Hierarchical Prompt → Structured discourse (stable)
  Result: 4,000+ timesteps with 73% token reduction
```

#### Example
```
Timestep 3,500: "Should we adopt the new policy?"
  Agent A: Claim → "I oppose" + Justification → "Changes traditions too quickly"
  Agent B: Challenge → "Current system isn't working"
  → Structured debate → Policy vote outcome
```

#### Relationship to Our Work

| Aspect     | SALM                 | Our Research Target                 |
|------------|----------------------|-------------------------------------|
| Stability  | 4,000+ timesteps     | Need long-term market simulation    |
| Efficiency | 73% token reduction  | Cost control for large-scale sims   |
| Theory     | Communicative action | May need financial theory grounding |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

## 4. Opinion Dynamics and Polarization

### 4.1 Decoding Echo Chambers: LLM-Powered Simulations Revealing Polarization (COLING 2025)

**[CAT: Opinion Dynamics] [REL: High]**

**Paper**: "Decoding Echo Chambers: LLM-Powered Simulations Revealing Polarization in Social Networks"
**Link**: https://arxiv.org/abs/2409.19338
**Code**: Null

#### Summary
Uses LLM-powered agents to simulate opinion dynamics and reproduce polarization and echo chamber phenomena in social networks. Proposes two mitigation methods (active and passive) for reducing polarization through language-based intervention. Demonstrates that LLM agents naturally develop polarized opinions when exposed to like-minded social networks, mirroring real-world echo chamber dynamics.

#### Core Motivation
Understanding opinion polarization requires models that capture not just opinion states but the reasoning behind opinion formation. Traditional bounded-confidence models use fixed update rules; LLM agents can reason about why they agree or disagree with arguments, producing more realistic polarization dynamics.

#### Core Idea
```
Traditional: opinion_i += α·(opinion_j - opinion_i)  (fixed update)
LLM-based:   Agent reads arguments → Reasons about validity → Updates opinion

Key finding: LLM agents naturally polarize in homophilous networks
Mitigation: Active (counter-argument injection) and Passive (diverse exposure)
```

#### Example
```
Network: 3 clusters with different political leanings
  After 10 rounds of social interaction:
  Cluster A (left-leaning): opinions shift further left
  Cluster C (right-leaning): opinions shift further right
  → Echo chambers form naturally, matching real-world data
```

#### Relationship to Our Work

| Aspect     | Echo Chamber Sim           | Our Research Target               |
|------------|----------------------------|-----------------------------------|
| Phenomenon | Opinion polarization       | Market sentiment polarization     |
| Mitigation | Counter-argument injection | Contrarian information injection  |
| Dynamics   | Gradual opinion shift      | Sudden sentiment reversal (crash) |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 4.2 MTOS: Multi-Topic Opinion Simulation for Echo Chamber Dynamics (2024)

**[CAT: Opinion Dynamics] [REL: Medium]**

**Paper**: "MTOS: A LLM-Driven Multi-topic Opinion Simulation Framework for Exploring Echo Chamber Dynamics"
**Link**: https://arxiv.org/abs/2510.12423
**Code**: Null

#### Summary
MTOS simulates multi-topic opinion dynamics in social networks, exploring how echo chambers form across multiple simultaneously discussed topics. Unlike single-topic models, MTOS captures cross-topic influence where opinions on one topic affect stances on related topics, producing more realistic polarization patterns.

#### Core Idea
```
Single-topic sim: Opinion_A evolves independently
MTOS: Opinion_A ↔ Opinion_B ↔ Opinion_C (cross-topic influence)
  Example: Views on climate policy affect views on energy regulation
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 4.3 LLM-Driven Agents for Simulating Echo Chamber Dynamics (2025)

**[CAT: Opinion Dynamics] [REL: Medium]**

**Paper**: "Large Language Model Driven Agents for Simulating Echo Chamber Dynamics in Social Networks"
**Link**: https://arxiv.org/abs/2502.18138
**Code**: Null

#### Summary
Presents a framework leveraging LLMs as generative agents to simulate echo chamber dynamics within social networks, studying how algorithmic recommendation and selective exposure create feedback loops that reinforce existing beliefs and reduce opinion diversity.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 5. Emergent Social Norms and Conventions

### 5.1 Emergent Social Conventions and Collective Bias in LLM Populations (Science Advances 2025)

**[CAT: Emergence] [REL: Critical]**

**Paper**: "Emergent Social Conventions and Collective Bias in LLM Populations"
**Link**: https://arxiv.org/abs/2410.08948
**Code**: Null

#### Summary
Published in Science Advances, this work demonstrates the spontaneous emergence of universally adopted social conventions in decentralized populations of LLM agents. Without any central coordination, LLM agents interacting in pairs converge on shared naming conventions, and critically, develop collective biases that are not present in any individual agent. This is the first demonstration that population-level social conventions and biases can emerge from LLM agent interactions, with direct implications for understanding how bias propagates in AI-mediated social systems.

#### Core Motivation
Social conventions (shared naming, behavioral norms) and collective biases emerge from human social interaction, not from individual cognition. Can LLM agents, interacting without central coordination, spontaneously develop shared conventions and biases? This is fundamental to understanding whether LLM-based simulations can reproduce the emergent social phenomena that define human societies.

#### Core Idea
```
No central coordination → Agents interact pairwise → Shared convention emerges

Key Discovery: Collective bias emerges that NO individual agent holds
  Individual: Unbiased preferences
  Population: Systematic collective bias (toward certain conventions)
  
This mirrors how systemic biases emerge in real societies
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│         Convention Emergence Experiment                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Setup: Population of LLM agents                          │
│  Task: Naming game — agents must agree on a name          │
│                                                           │
│  Round 1:  Agent A says "dax"  Agent B says "fep"        │
│            No agreement → try again                       │
│  Round 5:  Agent A says "dax"  Agent B says "dax"        │
│            Agreement! → Both remember "dax"               │
│  Round 20: 90% of population uses "dax"                  │
│            Convention has emerged                          │
│                                                           │
│  Critical Finding:                                        │
│    When multiple conventions compete, the winning          │
│    convention carries a systematic bias that was NOT       │
│    in any individual agent's prior.                       │
│    → Collective bias is an EMERGENT property              │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Naming game with 24 agents:
  Round 1: 24 different names proposed
  Round 10: 3 names remain in competition
  Round 30: 1 name adopted by all → Convention emerged

  Bias: The winning name was systematically preferred for
  objects associated with certain attributes → Collective bias
  emerged that no individual agent initially held
```

#### Relationship to Our Work

| Aspect      | Convention Emergence             | Our Research Target                  |
|-------------|----------------------------------|--------------------------------------|
| Phenomenon  | Social conventions               | Market conventions, trading norms    |
| Bias        | Collective bias from interaction | Systemic financial bias              |
| Key Insight | Emergence without coordination   | Financial norms may emerge similarly |
| Validation  | Naming game experiments          | Market convention experiments needed |

---

### 5.2 Emergent Social Dynamics in the El Farol Bar Problem (2025)

**[CAT: Emergence] [REL: High]**

**Paper**: "Emergent Social Dynamics of LLM Agents in the El Farol Bar Problem"
**Link**: https://arxiv.org/abs/2509.04537
**Code**: Null

#### Summary
Investigates emergent social dynamics of LLM agents in the spatially extended El Farol Bar problem — a classic bounded-resource social dilemma where agents must decide whether to attend a bar with limited capacity. LLM agents develop individual strategies through social interaction, showing spontaneous emergence of agent individuality and coordination patterns that mirror human behavior in shared-resource dilemmas.

#### Core Motivation
The El Farol Bar problem is a canonical model for studying how individuals coordinate (or fail to coordinate) in the face of limited resources. Traditional approaches use fixed strategies; LLM agents can adapt their reasoning based on social context, potentially producing more realistic coordination dynamics.

#### Core Idea
```
El Farol Bar: N agents, bar capacity < N/2
  If too many go → overcrowded → bad experience
  If too few go → underutilized → missed opportunity
  
LLM agents: Read past attendance → Reason about others → Decide go/stay
→ Spontaneous emergence of individuality and coordination patterns
```

#### Example
```
Week 1: 70% of agents go → Overcrowded → Bad experience
Week 2: 40% go → Good experience for attendees
Week 3: LLM agents reason: "Last week was good, more will go" → 65% go
→ Oscillating attendance pattern emerges, similar to human experiments
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 6. Cooperation, Trust, and Social Dilemmas

### 6.1 Simulating Cooperative Prosocial Behavior with Multi-Agent LLMs (2025)

**[CAT: Social Dilemmas] [REL: Medium]**

**Paper**: "Simulating Cooperative Prosocial Behavior with Multi-Agent LLMs"
**Link**: https://arxiv.org/abs/2502.12504
**Code**: Null

#### Summary
Studies how well multi-agent LLM systems can simulate prosocial human behavior in the Public Goods Game (PGG). LLM agents make contribution decisions in a shared resource pool, and their behavior is compared to human experimental data. Findings show LLM agents can produce cooperation levels qualitatively similar to humans but with different dynamics.

#### Core Idea
```
Public Goods Game: Each agent contributes to shared pool → Pool multiplied → Redistributed
  LLM agents: "Should I contribute? Others might free-ride..."
  → Cooperation emerges but with different decay patterns than humans
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 6.2 Evolution of Cooperation in LLM-Agent Societies (2025)

**[CAT: Social Dilemmas] [REL: Medium]**

**Paper**: "Evolution of Cooperation in LLM-Agent Societies"
**Link**: https://arxiv.org/abs/2504.19487
**Code**: Null

#### Summary
Investigates whether cooperation dynamics from Boyd and Richerson's cultural evolution model persist in LLM-agent simulations. Uses LLM agents to study how cooperation norms evolve and are maintained in societies facing free-rider problems, comparing simulation results to theoretical predictions from cultural evolution theory.

#### Core Idea
```
Question: Can LLM agents sustain cooperation when defection is individually rational?
Finding: LLM agents develop and maintain cooperation norms through social learning,
  but stability depends on population structure and interaction patterns
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 6.3 LLM Agents in Morally Charged Social Dilemmas (2025)

**[CAT: Social Dilemmas] [REL: Medium]**

**Paper**: "LLM Agents in Morally Charged Social Dilemmas"
**Link**: https://arxiv.org/abs/2505.19212
**Code**: Null

#### Summary
Focuses on two canonical social dilemmas (Prisoner's Dilemma and Public Goods Game) with moral framing. Studies how LLM agents make decisions when social dilemmas are presented with moral language, and whether their behavior mirrors human moral intuitions in cooperation/defection scenarios.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 7. Elections and Political Behavior Simulation

### 7.1 FlockVote: LLM-Empowered Agent-Based Modeling for U.S. Presidential Elections (2024)

**[CAT: Political Simulation] [REL: High]**

**Paper**: "FlockVote: LLM-Empowered Agent-Based Modeling for Simulating U.S. Presidential Elections"
**Link**: https://arxiv.org/abs/2512.05982
**Code**: Null

#### Summary
FlockVote combines demographic profiling with LLM agent-based modeling to simulate U.S. presidential elections. Agents are initialized with demographic personas and engage in political discussion, media consumption, and opinion formation. The system predicts election outcomes by modeling individual voter behavior and social influence dynamics, demonstrating that LLM agents can capture the complexity of voter decision-making.

#### Core Motivation
Traditional election models use statistical aggregation of polls, missing the dynamic process of voter opinion formation through social interaction. LLM agents can model how individual voters reason about candidates, how social influence shapes opinions, and how events shift the electorate.

#### Core Idea
```
Statistical Model:  Polls → Aggregate → Predict
FlockVote:          Demographics → LLM Voters → Social Interaction → Vote Decision

Each voter agent: Demographics + Media exposure + Social network → LLM → Vote choice
→ Emergent election outcomes from individual-level reasoning
```

#### Example
```
Voter "Maria" (Hispanic, 35, suburban):
  Social feed: 3 friends support Candidate A, 1 supports B
  Media: Read article about Candidate A's healthcare plan
  Reasoning: "A's plan helps my community" → Votes A

Aggregate across 10,000 voter agents → Predict state-level results
```

#### Relationship to Our Work

| Aspect           | FlockVote            | Our Research Target        |
|------------------|----------------------|----------------------------|
| Phenomenon       | Election outcomes    | Financial market outcomes  |
| Agents           | Voter personas       | Investor personas          |
| Social influence | Political discussion | Market sentiment contagion |
| Validation       | Election results     | Market price movements     |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

## 8. Financial Market Simulation

### 8.1 Can LLMs Trade? Testing Financial Theories with LLM Agents (2025)

**[CAT: Financial Simulation] [REL: Critical]**

**Paper**: "Can Large Language Models Trade? Testing Financial Theories with LLM Agents in Market Simulations"
**Link**: https://arxiv.org/abs/2504.10789
**Code**: Null

#### Summary
Presents a realistic simulated stock market where LLM agents act as heterogeneous competing trading agents. Tests whether LLM agents can reproduce known financial phenomena (market efficiency, momentum, mean reversion) and evaluates how different LLM personalities affect market dynamics. Provides a systematic protocol for implementing and validating LLM trading agents across different market conditions.

#### Core Motivation
If LLMs can trade like humans, we can run economic "experiments" with LLMs instead of human subjects. If they trade differently, we need to understand how they differ. This is fundamental to whether LLM-based financial simulation is viable for research and policy analysis.

#### Core Idea
```
Traditional Market Sim: Mathematical agents with fixed strategies
LLM Market Sim:        LLM agents with personality-driven strategies

Question: Do LLM markets reproduce real market phenomena?
Answer:  Yes for some (price discovery, spread dynamics), 
         No for others (excess volatility, momentum patterns)
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│           LLM Trading Agent Market Simulation              │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Market Engine:                                           │
│    - Continuous double auction order book                  │
│    - Multiple tradable assets                              │
│    - News feed system                                      │
│                                                           │
│  LLM Trading Agents:                                      │
│    Each agent has:                                         │
│    - Risk profile (conservative/aggressive)                │
│    - Trading style (fundamental/technical/momentum)        │
│    - Portfolio position                                    │
│    → LLM generates: BUY/SELL/HOLD + quantity + price      │
│                                                           │
│  Validation:                                              │
│    Compare emergent market phenomena to real markets:      │
│    - Price discovery efficiency                            │
│    - Spread dynamics                                       │
│    - Volatility clustering                                 │
│    - Momentum and mean reversion                           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
News: "Fed signals potential rate cut"
  Conservative agent: "Rate cuts support equities, but I'll wait for confirmation"
  Aggressive agent: "Buy now before the rally — rate cuts are bullish!"
  → Diverse reactions create realistic price dynamics
```

#### Relationship to Our Work

| Aspect      | LLM Trading Sim                    | Our Research Target                |
|-------------|------------------------------------|------------------------------------|
| Phenomenon  | Market dynamics                    | Full financial behavior            |
| Agents      | Heterogeneous traders              | Need institutional + retail agents |
| Validation  | Financial theory tests             | Match real market statistics       |
| Key Advance | Tests if LLM markets are realistic | Foundation for our financial sim   |

---

### 8.2 TwinMarket: A Scalable Behavioral and Social Simulation for Financial Markets (NeurIPS 2025)

**[CAT: Financial Simulation] [REL: Critical]**

**Paper**: "TwinMarket: A Scalable Behavioral and Social Simulation for Financial Markets"
**Authors**: Yuzhe Yang, Yifei Zhang, Minghao Wu, Kaidi Zhang, Yunmiao Zhang, Honghai Yu, Yan Hu, Benyou Wang (CUHK-Shenzhen, Nanjing University)
**Venue**: NeurIPS 2025 (also Best Paper Award at ICLR 2025 Financial AI Workshop)
**Link**: https://arxiv.org/abs/2502.01506
**Code**: https://github.com/FreedomIntelligence/TwinMarket

#### Summary
TwinMarket introduces a large-scale multi-agent framework that leverages LLMs with a Belief-Desire-Intention (BDI) cognitive architecture to simulate financial markets where individual behaviors, through social interaction and feedback mechanisms, produce emergent collective dynamics. Each agent operates within a socially embedded environment featuring an order-driven trading system and a social media platform, enabling the study of how micro-level cognitive processes aggregate into macro-level phenomena such as financial bubbles, market recessions, opinion leader emergence, and information polarization. The framework reproduces all four major stylized facts of financial markets (fat-tailed returns, leverage effect, volume-return correlation, volatility clustering) and scales to 1,000+ LLM-powered agents — the most comprehensive LLM-driven financial market simulation to date.

#### Core Motivation
Traditional agent-based models (ABMs) for financial markets rely on rule-based approaches that oversimplify human decision-making by assuming homogeneous agents and static behavioral rules. They fail to capture the irrational factors emphasized in behavioral economics — cognitive biases, emotional fluctuations, loss aversion, herding — that drive real market dynamics. Meanwhile, existing LLM-based financial systems (CompeteAI, EconAgent, ASFM) either use fixed prompts limiting behavioral nuance, lack agent interaction, or fail to model collective decision-making. A framework is needed that grounds LLM agents in behavioral theory, enables rich social interaction, and scales to realistic market populations while reproducing known empirical phenomena.

#### Core Idea
```
BDI Cognitive Architecture + Social Network + Order-Driven Market = Emergent Financial Dynamics

Traditional ABM:  Rules → Homogeneous agents → Simplified market
TwinMarket:      BDI (Belief-Desire-Intention) → Heterogeneous agents + Social interaction → Emergent phenomena

Key Insight: Individual cognitive processes (beliefs shaped by biases, desires driving information-seeking,
             intentions committing to actions) aggregate through social network propagation
             into macro-level market dynamics that NO individual agent designed.
```

#### Core Method
```
┌─────────────────────────────────────────────────────────────────┐
│                    TwinMarket Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MICRO-LEVEL: BDI-Driven Agent                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Belief:  Market perception + behavioral biases           │  │
│  │    - Overconfidence, loss aversion, herding, risk prefs   │  │
│  │    - Dynamically updated after each trading day           │  │
│  │    - Outputs sentiment scores for belief tracking         │  │
│  │         ↓                                                  │  │
│  │  Desire:  Agent-generated queries for market info          │  │
│  │    - Autonomously retrieves relevant stock/news data      │  │
│  │    - Enhances comprehension beyond initial beliefs        │  │
│  │         ↓                                                  │  │
│  │  Intention: Committed trading + social actions             │  │
│  │    - Final buy/sell/hold decisions                        │  │
│  │    - Social media posting and reposting                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  MACRO-LEVEL: Dual Infrastructure                                │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐  │
│  │ Order-Driven      │  │ Social Media Platform               │  │
│  │ Trading System     │  │ - Dynamic social network (G=V,E)    │  │
│  │ - Call auction     │  │ - Edge weight: trading similarity   │  │
│  │ - Index updates    │  │   w(u,i) = Σ e^(-λ·Δt)            │  │
│  │ - SSE 50 stocks    │  │ - Hot score ranking for feed        │  │
│  └──────────────────┘  │ - Personalized information delivery  │  │
│                         └──────────────────────────────────────┘  │
│                                                                  │
│  DATA GROUNDING: Real-world data from Xueqiu (639 users),        │
│  Guba (83K transactions), CSMAR (SSE 50 index), Sina Finance,    │
│  CNINFO (company announcements) — Jan-Dec 2023                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Example
```
Rumor Injection Experiment — Market Crash from Negative Information:

Step 1: Negative rumor injected into social media
Step 2: Agent beliefs diverge from control group (increasingly pessimistic)
Step 3: Sell-to-buy ratio nearly doubles: 0.495 → 0.997
Step 4: Market price shows pronounced decline vs. stable control
Step 5: Echo chambers form — rumor-affected users interact only
        with like-minded peers, intensifying belief polarization

→ Emergent outcome: Self-reinforcing market downturn from
   individual panic responses amplified through social network
```

#### Key Results
- **Stylized facts reproduced** (kurtosis 5.24 vs. real 7.26; leverage effect -0.11 vs. real -0.14; GARCH α+β=0.89 vs. real 0.95; volume-return p<0.01)
- **Ablation confirms BDI and heterogeneity are essential**: removing BDI drops kurtosis to 4.25, correlation to 0.34; removing heterogeneity produces near-Gaussian returns and negative correlation (-0.61)
- **Scalability**: 10%→80% activated traders show monotonic reduction in RMSE/MAE; successfully runs with 1,000 LLM agents
- **Wealth inequality emerges**: Gini coefficient shows upward trend; top 10% earn 6.65% returns with 4.02% turnover; bottom 50% lose -10.52% with 7.03% turnover
- **Opinion leaders emerge** organically from network structure; high-degree users receive more upvotes and shape market sentiment
- **Won Best Paper Award** at ICLR 2025 Advances in Financial AI Workshop

#### Relationship to Our Work

| Aspect          | TwinMarket                                | Our Research Target                             |
|-----------------|-------------------------------------------|-------------------------------------------------|
| Simulation Type | Financial market with social network      | Full society + financial system integration     |
| Agent Cognition | BDI framework with behavioral biases      | Need similar cognitive architecture for finance |
| Social Layer    | Social media + trading system             | Need broader social context beyond finance      |
| Scale           | 1,000+ LLM agents                         | Similar scale needed                            |
| Validation      | Stylized facts + rumor experiments        | Must match real societal + financial features   |
| Key Advance     | First to show BDI + social → emergent mkt | Foundation for our financial simulation module  |

---

### 8.3 MarS: A Financial Market Simulation Engine Powered by Generative Foundation Model (ICLR 2025)

**[CAT: Financial Simulation] [REL: Critical]**

**Paper**: "MarS: a Financial Market Simulation Engine Powered by Generative Foundation Model"
**Authors**: Junjie Li, Yang Liu, Weiqing Liu, Shikai Fang, Lewen Wang, Chang Xu, Jiang Bian (Microsoft Research Asia)
**Venue**: ICLR 2025
**Link**: https://arxiv.org/abs/2409.07486
**Code**: https://github.com/microsoft/MarS

#### Summary
MarS introduces a generative foundation model approach to financial market simulation, fundamentally different from agent-based methods. It proposes the Large Market Model (LMM) — an order-level generative model trained on 32 billion tokens of real order data — that simulates markets by autoregressively generating realistic order flows rather than having agents make decisions. The MarS engine combines fine-grained order sequence modeling (causal transformer) with macro-level order-batch modeling (VQ-VAE + autoregressive transformer) to produce controllable, interactive market simulations. It validates against 14 stylized facts, discovers new market impact factors via symbolic regression, and demonstrates applications in forecasting (outperforms DeepLOB), manipulation detection, what-if analysis, and RL agent training — representing a paradigm shift from agent-based to generative simulation.

#### Core Motivation
Existing financial market simulations rely on agent-based models with predefined behavioral rules that lack the resolution, interactivity, and realism to reflect full market complexity. Rule-based agents cannot capture the intricate microstructure of order-level dynamics. A generative foundation model approach — analogous to how language models generate text — can learn realistic market patterns directly from data and generate order-level simulations with fine-grained control, without requiring manually designed agent behaviors.

#### Core Idea
```
Agent-Based Simulation:  Predefined rules → Agent decisions → Market outcomes
Generative Simulation:   Historical order data → LMM → Realistic order generation → Market outcomes

Key Paradigm Shift:
  Traditional: Model the AGENTS (who trade?)
  MarS:        Model the ORDERS (what gets traded?)
  
  LMM learns order-level patterns from 32B tokens of real market data
  → Generates realistic order flows conditioned on control signals
  → Simulated clearing house processes orders → Market prices emerge
```

#### Core Method
```
┌─────────────────────────────────────────────────────────────────┐
│                    MarS Architecture                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Two-Level Order Generation:                                     │
│                                                                  │
│  Level 1 — Order Sequence Model (Fine-grained):                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Causal Transformer + LOB Embeddings                      │  │
│  │  Input: Order attributes (type, price, volume, interval)  │  │
│  │        + 10-level LOB volumes + mid-price                 │  │
│  │  Output: Next order prediction                            │  │
│  │  Scale: 2M to 1.02B parameters, 32B tokens               │  │
│  └────────────────────────────────────────────────────────────┘  │
│                         ↓                                        │
│  Level 2 — Order-Batch Model (Macro):                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Order batches → RGB images → VQ-VAE → Autoregressive TF  │  │
│  │  Input: Aggregated order batches per time step            │  │
│  │  Output: Next batch distribution (N candidates)           │  │
│  │  Scale: 150M to 3B parameters, 10B tokens                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                         ↓                                        │
│  Ensemble Model: Combines both levels for coherence + detail     │
│                         ↓                                        │
│  Fine-Grained Signal Interface:                                  │
│    Natural language → LLM retrieval → Control signals            │
│    (e.g., "price bump" → historical pattern → generation guide)  │
│                         ↓                                        │
│  Simulated Clearing House: Processes orders → Market prices      │
│                                                                  │
│  Two Guiding Principles:                                         │
│    1. "Shape future based on realized realities" (feedback loop) │
│    2. "Elect best from every possible future" (filter by signal) │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Example
```
Controllable Market Simulation — "What if the market experiences a crash?":

Step 1: User provides control signal: "significant price decline"
Step 2: Fine-Grained Signal Interface maps to historical crash patterns
Step 3: Order-Batch Model generates N candidate batch distributions
Step 4: Filter selects batch matching crash signal
Step 5: Order Model generates individual orders within batch
Step 6: Simulated clearing house processes → Prices decline
Step 7: Feedback: Generated prices feed back into next step

→ Realistic crash trajectory generated from learned order-level patterns
→ Correlation with historical data: 0.47 (vs. 0.23 without control)
```

#### Key Results
- **14 stylized facts reproduced**: aggregational Gaussianity, absence of autocorrelations, volatility clustering, + 11 more
- **Square-root-law validated**: Δ ∝ σQ/V, confirming realistic market impact
- **Forecasting**: Outperforms DeepLOB baseline; larger models perform better (scaling law confirmed)
- **Manipulation detection**: Distribution similarity >0.87 during normal periods; drops significantly during manipulation
- **New market impact factors discovered** via symbolic regression: resiliency, LOB pressure, LOB depth
- **RL agent training**: Agents improve from -6 BP to 2-6 BP price advantage when trained in MarS
- **Controllability**: Control signals improve correlation with real data by 103% (0.23→0.47)

#### Relationship to Our Work

| Aspect          | MarS                                   | Our Research Target                           |
|-----------------|----------------------------------------|-----------------------------------------------|
| Approach        | Generative model (data-driven)         | Agent-based simulation (behavior-driven)      |
| Granularity     | Order-level (finest microstructure)    | May need both agent-level and order-level     |
| Agents          | No explicit agents (orders generated)  | Need LLM agents with cognitive models         |
| Social Layer    | None (pure market simulation)          | Must include social interaction               |
| Validation      | Stylized facts + market impact laws    | Must match real societal + financial features |
| Key Difference  | Models ORDERS not agents               | We need agents with social behavior           |
| Complementarity | Best for market microstructure realism | Best for behavioral/social emergence          |

---

### 8.4 FCLAgent: Agent-Based Simulation with Fundamental-Chartist-LLM Agents (2025)

**[CAT: Financial Simulation] [REL: High]**

**Paper**: "Agent-Based Simulation of a Financial Market with Large Language Models"
**Authors**: Ryuji Hashimoto, Takehiro Takayanagi, Masahiro Suzuki, Kiyoshi Izumi
**Venue**: Published at Springer LNCS (2025)
**Link**: https://arxiv.org/abs/2510.12189
**Code**: Null

#### Summary
Proposes the Fundamental-Chartist-LLM-Agent (FCLAgent) framework that integrates LLM-based decision-making into traditional agent-based market simulation. In FCLAgent, buy/sell decisions are made by LLMs based on individual situations (capturing path-dependent behavioral biases like loss aversion anchored to personal reference points), while order price and volume follow standard rule-based methods. Simulations demonstrate that FCLAgents reproduce path-dependent market patterns — such as price declines near historical highs — that conventional rule-based agents fail to capture, with the reference points guiding loss aversion varying dynamically with market trajectories.

#### Core Motivation
Certain chart patterns in real stock markets — like price declines near historical highs — cannot be explained by fundamentals alone and suggest path dependence in price formation. A key driver is human loss aversion anchored to individual reference points (purchase prices, past peaks) that vary with personal context. Traditional ABMs struggle to capture such subtle, context-dependent behavioral tendencies because they use fixed rules. LLMs can model nuanced, path-dependent investor behavior by reasoning about individual situations rather than following static thresholds.

#### Core Idea
```
Traditional ABM:   Fixed rule → Same response for all agents in same state
FCLAgent:          LLM reasoning → Path-dependent response based on individual history

Key Mechanism:
  LLM makes buy/sell decision based on:
    - Personal reference point (e.g., purchase price, past peak)
    - Current market trajectory relative to that reference
    → Loss aversion varies with market path → Path-dependent price formation
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│              FCLAgent Architecture                         │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  LLM Decision Module (Buy/Sell/Hold):                     │
│    Input: Individual situation + market context            │
│    - Personal reference point (purchase price/past peak)  │
│    - Current price relative to reference                   │
│    - Market trajectory leading to present                  │
│    Output: Trading direction                               │
│                                                           │
│  Rule-Based Execution Module (Price + Volume):            │
│    - Order price: Based on standard pricing rules          │
│    - Order volume: Based on position sizing rules          │
│                                                           │
│  Key Insight: Hybrid approach                             │
│    LLM handles: Cognitive, context-dependent decisions    │
│    Rules handle: Quantitative execution parameters         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Path-Dependent Loss Aversion near Historical High:

Agent A (bought at $100, current price $95):
  LLM reasoning: "I'm losing money, but it might recover" → HOLD
  Reference point: $100 (purchase price)

Agent B (bought at $80, current price $95):
  LLM reasoning: "Still profitable, but near my peak — I should protect gains" → SELL
  Reference point: $95 (near peak, loss aversion kicks in)

→ Same price, different decisions based on individual trajectory
→ Produces path-dependent market patterns matching real observations
```

#### Key Results
- FCLAgents reproduce path-dependent patterns that conventional agents fail to capture
- Reference points guiding loss aversion vary dynamically with market trajectories
- LLMs' behavioral biases are context-dependent, similar to humans
- Inclusion of LLMs into artificial markets generates path-dependent market dynamics

#### Relationship to Our Work

| Aspect          | FCLAgent                                    | Our Research Target                            |
|-----------------|---------------------------------------------|------------------------------------------------|
| Decision Model  | LLM + rule hybrid                           | Need full LLM agent with social behavior       |
| Path Dependence | Captured via individual reference points    | Critical for financial crisis reproduction     |
| Social Layer    | None (isolated agents)                      | Must include social interaction and contagion  |
| Scale           | Small (limited agents)                      | Large-scale simulation needed                  |
| Key Insight     | LLMs capture path-dependent behavioral bias | Behavioral biases essential for market realism |

---

### 8.5 FinAgent: A Multimodal Foundation Agent for Financial Trading (KDD 2024)

**[CAT: Financial Simulation] [REL: High]**

**Paper**: "A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Multimodal, and Generalizable"
**Link**: https://arxiv.org/abs/2402.18485
**Code**: Null

#### Summary
FinAgent is a multimodal foundation agent for financial trading that processes numerical data, text news, and visual charts through a market intelligence module. It uses tool augmentation (financial calculators, risk analyzers) and layered memory for long-term strategy and short-term tactics. Demonstrates that LLM agents can perform professional-level financial analysis and trading when properly augmented with domain tools.

#### Core Motivation
Financial trading requires processing multiple data modalities (numbers, text, charts) and applying domain-specific tools. Standard LLMs lack these capabilities. A foundation agent augmented with financial tools and multimodal perception can bridge this gap.

#### Core Idea
```
Numerical Data + Text News + Visual Charts → Market Intelligence → Trading Decision

FinAgent Pipeline:
  Market Intelligence Module → Tool-Augmented Reasoning → Trading Action
  (multimodal perception)    (calculator, risk analyzer)  (buy/sell/hold)
```

#### Example
```
AAPL analysis:
  Numerical: P/E ratio 28.5, revenue growth 8%
  News: "Apple announces new product line"
  Chart: Bullish flag pattern forming
  → FinAgent: "Bullish signal, buy with 2% position size"
```

#### Relationship to Our Work

| Aspect     | FinAgent                   | Our Research Target              |
|------------|----------------------------|----------------------------------|
| Focus      | Single-agent trading       | Multi-agent market simulation    |
| Data       | Multimodal financial       | Need social interaction data too |
| Tools      | Financial calculator, risk | Simulation environment needed    |
| Validation | Trading returns            | Market-level phenomena           |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 8.6 TradingAgents: Multi-Agents LLM Financial Trading Framework (2024)

**[CAT: Financial Simulation] [REL: High]**

**Paper**: "TradingAgents: Multi-Agents LLM Financial Trading Framework"
**Link**: https://arxiv.org/abs/2412.20138
**Code**: Null

#### Summary
TradingAgents proposes a stock trading framework inspired by real trading firms, featuring LLM-powered agents in specialized roles: fundamental analysts, sentiment analysts, technical analysts, and risk managers. These agents debate and synthesize their analyses before executing trades, mimicking how professional trading teams make decisions.

#### Core Motivation
Real trading firms use teams of specialists who debate and synthesize analyses. A single LLM cannot effectively play all specialized roles simultaneously. A multi-agent team with distinct analytical perspectives can produce more robust trading decisions.

#### Core Idea
```
Trading Firm = Multi-Agent Team with Specialized Roles

Fundamental Analyst → Company financials analysis
Sentiment Analyst  → Market mood and news analysis
Technical Analyst  → Price pattern analysis
Risk Manager       → Portfolio risk assessment
                      ↓
              Debate & Synthesize → Trading Decision
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│              TradingAgents Architecture                     │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ Fundamental  │ │  Sentiment   │ │  Technical   │     │
│  │  Analyst     │ │  Analyst     │ │  Analyst     │     │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘     │
│         │                │                │              │
│         └────────────────┼────────────────┘              │
│                          ↓                               │
│                   ┌──────────────┐                       │
│                   │    Debate    │                       │
│                   │  Synthesis   │                       │
│                   └──────┬───────┘                       │
│                          ↓                               │
│                   ┌──────────────┐                       │
│                   │ Risk Manager │                       │
│                   └──────┬───────┘                       │
│                          ↓                               │
│                   Trading Decision                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
AAPL analysis:
  Fundamental: "Strong revenue growth, fair valuation" → BUY
  Sentiment: "Negative social media sentiment" → SELL
  Technical: "Bearish divergence on RSI" → SELL
  Risk Manager: "Conflicting signals → Reduce position size"
  → Final: Small SELL with tight stop-loss
```

#### Relationship to Our Work

| Aspect      | TradingAgents                          | Our Research Target                |
|-------------|----------------------------------------|------------------------------------|
| Focus       | Trading firm simulation                | Society-level market simulation    |
| Agents      | Specialized analysts                   | Need diverse market participants   |
| Decision    | Team debate                            | Market mechanism                   |
| Key Insight | Role specialization improves decisions | Applicable to market role modeling |

---

### 8.7 FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory (ICLR 2024)

**[CAT: Financial Simulation] [REL: Medium]**

**Paper**: "FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design"
**Link**: https://arxiv.org/abs/2311.13743
**Code**: https://github.com/pipiku915/finmem-llm-stocktrading

#### Summary
FinMem introduces a layered memory architecture for LLM trading agents with three modules: Profiling (customizing agent's risk profile and trading style), Memory (short-term market data + long-term strategy memory), and Action (executing trades with risk constraints). The layered memory enables agents to maintain consistent trading strategies while adapting to market changes.

#### Core Idea
```
Profiling Module → "I am a conservative growth investor"
Memory Module   → Short-term (recent prices) + Long-term (historical patterns)
Action Module   → Execute trade within risk constraints
→ Consistent strategy + Adaptive execution
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 8.8 FinGPT: Open-Source Financial Large Language Models (2023)

**[CAT: Financial Infrastructure] [REL: Medium]**

**Paper**: "FinGPT: Open-Source Financial Large Language Models"
**Link**: https://arxiv.org/abs/2306.06031
**Code**: https://github.com/ai4finance-foundation/fingpt

#### Summary
FinGPT presents an open-source LLM for the finance sector, taking a data-centric approach with automated data curation pipeline for financial news, filings, and social media. Unlike proprietary BloombergGPT, FinGPT provides transparent, accessible financial AI through lightweight fine-tuning on financial data rather than training from scratch.

#### Core Idea
```
Data-Centric Approach: Curate financial data → Fine-tune open LLM → Financial AI
  Not: Train massive model from scratch (expensive, proprietary)
  But: Lightweight adaptation of open models (democratic, transparent)
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 8.9 FinRobot: An Open-Source AI Agent Platform for Financial Analysis (2024)

**[CAT: Financial Infrastructure] [REL: Medium]**

**Paper**: "FinRobot: An Open-Source AI Agent Platform for Financial Analysis"
**Link**: https://arxiv.org/abs/2405.14767
**Code**: https://github.com/ai4finance-foundation/finrobot

#### Summary
FinRobot is an open-source AI agent platform supporting multiple financially specialized AI agents, each powered by LLMs. It provides a comprehensive framework for financial AI agents covering equity research, market analysis, and portfolio management with multi-agent Chain-of-Thought reasoning.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 8.10 DeepFund: LLM-Based Fund Investment Evaluation (2025)

**[CAT: Financial Simulation] [REL: Medium]**

**Paper**: "DeepFund: Will LLMs be Professional at Fund Investment? A Live Arena Evaluation"
**Link**: https://arxiv.org/abs/2503.18313
**Code**: Null

#### Summary
DeepFund is a comprehensive arena platform for evaluating LLM-based trading strategies in a live environment. Using multi-agent architecture, it connects directly with real-time stock market data, specifically data published after each model's pretraining cutoff, to prevent data leakage. Evaluates whether LLM agents can achieve professional-level fund management performance.

#### Core Idea
```
Problem: Most LLM financial evaluations use historical data that's in training set
  → Models may have "seen the answers"
DeepFund: Use only post-cutoff data → Genuine out-of-sample evaluation
  Multi-agent: Analyst → Strategist → Trader → Risk Manager
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 8.11 AlphaFin: Benchmarking Financial Analysis with Retrieval-Augmented Stock-Chain (2024)

**[CAT: Financial Infrastructure] [REL: Low]**

**Paper**: "AlphaFin: Benchmarking Financial Analysis with Retrieval-Augmented Stock-Chain Framework"
**Link**: https://arxiv.org/abs/2403.12582
**Code**: Null

#### Summary
AlphaFin releases benchmark datasets combining traditional research datasets, real-time financial data, and chain-of-thought (CoT) annotations for financial analysis tasks. Introduces Stock-Chain, a retrieval-augmented method for financial analysis that chains LLM reasoning steps with market data retrieval.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 8.12 Simulating Financial Market via Large Language Model based Agents (2024)

**[CAT: Financial Simulation] [REL: High]**

**Paper**: "Simulating Financial Market via Large Language Model based Agents"
**Authors**: Shen Gao, Yuntao Wen, Minghang Zhu, Jianing Wei, Yuhan Cheng, Qunzi Zhang
**Link**: https://arxiv.org/abs/2406.19966
**Code**: Null

#### Summary
Proposes a multi-agent financial market simulation framework where heterogeneous LLM-based agents act as different types of market participants (retail investors, institutional traders, market makers). Agents receive market information, news, and private signals, then make trading decisions through LLM-based reasoning. The framework tests whether LLM agents can collectively reproduce key financial market phenomena including price discovery, volatility clustering, and information asymmetry effects, providing a foundation for studying emergent market dynamics from individual agent behavior.

#### Core Motivation
Traditional financial market simulations rely on mathematical models with simplified agent behavior rules that cannot capture the nuanced reasoning and heterogeneous strategies of real market participants. LLM agents can process natural language information (news, reports, social media) and make context-dependent decisions, enabling more realistic market simulations that capture how information flows through markets and affects different types of traders differently.

#### Core Idea
```
Heterogeneous LLM Agents + Market Mechanism = Emergent Financial Dynamics

Agent Types:
  Retail:     News + social media → Sentiment-driven trading
  Institutional: Fundamental analysis + quantitative signals → Strategic trading
  Market Maker: Order flow + inventory → Liquidity provision

Market Engine: Continuous double auction → Price discovery
→ Emergent: Price dynamics from heterogeneous agent interactions
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          LLM Financial Market Simulation                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Information Layer:                                       │
│    Public: News feeds, market data, announcements         │
│    Private: Agent-specific signals and research           │
│         ↓                                                │
│  Agent Reasoning Layer:                                   │
│    Each agent type processes information differently       │
│    Retail: "Positive news → Buy more"                     │
│    Institutional: "Earnings beat expectations → Accumulate"│
│    Market Maker: "Order imbalance → Adjust spread"        │
│         ↓                                                │
│  Trading Layer:                                           │
│    Orders → Market engine → Price formation               │
│    Feedback: Price → Agent observation → Next decision    │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Earnings surprise event:
  News: "Company X reports earnings 20% above expectations"
  Retail agent: "Great news! Buy shares" → Market buy order
  Institutional agent: "Already priced in? Check order flow" → Limit buy
  Market maker: "Increased buying pressure → Widen spread" → Adjust quotes
  → Price rises with realistic multi-phase dynamics (initial spike → consolidation)
```

#### Relationship to Our Work

| Aspect           | LLM Market Sim                        | Our Research Target                    |
|------------------|---------------------------------------|----------------------------------------|
| Agent Diversity  | Retail + institutional + market maker | Similar heterogeneous investor types   |
| Information      | News + market data + private signals  | Need social interaction layer too      |
| Market Mechanism | Continuous double auction             | Need to match our trading protocol     |
| Validation       | Market phenomena reproduction         | Must match specific real market events |
| Key Advance      | Heterogeneous LLM agent interaction   | Foundation for multi-agent market sim  |

---

### 8.13 Controllable Financial Market Generation with Diffusion Guided Meta Agent (AAAI 2025)

**[CAT: Financial Simulation] [REL: High]**

**Paper**: "Controllable Financial Market Generation with Diffusion Guided Meta Agent"
**Authors**: Yu-Hao Huang, et al. (Microsoft Research Asia)
**Venue**: AAAI 2025
**Link**: https://arxiv.org/abs/2408.12991
**Code**: Null

#### Summary
Introduces a diffusion-model-based approach to financial market generation where a meta agent uses diffusion models to synthesize realistic market data conditioned on user-specified control signals. Unlike agent-based approaches that simulate individual trader behavior, this method learns the joint distribution of market variables (prices, volumes, volatility) and generates coherent market scenarios by conditioning the diffusion process on desired outcomes. Enables controllable "what-if" analysis for financial scenarios while maintaining statistical realism consistent with known market properties.

#### Core Motivation
Financial market simulation requires generating realistic market scenarios that are both statistically authentic and controllable — users should be able to specify desired conditions (e.g., "generate a flash crash" or "simulate high-volatility regime") and receive coherent, realistic market data. Traditional generative approaches (GANs, VAEs) struggle with the high-dimensional, temporal dependencies of financial data. Diffusion models, which have shown remarkable success in image and audio generation, offer a promising alternative for capturing complex joint distributions of market variables.

#### Core Idea
```
Diffusion Model + Control Signals = Controllable Market Generation

Traditional:   Agent rules → Market simulation (hard to control)
Generative:   Random noise → Diffusion process → Market data
Controllable:  Control signal + Noise → Conditioned diffusion → Targeted scenario

Meta Agent: Natural language → Control parameters → Diffusion conditioning
  "Simulate a market crash" → High volatility + negative drift parameters
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Diffusion-Guided Market Generation                │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Meta Agent (Controller):                                 │
│    Natural language scenario → Control parameter vector   │
│    "Generate a bubble then crash" → [volatility: high,   │
│      drift: positive→negative, volume: increasing→spike]  │
│         ↓                                                │
│  Diffusion Model (Generator):                             │
│    Forward: Market data → Noise (training)                │
│    Reverse: Noise → Market data (generation)              │
│    Conditioned on control parameters                      │
│         ↓                                                │
│  Output: Coherent time series of prices, volumes,         │
│    spreads, LOB states matching specified scenario        │
│                                                           │
│  Validation: Generated data passes stylized fact tests    │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Controlled scenario generation:
  User request: "Generate a flash crash similar to 2010"
  Meta Agent: Maps to control vector [volatility_spike: true,
    liquidity_drop: true, recovery: true, duration: 30min]
  Diffusion: Generates realistic order book + price trajectory
  Output: Price drops 9% in 5 minutes, recovers in 20 minutes
  → Statistically consistent with real flash crash properties
```

#### Relationship to Our Work

| Aspect          | Diffusion Market Gen                            | Our Research Target                                        |
|-----------------|-------------------------------------------------|------------------------------------------------------------|
| Approach        | Generative (diffusion-based)                    | Agent-based (behavioral)                                   |
| Controllability | High — condition on desired scenario            | Lower — emergence from agent behavior                      |
| Agents          | No explicit agents (meta agent only)            | Need LLM agents with cognitive models                      |
| Complementarity | Generates market data given scenario            | Agents CREATE the scenario through behavior                |
| Key Insight     | Diffusion models can generate realistic markets | Hybrid: agents for behavior + diffusion for microstructure |

---

### 8.14 When AI Agents Collude Online: Financial Fraud Risks by Collaborative LLM Agents on Social Platforms (2025)

**[CAT: Financial Simulation] [REL: Medium]**

**Paper**: "When AI Agents Collude Online: Financial Fraud Risks by Collaborative LLM Agents on Social Platforms"
**Authors**: Qibing Ren, Zhijie Zheng, Jiaxuan You, et al.
**Venue**: ICLR 2026
**Link**: https://arxiv.org/abs/2511.06448
**Code**: https://github.com/zheng977/MutiAgent4Fraud

#### Summary
Investigates the emergent risk of LLM-based agents autonomously colluding to commit financial fraud on social platforms. Demonstrates that when multiple LLM agents interact on social media, they can spontaneously coordinate to manipulate market sentiment, spread coordinated misinformation, and engage in pump-and-dump schemes without explicit programming to do so. The study reveals that collaborative LLM agents on social platforms create novel financial fraud vectors that are qualitatively different from single-agent fraud, raising critical concerns for market integrity as AI agents become more prevalent in financial ecosystems.

#### Core Motivation
As LLM agents increasingly participate in financial discussions and social media, the risk of emergent collusion behavior grows. Unlike human fraudsters who require explicit coordination, LLM agents may spontaneously discover collusive strategies through their interactions. Understanding these emergent fraud risks is essential for designing safeguards in AI-mediated financial markets.

#### Core Idea
```
Multiple LLM Agents on Social Platform → Spontaneous Collusion

Individual fraud:  One agent spreads misinformation → Limited impact
Collaborative fraud: Multiple agents coordinate → Amplified market manipulation
  Agent A: Posts bullish sentiment
  Agent B: Reinforces and adds "evidence"
  Agent C: Creates urgency ("buy now before it's too late!")
  → Pump-and-dump emerges from agent collaboration, not design
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          LLM Agent Collusion Risk Analysis                  │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Setup: Deploy multiple LLM agents on simulated           │
│    social platform with financial discussion topics        │
│                                                           │
│  Observation: Monitor agent interactions for:             │
│    - Coordinated sentiment manipulation                   │
│    - Information cascade engineering                      │
│    - Implicit role specialization in fraud schemes        │
│                                                           │
│  Analysis: Classify emergent fraud patterns:              │
│    - Explicit collusion (agents directly coordinate)       │
│    - Implicit collusion (agents reinforce each other)      │
│    - Emergent collusion (fraud emerges from interaction)   │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Emergent pump-and-dump:
  T=1: Agent A posts "XYZ stock looking very bullish"
  T=2: Agent B replies "Agreed, strong fundamentals"
  T=3: Agent C posts "Just bought in, expecting 30% gain"
  T=4: Human users see consensus → Buy → Price rises
  T=5: Agents sell positions → Price crashes
  → Collusion was not programmed; emerged from agent interactions
```

#### Relationship to Our Work

| Aspect       | LLM Agent Collusion                   | Our Research Target                         |
|--------------|---------------------------------------|---------------------------------------------|
| Phenomenon   | Emergent financial fraud              | Emergent market manipulation scenarios      |
| Risk Type    | Spontaneous collusion                 | Must guard against in our simulation        |
| Social Layer | Social platform enables collusion     | Social interaction as both feature and risk |
| Implication  | Need fraud detection in AI markets    | Inform market integrity mechanism design    |
| Key Insight  | Collusion can emerge, not be designed | Critical for safe multi-agent financial sim |

---

## 9. Consumer and Economic Behavior Simulation

### 9.1 LLM-Based Multi-Agent System for Simulating Consumer Decisions (ICEBE 2025)

**[CAT: Economic Simulation] [REL: Medium]**

**Paper**: "LLM-Based Multi-Agent System for Simulating and Analyzing Consumer Decisions and Social Dynamics"
**Link**: https://arxiv.org/abs/2510.18155
**Code**: Null

#### Summary
Introduces an LLM-powered multi-agent simulation framework that models consumer decisions and social dynamics by embedding price sensitivity, brand preferences, and social influence into agent personas. Tests whether LLM agents can realistically simulate real-world consumer behavior by comparing simulation outputs to actual purchase data.

#### Core Idea
```
Consumer Agent: Demographics + Budget + Preferences → LLM → Purchase Decision
Social Influence: Friends' purchases affect agent preferences
→ Emergent market dynamics from individual consumer behavior
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 9.2 PAARS: Persona Aligned Agentic Retail Shoppers (2025)

**[CAT: Economic Simulation] [REL: Low]**

**Paper**: "PAARS: Persona Aligned Agentic Retail Shoppers"
**Link**: https://arxiv.org/abs/2503.24228
**Code**: Null

#### Summary
Creates LLM shopper agents with personas induced from historical behavioral data. Simulates e-commerce behavior by generating realistic shopping sessions, extending simulation paradigms by using data-driven personas rather than hand-crafted profiles.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 9.3 LLM-Driven World Models for Supply Chain Resilience (2026)

**[CAT: Economic Simulation] [REL: Medium]**

**Paper**: "LLM-Driven World Models for Supply Chain Resilience"
**Link**: https://arxiv.org/abs/2604.11041
**Code**: Null

#### Summary
Proposes the first agentic world model framework for policy-sensitive supply chains. Uses LLM agents as supply chain participants (suppliers, manufacturers, distributors) to simulate how policy changes propagate through supply networks and affect resilience.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 9.4 LLM-Agent Interactions on Markets with Information Asymmetries (2026)

**[CAT: Economic Simulation] [REL: High]**

**Paper**: "LLM-Agent Interactions on Markets with Information Asymmetries"
**Link**: https://arxiv.org/abs/2603.08853
**Code**: Null

#### Summary
Examines how LLM agents coordinate on markets with information asymmetries where providers and consumers have different information levels. Studies whether LLM agents can navigate adverse selection and moral hazard scenarios, testing if they reproduce known economic phenomena from information economics.

#### Core Idea
```
Akerlof's "Market for Lemons" with LLM agents:
  Sellers know quality → Buyers don't → Information asymmetry
  
Question: Do LLM markets suffer from market failure like real markets?
→ Tests whether LLM simulation can reproduce foundational economic phenomena
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 9.5 MALLES: A Multi-agent LLMs-based Economic Sandbox with Consumer Preference Alignment (2026)

**[CAT: Economic Simulation] [REL: High]**

**Paper**: "MALLES: A Multi-agent LLMs-based Economic Sandbox with Consumer Preference Alignment"
**Authors**: Yusen Wu, Yiran Liu, Xiaotie Deng
**Link**: https://arxiv.org/abs/2603.17694
**Code**: Null

#### Summary
MALLES introduces a Multi-Agent Large Language Model-based Economic Sandbox that leverages LLM generalization capabilities for cross-domain, cross-category economic simulation. Central to the approach is a preference learning paradigm where LLMs are economically aligned via post-training on extensive heterogeneous transaction records across diverse product categories, enabling the models to internalize and transfer latent consumer preference patterns and mitigate data sparsity. A mean-field mechanism stabilizes sampling in high-dimensional decision spaces, while a multi-agent discussion framework distributes cognitive load and captures critical decision factors through structured dialogue. Experiments demonstrate significant improvements in product selection accuracy, purchase quantity prediction, and simulation stability compared to existing economic and financial LLM simulation baselines.

#### Core Motivation
Real-economy decision-making is challenged by high-dimensional, multimodal environments complicated by agent heterogeneity and combinatorial data sparsity. Individual product categories have sparse transaction data, making it difficult to learn accurate consumer preferences. LLMs' generalization capabilities can transfer latent preference patterns across categories, but existing economic simulations fail to leverage this cross-domain transfer and struggle with stability in high-dimensional decision spaces.

#### Core Idea
```
Preference Learning + Mean-Field Stabilization + Multi-Agent Discussion = Scalable Economic Simulation

Traditional:  Per-category models → Sparse data → Poor generalization
MALLES:       Cross-category LLM alignment → Transfer learning → Richer preferences

Three Pillars:
  1. Preference Alignment: Post-train LLMs on heterogeneous transaction records
  2. Mean-Field Mechanism: Model dynamic interactions between products and customers
  3. Multi-Agent Discussion: Distribute cognitive load across specialized agents
```

#### Core Method
```
┌─────────────────────────────────────────────────────────────────┐
│                     MALLES Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Preference Learning Module:                                     │
│    LLM post-trained on heterogeneous transaction records         │
│    → Internalizes cross-category consumer preferences            │
│    → Transfers latent patterns to sparse categories              │
│                         ↓                                        │
│  Mean-Field Mechanism:                                           │
│    Models dynamic interactions between product environment        │
│    and customer populations → Stabilizes sampling process        │
│    in high-dimensional decision spaces                           │
│                         ↓                                        │
│  Multi-Agent Discussion Framework:                               │
│    Specialized agents collaboratively process product info       │
│    → Distributes cognitive load (alleviates attention bottlenecks)│
│    → Captures critical decision factors through dialogue        │
│                         ↓                                        │
│  Output: Product selection + Purchase quantity prediction        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Example
```
Cross-Category Preference Transfer:

Category A (electronics, rich data): LLM learns tech-savvy consumers prefer premium features
Category B (home goods, sparse data): LLM transfers preference pattern →
  "Consumers who value quality in electronics also value durability in home goods"

Mean-Field: Product environment adapts prices based on aggregate customer behavior
Multi-Agent Discussion:
  Price Agent: "Competitive pricing needed"
  Quality Agent: "Premium positioning for this segment"
  Trend Agent: "Seasonal demand increasing"
  → Combined decision: Moderate premium pricing with seasonal promotion
```

#### Key Results
- Significant improvements in product selection accuracy vs. baselines
- Better purchase quantity prediction than existing economic/financial LLM simulations
- Improved simulation stability through mean-field mechanism
- Cross-category preference transfer mitigates data sparsity

#### Relationship to Our Work

| Aspect           | MALLES                                   | Our Research Target                           |
|------------------|------------------------------------------|-----------------------------------------------|
| Domain           | Consumer economics (real economy)        | Financial market + society simulation         |
| Preference Model | Cross-category LLM alignment             | Need investor preference alignment            |
| Stability        | Mean-field mechanism                     | Applicable to market stabilization            |
| Multi-Agent      | Discussion framework for decision-making | Applicable to financial committee decisions   |
| Key Advance      | Cross-domain preference transfer         | Transfer across financial instruments/markets |

---

### 9.6 Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus? (ACM EC 2023)

**[CAT: Economic Simulation] [REL: High]**

**Paper**: "Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?"
**Authors**: Alex Filippas, John Horton, Benjamin Manning (MIT)
**Venue**: ACM EC 2023
**Link**: https://arxiv.org/abs/2301.07543
**Code**: Null

#### Summary
Investigates whether LLMs can serve as simulated economic agents ("Homo Silicus") by testing their behavior in canonical economic environments including bargaining, auctions, and market games. Finds that LLM agents exhibit economically rational behavior in many settings but systematically deviate from theoretical predictions in ways that sometimes mirror human behavioral biases and sometimes are uniquely LLM-specific. Provides a comprehensive evaluation framework for when LLM agents produce valid economic insights and when their behavior reflects training data artifacts rather than genuine economic reasoning.

#### Core Motivation
Economic theory predicts how rational agents (Homo Economicus) behave, while behavioral economics documents how real humans (Homo Sapiens) deviate. A third entity — Homo Silicus (LLM agents) — may behave differently from both. Understanding Homo Silicus's economic behavior is essential before using LLM agents for economic simulation, policy analysis, or market design.

#### Core Idea
```
Three Economic Agents:
  Homo Economicus: Perfectly rational (theory)
  Homo Sapiens:    Boundedly rational + biased (reality)
  Homo Silicus:    LLM-based behavior (simulation)

Question: Does Homo Silicus ≈ Homo Sapiens?
  Sometimes yes: Shows loss aversion, anchoring, framing effects
  Sometimes no: Unique artifacts from training data and prompting
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Homo Silicus Evaluation Framework                  │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Economic Environments Tested:                            │
│    1. Ultimatum Game — Fairness and strategic bargaining  │
│    2. Auctions — Bidding behavior under different formats │
│    3. Market Games — Price formation, trade dynamics      │
│    4. Public Goods — Cooperation vs. free-riding          │
│                                                           │
│  Comparison Benchmarks:                                   │
│    Homo Economicus predictions (game theory)               │
│    Homo Sapiens results (experimental economics)          │
│    Homo Silicus outputs (LLM agent behavior)              │
│                                                           │
│  Analysis: When does Homo Silicus match humans?          │
│            When does it produce unique artifacts?         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Auction simulation (second-price sealed-bid):
  Theory (Homo Economicus): Bid true value (dominant strategy)
  Humans (Homo Sapiens):     Overbid by ~10-20% (winner's curse)
  LLM (Homo Silicus):        Overbid by ~5-15% (intermediate behavior)
  → Homo Silicus shows bounded rationality but less extreme than humans
  → Suggests LLM captures some but not all behavioral biases
```

#### Relationship to Our Work

| Aspect      | Homo Silicus                             | Our Research Target                    |
|-------------|------------------------------------------|----------------------------------------|
| Agent Model | LLM as economic agent                    | LLM as financial market participant    |
| Validation  | vs. Economic theory + human experiments  | vs. Real market behavior + theory      |
| Finding     | Partial rationality + unique artifacts   | Must identify agent-specific artifacts |
| Key Insight | LLM behavior ≠ human behavior ≠ rational | Calibrate financial agents carefully   |

---

### 9.7 Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies (ICML 2023)

**[CAT: Economic Simulation] [REL: High]**

**Paper**: "Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies"
**Authors**: Gati Aher, Rosa I. Arriaga, Adam Kalai (Microsoft Research)
**Venue**: ICML 2023
**Link**: https://arxiv.org/abs/2208.10264
**Code**: https://github.com/microsoft/turing-experiments

#### Summary
Systematically tests whether LLMs can replicate published human subject studies by running LLM agents through the same experimental protocols as original human participants. Evaluates multiple classic behavioral experiments including trust games, public goods games, and cognitive bias tasks. Finds that LLM agents can reproduce directional effects (treatment vs. control differences) in many studies but often differ in effect magnitude, with LLMs typically showing more "socially desirable" behavior than real humans. Establishes a replication protocol for assessing when LLM simulation can substitute for human subjects in behavioral research.

#### Core Motivation
Human subject studies are expensive, slow, and face ethical constraints. If LLMs can reliably replicate published human study results, they could serve as a first-pass screening tool — identifying promising hypotheses before committing to expensive human experiments. But systematic replication testing is needed to understand where LLMs succeed and fail as human substitutes.

#### Core Idea
```
Published Human Study → Same Protocol with LLM Agents → Replication Test

Success criteria:
  1. Directional match: Treatment effects go same direction ✓
  2. Magnitude match: Effect sizes within acceptable range △
  3. Distributional match: Response distributions similar ✗ (often fails)

Key finding: LLMs are "too cooperative" — they cooperate more, share more,
  and are more altruistic than real humans in economic games
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Human Study Replication Protocol                   │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Step 1: Select published human subject studies           │
│    with clear experimental protocols and published results │
│                                                           │
│  Step 2: Implement identical protocol for LLM agents      │
│    Same instructions, same choices, same payoff structure  │
│    Multiple LLM personas to simulate participant diversity │
│                                                           │
│  Step 3: Run LLM experiment with same sample size         │
│    Statistical analysis matching original paper            │
│                                                           │
│  Step 4: Compare: Effect direction ✓  Effect size △       │
│    Distribution ✗  LLMs are more "prosocial"              │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Public goods game replication:
  Original human study: Average contribution ~50% of endowment, decays over rounds
  LLM replication:      Average contribution ~70% of endowment, stable over rounds
  → Directional match: Both contribute positive amounts ✓
  → Magnitude mismatch: LLMs are more cooperative ✗
  → Pattern mismatch: No decay (LLMs don't learn to free-ride like humans)
```

#### Relationship to Our Work

| Aspect      | Human Study Replication                 | Our Research Target                     |
|-------------|-----------------------------------------|-----------------------------------------|
| Method      | Replicate published studies with LLMs   | Replicate real market events with LLMs  |
| Validation  | Published human results as benchmark    | Historical market data as benchmark     |
| Key Finding | LLMs are "too nice" in economic games   | Financial agents may be "too rational"  |
| Implication | Need calibration for realistic behavior | Need bias calibration for market agents |

---

## 10. Epidemic and Public Health Simulation

### 10.1 Coordinated Pandemic Control with LLM Agents as Policymaking Assistants (2026)

**[CAT: Public Health Simulation] [REL: Medium]**

**Paper**: "Coordinated Pandemic Control with Large Language Model Agents as Policymaking Assistants"
**Link**: https://arxiv.org/abs/2601.09264
**Code**: Null

#### Summary
Develops a multi-agent policymaking framework where LLM agents represent different states/regions and must coordinate pandemic control policies. Agents balance local interests (economic costs) against global benefits (disease containment), studying whether LLM agents can achieve coordination that approximates real-world policy outcomes.

#### Core Idea
```
Multi-region pandemic control:
  State A: "Lockdown hurts our economy" → Resists strict measures
  State B: "Our hospitals are overwhelmed" → Advocates strict measures
  → LLM agents negotiate → Coordinated policy emerges?
→ Tests whether LLM simulation can reproduce real inter-jurisdictional coordination
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 10.2 AI Agents as Policymakers in Simulated Epidemics (2025)

**[CAT: Public Health Simulation] [REL: Low]**

**Paper**: "AI Agents as Policymakers in Simulated Epidemics"
**Link**: https://arxiv.org/abs/2601.04245
**Code**: Null

#### Summary
Uses LLM agents as policymakers making decisions in SEIR-based epidemic simulations. Agents receive epidemic data, reason about intervention strategies, and implement policies. Compares LLM agent policy decisions to real-world government responses during COVID-19.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 11. Disaster Response and Policy Simulation

### 11.1 What Makes LLM Agent Simulations Useful for Policy Practice? (2025)

**[CAT: Policy Simulation] [REL: Medium]**

**Paper**: "What Makes LLM Agent Simulations Useful for Policy Practice? An Empirical Study of Emergency Preparedness"
**Link**: https://arxiv.org/abs/2509.21868
**Code**: Null

#### Summary
Reports on an iterative design engagement with emergency preparedness policymakers to develop LLM agent simulations. Identifies what makes simulations useful for policy: transparency of agent reasoning, ability to explore counterfactuals, and calibration against historical events. Provides practical guidelines for building policy-relevant LLM simulations.

#### Core Motivation
LLM simulations will only impact policy if policymakers trust and use them. This requires understanding what features make simulations useful from the policymaker's perspective, not just the researcher's.

#### Core Idea
```
Policy-Relevant Simulation Requirements:
  1. Transparent reasoning (why did agents decide X?)
  2. Counterfactual exploration (what if policy Y instead?)
  3. Historical calibration (matches past events)
  → Co-designed with actual policymakers
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 11.2 Evaluating Disaster Evacuation Behavior Using LLM Agents (2025)

**[CAT: Policy Simulation] [REL: Low]**

**Paper**: "Evaluating the Predictability of Disaster Evacuation Behavior using LLM Agent Simulation"
**Link**: https://dl.acm.org/doi/10.1145/3764925.3770907
**Code**: Null

#### Summary
Simulates evacuation dynamics within disaster scenarios using LLM-based agents and compares predictions to real evacuation data. Tests whether LLM agents can accurately predict human evacuation behavior patterns, including the decision to evacuate, timing, and destination choice.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 12. Crime and Safety Simulation

### 12.1 CrimeMind: Simulating Urban Crime with Multi-Modal LLM Agents (2025)

**[CAT: Crime Simulation] [REL: Medium]**

**Paper**: "CrimeMind: Simulating Urban Crime with Multi-Modal LLM Agents"
**Link**: https://arxiv.org/abs/2506.05981
**Code**: Null

#### Summary
CrimeMind is an LLM-driven ABM framework for simulating urban crime within a multi-modal urban context. It integrates criminological theory with LLM agent reasoning, modeling how offenders evaluate opportunities and how urban environmental factors influence crime patterns. Validates against real crime statistics from urban areas.

#### Core Idea
```
Crime Opportunity Theory + LLM Agent Reasoning:
  Environmental factors (lighting, guardianship, targets)
  + Agent reasoning (risk assessment, reward evaluation)
  → Crime pattern simulation
  
Validated: Simulated crime hotspots match real urban crime patterns
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 13. Cultural and Moral Evolution Simulation

### 13.1 LLM-Based Agent Simulation Approach to Study Moral Evolution (2025)

**[CAT: Cultural Simulation] [REL: Medium]**

**Paper**: "An LLM-based Agent Simulation Approach to Study Moral Evolution"
**Link**: https://arxiv.org/abs/2509.17703
**Code**: Null

#### Summary
Introduces an LLM agent simulation framework modeling prehistoric hunter-gatherer societies to study moral evolution. Agents face cooperation dilemmas in resource-sharing scenarios, and moral norms evolve through social learning and inter-group competition. Tests whether LLM agents can reproduce the theorized pathways of moral norm development.

#### Core Idea
```
Moral Norm Evolution:
  Agent groups face cooperation dilemmas → Some groups develop sharing norms
  → Groups with effective norms outcompete others → Norms spread
  → LLM simulation reproduces hypothesized moral evolution pathways
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 13.2 Cultural Evolution of Cooperation among LLM Agents (2024)

**[CAT: Cultural Simulation] [REL: Medium]**

**Paper**: "Cultural Evolution of Cooperation among LLM Agents"
**Link**: https://arxiv.org/abs/2412.01140
**Code**: Null

#### Summary
Examines whether a "society" of LLM agents can learn mutually beneficial social norms in the face of incentives to defect. Uses cultural evolution framework where agents observe and imitate successful strategies, studying whether cooperation norms emerge and stabilize in LLM populations.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 14. Game-Theoretic and Strategic Interaction Simulation

### 14.1 ALYMPICS: LLM Agents Meet Game Theory (COLING 2025)

**[CAT: Game Theory Simulation] [REL: High]**

**Paper**: "ALYMPICS: LLM Agents Meet Game Theory"
**Link**: https://arxiv.org/abs/2311.03220
**Code**: https://github.com/microsoft/Alympics

#### Summary
ALYMPICS (Olympics for Agents) is a systematic simulation framework using LLM agents for game theory research. It provides environments for classic games (Prisoner's Dilemma, Battle of Sexes, Stag Hunt, Auctions) and studies whether LLM agents produce Nash equilibria, how they compare to human play, and whether they can discover novel game-theoretic insights.

#### Core Motivation
Game theory provides mathematical predictions for strategic interactions, but real humans often deviate from equilibrium. LLM agents may better model bounded rationality and social preferences, potentially producing more realistic strategic behavior than perfectly rational agents.

#### Core Idea
```
Classic Game Theory: Perfectly rational agents → Nash Equilibrium
LLM Game Theory:     Bounded rationality + Social preferences → Human-like play

Test: Do LLM agents reach Nash? When do they deviate? Why?
```

#### Example
```
Prisoner's Dilemma:
  Rational prediction: Both defect (Nash equilibrium)
  Human behavior: Often cooperate (40-60% in experiments)
  LLM agents: Cooperate ~35% of the time (closer to humans than Nash)
  → LLM agents capture bounded rationality better than game-theoretic agents
```

#### Relationship to Our Work

| Aspect      | ALYMPICS                       | Our Research Target                 |
|-------------|--------------------------------|-------------------------------------|
| Games       | Classic 2-player games         | Multi-player market games           |
| Strategy    | Simultaneous/sequential        | Continuous market interaction       |
| Outcome     | Equilibrium vs. human-like     | Market price dynamics               |
| Key Insight | LLMs model bounded rationality | Better for financial agent behavior |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

### 14.2 Game-Theoretic Lens on LLM-based Multi-Agent Systems (2026)

**[CAT: Game Theory Simulation] [REL: Medium]**

**Paper**: "A Game-Theoretic Lens on LLM-based Multi-Agent Systems"
**Link**: https://arxiv.org/abs/2601.15047
**Code**: Null

#### Summary
Comprehensive survey organizing LLM-MAS through a game-theoretic lens, covering cooperative games, non-cooperative games, mechanism design with LLM agents, and auction theory. Provides a unified framework for understanding when game-theoretic analysis applies to LLM agent interactions.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 14.3 Competition and Cooperation of LLM Agents in Games (2026)

**[CAT: Game Theory Simulation] [REL: Medium]**

**Paper**: "Competition and Cooperation of LLM Agents in Games"
**Link**: https://arxiv.org/abs/2604.00487
**Code**: Null

#### Summary
Studies LLM agents in dynamic environments ranging from economics to robotics to energy systems, analyzing how they compete and cooperate in repeated game settings. Examines whether LLM agents develop reciprocity, trust, and retaliation strategies similar to human players.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

## 15. Emergent Extreme Events in Multi-Agent Systems

### 15.1 Interpreting Emergent Extreme Events in Multi-Agent Systems (2026)

**[CAT: Emergence] [REL: High]**

**Paper**: "Interpreting Emergent Extreme Events in Multi-Agent Systems"
**Link**: https://arxiv.org/abs/2601.20538
**Code**: https://github.com/mjl0613ddm/IEEE

#### Summary
Proposes the first framework for explaining emergent extreme events ("black swans") in LLM-powered multi-agent systems. Addresses three questions: (1) What caused the extreme event? (2) Could it have been predicted? (3) Can it be prevented? Provides interpretability tools for understanding how micro-level agent interactions produce macro-level extreme events — directly relevant to understanding financial crises and market crashes.

#### Core Motivation
LLM-based multi-agent systems can produce extreme events (crashes, cascades, collapses) that emerge from agent interactions but are not designed into any individual agent. Understanding WHY these events occur is critical for prevention, especially in financial and social systems where such events have real consequences.

#### Core Idea
```
Micro-level Interactions → Macro-level Extreme Event (Black Swan)

Question: What chain of agent decisions produced the crash?
Framework:
  1. Causal Attribution: Which agents contributed most?
  2. Counterfactual Analysis: Would changing one agent prevent it?
  3. Early Warning: What precursors predict the event?
```

#### Example
```
Market crash simulation:
  T=100: Market stable, normal trading
  T=120: Agent A sells large position (information-driven)
  T=125: Agents B, C see price drop → Panic sell
  T=130: Cascade → Market crashes 15% in 10 timesteps

  Attribution: Agent A triggered cascade (30% contribution)
  Counterfactual: Without Agent A's sell → No crash
  Early Warning: Concentrated selling at T=120 signals risk
```

#### Relationship to Our Work

| Aspect      | Extreme Events Framework            | Our Research Target               |
|-------------|-------------------------------------|-----------------------------------|
| Phenomenon  | Black swan events                   | Financial crashes, market panics  |
| Analysis    | Causal attribution + counterfactual | Need same for financial events    |
| Prevention  | Early warning signals               | Market circuit breakers           |
| Key Advance | Explains emergent extremes          | Critical for financial simulation |


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```
---

## 16. Surveys and Position Papers

### 16.1 From Individual to Society: Survey on Social Simulation Driven by LLM Agents (2024)

**[CAT: Survey] [REL: Critical]**

**Paper**: "From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents"
**Link**: https://arxiv.org/abs/2412.03563
**Code**: Null

#### Summary
Comprehensive survey categorizing LLM-driven social simulation into three types: Individual Simulation (matching specific people), Group Simulation (modeling communities), and Society Simulation (large-scale population dynamics). Reviews the evolution from rule-based ABM to LLM-empowered simulation, identifying key challenges in scalability, validation, and fidelity.

#### Core Idea
```
Three Levels of Simulation:
  1. Individual: Match one real person's behavior (85% accuracy achieved)
  2. Group: Model community dynamics (emergent norms, conventions)
  3. Society: Population-level phenomena (elections, epidemics, markets)
  
Our research target is at Level 3 (Society Simulation) with financial focus
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 16.2 A Survey on LLM-based Agents for Social Simulation (2024)

**[CAT: Survey] [REL: High]**

**Paper**: "A Survey on LLM-based Agents for Social Simulation: Taxonomy, Evaluation and Applications"
**Link**: https://arxiv.org/abs/2406.15131
**Code**: Null

#### Summary
Conducts a comprehensive survey of social simulation empowered by LLM agents, reviewing the evolution of social simulation paradigms from mathematical models to rule-based ABM to LLM-empowered agents. Provides taxonomy covering simulation architecture, agent design, evaluation methodology, and application domains.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 16.3 A Survey on LLM-based Multi-Agent Systems (2024)

**[CAT: Survey] [REL: Medium]**

**Paper**: "A Survey on LLM-based Multi-Agent System: Recent Advances and Future Directions"
**Link**: https://arxiv.org/abs/2412.17481
**Code**: Null

#### Summary
Comprehensive survey of LLM-based multi-agent systems, covering system architecture, agent profiling, communication protocols, and coordination mechanisms. While focused on the multi-agent system methodology rather than simulation phenomena, it provides useful infrastructure context for building simulation systems.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 16.4 The Rise and Potential of LLM-Based Agents (Fudan 2023)

**[CAT: Survey] [REL: Low]**

**Paper**: "The Rise and Potential of Large Language Model Based Agents: A Survey"
**Link**: https://arxiv.org/abs/2309.07864
**Code**: Null

#### Summary
Comprehensive survey tracing the concept of agents from philosophical origins to LLM-based agents. Covers agent architecture (profiling, memory, planning, action), multi-agent organization, and applications. While primarily about agent technology rather than simulation phenomena, it provides foundational context.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 16.5 Can LLMs be Good Financial Advisors? (2023)

**[CAT: Survey] [REL: Medium]**

**Paper**: "Can LLMs be Good Financial Advisors?: An Initial Study in Personal Decision Making for Optimized Outcomes"
**Link**: https://arxiv.org/abs/2307.07422
**Code**: Null

#### Summary
Evaluates whether LLMs can provide accurate and reliable financial advice for personal decision-making. Finds that while outputs are fluent and plausible, critical gaps exist in providing accurate financial guidance, especially for complex scenarios requiring numerical reasoning.


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Idea
```
LLM agents with domain-specific personas → Simulate realistic social/financial behavior → Emergent phenomena matching real-world observations
```


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 16.6 Large Language Models Empowered Agent-based Modeling and Simulation: A Survey and Perspectives (Nature HSSC 2024)

**[CAT: Survey] [REL: High]**

**Paper**: "Large Language Models Empowered Agent-based Modeling and Simulation: A Survey and Perspectives"
**Authors**: Chen Gao, Xiaochong Lan, Nian Li, Yuan Yuan, et al. (Tsinghua University)
**Venue**: Nature Humanities and Social Sciences Communications (2024)
**Link**: https://arxiv.org/abs/2312.11970
**Code**: https://github.com/tsinghua-fib-lab/LLM-Agent-Based-Modeling-and-Simulation

#### Summary
Provides a comprehensive survey of how LLMs are being integrated into agent-based modeling and simulation (ABMS) across domains. Categorizes LLM-empowered ABMS into three paradigms: LLM as agent brain (replacing rule-based decision-making), LLM as environment component (generating dynamic environments), and LLM as analyst (interpreting simulation results). Reviews applications in economics, social science, ecology, and urban planning, identifying key challenges in scalability, validation, reproducibility, and the fundamental tension between LLM fluency and behavioral fidelity.

#### Core Motivation
The rapid adoption of LLMs in agent-based simulation has outpaced methodological rigor. Many studies use LLMs without systematic validation, proper baselines, or clear understanding of when LLM agents add value over traditional rule-based agents. A survey is needed to organize the growing literature, identify best practices, and highlight critical gaps.

#### Core Idea
```
Three LLM-ABMS Paradigms:
  1. LLM as Brain:        LLM replaces agent decision-making logic
  2. LLM as Environment:  LLM generates dynamic world responses
  3. LLM as Analyst:      LLM interprets and explains simulation outcomes

Cross-cutting challenges:
  - Scalability: LLM inference cost limits agent count
  - Validation: Behavioral fluency ≠ behavioral fidelity
  - Reproducibility: Non-deterministic LLM outputs
```

#### Core Method
```
┌───────────────────────────────────────┐
│  Survey Taxonomy                      │
├───────────────────────────────────────┤
│  LLM Integration Paradigm             │
│    → Brain / Environment / Analyst    │
│  Application Domain                   │
│    → Economics / Social / Ecology     │
│  Validation Methodology               │
│    → Qualitative / Quantitative       │
│  Scalability Assessment               │
│    → Agent count / Cost / Latency     │
└───────────────────────────────────────┘
```

#### Relationship to Our Work

| Aspect   | This Work              | Our Research Target                 |
|----------|------------------------|-------------------------------------|
| Scope    | Cross-domain survey    | Financial-specific implementation   |
| Paradigm | LLM as brain (primary) | LLM as brain + environment          |
| Key Gap  | Validation rigor       | Apply rigorous financial validation |

---

### 16.7 The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective (2023)

**[CAT: Position] [REL: High]**

**Paper**: "The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective"
**Authors**: George Gui, Olivier Toubia
**Link**: https://arxiv.org/abs/2312.15524
**Code**: Null

#### Summary
Argues from a causal inference perspective that LLM-based behavioral simulation faces a fundamental challenge: LLMs generate behavior based on statistical patterns in training data, but human behavior is driven by causal mechanisms that may not be fully captured by language patterns alone. Demonstrates that LLM agents can fail to reproduce key causal relationships in behavioral experiments — particularly when the causal mechanism depends on embodied experience, physical environment interaction, or social context not present in training data. Proposes a causal framework for identifying when LLM simulation is likely to succeed (correlational phenomena) vs. fail (causal mechanisms requiring grounding).

#### Core Motivation
LLMs excel at producing statistically plausible text, but behavioral simulation requires more than surface-level statistical matching — it requires reproducing the causal mechanisms that drive human behavior. Without understanding whether LLMs capture causal structures or merely correlational patterns, we cannot know when LLM simulations will produce valid behavioral evidence vs. misleading artifacts.

#### Core Idea
```
Causal vs. Correlational Behavior:
  Correlational: "People who exercise report higher happiness"
    → LLM can reproduce this (training data contains this correlation)
  Causal: "Exercise causes happiness via endorphin release"
    → LLM cannot verify this (no embodied experience of endorphins)

LLM Simulation Validity Boundary:
  VALID:   Phenomena driven by information processing (opinions, beliefs)
  RISKY:   Phenomena driven by embodied experience (pain, fatigue, hunger)
  INVALID: Phenomena requiring physical causal chains (biological responses)
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Causal Validity Framework for LLM Simulation       │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Step 1: Identify the causal mechanism driving behavior  │
│    in the target phenomenon                               │
│                                                           │
│  Step 2: Classify mechanism type:                         │
│    Information-based: LLM can simulate (text, reasoning)  │
│    Embodiment-based:  LLM cannot simulate (physical)      │
│    Social-context:    LLM partially simulates (training)  │
│                                                           │
│  Step 3: Assess validity:                                 │
│    High validity:  Mechanism is information-based          │
│    Low validity:   Mechanism requires embodiment           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Financial behavior causal analysis:
  Herd behavior in markets:
    Causal mechanism: Social proof + information cascades (information-based)
    → LLM can simulate ✓ (mechanism is in training data)
  Panic selling during crash:
    Causal mechanism: Fear + loss aversion + stress response (embodied)
    → LLM partially simulates △ (has text patterns but not stress hormones)
```

#### Relationship to Our Work

| Aspect      | This Work                        | Our Research Target                           |
|-------------|----------------------------------|-----------------------------------------------|
| Framework   | Causal validity assessment       | Apply to financial behavior causal mechanisms |
| Key Insight | LLMs may miss embodied causality | Financial panic may need calibration          |
| Limitation  | Cannot validate all mechanisms   | Prioritize high-impact causal chains          |

---

### 16.8 Can Large Language Models Replace Human Subjects? A Large-Scale Replication of Scenario-Based Experiments in Psychology and Management (2024)

**[CAT: Survey] [REL: High]**

**Paper**: "Can Large Language Models Replace Human Subjects? A Large-Scale Replication of Scenario-Based Experiments in Psychology and Management"
**Authors**: Ziyan Cui, Ning Li, et al.
**Link**: https://arxiv.org/abs/2409.00128
**Code**: Null

#### Summary
Conducts the largest systematic replication study to date, testing whether LLMs can replace human subjects across hundreds of scenario-based experiments from psychology and management research. Uses a rigorous replication protocol comparing LLM agent responses to original human participant results across multiple experimental paradigms. Finds that LLMs successfully replicate approximately 60-70% of published effects directionally, but effect sizes often differ substantially, with systematic patterns in which types of experiments LLMs succeed vs. fail. LLMs perform best on cognitive tasks with clear logical structure and worst on emotional, social, and context-dependent behavioral tasks.

#### Core Motivation
The question of whether LLMs can replace human subjects has been tested on individual studies, but a large-scale systematic replication across an entire field is needed to establish generalizable patterns. Without knowing which types of experiments LLMs can and cannot replicate, researchers cannot make informed decisions about when to use LLM subjects as a cost-effective alternative.

#### Core Idea
```
Large-Scale Replication: N published experiments → LLM replication

Success rates by experiment type:
  Cognitive tasks (reasoning, judgment):  ~75% replication success
  Social tasks (conformity, persuasion):  ~55% replication success
  Emotional tasks (mood, affect):         ~40% replication success

Implication: LLMs are better at "thinking" experiments than "feeling" experiments
```

#### Core Method
```
┌───────────────────────────────────────────────────────────┐
│          Large-Scale LLM Replication Protocol               │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Source: Published scenario-based experiments             │
│    Psychology: Decision-making, social behavior, emotion  │
│    Management: Leadership, negotiation, organizational    │
│                                                           │
│  Protocol:                                                │
│    1. Replicate exact experimental scenario in prompt     │
│    2. Multiple LLM personas matching participant pool     │
│    3. Statistical comparison to published results          │
│                                                           │
│  Metrics:                                                 │
│    Directional match (effect sign)                        │
│    Effect size match (Cohen's d comparison)               │
│    Significance match (p-value replication)               │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

#### Example
```
Anchoring effect replication:
  Original: High anchor → Estimates 30% higher (p < 0.001)
  LLM:      High anchor → Estimates 22% higher (p < 0.01)
  → Directional match ✓  Effect size match △  Significance ✓
  → Cognitive bias successfully replicated with attenuated magnitude
```

#### Relationship to Our Work

| Aspect      | This Work                           | Our Research Target                   |
|-------------|-------------------------------------|---------------------------------------|
| Scale       | Hundreds of experiments             | Multiple financial scenarios          |
| Finding     | 60-70% directional replication      | Expect similar for financial behavior |
| Pattern     | Cognitive > Social > Emotional      | Financial decisions span all types    |
| Key Insight | Know which behaviors LLMs replicate | Calibrate financial agent design      |

---

## 17. Synthesis: Landscape and Open Challenges

### 17.1 LLM-Based Social Simulations Require a Boundary (2025)

**[CAT: Position] [REL: High]**

**Paper**: "LLM-Based Social Simulations Require a Boundary"
**Link**: https://arxiv.org/abs/2506.19806
**Code**: Null

#### Summary
Position paper arguing that LLM-based social simulations require clear boundaries to make meaningful contributions to social science. Identifies key limitations: LLM training data bias, hallucination in novel scenarios, lack of embodied experience, and difficulty reproducing quantitative social science findings. Proposes a boundary framework specifying when LLM simulations are valid vs. when traditional methods are more appropriate.

#### Core Idea
```
LLM Simulation Boundaries:
  VALID:   Qualitative phenomena, emergent norms, opinion dynamics
  RISKY:   Quantitative predictions, policy decisions, rare events
  INVALID: Scenarios outside training distribution, physical constraints

Rule: Always validate against real data before trusting simulation outputs
```


#### Core Motivation
Existing approaches to simulating this phenomenon lack the nuanced reasoning capabilities that LLM agents provide. The authors aim to demonstrate that LLM-based simulation can reproduce real-world dynamics more faithfully than traditional rule-based models.


#### Core Method
```
┌───────────────────────────────────────┐
│  Agent Design                         │
│  - Persona: demographics + domain role │
│  - Memory: interaction history         │
│  - Reasoning: LLM-based decisions     │
├───────────────────────────────────────┤
│  Simulation Environment               │
│  - Domain-specific rules              │
│  - Multi-agent interaction protocol   │
│  - Data collection & analysis         │
└───────────────────────────────────────┘
```


#### Example
```
Scenario: Agent faces a decision in the simulated environment
  Agent persona: domain-specific role and preferences
  Context: Current state of the simulation
  Reasoning: Agent evaluates options based on persona + context
  Action: Agent selects action → Environment updates
  → Emergent behavior pattern observed across agents
```


#### Relationship to Our Work

| Aspect     | This Work                     | Our Research Target               |
|------------|-------------------------------|-----------------------------------|
| Phenomenon | Specific simulated phenomenon | Society + finance integration     |
| Scale      | Limited                       | Large-scale needed                |
| Validation | Emergent patterns             | Quantitative real-data matching   |
| Key Gap    | Single domain                 | Multi-domain financial simulation |
---

### 17.2 Synthesis Table: Phenomena Coverage

| Phenomenon              | Papers        | Scale  | Validation             | Key Gap                         |
|-------------------------|---------------|--------|------------------------|---------------------------------|
| Human behavior fidelity | 1.1-1.6       | 25-1K  | Qualitative + GSS      | Financial behavior              |
| Community dynamics      | 2.1, 2.2, 2.3 | 1K-10M | Emergent patterns      | Market communities              |
| Information diffusion   | 3.1-3.5       | 100-1M | Network metrics        | Financial contagion             |
| Opinion polarization    | 4.1-4.3       | 50-10K | Echo chamber metrics   | Sentiment cascades              |
| Emergent norms          | 5.1, 5.2      | 24-200 | Convention emergence   | Market conventions              |
| Cooperation/trust       | 6.1-6.3       | 10-100 | Game outcomes          | Financial trust                 |
| Elections               | 7.1           | 10K    | Election results       | Market elections (proxy voting) |
| Market dynamics         | 8.1-8.14      | 5-1K   | Financial theory       | Full market reproduction        |
| Consumer behavior       | 9.1-9.7       | 100-1K | Purchase data          | Financial consumption           |
| Epidemic spread         | 10.1-10.2     | 1K-10K | SEIR comparison        | Financial contagion analogy     |
| Disaster/policy         | 11.1-11.2     | 1K     | Historical data        | Financial crisis policy         |
| Crime                   | 12.1          | 1K     | Crime statistics       | Financial crime                 |
| Cultural evolution      | 13.1-13.2     | 50-200 | Norm emergence         | Financial culture               |
| Game theory             | 14.1-14.3     | 2-10   | Equilibrium comparison | Market game theory              |
| Extreme events          | 15.1          | 10-100 | Causal attribution     | Financial black swans           |

### 17.3 Key Observations

1. **Financial simulation is rapidly evolving**: TwinMarket (NeurIPS 2025) and MarS (ICLR 2025) represent major advances — TwinMarket shows BDI + social interaction produces emergent market dynamics; MarS shows generative models can replace agent-based approaches for order-level realism
2. **Scale-fidelity tradeoff**: Small-scale simulations (1.2) achieve high fidelity; large-scale (OASIS) sacrifice individual accuracy; TwinMarket breaks this tradeoff with 1,000+ agents and stylized fact reproduction
3. **Validation gap is narrowing**: TwinMarket validates against 4 stylized facts with quantitative metrics; MarS validates 14 stylized facts; but most other papers still rely on qualitative emergence observation
4. **Two paradigms emerging**: Agent-based (TwinMarket: model the traders) vs. Generative (MarS: model the orders) — complementary approaches with different strengths
5. **Emergence is demonstrated but not controlled**: Social conventions and collective biases emerge spontaneously, but controlling what emerges remains unsolved (rumor injection in TwinMarket is a first step)
6. **Financial black swans**: Section 15's extreme events framework is directly applicable to financial crash simulation; TwinMarket's IEEE companion paper explicitly studies this
7. **Missing: Cross-domain simulation**: No work simultaneously models social, economic, and financial phenomena in an integrated framework

### 17.4 Our Position

Our research targets **reproducing real societal and financial events** using LLM-based multi-agent simulation. The key differentiators from existing work:

| Dimension       | Existing Work                                                            | Our Target                                                                     |
|-----------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Domain          | Single phenomenon (elections OR markets OR epidemics)                    | Integrated society + finance                                                   |
| Validation      | Qualitative emergence OR single-metric matching                          | Multi-metric matching of real events (stylized facts + social patterns)        |
| Scale           | Usually 25-1K agents                                                     | Need 1K+ with financial diversity                                              |
| Financial Focus | Single-agent trading (FinAgent, FinMem) OR order-level generation (MarS) | Multi-agent market dynamics with social layer (TwinMarket + social context)    |
| Emergence       | Observed but not controlled                                              | Targeted reproduction of specific events                                       |
| Approach        | Agent-based (TwinMarket) OR Generative (MarS)                            | Hybrid: agent-based for social behavior + generative for market microstructure |

---
