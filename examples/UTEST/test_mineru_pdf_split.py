"""Unit Test: Verify MinerU PDF Parsing with Automatic Splitting

Tests whether masim's MinerU integration can parse PDF files from
examples/document-sources directory, including large PDFs that need
automatic splitting.

Usage:
    cd /Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation
    PYTHONPATH=/Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation python examples/UTEST/test_mineru_pdf_split.py
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


def test_environment():
    """Test if required API keys are configured."""
    print("=" * 70)
    print("TEST 1: Environment Configuration")
    print("=" * 70)

    mineru_key = os.getenv("MINERU_API_KEY", "")
    ark_key = os.getenv("ARK_API_KEY", "")

    results = {}

    if not mineru_key:
        print("❌ MINERU_API_KEY not set")
        results["mineru"] = False
    else:
        print(f"✓ MINERU_API_KEY is set (length: {len(mineru_key)})")
        results["mineru"] = True

    if not ark_key:
        print("❌ ARK_API_KEY not set")
        results["ark"] = False
    else:
        print(f"✓ ARK_API_KEY is set: {ark_key[:20]}...")
        results["ark"] = True

    return results


def get_pdf_info(pdf_path: Path) -> dict:
    """Get PDF file information including page count."""
    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        info = {
            "pages": len(doc),
            "size": pdf_path.stat().st_size,
            "size_mb": pdf_path.stat().st_size / (1024 * 1024),
        }
        doc.close()
        return info
    except Exception as e:
        return {"error": str(e)}


def test_pymupdf_parse(pdf_path: Path) -> tuple[bool, str, int]:
    """Test PyMuPDF parsing on a PDF file.

    Returns:
        (success, extracted_text or error_message, char_count)
    """
    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        pages = []
        for page in doc:
            text = page.get_text()
            pages.append(text)
        doc.close()

        full_text = "\f".join(pages)

        if full_text.strip():
            return True, full_text, len(full_text)
        else:
            return False, "No text extracted (possibly scanned/image PDF)", 0

    except Exception as e:
        return False, f"PyMuPDF error: {type(e).__name__}: {e}", 0


def test_mineru_with_splitting(
    pdf_path: Path, timeout: int = 300
) -> tuple[bool, str, int, dict]:
    """Test MinerU parsing with automatic PDF splitting for large files.

    Args:
        pdf_path: Path to PDF file
        timeout: Maximum time to wait for parsing (seconds)

    Returns:
        (success, extracted_text or error_message, char_count, metadata)
    """
    metadata = {
        "split_used": False,
        "chunks": 0,
        "timeouts": 0,
        "errors": [],
    }

    try:
        from masim.knowledge.loader import _parse_pdf_with_mineru

        print(f"  Starting MinerU parsing (timeout: {timeout}s)...")
        start_time = time.time()

        # Get PDF info to determine if splitting is needed
        pdf_info = get_pdf_info(pdf_path)
        if "pages" in pdf_info:
            print(
                f"  PDF info: {pdf_info['pages']} pages, {pdf_info.get('size_mb', 0):.1f} MB"
            )
            if pdf_info["pages"] > 200:
                print(
                    f"  Large PDF detected (>200 pages), automatic splitting will be used"
                )
                metadata["split_used"] = True

        result = _parse_pdf_with_mineru(
            str(pdf_path), fail_fast=False, max_wait_time=timeout
        )

        elapsed = time.time() - start_time
        metadata["elapsed_time"] = elapsed

        if result and result.strip():
            return True, result, len(result), metadata
        else:
            return (
                False,
                f"MinerU returned empty result after {elapsed:.1f}s",
                0,
                metadata,
            )

    except Exception as e:
        metadata["errors"].append(str(e))
        return False, f"MinerU error: {type(e).__name__}: {e}", 0, metadata


def test_pdf_file(pdf_path: Path) -> dict:
    """Test both PyMuPDF and MinerU on a single PDF file."""
    print(f"\n{'=' * 70}")
    print(f"Testing: {pdf_path.name}")
    print(f"{'=' * 70}")

    results = {
        "file": pdf_path.name,
        "exists": pdf_path.exists(),
        "info": {},
        "pymupdf": {"success": False, "text": "", "chars": 0, "error": ""},
        "mineru": {
            "success": False,
            "text": "",
            "chars": 0,
            "error": "",
            "metadata": {},
        },
    }

    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return results

    # Get PDF info
    results["info"] = get_pdf_info(pdf_path)
    if "pages" in results["info"]:
        print(
            f"  PDF: {results['info']['pages']} pages, {results['info'].get('size_mb', 0):.1f} MB"
        )

    # Test PyMuPDF first
    print("\n  Testing PyMuPDF...")
    pymupdf_success, pymupdf_result, pymupdf_chars = test_pymupdf_parse(pdf_path)
    results["pymupdf"]["success"] = pymupdf_success
    results["pymupdf"]["chars"] = pymupdf_chars

    if pymupdf_success:
        results["pymupdf"]["text"] = pymupdf_result[:500]
        print(f"  ✓ PyMuPDF: SUCCESS ({pymupdf_chars:,} characters)")
        print(f"    Preview: {pymupdf_result[:150]}...")
    else:
        results["pymupdf"]["error"] = pymupdf_result
        print(f"  ✗ PyMuPDF: FAILED - {pymupdf_result}")

    # Test MinerU with splitting support
    print("\n  Testing MinerU (with auto-splitting for large PDFs)...")
    mineru_success, mineru_result, mineru_chars, mineru_metadata = (
        test_mineru_with_splitting(pdf_path)
    )
    results["mineru"]["success"] = mineru_success
    results["mineru"]["chars"] = mineru_chars
    results["mineru"]["metadata"] = mineru_metadata

    if mineru_success:
        results["mineru"]["text"] = mineru_result[:500]
        print(f"  ✓ MinerU: SUCCESS ({mineru_chars:,} characters)")
        if mineru_metadata.get("split_used"):
            print(f"    Note: PDF was automatically split for processing")
        print(f"    Preview: {mineru_result[:150]}...")
    else:
        results["mineru"]["error"] = mineru_result
        print(f"  ✗ MinerU: FAILED - {mineru_result}")

    return results


def main():
    """Run all PDF parsing tests."""
    print("\n" + "=" * 70)
    print("MinerU PDF Parsing Unit Test (with Auto-Splitting)")
    print("=" * 70)

    # Test environment
    env_results = test_environment()
    if not env_results.get("mineru", False):
        print("\n❌ MINERU_API_KEY not configured. Exiting.")
        return 1

    # Find PDF files to test
    docs_dir = PROJECT_ROOT / "examples" / "document-sources" / "files"

    if not docs_dir.exists():
        print(f"\n❌ Directory not found: {docs_dir}")
        return 1

    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"\n❌ No PDF files found in: {docs_dir}")
        return 1

    print(f"\nFound {len(pdf_files)} PDF file(s) to test:")
    for pdf in sorted(pdf_files):
        pdf_info = get_pdf_info(pdf)
        pages = pdf_info.get("pages", "?")
        size_mb = pdf_info.get("size_mb", 0)
        print(f"  - {pdf.name} ({pages} pages, {size_mb:.1f} MB)")

    # Test each PDF
    all_results = []
    for pdf_path in sorted(pdf_files):
        result = test_pdf_file(pdf_path)
        all_results.append(result)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for result in all_results:
        print(f"\n{result['file']}:")

        if not result["exists"]:
            print("  ❌ File not found")
            continue

        if "pages" in result["info"]:
            print(
                f"  Pages: {result['info']['pages']}, Size: {result['info'].get('size_mb', 0):.1f} MB"
            )

        # PyMuPDF status
        if result["pymupdf"]["success"]:
            print(f"  ✓ PyMuPDF: {result['pymupdf']['chars']:,} chars")
        else:
            print(f"  ✗ PyMuPDF: {result['pymupdf']['error'][:50]}...")

        # MinerU status
        if result["mineru"]["success"]:
            split_info = (
                " (split)" if result["mineru"]["metadata"].get("split_used") else ""
            )
            print(f"  ✓ MinerU: {result['mineru']['chars']:,} chars{split_info}")
        else:
            print(f"  ✗ MinerU: {result['mineru']['error'][:50]}...")

    # Overall assessment
    print("\n" + "=" * 70)
    total_files = len(all_results)
    pymupdf_working = sum(1 for r in all_results if r["pymupdf"]["success"])
    mineru_working = sum(1 for r in all_results if r["mineru"]["success"])
    split_used_count = sum(
        1 for r in all_results if r["mineru"]["metadata"].get("split_used")
    )

    print(f"Results: {pymupdf_working}/{total_files} files work with PyMuPDF")
    print(f"         {mineru_working}/{total_files} files work with MinerU")
    if split_used_count > 0:
        print(f"         {split_used_count} large PDF(s) used automatic splitting")

    if mineru_working > 0:
        print("\n✓ MinerU can successfully parse PDF files!")
        if mineru_working < total_files:
            print(
                f"  Note: {total_files - mineru_working} file(s) failed - may need longer timeout"
            )
        return 0
    else:
        print("\n⚠ MinerU failed to parse any PDF files.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
