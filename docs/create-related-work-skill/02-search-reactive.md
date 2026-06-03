# Reactive Search

## Purpose

This file covers **reactive search** — how to properly access, read, verify, and research individual papers that you already know about (by title, author, or recommendation). This is the foundation for processing any paper into a full `related-work.md` entry.

For discovering papers you don't yet know about, see `03-search-proactive.md`.

---

## §1 Paper Access Protocol

### Step 1: Access the Paper

Use this priority order:

1. **Primary source**: Click the arXiv link directly (abstract page, then open PDF)
2. **Conference page**: For papers without arXiv preprints (use DBLP or conference website)
3. **Semantic Scholar**: Use as fallback if neither arXiv nor conference page is found
4. **PDF search**: Search exact title in quotes on Google Scholar as last resort

### Step 2: Structured Reading (in order)

Read the paper in this sequence — do NOT skip steps for Critical/High relevance papers:

| Reading Step        | What to Extract                                                | Notes                                                |
|---------------------|----------------------------------------------------------------|------------------------------------------------------|
| Abstract            | Core claim, methodology overview, key metric                   | Takes 2 min; determines if full read is needed       |
| Introduction        | Problem statement, motivation, gap in prior work               | Most important section for Core Motivation           |
| Method/Architecture | Technical approach, formulas, architecture, training procedure | Most important section for Core Method and Core Idea |
| Experiments         | Datasets, metrics, baselines, key numbers                      | Required for Key Results                             |
| Conclusion          | Confirmed contributions, stated limitations                    | Cross-check with Introduction                        |

For Medium/Low relevance papers: Abstract + Introduction + Key Figure is sufficient.

---

## §2 Multi-Source Verification

Never rely on a single source. For Critical and High relevance papers, verify your understanding across at least 3 sources:

| Priority | Source                               | Reliability | Best For                                                          |
|----------|--------------------------------------|-------------|-------------------------------------------------------------------|
| 1        | arXiv PDF / Official Paper           | Highest     | All technical details; ground truth                               |
| 2        | GitHub Repository (README)           | High        | Implementation details, code verification, clearer explanations   |
| 3        | OpenReview Forum                     | High        | Reviewer questions, author clarifications, limitations discussion |
| 4        | Author Blog Posts / Project Pages    | Medium      | Accessible explanations, visual summaries, motivation             |
| 5        | Twitter/X Threads by authors         | Medium      | Quick insights, community reaction, informal context              |
| 6        | Citing Papers' Related Work sections | Medium      | How the field interprets and positions this work                  |
| 7        | Third-Party Summaries / YouTube      | Low         | Initial orientation only — never use as primary source            |

### GitHub README Check

When a GitHub repo exists:
```
1. Read the README fully
2. Check the "Getting Started" / "Usage" section — often clarifies the pipeline
3. Look at the config files — reveals hyperparameters and architectural choices
4. Check open Issues — reveals known bugs and limitations
5. Check the paper citation format — confirms venue and year
```

### OpenReview Check

For ICLR, NeurIPS, ICML, and other OpenReview-supported venues:
```
URL: https://openreview.net/forum?id=[PAPER_ID]

Read:
- Reviewer scores and comments (reveal limitations and weaknesses)
- Author responses (clarify ambiguities in the paper)
- Meta-reviewer summary (highest-level assessment)
- Post-rebuttal discussion (reveals final standing of any contested claims)
```

---

## §3 Depth-by-Relevance Reading Rules

### [REL: Critical] Papers

- Read the full paper from start to finish
- Read the mathematical formulation carefully; understand every symbol
- Trace the data flow through the architecture
- Identify all assumptions and their implications
- Note all hyperparameters and training details
- Read the appendix if it contains proofs or ablations
- Multi-source verify: arXiv + GitHub + OpenReview minimum
- Time budget: 60–90 minutes per paper

### [REL: High] Papers

- Read Abstract + Introduction fully
- Read Method section carefully
- Read Experiments summary
- Multi-source verify: arXiv + at least 1 other source
- Time budget: 30–45 minutes per paper

### [REL: Medium] Papers

- Read Abstract + Introduction
- Skim Method section for the key insight
- Note the best quantitative result
- Single source (arXiv) is sufficient
- Time budget: 10–15 minutes per paper

### [REL: Low] Papers

- Read Abstract only
- Extract: title, venue, year, core claim, one result
- Single source is sufficient
- Time budget: 3–5 minutes per paper

---

## §4 Iterative Search Strategy (for known papers)

When you start with a known paper and want to find closely related work:

### Round 1: Direct Access
- Search the paper title on arXiv / Google Scholar / Semantic Scholar
- Confirm: year, venue, authors, key claims
- Record the arXiv ID and link immediately

### Round 2: Deep Technical Understanding
- Read full method section
- Extract architecture diagrams and equations
- Understand training procedures and loss functions

### Round 3: Cross-Validation
- Search for blog posts, Twitter discussions, or video explanations
- Check OpenReview for reviewer questions and author responses
- Look at how citing papers describe this work

### Round 4: Connection Mapping
- Explicitly map the paper's approach to our approach (from `00-user-define.md`)
- Identify: similarities, differences, complementary aspects, limitations we address
- Draft the "Relationship to Our Work" comparison table

---

## §5 Parallel Browser Agent Strategy for Multiple Papers

When researching 3+ papers simultaneously, use parallel browser agents for efficiency.

### Agent Prompt Template (proven structure)

```
Research these N papers and return structured information for each.

I need: exact paper title, arxiv/conference link, core motivation, core idea,
core method, and a concrete simple example.

For each paper:
1. Search arxiv.org, openreview.net, google scholar, dblp.org
2. Read the abstract and introduction
3. Read the method section

Return for EACH paper:
- Exact title (must match the PDF)
- Link (arxiv URL or conference page)
- Venue and year
- 2-3 sentence core motivation (what problem they solve, what gap they fill)
- 2-3 sentence core idea (the single key insight, as a transformation or before/after)
- Core method description with ASCII diagram if possible
- Concrete simple example (show BEFORE baseline vs. AFTER their method)
- 2-3 key quantitative results (exact numbers)

Be thorough and accurate. Search multiple sources. Do NOT hallucinate.
If you cannot find a paper, say so explicitly.
```

### Key Prompting Principles

- **Explicit output structure**: Tell the agent exactly what fields to return in what order
- **Multi-source mandate**: Require searching arXiv, OpenReview, AND Google Scholar
- **ASCII diagram request**: Explicitly ask for visual representations
- **Concrete example requirement**: Specify the example domain (math word problems, toy markets, etc.)
- **Accuracy enforcement**: "Do NOT hallucinate" reduces confabulation
- **Missing paper handling**: "If you cannot find it, say so" prevents silent fabrication

### Agent Grouping Strategy

- Group 3–4 related papers per agent (they share context, reducing confusion)
- Group by topic (e.g., all papers about market simulation together)
- Group by venue/year (e.g., all NeurIPS 2024 papers together)
- Do NOT group papers that might confuse each other (e.g., a survey + a specific method with the same topic)

---

## §6 Source Quality Checklist

Before writing any paper entry, confirm:

- [ ] Paper title verified against PDF (not just arXiv title)
- [ ] arXiv link confirmed as resolving to the correct paper
- [ ] Venue and year confirmed (not guessed)
- [ ] Core claim verified against the abstract (not from a third-party summary)
- [ ] Key results verified against Tables/Figures in the paper (include table number)
- [ ] For Critical/High: at least 2 sources consulted (paper + GitHub or OpenReview)
- [ ] Code availability confirmed (GitHub link or confirmed Null)
