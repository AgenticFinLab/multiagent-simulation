"""Investor decision format -- prompt instruction for LLM output."""

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
