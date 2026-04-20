"""Unit Test: Verify MinerU PDF Parsing Capability

Tests whether masim's MinerU integration can parse PDF files
from examples/document-sources directory.

Usage:
    cd /Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation
    PYTHONPATH=/Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation python examples/UTEST/test_mineru_pdf.py
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
    """Test if MINERU_API_KEY is configured."""
    print("=" * 70)
    print("TEST 1: Environment Configuration")
    print("=" * 70)

    mineru_key = os.getenv("MINERU_API_KEY", "")

    if not mineru_key:
        print("❌ FAILED: MINERU_API_KEY not set in environment")
        print("   Please set MINERU_API_KEY in .env file")
        return False

    print(f"✓ MINERU_API_KEY is set (length: {len(mineru_key)})")
    print(f"  Key prefix: {mineru_key[:30]}...")
    return True


def test_pymupdf_parse(pdf_path: Path) -> tuple[bool, str]:
    """Test PyMuPDF parsing on a PDF file.

    Returns:
        (success, extracted_text or error_message)
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        pages = []
        for page in doc:
            text = page.get_text()
            pages.append(text)
        doc.close()

        full_text = "\f".join(pages)

        if full_text.strip():
            return True, full_text
        else:
            return False, "No text extracted (possibly scanned/image PDF)"

    except Exception as e:
        return False, f"PyMuPDF error: {type(e).__name__}: {e}"


def test_mineru_parse(pdf_path: Path, timeout: int = 180) -> tuple[bool, str]:
    """Test MinerU parsing on a PDF file.

    Args:
        pdf_path: Path to PDF file
        timeout: Maximum time to wait for parsing (seconds)

    Returns:
        (success, extracted_text or error_message)
    """
    try:
        from masim.knowledge.loader import _parse_pdf_with_mineru

        print(f"  Starting MinerU parsing (timeout: {timeout}s)...")
        start_time = time.time()

        result = _parse_pdf_with_mineru(
            str(pdf_path), fail_fast=False, max_wait_time=timeout
        )

        elapsed = time.time() - start_time

        if result and result.strip():
            return True, result
        else:
            return False, f"MinerU returned empty result after {elapsed:.1f}s"

    except Exception as e:
        return False, f"MinerU error: {type(e).__name__}: {e}"


def test_pdf_file(pdf_path: Path) -> dict:
    """Test both PyMuPDF and MinerU on a single PDF file."""
    print(f"\n{'=' * 70}")
    print(f"Testing: {pdf_path.name}")
    print(f"{'=' * 70}")

    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return {
            "file": pdf_path.name,
            "exists": False,
            "pymupdf": {"success": False, "error": "File not found"},
            "mineru": {"success": False, "error": "File not found"},
        }

    results = {
        "file": pdf_path.name,
        "exists": True,
        "pymupdf": {"success": False, "text": "", "error": ""},
        "mineru": {"success": False, "text": "", "error": ""},
    }

    # Test PyMuPDF first
    print("\n  Testing PyMuPDF...")
    pymupdf_success, pymupdf_result = test_pymupdf_parse(pdf_path)
    results["pymupdf"]["success"] = pymupdf_success

    if pymupdf_success:
        results["pymupdf"]["text"] = pymupdf_result[:500]  # Store preview
        print(f"  ✓ PyMuPDF: SUCCESS ({len(pymupdf_result)} characters)")
        print(f"    Preview: {pymupdf_result[:200]}...")
    else:
        results["pymupdf"]["error"] = pymupdf_result
        print(f"  ✗ PyMuPDF: FAILED - {pymupdf_result}")

    # Test MinerU if PyMuPDF failed or if forced
    print("\n  Testing MinerU...")
    mineru_success, mineru_result = test_mineru_parse(pdf_path)
    results["mineru"]["success"] = mineru_success

    if mineru_success:
        results["mineru"]["text"] = mineru_result[:500]  # Store preview
        print(f"  ✓ MinerU: SUCCESS ({len(mineru_result)} characters)")
        print(f"    Preview: {mineru_result[:200]}...")
    else:
        results["mineru"]["error"] = mineru_result
        print(f"  ✗ MinerU: FAILED - {mineru_result}")

    return results


def main():
    """Run all PDF parsing tests."""
    print("\n" + "=" * 70)
    print("MinerU PDF Parsing Unit Test")
    print("=" * 70)

    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed. Exiting.")
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
    for pdf in pdf_files:
        print(f"  - {pdf.name}")

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

        # PyMuPDF status
        if result["pymupdf"]["success"]:
            print("  ✓ PyMuPDF: Working")
        else:
            print(f"  ✗ PyMuPDF: {result['pymupdf']['error'][:50]}...")

        # MinerU status
        if result["mineru"]["success"]:
            print("  ✓ MinerU: Working")
        else:
            print(f"  ✗ MinerU: {result['mineru']['error'][:50]}...")

    # Overall assessment
    print("\n" + "=" * 70)
    total_files = len(all_results)
    pymupdf_working = sum(1 for r in all_results if r["pymupdf"]["success"])
    mineru_working = sum(1 for r in all_results if r["mineru"]["success"])

    print(f"Results: {pymupdf_working}/{total_files} files work with PyMuPDF")
    print(f"         {mineru_working}/{total_files} files work with MinerU")

    if mineru_working > 0:
        print("\n✓ MinerU can successfully parse PDF files!")
        return 0
    else:
        print("\n⚠ MinerU failed to parse any PDF files.")
        print("  This may indicate:")
        print("  - MINERU_API_KEY is invalid or expired")
        print("  - MinerU service is unavailable")
        print("  - PDF files are corrupted or unsupported format")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
