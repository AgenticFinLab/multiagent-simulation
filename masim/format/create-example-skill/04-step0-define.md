# Step 0: Define Your Simulation

## Purpose

Before writing a single line of code or documentation, you must produce a clear, grounded definition of the financial phenomenon you want to simulate. This step determines everything that follows.

---

## 0.1 Minimum Required Input

The researcher provides only:

```
SIMULATION DEFINITION
=====================

Name: [PascalCase — e.g., "FlashCrash", "ConfirmationBias", "CarryTradeUnwind"]

Phenomenon Description:
-----------------------
[1-3 paragraphs describing the financial phenomenon to simulate]

Key questions to answer here:
- What happens in this phenomenon? (what is the observable event)
- What are the key characteristics? (timing, intensity, trigger conditions)
- Who are the main participants? (types of investors/institutions involved)
- What makes this phenomenon distinct from other simulations already in this project?
```

---

## 0.2 Name Selection Guidelines

The simulation name becomes a Python package name (PascalCase), a directory name, and appears in all filenames. Choose carefully.

| Criterion   | Guidance                                       | Example                                     |
|-------------|------------------------------------------------|---------------------------------------------|
| PascalCase  | No spaces or underscores                       | `CarryTradeUnwind` not `carry_trade_unwind` |
| Descriptive | Conveys the phenomenon, not just an event      | `ArchegosCollapse` not `MarchCrash`         |
| Distinct    | Not already in `examples/` directory           | Check `ls examples/` first                  |
| Specific    | Refers to a specific mechanism, not a category | `ConfirmationBias` not `CognitiveBias`      |
| Length      | 2-4 words max                                  | `BlackMonday1987` (4 tokens) is acceptable  |

---

## 0.3 Phenomenon Description Quality Criteria

A good phenomenon description answers these questions:

**What is the trigger?** What specific initial condition sets the phenomenon in motion?
- Weak: "Prices fall and people panic."
- Strong: "A single heavily-leveraged fund faces margin calls, forced to liquidate large block positions. Each block sale reduces prices further, triggering additional margin calls at other funds holding the same assets."

**What is the self-reinforcing mechanism?** How does the initial event amplify itself?
- Weak: "The selling continues."
- Strong: "Prime brokers, each knowing that slower liquidation means worse prices as others sell ahead, race to liquidate first. This race-to-liquidate is the core amplification mechanism."

**Who are the participants?** What real-world institution types are involved?
- Weak: "Investors."
- Strong: "A concentrated family office fund (hidden leverage via TRS), two prime brokers (incentivized to liquidate first), opportunistic block trade buyers, and information-trading short sellers."

**What is the resolution?** How does the phenomenon end?
- Weak: "Eventually prices recover."
- Strong: "The cascade ends when: (a) the forced seller's position is exhausted, and (b) opportunistic buyers absorb supply at fire-sale prices, with mean reversion slowly pulling prices back toward fundamental value."

---

## 0.4 AI/Researcher Responsibility

After receiving the minimum input, the researcher (or AI assistant) must independently develop:

1. **Academic literature review** — identify the 3-6 core theories that explain the phenomenon
2. **Historical case studies** — find 1-3 real events with quantitative data
3. **Investor taxonomy** — identify the 4-6 participant types and their behavioral roles
4. **Parameter calibration** — find empirical estimates for all model parameters
5. **Research questions** — formulate 3-5 specific questions answerable through simulation

This is non-trivial work. Budget 2-4 hours of research before writing `simulation-bases.md`. The research quality directly determines the simulation quality.

---

## 0.5 Research Documentation Template

Before writing `simulation-bases.md`, compile research notes in this structure:

```
RESEARCH NOTES — {SimulationName}
==================================

1. Core Theories (3-6)
   For each theory:
   - Full name
   - Citation (full APA with DOI)
   - Key equation
   - Which investor type it motivates
   - Parameter calibration estimate from this work

2. Empirical Stylized Facts
   For each fact:
   - Description
   - Citation
   - Quantitative range (e.g., "bubble lasts 20-40% above fundamental for 6-18 months")

3. Historical Events (2-3)
   For each event:
   - Event name and dates
   - Trigger
   - Timeline of key developments
   - Quantitative data (prices, losses, percentages)
   - Which investors map to which simulation agents

4. Investor Types (4-6)
   For each investor type:
   - Name and class name
   - Market role (stabilizing/destabilizing/neutral)
   - Primary theory basis
   - What information they use
   - When they activate (trigger conditions)
   - How they size positions (order of magnitude)

5. Parameter Estimates
   For each parameter:
   - Name and symbol
   - Empirical range from literature
   - Chosen value
   - Source citation
```

---

## 0.6 Distinctiveness Verification

Before proceeding, check that this simulation is genuinely distinct from existing simulations:

```
Existing simulations in examples/:
[run: ls examples/ | grep -v __init__ | grep -v Demo | grep -v UTEST | grep -v document-sources | grep -v failed]

Does the new simulation differ from all existing ones in:
- [ ] Core mechanism (not just a variation of herding/bubble/crash)
- [ ] Investor types (at least 2 novel types not found in existing simulations)
- [ ] Theoretical basis (at least 1 theory not already primary in an existing simulation)
- [ ] Historical case study (not the same event as an existing simulation)
```

If the simulation is too similar to an existing one, consider extending the existing simulation with a new historical case study in `simulation-bases.md §8` rather than creating a new simulation.

---

## 0.7 Validation Checklist

Before proceeding to Step 1:

- [ ] Name is descriptive, PascalCase, and not already in `examples/`
- [ ] Phenomenon description answers: trigger, mechanism, participants, resolution
- [ ] At least 3 preliminary literature references identified
- [ ] At least 1 historical case study with quantitative data identified
- [ ] 4-6 investor types tentatively identified with distinct behavioral roles
- [ ] Simulation is distinct from existing examples
- [ ] Research notes documented in the template above

**If any item is unchecked, do not proceed to Step 1.** The research foundation determines everything.
