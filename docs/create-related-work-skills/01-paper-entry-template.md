# Paper Entry Template

## Purpose

Every paper entry in `docs/related-work.md` MUST contain all 9 components listed below, in the order shown. No exceptions. No "Summary only" stubs. No placeholder text.

A paper entry is **complete** when all 9 components are present with substantive, paper-specific content verified against the original paper.

---

## §1 The 9-Component Template (Mandatory)

Use this exact structure for every paper entry. **Header level is `####`** — paper entries are nested under `###` sub-categories (see `04b-paper-classification.md §7` for the full hierarchy):

```markdown
#### N.M.K Full Paper Title (Year)

**[CAT: X] [REL: Y]**

**Paper**: "Full Paper Title"
**Authors**: Author Names (list notable authors)
**Venue**: Conference/Journal Name Year
**Link**: https://arxiv.org/abs/XXXX.XXXXX
**Code**: https://github.com/... (or **Code**: Null)

##### Summary
[3-6 sentences. Overall motivation, core contribution, and key result.]

##### Core Motivation
[Why did the authors write this paper? What problem are they solving?
State the gap in existing work, limitations of prior approaches, and why it matters.
Start with the problem, not the solution.]

##### Core Idea
[What is the single most important insight?
Express as a transformation, formula, or before/after comparison.
Use ASCII code blocks or equations.]

##### Core Method
[How do they implement the core idea?
Step-by-step technical description with architecture details.
Use ASCII diagrams, flowcharts, and pseudocode.
Include: Input [B, L, D] → Process → Output [B, D] pipeline.
Label all tensor dimensions where applicable.]

##### Example
[A concrete, simple, self-contained example.
Show BEFORE (baseline) and AFTER (their method) side by side.
Include token counts, latency, or output format for quantitative comparison.
A reader should understand the paper's contribution from this example alone.]

##### Key Results
[Bullet points with quantitative results: cite Table N / Figure N from the paper.]
- Accuracy: [X]% on [benchmark] (Table N)
- Speedup: [X]× faster than [baseline] (Section N)

##### Relationship to Our Work
[1-2 sentences summarizing the relationship.]

| Aspect                                       | Their Work       | Our Work ({{Research Target from 00-user-define.md}}) |
|----------------------------------------------|------------------|-------------------------------------------------------|
| [Dimension 1 from 00-user-define.md field 7] | [Their approach] | [Our approach]                                        |
| [Dimension 2 from 00-user-define.md field 7] | [Their approach] | [Our approach]                                        |
| [Dimension 3 from 00-user-define.md field 7] | [Their approach] | [Our approach]                                        |
```

---

## §2 Component Specifications

### §2.1 Categorization Tags `[CAT: X] [REL: Y]`

**CAT — Category** (adapt to your field):
- `Core` — directly addresses the same problem or uses the same paradigm
- `Efficiency` — improves speed, memory, or compute
- `Training` — proposes new training objectives or procedures
- `Analysis` — empirical studies, ablations, theoretical analysis
- `Theory` — formal proofs, mathematical frameworks

For domain-specific fields, adapt categories (e.g., for finance simulation: `Market`, `Agent`, `Behavior`, `Methodology`, `Survey`).

**REL — Relevance**:
- `Critical` — directly addresses the same problem or uses nearly identical methods; must be cited
- `High` — strong conceptual overlap or complementary technique; likely to be cited
- `Medium` — related area with useful insights; may be mentioned in passing
- `Low` — peripheral relevance; context only

### §2.2 Paper Metadata

- **Title**: Must exactly match the PDF title (not the arXiv submission title if different)
- **Authors**: List 2-4 most notable authors; add "et al." for 5+
- **Venue**: Spell out the conference/journal name (not just abbreviation): "NeurIPS 2024", not "NIPS"
- **Link**: Use the arXiv abstract page URL (not PDF), or the official conference page
- **Code**: If public GitHub repo exists, include the URL; otherwise `Null`

### §2.3 Summary

- **Length**: 3-6 sentences (shorter for Medium/Low, longer for Critical/High)
- **Content**: Overall motivation + core contribution + key result
- **Style**: Explain what the paper DOES, not just what it CLAIMS
- **Must include**: The paper's method name (if it has one) and at least one quantitative result

### §2.4 Core Motivation

- **Question to answer**: Why did the authors write this paper? What problem are they solving?
- **Structure**: Problem → Gap in prior work → Why this matters
- **Style**: Start with the problem, not the solution
- **Common mistake**: Describing the method instead of the motivation (see `08-quality-standards.md §1.2`)

### §2.5 Core Idea

- **Question to answer**: What is the single most important insight — the "aha" moment?
- **Format**: Express as a transformation (`X → Y`), formula, or before/after comparison
- **Use**: ASCII code blocks or math notation for clarity
- **Length**: 1-3 sentences + 1 diagram or formula

### §2.6 Core Method

- **Question to answer**: How do they implement the core idea?
- **Depth**: Step-by-step technical description; not just "they use attention" but how attention is applied
- **Format**: Prefer ASCII flowcharts and pseudocode
- **Include**: Input → Process → Output pipeline
- **For Critical/High papers**: Full architecture description, loss functions, training procedures
- **For Medium/Low papers**: 3-5 sentences on the main mechanism is sufficient

### §2.7 Example

- **Requirement**: Concrete, simple, self-contained — can be understood without reading the paper
- **Format**: BEFORE (baseline) vs. AFTER (their method) side by side
- **Domain-specific examples**:
  - NLP: Math word problems, logic puzzles, short QA tasks
  - Vision: Small image (e.g., 3×3 patch, cat vs. dog detection)
  - Finance: Small portfolio, 2-agent market with specific prices and quantities
  - Systems: Tiny distributed transaction, 3-node replication scenario
  - Theory: Simple 2-step proof or 4-item problem instance
- **Goal**: A reader should understand the paper's contribution from this example alone

### §2.8 Key Results (Optional but Strongly Recommended)

- Use bullet points
- Include specific numbers: "87.2% accuracy on ImageNet", "3.2× speedup on A100"
- Cite table numbers from the paper: "(Table 3)", "(Figure 5)"
- For Critical/High papers: Required
- For Medium/Low papers: 2-3 bullet points is sufficient

### §2.9 Relationship to Our Work

**Text**: 1-2 sentences summarizing the relationship (similar to / different from our work)

**Comparison table**: MUST include at least 3 rows using dimensions from `00-user-define.md` field 7:
- The "Aspect" column uses the Comparison Dimensions from `00-user-define.md` field 7
- The "Their Work" column is accurate and specific — never vague
- The "Our Work" column references the Research Target from `00-user-define.md` field 2

**Rules**:
- Be specific: "Both use multi-scale processing, but they apply it sequentially while we apply it in parallel" — not "Both use similar techniques"
- Use actual values when available: "Their method requires 50K labeled examples; ours requires 5K"
- If our work is not yet defined, write "TBD — to be filled when our approach is finalized" rather than a vague placeholder

---

## §3 Component Priority by Relevance Level

| Component          | Critical                 | High                 | Medium        | Low                   |
|--------------------|--------------------------|----------------------|---------------|-----------------------|
| CAT + REL tags     | Required                 | Required             | Required      | Required              |
| Metadata           | Required                 | Required             | Required      | Required              |
| Summary            | Full (4-6 sentences)     | Full (3-5 sentences) | 3 sentences   | 2-3 sentences         |
| Core Motivation    | Required                 | Required             | Required      | Brief (1-2 sentences) |
| Core Idea          | Required                 | Required             | Required      | Brief                 |
| Core Method        | Detailed + ASCII diagram | Detailed             | 3-5 sentences | 1-2 sentences         |
| Example            | Required                 | Required             | Encouraged    | Optional              |
| Key Results        | Required                 | Required             | 2-3 bullets   | Optional              |
| Relationship table | ≥4 rows                  | ≥3 rows              | ≥3 rows       | ≥3 rows               |

**Rule**: Even Medium/Low papers must have all 9 sections present structurally — their content may be shorter, but no section may be absent.

---

## §4 Distinguishing Paper Entries from Organization Headers

In `related-work.md`, three header levels serve different purposes:

| Header Level         | Example                              | Content Type    | Needs 9-Component Template? |
|----------------------|--------------------------------------|-----------------|-----------------------------|
| `## N.`              | `## 1. LLM Agent Architectures`      | Category        | No                          |
| `### N.M`            | `### 1.1 Prompt-Based Agents`        | Sub-Category    | No                          |
| `#### N.M.K`         | `#### 1.1.1 GenerativeAgents (2023)` | **Paper entry** | **Yes**                     |
| `### N.N Synthesis:` | `### 1.5 Synthesis: ...`             | Synthesis table | No (own format)             |

**Decision checklist for `####` headers**:
- Has `**Paper**: "..."` line? → It's a paper entry (needs full template)
- Has `[CAT:X] [REL:Y]`? → Already marked as a paper entry
- Has only one sentence and no metadata? → Stub paper (needs upgrade)
- No **Link** line? → Organization or synthesis header (SKIP)
- Title contains "Synthesis:", "Taxonomy:", "Overview:", "Open Questions" → Organization header (SKIP)

**Common organization headers to skip** (use `###` level):
- `### 1.1 Taxonomy of Approaches` — sub-category
- `### 3.1 Synthesis: Trade-offs in the Field` — synthesis section
- `### N. Our Core Research Objective` — positioning section

---

## §5 Synthesis Section Format

At the end of each thematic group, add a synthesis section:

```markdown
### N.M Synthesis: [Theme Name]

| Method   | [Dim 1] | [Dim 2] | [Dim 3] | [Dim 4] |
|----------|---------|---------|---------|---------|
| Paper A  | ...     | ...     | ...     | ...     |
| Paper B  | ...     | ...     | ...     | ...     |
| **Ours** | ...     | ...     | ...     | ...     |

**Gap identified**: [What is missing from the literature?]
**Our position**: [Where does our work fit in this landscape?]
```

Use dimensions from `00-user-define.md` field 7 as the column headers.

---

## §6 Minimal Stub vs. Full Entry

**A stub** (incomplete — must be upgraded):
```
#### 1.1.5 Latent Thinking Optimization (2025)
Shows that latent thoughts naturally encode reward signals.
```

**A full entry** (complete):
```
#### 1.1.5 Latent Thinking Optimization (LTO) (2025)

**[CAT: Training] [REL: High]**

**Paper**: "Latent Thinking Optimization: Self-Improving Language Models via Latent Reasoning"
**Authors**: Smith et al.
**Venue**: ICLR 2025
**Link**: https://arxiv.org/abs/2501.XXXXX
**Code**: Null

##### Summary
[3-5 sentences...]

##### Core Motivation
[Gap in existing work...]

##### Core Idea
[Single insight as transformation/formula...]

##### Core Method
[Step-by-step with ASCII diagram and tensor shapes...]

##### Example
BEFORE: [baseline approach, N tokens]
AFTER: [their method, 1 latent vector of dim D]

##### Key Results
- Achieves X% on benchmark Y (Table 3)
- 1.6× speedup compared to baseline (Section 4.2)

##### Relationship to Our Work
[1-2 sentence relationship summary]

| Aspect | Their Work | Our Work (...) |
|--------|------------|----------------|
| ...    | ...        | ...            |
```
```

→ See `06-batch-processing.md §3` for the complete stub-to-full upgrade pipeline.
