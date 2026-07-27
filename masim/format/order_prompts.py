"""Investor decision format — prompt instructions and builders for LLM output.

Every canonical LLM agent must inject :data:`DECISION_FORMAT_INSTRUCTION` (or
call :func:`build_llm_system_prompt` / :func:`build_llm_user_template`) so the
prompt speaks the exact format that
:func:`masim.utils.llm_utils.parse_llm_response_with_thinking` expects and
that :meth:`masim.format.order.InvestorOrder.from_llm_decision` can consume.

Do NOT hand-write the format contract in individual agent prompts. Route
everything through the helpers below so a schema change is a one-file edit.
"""

from __future__ import annotations

from .base_prompts import ANALYSIS_DECISION_TAG, TRADING_CONSTRAINTS


DECISION_FORMAT_INSTRUCTION = """\
The decision JSON must follow this exact format:
{
    "action": "buy" | "sell" | "hold",
    "bid_price": <float>,
    "quantity": <float>,
    "reasoning": <str>,
}

Field requirements:
- action: Must be exactly "buy", "sell", or "hold".
- bid_price: Positive numeric value (e.g., 102.5). NOT expressions or formulas.
- quantity: Positive numeric value (e.g., 5.0). NOT expressions or formulas. 0 if action is "hold".
- reasoning: Concise string summarizing your analysis and rationale."""

# .format()-safe variant: braces escaped so literal JSON survives str.format()
# Use this in user-message templates that are later formatted with .format().
DECISION_FORMAT_INSTRUCTION_TPL = DECISION_FORMAT_INSTRUCTION.replace(
    "{", "{{"
).replace("}", "}}")


# ---------------------------------------------------------------------------
# Standard market-state placeholders (the ONLY variables that
# masim.agents._state.StandardMarketState.template_vars guarantees).
# ---------------------------------------------------------------------------


STANDARD_MARKET_STATE_BLOCK = (
    "Market state:\n"
    "- round: {round}\n"
    "- price: {price:.4f} (prev {prev_price:.4f}, change {price_change:+.2%})\n"
    "- fundamental: {fundamental:.4f} (deviation {deviation:+.2%})\n"
    "\n"
    "Portfolio:\n"
    "- cash: {cash:.4f}\n"
    "- position: {position:.4f}\n"
    "- portfolio_value: {portfolio_value:.4f}\n"
)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


# Markers that reliably indicate the start of the locked format tail in a
# full LLM system prompt. Any of these lines (or the header directly above
# them) means everything from that offset onward is the DECISION_FORMAT_*
# contract that the bundle writer must re-append verbatim — the persona is
# only the text BEFORE the first marker.
_PERSONA_CUT_MARKERS: tuple[str, ...] = (
    "TRADING CONSTRAINTS:",
    "== FORMAT ==",
    "Respond with your thinking in",
    "Your response MUST use the following structure",
    "The decision JSON must follow this exact format",
)


def extract_persona(full_prompt: str) -> str:
    """Return only the persona portion of a full LLM system prompt.

    Trims everything from the first occurrence of any known
    format-contract marker (see :data:`_PERSONA_CUT_MARKERS`) onward, so
    the caller can present the user with an editable persona textarea
    while keeping the locked format tail (TRADING_CONSTRAINTS +
    ANALYSIS_DECISION_TAG + DECISION_FORMAT_INSTRUCTION) safe from
    accidental edits.

    Idempotent: passing a persona-only string returns it unchanged
    (modulo trailing whitespace normalisation).  Passing an empty string
    returns an empty string.
    """
    text = full_prompt or ""
    cut_pos = len(text)
    for marker in _PERSONA_CUT_MARKERS:
        idx = text.find(marker)
        if idx != -1 and idx < cut_pos:
            cut_pos = idx
    return text[:cut_pos].rstrip("\n").rstrip()


def build_llm_system_prompt(
    *,
    persona: str,
    decision_rules: str = "",
    include_constraints: bool = True,
) -> str:
    """Compose a canonical LLM system prompt.

    Layout::

        <persona>

        DECISION RULES:
        <decision_rules>

        <TRADING_CONSTRAINTS>            # optional

        <ANALYSIS_DECISION_TAG>
        <DECISION_FORMAT_INSTRUCTION>

    Passing ``decision_rules`` is strongly recommended for Rule/LLM parity —
    it forces the model to spell out the exact quantitative rule the Rule
    sibling would apply, so behavioural drift between engines is bounded.
    """
    parts = [persona.strip()]
    if decision_rules.strip():
        parts.append("DECISION RULES:\n" + decision_rules.strip())
    if include_constraints:
        parts.append(TRADING_CONSTRAINTS)
    parts.append(ANALYSIS_DECISION_TAG)
    parts.append(DECISION_FORMAT_INSTRUCTION)
    return "\n\n".join(parts)


def build_llm_user_template(
    *,
    intro: str = "",
    extras_block: str = "",
    ask: str = "",
) -> str:
    """Compose a canonical LLM user-template string.

    Layout::

        <intro>                          # optional lead-in

        <STANDARD_MARKET_STATE_BLOCK>

        <extras_block>                   # optional per-archetype signals

        <ask>                            # optional closing question

    The result is a ``str.format()`` template — every ``{...}`` placeholder
    is resolved by :meth:`StandardMarketState.template_vars`, so agents that
    only need vanilla market signals do not have to memorise the field names.
    """
    chunks = []
    if intro.strip():
        chunks.append(intro.strip())
    chunks.append(STANDARD_MARKET_STATE_BLOCK.strip())
    if extras_block.strip():
        chunks.append(extras_block.strip())
    if ask.strip():
        chunks.append(ask.strip())
    return "\n\n".join(chunks) + "\n"


__all__ = [
    "DECISION_FORMAT_INSTRUCTION",
    "DECISION_FORMAT_INSTRUCTION_TPL",
    "STANDARD_MARKET_STATE_BLOCK",
    "build_llm_system_prompt",
    "build_llm_user_template",
    "extract_persona",
]
