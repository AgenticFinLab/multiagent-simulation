# Quality Standards

## Purpose

This file collects the quality standards that apply across all entries: common pitfalls to avoid, the "Our Work" reference template used in all comparison tables, terminology glossary guidelines, and relationship table design patterns.

---

## §1 Common Pitfalls and How to Avoid Them

### Pitfall 1: Shallow Summaries

**Bad**: "This paper proposes a new method for image classification."  
**Good**: "This paper proposes a vision transformer with hierarchical attention, which processes images at multiple scales using windowed self-attention and achieves 87.2% accuracy on ImageNet with 30% fewer FLOPs than ViT-Base."

**Bad**: "This paper proposes a new training method."  
**Good**: "This paper proposes contrastive self-supervised pre-training that learns visual representations by maximizing agreement between differently augmented views of the same image, eliminating the need for labeled data, and achieving 75.3% linear evaluation accuracy on ImageNet."

**Rule**: Include the method name, key mechanism, and at least one quantitative result.

---

### Pitfall 2: Confusing Motivation with Method

**Bad** (describes the method, not the problem):  
"They use reinforcement learning to train the model."

**Good** (describes the problem and gap):  
"Prior latent reasoning methods require expensive curriculum learning that suffers from catastrophic forgetting when task difficulty increases. The authors seek a single-stage training approach that avoids this instability without sacrificing reasoning quality."

**Rule**: Core Motivation answers "What problem prompted them to do this work?" — not "What did they do?"

---

### Pitfall 3: Missing Concrete Examples

**Bad**: "Their method compresses reasoning traces."

**Good**:
```
For the problem "If a train travels 60 km/h for 2 hours, how far does it go?":

Standard CoT:
  "First, I need distance. Distance = speed × time. Speed = 60 km/h. Time = 2 hours.
   So distance = 60 × 2 = 120 km." (45 tokens)

Their method:
  Single 2048-dimensional latent vector encoding the same reasoning.
  (1 vector, 1 forward pass — no intermediate tokens generated)
```

**Rule**: A reader should understand the paper's contribution from the Example alone.

---

### Pitfall 4: Vague Relationship Statements

**Bad**: "This is related to our work."

**Good**: "Both approaches use multi-scale processing to capture features at different levels of abstraction, but their method applies scales sequentially (coarse → fine refinement), whereas our approach processes all scales in parallel with cross-scale attention, reducing latency by 40% at inference time."

**Rule**: State specifically: (a) what they share with our work, (b) how they differ, (c) in concrete terms.

---

### Pitfall 5: Inconsistent Terminology

**Bad**: Using "latent vectors" in one entry, "hidden states" in another, "concept embeddings" in a third — all referring to the same concept.

**Good**: Choose one term (e.g., "concept vectors") and use it consistently. When a paper uses a different term, note it: "The authors call these 'thought tokens' — equivalent to our concept vectors."

**Rule**: See §3 (Terminology Glossary) for your project's canonical terms.

---

### Pitfall 6: Unchecked Quantitative Claims

**Bad**: "Their method achieves 10× speedup." (from memory)

**Good**: "Their method achieves 1.6–2.0× speedup on math reasoning benchmarks (Section 4.2, Table 3)."

**Rule**: Always cite the table/figure number. Always verify the number by looking at the paper, not from memory.

---

### Pitfall 7: Garbled Text from Bulk Scripts

**Bad**:
```
Proposes Latent Guidance... Existing methods face challenges in efficiency, scalability,
or adaptability. The authors seek to overcome these limitations through novel
latent-space techniques...
```
(This is generic bulk-script text, not paper-specific content.)

**Good**:
```
Small LLMs struggle with complex multi-step reasoning due to limited capacity for
planning, yet deploying large models at inference time is prohibitively expensive.
The authors ask: can we decouple cognitive planning from linguistic execution by
having a large model generate compact latent guidance vectors that steer a small model?
```

**How to detect**: Run `grep -n "Existing methods face challenges" docs/related-work.md` — any match indicates garbled content.  
**How to fix**: Replace with paper-specific content from the actual paper.

---

### Pitfall 8: Papers Appearing in Multiple Sections with Inconsistent Facts

**Bad**: Writing completely different method descriptions or different result numbers for the same paper in two sections.

**Good**: Same core facts (method, key result, link) everywhere; section-appropriate depth (brief overview section = shorter, technical section = longer).

**How to detect**: `grep -n "ExactPaperTitle" docs/related-work.md` — find all occurrences, then compare.

---

### Pitfall 9: Writing "Summary" First

**Bad**: Starting with the Summary before understanding the paper.

**Good**: Write in order from `05-writing-guidelines.md §1`: Core Motivation → Core Idea → Core Method → Example → Summary.

**Why it matters**: Writing Summary first forces shallow premature abstraction. By the time you write Core Method, you may realize your Summary was wrong.

---

### Pitfall 10: Organization Headers Treated as Paper Entries

**Bad**: Trying to apply the 9-part template to a header like `### 12.5 Synthesis: Trade-offs in the Field`.

**Good**: Identify organization headers using the checklist in `01-paper-entry-template.md §4` and skip them.

---

## §2 "Our Work" Reference Template

When writing "Relationship to Our Work" comparison tables, always compare against the research target from `00-user-define.md`. Use this template to keep it consistent:

```
Our Approach: {{Research Target from 00-user-define.md}}
- Goal: {{Main Motivation from 00-user-define.md}}
- Core Idea: {{Main Idea from 00-user-define.md}}
- Key Techniques:
  - {{Key Technique 1}}
  - {{Key Technique 2}}
  - {{Key Technique 3}}
- Comparison Dimensions: {{Comparison Dimensions from 00-user-define.md}}
```

### Example (filled in for LLM financial simulation):

```
Our Approach: LLM-based multi-agent simulation of financial markets

- Goal: Replicate real-world financial events (bubbles, crashes, collusion) with
  agents whose behavior is grounded in behavioral finance theory

- Core Idea: LLM-driven agents whose system prompts encode named behavioral biases
  (availability heuristic, herding, overconfidence), enabling emergent market dynamics
  that match historical patterns

- Key Techniques:
  - LLM-based multi-agent systems with per-agent persona prompts
  - Behavioral finance theory encoded in prompt design
  - RAG-augmented agents for knowledge retrieval
  - Rule + LLM hybrid variants for controlled comparison

- Comparison Dimensions:
  - Simulation realism (matches historical events)
  - Agent behavioral diversity (range of biases)
  - LLM integration depth (none / surface / deep)
  - Financial phenomenon coverage (bubbles / crashes / collusion)
  - Scalability (number of agents)
  - Interpretability (can we explain agent decisions)
```

### Comparison Table Templates by Paper Type

**For architecture / method papers**:
```
| Aspect                             | Their Work                  | Our Work                             |
|------------------------------------|-----------------------------|--------------------------------------|
| Agent decision mechanism           | [e.g., rule-based / neural] | LLM-driven with behavioral persona   |
| Theory grounding                   | [e.g., none / mathematical] | Behavioral finance theory in prompts |
| LLM integration                    | [e.g., none / post-hoc]     | Core decision-making mechanism       |
| [Other dim from 00-user-define.md] | [their approach]            | [our approach]                       |
```

**For analysis / empirical papers**:
```
| Aspect                             | Their Work                     | Our Work                  |
|------------------------------------|--------------------------------|---------------------------|
| Analysis type                      | [e.g., causal / correlational] | [our approach]            |
| Finding                            | [what they discover]           | [what our work addresses] |
| Scope                              | [narrow / broad]               | [our scope]               |
| [Other dim from 00-user-define.md] | [their approach]               | [our approach]            |
```

**For survey papers**:
```
| Aspect                             | Their Survey           | Our Work             |
|------------------------------------|------------------------|----------------------|
| Coverage                           | [what they cover]      | [what we contribute] |
| Taxonomy                           | [their classification] | [how we fit]         |
| [Other dim from 00-user-define.md] | [their approach]       | [our approach]       |
```

---

## §3 Terminology Glossary

### Why You Need a Glossary

Different papers use different terms for the same concept. Without a glossary, you will drift into inconsistent terminology across entries, making your document harder to read and cross-reference.

### How to Create and Maintain Your Glossary

1. As you read papers, note terms that refer to concepts in your research area
2. Choose ONE canonical term for each concept (usually from the most prominent paper)
3. Note all synonyms used by other papers
4. Update this section whenever you encounter a new synonym

### Glossary Template

Fill this in as you discover terms in your domain:

```
| Canonical Term | Definition         | Synonyms Used by Other Papers      |
|----------------|--------------------|------------------------------------|
| [Your term 1]  | [Clear definition] | [term_A, term_B (used in Paper X)] |
| [Your term 2]  | [Clear definition] | [term_C (used in Paper Y)]         |
```

### Glossary Construction Rules

- Keep it short: 8–12 terms maximum — only domain-specific terms that vary across papers
- When writing an entry that uses a different term, note it: "The authors call these 'X' — equivalent to our canonical term Y"
- Review the glossary before starting each new writing session to maintain consistency

---

## §4 Relationship Table Design Patterns

### Standard Dimensions (Always Include)

Every comparison table should include these dimensions (unless clearly not applicable):

| Dimension                      | What It Captures                                   |
|--------------------------------|----------------------------------------------------|
| [Dim 1 from 00-user-define.md] | Primary comparison axis from your configuration    |
| [Dim 2 from 00-user-define.md] | Secondary comparison axis                          |
| [Dim 3 from 00-user-define.md] | Third comparison axis                              |
| Key Difference                 | One-line summary of the most important distinction |

### Optional Dimensions (Add as Relevant)

| Dimension              | When to Include                                              |
|------------------------|--------------------------------------------------------------|
| Scalability            | When their method has different scaling properties from ours |
| Interpretability       | When explainability is relevant to our comparison dimensions |
| Training requirements  | When data or compute requirements differ significantly       |
| Generalization         | When cross-domain transfer is relevant                       |
| Evaluation methodology | When they evaluate differently from how we evaluate          |

### Table Templates by Paper Category

**For simulation/modeling papers**:
```
| Aspect                   | Their Work   | Our Work |
|--------------------------|--------------|----------|
| Agent decision mechanism | [theirs]     | [ours]   |
| Behavioral realism       | [theirs]     | [ours]   |
| LLM integration          | [theirs]     | [ours]   |
| Phenomenon coverage      | [theirs]     | [ours]   |
| Key difference           | [1 sentence] | —        |
```

**For method/architecture papers**:
```
| Aspect                | Their Work | Our Work |
|-----------------------|------------|----------|
| Primary technique     | [theirs]   | [ours]   |
| Training paradigm     | [theirs]   | [ours]   |
| Key mechanism         | [theirs]   | [ours]   |
| Limitations addressed | [theirs]   | [ours]   |
```

**For survey/review papers**:
```
| Aspect               | Their Survey                       | Our Work       |
|----------------------|------------------------------------|----------------|
| Scope                | [theirs]                           | [ours]         |
| Primary contribution | [theirs]                           | [ours]         |
| Relationship         | [how their survey frames our area] | [our position] |
```

### Table Quality Rules

1. **Never use "N/A"** without explanation — if a dimension genuinely doesn't apply, write "Not applicable — [reason]"
2. **Never use "Similar"** without qualification — say HOW they are similar
3. **Never leave "Our Work" column empty or as "TBD"** — if our work isn't defined yet, write "TBD — pending research direction" so it's clearly intentional
4. **Minimum 3 rows** for all relevance levels
5. **Maximum 6 rows** — tables larger than 6 rows lose clarity; consolidate dimensions if needed

---

## §5 Summary of Key Principles

1. **Every paper gets the full template** — no shortcuts, no "Summary only" stubs
2. **Read before writing** — never write content without reading the paper
3. **Multi-source verification** — for Critical/High: confirm across arXiv, GitHub, OpenReview
4. **Concrete examples** — every paper needs a toy problem BEFORE/AFTER illustration
5. **Systematic comparison** — every paper needs a comparison table with our work
6. **Visual explanations** — use ASCII diagrams for Core Method whenever possible
7. **Iterative validation** — run the validation script after every batch, not just at the end
8. **Bulk then refine** — use bulk scripts for structural completeness; manual upgrade for accuracy
9. **Distinguish headers** — organization headers do not need the full template
10. **Cross-check duplicates** — papers in multiple sections must have consistent facts
11. **Accurate over fast** — a wrong entry is worse than no entry; verify all claims
12. **Configuration-driven** — everything derives from `00-user-define.md`; keep it current
