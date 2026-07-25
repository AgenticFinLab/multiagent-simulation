"""Documentation page — renders a scenario's bases document with a Back button.

The sidebar exposes two entry points ("📖 Simulation Bases" and
"📊 Analysis Bases") which route through the shared "Docs" page and pick
the document by writing ``st.session_state.docs_target`` to either
``"simulation_bases"`` or ``"analysis_bases"``. This module is the single
implementation of that page — a previous stale duplicate of
``render_docs_page`` used to shadow the docs_target handling and always
resolved to ``explain.md`` regardless of which button the user clicked.
"""

import streamlit as st


def render_docs_page(scenario_name: str):
    """Render a scenario's bases document (simulation or analysis).

    The document to show is selected via ``st.session_state.docs_target``:
      - ``"simulation_bases"`` (default) -> ``simulation-bases.md``
      - ``"analysis_bases"``             -> ``analysis-bases.md``

    Layout:
      - Back button (returns to the previous page)
      - Scenario name + document label header
      - Full bases markdown content rendered as markdown

    Args:
        scenario_name: Active scenario key. May be a shipped-scenario key
            like ``"AnchoringEffect/LLM"``, a project-prefixed key like
            ``"myproj/AnchoringEffect/LLM"``, or a customized-bundle key
            like ``"CUSTOMIZED_SIMULATION/{bundle}/Customized-agents"``.
            The loader chooses the right on-disk file for each shape.
    """
    from ..config_loader import (
        get_analysis_bases_content,
        get_analysis_bases_path,
        get_market_description,
        get_simulation_bases_content,
        get_simulation_bases_path,
        scenario_display_name,
    )

    target = st.session_state.get("docs_target", "simulation_bases")
    if target == "analysis_bases":
        title_icon = "📊"
        doc_label = "Analysis Bases"
        content = get_analysis_bases_content(scenario_name)
        # The concrete Path candidates the loader tried, so the empty
        # state points at the real filenames rather than a generic
        # ``examples/<Scenario>/<Variant>/...`` placeholder.
        expected_paths = _bases_candidate_paths(scenario_name, "analysis-bases.md")
    else:
        title_icon = "📖"
        doc_label = "Simulation Bases"
        content = get_simulation_bases_content(scenario_name)
        expected_paths = _bases_candidate_paths(scenario_name, "simulation-bases.md")

    # ------------------------------------------------------------------
    # Top bar: Back button + title
    # ------------------------------------------------------------------
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown("<div style='margin-top:18px'/>", unsafe_allow_html=True)
        if st.button("← Back", width="stretch", key="docs_back_btn"):
            st.session_state.current_page = st.session_state.get(
                "previous_page", "Simulation"
            )
            st.rerun()
    with col_title:
        display_name = scenario_display_name(scenario_name)
        st.title(f"{title_icon} {display_name} — {doc_label}")

    # Sub-header: market description as a short context line
    market_desc = get_market_description(scenario_name)
    if market_desc:
        st.markdown(
            f"<p style='font-size:15px; color: #a0aec0; margin-top:-10px;'>"
            f"{market_desc}</p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ------------------------------------------------------------------
    # Docs content
    # ------------------------------------------------------------------
    if content is None:
        st.warning(
            f"No {doc_label} document found for **{display_name}**."
        )
        # Show every candidate path the loader inspected. For a customized
        # bundle that means both the bundle-local copy and the shipped
        # fallback — the user can see immediately whether the missing
        # file is the source or the bundle-local copy.
        if expected_paths:
            path_lines = "\n".join(f"- `{p}`" for p in expected_paths)
            st.info(f"Looked for:\n{path_lines}")
        return

    # Strip the H1 title from the docs (we already show it above)
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    content_body = "\n".join(lines).lstrip("\n")

    st.markdown(content_body, unsafe_allow_html=False)


def _bases_candidate_paths(scenario_key: str, filename: str) -> list[str]:
    """Return the ordered list of candidate paths the bases loader tries.

    Used purely for the empty-state hint so the user sees the *real*
    locations that were inspected instead of a placeholder like
    ``examples/<Scenario>/<Variant>/...``. Paths are workspace-relative
    strings.
    """
    from pathlib import Path
    from ..config_loader import EXAMPLES_DIR, _resolve_display_key

    candidates: list[Path] = []

    # 1) For customized bundles, prefer the bundle-local copy.
    if scenario_key.startswith("CUSTOMIZED_SIMULATION/"):
        tail = scenario_key.split("/", 1)[1]
        tail_parts = tail.split("/")
        # New project-scoped format:
        #   {bundle}/Default/{variant} → look under {bundle}/Default/
        #   {bundle}/Customized-agents → look under {bundle}/Customized-agents/
        if len(tail_parts) >= 2:
            bundle_dir = EXAMPLES_DIR / "CUSTOMIZED_SIMULATION" / tail_parts[0]
            if tail_parts[1] == "Default" or tail_parts[1] == "Customized-agents":
                candidates.append(bundle_dir / tail_parts[1] / filename)

    # 2) Shipped scenario canonical path (also serves as the fallback for
    #    customized bundles when the bundle-local copy is missing).
    display_key = _resolve_display_key(scenario_key)
    parts = display_key.split("/") if display_key else []
    if parts and parts[-1] in ("Rule", "LLM", "RuleLLM", "Rag"):
        parts = parts[:-1]
    base = parts[-1] if parts else display_key
    if base:
        candidates.append(EXAMPLES_DIR / base / filename)

    # Deduplicate while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for path in candidates:
        s = str(path)
        if s in seen:
            continue
        seen.add(s)
        # Present as workspace-relative when possible for a cleaner hint.
        try:
            out.append(str(path.relative_to(EXAMPLES_DIR.parent)))
        except ValueError:
            out.append(s)
    return out
