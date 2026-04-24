# Financial Multi-Agent Simulation Creation Guide

## How to Use This Guide

This document provides a complete 10-step methodology for creating financial market simulations. Each step references specific template files from the AssetBubble implementation. Follow the steps sequentially, using the referenced files as guides for structure and content.

---

## STEP 0: Define Your Simulation

### 0.1 Minimum Required Input

The user only needs to provide:

```
SIMULATION DEFINITION
=====================

Name: [PascalCase, e.g., "FlashCrash", "HerdBehavior", "VolatilitySpike"]

Phenomenon Description:
-----------------------
[1-2 paragraphs describing the financial phenomenon to simulate]
- What happens in this phenomenon?
- What are the key characteristics?
```

### 0.2 AI/Researcher Responsibility

**All remaining information must be researched and developed through comprehensive investigation:**

The AI or researcher should:

1. **Search extensively** for academic papers, empirical studies, and historical data about the phenomenon
2. **Identify real-world examples** (historical events, case studies)
3. **Determine the market context** (type, structure, institutional features)
4. **Formulate research questions** based on gaps in understanding
5. **Build the theoretical foundation** through literature review

**Reference**: See how AssetBubble's `explain.md` develops comprehensive context from a simple starting point. The phenomenon "asset bubbles" expands into detailed theoretical discussion, historical cases, and research questions through thorough investigation.

### 0.3 Research Output Structure

After research, compile findings into:

```
RESEARCHED CONTENT (to be filled through investigation)
======================================================

Scenario Context:
-----------------
[Market type, structure, institutional features - RESEARCHED]

Research Questions:
-------------------
[3-5 specific questions - DEVELOPED from literature gaps]

Real-World Examples:
--------------------
[2-3 historical events with details - FOUND through search]

Theoretical Foundation:
-----------------------
[Core theories, citations, models - EXTRACTED from academic papers]
```

### 0.2 Example: AssetBubble Definition

**Reference**: See `examples/AssetBubble/Rule/explain.md` lines 1-30 for how AssetBubble defines its phenomenon.

Key elements in AssetBubble definition:
- Clear phenomenon name (Asset Bubbles)
- Mechanism description (positive feedback, speculation)
- Theoretical foundation preview (Greater Fool Theory, etc.)
- Key dynamics listed (5-step bubble process)

### 0.3 Validation Checklist

Before proceeding, verify:
- [ ] Name is descriptive and PascalCase
- [ ] Phenomenon is distinct from existing simulations
- [ ] Description is specific enough to guide agent design
- [ ] Research questions are answerable through simulation
- [ ] Real-world examples exist for validation

---

## STEP 1: Research and Theory Foundation

### 1.1 Research Strategy

Conduct systematic research across five dimensions:

**Dimension 1: Core Economic Theory**
Search for academic papers establishing the theoretical foundations of your phenomenon.

Key search terms to use:
```
"[phenomenon] financial theory"
"[phenomenon] economic model"
"[phenomenon] academic papers/books"
"agent-based model [phenomenon]"
```

**Dimension 2: Behavioral Finance**
Identify cognitive biases and psychological factors involved.

Key search terms:
```
"[phenomenon] behavioral finance"
"[phenomenon] cognitive bias"
"[phenomenon] investor psychology"
```

**Dimension 3: Empirical Evidence**
Find stylized facts from real markets.

Key search terms:
```
"[phenomenon] empirical evidence"
"[phenomenon] stylized facts"
"[phenomenon] statistical properties"
```

**Dimension 4: Historical Case Studies**
Document specific historical events.

Key search terms:
```
"[phenomenon] case study"
"[phenomenon] historical analysis"
"famous [phenomenon] events"
```

**Dimension 5: Market Microstructure**
Understand trading mechanisms and institutional details.

Key search terms:
```
"[phenomenon] market microstructure"
"[phenomenon] trading mechanism"
"[phenomenon] high frequency trading"
```

### 1.2 Research Documentation Structure

Create a research notes file with these sections:

**Section 1: Core Theories**

For each theory identified, document:

```
Theory: [Full name]
Citation: [Author, Year, Journal, DOI if available]
Key Insight: [2-3 sentence summary of core mechanism]
Mathematical Model: [Formula if available]
Relevance: [How this applies to your simulation]
Implementation Notes: [How to operationalize in agents]
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 1-21 for how AssetBubble documents its theoretical foundation in the module docstring.

**Section 2: Stylized Facts**

Create a table:

| Stylized Fact | Source     | Implementation Approach |
|---------------|------------|-------------------------|
| [Description] | [Citation] | [How to model]          |

**Section 3: Historical Events**

For each event:

```
Event: [Name]
Date: [When it occurred]
Market: [Which market/asset]
Trigger: [What started it]
Timeline:
  - [Time]: [Event]
  - [Time]: [Event]
Price Movement: [Peak, trough, % change]
Key Participants: [Who was involved]
Lessons for Simulation: [What to model]
```

**Section 4: Agent Types from Literature**

Document participant types found in research:

```
Agent Type: [Name from literature]
Frequency: [% of market or prevalence]
Behavior: [What they do]
Strategy: [How they decide]
Impact: [Effect on market]
Theory Basis: [Which theory explains them]
```

**Section 5: Parameter Values**

Compile quantitative estimates:

| Parameter | Typical Range | Source     | Notes     |
|-----------|---------------|------------|-----------|
| [Name]    | [Min-Max]     | [Citation] | [Context] |

### 1.3 Theory Selection Criteria

Select 2-4 theories that:

1. **Explain the core mechanism** - Must directly address what causes the phenomenon
2. **Are implementable** - Can be operationalized as agent rules or prompts
3. **Suggest different agent types** - Each theory maps to a distinct investor class
4. **Have empirical support** - Backed by data or widely accepted in literature

**Reference**: AssetBubble uses four theories (see `examples/AssetBubble/Rule/players.py` lines 7-11):
- Greater Fool Theory → MomentumSpeculator
- Limits to Arbitrage → RationalArbitrageur  
- Noise Trader Risk → NoiseTrader
- Synchronization Risk → timing of bubble bursts

---

## STEP 2: Design Agent Architecture

### 2.1 Market Agent Design

The Market is the coordinator that clears orders and sets prices. Design it first as all investors interact with it.

**Step 2.1.1: Define Price Formation Mechanism**

Specify the mathematical model:

```
PRICE FORMULA SPECIFICATION
===========================

Formula: [Write the complete equation]

Variables:
- P(t): [Definition]
- NetDemand: [How calculated]
- [Other variables]: [Definitions]

Parameters:
- price_impact (λ): [Description, typical value range, your value, source]
- mean_reversion (γ): [Description, typical value range, your value, source]
- [Other parameters]: [Same structure]

Economic Rationale:
[Explain why each term is included and how it contributes to the phenomenon]

Dynamic Properties:
- What happens when NetDemand is positive?
- What happens when price deviates from fundamental?
- How does noise affect dynamics?
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 41-62 for Market class docstring showing formula documentation.

**Step 2.1.2: Define Additional Market Mechanisms**

List all market features:

```
MARKET MECHANISMS
=================

Circuit Breakers:
- Trigger: [Condition]
- Action: [What happens]
- Duration: [How long]

Short Selling:
- Allowed: [Yes/No]
- Cost: [% of position value]
- Constraints: [Any limits]

Margin Requirements:
- Initial margin: [%]
- Maintenance margin: [%]
- Margin call process: [Description]

Liquidity Provision:
- Market makers: [Yes/No]
- Their behavior: [How they quote]

Other Features:
- [Any other mechanisms]
```

**Step 2.1.3: Define Information Broadcast**

Specify what Market tells investors each round:

```
INFORMATION BROADCAST
=====================

Always Included:
- Current price
- Fundamental value
- Current round number

Calculated Metrics:
- Price deviation from fundamental [%]
- Price change over last N rounds [%]
- Trading volume
- [Other metrics]

Rationale:
[Why each piece of information is included]
```

### 2.2 Investor Taxonomy Design

Design 4-6 distinct investor types. For each type, create a complete specification.

**Step 2.2.1: Investor Type Specification Template**

```
INVESTOR TYPE SPECIFICATION
===========================

Name: [Descriptive name]
Code Name: [PascalCase class name]

Theoretical Basis:
- Primary Theory: [Name from Step 1]
- Citation: [Full reference]
- Key Mechanism: [How theory explains behavior]

Market Role:
- Category: [Stabilizing/Destabilizing/Neutral]
- Typical Fraction: [% of market]
- When Active: [Market conditions]

Behavioral Profile:
- Decision Style: [Rule-based/Discretionary/Hybrid]
- Information Used: [List what they observe]
- Time Horizon: [High-frequency/Day trader/Long-term]
- Risk Tolerance: [Low/Medium/High/Extreme]

RULE-BASED SPECIFICATION
------------------------

Trigger Conditions:
- Buy when: [Specific condition]
- Sell when: [Specific condition]
- Hold when: [Specific condition]

Position Sizing:
- Formula: [How many shares to trade]
- Constraints: [Max position, cash limits, etc.]

Parameters:
| Parameter | Value   | Source     | Description        |
|-----------|---------|------------|--------------------|
| [Name]    | [Value] | [Citation] | [What it controls] |

LLM PERSONA SPECIFICATION
-------------------------

Core Belief: [One sentence that guides all decisions]

Psychological Profile:
[2-3 paragraphs describing mindset, biases, tendencies]

Decision Framework:
1. [Step 1: What to assess first]
2. [Step 2: What to assess next]
3. [Step 3: How to decide]

Signal Interpretation:
- Price rising strongly: [How they interpret]
- Price falling sharply: [How they interpret]
- Price near fundamental: [How they interpret]
- High volatility: [How they interpret]

Position Sizing Approach:
- Aggressive trades: [Range] shares
- Moderate trades: [Range] shares
- Conservative trades: [Range] shares

Risk Management:
[How they manage risk, when they exit]

RULELLM HYBRID SPECIFICATION
----------------------------

Embedded Rules:
[List quantitative formulas to include in prompt]

Rule-Judgment Balance:
[When to follow rules strictly vs use discretion]
```

**Reference**: See `examples/AssetBubble/Rule/players.py` lines 100-200 for MomentumSpeculator class showing rule-based implementation structure.

**Reference**: See `examples/AssetBubble/LLM/prompts.py` lines 15-36 for LLMGreaterFoolSpec system prompt showing persona design.

**Step 2.2.2: Agent Diversity Check**

Ensure your investor set has:

1. **Different time horizons** - Some fast, some slow
2. **Different information processing** - Some technical, some fundamental
3. **Different risk attitudes** - Some conservative, some aggressive
4. **Conflicting strategies** - Some buy when others sell
5. **Different market impacts** - Some small, some large

**Reference**: AssetBubble has 5 investor types (see `configs/AssetBubble/Rule/players.yml`):
- MomentumSpeculator (trend follower, destabilizing)
- Fundamentalist (value-based, stabilizing)
- NoiseTrader (random, creates opportunities)
- RationalArbitrageur (corrects mispricings, weakly stabilizing)
- LeveragedSpeculator (amplifies moves, extreme risk)

### 2.3 Communication Design

**Step 2.3.1: Message Flow Design**

```
ROUND STRUCTURE
===============

Step 1: Market broadcasts state
  └─> All investors receive market_update message

Step 2: Each investor processes information
  └─> Extract relevant data
  └─> Apply strategy (rule or LLM)
  └─> Form decision

Step 3: Investors send orders to Market
  └─> order message with action, quantity, price

Step 4: Market aggregates orders
  └─> Calculate net demand
  └─> Apply price formula
  └─> Update state

Step 5: Record and repeat
  └─> Log transactions
  └─> Increment round
```

**Step 2.3.2: Topology Specification**

```
COMMUNICATION TOPOLOGY
======================

Structure: Star (Market center, all investors connected)

Connections:
- Market → Investors: Broadcast market state
- Investors → Market: Send orders

Message Types:
- market_update: [Fields included]
- order: [Fields included]

Frequency: Every round, synchronous
```

**Reference**: See `configs/AssetBubble/Rule/topology.yml` for topology configuration structure.

---

## STEP 3: Create Configuration Files

### 3.1 Configuration Principles

All parameters must be externalized. No hardcoded values in Python code.

**Principle 1**: Every numeric value has a source citation
**Principle 2**: All file paths are relative and consistent
**Principle 3**: Parameters are grouped logically
**Principle 4**: Documentation comments explain each parameter

### 3.2 File Structure

Create these files for each variant (Rule, LLM, RuleLLM, Rag):

```
configs/{SimulationName}/
├── Rule/
│   ├── simulation.yml    # Simulation settings
│   ├── players.yml       # Agent definitions
│   ├── topology.yml      # Communication structure
│   └── persona.yml       # Persistence settings
├── LLM/
│   └── [same 4 files]
├── RuleLLM/
│   └── [same 4 files]
└── Rag/
    └── [same 4 files]
```

### 3.3 simulation.yml Structure

**Reference**: See `configs/AssetBubble/Rule/simulation.yml` for template.

Key sections to populate:

```
simulation.yml STRUCTURE
========================

Header Comments:
- Simulation name and description
- Phenomenon being studied
- Core theories
- Usage instructions

setting:
  name: [simulation identifier]
  description: [detailed description]
  total_rounds: [200-500 typical]
  record_path: [EXPERIMENT/{Sim}/Rule/records]
  storage_path: [EXPERIMENT/{Sim}/Rule/communication]

environment:
  dotenv_path: [.env file location]
  workspace: [project root]

ray:
  namespace: [unique identifier]
  object_store_memory: [536870912 for LLM sims]
  [other Ray settings]

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: [message storage location]
  record_messages: [true/false]
```

### 3.4 players.yml Structure

**Reference**: See `configs/AssetBubble/Rule/players.yml` for template.

Key sections to populate:

```
players.yml STRUCTURE
=====================

Header Comments:
- Agent architecture overview
- Theory basis

market:
  name: "Market"
  class: "examples.{Sim}.Rule.players:Market"
  num_instances: 1
  config:
    identity: "market"
    role: coordinator
    extras:
      # All market parameters here
      fundamental_value: [with source comment]
      initial_price: [with source comment]
      price_impact: [with source comment]
      mean_reversion: [with source comment]
      [other parameters]

investor_type_1:
  name: [Display name]
  class: "examples.{Sim}.Rule.players:[ClassName]"
  num_instances: [3-5 typical]
  config:
    identity: [code name]
    role: player
    extras:
      # All investor parameters here
      initial_cash: [value]
      initial_position: [value]
      [strategy parameters with source comments]

# Repeat for each investor type
```

### 3.5 topology.yml Structure

**Reference**: See `configs/AssetBubble/Rule/topology.yml` for template.

```
topology.yml STRUCTURE
======================

graph:
  type: star
  center: market

connections:
  - from: market
    to: [list all investor instances]
    bidirectional: true
  
  - from: [investor group]
    to: [market]
    bidirectional: false

broadcast:
  enabled: true
  from: market
  to: all_players
```

### 3.6 persona.yml Structure

**Reference**: See `configs/AssetBubble/Rule/persona.yml` for template.

```
persona.yml STRUCTURE
=====================

market:
  type: proxy
  checkpoint_dir: [path]
  record_path: [path]
  monitoring:
    record_path: [path]

investor_type_1:
  type: player
  checkpoint_dir: [path]
  record_path: [path]
  monitoring:
    record_path: [path]

# Repeat for each agent
```

---

## STEP 4: Implement Code

### 4.1 Rule Variant Implementation

**Step 4.1.1: Create Directory Structure**

```
examples/{SimulationName}/
├── __init__.py
└── Rule/
    ├── __init__.py
    ├── players.py
    ├── run_{name}.py
    └── analysis.py
```

**Step 4.1.2: Implement Market Agent**

**Reference**: Use `examples/AssetBubble/Rule/players.py` lines 41-150 as template.

Structure to implement:

```
Market Agent Implementation
===========================

Module Docstring:
- Phenomenon description
- Theoretical foundation (cite papers)
- Key dynamics
- Parameter configuration note

Class: Market
-------------

Docstring:
- Purpose
- Price formula with all terms
- Parameter descriptions
- Dynamic properties

Methods to implement:

1. perceive()
   - Initialize state on first call
   - Extract orders from observation
   - Call clearing function
   - Update state
   - Log metrics

2. _initialize_market_state()
   - Load parameters from config
   - Set up history buffers
   - Create output directories

3. _extract_orders()
   - Parse inbound messages
   - Validate order format
   - Return list of orders

4. _clear_market()
   - Calculate net demand
   - Apply price impact
   - Apply mean reversion
   - Add noise
   - Update fundamental
   - Return market result

5. _update_state()
   - Store new price
   - Store new fundamental
   - Update history buffers

6. _log_market_state()
   - Log key metrics
   - Use appropriate log level

7. step()
   - Broadcast market state
   - Include all relevant metrics
   - Return Action with outbounds
```

**Step 4.1.3: Implement Investor Agents**

**Reference**: Use `examples/AssetBubble/Rule/players.py` lines 150+ for investor templates.

For each investor type:

```
Investor Agent Implementation
=============================

Class Docstring:
- Investor description
- Theoretical basis (cite paper)
- Strategy summary
- Parameters from config

Methods to implement:

1. perceive()
   - Initialize state on first call
   - Extract market info from observation
   - Store in custom_state

2. _initialize_investor_state()
   - Load wealth parameters
   - Load strategy parameters
   - Set up history buffers

3. step()
   - Get market info
   - Call decision function
   - Update portfolio state
   - Record wealth
   - Send order message

4. _make_decision()
   - Implement strategy logic
   - Check all conditions
   - Calculate position size
   - Respect constraints
   - Return decision dict
```

**Step 4.1.4: Implement Runner Script**

**Reference**: Use `examples/AssetBubble/Rule/run_bubble.py` as template.

Structure:

```
Runner Script
=============

Docstring:
- Phenomenon description
- Theory basis
- Usage instructions

Implementation:
1. Add project root to sys.path
2. Import run_simulation_with_progress
3. Parse command line arguments
4. Run simulation with progress updates
5. Print completion message
```

**Step 4.1.5: Implement Analysis Script**

**Reference**: Use `examples/AssetBubble/Rule/analysis.py` as template.

Structure:

```
Analysis Script
===============

Functions to implement:

1. load_simulation_data()
   - Read price history
   - Read fundamental history
   - Read volume history
   - Read agent wealth data
   - Return structured data

2. calculate_metrics()
   - Max/min price
   - Max deviation
   - Volatility
   - Average volume
   - [Phenomenon-specific metrics]

3. create_visualizations()
   - Price vs fundamental plot
   - Deviation plot
   - Volume plot
   - Wealth distribution plot
   - [Additional plots]

4. generate_summary_report()
   - Text summary of metrics
   - Interpretation guidance
   - Save to file

5. main()
   - Parse config
   - Load data
   - Calculate metrics
   - Create visualizations
   - Generate report
```

### 4.2 LLM Variant Implementation

**Step 4.2.1: Create Directory Structure**

```
examples/{SimulationName}/
└── LLM/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_llm.py
    └── analysis.py
```

**Step 4.2.2: Implement LLM Investor Agents**

**Reference**: Use `examples/AssetBubble/LLM/players.py` as template.

Structure:

```
LLM Investor Implementation
===========================

Module Docstring:
- Phenomenon
- Design (Market rule-based, Investors LLM)
- LLM provider details
- Usage

Helper Function:
- load_prompt(): Load prompt from module path

Class: Market
-------------
- IDENTICAL to Rule variant
- Copy implementation

Class: LLM{InvestorType}
------------------------

Docstring:
- Personality description
- Psychological profile
- LLM interaction description

Methods:

1. __init__()
   - Initialize LLM client
   - Load prompt paths from config
   - Set generation parameters

2. perceive()
   - Same as Rule variant

3. _initialize_state()
   - Same as Rule variant

4. step()
   - Load system prompt
   - Format user prompt with market data
   - Call LLM API
   - Parse response
   - Validate decision
   - Update state
   - Send order

5. _format_user_prompt()
   - Extract market data
   - Extract portfolio data
   - Fill template variables
   - Return formatted string

6. _validate_decision()
   - Check action validity
   - Enforce quantity limits
   - Respect cash constraints
   - Respect position constraints
   - Return validated decision

7. _update_state()
   - Same as Rule variant
```

**Step 4.2.3: Design LLM Prompts**

**CRITICAL CONSTRAINT**: Prompts must define INVESTOR PERSONALITY ONLY. They must NOT mention the specific phenomenon being simulated.

**Reference**: Use `examples/AssetBubble/LLM/prompts.py` as template.

**CANONICAL OUTPUT FORMAT** (mandatory at end of every system prompt):

```
OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags,
then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
```

- `<analysis>` tag: chain-of-thought reasoning — market assessment, strategy logic, rationale
- `<decision>` tag: the parseable JSON decision
- **Never use `<think>` tags** — `<think>` is deprecated; `<analysis>` is the canonical tag
- `bid_price` and `quantity` must be numeric literals, not formulas or strings

Structure for each investor type:

```
Prompt Design
=============

System Prompt Structure:

1. Identity Statement
   "You are a [TYPE] in financial markets."

2. Core Belief
   "CORE BELIEF: [One sentence guiding philosophy]"

3. Psychology Description
   "YOUR PSYCHOLOGY: [Mindset, biases, tendencies]"

4. Strategy Framework
   "YOUR STRATEGY:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]"

5. Signal Interpretation
   "HOW YOU INTERPRET MARKET DATA:
    - Price rising: [Interpretation]
    - Price falling: [Interpretation]
    - [Other signals]"

6. Position Sizing
   "POSITION SIZING:
    - Aggressive: [Range] shares
    - Moderate: [Range] shares
    - Conservative: [Range] shares"

7. Risk Profile
   "RISK PROFILE: [Description]"

8. Constraints
   "CONSTRAINTS:
    - Cannot spend more than cash
    - Cannot sell more than owned
    - [Other constraints]"

9. Output Format
   "OUTPUT FORMAT:
    First output your reasoning inside <analysis>...</analysis> tags,
    then output your decision inside <decision>...</decision> tags.
    The decision must be valid JSON:
    {\"action\": \"buy\"|\"sell\"|\"hold\", \"bid_price\": float, \"quantity\": float, \"reasoning\": string}
    IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."

User Prompt Template:

"Current Market State:
- Price: ${price}
- Fundamental: ${fundamental}
- Deviation: {deviation}
- Recent change: {price_change}

Your Portfolio:
- Cash: ${cash}
- Position: {position} shares
- Value: ${portfolio_value}

[Question prompting decision]"
```

### 4.3 RuleLLM Variant Implementation

**Step 4.3.1: Create Directory Structure**

```
examples/{SimulationName}/
└── RuleLLM/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_rulellm.py
    └── analysis.py
```

**Step 4.3.2: Implement Hybrid Prompts**

**Reference**: Use `examples/AssetBubble/RuleLLM/prompts.py` as template.

Structure:

```
RuleLLM Prompt Design
=====================

System Prompt Structure:

1-7. Same as LLM variant

8. Embedded Rules Section
    "QUANTITATIVE RULES:
     You follow these formulas:
     
     1. [Formula name]:
        [Mathematical expression]
     
     2. [Formula name]:
        [Mathematical expression]
     
     [Additional formulas]"

9. Rule-Judgment Instructions
    "HOW TO USE RULES:
     - Apply formulas to calculate initial values
     - Use judgment to adjust based on context
     - Explain when you follow vs override rules
     - Consider risk management"

10. Output Format
    "OUTPUT FORMAT:
     First output your reasoning inside <analysis>...</analysis> tags,
     then output your decision inside <decision>...</decision> tags.
     The decision must be valid JSON:
     {\"action\": \"buy\"|\"sell\"|\"hold\", \"bid_price\": float, \"quantity\": float, \"reasoning\": string}
     IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."
    (Identical to LLM variant — always use <analysis> not <think>)
```

**Step 4.3.3: Implement Players**

- Market: IDENTICAL to Rule variant
- Investors: Same structure as LLM variant
- Only difference is prompt content

### 4.4 RAG Variant Implementation

**Step 4.4.1: Create Directory Structure**

```
examples/{SimulationName}/
└── Rag/
    ├── __init__.py
    ├── players.py
    ├── prompts.py
    ├── run_{name}_rag.py
    └── analysis.py
```

**Step 4.4.2: Design Knowledge Base**

```
Knowledge Base Design
=====================

Content to Include:
- Historical case studies
- Academic research findings
- Similar market events
- Strategy performance data

Indexing Strategy:
- Vector store per agent type
- Metadata filters
- Top-k retrieval (k=3 typical)

Query Formulation:
- Based on current market state
- Price deviation magnitude
- Volatility level
- Trend direction
```

**Step 4.4.3: Implement RAG Investors**

**Reference**: Use `examples/AssetBubble/Rag/players.py` as template.

Additional methods needed:

```
RAG Investor Additional Methods
===============================

1. _init_knowledge_store()
   - Initialize vector store
   - Set persist directory
   - Load existing index if available

2. _formulate_knowledge_query()
   - Extract key market features
   - Create search query
   - Return query string

3. _format_retrieved_docs()
   - Take retrieved documents
   - Format for prompt inclusion
   - Return context string

Modified step() method:
- Formulate query
- Retrieve documents
- Format context
- Augment system prompt
- Generate decision
```

---

## STEP 5: Validate Design

### 5.1 Design Validation Checklist

**Theory Alignment**
- [ ] Every agent behavior is justified by specific financial theory
- [ ] Every parameter value is backed by empirical research
- [ ] Market mechanism captures key phenomenon dynamics
- [ ] All theories are properly cited

**Agent Diversity**
- [ ] Multiple distinct strategies represented
- [ ] Agents have conflicting incentives
- [ ] Different time horizons present
- [ ] Different risk tolerances present
- [ ] Mix of stabilizing and destabilizing agents

**Phenomenon Specificity**
- [ ] Simulation captures unique aspects of target phenomenon
- [ ] Not generic - has distinctive features
- [ ] Can generate stylized facts from literature
- [ ] Parameters calibrated for phenomenon emergence

**Comparability**
- [ ] Rule and LLM variants use same market mechanism
- [ ] Agent types are roughly equivalent across variants
- [ ] Parameters are calibrated for fair comparison
- [ ] Output metrics are comparable

### 5.2 Prompt Validation Checklist

**LLM Prompts**
- [ ] Define personality only, not phenomenon
- [ ] Core belief is clear and consistent
- [ ] Decision framework is specific
- [ ] Output format is unambiguous
- [ ] Constraints are explicit

**RuleLLM Prompts**
- [ ] Include all quantitative rules
- [ ] Explain rule-judgment balance
- [ ] Rules match Rule variant exactly
- [ ] Examples show rule application

### 5.3 Configuration Validation Checklist

- [ ] All paths are correct and consistent
- [ ] All parameters have source comments
- [ ] No hardcoded values in code
- [ ] YAML syntax is valid
- [ ] All required fields present

---

## STEP 6: Code Quality Check

### 6.1 Code Review Checklist

**Documentation**
- [ ] Module docstrings present with phenomenon and theory
- [ ] Class docstrings present with parameter descriptions
- [ ] Method docstrings present with inputs/outputs
- [ ] Complex formulas have inline comments
- [ ] Variable names are descriptive

**Correctness**
- [ ] Price calculations are numerically stable
- [ ] Division by zero prevented
- [ ] Negative prices prevented
- [ ] Edge cases handled
- [ ] State updates are atomic

**Structure**
- [ ] Methods follow perceive/decide/act pattern
- [ ] Helper functions for complex logic
- [ ] Consistent error handling
- [ ] Appropriate logging

**Performance**
- [ ] No unnecessary computations in loops
- [ ] History buffers have size limits
- [ ] Efficient data structures

### 6.2 Reference File Check

Verify your implementation matches reference structure:

**Market Agent**: Compare to `examples/AssetBubble/Rule/players.py` Market class
**Investor Agents**: Compare to `examples/AssetBubble/Rule/players.py` investor classes
**LLM Investors**: Compare to `examples/AssetBubble/LLM/players.py`
**Prompts**: Compare to `examples/AssetBubble/LLM/prompts.py`
**Runner**: Compare to `examples/AssetBubble/Rule/run_bubble.py`
**Analysis**: Compare to `examples/AssetBubble/Rule/analysis.py`

---

## STEP 7: Create Analysis Tools

### 7.1 Analysis Script Requirements

**Reference**: Use `examples/AssetBubble/Rule/analysis.py` as template.

Functions to implement:

```
Analysis Script Components
==========================

1. Data Loading
   - Load price history from EXPERIMENT/.../market/price
   - Load fundamental history
   - Load volume history
   - Load wealth history for each agent
   - Handle missing data gracefully

2. Metric Calculation
   - Price statistics (max, min, final)
   - Deviation statistics (max, min, mean)
   - Volatility (std of returns)
   - Volume statistics
   - Wealth distribution metrics
   - [Phenomenon-specific metrics]

3. Visualization
   - Price vs fundamental over time
   - Price deviation percentage
   - Trading volume by round
   - Wealth distribution histogram
   - Agent-type performance comparison
   - [Phenomenon-specific plots]

4. Report Generation
   - Text summary of all metrics
   - Interpretation guidance
   - Comparison to expected ranges
   - Save to EXPERIMENT/.../analysis/
```

### 7.2 Testing Strategy

**Unit Tests**
- Test Market price calculation
- Test each investor decision logic
- Test edge cases
- Test data loading

**Integration Tests**
- Run short simulation (10 rounds)
- Verify all agents participate
- Verify data is recorded
- Verify analysis runs

**Validation Tests**
- Check phenomenon emerges
- Verify metrics in reasonable ranges
- Compare to historical data

---

## STEP 8: Create Documentation

### 8.1 explain.md Structure

**Reference**: Use `examples/AssetBubble/Rule/explain.md` as template.

Required sections:

```
explain.md Structure
====================

1. Header with Title

2. Overview Table
   | Item | Description |
   | Phenomenon | [Name and brief] |
   | Model | [Rule/LLM/Hybrid] |
   | Key Feature | [Unique aspect] |
   | Academic Value | [Research contribution] |

3. Theoretical Foundation
   - Primary theory with citation
   - Mathematical model
   - Key insight
   - Supporting theories

4. Architecture Diagram
   - ASCII art showing agents
   - Message flow
   - Information structure

5. Agent Descriptions
   - Market: mechanism, parameters
   - For each investor:
     * Theoretical basis
     * Behavior description
     * Parameters
     * Expected impact

6. Variant Comparison
   - Table comparing Rule/LLM/RuleLLM/RAG
   - When to use each
   - Expected differences

7. Usage Instructions
   - Command to run each variant
   - Environment variables needed
   - Expected runtime
   - Output locations

8. Expected Results
   - Stylized facts to observe
   - Typical metric ranges
   - Interpretation guidance

9. References
   - Complete academic citations
   - Related work
```

### 8.2 analysis.md Structure

**Reference**: Use `examples/AssetBubble/Rule/analysis.md` as template.

Required sections:

```
analysis.md Structure
=====================

1. Metrics Guide
   - Definition of each metric
   - How to calculate
   - Interpretation of values

2. Visualization Guide
   - What each plot shows
   - How to read patterns
   - Red flags to watch for

3. Comparative Framework
   - How to compare variants
   - Statistical approaches
   - Reporting standards

4. Troubleshooting
   - Common issues in results
   - How to diagnose
   - Parameter adjustments
```

---

## STEP 9: Execute and Debug

### 9.1 Execution Steps

```
Execution Workflow
==================

Step 1: Run Rule variant
  $ python examples/{Sim}/Rule/run_{name}.py \\
      -c configs/{Sim}/Rule/simulation.yml

Step 2: Check outputs
  $ ls EXPERIMENT/{Sim}/Rule/records/
  Verify files created

Step 3: Run analysis
  $ python examples/{Sim}/Rule/analysis.py \\
      -c configs/{Sim}/Rule/simulation.yml

Step 4: View results
  $ open EXPERIMENT/{Sim}/Rule/analysis/analysis_summary.png

Step 5: Run LLM variant (if API key available)
  $ python examples/{Sim}/LLM/run_{name}_llm.py \\
      -c configs/{Sim}/LLM/simulation.yml

Step 6: Compare variants
  Run analysis on both
  Compare metrics
```

### 9.2 Common Issues and Solutions

| Issue                  | Diagnosis            | Solution                       |
|------------------------|----------------------|--------------------------------|
| Simulation won't start | Check YAML syntax    | Validate YAML online           |
| Import errors          | Check sys.path       | Verify project structure       |
| No trading             | Check thresholds     | Relax conditions               |
| Price goes negative    | Check floor          | Add max(price, 0.01)           |
| LLM invalid JSON       | Check prompt clarity | Strengthen format instructions |
| Too slow               | Check agent count    | Reduce num_instances           |
| No phenomenon          | Check parameters     | Calibrate to literature        |

### 9.3 Debugging Strategy

```
Debugging Workflow
==================

1. Test Market alone
   - Create minimal simulation
   - Only Market agent
   - Verify price dynamics

2. Add one investor type
   - Test in isolation
   - Verify decisions
   - Check state updates

3. Add remaining investors
   - One at a time
   - Verify interactions

4. Full simulation
   - Short run (10 rounds)
   - Check all outputs
   - Verify phenomenon emerges

5. Production run
   - Full rounds
   - All variants
   - Complete analysis
```

---

## STEP 10: Final Review

### 10.1 Completeness Checklist

**Code**
- [ ] Rule/ players.py implements all agents
- [ ] Rule/ run script works
- [ ] Rule/ analysis.py generates plots
- [ ] LLM/ prompts.py has all personalities
- [ ] LLM/ prompts.py uses `<analysis>` tag (not `<think>`) in output format
- [ ] LLM/ prompts.py decision JSON includes `bid_price`, `quantity`, `reasoning` fields
- [ ] LLM/ players.py handles responses
- [ ] RuleLLM/ hybrid prompts complete
- [ ] RuleLLM/ prompts.py uses `<analysis>` tag in output format
- [ ] Rag/ knowledge retrieval implemented
- [ ] Rag/ prompts.py uses `<analysis>` tag in output format
- [ ] All __init__.py files present

**Configuration**
- [ ] All simulation.yml files valid
- [ ] All players.yml files valid
- [ ] All topology.yml files valid
- [ ] All persona.yml files valid
- [ ] Paths correct in all files
- [ ] Parameters documented

**Documentation**
- [ ] Rule/explain.md complete
- [ ] Rule/analysis.md complete
- [ ] LLM/explain.md complete
- [ ] LLM/analysis.md complete
- [ ] All citations included
- [ ] Usage examples provided

**Integration**
- [ ] SCENARIO_PATH_MAP updated
- [ ] WebUI discovers simulation
- [ ] Paths use nested structure
- [ ] All imports resolve

### 10.2 Quality Standards

**Theory Quality**
- Every claim backed by citation
- Parameters from empirical research
- Mechanisms justified by theory

**Code Quality**
- Follows project conventions
- Well-documented
- Handles errors gracefully
- Efficient implementation

**Documentation Quality**
- Clear and comprehensive
- Properly formatted
- Examples included
- Accessible to newcomers

**Reproducibility**
- All parameters externalized
- Random seeds documented
- Environment specified
- Results verifiable

---

## Reference: AssetBubble Implementation

Use AssetBubble as the primary reference for all implementation details:

### Key Reference Files

| Component         | Reference File                                      |
|-------------------|-----------------------------------------------------|
| Market Agent      | `examples/AssetBubble/Rule/players.py` lines 41-150 |
| Investor Agents   | `examples/AssetBubble/Rule/players.py` lines 150+   |
| LLM Investors     | `examples/AssetBubble/LLM/players.py`               |
| LLM Prompts       | `examples/AssetBubble/LLM/prompts.py`               |
| RuleLLM Prompts   | `examples/AssetBubble/RuleLLM/prompts.py`           |
| RAG Investors     | `examples/AssetBubble/Rag/players.py`               |
| Runner Script     | `examples/AssetBubble/Rule/run_bubble.py`           |
| Analysis Script   | `examples/AssetBubble/Rule/analysis.py`             |
| Simulation Config | `configs/AssetBubble/Rule/simulation.yml`           |
| Players Config    | `configs/AssetBubble/Rule/players.yml`              |
| Topology Config   | `configs/AssetBubble/Rule/topology.yml`             |
| Persona Config    | `configs/AssetBubble/Rule/persona.yml`              |
| Documentation     | `examples/AssetBubble/Rule/explain.md`              |
| Analysis Guide    | `examples/AssetBubble/Rule/analysis.md`             |

### AssetBubble Key Patterns

**Price Formula Pattern**:
```
P(t+1) = P(t) + λ×NetDemand + γ×[F-P(t)] + ε
```

**Agent Decision Pattern**:
1. Perceive: Extract market info
2. Decide: Apply strategy (rule or LLM)
3. Act: Send order, update state

**Prompt Structure Pattern**:
1. Identity
2. Core Belief
3. Psychology
4. Strategy
5. Constraints
6. Output Format

**Configuration Pattern**:
- All parameters in extras
- Source comments on each
- Consistent path structure

---

## Conclusion

This guide provides a complete methodology for creating financial market simulations. By following the 10 steps and referencing the AssetBubble implementation, you can create rigorous, theory-grounded simulations.

Remember:
1. Ground everything in academic research
2. Document all parameters and their sources
3. Test incrementally
4. Validate against stylized facts
5. Document thoroughly for reproducibility

For questions, refer to the AssetBubble reference files and the troubleshooting section.
