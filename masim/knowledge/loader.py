"""masim.knowledge.loader — Concrete knowledge acquisition implementation

Implements BaseKnowledgeLoader for the standard MASim use case:

    Source 1 — Local directory : PDF (PyMuPDF) + Markdown files
    Source 2 — URL CSV         : CSV file with a "url" column
    Source 3 — Explicit URLs   : caller-supplied list of HTTP/HTTPS URLs
    Source 4 — LLM-suggested   : LLM recommends URLs from the agent's persona,
                                  then fetches and caches them as .txt files

All public methods return List[KnowledgeDocument] (defined in base.py),
ready to be passed to KnowledgeStore.build().

For the abstract interface and full design documentation, see base.py.

Dependencies (all present in LMSim conda env):
    fitz (PyMuPDF), requests, beautifulsoup4, llama_index_core
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import time
from typing import Any, List, Optional

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup

from masim.knowledge.base import (
    BaseKnowledgeLoader,
    KnowledgeDocument,
    KnowledgeSourceType,
)

logger = logging.getLogger("masim.knowledge.loader")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
_REQUEST_TIMEOUT = 30  # seconds per request (increased from 15)
_REQUEST_MAX_RETRIES = 3  # number of retries for failed requests
_REQUEST_RETRY_DELAY = 2  # seconds between retries


def _slug(text: str, max_len: int = 60) -> str:
    """Convert text to a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:max_len] or "doc"


def _fetch_url_text(url: str) -> Optional[str]:
    """Download a URL and extract clean text.

    Handles both HTML pages (via BeautifulSoup) and PDF files (via PyMuPDF).
    Retries on timeout errors up to _REQUEST_MAX_RETRIES times.
    Returns None on any network/parse error.
    """
    # Check if URL points to a PDF
    is_pdf = url.lower().endswith(".pdf") or ".pdf?" in url.lower()

    for attempt in range(_REQUEST_MAX_RETRIES):
        try:
            resp = requests.get(url, headers=_REQUEST_HEADERS, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()

            # Handle PDF files
            if is_pdf or resp.headers.get("content-type", "").lower().startswith(
                "application/pdf"
            ):
                return _parse_pdf_from_bytes(resp.content)

            # Handle HTML pages
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove script/style noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Collapse excessive blank lines
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text if len(text) > 100 else None

        except requests.exceptions.Timeout as exc:
            if attempt < _REQUEST_MAX_RETRIES - 1:
                logger.warning(
                    "Timeout fetching %s (attempt %d/%d), retrying in %ds...",
                    url,
                    attempt + 1,
                    _REQUEST_MAX_RETRIES,
                    _REQUEST_RETRY_DELAY,
                )
                time.sleep(_REQUEST_RETRY_DELAY)
            else:
                logger.warning(
                    "Failed to fetch %s after %d attempts: %s",
                    url,
                    _REQUEST_MAX_RETRIES,
                    exc,
                )
                return None
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", url, exc)
            return None
    return None


def _parse_pdf_from_bytes(pdf_bytes: bytes) -> Optional[str]:
    """Extract text from PDF bytes using PyMuPDF.

    Parameters
    ----------
    pdf_bytes:
        Raw PDF file content as bytes.

    Returns
    -------
    Optional[str]
        Extracted text, or None if extraction fails or text is too short.
    """
    try:
        import io

        stream = io.BytesIO(pdf_bytes)
        doc = fitz.open(stream=stream, filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        text = "\f".join(pages)
        return text if text.strip() and len(text) > 100 else None
    except Exception as exc:
        logger.warning("Failed to parse PDF from bytes: %s", exc)
        return None


def _parse_pdf(path: str) -> Optional[str]:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(path)
        pages = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        text = "\f".join(pages)
        return text if text.strip() else None
    except Exception as exc:
        logger.warning("Failed to parse PDF %s: %s", path, exc)
        return None


def _parse_markdown(path: str) -> Optional[str]:
    """Read a .md file as plain text."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as exc:
        logger.warning("Failed to read markdown %s: %s", path, exc)
        return None


# ---------------------------------------------------------------------------
# Agent → Document Mapping
# ---------------------------------------------------------------------------

# Default catalog file containing agent-specific book recommendations
DEFAULT_CATALOG_PATH = "examples/document-sources/finance_books.csv"

# Mapping from agent identity patterns to agent_type in the catalog
# Keys are substrings that identify the agent's role; values match the
# agent_type column in finance_books.csv
AGENT_TYPE_MAPPING = {
    "momentum": "momentum_speculator",
    "arbitrageur": "arbitrageur",
    "noise": "noise_trader",
    "value": "value_investor",
    "leveraged": "leveraged_buyer",
}


def resolve_agent_type(identity: str) -> str:
    """Resolve an agent identity to its document type.

    Maps agent identities like "ragllm_momentum_1" or "momentum_speculator"
    to the canonical agent_type used in the document catalog.

    Parameters
    ----------
    identity : str
        Agent identity string (e.g., "ragllm_momentum_1", "arbitrageur_2").

    Returns
    -------
    str
        Canonical agent_type for document lookup.

    Raises
    ------
    ValueError
        If no matching agent_type can be determined.
    """
    identity_lower = identity.lower()

    for pattern, agent_type in AGENT_TYPE_MAPPING.items():
        if pattern in identity_lower:
            return agent_type

    raise ValueError(
        f"Cannot determine agent_type from identity '{identity}'. "
        f"Expected one of: {list(AGENT_TYPE_MAPPING.keys())}"
    )


# ---------------------------------------------------------------------------
# KnowledgeLoader
# ---------------------------------------------------------------------------


class KnowledgeLoader(BaseKnowledgeLoader):
    """Concrete knowledge acquisition implementation.

    Acquires KnowledgeDocument objects from four source types (in priority order):
    local directory, URL CSV, explicit URLs, and LLM-suggested URLs.

    For the full interface contract and design documentation,
    see BaseKnowledgeLoader in base.py.
    """

    # ------------------------------------------------------------------
    # Source 1: local directory
    # ------------------------------------------------------------------

    def load_from_dir(self, folder: str) -> List[KnowledgeDocument]:
        """Load all PDF and .md files recursively from *folder*.

        Parameters
        ----------
        folder:
            Absolute or relative path to the directory.

        Returns
        -------
        List[KnowledgeDocument]
            One Document per successfully parsed file.
        """
        docs: List[KnowledgeDocument] = []
        if not os.path.isdir(folder):
            logger.warning("load_from_dir: folder not found: %s", folder)
            return docs

        for root, _dirs, files in os.walk(folder):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                lower = fname.lower()
                if lower.endswith(".pdf"):
                    text = _parse_pdf(fpath)
                elif lower.endswith(".md"):
                    text = _parse_markdown(fpath)
                else:
                    continue

                if text:
                    docs.append(
                        KnowledgeDocument(
                            text=text,
                            source=fpath,
                            source_type=KnowledgeSourceType.LOCAL_FILE,
                            title=fname,
                            metadata={"filename": fname},
                        )
                    )
                    logger.info("Loaded local file: %s (%d chars)", fname, len(text))

        logger.info("load_from_dir: loaded %d document(s) from %s", len(docs), folder)
        return docs

    # ------------------------------------------------------------------
    # Source 2 / 3: explicit URLs or CSV
    # ------------------------------------------------------------------

    def load_from_urls(self, urls: List[str]) -> List[KnowledgeDocument]:
        """Fetch and parse a list of web-page URLs.

        Parameters
        ----------
        urls:
            List of HTTP/HTTPS URLs to download.

        Returns
        -------
        List[KnowledgeDocument]
            One Document per successfully fetched URL.
        """
        docs: List[KnowledgeDocument] = []
        for url in urls:
            url = url.strip()
            if not url:
                continue
            text = _fetch_url_text(url)
            if text:
                docs.append(
                    KnowledgeDocument(
                        text=text,
                        source=url,
                        source_type=KnowledgeSourceType.WEB_URL,
                        metadata={"url": url},
                    )
                )
                logger.info("Fetched URL: %s (%d chars)", url, len(text))
            time.sleep(0.3)  # polite crawl delay

        logger.info("load_from_urls: loaded %d / %d URL(s)", len(docs), len(urls))
        return docs

    def load_from_url_csv(self, csv_path: str) -> List[KnowledgeDocument]:
        """Read documents from a CSV file with source_type and url columns.

        Supports both web URLs (source_type=web) and local files (source_type=file).

        Parameters
        ----------
        csv_path:
            Path to a CSV file with columns: source_type, url, book_title (optional).

        Returns
        -------
        List[KnowledgeDocument]
        """
        web_urls: List[str] = []
        file_paths: List[tuple[str, str]] = []  # (path, title)

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    source_type = (
                        (row.get("source_type") or row.get("source") or "web")
                        .lower()
                        .strip()
                    )
                    url = row.get("url") or row.get("URL") or ""
                    url = url.strip()
                    title = row.get("book_title") or row.get("title") or ""
                    if not url:
                        continue
                    if source_type == "file":
                        file_paths.append((url, title))
                    else:
                        web_urls.append(url)
        except Exception as exc:
            logger.error("load_from_url_csv: failed to read %s: %s", csv_path, exc)
            return []

        docs: List[KnowledgeDocument] = []

        # Load local files
        for path, title in file_paths:
            text = None
            if path.lower().endswith(".pdf"):
                text = _parse_pdf(path)
            elif path.lower().endswith(".md"):
                text = _parse_markdown(path)
            else:
                # Try to read as text file
                try:
                    with open(path, encoding="utf-8", errors="replace") as f:
                        text = f.read()
                except Exception as exc:
                    logger.warning("Failed to read file %s: %s", path, exc)

            if text:
                docs.append(
                    KnowledgeDocument(
                        text=text,
                        source=path,
                        source_type=KnowledgeSourceType.LOCAL_FILE,
                        title=title or os.path.basename(path),
                        metadata={"filename": os.path.basename(path)},
                    )
                )
                logger.info("Loaded local file: %s (%d chars)", path, len(text))

        # Fetch web URLs
        if web_urls:
            docs.extend(self.load_from_urls(web_urls))

        logger.info(
            "load_from_url_csv: loaded %d docs (%d files, %d web) from %s",
            len(docs),
            len(file_paths),
            len(web_urls),
            csv_path,
        )
        return docs

    # ------------------------------------------------------------------
    # Source 4: LLM-directed web search (tool-use pattern)
    # ------------------------------------------------------------------

    _SEARCH_QUERY_SYSTEM = (
        "You are a research assistant for a financial investor. "
        "When given an investor persona description, you generate precise web "
        "search queries that will find the most relevant and authoritative "
        "financial resources: academic papers, textbook summaries, Investopedia "
        "articles, Wikipedia entries, CFA Institute content, or SSRN abstracts. "
        "Output ONLY valid JSON — no prose, no markdown fences."
    )

    _SEARCH_QUERY_USER = (
        "Persona: {persona_desc}\n\n"
        "Generate exactly {n} concise web search queries to find freely accessible "
        "resources (research papers, articles, Wikipedia/Investopedia pages) that "
        "best cover the financial theory, investment principles, and market behavior "
        "relevant to this persona.\n\n"
        'Output ONLY a JSON array of query strings: ["query 1", "query 2", ...]'
    )

    def suggest_and_download(
        self,
        persona_desc: str,
        llm_client: Any,
        n_urls: int = 5,
        save_dir: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """Use the LLM as a tool caller to find and download relevant documents.

        Flow (proper tool-use pattern):
            1. LLM generates search queries based on the agent persona
               (NOT URLs — this avoids hallucinated links)
            2. DuckDuckGo search executes each query and returns real URLs
            3. Top results are fetched and their content extracted
            4. Documents are cached to *save_dir* for resume support

        If *save_dir* is provided and already contains cached ``.txt`` files,
        those are loaded directly (no LLM call or network requests needed).

        Parameters
        ----------
        persona_desc:
            Short description of the agent's persona / investment style.
            Typically the first 300 chars of the agent's system prompt.
        llm_client:
            A ``LangChainAPIInference`` instance (or any object with a
            ``run([InferInput]) -> InferBatchOutput`` method).
        n_urls:
            Target number of documents to collect (one per search query).
        save_dir:
            Directory to cache downloaded documents as ``.txt`` files.
            If None, documents are returned in memory only.

        Returns
        -------
        List[KnowledgeDocument]
        """
        # --- Check cache first (resume support) ---------------------------------
        if save_dir and os.path.isdir(save_dir):
            cached = [f for f in os.listdir(save_dir) if f.endswith(".txt")]
            if cached:
                logger.info(
                    "suggest_and_download: loading %d cached doc(s) from %s",
                    len(cached),
                    save_dir,
                )
                docs: List[KnowledgeDocument] = []
                for fname in sorted(cached):
                    fpath = os.path.join(save_dir, fname)
                    try:
                        with open(fpath, encoding="utf-8") as f:
                            text = f.read()
                        if text.strip():
                            docs.append(
                                KnowledgeDocument(
                                    text=text,
                                    source=fpath,
                                    source_type=KnowledgeSourceType.CACHED,
                                    metadata={"cached": True},
                                )
                            )
                    except Exception as exc:
                        logger.warning("Cache read error %s: %s", fname, exc)
                if docs:
                    return docs

        # --- Step 1: LLM generates search queries (NOT URLs) --------------------
        logger.info(
            "suggest_and_download: asking LLM for search queries (persona: %s…)",
            persona_desc[:80],
        )
        search_queries: List[str] = []
        try:
            from lmbase.inference.base import InferInput

            user_msg = self._SEARCH_QUERY_USER.format(
                persona_desc=persona_desc, n=n_urls
            )
            infer_input = InferInput(
                system_msg=self._SEARCH_QUERY_SYSTEM, user_msg=user_msg
            )
            batch_output = llm_client.run([infer_input])
            raw = batch_output.outputs[0].response.strip()

            # Parse JSON array of query strings
            clean = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            clean = re.sub(r"```", "", clean).strip()
            parsed = json.loads(clean)
            if isinstance(parsed, list):
                search_queries = [str(q).strip() for q in parsed if str(q).strip()]
        except Exception as exc:
            logger.error("LLM search-query generation failed: %s", exc)

        if not search_queries:
            # Fallback: generate generic queries directly from persona_desc
            logger.warning(
                "suggest_and_download: falling back to persona-derived queries"
            )
            search_queries = [
                f"{persona_desc[:120]} investment strategy financial theory",
                f"{persona_desc[:80]} market behavior academic paper",
            ]

        logger.info(
            "suggest_and_download: LLM generated %d search queries: %s",
            len(search_queries),
            search_queries,
        )

        # --- Step 2: Execute web search to get real URLs ------------------------
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.error(
                "duckduckgo_search not installed. Run: pip install duckduckgo-search"
            )
            return []

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        docs = []
        seen_urls: set = set()

        for query in search_queries[:n_urls]:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=3))
            except Exception as exc:
                logger.warning("DuckDuckGo search failed for %r: %s", query, exc)
                time.sleep(1.0)
                continue

            # --- Step 3: Fetch content from each search result ------------------
            for hit in results:
                url = hit.get("href", "").strip()
                title = hit.get("title", "").strip()
                snippet = hit.get("body", "").strip()

                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                text = _fetch_url_text(url)
                if not text:
                    # Fall back to snippet if full page fetch fails
                    if snippet and len(snippet) > 80:
                        text = f"# {title}\n\nSource: {url}\n\n{snippet}"
                        logger.info(
                            "suggest_and_download: using snippet for %s (%d chars)",
                            url,
                            len(text),
                        )
                    else:
                        logger.warning(
                            "suggest_and_download: skip (no content): %s", url
                        )
                        time.sleep(0.3)
                        continue

                # Prepend title and source as context
                full_text = (
                    f"# {title}\n\nSource: {url}\n\nSearch query: {query}\n\n{text}"
                )

                # Cache to disk
                if save_dir:
                    slug = _slug(title or url)
                    cache_path = os.path.join(save_dir, f"{slug}.txt")
                    try:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            f.write(full_text)
                        logger.info(
                            "suggest_and_download: cached %d chars → %s",
                            len(full_text),
                            cache_path,
                        )
                    except Exception as exc:
                        logger.warning("Cache write error %s: %s", cache_path, exc)

                docs.append(
                    KnowledgeDocument(
                        text=full_text,
                        source=url,
                        source_type=KnowledgeSourceType.LLM_SUGGESTED,
                        title=title,
                        metadata={
                            "url": url,
                            "search_query": query,
                            "snippet": snippet,
                        },
                    )
                )

                if len(docs) >= n_urls:
                    break

            time.sleep(0.5)  # polite crawl delay between queries
            if len(docs) >= n_urls:
                break

        logger.info(
            "suggest_and_download: collected %d document(s) for persona: %s…",
            len(docs),
            persona_desc[:60],
        )
        return docs

    # ------------------------------------------------------------------
    # Agent-autonomous document selection
    # ------------------------------------------------------------------

    def load_for_agent(
        self,
        identity: str,
        catalog_path: Optional[str] = None,
        save_dir: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """Autonomously load documents appropriate for an agent's role.

        This method enables each agent to determine which documents to use
        for RAG based on its identity, without manual configuration.

        The mapping from identity → documents works as follows:
            1. Extract agent_type from identity (e.g., "ragllm_momentum_1" → "momentum_speculator")
            2. Look up URLs from the catalog CSV for that agent_type
            3. Fetch and parse each URL into a KnowledgeDocument

        Parameters
        ----------
        identity : str
            Agent identity string (e.g., "ragllm_momentum_1", "arbitrageur_2").
            Used to determine which documents are relevant.

        catalog_path : str, optional
            Path to the master catalog CSV file.
            If not provided, uses DEFAULT_CATALOG_PATH.

        save_dir : str, optional
            Directory to cache downloaded documents.
            If provided, documents are saved as .txt files for resume support.

        Returns
        -------
        List[KnowledgeDocument]
            Documents appropriate for the agent's role.

        Raises
        ------
        ValueError
            If agent_type cannot be determined from identity.
        FileNotFoundError
            If catalog_path does not exist.

        Example
        -------
        >>> loader = KnowledgeLoader()
        >>> docs = loader.load_for_agent("ragllm_momentum_1")
        >>> print(f"Loaded {len(docs)} documents for momentum speculator")
        """
        agent_type = resolve_agent_type(identity)
        catalog = catalog_path or DEFAULT_CATALOG_PATH

        if not os.path.isfile(catalog):
            raise FileNotFoundError(
                f"Document catalog not found: {catalog}. "
                f"Ensure the file exists or provide a valid catalog_path."
            )

        # Read URLs for this agent_type from the catalog
        urls: List[str] = []
        titles: List[str] = []
        with open(catalog, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_type = row.get("agent_type", "").strip().lower()
                if row_type == agent_type:
                    url = (row.get("url") or row.get("URL") or "").strip()
                    if url:
                        urls.append(url)
                        titles.append(row.get("book_title", url))

        if not urls:
            raise ValueError(
                f"No documents found for agent_type '{agent_type}' in {catalog}. "
                f"Ensure the catalog has an 'agent_type' column with value '{agent_type}'."
            )

        logger.info(
            "load_for_agent: identity='%s' → agent_type='%s' → %d URL(s)",
            identity,
            agent_type,
            len(urls),
        )

        # Fetch and parse documents
        docs: List[KnowledgeDocument] = []
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        for url, title in zip(urls, titles):
            text = _fetch_url_text(url)
            if not text:
                logger.warning("load_for_agent: failed to fetch %s", url)
                continue

            # Prepend title as context
            full_text = f"# {title}\n\nSource: {url}\n\n{text}"

            # Cache to disk if requested
            if save_dir:
                slug = _slug(title or url)
                cache_path = os.path.join(save_dir, f"{slug}.txt")
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(full_text)
                    logger.info("load_for_agent: cached → %s", cache_path)
                except Exception as exc:
                    logger.warning("Cache write error %s: %s", cache_path, exc)

            docs.append(
                KnowledgeDocument(
                    text=full_text,
                    source=url,
                    source_type=KnowledgeSourceType.WEB_URL,
                    title=title,
                    metadata={"agent_type": agent_type, "url": url},
                )
            )

        logger.info(
            "load_for_agent: loaded %d document(s) for %s (agent_type=%s)",
            len(docs),
            identity,
            agent_type,
        )
        return docs
