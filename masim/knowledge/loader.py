"""masim.knowledge.loader — Concrete knowledge acquisition implementation

Implements BaseKnowledgeLoader for the standard MASim use case:

    Source 1 — Local directory : PDF (MinerU only) + Markdown files
    Source 2 — URL CSV         : CSV file with a "url" column
    Source 3 — Explicit URLs   : caller-supplied list of HTTP/HTTPS URLs
    Source 4 — LLM-suggested   : LLM recommends URLs from the agent's persona,
                                  then fetches and caches them as .txt files

All public methods return List[KnowledgeDocument] (defined in base.py),
ready to be passed to KnowledgeStore.build().

For the abstract interface and full design documentation, see base.py.

Dependencies (all present in LMSim conda env):
    requests, beautifulsoup4, llama_index_core
    Required: MinerU API for PDF parsing (requires MINERU_API_KEY)

Note: PyMuPDF has been removed. All PDF parsing is done through MinerU API.
      Large PDFs are automatically split into 200-page chunks.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import random
import re
import shutil
import tempfile
import time
import zipfile
from typing import Any, List, Optional

# PyMuPDF is ONLY used for PDF splitting (not for text extraction)
# All PDF text extraction is done through MinerU API
import fitz
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

# PDF splitting threshold for MinerU processing
# PDFs exceeding this limit are automatically split into chunks
# Smaller chunks process faster and are more reliable
# No longer a hard limit - large PDFs are processed with dynamic timeouts
MINERU_CHUNK_SIZE = 100  # pages per chunk (reduced from 200 for faster processing)


def _slug(text: str, max_len: int = 60) -> str:
    """Convert text to a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:max_len] or "doc"


def _check_pdf_page_count(pdf_path: str) -> int:
    """Check the page count of a PDF file.

    Uses PyMuPDF (fitz) only for counting pages, not for text extraction.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.

    Returns
    -------
    int
        Number of pages in the PDF, or 0 if error.
    """
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as exc:
        logger.warning(
            "[KNOWLEDGE_LOADER] Failed to check PDF page count for %s: %s",
            pdf_path,
            exc,
        )
        return 0


def _fetch_url_text(url: str, fail_fast: bool = False) -> Optional[str]:
    """Download a URL and extract clean text.

    Handles HTML pages (via BeautifulSoup). PDF files from URLs are not supported
    (use local PDF files with MinerU instead).
    Retries on timeout errors up to _REQUEST_MAX_RETRIES times.

    Parameters
    ----------
    url : str
        URL to fetch.
    fail_fast : bool
        If True, raise exception on error instead of returning None.

    Returns
    -------
    Optional[str]
        Extracted text, or None if fail_fast=False and error occurred.

    Raises
    ------
    RuntimeError
        If fail_fast=True and fetch/parse fails.
    """
    # Check if URL points to a PDF - not supported
    is_pdf = url.lower().endswith(".pdf") or ".pdf?" in url.lower()
    if is_pdf:
        error_msg = f"PDF URLs not supported. Download the PDF locally and use local file path: {url}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
        return None

    for attempt in range(_REQUEST_MAX_RETRIES):
        try:
            resp = requests.get(url, headers=_REQUEST_HEADERS, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()

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
                    "[KNOWLEDGE_LOADER] Timeout fetching %s (attempt %d/%d), retrying in %ds...",
                    url,
                    attempt + 1,
                    _REQUEST_MAX_RETRIES,
                    _REQUEST_RETRY_DELAY,
                )
                time.sleep(_REQUEST_RETRY_DELAY)
            else:
                error_msg = f"Failed to fetch URL after {_REQUEST_MAX_RETRIES} attempts: {url} - Error: {exc}"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                if fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                return None
        except Exception as exc:
            error_msg = f"Failed to fetch URL {url}: {type(exc).__name__}: {exc}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return None
    error_msg = f"Unknown error fetching URL: {url}"
    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
    if fail_fast:
        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
    return None


def _parse_pdf(
    path: str,
    fail_fast: bool = False,
    processed_dir: Optional[str] = None,
) -> Optional[str]:
    """Extract text from a PDF file using MinerU API.

    All PDF parsing is done through MinerU API. Large PDFs (>200 pages)
    are automatically split into smaller chunks and processed separately.

    Processed output is saved to processed_dir (if provided) for caching.

    Parameters
    ----------
    path : str
        Path to the PDF file.
    fail_fast : bool
        If True, raise exception on error instead of returning None.
    processed_dir : str, optional
        Directory to save processed MinerU output. If provided and processed
        file exists, it will be loaded from cache instead of re-processing.

    Returns
    -------
    Optional[str]
        Extracted text in Markdown format, or None if fail_fast=False and extraction fails.

    Raises
    ------
    RuntimeError
        If fail_fast=True and file cannot be parsed by MinerU.
    """
    logger.info("[KNOWLEDGE_LOADER] Attempting to parse PDF with MinerU: %s", path)

    # Check if PDF file exists
    if not os.path.isfile(path):
        error_msg = f"PDF file not found: {path}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
        return None

    # Check if processed file exists (cache hit)
    if processed_dir:
        pdf_name = os.path.splitext(os.path.basename(path))[0]
        cached_md_path = os.path.join(processed_dir, pdf_name, f"{pdf_name}.md")
        if os.path.isfile(cached_md_path):
            logger.info(
                "[KNOWLEDGE_LOADER] Found cached MinerU output for %s: %s",
                path,
                cached_md_path,
            )
            try:
                with open(cached_md_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as exc:
                logger.warning(
                    "[KNOWLEDGE_LOADER] Failed to read cached file %s: %s",
                    cached_md_path,
                    exc,
                )

    # Check for MinerU API key
    if not os.getenv("MINERU_API_KEY", ""):
        error_msg = f"MINERU_API_KEY not set. Cannot parse PDF: {path}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
        return None

    # Use MinerU with automatic PDF splitting for large files
    text = _parse_pdf_with_mineru(path, fail_fast=fail_fast)

    # Save processed output to cache
    if text and processed_dir:
        try:
            pdf_name = os.path.splitext(os.path.basename(path))[0]
            output_subdir = os.path.join(processed_dir, pdf_name)
            os.makedirs(output_subdir, exist_ok=True)
            output_path = os.path.join(output_subdir, f"{pdf_name}.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(
                "[KNOWLEDGE_LOADER] Saved MinerU output to cache: %s",
                output_path,
            )
        except Exception as exc:
            logger.warning(
                "[KNOWLEDGE_LOADER] Failed to save processed output: %s",
                exc,
            )

    return text


def _extract_markdown_from_zip(zip_content: bytes) -> Optional[str]:
    """Extract markdown text from a MinerU result zip file.

    MinerU batch results are returned as zip files containing:
    - <filename>.md  (markdown output)
    - <filename>.json (structured content list)
    - content_list.json

    Parameters
    ----------
    zip_content : bytes
        Raw bytes of the zip file.

    Returns
    -------
    Optional[str]
        Concatenated markdown text, or None if no markdown found.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            md_parts: List[str] = []
            for name in sorted(zf.namelist()):
                if name.endswith(".md") and not name.startswith("__MACOSX"):
                    with zf.open(name) as md_file:
                        md_text = md_file.read().decode("utf-8", errors="replace")
                        if md_text.strip():
                            md_parts.append(md_text)
            if md_parts:
                return "\n\n".join(md_parts)
            logger.warning("[KNOWLEDGE_LOADER] No .md files found in MinerU zip")
            return None
    except Exception as exc:
        logger.error("[KNOWLEDGE_LOADER] Failed to extract markdown from zip: %s", exc)
        return None


def _split_pdf(path: str, max_pages: int = 100) -> List[str]:
    """Split a PDF into smaller chunks that stay within MinerU's page limit.

    Uses PyMuPDF (fitz) ONLY for splitting PDFs into page ranges.
    Text extraction is done by MinerU, not PyMuPDF.
    The caller is responsible for cleaning up the returned paths after processing.

    Parameters
    ----------
    path : str
        Path to the source PDF file.
    max_pages : int
        Maximum pages per split chunk (default 100, reduced for faster processing).

    Returns
    -------
    List[str]
        List of file paths for the split PDF chunks.  Empty list on error.
    """
    try:
        src_doc = fitz.open(path)
        total_pages = len(src_doc)

        if total_pages <= max_pages:
            src_doc.close()
            return [path]

        logger.info(
            "[KNOWLEDGE_LOADER] Splitting PDF %s (%d pages) into chunks of max %d pages",
            path,
            total_pages,
            max_pages,
        )

        tmp_dir = tempfile.mkdtemp(prefix="mineru_split_")
        split_paths: List[str] = []

        for start in range(0, total_pages, max_pages):
            end = min(start + max_pages, total_pages)
            chunk_doc = fitz.open()  # new empty document
            chunk_doc.insert_pdf(src_doc, from_page=start, to_page=end - 1)
            chunk_path = os.path.join(
                tmp_dir,
                f"{os.path.splitext(os.path.basename(path))[0]}_p{start + 1}-{end}.pdf",
            )
            chunk_doc.save(chunk_path)
            chunk_doc.close()
            split_paths.append(chunk_path)
            logger.debug(
                "[KNOWLEDGE_LOADER]   Chunk: pages %d-%d → %s",
                start + 1,
                end,
                chunk_path,
            )

        src_doc.close()
        logger.info("[KNOWLEDGE_LOADER] Split into %d chunks", len(split_paths))
        return split_paths

    except Exception as exc:
        logger.error(
            "[KNOWLEDGE_LOADER] Failed to split PDF %s: %s: %s",
            path,
            type(exc).__name__,
            exc,
        )
        import traceback

        logger.debug(
            "[KNOWLEDGE_LOADER] Split PDF traceback: %s", traceback.format_exc()
        )
        return []


def _mineru_single_pdf(
    path: str,
    api_key: str,
    fail_fast: bool = False,
    max_wait_time: int = 300,
    poll_interval: int = 5,
    max_retries: int = 3,
) -> Optional[str]:
    """Submit *one* PDF to the MinerU batch API and return its Markdown.

    This is a low-level helper called by ``_parse_pdf_with_mineru`` for each
    chunk after optional splitting.

    Workflow:
    1. POST /api/v4/file-urls/batch  → batch_id + upload URLs
    2. PUT  to upload URL            → upload PDF binary
    3. GET  /api/v4/extract-results/batch/{batch_id} → poll until done

    Parameters
    ----------
    path : str
        Path to the PDF file.
    api_key : str
        MinerU API key.
    fail_fast : bool
        If True, raise exception on error instead of returning None.
    max_wait_time : int
        Maximum seconds to wait for processing.
    poll_interval : int
        Seconds between polling requests.
    max_retries : int
        Maximum number of retries for transient errors (ConnectionError, etc).

    Returns
    -------
    Optional[str]
        Extracted markdown text, or None if extraction fails.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Prepare file metadata (name truncated to 16 chars to avoid API issues)
    base_name = os.path.basename(path)
    base_without_ext = os.path.splitext(base_name)[0]
    data_id = base_without_ext[:16] if len(base_without_ext) > 16 else base_without_ext

    # Retry loop for the entire process
    for attempt in range(max_retries):
        try:
            # Step 1: Request batch ID and pre-signed upload URL
            batch_url = "https://mineru.net/api/v4/file-urls/batch"
            batch_data = {
                "enable_formula": True,
                "language": "en",
                "layout_model": "doclayout_yolo",
                "enable_table": True,
                "files": [
                    {
                        "name": base_name,
                        "data_id": data_id,
                        "language": "en",
                    }
                ],
            }

            logger.info(
                "[KNOWLEDGE_LOADER] Requesting MinerU batch upload URL for: %s (attempt %d/%d)",
                path,
                attempt + 1,
                max_retries,
            )
            batch_response = requests.post(
                batch_url, headers=headers, json=batch_data, timeout=60
            )
            batch_response.raise_for_status()
            batch_result = batch_response.json()

            if batch_result.get("code") != 0:
                error_msg = f"MinerU batch request failed: {batch_result.get('msg', 'Unknown error')}"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                if fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                return None

            batch_id = batch_result["data"]["batch_id"]
            upload_urls = batch_result["data"]["file_urls"]

            if not upload_urls:
                error_msg = "MinerU batch request returned no upload URLs"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                if fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                return None

            upload_url = upload_urls[0]
            logger.info(
                "[KNOWLEDGE_LOADER] MinerU batch created: %s, uploading file...",
                batch_id,
            )

            # Step 2: Upload file via PUT to the pre-signed URL
            with open(path, "rb") as f:
                upload_response = requests.put(upload_url, data=f, timeout=120)
                if upload_response.status_code not in [200, 201]:
                    error_msg = (
                        f"MinerU file upload failed: HTTP {upload_response.status_code}"
                    )
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    if fail_fast:
                        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                    return None

            logger.info(
                "[KNOWLEDGE_LOADER] PDF uploaded to MinerU, polling for results: %s",
                batch_id,
            )

            # Step 3: Poll for results using the correct batch result endpoint
            # NOTE: /api/v4/extract-results/batch/{batch_id} is the correct endpoint
            # for batch uploads, NOT /api/v4/extract/task/{batch_id}
            result_url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                logger.debug("[KNOWLEDGE_LOADER] Polling MinerU batch: %s", batch_id)
                result_response = requests.get(
                    result_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30,
                )
                result_response.raise_for_status()
                result_data = result_response.json()

                if result_data.get("code") != 0:
                    error_msg = f"MinerU result query failed: {result_data.get('msg', 'Unknown error')}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    if fail_fast:
                        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                    return None

                # Batch results contain an "extract_result" list with per-file status
                extract_results = result_data.get("data", {}).get("extract_result", [])

                if not extract_results:
                    # No results yet, still processing
                    time.sleep(poll_interval)
                    continue

                # Check the status of our single file in the batch
                file_result = extract_results[0]  # We only submitted one file
                state = file_result.get("state", "")

                if state == "done":
                    # Download markdown content from the result zip
                    # MinerU batch results use "full_zip_url" field (contains .md + .json)
                    download_url = (
                        file_result.get("full_zip_url", "")
                        or file_result.get("zip_url", "")
                        or file_result.get("markdown", "")
                    )

                    if download_url:
                        logger.info(
                            "[KNOWLEDGE_LOADER] MinerU batch complete, downloading result: %s",
                            batch_id,
                        )
                        dl_response = requests.get(download_url, timeout=60)
                        dl_response.raise_for_status()

                        # Result may be a zip file containing markdown + json
                        content_type = dl_response.headers.get("Content-Type", "")
                        if "zip" in content_type or download_url.endswith(".zip"):
                            text = _extract_markdown_from_zip(dl_response.content)
                        else:
                            text = dl_response.text

                        if text and text.strip():
                            logger.info(
                                "[KNOWLEDGE_LOADER] MinerU chunk done: path=%s, chars=%d",
                                path,
                                len(text),
                            )
                            return text
                        else:
                            logger.warning(
                                "[KNOWLEDGE_LOADER] MinerU returned empty content for: %s",
                                path,
                            )
                            if fail_fast:
                                raise RuntimeError(
                                    f"[KNOWLEDGE_LOADER] MinerU returned empty content for: {path}"
                                )
                            return None
                    else:
                        logger.warning(
                            "[KNOWLEDGE_LOADER] MinerU result missing download URL: %s",
                            path,
                        )
                        if fail_fast:
                            raise RuntimeError(
                                f"[KNOWLEDGE_LOADER] MinerU result missing download URL for: {path}"
                            )
                        return None

                elif state == "failed":
                    err_msg = file_result.get("err_msg", "Unknown error")
                    error_msg = f"MinerU file parsing failed: {err_msg}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    if fail_fast:
                        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                    return None

                # Task still processing, wait and poll again
                time.sleep(poll_interval)

            # Timeout
            error_msg = f"MinerU batch timeout after {max_wait_time}s: {batch_id}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return None

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as exc:
            logger.warning(
                "[KNOWLEDGE_LOADER] MinerU connection error on attempt %d/%d for %s: %s",
                attempt + 1,
                max_retries,
                path,
                exc,
            )
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                wait_time = (2**attempt) + random.uniform(0, 1)
                logger.info("[KNOWLEDGE_LOADER] Retrying in %.1f seconds...", wait_time)
                time.sleep(wait_time)
                continue
            else:
                logger.error(
                    "[KNOWLEDGE_LOADER] MinerU failed after %d attempts for %s",
                    max_retries,
                    path,
                )
                if fail_fast:
                    raise RuntimeError(
                        f"[KNOWLEDGE_LOADER] MinerU API connection failed after {max_retries} attempts for {path}: {exc}"
                    )
                return None
        except requests.exceptions.RequestException as exc:
            logger.error(
                "[KNOWLEDGE_LOADER] MinerU API request failed for %s: %s", path, exc
            )
            if fail_fast:
                raise RuntimeError(
                    f"[KNOWLEDGE_LOADER] MinerU API request failed for {path}: {exc}"
                )
            return None


def _calculate_mineru_timeout(page_count: int, base_timeout: int = 1800) -> int:
    """Calculate MinerU timeout based on PDF page count.

    Larger PDFs need more processing time. This function provides
    a dynamic timeout that scales with document size.

    Note: MinerU API can be extremely slow for complex PDFs. Based on
    observed behavior, even 100-page chunks can take 30+ minutes.
    Timeouts are set very generously (3x previous values) to ensure
    processing completes without timeout errors.

    Parameters
    ----------
    page_count : int
        Number of pages in the PDF.
    base_timeout : int
        Base timeout in seconds for small PDFs (default 1800s = 30 min).

    Returns
    -------
    int
        Calculated timeout in seconds.
    """
    if page_count <= 50:
        # Small PDFs: base timeout (30 min)
        return base_timeout
    elif page_count <= 100:
        # Medium PDFs: 1.5x base timeout (45 min)
        return int(base_timeout * 1.5)
    elif page_count <= 200:
        # Large PDFs: 2x base timeout (60 min)
        return base_timeout * 2
    elif page_count <= 500:
        # Very large PDFs: 3x base timeout (90 min)
        return base_timeout * 3
    else:
        # Extremely large PDFs: 4x base timeout (120 min per chunk)
        return base_timeout * 4


def _parse_pdf_with_mineru(
    path: str,
    fail_fast: bool = False,
    max_wait_time: Optional[int] = None,
    poll_interval: int = 5,
    max_retries: int = 3,
) -> Optional[str]:
    """Extract text from a PDF file using MinerU API (batch workflow).

    Automatically splits PDFs that exceed MINERU_CHUNK_SIZE (100 pages) into
    smaller chunks, processes each chunk separately, and concatenates
    the results. Smaller chunks are more reliable and process faster.

    Timeout is dynamically calculated based on PDF page count to ensure
    large documents have sufficient processing time (up to 40 min per chunk).

    Workflow per chunk:
    1. POST /api/v4/file-urls/batch  — get batch_id + pre-signed upload URLs
    2. PUT to each upload URL        — upload PDF binary
    3. GET /api/v4/extract-results/batch/{batch_id} — poll until done, download markdown

    Parameters
    ----------
    path : str
        Path to the PDF file.
    fail_fast : bool
        If True, raise exception on error instead of returning None.
    max_wait_time : int, optional
        Maximum seconds to wait per chunk for MinerU processing.
        If not provided, calculated dynamically based on PDF page count.
    poll_interval : int
        Seconds between polling requests, default 5.
    max_retries : int
        Maximum number of retries for transient errors per chunk.

    Returns
    -------
    Optional[str]
        Extracted text in Markdown format, or None if fail_fast=False and extraction fails.

    Raises
    ------
    RuntimeError
        If fail_fast=True and file cannot be parsed.
    """
    api_key = os.getenv("MINERU_API_KEY", "")
    if not api_key:
        logger.warning(
            "[KNOWLEDGE_LOADER] MINERU_API_KEY not set, skipping MinerU PDF parsing for: %s",
            path,
        )
        if fail_fast:
            raise RuntimeError(
                f"[KNOWLEDGE_LOADER] MINERU_API_KEY not set and PDF has no extractable text: {path}"
            )
        return None

    # Get PDF page count for dynamic timeout calculation
    total_pages = _check_pdf_page_count(path)
    if total_pages == 0:
        logger.warning(
            "[KNOWLEDGE_LOADER] Could not determine page count for: %s", path
        )
        total_pages = 100  # Assume medium size as fallback

    # Calculate dynamic timeout if not explicitly provided
    if max_wait_time is None:
        max_wait_time = _calculate_mineru_timeout(total_pages)

    logger.info(
        "[KNOWLEDGE_LOADER] Attempting to parse PDF with MinerU API: %s (%d pages, timeout: %ds)",
        path,
        total_pages,
        max_wait_time,
    )

    try:
        # Split PDF if it exceeds MinerU's 200-page limit
        split_paths = _split_pdf(path, max_pages=MINERU_CHUNK_SIZE)

        if not split_paths:
            error_msg = f"Failed to split PDF for MinerU processing: {path}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return None

        # Determine the temp directory (for cleanup later) if we split the file
        tmp_dir = None
        if len(split_paths) > 1:
            tmp_dir = os.path.dirname(split_paths[0])
            logger.info(
                "[KNOWLEDGE_LOADER] Processing %d PDF chunks sequentially (total %d pages)",
                len(split_paths),
                total_pages,
            )

        # Process each chunk and collect results
        all_texts: List[str] = []
        try:
            for i, chunk_path in enumerate(split_paths):
                # Calculate per-chunk timeout based on chunk size
                chunk_pages = _check_pdf_page_count(chunk_path)
                chunk_timeout = _calculate_mineru_timeout(chunk_pages)

                logger.info(
                    "[KNOWLEDGE_LOADER] Processing chunk %d/%d: %s (%d pages, timeout: %ds)",
                    i + 1,
                    len(split_paths),
                    os.path.basename(chunk_path),
                    chunk_pages,
                    chunk_timeout,
                )
                chunk_text = _mineru_single_pdf(
                    chunk_path,
                    api_key=api_key,
                    fail_fast=fail_fast,
                    max_wait_time=chunk_timeout,
                    poll_interval=poll_interval,
                    max_retries=max_retries,
                )
                if chunk_text:
                    all_texts.append(chunk_text)
                else:
                    logger.warning(
                        "[KNOWLEDGE_LOADER] Chunk %d/%d returned no text: %s",
                        i + 1,
                        len(split_paths),
                        chunk_path,
                    )
        finally:
            # Clean up temporary split files
            if tmp_dir and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
                logger.debug(
                    "[KNOWLEDGE_LOADER] Cleaned up temp split dir: %s", tmp_dir
                )

        if not all_texts:
            logger.warning(
                "[KNOWLEDGE_LOADER] All MinerU chunks returned empty for: %s", path
            )
            if fail_fast:
                raise RuntimeError(
                    f"[KNOWLEDGE_LOADER] MinerU returned empty content for all chunks: {path}"
                )
            return None

        combined_text = "\n\n".join(all_texts)
        logger.info(
            "[KNOWLEDGE_LOADER] Successfully parsed PDF with MinerU: path=%s, chars=%d (from %d chunks)",
            path,
            len(combined_text),
            len(all_texts),
        )
        return combined_text

    except requests.exceptions.RequestException as exc:
        error_msg = f"MinerU API request failed for {path}: {type(exc).__name__}: {exc}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
        return None
    except Exception as exc:
        error_msg = f"MinerU parsing failed for {path}: {type(exc).__name__}: {exc}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
        return None


def _parse_markdown(path: str, fail_fast: bool = False) -> Optional[str]:
    """Read a .md file as plain text.

    Parameters
    ----------
    path : str
        Path to the markdown file.
    fail_fast : bool
        If True, raise exception on error instead of returning None.

    Returns
    -------
    Optional[str]
        File contents, or None if fail_fast=False and read fails.

    Raises
    ------
    RuntimeError
        If fail_fast=True and file cannot be read.
    """
    logger.info("[KNOWLEDGE_LOADER] Attempting to read markdown file: %s", path)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        logger.info(
            "[KNOWLEDGE_LOADER] Successfully read markdown: path=%s, chars=%d",
            path,
            len(content),
        )
        return content
    except Exception as exc:
        error_msg = f"Failed to read markdown file {path}: {type(exc).__name__}: {exc}"
        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
        if fail_fast:
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
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

    Fail-Fast Behavior
    ------------------
    When fail_fast=True (default), any file read or URL fetch failure will raise
    a RuntimeError instead of silently skipping. This ensures users are immediately
    aware of configuration or network issues.

    Set fail_fast=False only when you want graceful degradation (e.g., optional docs).
    """

    def __init__(self, fail_fast: bool = True):
        """Initialize KnowledgeLoader.

        Parameters
        ----------
        fail_fast : bool
            If True (default), raise exceptions on file/URL errors.
            If False, log warnings and continue with partial results.
        """
        self._fail_fast = fail_fast
        self._failed_urls: List[str] = []  # Track failed URLs for fallback search
        logger.info("[KNOWLEDGE_LOADER] Initialized with fail_fast=%s", fail_fast)

    def get_failed_urls(self) -> List[str]:
        """Return the list of URLs that failed to download.

        Returns
        -------
        List[str]
            URLs that failed during load_from_urls or load_from_url_csv.
            Used for fallback search when is_search_after_fail is enabled.
        """
        return self._failed_urls.copy()

    def clear_failed_urls(self) -> None:
        """Clear the list of failed URLs."""
        self._failed_urls.clear()

    # ------------------------------------------------------------------
    # Source 1: local directory
    # ------------------------------------------------------------------

    def load_from_dir(
        self,
        folder: str,
        processed_dir: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """Load all PDF and .md files recursively from *folder*.

        Parameters
        ----------
        folder:
            Absolute or relative path to the directory.
        processed_dir:
            Directory to save/load processed MinerU output for PDF files.
            If provided, processed PDFs are cached here to avoid re-processing.

        Returns
        -------
        List[KnowledgeDocument]
            One Document per successfully parsed file.

        Raises
        ------
        RuntimeError
            If fail_fast=True and folder doesn't exist or any file fails to parse.
        """
        docs: List[KnowledgeDocument] = []
        logger.info("[KNOWLEDGE_LOADER] load_from_dir: scanning folder: %s", folder)

        if not os.path.isdir(folder):
            error_msg = f"load_from_dir: folder not found: {folder}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return docs

        file_count = 0
        for root, _dirs, files in os.walk(folder):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                lower = fname.lower()
                if lower.endswith(".pdf"):
                    # Check PDF page count for logging and timeout calculation
                    page_count = _check_pdf_page_count(fpath)
                    logger.info(
                        "[KNOWLEDGE_LOADER] load_from_dir: found PDF file: %s (%d pages)",
                        fpath,
                        page_count,
                    )
                    if page_count > 200:
                        logger.warning(
                            "[KNOWLEDGE_LOADER] Large PDF detected (%d pages), "
                            "will be split into chunks for processing: %s",
                            page_count,
                            fpath,
                        )
                    text = _parse_pdf(
                        fpath, fail_fast=self._fail_fast, processed_dir=processed_dir
                    )
                    file_count += 1
                elif lower.endswith(".md"):
                    logger.info(
                        "[KNOWLEDGE_LOADER] load_from_dir: found markdown file: %s",
                        fpath,
                    )
                    text = _parse_markdown(fpath, fail_fast=self._fail_fast)
                    file_count += 1
                else:
                    continue

                if text:
                    docs.append(
                        KnowledgeDocument(
                            text=text,
                            source=fpath,
                            source_type=KnowledgeSourceType.LOCAL_FILE,
                            title=fname,
                            metadata={"filename": fname, "full_path": fpath},
                        )
                    )
                    logger.info(
                        "[KNOWLEDGE_LOADER] load_from_dir: SUCCESS - file=%s, chars=%d",
                        fname,
                        len(text),
                    )
                elif self._fail_fast:
                    # If fail_fast and text is None, an exception should have been raised
                    # But handle case where it wasn't
                    error_msg = f"load_from_dir: failed to parse file: {fpath}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        logger.info(
            "[KNOWLEDGE_LOADER] load_from_dir: COMPLETE - %d file(s) scanned, %d document(s) loaded from %s",
            file_count,
            len(docs),
            folder,
        )
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
            One Document per successfully fetched URL.

        Raises
        ------
        RuntimeError
            If fail_fast=True and any URL fails to fetch.
        """
        docs: List[KnowledgeDocument] = []
        self._failed_urls.clear()  # Reset failed URLs tracking
        logger.info(
            "[KNOWLEDGE_LOADER] load_from_urls: starting fetch of %d URL(s)", len(urls)
        )

        for idx, url in enumerate(urls):
            url = url.strip()
            if not url:
                logger.warning(
                    "[KNOWLEDGE_LOADER] load_from_urls: skipping empty URL at index %d",
                    idx,
                )
                continue
            logger.info(
                "[KNOWLEDGE_LOADER] load_from_urls: fetching URL %d/%d: %s",
                idx + 1,
                len(urls),
                url,
            )
            text = _fetch_url_text(url, fail_fast=False)  # Don't raise, track failures
            if text:
                docs.append(
                    KnowledgeDocument(
                        text=text,
                        source=url,
                        source_type=KnowledgeSourceType.WEB_URL,
                        metadata={"url": url},
                    )
                )
                logger.info(
                    "[KNOWLEDGE_LOADER] load_from_urls: SUCCESS - url=%s, chars=%d",
                    url,
                    len(text),
                )
            else:
                # Track failed URL for potential fallback search
                self._failed_urls.append(url)
                logger.warning(
                    "[KNOWLEDGE_LOADER] load_from_urls: FAILED - url=%s (tracked for fallback)",
                    url,
                )
                if self._fail_fast:
                    error_msg = f"load_from_urls: failed to fetch URL: {url}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            time.sleep(0.3)  # polite crawl delay

        logger.info(
            "[KNOWLEDGE_LOADER] load_from_urls: COMPLETE - %d/%d URL(s) fetched successfully, %d failed",
            len(docs),
            len(urls),
            len(self._failed_urls),
        )
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

        Raises
        ------
        RuntimeError
            If fail_fast=True and CSV cannot be read or any file/URL fails.
        """
        logger.info("[KNOWLEDGE_LOADER] load_from_url_csv: reading CSV: %s", csv_path)
        web_urls: List[str] = []
        file_paths: List[tuple[str, str]] = []  # (path, title)

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    row_count += 1
                    source_type = (
                        (row.get("source_type") or row.get("source") or "web")
                        .lower()
                        .strip()
                    )
                    url = row.get("url") or row.get("URL") or ""
                    url = url.strip()
                    title = row.get("book_title") or row.get("title") or ""
                    if not url:
                        logger.warning(
                            "[KNOWLEDGE_LOADER] load_from_url_csv: row %d has empty URL, skipping",
                            row_count,
                        )
                        continue
                    if source_type == "file":
                        file_paths.append((url, title))
                        logger.info(
                            "[KNOWLEDGE_LOADER] load_from_url_csv: row %d - LOCAL FILE: %s (title: %s)",
                            row_count,
                            url,
                            title or "(none)",
                        )
                    else:
                        web_urls.append(url)
                        logger.info(
                            "[KNOWLEDGE_LOADER] load_from_url_csv: row %d - WEB URL: %s (title: %s)",
                            row_count,
                            url,
                            title or "(none)",
                        )
            logger.info(
                "[KNOWLEDGE_LOADER] load_from_url_csv: parsed %d rows: %d local file(s), %d web URL(s)",
                row_count,
                len(file_paths),
                len(web_urls),
            )
        except FileNotFoundError:
            error_msg = f"load_from_url_csv: CSV file not found: {csv_path}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return []
        except Exception as exc:
            error_msg = f"load_from_url_csv: failed to read CSV {csv_path}: {type(exc).__name__}: {exc}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return []

        docs: List[KnowledgeDocument] = []

        # Load local files
        for path, title in file_paths:
            logger.info(
                "[KNOWLEDGE_LOADER] load_from_url_csv: loading local file: %s", path
            )

            # Check if file exists first
            if not os.path.exists(path):
                error_msg = f"load_from_url_csv: file not found: {path}"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                if self._fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                continue

            text = None
            if path.lower().endswith(".pdf"):
                text = _parse_pdf(path, fail_fast=self._fail_fast)
            elif path.lower().endswith(".md"):
                text = _parse_markdown(path, fail_fast=self._fail_fast)
            else:
                # Try to read as text file
                try:
                    with open(path, encoding="utf-8", errors="replace") as f:
                        text = f.read()
                    logger.info(
                        "[KNOWLEDGE_LOADER] load_from_url_csv: read text file: %s (%d chars)",
                        path,
                        len(text),
                    )
                except Exception as exc:
                    error_msg = f"load_from_url_csv: failed to read file {path}: {type(exc).__name__}: {exc}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    if self._fail_fast:
                        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

            if text:
                docs.append(
                    KnowledgeDocument(
                        text=text,
                        source=path,
                        source_type=KnowledgeSourceType.LOCAL_FILE,
                        title=title or os.path.basename(path),
                        metadata={
                            "filename": os.path.basename(path),
                            "full_path": path,
                        },
                    )
                )
                logger.info(
                    "[KNOWLEDGE_LOADER] load_from_url_csv: SUCCESS - file=%s, chars=%d",
                    path,
                    len(text),
                )
            elif self._fail_fast:
                error_msg = f"load_from_url_csv: failed to load file: {path}"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        # Fetch web URLs
        if web_urls:
            docs.extend(self.load_from_urls(web_urls))

        logger.info(
            "[KNOWLEDGE_LOADER] load_from_url_csv: COMPLETE - %d document(s) loaded from %s",
            len(docs),
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

        Raises
        ------
        RuntimeError
            If fail_fast=True and no documents can be obtained.
        """
        logger.info(
            "[KNOWLEDGE_LOADER] suggest_and_download: START - persona='%s...', n_urls=%d, save_dir=%s",
            persona_desc[:60],
            n_urls,
            save_dir or "(none)",
        )

        # --- Check cache first (resume support) ---------------------------------
        if save_dir and os.path.isdir(save_dir):
            cached = [f for f in os.listdir(save_dir) if f.endswith(".txt")]
            if cached:
                logger.info(
                    "[KNOWLEDGE_LOADER] suggest_and_download: found %d cached file(s) in %s",
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
                                    title=fname,
                                    metadata={"cached": True, "cache_file": fpath},
                                )
                            )
                            logger.info(
                                "[KNOWLEDGE_LOADER] suggest_and_download: loaded cache file: %s (%d chars)",
                                fname,
                                len(text),
                            )
                    except Exception as exc:
                        error_msg = f"Failed to read cache file {fpath}: {type(exc).__name__}: {exc}"
                        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                        if self._fail_fast:
                            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                if docs:
                    logger.info(
                        "[KNOWLEDGE_LOADER] suggest_and_download: COMPLETE (from cache) - %d document(s) from %s",
                        len(docs),
                        save_dir,
                    )
                    return docs

        # --- Step 1: LLM generates search queries (NOT URLs) --------------------
        logger.info(
            "[KNOWLEDGE_LOADER] suggest_and_download: asking LLM for search queries...",
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
            logger.info(
                "[KNOWLEDGE_LOADER] suggest_and_download: LLM generated %d search queries: %s",
                len(search_queries),
                search_queries,
            )
        except Exception as exc:
            error_msg = (
                f"LLM search-query generation failed: {type(exc).__name__}: {exc}"
            )
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        if not search_queries:
            # Fallback: generate generic queries directly from persona_desc
            logger.warning(
                "[KNOWLEDGE_LOADER] suggest_and_download: falling back to persona-derived queries"
            )
            search_queries = [
                f"{persona_desc[:120]} investment strategy financial theory",
                f"{persona_desc[:80]} market behavior academic paper",
            ]

        # --- Step 2: Execute web search to get real URLs ------------------------
        try:
            from duckduckgo_search import DDGS

            logger.info(
                "[KNOWLEDGE_LOADER] suggest_and_download: DuckDuckGo search available"
            )
        except ImportError:
            error_msg = (
                "duckduckgo_search not installed. Run: pip install duckduckgo-search"
            )
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return []

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            logger.info(
                "[KNOWLEDGE_LOADER] suggest_and_download: created cache directory: %s",
                save_dir,
            )

        docs = []
        seen_urls: set = set()

        for query_idx, query in enumerate(search_queries[:n_urls]):
            logger.info(
                "[KNOWLEDGE_LOADER] suggest_and_download: executing search query %d/%d: '%s'",
                query_idx + 1,
                min(len(search_queries), n_urls),
                query,
            )
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=3))
                logger.info(
                    "[KNOWLEDGE_LOADER] suggest_and_download: DuckDuckGo returned %d result(s) for query: '%s'",
                    len(results),
                    query,
                )
            except Exception as exc:
                error_msg = f"DuckDuckGo search failed for query '{query}': {type(exc).__name__}: {exc}"
                logger.warning("[KNOWLEDGE_LOADER] %s", error_msg)
                if self._fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                time.sleep(1.0)
                continue

            # --- Step 3: Fetch content from each search result ------------------
            for hit_idx, hit in enumerate(results):
                url = hit.get("href", "").strip()
                title = hit.get("title", "").strip()
                snippet = hit.get("body", "").strip()

                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                logger.info(
                    "[KNOWLEDGE_LOADER] suggest_and_download: hit %d - fetching URL: %s (title: %s)",
                    hit_idx + 1,
                    url,
                    title[:50] + "..." if len(title) > 50 else title,
                )

                text = _fetch_url_text(url, fail_fast=self._fail_fast)
                if not text:
                    # Fall back to snippet if full page fetch fails
                    if snippet and len(snippet) > 80:
                        text = f"# {title}\n\nSource: {url}\n\n{snippet}"
                        logger.info(
                            "[KNOWLEDGE_LOADER] suggest_and_download: using snippet for %s (%d chars)",
                            url,
                            len(text),
                        )
                    else:
                        error_msg = f"Failed to fetch content from URL: {url}"
                        logger.warning("[KNOWLEDGE_LOADER] %s", error_msg)
                        if self._fail_fast:
                            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
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
                            "[KNOWLEDGE_LOADER] suggest_and_download: cached %d chars → %s",
                            len(full_text),
                            cache_path,
                        )
                    except Exception as exc:
                        error_msg = f"Failed to write cache file {cache_path}: {type(exc).__name__}: {exc}"
                        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                        if self._fail_fast:
                            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

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
                logger.info(
                    "[KNOWLEDGE_LOADER] suggest_and_download: SUCCESS - added document from %s (%d chars)",
                    url,
                    len(full_text),
                )

                if len(docs) >= n_urls:
                    break

            time.sleep(0.5)  # polite crawl delay between queries
            if len(docs) >= n_urls:
                break

        if not docs and self._fail_fast:
            error_msg = f"suggest_and_download: failed to collect any documents for persona: {persona_desc[:60]}..."
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        logger.info(
            "[KNOWLEDGE_LOADER] suggest_and_download: COMPLETE - collected %d document(s) for persona: %s...",
            len(docs),
            persona_desc[:40],
        )
        return docs

    # ------------------------------------------------------------------
    # Source 5: Fallback search for failed downloads
    # ------------------------------------------------------------------

    _FALLBACK_SEARCH_SYSTEM = (
        "You are a research assistant helping find alternative sources for failed downloads. "
        "When given a list of failed URLs and a persona description, you generate targeted "
        "web search queries to find replacement documents covering the same topics. "
        "Focus on finding freely accessible sources: Wikipedia, Investopedia, academic "
        "papers, or educational resources. Output ONLY valid JSON — no prose, no markdown fences."
    )

    _FALLBACK_SEARCH_USER = (
        "Failed URLs that could not be downloaded:\n{failed_urls}\n\n"
        "Agent persona: {persona_desc}\n\n"
        "Generate exactly {n} concise web search queries to find alternative sources "
        "covering the same financial theories and concepts as the failed URLs. "
        "Focus on accessible sources like Wikipedia, Investopedia, or educational sites.\n\n"
        'Output ONLY a JSON array of query strings: ["query 1", "query 2", ...]'
    )

    def search_for_fallback(
        self,
        failed_urls: List[str],
        persona_desc: str,
        llm_client: Any,
        n_urls: int = 5,
        save_dir: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """Search for alternative documents when primary sources fail to download.

        This method is called when is_search_after_fail is enabled and URLs/PDFs
        fail to download. It uses the LLM to generate search queries based on
        the failed URLs and persona description, then searches for alternatives.

        Flow:
            1. LLM generates search queries based on failed URLs + persona
            2. DuckDuckGo search executes each query and returns real URLs
            3. Top results are fetched and their content extracted
            4. Documents are cached to *save_dir* for resume support

        Parameters
        ----------
        failed_urls:
            List of URLs that failed to download (from get_failed_urls()).
        persona_desc:
            Short description of the agent's persona / investment style.
        llm_client:
            A ``LangChainAPIInference`` instance (or any object with a
            ``run([InferInput]) -> InferBatchOutput`` method).
        n_urls:
            Target number of documents to collect.
        save_dir:
            Directory to cache downloaded documents as ``.txt`` files.

        Returns
        -------
        List[KnowledgeDocument]
            Documents found as alternatives to the failed downloads.
        """
        if not failed_urls:
            logger.info(
                "[KNOWLEDGE_LOADER] search_for_fallback: no failed URLs to replace"
            )
            return []

        logger.info(
            "[KNOWLEDGE_LOADER] search_for_fallback: START - %d failed URLs, persona='%s...', n_urls=%d",
            len(failed_urls),
            persona_desc[:60],
            n_urls,
        )

        # --- Step 1: LLM generates search queries based on failed URLs --------
        logger.info(
            "[KNOWLEDGE_LOADER] search_for_fallback: asking LLM for fallback search queries...",
        )
        search_queries: List[str] = []
        try:
            from lmbase.inference.base import InferInput

            failed_urls_str = "\n".join(f"- {url}" for url in failed_urls[:10])
            user_msg = self._FALLBACK_SEARCH_USER.format(
                failed_urls=failed_urls_str,
                persona_desc=persona_desc,
                n=n_urls,
            )
            infer_input = InferInput(
                system_msg=self._FALLBACK_SEARCH_SYSTEM, user_msg=user_msg
            )
            batch_output = llm_client.run([infer_input])
            raw = batch_output.outputs[0].response.strip()

            # Parse JSON array of query strings
            clean = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
            clean = re.sub(r"```", "", clean).strip()
            parsed = json.loads(clean)
            if isinstance(parsed, list):
                search_queries = [str(q).strip() for q in parsed if str(q).strip()]
            logger.info(
                "[KNOWLEDGE_LOADER] search_for_fallback: LLM generated %d search queries: %s",
                len(search_queries),
                search_queries,
            )
        except Exception as exc:
            error_msg = f"LLM fallback search-query generation failed: {type(exc).__name__}: {exc}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        if not search_queries:
            # Fallback: generate queries from failed URL domains/topics
            logger.warning(
                "[KNOWLEDGE_LOADER] search_for_fallback: falling back to URL-derived queries"
            )
            # Extract topics from failed URLs
            topics = []
            for url in failed_urls[:3]:
                # Extract last path component as topic
                parts = url.rstrip("/").split("/")
                if parts:
                    topic = parts[-1].replace("_", " ").replace("-", " ")
                    if topic:
                        topics.append(topic)
            if topics:
                search_queries = [
                    f"{topic} wikipedia investopedia financial theory"
                    for topic in topics[:n_urls]
                ]
            else:
                search_queries = [f"{persona_desc[:100]} financial theory wikipedia"]

        # --- Step 2: Execute web search to get real URLs ------------------------
        try:
            from duckduckgo_search import DDGS

            logger.info(
                "[KNOWLEDGE_LOADER] search_for_fallback: DuckDuckGo search available"
            )
        except ImportError:
            error_msg = (
                "duckduckgo_search not installed. Run: pip install duckduckgo-search"
            )
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            if self._fail_fast:
                raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
            return []

        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            # Create a subdirectory for fallback documents
            fallback_dir = os.path.join(save_dir, "fallback")
            os.makedirs(fallback_dir, exist_ok=True)
            logger.info(
                "[KNOWLEDGE_LOADER] search_for_fallback: created fallback cache directory: %s",
                fallback_dir,
            )
        else:
            fallback_dir = None

        docs = []
        seen_urls: set = set()

        for query_idx, query in enumerate(search_queries[:n_urls]):
            logger.info(
                "[KNOWLEDGE_LOADER] search_for_fallback: executing search query %d/%d: '%s'",
                query_idx + 1,
                min(len(search_queries), n_urls),
                query,
            )
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=3))
                logger.info(
                    "[KNOWLEDGE_LOADER] search_for_fallback: DuckDuckGo returned %d result(s)",
                    len(results),
                )
            except Exception as exc:
                error_msg = f"DuckDuckGo search failed for query '{query}': {type(exc).__name__}: {exc}"
                logger.warning("[KNOWLEDGE_LOADER] %s", error_msg)
                if self._fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
                time.sleep(1.0)
                continue

            # --- Step 3: Fetch content from each search result ------------------
            for hit_idx, hit in enumerate(results):
                url = hit.get("href", "").strip()
                title = hit.get("title", "").strip()
                snippet = hit.get("body", "").strip()

                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                logger.info(
                    "[KNOWLEDGE_LOADER] search_for_fallback: hit %d - fetching URL: %s",
                    hit_idx + 1,
                    url,
                )

                text = _fetch_url_text(
                    url, fail_fast=False
                )  # Don't fail on individual URLs
                if not text:
                    # Fall back to snippet if full page fetch fails
                    if snippet and len(snippet) > 80:
                        text = f"# {title}\n\nSource: {url}\n\n{snippet}"
                        logger.info(
                            "[KNOWLEDGE_LOADER] search_for_fallback: using snippet for %s (%d chars)",
                            url,
                            len(text),
                        )
                    else:
                        logger.warning(
                            "[KNOWLEDGE_LOADER] search_for_fallback: failed to fetch %s, skipping",
                            url,
                        )
                        time.sleep(0.3)
                        continue

                # Prepend title and source as context
                full_text = (
                    f"# {title}\n\nSource: {url}\n\n"
                    f"Search query: {query}\n"
                    f"Fallback for failed URLs: {', '.join(failed_urls[:3])}\n\n{text}"
                )

                # Cache to disk
                if fallback_dir:
                    slug = _slug(title or url)
                    cache_path = os.path.join(fallback_dir, f"{slug}.txt")
                    try:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            f.write(full_text)
                        logger.info(
                            "[KNOWLEDGE_LOADER] search_for_fallback: cached %d chars → %s",
                            len(full_text),
                            cache_path,
                        )
                    except Exception as exc:
                        error_msg = f"Failed to write cache file {cache_path}: {type(exc).__name__}: {exc}"
                        logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                        if self._fail_fast:
                            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

                docs.append(
                    KnowledgeDocument(
                        text=full_text,
                        source=url,
                        source_type=KnowledgeSourceType.LLM_SUGGESTED,
                        title=f"[Fallback] {title}",
                        metadata={
                            "url": url,
                            "search_query": query,
                            "snippet": snippet,
                            "fallback_for": failed_urls[
                                :5
                            ],  # Track which URLs this replaces
                            "is_fallback": True,
                        },
                    )
                )
                logger.info(
                    "[KNOWLEDGE_LOADER] search_for_fallback: SUCCESS - added fallback document from %s (%d chars)",
                    url,
                    len(full_text),
                )

                if len(docs) >= n_urls:
                    break

            time.sleep(0.5)  # polite crawl delay between queries
            if len(docs) >= n_urls:
                break

        if not docs and self._fail_fast:
            error_msg = f"search_for_fallback: failed to find any alternative documents for failed URLs"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        logger.info(
            "[KNOWLEDGE_LOADER] search_for_fallback: COMPLETE - found %d alternative document(s) for %d failed URLs",
            len(docs),
            len(failed_urls),
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
        RuntimeError
            If fail_fast=True and any URL fails to fetch.

        Example
        -------
        >>> loader = KnowledgeLoader()
        >>> docs = loader.load_for_agent("ragllm_momentum_1")
        >>> print(f"Loaded {len(docs)} documents for momentum speculator")
        """
        logger.info(
            "[KNOWLEDGE_LOADER] load_for_agent: START - identity='%s', catalog='%s'",
            identity,
            catalog_path or DEFAULT_CATALOG_PATH,
        )

        agent_type = resolve_agent_type(identity)
        catalog = catalog_path or DEFAULT_CATALOG_PATH

        if not os.path.isfile(catalog):
            error_msg = f"Document catalog not found: {catalog}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            raise FileNotFoundError(
                f"[KNOWLEDGE_LOADER] {error_msg}. "
                f"Ensure the file exists or provide a valid catalog_path."
            )

        logger.info(
            "[KNOWLEDGE_LOADER] load_for_agent: identity='%s' → agent_type='%s'",
            identity,
            agent_type,
        )

        # Read URLs for this agent_type from the catalog
        urls: List[str] = []
        titles: List[str] = []
        with open(catalog, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                row_type = row.get("agent_type", "").strip().lower()
                if row_type == agent_type:
                    url = (row.get("url") or row.get("URL") or "").strip()
                    if url:
                        urls.append(url)
                        title = row.get("book_title", url)
                        titles.append(title)
                        logger.info(
                            "[KNOWLEDGE_LOADER] load_for_agent: catalog row %d - URL: %s (title: %s)",
                            row_num,
                            url,
                            title,
                        )

        if not urls:
            error_msg = f"No documents found for agent_type '{agent_type}' in {catalog}"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            raise ValueError(
                f"[KNOWLEDGE_LOADER] {error_msg}. "
                f"Ensure the catalog has an 'agent_type' column with value '{agent_type}'."
            )

        logger.info(
            "[KNOWLEDGE_LOADER] load_for_agent: found %d URL(s) for agent_type='%s'",
            len(urls),
            agent_type,
        )

        # Fetch and parse documents
        docs: List[KnowledgeDocument] = []
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            logger.info(
                "[KNOWLEDGE_LOADER] load_for_agent: cache directory: %s", save_dir
            )

        for idx, (url, title) in enumerate(zip(urls, titles)):
            logger.info(
                "[KNOWLEDGE_LOADER] load_for_agent: fetching URL %d/%d: %s",
                idx + 1,
                len(urls),
                url,
            )
            text = _fetch_url_text(url, fail_fast=self._fail_fast)
            if not text:
                error_msg = f"Failed to fetch URL for agent '{identity}': {url}"
                logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                if self._fail_fast:
                    raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")
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
                    logger.info(
                        "[KNOWLEDGE_LOADER] load_for_agent: cached document → %s (%d chars)",
                        cache_path,
                        len(full_text),
                    )
                except Exception as exc:
                    error_msg = f"Failed to write cache file {cache_path}: {type(exc).__name__}: {exc}"
                    logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
                    if self._fail_fast:
                        raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

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
                "[KNOWLEDGE_LOADER] load_for_agent: SUCCESS - fetched document from %s (%d chars)",
                url,
                len(full_text),
            )

        if not docs and self._fail_fast:
            error_msg = f"load_for_agent: failed to load any documents for identity='{identity}'"
            logger.error("[KNOWLEDGE_LOADER] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_LOADER] {error_msg}")

        logger.info(
            "[KNOWLEDGE_LOADER] load_for_agent: COMPLETE - %d document(s) loaded for identity='%s' (agent_type=%s)",
            len(docs),
            identity,
            agent_type,
        )
        return docs
