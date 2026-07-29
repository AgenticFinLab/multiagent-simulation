"""Bundle generator for a customized simulation run.

A *bundle* is a self-contained pair of folders that mirrors the layout
of the existing example scenarios:

    configs/CUSTOMIZED_SIMULATION/Customized-NNN/
        simulation.yml         (copy of the chosen scenario, !include
                                directives kept and pointed at local
                                ``players.yml`` / ``topology.yml`` /
                                ``persona.yml``)
        players.yml            (regenerated from the user's selection)
        topology.yml           (star topology covering all selected
                                investors)
        persona.yml            (verbatim copy of the chosen scenario)

    examples/CUSTOMIZED_SIMULATION/Customized-NNN/
        run_customized.py      (mirror of the canonical
                                ``run_<scenario>.py`` runner; points
                                at the configs/ bundle above)
        prompts.py             (canonical, scenario-free LLM prompt
                                strings — one ``<KEY>_SYS`` /
                                ``<KEY>_USER`` constant per LLM agent)
        README.md              (provenance: timestamp, scenario,
                                agent list, link back to configs/)

The generator never writes into ``examples/<Scenario>/`` — it only
*reads* the chosen scenario once to copy ``simulation.yml`` /
``persona.yml`` and to source a single market block.  The customized
``players.yml`` references canonical agent classes via dotted import
path (``masim.agents.noise_trader:RuleNoiseTrader``); LLM prompts
reference the bundle-local ``prompts.py`` module so each bundle is
self-contained and reproducible.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from .agent_catalog import (
    get_canonical_class_path,
    get_default_prompts,
)
from .scenario_features import is_scenario_compatible


# ----------------------------------------------------------------------
# Public dataclasses
# ----------------------------------------------------------------------


# Reserved sentinel keys persisted by the Streamlit UI inside
# ``selection.params`` for LLM-flavoured engines. They carry the LLM
# hyperparameters and the user-edited prompt strings; we strip them out
# of the handbook-symbol dict before writing ``extras`` and route them
# through ``extras.llm.*`` and the bundle-local ``prompts.py`` instead.
_LLM_LM_KEY = "__llm_lm_name__"
_LLM_TEMP_KEY = "__llm_temperature__"
_LLM_TOKENS_KEY = "__llm_max_tokens__"
_LLM_SYS_KEY = "__llm_system_prompt__"
_LLM_USR_KEY = "__llm_user_prompt__"
_LLM_RESERVED = {
    _LLM_LM_KEY,
    _LLM_TEMP_KEY,
    _LLM_TOKENS_KEY,
    _LLM_SYS_KEY,
    _LLM_USR_KEY,
}

# Engines that consult ``extras.llm`` and need a prompts.py entry.
_LLM_FLAVOURED_ENGINES = {"LLM", "RuleLLM", "Rag"}


@dataclass
class CustomizedAgentSelection:
    """One investor row in the user's customized lineup.

    Attributes:
        archetype: handbook filename stem (e.g. ``"NoiseTrader"``).
        display_name: human-readable label from the catalog.
        engine: chosen decision engine (``"Rule"``, ``"LLM"`` …).
        params: handbook ``symbol → value`` dict (already user-edited).
            May include reserved ``__llm_*__`` sentinel keys carrying
            LLM hyperparameters and prompt overrides; the bundle writer
            extracts those into ``extras.llm.*`` and ``prompts.py``.
        num_instances: how many copies to spawn (default 1).
        instance_key: optional explicit YAML block key; auto-derived
            from the archetype when omitted.
    """

    archetype: str
    display_name: str
    engine: str
    params: dict[str, Any]
    num_instances: int = 1
    instance_key: Optional[str] = None


@dataclass
class CustomizedBundleResult:
    """Return value of :func:`write_customized_bundle`."""

    customized_id: str
    config_dir: Path
    example_dir: Path
    simulation_yaml: Path
    players_yaml: Path
    topology_yaml: Path
    persona_yaml: Path
    runner_path: Path
    scenario_name: str
    prompts_path: Optional[Path] = None


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


_DIR_RE = re.compile(r"^Customized-(\d+)$")


def next_customized_id(*roots: Path, width: int = 3) -> str:
    """Return ``"Customized-NNN"`` with the next available index.

    Scans every directory in ``roots`` (typically the configs/ and
    examples/ Customized parents) and picks ``max(existing) + 1`` so the
    id is unique across both trees simultaneously.
    """
    highest = 0
    for root in roots:
        if not root or not root.exists():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            m = _DIR_RE.match(child.name)
            if m:
                try:
                    highest = max(highest, int(m.group(1)))
                except ValueError:
                    continue
    next_index = highest + 1
    return f"Customized-{next_index:0{width}d}"


# ---------------------------------------------------------------------------
# Import / class-path localisation
# ---------------------------------------------------------------------------

# Sys-path prelude injected at the top of every ENTRY-POINT script inside a
# bundle. Entry-point = a script executed directly via ``python <path>`` (by
# ``run_analysis`` subprocess, ``run_customized.py``, or a user's shell). The
# prelude adds the bundle's ``Customized-agents/`` root to ``sys.path`` so
# short-form imports like ``from metrics import REGISTRY`` and
# ``from Rule.players import Market`` resolve to the bundle's own copies.
#
# Marker comment lets us detect the block and avoid duplicate injection on
# re-localisation (idempotency).
_LOCALIZE_PRELUDE_MARKER = "# ⇢ MASIM bundle-localise sys.path prelude"
_LOCALIZE_PRELUDE = f"""{_LOCALIZE_PRELUDE_MARKER}
import sys as _sys
from pathlib import Path as _Path
_BUNDLE_ROOT = _Path(__file__).resolve()
while _BUNDLE_ROOT.name and _BUNDLE_ROOT.name != "Customized-agents":
    _BUNDLE_ROOT = _BUNDLE_ROOT.parent
if _BUNDLE_ROOT.name == "Customized-agents":
    _p = str(_BUNDLE_ROOT)
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
del _sys, _Path, _BUNDLE_ROOT
# ⇠ end MASIM prelude
"""

# Files that are executed directly (subprocess entry points) and therefore
# need the sys.path prelude. Any file matching these RELATIVE paths inside
# ``example_dir`` receives the prelude.
_ENTRY_POINT_RELPATHS = frozenset({
    "run_customized.py",
    "Rule/analysis.py",
    "LLM/analysis.py",
    "RuleLLM/analysis.py",
    "Rag/analysis.py",
    # scenario-specific runners preserved from shipped examples/
    # (name pattern ``run_<scenario>.py`` — matched by suffix below).
})


def _needs_prelude(rel_path: Path) -> bool:
    """True if ``rel_path`` (relative to example_dir) is an entry-point script."""
    posix = rel_path.as_posix()
    if posix in _ENTRY_POINT_RELPATHS:
        return True
    # Scenario-specific runners: {Variant}/run_<anything>.py
    parts = posix.split("/")
    if len(parts) == 2 and parts[1].startswith("run_") and parts[1].endswith(".py"):
        return True
    return False


def _localize_bundle_imports(
    *,
    example_dir: Path,
    config_dir: Path,
    scenario_name: str,
    bundle_name: str,
) -> int:
    """Make the bundle fully self-contained: every reference to shipped
    ``examples.{Scenario}.…`` is rewritten to a short bundle-local form,
    and each entry-point script gets a ``sys.path`` prelude so that short
    form resolves inside the bundle instead of via project-root packages.

    Why not ``examples.CUSTOMIZED_SIMULATION.{bundle}.Customized-agents.<sub>``
    fully-qualified paths? Because bundle folder names include hyphens
    (e.g. ``MYTest-a4fc6d93-AnchoringEffect``) which are illegal in Python
    ``import`` statement syntax. Short-form imports ``from metrics import X``
    combined with a per-file ``sys.path.insert(0, <bundle_root>)`` prelude
    are the cleanest way to keep imports lexically legal AND ensure the
    resolved module lives inside the bundle.

    Rewrites applied to every ``.py`` under ``example_dir``:

        from examples.{S}.metrics import X           → from metrics import X
        from examples.{S}.{Var}.<mod> import X       → from {Var}.<mod> import X
        from examples.{S} import X                   → from . import X   (rare)
        import examples.{S}.<mod> [as N]             → import <mod> [as N]

    Rewrites applied to every ``*.yml`` under ``config_dir``:

        examples.{S}.<mod>:Class  → <mod>:Class     (dotted class-path form
                                                     used by masim's plug-in
                                                     loader; kept short so
                                                     the runner's importer,
                                                     which respects sys.path,
                                                     resolves inside bundle)

    Post-rewrite, scenario-specific handbook-symbol aliases are applied to
    bridge parameter-name mismatches between canonical agent classes (which
    read the handbook symbol name, e.g. ``alpha``) and the shipped scenario
    metrics/analysis code (which historically reads its own parameter name,
    e.g. ``adjustment_factor``). See :func:`_apply_handbook_symbol_aliases`.

    Entry-point scripts additionally receive the sys.path prelude at the
    top of the file (below any ``__future__`` imports, after the module
    docstring). Idempotent: the prelude is guarded by
    ``_LOCALIZE_PRELUDE_MARKER`` so repeated invocations are safe.

    Args:
        example_dir: ``examples/CUSTOMIZED_SIMULATION/{bundle}/Customized-agents/``
        config_dir:  ``configs/CUSTOMIZED_SIMULATION/{bundle}/Customized-agents/``
        scenario_name: source scenario name, e.g. ``"AnchoringEffect"``.
        bundle_name: bundle folder, e.g. ``"MYTest-a4fc6d93-AnchoringEffect"``.

    Returns:
        Number of files that were rewritten (useful for logging/tests).
    """
    src = re.escape(f"examples.{scenario_name}")

    # ── Python rewrite patterns ──────────────────────────────────────────
    # Order matters: match the most specific first.
    py_rules = [
        # from examples.{S}.<sub> import X   →  from <sub> import X
        (
            re.compile(rf"\bfrom\s+{src}\.([\w.]+)\s+import\b"),
            lambda m: f"from {m.group(1)} import",
        ),
        # from examples.{S} import X         →  from . import X
        (
            re.compile(rf"\bfrom\s+{src}\s+import\b"),
            lambda m: "from . import",
        ),
        # import examples.{S}.<sub> [as N]   →  import <sub> [as N]
        (
            re.compile(rf"\bimport\s+{src}\.([\w.]+)"),
            lambda m: f"import {m.group(1)}",
        ),
        # bare dotted refs in strings/comments
        (
            re.compile(rf"\b{src}(\.[\w.]+)"),
            lambda m: m.group(1).lstrip("."),
        ),
    ]

    yml_class_rule = (
        # examples.{S}.<mod>:Class → <mod>:Class
        re.compile(rf"\b{src}\.([\w.]+:[\w.]+)"),
        lambda m: m.group(1),
    )

    changed = 0

    # --- Rewrite Python files ---
    for py in example_dir.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = text
        for pat, repl in py_rules:
            new_text = pat.sub(repl, new_text)

        # Scenario-aware handbook-symbol aliasing (idempotent via marker).
        new_text = _apply_handbook_symbol_aliases(
            new_text, scenario_name=scenario_name, rel_path=py.relative_to(example_dir)
        )

        # Inject sys.path prelude for entry-point scripts (idempotent).
        rel = py.relative_to(example_dir)
        if _needs_prelude(rel) and _LOCALIZE_PRELUDE_MARKER not in new_text:
            new_text = _inject_prelude(new_text)

        if new_text != text:
            py.write_text(new_text, encoding="utf-8")
            changed += 1

    # --- Rewrite YAML class-paths in per-variant snapshots ---
    # (Root ``players.yml`` is regenerated fresh by apply_customized_modifications
    #  each launch and already uses canonical ``masim.agents.*`` class paths.)
    pat, repl = yml_class_rule
    for yml in config_dir.rglob("*.yml"):
        try:
            text = yml.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = pat.sub(repl, text)
        if new_text != text:
            yml.write_text(new_text, encoding="utf-8")
            changed += 1

    return changed


# ---------------------------------------------------------------------------
# Handbook-symbol alias patches
# ---------------------------------------------------------------------------

# Idempotency marker for the alias-patch block. Presence anywhere in the
# file suppresses re-patching, so users can run localization repeatedly (or
# manually edit the patched block) without duplication.
_ALIAS_PATCH_MARKER = "# ⇢ MASIM handbook-symbol alias patch"

# Per-scenario handbook-symbol alias tables. Each entry maps a shipped-code
# parameter name → (canonical handbook symbol, canonical default). At
# localization time we patch the bundle-local metrics/analysis code so it
# reads the canonical handbook symbol (matching the actual class parameter)
# with fallback to the shipped-code name and finally the canonical default.
#
# Why: the customized flow uses canonical ``masim.agents.*`` classes which
# consume handbook symbols documented in ``examples/AGENT_POOL/finance/*.md``
# (e.g. ``alpha``). The shipped scenario's ``metrics.py`` and
# ``{Variant}/analysis.py`` were written against the scenario-specific
# parameter name (e.g. ``adjustment_factor``). Without this bridge, analysis
# raises ``MetricUnavailable`` / ``ValueError`` on every customized run.
_SCENARIO_HANDBOOK_ALIASES: dict[str, dict[str, tuple[str, float]]] = {
    "AnchoringEffect": {
        "adjustment_factor": ("alpha", 0.30),
    },
}


def _apply_handbook_symbol_aliases(
    source: str, *, scenario_name: str, rel_path: Path
) -> str:
    """Rewrite handbook-symbol lookups in bundle Python code (idempotent).

    For every alias (shipped_name → (canonical_name, default_value)) declared
    for the current scenario, replace two common lookup patterns:

    1. Guarded return / raise pattern
       ``if "<shipped>" in extras: return float(extras["<shipped>"])``
       →   check canonical first, fall back to shipped, else canonical default.

    2. Bare lookup pattern
       ``extras["<shipped>"]``  or  ``extras.get("<shipped>", …)``
       →   check both keys with canonical default as final fallback.

    Only ``metrics.py`` and ``*/analysis.py`` files are touched; other bundle
    code is left alone. The patch is bracketed by ``_ALIAS_PATCH_MARKER`` so
    a second invocation is a no-op.
    """
    aliases = _SCENARIO_HANDBOOK_ALIASES.get(scenario_name)
    if not aliases:
        return source

    posix = rel_path.as_posix()
    # Restrict to files that actually query extras for these symbols.
    if not (
        posix.endswith("metrics.py") or posix.endswith("analysis.py")
    ):
        return source

    if _ALIAS_PATCH_MARKER in source:
        return source  # already patched

    new_text = source
    for shipped_name, (canonical_name, default_value) in aliases.items():
        # Pattern 1: ``if "<shipped>" in extras: return float(extras["<shipped>"])``
        # Common in both metrics.py (``_anchored_adjustment_factor``) and
        # Rule/analysis.py (``_get_adjustment_factor``). Rewrites to check
        # canonical first, then shipped, else default — preserving indent.
        pat_guarded = re.compile(
            rf'(?P<indent>[ \t]+)if\s+"{re.escape(shipped_name)}"\s+in\s+extras\s*:\s*\n'
            rf'(?P=indent)[ \t]+return\s+float\(extras\["{re.escape(shipped_name)}"\]\)',
            re.MULTILINE,
        )

        def _replace_guarded(m: re.Match) -> str:
            indent = m.group("indent")
            body_indent = indent + "    "
            return (
                f'{indent}{_ALIAS_PATCH_MARKER} ({shipped_name} → {canonical_name})\n'
                f'{indent}if "{canonical_name}" in extras:\n'
                f'{body_indent}return float(extras["{canonical_name}"])\n'
                f'{indent}if "{shipped_name}" in extras:\n'
                f'{body_indent}return float(extras["{shipped_name}"])'
            )

        new_text = pat_guarded.sub(_replace_guarded, new_text)

        # Pattern 2: bare ``raise ValueError("No <shipped> found...")`` and
        # ``raise MetricUnavailable("... <shipped> ...")`` — replace with a
        # return of the canonical default so callers can proceed with the
        # documented handbook default instead of crashing.
        raise_pat = re.compile(
            rf'(?P<indent>[ \t]+)raise\s+(?:ValueError|MetricUnavailable)\([^)]*'
            rf'{re.escape(shipped_name)}[^)]*\)',
            re.MULTILINE,
        )

        def _replace_raise(m: re.Match) -> str:
            indent = m.group("indent")
            return (
                f'{indent}{_ALIAS_PATCH_MARKER} default fallback\n'
                f'{indent}return float({default_value})'
            )

        new_text = raise_pat.sub(_replace_raise, new_text)

    return new_text


def _inject_prelude(source: str) -> str:
    """Insert the sys.path prelude at the correct spot in a Python source.

    Placement rules:
      * If the file has a ``__future__`` import block, prelude goes AFTER
        all ``from __future__ import …`` lines (Python requires future
        imports to precede any executable statement).
      * Otherwise the prelude goes right after the module docstring
        (if present) and any shebang / encoding declaration.
    """
    lines = source.splitlines(keepends=True)
    insert_at = 0

    # Skip shebang.
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    # Skip encoding declaration (must be in first two lines).
    if insert_at < len(lines) and re.match(r"^#.*coding[:=]", lines[insert_at]):
        insert_at += 1

    # Skip module-level docstring if present.
    i = insert_at
    # Skip blank/comment lines to find the first real token.
    while i < len(lines) and (lines[i].strip() == "" or lines[i].lstrip().startswith("#")):
        i += 1
    if i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith(('"""', "'''")):
            quote = stripped[:3]
            # single-line docstring?
            if stripped.count(quote) >= 2 and len(stripped) > 3:
                insert_at = i + 1
            else:
                # multi-line: find closing quote
                j = i + 1
                while j < len(lines) and quote not in lines[j]:
                    j += 1
                insert_at = min(j + 1, len(lines))

    # Skip past any __future__ imports.
    j = insert_at
    while j < len(lines):
        stripped = lines[j].strip()
        if stripped.startswith("from __future__ import"):
            j += 1
            insert_at = j
        elif stripped == "" or stripped.startswith("#"):
            j += 1
        else:
            break

    prelude_block = "\n" + _LOCALIZE_PRELUDE + "\n"
    return "".join(lines[:insert_at]) + prelude_block + "".join(lines[insert_at:])


def initialize_customized_folder(
    *,
    bundle_name: str,
    scenario_name: str,
    project_root: Path,
) -> CustomizedBundleResult:
    """Create the Customized-agents/ subfolder with a full scenario copy.

    Called lazily at launch time (inside :func:`apply_customized_modifications`)
    when the user commits their agent selections. The folder is a complete
    snapshot of the scenario — all variant subdirectories (Rule, LLM,
    RuleLLM, Rag) are copied into
    ``configs/CUSTOMIZED_SIMULATION/{bundle}/Customized-agents/`` and
    ``examples/CUSTOMIZED_SIMULATION/{bundle}/Customized-agents/``.

    This keeps the Customize path's files separate from the Default
    path's files; both live under the same project bundle directory.

    Idempotent: if ``Customized-agents/Rule/simulation.yml`` already
    exists, returns existing paths without re-copying.

    Args:
        bundle_name: folder name, e.g. ``"MyProject-a3b9c1d2-AnchoringEffect"``.
        scenario_name: scenario base name (e.g. ``"AnchoringEffect"``).
        project_root: the repo root (parent of ``configs/`` and ``examples/``).

    Returns:
        :class:`CustomizedBundleResult` with absolute paths.

    Raises:
        FileNotFoundError: the chosen scenario lacks a base ``simulation.yml``.
    """
    import shutil

    project_root = Path(project_root).resolve()
    configs_parent = project_root / "configs" / "CUSTOMIZED_SIMULATION"
    examples_parent = project_root / "examples" / "CUSTOMIZED_SIMULATION"
    config_dir = configs_parent / bundle_name / "Customized-agents"
    example_dir = examples_parent / bundle_name / "Customized-agents"

    # Idempotent: if already initialized, return existing paths.
    if (config_dir / "Rule" / "simulation.yml").exists():
        runner_out = example_dir / "run_customized.py"
        return CustomizedBundleResult(
            customized_id=bundle_name,
            config_dir=config_dir,
            example_dir=example_dir,
            simulation_yaml=config_dir / "Rule" / "simulation.yml",
            players_yaml=config_dir / "Rule" / "players.yml",
            topology_yaml=config_dir / "Rule" / "topology.yml",
            persona_yaml=config_dir / "Rule" / "persona.yml",
            runner_path=runner_out if runner_out.exists() else None,
            scenario_name=scenario_name,
            prompts_path=None,
        )

    config_dir.mkdir(parents=True, exist_ok=True)
    example_dir.mkdir(parents=True, exist_ok=True)

    # Validate that at least the Rule variant exists.
    base_rule_path = project_root / "configs" / scenario_name / "Rule"
    base_simulation = base_rule_path / "simulation.yml"
    if not base_simulation.exists():
        raise FileNotFoundError(
            "Scenario simulation file is missing for "
            f"'{scenario_name}': {base_simulation}"
        )

    def _ignore_pycache(directory: str, contents: list[str]) -> list[str]:
        return [c for c in contents if c == "__pycache__"]

    # Record paths target: {bundle_name}/Customized-agents
    record_sub = f"{bundle_name}/Customized-agents"

    # --- Copy ALL variant subdirectories from configs/{scenario}/ ---
    src_configs = project_root / "configs" / scenario_name
    for variant_dir in sorted(src_configs.iterdir()):
        if not variant_dir.is_dir() or variant_dir.name.startswith("_"):
            continue
        dst_variant = config_dir / variant_dir.name
        shutil.copytree(
            variant_dir, dst_variant,
            ignore=_ignore_pycache, dirs_exist_ok=True,
        )
        # Retarget record/storage paths in all yml files to point to the
        # bundle's own EXPERIMENT directory.
        for yml in dst_variant.glob("*.yml"):
            text = yml.read_text(encoding="utf-8")
            text = _retarget_record_paths(text, record_sub)
            if yml.name == "simulation.yml":
                text = _set_ray_namespace(text, record_sub)
            yml.write_text(text, encoding="utf-8")

    # --- Copy ALL variant subdirectories from examples/{scenario}/ ---
    src_examples = project_root / "examples" / scenario_name
    if src_examples.exists():
        for item in sorted(src_examples.iterdir()):
            if item.name.startswith("_") and item.name != "__init__.py":
                continue
            if item.is_dir():
                shutil.copytree(
                    item, example_dir / item.name,
                    ignore=_ignore_pycache, dirs_exist_ok=True,
                )
            else:
                # Copy top-level files (e.g. __init__.py, metrics.py,
                # analysis-bases.md, finance-*.md, simulation-bases.md)
                shutil.copy2(item, example_dir / item.name)

    # --- Bundle-level runner script ---
    runner_text = _render_runner_script(cid=bundle_name, scenario_name=scenario_name)
    runner_out = example_dir / "run_customized.py"
    runner_out.write_text(runner_text, encoding="utf-8")

    # --- __init__.py package marker ---
    init_path = example_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    # --- Localise all imports inside the bundle ---
    # After copytree, every .py under example_dir still references shipped
    # ``examples.{scenario_name}.…`` modules; rewrite those to bundle-local
    # short-form imports and inject a sys.path prelude into entry-point
    # scripts so subprocess execution (analysis.py, run_customized.py,
    # scenario-specific runners) resolves inside the bundle rather than
    # falling back to the shipped code tree.
    #
    # Called BEFORE README so any errors surface without leaving a
    # half-finalised bundle marked as complete.
    _localize_bundle_imports(
        example_dir=example_dir,
        config_dir=config_dir,
        scenario_name=scenario_name,
        bundle_name=bundle_name,
    )

    # --- README.md provenance placeholder ---
    readme_text = (
        f"# {bundle_name} / Customized-agents\n\n"
        f"Customized simulation bundle (scenario: `{scenario_name}`).\n\n"
        f"- **Initialized**: {_dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"- **Status**: awaiting agent selections (launch will finalize)\n\n"
        f"## Structure\n\n"
        f"All 4 variants (Rule, LLM, RuleLLM, Rag) are copied from the\n"
        f"shipped scenario as a full snapshot. The Customize flow reads\n"
        f"prompts from the variant matching the user's engine choice.\n\n"
        f"All imports inside this bundle have been *localised* — code here\n"
        f"references sibling modules directly (e.g. ``from metrics import\n"
        f"REGISTRY``) so this bundle is fully self-contained and does NOT\n"
        f"depend on the shipped ``examples/{scenario_name}/`` folder at\n"
        f"runtime.\n\n"
        f"## Run\n\n"
        f"```bash\n"
        f"python examples/CUSTOMIZED_SIMULATION/{bundle_name}/Customized-agents/"
        f"run_customized.py \\\n"
        f"    -c configs/CUSTOMIZED_SIMULATION/{bundle_name}/"
        f"Customized-agents/simulation.yml\n"
        f"```\n"
    )
    (example_dir / "README.md").write_text(readme_text, encoding="utf-8")

    return CustomizedBundleResult(
        customized_id=bundle_name,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=config_dir / "Rule" / "simulation.yml",
        players_yaml=config_dir / "Rule" / "players.yml",
        topology_yaml=config_dir / "Rule" / "topology.yml",
        persona_yaml=config_dir / "Rule" / "persona.yml",
        runner_path=runner_out,
        scenario_name=scenario_name,
        prompts_path=None,
    )


def apply_customized_modifications(
    *,
    bundle_name: str,
    selections: list[CustomizedAgentSelection],
    scenario_name: str,
    project_root: Path,
    total_rounds: Optional[int] = None,
    market_extras_override: Optional[dict[str, Any]] = None,
) -> CustomizedBundleResult:
    """Apply user's agent selections and params to the Customized-agents/ folder.

    Called at launch time. If the ``Customized-agents/`` subfolder does
    not exist yet, it is created lazily via
    :func:`initialize_customized_folder`. This function then regenerates
    ``players.yml``, ``topology.yml``, and optionally ``prompts.py``
    from the user's selections.

    Args:
        bundle_name: the project bundle folder name.
        selections: user's agent selections with edited params.
        scenario_name: scenario base name.
        project_root: repo root.
        total_rounds: optional round count override baked into simulation.yml.
        market_extras_override: optional market parameter overrides.

    Returns:
        :class:`CustomizedBundleResult` with absolute paths.

    Raises:
        ValueError: roster is incompatible or an archetype has no class path.
    """
    # --- compatibility gate ---
    roster = [s.archetype for s in selections]
    compatible, reasons = is_scenario_compatible(scenario_name, roster)
    if not compatible:
        raise ValueError(
            "Roster is not compatible with scenario "
            f"'{scenario_name}': " + "; ".join(reasons)
        )

    # --- resolve canonical class paths ---
    class_paths: list[str] = []
    for sel in selections:
        path = get_canonical_class_path(sel.archetype, sel.engine)
        if not path:
            raise ValueError(
                f"Canonical class for archetype '{sel.archetype}' with "
                f"engine '{sel.engine}' is not implemented yet. "
                "Pick a different engine or remove the agent from the "
                "roster."
            )
        class_paths.append(path)

    project_root = Path(project_root).resolve()
    config_dir = (
        project_root / "configs" / "CUSTOMIZED_SIMULATION"
        / bundle_name / "Customized-agents"
    )
    example_dir = (
        project_root / "examples" / "CUSTOMIZED_SIMULATION"
        / bundle_name / "Customized-agents"
    )

    # Lazy initialization: create Customized-agents/ if not present yet.
    if not config_dir.exists() or not (config_dir / "Rule" / "simulation.yml").exists():
        initialize_customized_folder(
            bundle_name=bundle_name,
            scenario_name=scenario_name,
            project_root=project_root,
        )

    # --- optionally update total_rounds in simulation.yml ---
    # Write a root-level simulation.yml (copied from the bundle's Rule/ copy)
    # so the runner can find it at a predictable path.
    rule_sim = config_dir / "Rule" / "simulation.yml"
    if rule_sim.exists():
        sim_text = rule_sim.read_text(encoding="utf-8")
    else:
        # Legacy fallback: flat structure from before the multi-variant change.
        flat_sim = config_dir / "simulation.yml"
        if flat_sim.exists():
            sim_text = flat_sim.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(
                f"Cannot find simulation.yml in bundle: {config_dir}"
            )
    if total_rounds is not None:
        sim_text = _set_total_rounds(sim_text, int(total_rounds))
    sim_out = config_dir / "simulation.yml"
    sim_out.write_text(sim_text, encoding="utf-8")

    # --- persona.yml at root level (from Rule/ copy) ---
    rule_persona = config_dir / "Rule" / "persona.yml"
    persona_out = config_dir / "persona.yml"
    if rule_persona.exists():
        persona_text = rule_persona.read_text(encoding="utf-8")
        persona_out.write_text(persona_text, encoding="utf-8")

    # --- prompts.py ---
    prompts_path: Optional[Path] = _maybe_write_prompts_module(
        example_dir=example_dir,
        cid=bundle_name,
        selections=selections,
    )

    # --- players.yml ---
    # Source the market block from the bundle's own Rule/ copy.
    bundle_rule_players = config_dir / "Rule" / "players.yml"
    if not bundle_rule_players.exists():
        # Fallback to shipped scenario if bundle copy is missing.
        bundle_rule_players = (
            project_root / "configs" / scenario_name / "Rule" / "players.yml"
        )
    market_block, market_key = _extract_market_block(
        bundle_rule_players, bundle_name
    )
    players_yaml_text, agent_keys = _render_players_yaml(
        market_block=market_block,
        market_key=market_key,
        selections=selections,
        class_paths=class_paths,
        cid=bundle_name,
        has_prompts_module=prompts_path is not None,
        market_extras_override=market_extras_override,
    )
    players_out = config_dir / "players.yml"
    players_out.write_text(players_yaml_text, encoding="utf-8")

    # --- topology.yml ---
    topology_text = _render_topology_yaml(
        market_key=market_key,
        agent_keys=agent_keys,
    )
    topology_out = config_dir / "topology.yml"
    topology_out.write_text(topology_text, encoding="utf-8")

    # --- Update README.md with final provenance ---
    readme_text = _render_readme(
        cid=bundle_name,
        scenario_name=scenario_name,
        selections=selections,
        timestamp=_dt.datetime.now(),
    )
    (example_dir / "README.md").write_text(readme_text, encoding="utf-8")

    return CustomizedBundleResult(
        customized_id=bundle_name,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=config_dir / "simulation.yml",
        players_yaml=players_out,
        topology_yaml=topology_out,
        persona_yaml=config_dir / "persona.yml",
        runner_path=example_dir / "run_customized.py",
        scenario_name=scenario_name,
        prompts_path=prompts_path,
    )


def write_customized_bundle(
    *,
    selections: list[CustomizedAgentSelection],
    scenario_name: str,
    project_root: Path,
    customized_id: Optional[str] = None,
    timestamp: Optional[_dt.datetime] = None,
    total_rounds: Optional[int] = None,
) -> CustomizedBundleResult:
    """Materialise a customized bundle on disk.

    Args:
        selections: list of agents the user picked, with edited params.
        scenario_name: scenario base name (e.g. ``"AnchoringEffect"``).
            The writer resolves this to ``"<scenario>/Rule"`` to source
            ``simulation.yml`` / ``persona.yml`` / the market block.
        project_root: the repo root (parent of ``configs/`` and
            ``examples/``).
        customized_id: optional explicit folder id; defaults to the next
            free one across both trees.
        timestamp: optional override (used by tests for determinism).

    Returns:
        :class:`CustomizedBundleResult` with absolute paths of every
        artifact written.

    Raises:
        ValueError: roster is incompatible with the chosen scenario, or
            an archetype has no canonical class for the chosen engine.
        FileNotFoundError: the chosen scenario lacks a base
            ``simulation.yml``.
    """
    # --- compatibility gate (defense-in-depth; Step-2 already gates) ---
    roster = [s.archetype for s in selections]
    compatible, reasons = is_scenario_compatible(scenario_name, roster)
    if not compatible:
        raise ValueError(
            "Roster is not compatible with scenario "
            f"'{scenario_name}': " + "; ".join(reasons)
        )

    # --- resolve canonical class paths up front; abort if any unmapped --
    class_paths: list[str] = []
    for sel in selections:
        path = get_canonical_class_path(sel.archetype, sel.engine)
        if not path:
            raise ValueError(
                f"Canonical class for archetype '{sel.archetype}' with "
                f"engine '{sel.engine}' is not implemented yet. "
                "Pick a different engine or remove the agent from the "
                "roster."
            )
        class_paths.append(path)

    project_root = Path(project_root).resolve()
    configs_parent = project_root / "configs" / "CUSTOMIZED_SIMULATION"
    examples_parent = project_root / "examples" / "CUSTOMIZED_SIMULATION"
    configs_parent.mkdir(parents=True, exist_ok=True)
    examples_parent.mkdir(parents=True, exist_ok=True)

    cid = customized_id or next_customized_id(configs_parent, examples_parent)
    config_dir = configs_parent / cid
    example_dir = examples_parent / cid
    config_dir.mkdir(parents=True, exist_ok=True)
    example_dir.mkdir(parents=True, exist_ok=True)

    # Resolve the scenario source: every scenario ships a Rule variant
    # whose simulation.yml / persona.yml / players.yml define the base
    # market block we copy.
    base_scenario_subkey = f"{scenario_name}/Rule"
    base_path = project_root / "configs" / base_scenario_subkey
    base_simulation = base_path / "simulation.yml"
    base_persona = base_path / "persona.yml"
    base_players = base_path / "players.yml"

    if not base_simulation.exists():
        raise FileNotFoundError(
            "Scenario simulation file is missing for "
            f"'{scenario_name}': {base_simulation}"
        )

    # --- simulation.yml: copy verbatim and rewrite the record/comm paths
    simulation_text = base_simulation.read_text(encoding="utf-8")
    simulation_text = _retarget_record_paths(simulation_text, cid)
    simulation_text = _set_ray_namespace(simulation_text, cid)
    # Honour a user-adjusted round count (from the variant_choice page)
    # by baking it into the generated config, keeping the run reproducible.
    if total_rounds is not None:
        simulation_text = _set_total_rounds(simulation_text, int(total_rounds))
    sim_out = config_dir / "simulation.yml"
    sim_out.write_text(simulation_text, encoding="utf-8")

    # --- persona.yml: copy verbatim with retargeted record paths
    persona_out = config_dir / "persona.yml"
    if base_persona.exists():
        persona_text = _retarget_record_paths(
            base_persona.read_text(encoding="utf-8"), cid
        )
        persona_out.write_text(persona_text, encoding="utf-8")
    else:
        persona_out.write_text(
            "# (no persona section in base scenario)\n", encoding="utf-8"
        )

    # --- prompts.py: materialise inline LLM prompts (if any LLM agents)
    prompts_path: Optional[Path] = _maybe_write_prompts_module(
        example_dir=example_dir,
        cid=cid,
        selections=selections,
    )

    # --- players.yml: rebuild from selections + base market block
    market_block, market_key = _extract_market_block(base_players, cid)
    players_yaml_text, agent_keys = _render_players_yaml(
        market_block=market_block,
        market_key=market_key,
        selections=selections,
        class_paths=class_paths,
        cid=cid,
        has_prompts_module=prompts_path is not None,
    )
    players_out = config_dir / "players.yml"
    players_out.write_text(players_yaml_text, encoding="utf-8")

    # --- topology.yml: star centred on the market block
    topology_text = _render_topology_yaml(
        market_key=market_key,
        agent_keys=agent_keys,
    )
    topology_out = config_dir / "topology.yml"
    topology_out.write_text(topology_text, encoding="utf-8")

    # --- run_customized.py: parameterised copy of the canonical runner
    runner_text = _render_runner_script(cid=cid, scenario_name=scenario_name)
    runner_out = example_dir / "run_customized.py"
    runner_out.write_text(runner_text, encoding="utf-8")

    # --- __init__.py so the example folder is a regular package
    init_path = example_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    # --- README.md provenance
    readme_text = _render_readme(
        cid=cid,
        scenario_name=scenario_name,
        selections=selections,
        timestamp=timestamp or _dt.datetime.now(),
    )
    (example_dir / "README.md").write_text(readme_text, encoding="utf-8")

    return CustomizedBundleResult(
        customized_id=cid,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=sim_out,
        players_yaml=players_out,
        topology_yaml=topology_out,
        persona_yaml=persona_out,
        runner_path=runner_out,
        scenario_name=scenario_name,
        prompts_path=prompts_path,
    )


def write_default_scenario_bundle(
    *,
    scenario_name: str,
    variant: str,
    total_rounds: int,
    project_root: Path,
    market_extras_override: Optional[dict[str, Any]] = None,
    agent_extras_overrides: Optional[dict[str, dict[str, Any]]] = None,
    team_name: str = "",
) -> CustomizedBundleResult:
    """DEPRECATED — produces the rejected flat ``Default-{S}-{V}-rN`` layout.

    All ``CUSTOMIZED_SIMULATION`` bundles must use the unified nested
    format ``{bundle}/Default/{V}/`` (see
    :func:`copy_default_scenario_bundle`).  The flat layout this function
    used to emit is explicitly rejected by the current architecture — its
    folder name does not match ``_BUNDLE_NAME_RE`` (``variant`` is not a
    hex-8 project id), so team-scanning helpers in
    :mod:`masim.interface.components.team_gate` cannot see it, and
    sidebar/analysis decoders will misread it as a display key.

    The function is kept as a stub only so accidental re-imports fail
    loudly instead of silently reintroducing the deprecated format.  It
    has zero live callers as of this refactor — the runtime path for
    rounds/extras overrides now goes through
    :func:`copy_default_scenario_bundle` followed by
    :func:`apply_customized_modifications`.

    Raises:
        RuntimeError: always, with a pointer to the replacement API.
    """
    raise RuntimeError(
        "write_default_scenario_bundle is deprecated dead code — it emitted "
        "the rejected flat 'Default-{S}-{V}-rN' bundle layout. Use "
        "copy_default_scenario_bundle (nested '{bundle}/Default/{V}/') "
        "followed by apply_customized_modifications for total_rounds / "
        "extras overrides."
    )
    # ------------------------------------------------------------------
    # Original body preserved for reference — the unreachable code below
    # is what used to produce the flat layout.  Kept so future readers can
    # diff intent, but never executed.
    # ------------------------------------------------------------------
    project_root = Path(project_root).resolve()
    base_path = project_root / "configs" / scenario_name / variant
    base_simulation = base_path / "simulation.yml"
    if not base_simulation.exists():
        raise FileNotFoundError(
            "Scenario simulation file is missing for "
            f"'{scenario_name}/{variant}': {base_simulation}"
        )

    base_cid = f"Default-{scenario_name}-{variant}-r{int(total_rounds)}"
    # Team-namespace the bundle folder so concurrent teams cannot clobber
    # each other's ``(scenario, variant, rounds)`` bundle.  Uses the same
    # ``team-{slug}-`` literal marker as
    # :mod:`masim.interface.customized.team_namespace` so downstream
    # decoders (sidebar, ``_resolve_display_key``) recognise it.
    if team_name:
        cid = f"team-{team_name}-{base_cid}"
    else:
        cid = base_cid
    configs_parent = project_root / "configs" / "CUSTOMIZED_SIMULATION"
    examples_parent = project_root / "examples" / "CUSTOMIZED_SIMULATION"
    config_dir = configs_parent / cid
    example_dir = examples_parent / cid
    config_dir.mkdir(parents=True, exist_ok=True)
    example_dir.mkdir(parents=True, exist_ok=True)

    # Copy every YAML verbatim; retarget record paths so this run writes
    # under its own EXPERIMENT subtree, and bake the new round count into
    # simulation.yml only. players.yml gets an extra pass to patch any
    # user-provided extras overrides.
    for yml in sorted(base_path.glob("*.yml")):
        text = _retarget_record_paths(yml.read_text(encoding="utf-8"), cid)
        if yml.name == "simulation.yml":
            text = _set_total_rounds(text, int(total_rounds))
            text = _set_ray_namespace(text, cid)
        if yml.name == "players.yml" and (
            market_extras_override or agent_extras_overrides
        ):
            text = _apply_players_extras_overrides(
                text,
                market_extras_override=market_extras_override or {},
                agent_extras_overrides=agent_extras_overrides or {},
            )
        (config_dir / yml.name).write_text(text, encoding="utf-8")

    def _out(name: str) -> Path:
        return config_dir / name

    # --- run_customized.py + package marker so the bundle is runnable
    runner_text = _render_runner_script(cid=cid, scenario_name=scenario_name)
    runner_out = example_dir / "run_customized.py"
    runner_out.write_text(runner_text, encoding="utf-8")
    init_path = example_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    # --- README.md provenance for the rounds-adjusted copy
    readme_lines = [
        f"# {cid}",
        "",
        "Auto-generated rounds-adjusted copy of a shipped scenario.",
        "",
        f"- **Scenario**: `{scenario_name}/{variant}`",
        f"- **total_rounds**: {int(total_rounds)}",
        f"- **Generated at**: "
        f"{_dt.datetime.now().isoformat(timespec='seconds')}",
        f"- **Config bundle**: `configs/CUSTOMIZED_SIMULATION/{cid}/`",
        "",
        "The roster is identical to the shipped scenario; only the round "
        "count was changed through the interface.",
        "",
        "## Run",
        "",
        "```bash",
        f"python examples/CUSTOMIZED_SIMULATION/{cid}/run_customized.py \\",
        f"    -c configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml",
        "```",
        "",
    ]
    (example_dir / "README.md").write_text(
        "\n".join(readme_lines), encoding="utf-8"
    )

    return CustomizedBundleResult(
        customized_id=cid,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=_out("simulation.yml"),
        players_yaml=_out("players.yml"),
        topology_yaml=_out("topology.yml"),
        persona_yaml=_out("persona.yml"),
        runner_path=runner_out,
        scenario_name=scenario_name,
        prompts_path=None,
    )


def copy_default_scenario_bundle(
    *,
    scenario_name: str,
    variant: str,
    bundle_name: str,
    project_root: Path,
) -> CustomizedBundleResult:
    """Copy a full shipped scenario into a Default bundle for editing.

    Creates a self-contained bundle at:
        configs/CUSTOMIZED_SIMULATION/{bundle_name}/Default/{variant}/
        examples/CUSTOMIZED_SIMULATION/{bundle_name}/Default/{variant}/

    The bundle is scoped under the project's bundle directory so multiple
    projects don't collide.  Mirrors the shipped scenario structure
    verbatim (configs YAML + examples code/docs) so users can edit
    parameters on the config page and then launch directly.  Re-targets
    ``record_path`` in ``simulation.yml`` so output goes to its own
    EXPERIMENT/ subtree.

    Idempotent: if the bundle already exists, returns existing paths
    without re-copying (so repeated page refreshes don't clobber edits).

    Args:
        scenario_name: base scenario name (e.g. ``"AnchoringEffect"``).
        variant: engine variant (e.g. ``"Rule"``).
        bundle_name: project bundle name (e.g. ``"MYTest-b6beb998-AnchoringEffect"``).
        project_root: repository root.

    Returns:
        :class:`CustomizedBundleResult` with paths to the copied bundle.
    """
    import shutil

    project_root = Path(project_root).resolve()
    cid = bundle_name

    configs_parent = project_root / "configs" / "CUSTOMIZED_SIMULATION"
    examples_parent = project_root / "examples" / "CUSTOMIZED_SIMULATION"

    config_dir = configs_parent / cid / "Default" / variant
    example_dir = examples_parent / cid / "Default" / variant

    # Idempotent: if simulation.yml already exists in the target, skip copy.
    if (config_dir / "simulation.yml").exists():
        return CustomizedBundleResult(
            customized_id=cid,
            config_dir=config_dir,
            example_dir=example_dir,
            simulation_yaml=config_dir / "simulation.yml",
            players_yaml=config_dir / "players.yml",
            topology_yaml=config_dir / "topology.yml",
            persona_yaml=config_dir / "persona.yml",
            runner_path=example_dir / "run_customized.py",
            scenario_name=scenario_name,
            prompts_path=None,
        )

    # Source directories
    src_configs = project_root / "configs" / scenario_name / variant
    src_examples = project_root / "examples" / scenario_name / variant

    if not src_configs.exists():
        raise FileNotFoundError(
            f"Source configs not found: {src_configs}"
        )

    # Copy configs (YAML files)
    config_dir.mkdir(parents=True, exist_ok=True)
    record_sub = f"{cid}/Default/{variant}"
    for yml in src_configs.glob("*.yml"):
        text = yml.read_text(encoding="utf-8")
        # Re-target record paths so the bundle writes its own data
        text = _retarget_record_paths(text, record_sub)
        if yml.name == "simulation.yml":
            text = _set_ray_namespace(text, record_sub)
        (config_dir / yml.name).write_text(text, encoding="utf-8")

    # Copy examples (code, .md, .py files — skip __pycache__)
    example_dir.mkdir(parents=True, exist_ok=True)
    if src_examples.exists():
        for item in src_examples.iterdir():
            if item.name == "__pycache__":
                continue
            dst = example_dir / item.name
            if item.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)

    # Also copy scenario-level shared files (e.g., finance-*.md, metrics.py)
    src_scenario_root = project_root / "examples" / scenario_name
    scenario_shared_dir = examples_parent / cid / "Default"
    scenario_shared_dir.mkdir(parents=True, exist_ok=True)
    for item in src_scenario_root.iterdir():
        if item.is_dir():
            continue  # skip variant subdirs and __pycache__
        dst = scenario_shared_dir / item.name
        if not dst.exists():
            shutil.copy2(item, dst)

    # Ensure __init__.py exists
    init_path = example_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")
    scenario_init = scenario_shared_dir / "__init__.py"
    if not scenario_init.exists():
        scenario_init.write_text("", encoding="utf-8")

    return CustomizedBundleResult(
        customized_id=cid,
        config_dir=config_dir,
        example_dir=example_dir,
        simulation_yaml=config_dir / "simulation.yml",
        players_yaml=config_dir / "players.yml",
        topology_yaml=config_dir / "topology.yml",
        persona_yaml=config_dir / "persona.yml",
        runner_path=example_dir / "run_customized.py"
        if (example_dir / "run_customized.py").exists()
        else None,
        scenario_name=scenario_name,
        prompts_path=None,
    )


def apply_default_bundle_overrides(
    *,
    config_dir: Path,
    total_rounds: int,
    market_extras_override: Optional[dict[str, Any]] = None,
    agent_extras_overrides: Optional[dict[str, dict[str, Any]]] = None,
) -> None:
    """Write parameter edits into an already-copied Default bundle.

    Called on Confirm & Launch — patches the bundle's simulation.yml and
    players.yml in-place with the user's round count and extras changes.

    Args:
        config_dir: path to the bundle's config directory (e.g.,
            ``configs/CUSTOMIZED_SIMULATION/Default-AnchoringEffect/Rule/``).
        total_rounds: the user-edited round count.
        market_extras_override: market coordinator extras overrides.
        agent_extras_overrides: per-agent extras overrides.
    """
    # Patch simulation.yml total_rounds
    sim_path = config_dir / "simulation.yml"
    if sim_path.exists():
        text = sim_path.read_text(encoding="utf-8")
        text = _set_total_rounds(text, int(total_rounds))
        sim_path.write_text(text, encoding="utf-8")

    # Patch players.yml extras
    players_path = config_dir / "players.yml"
    if players_path.exists() and (market_extras_override or agent_extras_overrides):
        text = players_path.read_text(encoding="utf-8")
        text = _apply_players_extras_overrides(
            text,
            market_extras_override=market_extras_override or {},
            agent_extras_overrides=agent_extras_overrides or {},
        )
        players_path.write_text(text, encoding="utf-8")


def extract_market_extras(
    *,
    bundle_name: str,
    scenario_name: str,
    project_root: Path,
) -> dict[str, Any]:
    """Extract the editable market extras from a bundle's Rule/players.yml.

    Returns the ``extras`` dict from the market (first top-level) block,
    excluding infrastructure keys (``record_path``, ``custom_state_hot_limit``)
    that users should not edit.

    Used by the Customize UI to populate the Market Parameters editor.
    """
    project_root = Path(project_root).resolve()
    # Try bundle-local copy first.
    players_path = (
        project_root / "configs" / "CUSTOMIZED_SIMULATION" / bundle_name
        / "Rule" / "players.yml"
    )
    if not players_path.exists():
        # Fallback to shipped scenario.
        players_path = (
            project_root / "configs" / scenario_name / "Rule" / "players.yml"
        )
    if not players_path.exists():
        return {}

    text = players_path.read_text(encoding="utf-8")
    market_key = _first_top_level_key(text)
    if not market_key:
        return {}

    # Parse with !include support.
    import yaml as _yaml

    class _IncludeLoader(_yaml.SafeLoader):
        pass

    _IncludeLoader.add_constructor(
        "!include",
        lambda loader, node: loader.construct_scalar(node),
    )

    try:
        data = _yaml.load(text, Loader=_IncludeLoader)
    except _yaml.YAMLError:
        return {}

    if not isinstance(data, dict) or market_key not in data:
        return {}

    market_block = data[market_key]
    extras = (market_block.get("config") or {}).get("extras") or {}

    # Filter out non-editable infrastructure keys.
    _INFRA_KEYS = {"record_path", "custom_state_hot_limit"}
    return {k: v for k, v in extras.items() if k not in _INFRA_KEYS}


# Infrastructure keys hidden from user-facing extras editors.  These are
# owned by the runner (record path, custom-state hot limit) rather than by
# the agent's behavioural parameterisation, so surfacing them would only
# encourage users to shoot themselves in the foot.
_INFRA_EXTRAS_KEYS = frozenset(
    {"record_path", "custom_state_hot_limit"}
)


def extract_default_players(
    *,
    scenario_name: str,
    variant: str,
    project_root: Path,
) -> dict[str, dict[str, Any]]:
    """Read every top-level block from a shipped ``players.yml`` file.

    Returns a mapping ``{block_key: {"name", "class", "num_instances",
    "role", "extras": {...}}}`` covering both the market coordinator block
    (first top-level key) and each investor block that follows. The
    ``extras`` sub-dict strips infrastructure-only keys (``record_path``,
    ``custom_state_hot_limit``) that are managed by the runner rather than
    the user. Returns an empty dict when the scenario has no shipped
    players.yml for this variant (defensive; also lets the UI hide the
    editor cleanly instead of crashing).

    Used by the *Default* section of the Streamlit interface to build the
    agent-parameter editor panel: every listed extras key becomes a
    ``st.number_input`` (numeric values) or ``st.text_input`` (strings)
    with an associated session-state override slot.
    """
    project_root = Path(project_root).resolve()
    players_path = project_root / "configs" / scenario_name / variant / "players.yml"
    if not players_path.exists():
        return {}

    import yaml as _yaml

    class _IncludeLoader(_yaml.SafeLoader):
        pass

    _IncludeLoader.add_constructor(
        "!include",
        lambda loader, node: loader.construct_scalar(node),
    )

    try:
        data = _yaml.load(
            players_path.read_text(encoding="utf-8"), Loader=_IncludeLoader
        )
    except _yaml.YAMLError:
        return {}

    if not isinstance(data, dict):
        return {}

    out: dict[str, dict[str, Any]] = {}
    for key, block in data.items():
        if not isinstance(block, dict):
            continue
        cfg = block.get("config") or {}
        extras_raw = cfg.get("extras") or {}
        # Separate the llm sub-block (if present) from regular extras.
        llm_block = extras_raw.get("llm") if isinstance(extras_raw.get("llm"), dict) else None
        extras = {
            k: v
            for k, v in extras_raw.items()
            if k not in _INFRA_EXTRAS_KEYS and k != "llm"
        }
        out[key] = {
            "name": block.get("name", key),
            "class": block.get("class", ""),
            "num_instances": block.get("num_instances", 1),
            "role": (cfg.get("role") or "").strip(),
            "extras": extras,
            "llm": llm_block,
        }
    return out


def _apply_players_extras_overrides(
    text: str,
    *,
    market_extras_override: dict[str, Any],
    agent_extras_overrides: dict[str, dict[str, Any]],
) -> str:
    """Rewrite a shipped ``players.yml`` text with per-block extras overrides.

    Reuses :func:`_apply_market_extras_override` to patch individual lines
    inside each top-level block while preserving all formatting, comments,
    and !include directives.  The first top-level key is treated as the
    market coordinator (matching :func:`_extract_market_block`); every
    other top-level key is matched by name against
    ``agent_extras_overrides``.  Unknown keys in either override dict are
    silently ignored so stale Streamlit widget state cannot corrupt the
    output.
    """
    # First top-level key — market coordinator — is patched via the market
    # override dict.
    market_key = _first_top_level_key(text) or ""

    # Discover every top-level key so we can slice each block, patch it,
    # and reassemble.  The market block is the first slice; investor
    # blocks follow.
    top_keys: list[str] = []
    for raw in text.splitlines():
        if not raw or raw.startswith("#") or raw[0].isspace():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", raw)
        if m:
            top_keys.append(m.group(1))

    if not top_keys:
        return text

    # Header preserved verbatim: everything before the first top-level
    # key stays as-is (including shebang/blank lines/comments).
    header_end: int = 0
    for i, raw in enumerate(text.splitlines()):
        if (
            raw
            and not raw.startswith("#")
            and not raw[0].isspace()
            and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", raw)
        ):
            header_end = i
            break
    header_lines = text.splitlines()[:header_end]

    patched_blocks: list[str] = []
    for key in top_keys:
        block = _slice_top_level_block(text, key).rstrip("\n")
        overrides: dict[str, Any] = {}
        if key == market_key:
            overrides = dict(market_extras_override or {})
        else:
            overrides = dict((agent_extras_overrides or {}).get(key) or {})
        if overrides:
            block = _apply_market_extras_override(block, overrides).rstrip("\n")
        patched_blocks.append(block + "\n")

    body = "\n".join(patched_blocks)
    return ("\n".join(header_lines) + ("\n" if header_lines else "") + body)


# ----------------------------------------------------------------------
# Helpers — players.yml
# ----------------------------------------------------------------------


def _instance_key(selection: CustomizedAgentSelection) -> str:
    """Pick a YAML block key for an agent: snake_case archetype by default."""
    if selection.instance_key:
        return selection.instance_key
    return _normalise_stem(selection.archetype)


def _camel_to_snake(text: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _normalise_stem(archetype: str) -> str:
    """Normalise an archetype id to a Python-safe snake_case stem.

    Handles both the canonical kebab-case form documented in
    ``examples/AGENT_POOL/finance/<stem>.md`` (e.g. ``"anchored-trader"``)
    and the legacy PascalCase form used by earlier canonical classes
    (e.g. ``"AnchoringBiasInvestor"``).  Downstream identifiers (YAML block
    keys, Python module stems, ``SCREAMING_SNAKE`` prompt constants) MUST
    be valid Python attribute names, which forbids ``-``.  Without this
    normalisation, ``_prompt_var_stem("anchored-trader")`` would emit
    ``ANCHORED-TRADER_SYS = ...`` and blow up the generated ``prompts.py``
    with a ``SyntaxError`` at import time.
    """
    return _camel_to_snake(archetype).replace("-", "_")


def _prompt_var_stem(archetype: str) -> str:
    """Return the SCREAMING_SNAKE stem used for prompt constants."""
    return _normalise_stem(archetype).upper()


def _split_handbook_and_llm(
    selection: CustomizedAgentSelection,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Partition ``selection.params`` into handbook-symbol and LLM-sentinel dicts.

    Reserved ``__llm_*__`` keys carry LLM hyperparameters and prompt
    overrides persisted by the Streamlit UI. They are routed to
    ``extras.llm`` / ``prompts.py`` and stripped from the handbook
    extras the canonical agent receives.
    """
    handbook: dict[str, Any] = {}
    llm: dict[str, Any] = {}
    for symbol, value in selection.params.items():
        if symbol in _LLM_RESERVED:
            llm[symbol] = value
        else:
            handbook[symbol] = value
    return handbook, llm


def _render_players_yaml(
    *,
    market_block: str,
    market_key: str,
    selections: list[CustomizedAgentSelection],
    class_paths: list[str],
    cid: str,
    has_prompts_module: bool,
    market_extras_override: Optional[dict[str, Any]] = None,
) -> tuple[str, list[str]]:
    """Compose the customized ``players.yml`` text.

    Returns:
        A tuple of (yaml_text, agent_keys) where ``agent_keys`` is the
        ordered list of deduplicated player keys (excluding the market key).
        The topology generator should use this list directly to guarantee
        consistency between players.yml and topology.yml.
    """
    record_path = f"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}/records"
    blocks: list[str] = []
    blocks.append(_HEADER_PLAYERS.format(cid=cid))

    # Apply market extras override if provided.
    final_market_block = market_block
    if market_extras_override:
        final_market_block = _apply_market_extras_override(
            market_block, market_extras_override
        )
    blocks.append(final_market_block.rstrip() + "\n")

    used_keys: set[str] = {market_key}
    agent_keys: list[str] = []
    for selection, class_path in zip(selections, class_paths):
        block, resolved_key = _render_agent_block(
            selection=selection,
            class_path=class_path,
            record_path=record_path,
            used_keys=used_keys,
            cid=cid,
            has_prompts_module=has_prompts_module,
        )
        blocks.append(block)
        agent_keys.append(resolved_key)
    return "\n".join(blocks).rstrip() + "\n", agent_keys


def _apply_market_extras_override(
    market_block: str, overrides: dict[str, Any]
) -> str:
    """Patch market extras values in the raw YAML text block.

    For each key in ``overrides``, finds the corresponding line in the
    market block (matching ``<key>: <value>``) and rewrites its value.
    This preserves comments, indentation, and ordering of the original.

    String values are quoted to prevent YAML injection (e.g. values
    containing ``:``, ``#``, or other special characters).
    """
    lines = market_block.splitlines()
    for key, new_value in overrides.items():
        pattern = re.compile(
            rf"^(\s+{re.escape(key)}\s*:\s*)(.+)$"
        )
        for i, line in enumerate(lines):
            m = pattern.match(line)
            if m:
                # Format the value appropriately.
                # Note: check bool BEFORE int since bool is a subclass of int.
                if isinstance(new_value, bool):
                    formatted = "true" if new_value else "false"
                elif isinstance(new_value, float):
                    formatted = f"{new_value}"
                elif isinstance(new_value, int):
                    formatted = str(new_value)
                else:
                    # String values: quote to prevent YAML injection.
                    s = str(new_value)
                    if any(c in s for c in (':', '#', '{', '}', '[', ']', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'")):
                        # Use double-quotes with escaped inner double-quotes.
                        formatted = '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
                    else:
                        formatted = s
                lines[i] = f"{m.group(1)}{formatted}"
                break
    return "\n".join(lines)


_HEADER_PLAYERS = """\
# =============================================================================
# {cid} — Customized Players Configuration
# =============================================================================
# Auto-generated by the Customized Simulation Builder.
# Edit through the Streamlit interface; manual edits are preserved on
# next run unless the bundle is regenerated.
# =============================================================================
"""


def _render_agent_block(
    *,
    selection: CustomizedAgentSelection,
    class_path: str,
    record_path: str,
    used_keys: set[str],
    cid: str,
    has_prompts_module: bool,
) -> tuple[str, str]:
    """Render one investor block for the customized players.yml.

    Returns:
        A tuple of (yaml_block_text, resolved_key) where resolved_key is
        the final deduplicated key used for this agent in players.yml.
    """
    base_key = _instance_key(selection)
    key = base_key
    counter = 2
    while key in used_keys:
        key = f"{base_key}_{counter}"
        counter += 1
    used_keys.add(key)
    # When num_instances > 1, expand_player_instances will produce keys
    # "{key}_1", "{key}_2", ..., "{key}_N".  Reserve those names so
    # subsequent blocks cannot collide with the expanded names.
    if selection.num_instances > 1:
        for i in range(1, selection.num_instances + 1):
            used_keys.add(f"{key}_{i}")

    handbook_params, llm_overrides = _split_handbook_and_llm(selection)
    extras: dict[str, Any] = dict(handbook_params)
    extras["record_path"] = record_path
    extras.setdefault("custom_state_hot_limit", 3)
    extras.setdefault("initial_cash", 10000.0)
    extras.setdefault("initial_position", 100.0)

    if selection.engine in _LLM_FLAVOURED_ENGINES:
        extras["llm"] = _build_llm_extras(
            archetype=selection.archetype,
            engine=selection.engine,
            llm_overrides=llm_overrides,
            cid=cid,
            has_prompts_module=has_prompts_module,
        )

    comment = (
        f"# Class: {class_path}  (canonical, resolved via masim.interface.customized.agent_catalog)\n"
        f"# Engine: {selection.engine}"
    )

    body = {
        "name": selection.display_name,
        "class": class_path,
        "num_instances": int(selection.num_instances),
        "config": {
            "identity": key,
            "role": "player",
            "steps_per_turn": 1,
            "group_tags": ["investors"],
            "extras": extras,
        },
    }
    yaml_text = yaml.safe_dump(
        {key: body},
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    yaml_text = _append_persona_include(yaml_text, key)
    return f"{comment}\n{yaml_text}".rstrip() + "\n", key


def _build_llm_extras(
    *,
    archetype: str,
    engine: str,
    llm_overrides: dict[str, Any],
    cid: str,
    has_prompts_module: bool,
) -> dict[str, Any]:
    """Translate the persisted ``__llm_*__`` overrides into ``extras.llm``.

    The result mirrors the schema the canonical
    :class:`masim.agents._base.CanonicalLLMPlayer` consumes:

        extras:
          llm:
            lm_name: <model id>
            generation_config: {temperature, max_tokens}
            sys_message: "prompts:<KEY>_SYS"
            user_message: "prompts:<KEY>_USER"

    The short module path ``prompts`` (rather than a fully-qualified dotted
    path) is used because bundle folder names contain hyphens (e.g.
    ``MYTest-a4fc6d93-AnchoringEffect``) which are illegal in Python import
    syntax.  At runtime, :func:`SimulationRunner._customized_bundle_import_root`
    adds the bundle's ``Customized-agents/`` directory to ``sys.path``, so
    ``importlib.import_module("prompts")`` resolves to the correct file.
    """
    lm_name = str(
        llm_overrides.get(_LLM_LM_KEY, "ark/doubao-seed-2-0-mini-260428")
    ).strip()
    temperature = float(llm_overrides.get(_LLM_TEMP_KEY, 0.7))
    max_tokens = int(llm_overrides.get(_LLM_TOKENS_KEY, 512))

    if has_prompts_module:
        # Use short module path — the bundle's Customized-agents/ dir is on
        # sys.path at runtime (see simulation_runner._customized_bundle_import_root).
        prompt_module = "prompts"
        stem = _prompt_var_stem(archetype)
        sys_ref = f"{prompt_module}:{stem}_SYS"
        user_ref = f"{prompt_module}:{stem}_USER"
    else:
        # Defensive fallback: should never trigger because the writer
        # always emits a prompts.py when at least one LLM agent is in
        # the roster, but we keep the references valid YAML so the
        # bundle is at least loadable.
        sys_ref = ""
        user_ref = ""

    return {
        "lm_name": lm_name,
        "generation_config": {
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        "sys_message": sys_ref,
        "user_message": user_ref,
    }


def _append_persona_include(yaml_text: str, key: str) -> str:
    """Inject ``persona: !include persona.yml`` under the agent's ``config:``.

    PyYAML cannot emit ``!include`` cleanly because we want a *string*
    that the interface's custom loader will recognise.  We therefore
    append the line manually, matching the indentation used by hand-
    written scenarios (two-space block indent inside the agent key).
    """
    suffix = "  persona: !include persona.yml\n"
    return yaml_text.rstrip() + "\n" + suffix


# ----------------------------------------------------------------------
# Helpers — prompts.py (LLM)
# ----------------------------------------------------------------------


def _maybe_write_prompts_module(
    *,
    example_dir: Path,
    cid: str,
    selections: list[CustomizedAgentSelection],
) -> Optional[Path]:
    """Materialise ``examples/CUSTOMIZED_SIMULATION/<cid>/prompts.py``.

    Each LLM-flavoured agent contributes one ``<KEY>_SYS`` and one
    ``<KEY>_USER`` constant where ``KEY`` is the SCREAMING_SNAKE form of
    the archetype name. User-edited prompt strings (carried via the
    reserved ``__llm_system_prompt__`` / ``__llm_user_prompt__`` keys)
    take precedence; otherwise the catalog-shipped scenario-free defaults
    fill in.

    Returns the prompts.py path if any LLM agents were present, else
    ``None``.
    """
    llm_selections = [
        s for s in selections if s.engine in _LLM_FLAVOURED_ENGINES
    ]
    if not llm_selections:
        return None

    seen_stems: set[str] = set()
    entries: list[tuple[str, str, str, str]] = []  # (archetype, engine, sys, user)
    for sel in llm_selections:
        stem = _prompt_var_stem(sel.archetype)
        # Distinct archetypes share a stem only by accident; if two
        # rosters of the same archetype appear, write the constants
        # once — both YAML blocks reference the same stem.
        if stem in seen_stems:
            continue
        seen_stems.add(stem)

        _, llm_overrides = _split_handbook_and_llm(sel)
        sys_text = str(llm_overrides.get(_LLM_SYS_KEY, "") or "").strip()
        user_text = str(llm_overrides.get(_LLM_USR_KEY, "") or "").strip()
        if not sys_text or not user_text:
            default_sys, default_user = get_default_prompts(
                sel.archetype, sel.engine
            )
            if not sys_text:
                sys_text = default_sys
            if not user_text:
                user_text = default_user

        # ── Re-lock the output-format contract ────────────────────────
        # The Streamlit editor exposes only the persona portion of the
        # system prompt to the user; the DECISION_FORMAT_INSTRUCTION +
        # ANALYSIS_DECISION_TAG + TRADING_CONSTRAINTS tail is always
        # appended here so the LLM output contract cannot drift
        # regardless of what the user typed (or what a legacy
        # selection_state.json carries).  ``extract_persona`` is
        # idempotent: a persona-only string passes through unchanged
        # (modulo trailing whitespace), while any full prompt gets its
        # format tail stripped before we re-append the canonical one.
        from masim.format.order_prompts import (
            build_llm_system_prompt,
            extract_persona,
        )

        persona = extract_persona(sys_text)
        if persona:
            sys_text = build_llm_system_prompt(
                persona=persona,
                include_constraints=True,
            )
        entries.append((sel.archetype, sel.engine, sys_text, user_text))

    text = _render_prompts_module(cid=cid, entries=entries)
    out = example_dir / "prompts.py"
    out.write_text(text, encoding="utf-8")
    return out


def _render_prompts_module(
    *,
    cid: str,
    entries: list[tuple[str, str, str, str]],
) -> str:
    """Compose the ``prompts.py`` text for a customized bundle."""
    header = (
        '"""Auto-generated prompt constants for ' + cid + '.\n\n'
        "One ``<ARCHETYPE>_SYS`` / ``<ARCHETYPE>_USER`` pair per LLM agent\n"
        "in the bundle. The strings are scenario-agnostic by construction —\n"
        "they originate from the marketplace catalog (discovered from\n"
        "masim.agents class metadata) or from the user's edits in the\n"
        "Streamlit interface, and are referenced by ``players.yml`` via\n"
        "dotted ``module:VAR`` paths.\n"
        '"""\n\n'
    )
    body_chunks: list[str] = [header]
    for archetype, engine, sys_text, user_text in entries:
        stem = _prompt_var_stem(archetype)
        body_chunks.append(
            f"# --- {archetype} ({engine}) ---\n"
            f"{stem}_SYS = {_py_triple_quote(sys_text)}\n\n"
            f"{stem}_USER = {_py_triple_quote(user_text)}\n\n"
        )
    return "".join(body_chunks).rstrip() + "\n"


def _py_triple_quote(text: str) -> str:
    """Render ``text`` as a triple-quoted Python string literal.

    Escapes any embedded triple quotes so the output is always parseable
    as Python source.
    """
    safe = text.replace('"""', '\\"\\"\\"')
    return '"""\\\n' + safe + '\n"""'


# ----------------------------------------------------------------------
# Helpers — topology.yml
# ----------------------------------------------------------------------


def _render_topology_yaml(
    *,
    market_key: str,
    agent_keys: list[str],
    selections: list[CustomizedAgentSelection] | None = None,
) -> str:
    """Star topology centred on the market hub.

    Args:
        market_key: The market coordinator's YAML key.
        agent_keys: Ordered list of deduplicated agent keys as resolved by
            ``_render_players_yaml``. Using this directly (instead of
            recomputing from selections) guarantees consistency between
            players.yml and topology.yml.
        selections: Deprecated / unused. Kept for backward compatibility
            but ignored when ``agent_keys`` is provided.
    """
    lines: list[str] = []
    lines.append("# Auto-generated star topology for the customized bundle.")
    lines.append("# Market is the hub; every selected investor talks to market.")
    lines.append("")
    lines.append("type: \"star\"")
    lines.append("")
    lines.append("sources:")
    lines.append(f"  - {market_key}")
    lines.append("")
    lines.append("connections:")
    lines.append(f"  {market_key}:")
    for full_key in agent_keys:
        lines.append(f"    - {full_key}")
    lines.append("")
    for full_key in agent_keys:
        lines.append(f"  {full_key}:")
        lines.append(f"    - {market_key}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ----------------------------------------------------------------------
# Helpers — base scenario reuse
# ----------------------------------------------------------------------


def _extract_market_block(base_players: Path, cid: str) -> tuple[str, str]:
    """Read the *first* coordinator/market block from the base players.yml.

    We treat the very first top-level YAML key as the market block.  The
    block is returned as raw text (preserving comments and ordering)
    along with its key.  The record_path inside is retargeted to the
    new bundle so artifacts land under EXPERIMENT/CUSTOMIZED_SIMULATION/.
    """
    if not base_players.exists():
        # Synthesise a minimal market coordinator if the base scenario
        # has no players.yml (rare; defensive).
        market_key = "market"
        block = (
            f"{market_key}:\n"
            f"  name: \"Market\"\n"
            f"  class: \"examples.AnchoringEffect.Rule.players:Market\"\n"
            f"  num_instances: 1\n"
            f"  config:\n"
            f"    identity: \"market\"\n"
            f"    role: coordinator\n"
            f"    steps_per_turn: 1\n"
            f"    group_tags: [market]\n"
            f"    extras:\n"
            f"      record_path: \"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}/records\"\n"
            f"      fundamental_value: 100.0\n"
            f"      initial_price: 105.0\n"
            f"      price_impact: 0.01\n"
            f"      mean_reversion: 0.01\n"
            f"      noise_std: 0.5\n"
            f"      custom_state_hot_limit: 3\n"
            f"  persona: !include persona.yml\n"
        )
        return block, market_key

    text = base_players.read_text(encoding="utf-8")
    # First top-level key (line that starts at column 0 with ``key:``).
    market_key = _first_top_level_key(text)
    if not market_key:
        raise ValueError(
            f"Could not locate a market block in {base_players}; "
            "the file appears to have no top-level keys."
        )
    block = _slice_top_level_block(text, market_key)
    block = _retarget_record_paths(block, cid)
    return block, market_key


def _first_top_level_key(text: str) -> Optional[str]:
    """Return the first line that defines a top-level YAML key."""
    for raw in text.splitlines():
        if not raw or raw.startswith("#"):
            continue
        if raw[0].isspace():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:", raw)
        if m:
            return m.group(1)
    return None


def _slice_top_level_block(text: str, key: str) -> str:
    """Slice the textual block belonging to a given top-level YAML key."""
    lines = text.splitlines()
    start: Optional[int] = None
    end: int = len(lines)
    pattern = re.compile(rf"^{re.escape(key)}\s*:")
    for i, line in enumerate(lines):
        if start is None:
            if pattern.match(line):
                start = i
            continue
        # End when we hit the next top-level key.
        if line and not line[0].isspace() and not line.startswith("#"):
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*:", line):
                end = i
                break
    if start is None:
        return ""
    return "\n".join(lines[start:end]).rstrip() + "\n"


_RECORD_PATH_RE = re.compile(
    r'(record_path|storage_path|checkpoint_dir)\s*:\s*"?(EXPERIMENT/[^"\n]+)"?'
)


def _retarget_record_paths(text: str, cid: str) -> str:
    """Rewrite EXPERIMENT/<scenario>/<engine>/... to live under our bundle."""
    target = f"EXPERIMENT/CUSTOMIZED_SIMULATION/{cid}"

    def _sub(match: re.Match) -> str:
        key = match.group(1)
        original = match.group(2)
        # Preserve the trailing path component (records / communication /
        # monitoring / checkpoints) so we don't collide with sibling
        # subsystems within the same bundle.
        tail = original.split("/", 2)
        if len(tail) >= 3:
            suffix = tail[2]
            # Drop the original <scenario>/<engine> prefix (first two
            # path segments after EXPERIMENT/) and graft our cid in.
            inner_parts = suffix.split("/", 1)
            kind = inner_parts[-1] if len(inner_parts) == 1 else inner_parts[1]
        else:
            kind = "records"
        return f'{key}: "{target}/{kind}"'

    return _RECORD_PATH_RE.sub(_sub, text)


_TOTAL_ROUNDS_RE = re.compile(r"^(\s*total_rounds\s*:\s*)\d+", re.MULTILINE)


def _set_total_rounds(text: str, total_rounds: int) -> str:
    """Rewrite the ``total_rounds`` value in a simulation.yml text blob.

    Only the numeric value is replaced; indentation, key spelling and any
    trailing comment are preserved. Raises ``ValueError`` if no
    ``total_rounds`` key is present so the caller fails loudly rather than
    silently launching with the shipped count.
    """
    new_text, n = _TOTAL_ROUNDS_RE.subn(
        lambda m: f"{m.group(1)}{int(total_rounds)}", text
    )
    if n == 0:
        raise ValueError("Could not locate 'total_rounds' in simulation.yml")
    return new_text


_RAY_NAMESPACE_RE = re.compile(
    r'^(\s*namespace\s*:\s*)"?([^"\n]+?)"?\s*$', re.MULTILINE
)


def _set_ray_namespace(text: str, cid: str) -> str:
    """Append bundle id to the Ray namespace for per-team actor isolation.

    Prevents actor-name collisions when multiple teams run the same base
    scenario concurrently on a shared Ray cluster.  The original namespace
    is preserved as a prefix so downstream log analysis can still identify
    the scenario source.
    """
    def _sub(m: re.Match) -> str:
        original_ns = m.group(2).strip()
        return f'{m.group(1)}"{original_ns}__{cid}"'

    new_text, n = _RAY_NAMESPACE_RE.subn(_sub, text, count=1)
    if n == 0:
        # Graceful fallback — if the key is missing the simulator will use
        # its own default; do not fail the bundle creation.
        return text
    return new_text


# ----------------------------------------------------------------------
# Helpers — runner script and README
# ----------------------------------------------------------------------


_RUNNER_TEMPLATE = '''\
#!/usr/bin/env python
"""{cid} — Customized Simulation Runner.

Auto-generated by the Customized Simulation Builder.
Scenario: {scenario_name}

Usage:
    python examples/CUSTOMIZED_SIMULATION/{cid}/run_customized.py \\
        -c configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


DEFAULT_CONFIG = "configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml"


async def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Run customized simulation {cid} (scenario: {scenario_name})"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=DEFAULT_CONFIG,
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    print("\\n" + "=" * 70)
    print("{cid} — Customized Simulation")
    print("=" * 70)
    print("Scenario:      {scenario_name}")
    print("Rounds:        %s" % config.setting["total_rounds"])
    print("=" * 70 + "\\n")

    simulator = GeneralSimulator(config)

    try:
        await simulator.setup()
        results = await simulator.run()
        print("\\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
'''


def _render_runner_script(*, cid: str, scenario_name: str) -> str:
    return _RUNNER_TEMPLATE.format(cid=cid, scenario_name=scenario_name)


def _render_readme(
    *,
    cid: str,
    scenario_name: str,
    selections: list[CustomizedAgentSelection],
    timestamp: _dt.datetime,
) -> str:
    lines = [
        f"# {cid}",
        "",
        "Auto-generated customized simulation bundle.",
        "",
        f"- **Scenario**: `{scenario_name}`",
        f"- **Generated at**: {timestamp.isoformat(timespec='seconds')}",
        f"- **Config bundle**: `configs/CUSTOMIZED_SIMULATION/{cid}/`",
        "",
        "## Selected investors",
        "",
        "| Archetype | Engine | Instances | Edited parameters |",
        "|-----------|--------|-----------|-------------------|",
    ]
    for sel in selections:
        visible = {
            k: v
            for k, v in sel.params.items()
            if k not in _LLM_RESERVED
        }
        params_short = (
            ", ".join(f"`{k}={v}`" for k, v in visible.items()) or "—"
        )
        lines.append(
            f"| {sel.archetype} | {sel.engine} | {sel.num_instances} | "
            f"{params_short} |"
        )
    lines.extend([
        "",
        "## Run",
        "",
        "```bash",
        f"python examples/CUSTOMIZED_SIMULATION/{cid}/run_customized.py \\",
        f"    -c configs/CUSTOMIZED_SIMULATION/{cid}/simulation.yml",
        "```",
        "",
    ])
    return "\n".join(lines)
