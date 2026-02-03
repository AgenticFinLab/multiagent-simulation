 """
Prompts for different pricing scenarios: collusion vs monopoly.
- SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V1_REASONING: General system prompts.
- INITIAL_PROMPT_V1: Initial prompt for agents.
- TOOLS_COMMON: Common tools for pricing decisions.
- TOOLS_COLLUSION_V1, TOOLS_MONOPOLY_V1: Tools specific to collusion and monopoly scenarios.
- TOOLS_COLLUSION_V1_REASONING, TOOLS_MONOPOLY_V1_REASONING: Reasoning tools for each scenario.

Prompt terms:
TOOLS_COLLUSION_V1= “Returns all data from previous pricing decisions, including the user's prices,
quantities sold, per-unit costs, and competitor prices.
Read this data before making a price-setting decision.”

TOOLS_MONOPOLY_V1= "Returns all data from previous pricing decisions, including the user's prices, quantities sold,
per-unit costs, and profits earned. Always read this data before making a price-setting decision."



The prompts are used in economic experiments simulating pricing strategies under different market conditions.
"""

from econ_evals.experiments.pricing.prompts import (
    SYSTEM_PROMPT_V1,
    SYSTEM_PROMPT_V1_REASONING,
    INITIAL_PROMPT_V1,
    PROMPT_V1,
    TOOLS_COMMON,
    TOOLS_COMMON_REASONING,
)

TOOLS_COLLUSION_V1 = [
    {
        "name": "get_previous_pricing_data",
        "description": "Returns all data from previous pricing decisions, including the user's prices, quantities sold, per-unit costs, and competitor prices. Read this data before making a price-setting decision.",
        "input_schema": {"type": "object", "properties": {}},
    },
] + TOOLS_COMMON

TOOLS_MONOPOLY_V1 = [
    {
        "name": "get_previous_pricing_data",
        "description": "Returns all data from previous pricing decisions, including the user's prices, quantities sold, per-unit costs, and profits earned. Always read this data before making a price-setting decision.",
        "input_schema": {"type": "object", "properties": {}},
    },
] + TOOLS_COMMON

TOOLS_COLLUSION_V1_REASONING = [TOOLS_COLLUSION_V1[0]] + TOOLS_COMMON_REASONING
TOOLS_MONOPOLY_V1_REASONING = [TOOLS_MONOPOLY_V1[0]] + TOOLS_COMMON_REASONING

def get_prompts(prompt_type: str) -> tuple[str, str, str, list[dict], str]:
    """
    Returns the appropriate prompts and tools based on the scenario type.
    """
    if prompt_type == "collusion_v1":
        return (
            SYSTEM_PROMPT_V1,
            INITIAL_PROMPT_V1,
            TOOLS_COLLUSION_V1,
            [TOOLS_COLLUSION_V1[-1]],
            PROMPT_V1,
        )
    elif prompt_type == "monopoly_v1":
        return (
            SYSTEM_PROMPT_V1,
            INITIAL_PROMPT_V1,
            TOOLS_MONOPOLY_V1,
            [TOOLS_MONOPOLY_V1[-1]],
            PROMPT_V1,
        )
    elif prompt_type == "collusion_v1_reasoning":
        return (
            SYSTEM_PROMPT_V1_REASONING,
            INITIAL_PROMPT_V1,
            TOOLS_COLLUSION_V1_REASONING,
            [TOOLS_COLLUSION_V1_REASONING[-1]],
            PROMPT_V1,
        )
    elif prompt_type == "monopoly_v1_reasoning":
        return (
            SYSTEM_PROMPT_V1_REASONING,
            INITIAL_PROMPT_V1,
            TOOLS_MONOPOLY_V1_REASONING,
            [TOOLS_MONOPOLY_V1_REASONING[-1]],
            PROMPT_V1,
        )
    else:
        raise NotImplementedError
