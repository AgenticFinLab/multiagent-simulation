"""Batch injector — Polish Hook 9 universal-baseline invocation.

Idempotently patches every ``examples/*/{Rule,LLM,RuleLLM,Rag}/analysis.py``
so that it calls ``masim.evaluation.write_universal_summary(...)`` at the
end of its ``main()`` (or before the final scenario-specific summary return).

Only files that (a) exist, (b) contain a ``def main(`` block, (c) contain a
``_load_data(`` call inside ``main``, and (d) do NOT already import
``write_universal_summary`` are patched. Files that already carry the
import are left untouched (idempotency).

Usage:
    python3 scripts/inject_universal_summary.py [--dry-run] [--scenario ScenarioName]

This script is safe to re-run — it never patches a file twice.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "examples"
VARIANTS = ("Rule", "LLM", "RuleLLM", "Rag")
SKIP_DIRS = {"AGENT_POOL", "CUSTOMIZED_SIMULATION", "document-sources",
             "MYTest", "__pycache__"}

# Marker so we can detect an already-patched file without depending on the
# import line alone.
INJECT_MARKER = "# [polish-hook-9] universal baseline invocation"


def scenarios() -> List[Tuple[str, Path]]:
    """Yield (scenario_name, scenario_dir) pairs for buildable scenarios."""
    out = []
    for child in sorted(EXAMPLES.iterdir()):
        if not child.is_dir():
            continue
        if child.name in SKIP_DIRS:
            continue
        out.append((child.name, child))
    return out


def variant_analysis_files(scenario_dir: Path) -> List[Path]:
    """Return existing analysis.py files across the four canonical variants."""
    files: List[Path] = []
    for v in VARIANTS:
        f = scenario_dir / v / "analysis.py"
        if f.exists():
            files.append(f)
    return files


def already_patched(text: str) -> bool:
    """Idempotency check — a file is 'patched' if it either

    (a) has been directly injected (marker or import present),
    (b) delegates to the shared ``run_standard_analysis`` driver which itself
        invokes ``write_universal_summary``,
    (c) delegates to a scenario-family aggregator that internally invokes
        ``write_universal_summary`` (e.g. ``analyze_standard_scenario``,
        ``analyze_europeandebtcrisis``, ``analyze_flash_crash``), or
    (d) re-exports ``main`` from a sibling variant module which itself has
        been patched (thin variant wrapper pattern).
    """
    if INJECT_MARKER in text or "write_universal_summary" in text:
        return True
    if "run_standard_analysis(" in text or "_run_standard_analysis(" in text:
        return True
    delegator_callers = (
        "analyze_standard_scenario(",
        "analyze_europeandebtcrisis(",
        "analyze_flash_crash(",
        "analyze_gfc2008(",
        "analyze_ltcm_collapse(",
        "analyze_svbbankrun(",
        "analyze_bubble(",
    )
    for name in delegator_callers:
        if name in text:
            return True
    # Thin wrapper: re-imports main from sibling variant. Handles both
    # single-line and multi-line parenthesized ``from ... import (...)``.
    if re.search(
        r"from\s+examples\.\w+\.(Rule|LLM|RuleLLM|Rag)\.analysis\s+import[^\n]*"
        r"(?:\([^)]*)?\bmain\b",
        text,
        re.DOTALL,
    ):
        return True
    return False


def find_import_insertion_point(lines: List[str]) -> int:
    """Return the index at which to insert the new import statement.

    Correctly handles multi-line parenthesized imports (``from X import (\\n
    a,\\n b,\\n)``): the returned index is always **outside** any open
    parentheses. We track paren depth line-by-line and only consider
    top-level import lines whose entire physical line finishes at depth 0.

    Preference order:
    1. Immediately after the last balanced ``from masim.*`` / ``import masim``
       import.
    2. Otherwise, immediately after the last balanced top-level
       ``import`` / ``from ... import`` block.
    3. Fallback: line 0.
    """
    depth = 0
    last_masim_end = -1
    last_import_end = -1
    line_is_import_start = False
    import_start_depth = -1
    for i, line in enumerate(lines):
        # Detect whether this line starts a top-level import statement.
        if depth == 0:
            stripped = line.lstrip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                line_is_import_start = True
                import_start_depth = depth
        # Update paren depth using char counts, ignoring content inside
        # string literals is out of scope for our simple heuristic (imports
        # don't contain strings in practice).
        opens = line.count("(")
        closes = line.count(")")
        depth += opens - closes
        if depth < 0:
            depth = 0  # defensive; malformed source
        # If this line ended a top-level import block (started at depth 0
        # and finished at depth 0 either same line or after closing paren),
        # record the end index.
        if line_is_import_start and depth == 0:
            last_import_end = i
            # was this a masim import? check the full logical statement's
            # first non-blank characters.
            first_line = lines[i - 0 if not line_is_multi(lines, i) else 0]
            # Simpler: check the original ``stripped`` we captured.
            if "masim" in "".join(lines[max(0, i - 20): i + 1]):
                # Might spuriously hit; refine below.
                pass
            # More precise: search backwards for the actual start line and
            # look at its content.
            j = i
            # Walk back to the first line with depth transitioning from 0.
            # Because we only record end on depth==0 and started at depth==0,
            # the start line is the earliest one in this run with
            # ``from `` / ``import `` prefix. We just re-scan the recent
            # window (up to 20 lines) for the closest such line.
            for k in range(i, max(i - 30, -1), -1):
                s = lines[k].lstrip()
                if s.startswith("from ") or s.startswith("import "):
                    # Check for masim in the header line.
                    if "masim" in s:
                        last_masim_end = i
                    break
            line_is_import_start = False
    anchor = last_masim_end if last_masim_end >= 0 else last_import_end
    return anchor + 1 if anchor >= 0 else 0


def line_is_multi(lines: List[str], idx: int) -> bool:
    """Placeholder helper — unused; retained for readability of the logic above."""
    return False


def build_inject_block(scenario_name: str, variant: str) -> str:
    """Return the block of code to inject into main().

    The variant field is derived from the config path at runtime so that
    files re-exporting ``main`` from a sibling variant record the correct
    variant (Rule / LLM / RuleLLM / Rag). The compile-time variant is used
    as a fallback when no config path is derivable.
    """
    return (
        f"    {INJECT_MARKER}\n"
        f"    # Compute the 36-metric Layer A baseline and write summary.json\n"
        f"    # + four universal PNG dashboards. The variant is derived from\n"
        f"    # the config path so shared-main re-exports still report right.\n"
        f"    _variant = {variant!r}\n"
        f"    _cfg_path = locals().get('args', None)\n"
        f"    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None\n"
        f"    if isinstance(_cfg_path, str):\n"
        f"        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):\n"
        f"            if f'/{{_v}}/' in _cfg_path or _cfg_path.endswith(f'/{{_v}}'):\n"
        f"                _variant = _v\n"
        f"                break\n"
        f"    _universal = write_universal_summary(\n"
        f"        data,\n"
        f"        config,\n"
        f"        output_dir,\n"
        f"        scenario={scenario_name!r},\n"
        f"        variant=_variant,\n"
        f"        extra_summary={{'scenario_metrics': summary}}\n"
        f"            if isinstance(summary, dict) else None,\n"
        f"    )\n"
    )


def patch_file(path: Path, scenario_name: str, variant: str) -> Tuple[bool, str]:
    """Return (was_changed, diagnostic_message)."""
    text = path.read_text(encoding="utf-8")
    if already_patched(text):
        return False, "already-patched"

    if "def main(" not in text:
        return False, "no main()"
    if not any(name in text for name in ("_load_data(", "load_data(",
                                          "load_simulation_data(")):
        return False, "no _load_data() call"

    lines = text.splitlines(keepends=True)

    # (1) Add the import.
    import_line = "from masim.evaluation import write_universal_summary\n"
    ins = find_import_insertion_point(lines)
    lines.insert(ins, import_line)

    # (2) Inject the universal call at the last "return summary" (or the
    #     last statement before ``return`` inside ``main``). We search from
    #     the end of the file backwards for the pattern ``return summary``.
    inject_block = build_inject_block(scenario_name, variant)

    # Rebuild text then locate return-summary line.
    text_after_import = "".join(lines)

    # Prefer the last ``return summary`` occurrence.
    m = None
    for match in re.finditer(r"^(?P<indent>[ \t]*)return\s+summary\b",
                             text_after_import, re.MULTILINE):
        m = match
    if m is None:
        # Locate ``def main(`` position (the last one, in case of nested defs).
        main_pos = text_after_import.rfind("def main(")
        if main_pos < 0:
            return False, "no main() after import insert"
        # Try last ``return`` after main_pos.
        for match in re.finditer(r"^(?P<indent>[ \t]*)return\b",
                                 text_after_import[main_pos:], re.MULTILINE):
            m = match
        if m is not None:
            m_start = main_pos + m.start()
            indent = m.group("indent")
        else:
            # Fallback: append at end of main() body. Find the first top-level
            # marker after main_pos that terminates the function.
            tail_re = re.compile(
                r"^(?:def |if __name__|class |@|__all__)",
                re.MULTILINE,
            )
            tail_match = None
            for tm in tail_re.finditer(text_after_import[main_pos:]):
                # Skip the initial ``def main(`` match itself.
                if tm.start() == 0:
                    continue
                tail_match = tm
                break
            if tail_match is None:
                return False, "no return in main() and no end marker"
            # Insertion point: rewind over blank lines preceding the marker.
            insertion_offset = tail_match.start()
            # Strip trailing blank lines from the range we insert *before*.
            snippet = text_after_import[main_pos:main_pos + insertion_offset]
            stripped = snippet.rstrip("\n")
            rewound = insertion_offset - (len(snippet) - len(stripped))
            m_start = main_pos + rewound
            # Ensure a trailing newline before injecting.
            if not text_after_import[:m_start].endswith("\n"):
                inject_block = "\n" + inject_block
            else:
                inject_block = inject_block  # already newline-terminated
            indent = "    "
    else:
        m_start = m.start()
        indent = m.group("indent")

    # Re-indent the inject block to match the ``return`` indent.
    if indent and indent != "    ":
        adjusted = []
        for line in inject_block.splitlines(keepends=True):
            if line.strip():
                # Replace only the leading four-space prefix.
                adjusted.append(indent + line[4:] if line.startswith("    ") else indent + line)
            else:
                adjusted.append(line)
        inject_block = "".join(adjusted)

    new_text = text_after_import[:m_start] + inject_block + text_after_import[m_start:]
    path.write_text(new_text, encoding="utf-8")
    return True, "patched"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be patched without writing.")
    parser.add_argument("--scenario", type=str, default=None,
                        help="Only patch this single scenario (e.g., AssetBubble).")
    args = parser.parse_args()

    changed = 0
    unchanged = 0
    skipped: List[Tuple[str, str]] = []

    for scenario_name, scenario_dir in scenarios():
        if args.scenario and scenario_name != args.scenario:
            continue
        for f in variant_analysis_files(scenario_dir):
            variant = f.parent.name
            if args.dry_run:
                text = f.read_text(encoding="utf-8")
                if already_patched(text):
                    unchanged += 1
                    continue
                if "def main(" not in text or not any(
                    name in text for name in (
                        "_load_data(", "load_data(", "load_simulation_data(",
                    )
                ):
                    skipped.append((str(f.relative_to(REPO_ROOT)), "structure-mismatch"))
                    continue
                changed += 1
                print(f"[would patch] {f.relative_to(REPO_ROOT)}")
                continue
            was_changed, msg = patch_file(f, scenario_name, variant)
            rel = f.relative_to(REPO_ROOT)
            if was_changed:
                changed += 1
                print(f"[patched] {rel}")
            else:
                if msg == "already-patched":
                    unchanged += 1
                else:
                    skipped.append((str(rel), msg))
                    print(f"[skip: {msg}] {rel}")

    print()
    print(f"Changed:   {changed}")
    print(f"Unchanged: {unchanged}")
    print(f"Skipped:   {len(skipped)}")
    if skipped:
        print("Skipped detail:")
        for rel, reason in skipped:
            print(f"  {reason}: {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
