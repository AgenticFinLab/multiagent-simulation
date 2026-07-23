"""Documentation page — renders a scenario's bases document with a Back button."""

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
        scenario_name: Name of the selected scenario
    """
    from ..config_loader import (
        get_analysis_bases_content,
        get_market_description,
        get_simulation_bases_content,
        scenario_display_name,
    )

    target = st.session_state.get("docs_target", "simulation_bases")
    if target == "analysis_bases":
        title_icon = "📊"
        doc_label = "Analysis Bases"
        content = get_analysis_bases_content(scenario_name)
        expected_path = "examples/<Scenario>/analysis-bases.md"
    else:
        title_icon = "📖"
        doc_label = "Simulation Bases"
        content = get_simulation_bases_content(scenario_name)
        expected_path = "examples/<Scenario>/simulation-bases.md"

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
        st.info(f"Expected at: `{expected_path}`")
        return

    # Strip the H1 title from the docs (we already show it above)
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    content_body = "\n".join(lines).lstrip("\n")

    st.markdown(content_body, unsafe_allow_html=False)
"""Documentation page — renders a scenario's explain.md with a Back button."""

import streamlit as st


def render_docs_page(scenario_name: str):
    """Render the full documentation page for a scenario.

    Layout:
      - Back button (returns to Simulation page)
      - Scenario name + short principle header
      - Full explain.md content rendered as markdown

    Args:
        scenario_name: Name of the seclected scenario
    """
    from ..config_loader import (
        get_docs_content,
        get_market_description,
        scenario_display_name,
    )

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
        st.title(f"📚 {display_name}")

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
    docs_content = get_docs_content(scenario_name)

    if docs_content is None:
        st.warning(f"No documentation file found for **{display_name}**.")
        st.info(f"Expected at: `examples/<Scenario>/<Variant>/explain.md`")
        return

    # Strip the H1 title from the docs (we already show it above)
    lines = docs_content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    content_body = "\n".join(lines).lstrip("\n")

    st.markdown(content_body, unsafe_allow_html=False)
