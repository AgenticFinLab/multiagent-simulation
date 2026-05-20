# AssetBubble Rag — RAG-Augmented Hybrid Agent Implementation

## §1 Overview

| Item                       | Description                                                                                                                                                                        |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                | Rag (RAG-augmented hybrid)                                                                                                                                                         |
| **Implements**             | `../simulation-bases.md`                                                                                                                                                           |
| **Players**                | `players.py` — `RagLLMInvestor` base + 5 investor subclasses                                                                                                                       |
| **Prompts**                | `prompts.py` — `== PERSONA ==` + `== DECISION RULES ==` + `{rag_context}`                                                                                                          |
| **Config**                 | `configs/AssetBubble/Rag/`                                                                                                                                                         |
| **Core construction rule** | System prompts define personality and quantitative rules; RAG context is injected dynamically each round from each agent's personal knowledge index — must NOT name the phenomenon |

---

## §2 Theory → Implementation Mapping

> All theoretical foundations are defined in `../simulation-bases.md`. This section records how each agent's RAG persona and rules map to those sections.

### Agent-Level Mapping

| Agent Class              | PERSONA Source                | DECISION RULES Source         | RAG Knowledge Source             | sim-bases Reference        |
|--------------------------|-------------------------------|-------------------------------|----------------------------------|----------------------------|
| `MomentumRagInvestor`    | Overconfident momentum trader | MA5 momentum ≥ 1%: buy        | Momentum crash literature        | `§4 — MomentumSpeculator`  |
| `ArbitrageRagInvestor`   | Rigorous quant analyst        | (P−F)/F ≥ 5%: short with cost | Limits to arbitrage papers       | `§4 — RationalArbitrageur` |
| `NoiseRagInvestor`       | Emotional retail investor     | Sentiment + herding weight    | Behavioral finance overreaction  | `§4 — NoiseTrader`         |
| `FundamentalRagInvestor` | Patient value investor        | Every N rounds: F−P deviation | Value investing & DCF theory     | `§4 — FundamentalInvestor` |
| `LeveragedRagInvestor`   | Aggressive hedge fund manager | Leverage ratio + margin call  | Leverage & deleveraging dynamics | `§4 — LeveragedBuyer`      |

### Market Mechanism Mapping

| Formula Component    | Code Key                                | sim-bases Reference |
|----------------------|-----------------------------------------|---------------------|
| `λ` (price impact)   | `extras["price_impact"]`                | `§3.1`              |
| `γ` (mean reversion) | `extras["mean_reversion"]`              | `§3.1`              |
| `F(t)` (fundamental) | `extras["fundamental_value"]`           | `§3.2`              |
| `ε(t)` (noise)       | `random.gauss(0, noise_std)`            | `§3.3`              |
| RAG top-k chunks     | `rag_store.query(query).formatted_text` | `§7 (variant)`      |

### RAG Pipeline Mapping

| Pipeline Stage       | Code Method                              | sim-bases Reference    |
|----------------------|------------------------------------------|------------------------|
| Index initialization | `_initialize_rag()`                      | `§8 (communication)`   |
| Per-round query      | `_build_prompt(market_data)`             | `§3` (market dynamics) |
| Context injection    | `{rag_context}` in user template         | `§7` (variant)         |
| Document acquisition | `KnowledgeLoader.suggest_and_download()` | `§4` (investor types)  |

---

## §3 Table of Contents

1. [Design Motivation and Core Idea](#1-design-motivation-and-core-idea)
2. [Four-Variant Comparison Framework](#2-four-variant-comparison-framework)
3. [Directory Structure](#3-directory-structure)
4. [System Architecture and Data Flow](#4-system-architecture-and-data-flow)
5. [masim/knowledge Module — Integration Deep-Dive](#5-masimknowledge-module--integration-deep-dive)
6. [RagLLMInvestor Base Class — RAG Pipeline](#6-ragllminvestor-base-class--rag-pipeline)
7. [Prompt Design: Three-Section Structure](#7-prompt-design-three-section-structure)
8. [Configuration System](#8-configuration-system)
9. [Running and Output](#9-running-and-output)
10. [Research Questions and Extensions](#10-research-questions-and-extensions)

---

## §4 Design Motivation and Core Idea

### Background: The Three-Layer Problem

Prior variants each have inherent limitations:

| Variant                          | Strengths                                                | Weaknesses                                                        |
|----------------------------------|----------------------------------------------------------|-------------------------------------------------------------------|
| **AssetBubble** (rule-based)     | Fully interpretable, deterministic, grounded in formulas | No language reasoning, no adaptability, rigid behavior            |
| **AssetBubble LLM** (pure LLM)   | Natural language reasoning, contextual understanding     | No quantitative constraints, decision drift, ungrounded in theory |
| **AssetBubble RuleLLM** (hybrid) | Persona + explicit rules = constrained reasoning         | Knowledge limited to prompt; no external reference material       |

### Solution: Add Personal Knowledge Retrieval

AssetBubble Rag extends RuleLLM by giving each agent a **personal RAG library**:

> **Each agent now has three grounding layers:**
> 1. **PERSONA** — behavioral style, risk attitude, emotional traits
> 2. **DECISION RULES** — quantitative formulas embedded in the system prompt
> 3. **RELEVANT KNOWLEDGE** — top-k chunks retrieved from a personal document library

The third layer is dynamic: at every decision round, the agent formulates a query from current market state, retrieves the most relevant passages from its indexed documents, and injects them into the prompt before calling the LLM.

### Core Innovation

```
RuleLLM:   Persona + Rules → LLM → decision
    ↓ add external knowledge
RagLLM:    Persona + Rules + Retrieved Knowledge → LLM → decision
                                    ↑
                     Personal RAG library built at initialization
                     Query each round → top-k chunks injected into prompt
```

---

## §5 Four-Variant Comparison Framework

```
AssetBubble          ─── pure rule-based (baseline)
    ↓ add natural language reasoning
AssetBubble LLM       ─── pure LLM (persona only, no explicit rules)
    ↓ add quantitative rule constraints
AssetBubble RuleLLM   ─── hybrid (persona + rules embedded in prompt)
    ↓ add external knowledge retrieval
AssetBubble Rag       ─── hybrid + personal RAG knowledge library
```

All four variants share identical:
- Market price dynamics formula
- Total agent count (18 players)
- Initial cash and position settings
- Simulation length (100 rounds)

This enables systematic cross-variant comparison:

| Metric            | Rule | LLM             | RuleLLM        | RagLLM                  |
|-------------------|------|-----------------|----------------|-------------------------|
| Rule adherence    | 100% | N/A             | Partial (±20%) | Partial                 |
| Knowledge breadth | None | Parametric only | Prompt only    | Prompt + Retrieved docs |
| Contextual depth  | None | High            | Medium         | Highest                 |

---

## §6 Directory Structure

```
examples/AssetBubble/Rag/
├── __init__.py              # Module init
├── players.py               # Market + RagLLMInvestor base class + 5 subclasses
├── prompts.py               # 5 system prompts + shared user template with {rag_context}
├── run_bubble_ragllm.py     # Simulation runner script
├── analysis.py              # Analysis script (delegates to AssetBubble/analysis.py)
└── explain.md               # This document

configs/AssetBubble/Rag/
├── simulation.yml           # Global simulation settings (rounds, Ray config)
├── players.yml              # All agent definitions (parameters + LLM + RAG config)
├── topology.yml             # Star topology network
└── persona.yml              # Persistence, monitoring, communication settings

masim/knowledge/              # Shared knowledge infrastructure module
├── __init__.py              # Public exports: KnowledgeLoader, KnowledgeStore, etc.
├── base.py                  # Abstract base classes + dataclasses (contracts)
├── loader.py                # KnowledgeLoader — document acquisition
└── store.py                 # KnowledgeStore — indexing and retrieval
```

---

## §7 System Architecture and Data Flow

### Initialization Phase (Round 1 only)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RagLLMInvestor._initialize_agent()                  │
│                                                                             │
│   ① Portfolio state init                                                    │
│      cash = 10000, position = 0, short_position = 0                         │
│                                                                             │
│   ② LLM client init                                                         │
│      LangChainAPIInference(lm_name, generation_config)                      │
│                                                                             │
│   ③ RAG pipeline init ──────────────────────────────────────────────────── │
│      │                                                                      │
│      ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  KnowledgeStore(embed_model, persist_dir)                           │  │
│   │                                                                      │  │
│   │  IF persist_dir exists and contains index files:                    │  │
│   │      store.load(persist_dir)  → resume from disk                     │  │
│   │  ELSE:                                                              │  │
│   │      KnowledgeLoader.suggest_and_download(persona, llm_client)      │  │
│   │          → List[KnowledgeDocument]                                   │  │
│   │      store.build(docs)  → build index, persist to disk               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Per-Round Decision Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Round N                                        │
│                                                                             │
│   ① perceive() — receive market_data broadcast, append to price_history    │
│                                                                             │
│   ② decide() ───────────────────────────────────────────────────────────── │
│      │                                                                      │
│      ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  _build_prompt(market_data)                                          │  │
│   │                                                                      │  │
│   │  query = KnowledgeQuery(                                             │  │
│   │      text = f"investment strategy when price={price}, P/F={ratio}x", │  │
│   │      top_k = 3                                                       │  │
│   │  )                                                                   │  │
│   │  result = rag_store.query(query)                                     │  │
│   │  rag_context = result.formatted_text  → injected into user prompt    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   LLM call → parse JSON → apply constraints → execute trade                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## §8 masim/knowledge Module — Integration Deep-Dive

This section details how AssetBubble Rag agents use the `masim/knowledge` module.

### Module Overview

The `masim/knowledge` module provides a complete RAG infrastructure:

```
masim/knowledge/
├── base.py      # Abstract contracts + typed dataclasses
├── loader.py    # KnowledgeLoader — acquires documents from sources
└── store.py     # KnowledgeStore — indexes + retrieves via LlamaIndex
```

### Key Imports in players.py

```python
from masim.knowledge import (
    KnowledgeLoader,    # Document acquisition
    KnowledgeStore,     # Vector index + retrieval
    KnowledgeQuery,     # Typed query object
)
```

### Data Classes (defined in base.py)

#### KnowledgeDocument

Atomic unit of acquired knowledge — one parsed document.

```python
@dataclass
class KnowledgeDocument:
    text: str                           # Full text content
    source: str                         # Origin (file path or URL)
    source_type: KnowledgeSourceType    # How it was acquired
    title: str                          # Human-readable title
    acquired_at: str                    # ISO-8601 timestamp
    metadata: Dict[str, Any]            # Additional provenance info
```

#### KnowledgeQuery

Retrieval request submitted by an agent at decision time.

```python
@dataclass
class KnowledgeQuery:
    text: str                    # Natural-language search query
    top_k: int = 3               # Max chunks to retrieve
    round_num: Optional[int]     # For logging only
    agent_id: Optional[str]      # For logging only
```

#### KnowledgeResult

Retrieved chunks returned by the store.

```python
@dataclass
class KnowledgeResult:
    chunks: List[str]            # Ordered by relevance
    query: KnowledgeQuery        # Original query

    @property
    def formatted_text(self) -> str:
        """Returns chunks joined by '\n\n---\n\n'"""
        if self.is_empty:
            return "(No relevant knowledge retrieved for this decision.)"
        return "\n\n---\n\n".join(self.chunks)
```

### KnowledgeLoader — Document Acquisition

`KnowledgeLoader` implements `BaseKnowledgeLoader` with four source methods:

```python
loader = KnowledgeLoader()

# Source 1: Local directory (PDF + Markdown)
docs = loader.load_from_dir("/path/to/docs")

# Source 2: URL CSV file
docs = loader.load_from_url_csv("/path/to/urls.csv")

# Source 3: Explicit URL list
docs = loader.load_from_urls(["https://example.com/article1", ...])

# Source 4: LLM-directed web search (default when no explicit source)
docs = loader.suggest_and_download(
    persona_desc="Momentum investor following Greater Fool Theory...",
    llm_client=llm_client,
    n_urls=5,
    save_dir="EXPERIMENT/AssetBubble/Rag/rag_docs/momentum"
)
```

#### Tool-Use Pattern in suggest_and_download()

The method uses a proper tool-use design (not hallucinated URLs):

```
Step 1: LLM generates search queries (NOT URLs)
        → LLM receives persona description
        → Returns JSON array: ["momentum investing theory", "greater fool theory academic", ...]

Step 2: DuckDuckGo executes each query
        → Returns real URLs with title, snippet, href
        → No hallucination — actual web resources

Step 3: Fetch content from each result URL
        → BeautifulSoup extracts clean text
        → Falls back to snippet if full page fails

Step 4: Cache to save_dir as .txt files
        → Resume support: cached files reused on subsequent runs
```

### KnowledgeStore — Indexing and Retrieval

`KnowledgeStore` implements `BaseKnowledgeStore` using LlamaIndex:

```python
store = KnowledgeStore(
    embed_model_name="doubao-embedding-large-text-240915",
    embed_api_key=os.getenv("ARK_API_KEY"),
    embed_api_base="https://ark.cn-beijing.volces.com/api/v3",
    persist_dir="EXPERIMENT/AssetBubble/Rag/rag_index/momentum",
    chunk_size=512,
    chunk_overlap=64,
)

# Build from documents (first run)
store.build(docs)          # Chunks → Embed → Index → Persist

# Or load from disk (resume)
store.load(persist_dir)

# Query at each decision round
result = store.query(KnowledgeQuery(text="...", top_k=3))
rag_context = result.formatted_text
```

#### Indexing Pipeline

```
List[KnowledgeDocument]
        │
        ▼
Convert to LlamaIndex Document (metadata preserved)
        │
        ▼
SentenceSplitter(chunk_size=512, chunk_overlap=64)
        │
        ▼
OpenAIEmbedding (ARK doubao-embedding-large-text-240915)
        │
        ▼
VectorStoreIndex (in-memory)
        │
        ▼
Persist to persist_dir/ (JSON files)
```

#### Retrieval Pipeline

```
KnowledgeQuery.text
        │
        ▼
Embed query with same model
        │
        ▼
Cosine similarity over VectorStoreIndex
        │
        ▼
Top-k nodes → extract text content
        │
        ▼
KnowledgeResult.chunks (ordered by relevance)
```

---

## §9 RagLLMInvestor Base Class — RAG Pipeline

### perceive() — Initialization Hook

```python
async def perceive(self, observation, prev_result=None):
    round_num = observation.round
    self.state.custom_state["round"] = round_num

    if "cash" not in self.state.custom_state:
        # First round → initialize agent
        await self._initialize_agent()

    # Every round: receive market data
    if observation.inbounds:
        for inb in observation.inbounds:
            market_data = inb.payload
            self.state.custom_state["market_data"] = market_data
            self.state.custom_state["price_history"].append(market_data["price"])
```

### _initialize_agent() — One-Time Setup

```python
async def _initialize_agent(self) -> None:
    extras = self.config.extras

    # 1. Portfolio state
    self.state.custom_state["cash"] = extras["initial_cash"]
    self.state.custom_state["position"] = extras["initial_position"]
    self.state.custom_state["short_position"] = 0.0

    # 2. LLM client
    load_dotenv()
    llm_config = extras["llm"]
    llm_client = LangChainAPIInference(
        lm_name=llm_config["lm_name"],
        generation_config=llm_config["generation_config"],
    )
    self.state.custom_state["llm_client"] = llm_client

    # 3. RAG pipeline
    rag_cfg = extras["rag"]
    await self._initialize_rag(rag_cfg, llm_client, llm_config)
```

### _initialize_rag() — Core RAG Setup

This is where the agent integrates with masim/knowledge:

```python
async def _initialize_rag(self, rag_cfg, llm_client, llm_config) -> None:
    persist_dir = rag_cfg.get("rag_persist_dir")
    embed_model = rag_cfg["embed_model"]
    embed_api_base = rag_cfg["embed_api_base"]
    embed_api_key = os.getenv("ARK_API_KEY", "")

    # Create the store
    rag_store = KnowledgeStore(
        embed_model_name=embed_model,
        embed_api_key=embed_api_key,
        embed_api_base=embed_api_base,
        persist_dir=persist_dir,
    )

    # Resume: check if persisted index already exists
    if persist_dir and os.path.isdir(persist_dir):
        index_files = [f for f in os.listdir(persist_dir) if not f.startswith(".")]
        if index_files:
            logger.info("[%s] Loading persisted RAG index from %s", 
                        self.identity, persist_dir)
            try:
                rag_store.load(persist_dir)
                self.state.custom_state["rag_store"] = rag_store
                self.state.custom_state["rag_cfg"] = rag_cfg
                return  # Resume successful, skip rebuild
            except Exception as exc:
                logger.warning("Failed to load persisted index; rebuilding")

    # First run: load documents and build index
    loader = KnowledgeLoader()

    # Priority chain: docs_dir > url_csv > LLM-suggested
    if rag_cfg.get("docs_dir") and os.path.isdir(rag_cfg["docs_dir"]):
        docs = loader.load_from_dir(rag_cfg["docs_dir"])

    elif rag_cfg.get("url_csv") and os.path.isfile(rag_cfg["url_csv"]):
        docs = loader.load_from_url_csv(rag_cfg["url_csv"])

    else:
        # Default: LLM-directed web search
        system_prompt = load_prompt(llm_config["sys_message"])
        persona_desc = f"{self.__class__.__name__}: {system_prompt[:300]}"
        save_dir = rag_cfg.get("docs_save_dir")
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        docs = loader.suggest_and_download(
            persona_desc=persona_desc,
            llm_client=llm_client,
            n_urls=5,
            save_dir=save_dir,
        )

    # Build and persist the index
    logger.info("[%s] Building RAG index over %d document(s)", 
                self.identity, len(docs))
    rag_store.build(docs)

    self.state.custom_state["rag_store"] = rag_store
    self.state.custom_state["rag_cfg"] = rag_cfg
```

### _build_prompt() — Per-Round Retrieval

```python
def _build_prompt(self, market_data: Dict[str, Any]) -> str:
    rag_store: KnowledgeStore = self.state.custom_state.get("rag_store")
    rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})

    # Retrieve relevant context from RAG library
    rag_context = ""
    if rag_store and rag_store.is_built():
        top_k = rag_cfg.get("top_k", 3)
        
        # Construct query from current market state
        query = KnowledgeQuery(
            text=(
                f"investment strategy when: "
                f"price={market_data['price']:.2f}, "
                f"price/fundamental={market_data['bubble_ratio']:.2f}x, "
                f"momentum={market_data['return_pct']:+.2f}% this round, "
                f"net_demand={market_data['net_demand']:+.2f}"
            ),
            top_k=top_k,
            round_num=round_num,
            agent_id=self.config.identity,
        )
        
        # Execute retrieval
        result = rag_store.query(query)
        rag_context = result.formatted_text  # "\n\n---\n\n"-joined chunks

    if not rag_context:
        rag_context = "(No relevant knowledge retrieved this round.)"

    # Format the user prompt template with rag_context + market data
    template = load_prompt(llm_config["user_message"])
    return template.format(
        rag_context=rag_context,
        round=round_num,
        price=market_data["price"],
        # ... other market fields
    )
```

### Ray Serialization — __getstate__ / __setstate__

LLM clients and RAG stores are not picklable. They must be excluded and reconstructed:

```python
def __getstate__(self):
    state = self.__dict__.copy()
    if "state" in state and hasattr(state["state"], "custom_state"):
        custom = dict(state["state"].custom_state)
        # Exclude non-picklable objects
        for key in ("llm_client", "rag_store"):
            custom.pop(key, None)
        state["state"].custom_state = custom
    return state

def __setstate__(self, state):
    self.__dict__.update(state)
    if hasattr(self, "state") and hasattr(self.state, "custom_state"):
        custom = self.state.custom_state
        
        # Reconstruct LLM client
        if "lm_name" in custom and "llm_client" not in custom:
            custom["llm_client"] = LangChainAPIInference(
                lm_name=custom["lm_name"],
                generation_config=custom["generation_config"],
            )
        
        # Reconstruct RAG store (load persisted index)
        if "rag_cfg" in custom and "rag_store" not in custom:
            rag_cfg = custom["rag_cfg"]
            persist_dir = rag_cfg.get("rag_persist_dir")
            rag_store = KnowledgeStore(
                embed_model_name=rag_cfg["embed_model"],
                embed_api_key=os.getenv("ARK_API_KEY", ""),
                embed_api_base=rag_cfg["embed_api_base"],
                persist_dir=persist_dir,
            )
            if persist_dir and os.path.isdir(persist_dir):
                try:
                    rag_store.load(persist_dir)
                except Exception as exc:
                    logger.warning("RAG store reload failed: %s", exc)
            custom["rag_store"] = rag_store
```

---

## §10 Prompt Design: Three-Section Structure

### System Prompt — PERSONA + DECISION RULES

Identical to AssetBubble RuleLLM:

```
You are an AGGRESSIVE MOMENTUM SPECULATOR in the stock market.

== PERSONA ==
Identity: High-risk, high-reward trend chaser driven by the Greater Fool Theory.
Belief: "I don't care about fundamental value — I care about momentum."
Style: Extremely aggressive. You fear missing big moves more than you fear losses.
Risk tolerance: Very high. You use leverage and large position sizes.
Emotional state: Excited by rising prices, panic-driven selling on sharp reversals.

== DECISION RULES (from Momentum Speculator, Greater Fool Theory) ==

Step 1 — Compute short-term momentum:
    momentum = (current_price - moving_average_5) / moving_average_5

Step 2 — Decide action:
    IF momentum > 0.01:  quantity = 2.0 × momentum × 20 × 2.0 (cap: +100)
    ELIF momentum < -0.02:  quantity = 2.0 × momentum × 20 (floor: -80)
    ELSE: hold
```

### User Prompt — RELEVANT KNOWLEDGE + MARKET STATE

The user template adds a new section for retrieved knowledge:

```
== RELEVANT KNOWLEDGE (from your personal reference library) ==
{rag_context}

== MARKET STATE (Round {round}) ==
- Current Price:           $120.50
- Previous Price:          $118.20
- This Round Return:       +1.94%
- Fundamental Value:       $102.30
- Price/Fundamental Ratio: 1.18x  (>1.0 = overvalued)
- Trading Volume:          245.00 shares
- Net Demand:              +32.50
- Short-Selling Cost:      2.0% per round
- Recent Prices (last 5):  [115.0, 116.3, 117.8, 118.2, 120.5]

== YOUR PORTFOLIO ==
- Cash Available:          $8420.50
- Long Position:           15.00 shares
- Short Position:          0.00 shares
- Portfolio Value:         $10231.00

Apply your DECISION RULES, informed by the relevant knowledge above,
and output your trade decision.

Respond with ONLY valid JSON:
{"action": "buy"|"sell"|"hold", "bid_price": <float>, "quantity": <float>, "reasoning": "<brief>"}
```

### Example rag_context Injection

After retrieval, `{rag_context}` might be replaced with:

```
# Greater Fool Theory and Asset Bubbles

Source: https://en.wikipedia.org/wiki/Greater_fool_theory

The greater fool theory states that the price of an object is determined
not by its intrinsic value, but rather by irrational beliefs and expectations
of market participants. A person buys an overpriced asset with the belief
that they can sell it to someone else at an even higher price...

---

# Momentum Investing Strategies

Source: https://www.investopedia.com/momentum-investing

Momentum investing is a strategy that seeks to capitalize on existing
trends in the market. The strategy assumes that assets that have performed
well in the recent past will continue to perform well...
```

---

## §11 Configuration System

### RAG Configuration Block

Each agent's `extras.rag` section in `players.yml`:

```yaml
rag:
  # Document source (priority: docs_dir > url_csv > LLM-suggested)
  docs_dir: null                    # Local folder with PDF/MD files
  url_csv: null                     # CSV file with "url" column
  docs_save_dir: "EXPERIMENT/.../rag_docs/momentum"   # Cache for fetched docs
  rag_persist_dir: "EXPERIMENT/.../rag_index/momentum" # Persisted index

  # Retrieval settings
  top_k: 3                          # Chunks to retrieve per round

  # Embedding configuration (ARK ByteDance OpenAI-compatible endpoint)
  embed_model: "doubao-embedding-large-text-240915"
  embed_api_base: "https://ark.cn-beijing.volces.com/api/v3"
```

### Document Source Priority Chain

```
1. docs_dir (local files)
   └── Highest priority, no network, deterministic
   └── Use for controlled experiments with curated documents

2. url_csv (CSV-specified URLs)
   └── Medium priority, explicit URLs from file
   └── Use when you know exactly which resources to use

3. LLM-suggested (default)
   └── Fallback when neither above is configured
   └── Agent autonomously discovers relevant resources
   └── Uses tool-use pattern: LLM → search queries → DuckDuckGo → fetch
```

### LLM Configuration Block

```yaml
llm:
  sys_message: "examples.AssetBubble Rag.prompts:RAGLLM_MOMENTUM_SYS"
  user_message: "examples.AssetBubble Rag.prompts:RAGLLM_USER_TEMPLATE"
  lm_name: "ark/doubao-seed-1-6-lite-251015"
  generation_config:
    temperature: 0.3    # Low → more deterministic, stricter rule following
    max_new_tokens: 600
```

### Agent Instance Counts

| Agent Type               | Instances | Rationale                              |
|--------------------------|-----------|----------------------------------------|
| Market                   | 1         | Single coordinator                     |
| RAG Momentum Speculator  | 5         | Most aggressive; primary bubble driver |
| RAG Rational Arbitrageur | 3         | Corrective counterforce                |
| RAG Noise Trader         | 2         | Adds stochastic crowd behavior         |
| RAG Value Investor       | 4         | Long-term stabilizing anchor           |
| RAG Leveraged Buyer      | 3         | Amplifies upswings; triggers crash     |
| **Total**                | **18**    | Identical to all other variants        |

---

## §12 Running and Output

### Running the Simulation

```bash
# Activate environment
conda activate LMSim

# Set API key in .env file
# ARK_API_KEY = your_key_here

# Run simulation (100 rounds)
python examples/AssetBubble/Rag/run_bubble_ragllm.py \
    -c configs/AssetBubble/Rag/simulation.yml

# Run analysis
python examples/AssetBubble/Rag/analysis.py \
    -c configs/AssetBubble/Rag/simulation.yml
```

### Output File Structure

```
EXPERIMENT/AssetBubble/Rag/
├── rag_docs/                       # Cached downloaded documents
│   ├── momentum/
│   │   ├── greater_fool_theory.txt
│   │   └── momentum_investing.txt
│   ├── arbitrageur/
│   ├── noise/
│   ├── value/
│   └── leveraged/
│
├── rag_index/                      # Persisted LlamaIndex indices
│   ├── momentum/                   # (docstore.json, index_store.json, etc.)
│   ├── arbitrageur/
│   ├── noise/
│   ├── value/
│   └── leveraged/
│
├── records/                        # Per-agent state histories
│   ├── market/
│   │   ├── price/
│   │   ├── fundamental/
│   │   └── bubble_metric/
│   ├── ragllm_momentum_1/
│   │   └── price/
│   └── ...
│
└── communication/                  # Message logs
```

### Resume Support

On subsequent runs:
1. `rag_docs/` cached `.txt` files are loaded directly (no re-fetch)
2. `rag_index/` persisted indices are loaded directly (no re-embedding)
3. Only if both are missing does the agent rebuild from scratch

---

## §13 Research Questions and Extensions

### Cross-Variant Comparison Questions

| Question                                                  | RuleLLM vs RagLLM              |
|-----------------------------------------------------------|--------------------------------|
| Does access to external knowledge change bubble severity? | Compare peak P/F ratio         |
| Does retrieved knowledge reduce decision variance?        | Compare quantity std dev       |
| Do agents with RAG better time market exits?              | Compare final portfolio values |
| Does RAG knowledge amplify or dampen herding?             | Compare net demand correlation |

### Extension Possibilities

1. **Shared Knowledge Pool**: All agents query a single shared index (market-wide information)
2. **Dynamic Knowledge Refresh**: Re-fetch documents every N rounds to capture news
3. **Heterogeneous Knowledge**: Different agent types get different document sources
4. **Knowledge Filtering**: Only retrieve documents matching certain themes or dates
5. **Multi-Modal RAG**: Include charts, tables, or numerical data in retrieved context

### Custom Knowledge Sources

To add a new source type (e.g., Bloomberg API, financial database):

1. Subclass `BaseKnowledgeLoader`
2. Implement `load_from_dir`, `load_from_urls`, `load_from_url_csv`, `suggest_and_download`
3. Return `List[KnowledgeDocument]` from each method
4. Reference your custom loader in `_initialize_rag()` instead of the default

---

## §14 Summary

AssetBubble Rag demonstrates how to integrate the `masim/knowledge` module into agent-based simulations:

1. **At initialization**: `KnowledgeLoader` acquires documents → `KnowledgeStore` builds and persists the vector index
2. **At each round**: Agent formulates `KnowledgeQuery` from market state → store returns `KnowledgeResult` → `formatted_text` injected into LLM prompt
3. **On resume**: Persisted index reloaded from disk; no re-indexing or re-fetching

The three-layer grounding (persona + rules + retrieved knowledge) creates agents that are behaviorally consistent, mathematically constrained, and contextually informed.

---

## §15 References

| Topic                                             | Source                                                                        |
|---------------------------------------------------|-------------------------------------------------------------------------------|
| Phenomenon definition + 4 theories                | `../simulation-bases.md §1–§2`                                                |
| Price formula (P(t+1) = P(t) + λ×D + γ×[F−P] + ε) | `../simulation-bases.md §3.1`                                                 |
| All 5 investor type specifications                | `../simulation-bases.md §4`                                                   |
| Full parameter table (24 params)                  | `../simulation-bases.md §6`                                                   |
| Communication structure (star topology)           | `../simulation-bases.md §8`                                                   |
| Cross-variant comparison                          | `../simulation-bases.md §9`                                                   |
| Analysis methodology                              | `../analysis-bases.md`                                                        |
| Limits to Arbitrage theory                        | Shleifer, A. & Vishny, R.W. (1997) *JF* 52(1) — `../simulation-bases.md §2.2` |
| Noise Trader Risk theory                          | De Long et al. (1990) *JPE* 98(4) — `../simulation-bases.md §2.3`             |
| Synchronization Risk theory                       | Abreu & Brunnermeier (2003) *Econometrica* 71 — `../simulation-bases.md §2.4` |
