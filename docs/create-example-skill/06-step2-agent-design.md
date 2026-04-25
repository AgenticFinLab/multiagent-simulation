# Step 2: Design Agent Architecture

## Purpose

Translate research findings from Step 1 into a concrete agent design. This step produces the content for `simulation-bases.md §3` (Market Design) and `§4` (Investor Taxonomy). Every design decision made here must be backed by a citation from Step 1.

---

## 2.1 Market Agent Design

The Market is the coordinator that clears all orders and updates the price. Design it before designing any investor.

### 2.1.1 Price Formation Mechanism

**Reference implementation**: `examples/AssetBubble/Rule/players.py` — `Market` class

Choose parameter values for the standard price formula:

```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

For each parameter, make an explicit calibration decision:

**λ (price impact)**:
- Empirical range: 0.01–0.05 (Hasbrouck, 1991, *Journal of Finance*, microstructure estimates)
- Choose higher λ for: bubble/crash simulations (need large price moves from concentrated selling)
- Choose lower λ for: behavioral bias simulations (smaller, persistent deviations from gradual behavior)
- Your choice: [value] — because [reason tied to phenomenon mechanics]

**γ (mean reversion)**:
- Empirical range: 0.005–0.05 (French & Roll, 1986, *Journal of Financial Economics*)
- Choose lower γ for: bubble/bias simulations (mispricing must persist; fast mean reversion destroys the phenomenon)
- Choose higher γ for: crash simulations (need recovery after cascade)
- Your choice: [value] — because [reason]

**σ (noise standard deviation)**:
- Empirical range: 0.01–0.03 per round (Roll, 1984, bid-ask bounce model)
- Too high: noise obscures the phenomenon signal
- Too low: price paths become unrealistically clean
- Typical choice: 0.015–0.02 for most simulations

**F(t) (fundamental value)**:
- Constant vs. growing: constant F is simpler and sufficient for most behavioral bias simulations; growing F is needed for long-horizon simulations
- Standard choice: constant F = 100.0 (normalization — acceptable)

### 2.1.2 Additional Mechanism Decision Table

For EACH market mechanism, make an explicit Yes/No decision:

| Mechanism                         | Include? | Rationale                                             | Implementation trigger                               |
|-----------------------------------|----------|-------------------------------------------------------|------------------------------------------------------|
| Short-selling constraints         | [Yes/No] | [Why]                                                 | [Condition: deviation > threshold; cap at max_short] |
| Short-selling cost                | [Yes/No] | [Why]                                                 | [Cost rate reduces effective short size]             |
| Margin call / forced deleveraging | [Yes/No] | [Why — essential for leverage-based simulations]      | [equity_ratio < threshold → force sell]              |
| Price floor (P ≥ 0.01)            | Yes      | Always — prevents numerical instability               | `new_price = max(new_price, 0.01)`                   |
| Circuit breaker                   | [Yes/No] | [Why — for crash simulations that need trading halts] | [% move trigger]                                     |

### 2.1.3 Information Broadcast Design

Apply the minimal sufficiency principle: broadcast only the information that at least one agent actually needs. Every broadcast field must be justified.

```
Standard broadcast (all simulations):
  price         — current market price (all agents need this)
  fundamental   — intrinsic value (agents making deviation-based decisions)
  deviation     — (price − fundamental) / fundamental (pre-computed for convenience)
  round         — current round number (frequency-controlled agents)

Optional (add only if a specific agent needs it):
  prev_price    — previous price (for agents computing returns in-code)
  return_pct    — return in percentage (for LLM readability in prompts)
  volume        — total shares traded (for volume-sensitive agents)
  bubble_ratio  — price / fundamental (for bubble simulations)
  net_demand    — signed net demand (for agents reading crowd sentiment)
```

**Decision rule**: If no agent in the design uses a field, don't broadcast it.

---

## 2.2 Investor Taxonomy Design

Design 4-6 investor types. Fewer than 4 produces insufficient behavioral diversity; more than 6 makes calibration unwieldy.

### 2.2.1 Taxonomy Design Principles

**Principle 1 — Theory-first**: Start from each theory in `simulation-bases.md §2`. Each theory should produce exactly one investor type.

**Principle 2 — Conflicting incentives**: At least one investor type must be stabilizing (mean-reversion, value-buying) to create the competitive dynamic that makes the phenomenon an emergent property rather than a guaranteed outcome.

**Principle 3 — Role coverage**: Ensure the following roles are covered:
- Primary phenomenon driver: the agent that initiates the target dynamic (destabilizing)
- Amplifier: an agent that makes the phenomenon worse once started (destabilizing)
- Stabilizer: an agent that provides corrective force (stabilizing)
- Background noise: an agent that trades randomly, providing liquidity (neutral)
- Optional: a secondary phenomenon driver or a specialized observer

**Principle 4 — Distinct information sets**: No two investor types should use identical information signals with identical processing. Diversity in information processing is what creates interesting emergent dynamics.

### 2.2.2 Investor Design Worksheet

For EACH investor type (to fill in `simulation-bases.md §4` using the 7-part standard):

```
Investor Type Design Worksheet
================================

Name: [Descriptive name]
Class Name: [PascalCase — e.g., "MomentumSpeculator", "BeliefAnchor"]

Role: [Destabilizing / Stabilizing / Neutral / Amplifying]

Primary Theory (from §2): [Theory name → citation]
  What mechanism from this theory does this agent implement?
  [1-2 sentences]

Trigger Condition:
  What market signal(s) does this agent watch?
  What threshold(s) trigger an action?
  What is the economic rationale for this threshold value?
  (The threshold value must trace to a parameter in §6 with a source citation)

Action When Triggered:
  Buy or Sell?
  How many shares? (formula, not just "a lot")
  What constraints bound the action? (cash, position, leverage cap)

State Variables:
  Does this agent maintain any persistent state across rounds?
  If yes: what is it, how is it initialized, how is it updated each round?
  (E.g., "rolling price history," "belief variable," "anchor price")

Unique Feature:
  What makes this agent different from all others in the simulation?
  What would the simulation lose if this type were removed?

Theory-to-Code Path:
  [Theory mechanism] → [Decision logic] → [Python method]
  This is the direct translation that will appear in explain.md §2 and players.py docstring.
```

### 2.2.3 Diversity Verification

After designing all investor types, verify diversity:

| Criterion              | Required                      | How to Verify                                         |
|------------------------|-------------------------------|-------------------------------------------------------|
| Time horizons          | ≥2 distinct                   | E.g., "high-frequency" vs "position trader"           |
| Information signals    | ≥2 distinct primary signals   | E.g., some use deviation, others use return or volume |
| Risk tolerances        | Range from Low to Extreme     | At least one Low and one High/Extreme                 |
| Conflicting incentives | ≥1 pair buys when others sell | E.g., BlockTradeBuyer buys when PrimeBrokers sell     |
| Stabilizing agents     | ≥1                            | Market would go to zero/infinity without one          |
| Destabilizing agents   | ≥2                            | Needed for cascade/self-reinforcing dynamics          |

---

## 2.3 Communication Structure

All simulations use the same star topology:

```
Topology: Star
Center: Market (1 instance)
Leaves: All investor instances

Message types:
  Market → Investors: broadcast (round start) — carries market state fields
  Investors → Market: order — carries {action, quantity, bid_price}

Synchrony: Synchronous — all investors decide in the same round based on the same broadcast
```

The topology YAML (`topology.yml`) follows the AssetBubble reference exactly for structure. Only the agent names change.

---

## 2.4 LLM Persona Design Principles

For each investor type, the LLM persona is derived from `simulation-bases.md §4.{N}.4.4 Behavioral Properties`. Key rules:

1. **No phenomenon name in prompts**: The system prompt describes the investor's personality, not the market event. "You are a leveraged carry trader" — not "You are trading during a carry trade unwind crisis."

2. **Persona derives from behavioral theory**: Every trait in the persona should trace to a published psychological or behavioral finance study. "Overconfident" must cite Barber & Odean (2001) or similar.

3. **Three-layer persona structure**:
   - Who they are (professional identity, experience)
   - How they process information (cognitive style, biases, heuristics)
   - How they act (decision style, risk tolerance, response to stress)

4. **Canonical output format** (mandatory at end of every system prompt):
   ```
   OUTPUT FORMAT:
   First output your reasoning inside <analysis>...</analysis> tags,
   then output your decision inside <decision>...</decision> tags.
   The decision must be valid JSON:
   {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
   IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
   ```
   Never use `<think>` — always `<analysis>`.

---

## 2.5 Design Validation Before Proceeding

Before moving to Step 3, verify:

**Market design**:
- [ ] λ, γ, σ values chosen with specific literature citations
- [ ] Every broadcast field justified (no orphan fields without a consuming agent)
- [ ] All applicable market mechanisms decided Yes/No with rationale

**Investor taxonomy**:
- [ ] 4-6 investor types designed
- [ ] Every investor maps to exactly one primary theory from §2
- [ ] At least one stabilizing and at least two destabilizing agents
- [ ] No two investors use identical information + processing combination
- [ ] Every trigger threshold has a literature-calibrated value (or explicit approximation)
- [ ] All 7 parts of the investor design standard completable from available research

**Conflict check**:
- [ ] Can you describe a scenario where one agent buys while another sells in the same round?
- [ ] Does the phenomenon still emerge if the stabilizing agents are slightly stronger? (robustness)
