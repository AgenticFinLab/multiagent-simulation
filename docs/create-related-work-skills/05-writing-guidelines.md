# Writing Guidelines

## Purpose

This file specifies how to write a complete `related-work.md` paper entry. It covers the writing order, style rules, ASCII diagram techniques, and section-specific guidance for different paper types.

---

## §1 Writing Order

Always write the components in this specific order. The order matters because each component builds on the previous:

| Order | Component                | Why This Order                                                                        |
|-------|--------------------------|---------------------------------------------------------------------------------------|
| 1     | Core Motivation          | Grounds everything in the problem — prevents method-first thinking                    |
| 2     | Core Idea                | The central insight — drives all other components                                     |
| 3     | Core Method              | Technical implementation — flows from the Core Idea                                   |
| 4     | Example                  | Concretizes the above — catches misunderstandings before they propagate               |
| 5     | Summary                  | Synthesizes 1–4 into a concise overview — only possible after understanding the above |
| 6     | Key Results              | Quantitative grounding — factual, so write last after the conceptual is clear         |
| 7     | Relationship to Our Work | Comparative analysis — requires fully understanding both the paper and our work       |
| 8     | Tags + Metadata          | Final classification — assign CAT and REL only after full understanding               |

**Never write the Summary first.** Summary writing forces premature abstraction before you fully understand the paper.

---

## §2 Style Rules

### Rule 1: Accuracy Over Hype

Never exaggerate claims. Use the exact numbers from the paper.

```
WRONG: "significantly improves performance"
RIGHT: "improves accuracy by 14.1% on GSM8K (Table 4)"

WRONG: "dramatically reduces latency"
RIGHT: "reduces inference latency by 2.4× on A100 GPUs (Figure 6)"
```

### Rule 2: Specific Over Vague

Every statement should be verifiable.

```
WRONG: "Their method processes information differently from prior approaches."
RIGHT: "Their method processes patches at 4 different scales simultaneously using windowed attention,
        while prior methods (ViT-Base) process all patches at a single fixed scale."
```

### Rule 3: Problem First, Method Second

Core Motivation must describe the PROBLEM, not the SOLUTION.

```
WRONG (method-first): "They propose latent reasoning to overcome limitations."
RIGHT (problem-first): "Standard CoT requires generating full natural-language reasoning chains
                        at inference time, creating O(k) token overhead for k reasoning steps.
                        For resource-constrained deployment, this overhead is prohibitive."
```

### Rule 4: Active Voice

```
WRONG: "It is proposed that a hierarchical structure is used."
RIGHT: "The authors propose a hierarchical patch pyramid."
```

### Rule 5: Consistent Terminology

Decide on one term per concept and use it throughout all entries. Create a glossary in `08-quality-standards.md §3` for your project's key terms. When a paper uses a different term for the same concept, note it explicitly:

```
RIGHT: "The authors call their latent vectors 'thought tokens' — equivalent to what we call
        concept vectors throughout this document."
```

### Rule 6: Annotate Tensor Dimensions

When describing neural components, always label tensor shapes:

```
WRONG: "The encoder outputs a hidden state."
RIGHT: "The encoder outputs h ∈ R^{B × L × D} where B = batch size, L = sequence length, D = hidden dim."
```

This forces precision about what is actually happening and reveals architectural differences between methods.

---

## §3 ASCII Diagram Techniques

Use ASCII diagrams extensively — they are the single most powerful tool for making Core Method sections clear.

### §3.1 Architecture Box Diagram

```
┌─────────────────────────────────────────────┐
│  Component Name                             │
├─────────────────────────────────────────────┤
│  Input: [describe type and shape]           │
│    ↓                                        │
│  [Sub-process A]                            │
│    ↓                                        │
│  [Sub-process B]                            │
│    ↓                                        │
│  Output: [describe type and shape]          │
└─────────────────────────────────────────────┘
```

### §3.2 Data Flow Diagram

```
Input X
    ↓
[Encoder / Feature Extractor]
    ↓
Representation Z ∈ R^{d}
    ↓
[Processing Module]
    ↓
Modified Z' ∈ R^{d}
    ↓
[Decoder / Output Head]
    ↓
Output Y
```

### §3.3 Before / After Comparison

```
Standard Method:
  Q → [Process A] → [Process B] → [Process C] → Answer
       [100 tokens]  [120 tokens]  [80 tokens]
       (total: ~300 tokens)

Their Method:
  Q → [Compact Representation] → Answer
       [1 vector, 2048-dim]
       (total: 1 pass, no intermediate tokens)
```

### §3.4 Multi-Phase Architecture

```
Phase 1: Training
  ┌─────────────┐     ┌─────────────┐     ┌──────────┐
  │   Input     │────→│  Ground     │────→│  Target  │
  │   Data      │     │  Truth      │     │          │
  └─────────────┘     └─────────────┘     └──────────┘
         │                   │
         └───────────────────┘
                   ↓
          [Extractor Component]
                   ↓
         Learned Representation

Phase 2: Inference
  ┌─────────────┐
  │   Input     │────→ [Predictor Component] ──→ Output
  └─────────────┘              ↑
                    Learned Representation
```

### §3.5 Formula Block

Use code blocks for mathematical notation:

```
Core Formula:
  Y = f(X) + residual(X)

  where:
    Y         = output representation
    f(X)      = base transformation
    residual  = fine-grained correction term

Or for decomposition:
  Z_total = Z_coarse + Z_fine

  where:
    Z_coarse  = low-resolution / high-level features
    Z_fine    = high-resolution / detail features
```

### §3.6 Hierarchical Structure Diagram

```
Level 0 (coarsest)
  └─→ Level 1 (c_1 = f_1(c_0))
        └─→ Level 2 (c_2 = f_2(c_1))
              └─→ Level 3 (c_3 = f_3(c_2))
                    └─→ Level 4 (finest)
```

### §3.7 Agent / System Interaction Diagram

```
Agent A                 Shared Market               Agent B
    │                        │                          │
    │──── Action (buy) ──────→│                          │
    │                        │──── Price Update ────────→│
    │                        │                          │
    │←─── Market Data ────────│                          │
    │                        │←─── Action (sell) ────────│
    │                        │                          │
    │──────────────────── Round N complete ─────────────→│
```

### §3.8 Diagram Selection Guide

| Diagram Type             | When to Use                            | Section                  |
|--------------------------|----------------------------------------|--------------------------|
| Architecture box         | Model structure with named components  | Core Method              |
| Data flow arrows         | Input → intermediate → output pipeline | Core Idea or Core Method |
| Before/After             | Comparison of baseline vs. method      | Example section          |
| Multi-phase              | Training vs. inference distinction     | Core Method              |
| Formula block            | Mathematical formulation               | Core Idea                |
| Hierarchical             | Nested or recursive structures         | Core Method              |
| Agent/system interaction | Multi-agent or distributed systems     | Core Method or Example   |

### §3.9 ASCII Diagram Rules

- Use `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼` for boxes (box-drawing characters, not regular `-` and `|`)
- Use `→`, `←`, `↑`, `↓` for directed arrows
- Label all components with actual names from the paper (not "Block A", "Block B")
- Label data shapes when relevant: `h ∈ R^{batch × seq × dim}`
- Keep diagrams under 20 lines — break into sub-diagrams if needed
- Always embed diagrams in code blocks (triple backticks) for correct rendering

---

## §4 Section-Specific Writing Guidance

### §4.1 Writing Core Motivation

The Core Motivation is the most important section for accurately positioning the paper. Getting it wrong invalidates everything else.

**Structure**:
```
1. State the domain/task being addressed (1 sentence)
2. Describe what prior approaches do (1-2 sentences)
3. State the specific limitation or gap (1 sentence — the most critical)
4. Explain why this limitation matters (1 sentence — stakes)
```

**Verification**: After writing, check — does this describe a PROBLEM a reasonable researcher would have? If it sounds like a marketing claim rather than a research gap, rewrite.

### §4.2 Writing Core Idea

The Core Idea must be compressible into a single sentence or a visual diagram.

**Test**: If you cannot express the Core Idea in one sentence or one ASCII diagram, you don't understand it yet. Go back and read the paper more carefully.

**Format options**:
```
Option A — Transformation:
"Instead of [doing X the old way], they [do X the new way] by [key mechanism]."

Option B — Formula:
"Their method computes Y = f(X) where f is [key insight about f]."

Option C — Before/After:
"Old method: [description, N tokens/steps/cost]
 Their method: [description, M tokens/steps/cost, where M << N]"
```

### §4.3 Writing Core Method

Depth requirements by relevance:

**Critical/High**:
- Name every component with its exact name from the paper
- Describe the data flow (what goes in, what comes out at each step)
- Include the primary loss function or optimization objective
- Include training procedure (number of phases, special curriculum, etc.)
- Include at least one ASCII diagram

**Medium/Low**:
- 3-5 sentences on the main mechanism
- Name the key components
- No ASCII diagram required

### §4.4 Writing the Example

The Example must be self-contained — a reader with no background should understand the paper's contribution from it alone.

**Required structure**:
```
BEFORE (baseline / standard approach):
  [Input]: [specific value]
  [Process]: [what the baseline does]
  [Output]: [what the baseline produces]
  [Problem]: [what goes wrong or what is expensive]

AFTER (their method):
  [Input]: [same specific value]
  [Process]: [what their method does differently]
  [Output]: [what their method produces]
  [Advantage]: [what is better — be specific]
```

**Example domain selection**:
- NLP / Reasoning: Use a 1-2 sentence math word problem or logic puzzle
- Vision: Use a 3×3 image or a simple "cat vs. dog on white background" scenario
- Finance / Agents: Use a 2-3 agent market with specific prices and quantities
- Systems: Use a 3-node distributed transaction or a 4-row database query
- Theory: Walk through a 2-step proof instance with specific values

**Anti-patterns to avoid**:
- Using domain jargon without defining it
- Making the example abstract ("suppose we have data X...")
- Skipping the BEFORE comparison
- Using a real-world large-scale example (toy problems are better)

### §4.5 Writing the Summary

Write the Summary LAST. It should synthesize Core Motivation + Core Idea + Key Results into 3-6 sentences.

**Required elements**:
1. The paper's method name (if it has one) — 1 sentence
2. The core insight or mechanism — 1-2 sentences
3. The primary quantitative result (include the number) — 1 sentence

**Anti-patterns**:
- Starting with "This paper proposes..." (too generic)
- Including only claims without results
- Exceeding 6 sentences

### §4.6 Writing Section-Specific Paper Types

**For survey/review papers**:
- Core Method describes the taxonomy or framework they develop
- Example shows how a specific method fits into their framework
- Core Idea is the organizing principle they propose

**For analysis/empirical papers**:
- Core Motivation is the question being investigated
- Core Method describes the experimental setup and analysis procedure
- Example shows one specific finding with numbers

**For theoretical papers**:
- Core Idea includes the theorem statement (not just a vague description)
- Core Method is the proof sketch
- Example is a concrete instantiation of the theorem

---

## §5 Document-Level Organization for `related-work.md`

### Section Header Hierarchy

The taxonomy from `04b-paper-classification.md` maps directly to the header levels:

```
## 1. Category Title                           ← ORGANIZATION header (no template)
### 1.1 Sub-Category Title                     ← ORGANIZATION header (no template)
#### 1.1.1 Paper Title (Year)                  ← PAPER entry (needs 9-component template)
##### Summary                                  ← Within a paper entry
##### Core Motivation                          ← Within a paper entry
##### Core Method                              ← Within a paper entry
...

### 1.N Synthesis: [Theme Summary]             ← SYNTHESIS (use format below)
```

| Header Level         | Content               | Needs 9-Component Template? |
|----------------------|-----------------------|-----------------------------|
| `## N.`              | Category              | No                          |
| `### N.M`            | Sub-Category          | No                          |
| `#### N.M.K`         | Paper entry           | **Yes**                     |
| `### N.N Synthesis:` | Synthesis table       | No (own format)             |
| `#####`              | Within-paper sections | N/A                         |

### Synthesis Sections

Synthesis sections tie together multiple papers. Write one at the end of each thematic group:

```
### N.M Synthesis: [Theme Name]

| Method    | [Dim 1 from 00-user-define.md field 7] | [Dim 2] | [Dim 3] | [Key Difference] |
|-----------|----------------------------------------|---------|---------|------------------|
| [Paper A] | ...                                    | ...     | ...     | ...              |
| [Paper B] | ...                                    | ...     | ...     | ...              |
| **Ours**  | ...                                    | ...     | ...     | ...              |

**Gap identified**: [What is missing from the literature that we address?]
**Our position**: [Where does our work fit in this landscape?]
```

### Writing Synthesis Sections

- Use synthesis sections to tell a STORY about the field's evolution
- Highlight tensions and tradeoffs (e.g., accuracy vs. efficiency, realism vs. tractability)
- Explicitly position our work using Research Target and Comparison Dimensions from `00-user-define.md`
- Place "**Ours**" row last in the comparison table for maximal contrast
