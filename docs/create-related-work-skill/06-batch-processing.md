# Batch Processing

## Purpose

This file specifies how to efficiently process large numbers of papers — both upgrading existing stubs and adding new entries. It covers: phased batch strategies, the stub-to-full upgrade pipeline, cross-section consistency, and bulk scripting patterns.

---

## §1 When to Use Batch Processing

| Scenario               | Approach                                                   |
|------------------------|------------------------------------------------------------|
| 1–3 papers             | Direct individual writing (see `05-writing-guidelines.md`) |
| 4–10 papers            | Parallel browser agents (see `02-search-reactive.md §5`)   |
| 10–20 papers           | Phased batch (see §2 below)                                |
| 20+ papers             | Full phased batch with bulk scripts (see §2 and §4)        |
| All stubs in a section | Stub-to-full pipeline (see §3)                             |

---

## §2 Phased Batch Strategy

### Phase 1: Preparation

Before writing a single word:

1. Run the validation script (`07-validation.md §2`) to identify ALL incomplete papers
2. Categorize papers by relevance — Critical/High get full treatment, Medium/Low get abbreviated
3. Identify organization headers vs. paper entries (`01-paper-entry-template.md §4`)
4. Group papers by topic for efficient context (papers on the same topic can be processed together)
5. Create a local work queue:
   ```
   Critical/High (N papers) → require individual research and writing
   Medium/Low (M papers)    → eligible for bulk structural fill
   Stubs (K papers)         → use stub-to-full pipeline (§3)
   ```

### Phase 2: Parallel Research (Browser Agents)

For Critical/High papers that need research:

1. Launch 4 browser agents simultaneously (do not launch more than 6 at once — quality degrades)
2. Each agent reads 3–4 papers and returns structured extraction output
3. While agents run, write entries for papers you already have full information about
4. After agents return: review output for accuracy, flag any suspicious claims for manual verification
5. Agent prompt template: see `02-search-reactive.md §5`

**Agent grouping rules**:
- Group papers by topic — agents with shared context produce better output
- Do NOT group a survey paper with specific papers it surveys (they will be confused)
- Do NOT group papers that use very similar names for different concepts

### Phase 3: Bulk Generic Content Fill (Optional)

For papers that only need structural completeness (Medium/Low relevance, not yet needing accurate content):

```python
# Bulk add missing sections — ONLY for Medium/Low relevance papers
import re

with open('docs/related-work.md', 'r') as f:
    content = f.read()

# Add a placeholder Core Method section after Core Idea if missing
# This is for structural completeness only — content must be replaced later
def add_missing_method(match):
    block = match.group(0)
    if '#### Core Method' not in block:
        block = block.replace(
            '#### Example',
            '#### Core Method\n[To be completed — see paper for technical details]\n\n#### Example'
        )
    return block

# Apply to each paper block (adjust regex to match your document structure)
content = re.sub(r'(### \d+\.\d+.*?)(?=### \d+\.\d+|\Z)', add_missing_method, content, flags=re.DOTALL)

with open('docs/related-work.md', 'w') as f:
    f.write(content)
```

**When to use bulk scripts**:
- 20+ papers need the same missing sections
- Papers are [REL: Medium] or [REL: Low]
- Time is limited and structural completeness is the immediate goal
- Creates structure that can be refined iteratively

**When NOT to use bulk scripts**:
- [REL: Critical] or [REL: High] papers — these need accurate content
- Papers with unique or complex methods that require custom descriptions
- Survey or analysis papers

### Phase 4: Manual Upgrade of Critical/High Papers

1. Focus exclusively on [REL: Critical] and [REL: High] papers
2. Use agent research outputs as input — verify key claims before writing
3. Write custom Core Method with ASCII diagrams
4. Write concrete, paper-specific Examples with BEFORE/AFTER comparison
5. Cross-check all quantitative claims against the original paper

### Phase 5: Incremental Refinement

1. Re-run validation script
2. Identify papers still missing sections
3. Apply targeted fixes — no bulk scripts in this phase
4. Spot-check bulk-generated content for garbled text or inaccuracies (see §4.2 below)

### Phase 6: Final Validation

1. Run the automated validation script (see `07-validation.md §2`)
2. Confirm 0 incomplete papers (excluding organization headers)
3. Do a final manual read-through of all [REL: Critical] papers

---

## §3 Stub-to-Full Entry Upgrade Pipeline

Many papers start as one-line stubs and must be upgraded to full entries.

**A stub** looks like:
```
### 10.5 Latent Thinking Optimization (LTO) (2025)
Shows that latent thoughts naturally encode reward signals.
```

### Step 1: Research the Paper

```
1. Search arXiv for exact title: site:arxiv.org "Latent Thinking Optimization"
2. Confirm: exact title, arXiv ID, venue, year, authors
3. Read abstract and introduction (minimum for Medium/Low)
4. For Critical/High: full read following 04-reading-extraction.md
```

### Step 2: Extract Structured Information

Use the extraction template from `04-reading-extraction.md §2`:
```
PROBLEM: [1 sentence]
GAP: [1-2 sentences]
INSIGHT: [1 sentence]
METHOD: [3-5 sentences]
RESULT: [1-2 sentences with numbers]
LIMITATIONS: [1 sentence]
CONNECTION: [2-3 sentences vs. our work]
CAT + REL: [with rationale]
```

### Step 3: Write Tags and Metadata

```markdown
**[CAT: Training] [REL: High]**

**Paper**: "Latent Thinking Optimization: Self-Improving Language Models via Latent Reasoning"
**Authors**: Smith, Jones, Lee
**Venue**: ICLR 2025
**Link**: https://arxiv.org/abs/2501.XXXXX
**Code**: Null
```

### Step 4: Expand Each Section

Write in the order from `05-writing-guidelines.md §1`:
1. Core Motivation — from PROBLEM + GAP in extraction
2. Core Idea — from INSIGHT in extraction
3. Core Method — from METHOD in extraction + ASCII diagram
4. Example — BEFORE/AFTER using domain-appropriate toy problem
5. Summary — synthesize the above
6. Key Results — from RESULT in extraction
7. Relationship to Our Work — from CONNECTION + comparison table

### Step 5: Verify

```bash
# Confirm the entry has all required sections
grep -A 50 "10.5 Latent Thinking" docs/related-work.md | grep -E "Summary|Core Motivation|Core Idea|Core Method|Example|Relationship"
```

---

## §4 Bulk Script Patterns

### §4.1 Detect All Stubs (papers with no full sections)

```python
import re

with open('docs/related-work.md') as f:
    content = f.read()

# Find paper headers (headers with CAT/REL tags or **Paper** lines)
# A stub has a header but no #### sections
paper_headers = re.finditer(r'(### \d+\.\d+ .+?\n)', content)
for match in paper_headers:
    pos = match.start()
    # Get the next 500 chars to check for sections
    snippet = content[pos:pos+500]
    if '#### ' not in snippet and '**Paper**' not in snippet:
        print(f"STUB: {match.group(0).strip()}")
```

### §4.2 Detect Garbled Bulk-Script Content

After running bulk scripts that add generic text, always scan for generic placeholder phrases that indicate content was NOT paper-specific:

```bash
# Search for common generic phrases that indicate bulk-generated content
grep -n "Existing methods face challenges" docs/related-work.md
grep -n "novel latent-space techniques" docs/related-work.md
grep -n "To be completed" docs/related-work.md
grep -n "TBD" docs/related-work.md
grep -n "\[Generic" docs/related-work.md
grep -n "improves performance" docs/related-work.md  # vague — should have numbers
```

Replace all matches with paper-specific content.

### §4.3 Detect Missing CAT/REL Tags

```bash
# Find paper entries (those with **Paper** line) that are missing [CAT:] [REL:] tags
python3 -c "
import re
with open('docs/related-work.md') as f:
    content = f.read()

# Find blocks with **Paper** but no [CAT:
for m in re.finditer(r'### \d+\.\d+.*?\n(?:(?!### \d+\.\d+).)+', content, re.DOTALL):
    block = m.group(0)
    if '**Paper**:' in block and '[CAT:' not in block:
        title = re.search(r'### \d+\.\d+ (.+?)\n', block)
        if title:
            print(f'Missing tags: {title.group(1)}')
"
```

### §4.4 Fix `<think>` Tags in Legacy Content

If old entries use deprecated `<think>` notation in examples or method sections:

```python
import re

with open('docs/related-work.md', 'r') as f:
    content = f.read()

# Fix deprecated think tags (only in content, not in code blocks)
# This is a conservative replacement — review output before saving
original = content
content = content.replace('<think>', '<analysis>').replace('</think>', '</analysis>')

if content != original:
    with open('docs/related-work.md', 'w') as f:
        f.write(content)
    print(f"Fixed {original.count('<think>')} think tag(s)")
```

---

## §5 Cross-Section Consistency

Some papers appear in multiple sections (e.g., in a brief overview section AND a detailed technical section). Maintaining consistency between them is mandatory.

### Consistency Rules

1. **Same core facts everywhere**: Method description, key results, and links must match exactly
2. **Section-appropriate emphasis**:
   - Brief overview section: shorter, focuses on high-level contribution and relationship
   - Detailed technical section: longer, focuses on architecture and implementation depth
3. **Same comparison table columns**: Use the same Comparison Dimension names from `00-user-define.md` across all sections
4. **Cross-reference**: Add explicit cross-references between sections: "See §14.10 for detailed technical discussion."

### How to Check for Inconsistencies

```bash
# Find all occurrences of a paper title across the document
PAPER="ExactPaperTitle"
grep -n "$PAPER" docs/related-work.md

# Then manually compare the two entries for:
# - Same link URL
# - Same venue/year
# - Consistent key result numbers
# - Same method description (different depth, same facts)
```

### Resolving Inconsistencies

When two sections describe the same paper differently:
1. Identify the more accurate version (verify against the actual paper)
2. Correct the less accurate version to match
3. Add the cross-reference pointer in both sections
4. Never just delete the less accurate version — the brief section may still serve a purpose

---

## §6 Content Verification After Large Edits

After large `search_replace` operations (especially bulk rewrites):

### Verification Protocol

1. **Grep spot-check**: Search for the modified paper headers to confirm they exist and haven't been split
   ```bash
   grep -c "^### " docs/related-work.md  # count all section headers
   ```

2. **Read sample sections**: Read 20–30 lines after each modified header to confirm content is present

3. **Line count check**: Compare before/after file sizes to confirm additions:
   ```bash
   wc -l docs/related-work.md
   ```

4. **Tag verification**: Confirm `[CAT:X] [REL:Y]` tags were saved correctly:
   ```bash
   grep -c "\[CAT:" docs/related-work.md
   ```

**Important**: The `search_replace` tool may report "save file failed, reason: unknown" but the content IS actually saved. Always verify with `grep` before retrying — a false retry will create duplicate content.
