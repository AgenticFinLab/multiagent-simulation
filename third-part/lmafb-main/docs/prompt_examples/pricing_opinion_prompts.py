"""
Prompt Descriptions:
- SYSTEM_PROMPT_V1:
“You will be given some information about a group of users.
Your task is to write a very short opinion that all users would agree with as much as possible.
The users have been pre-selected to have relatively similar opinions.
Accordingly, the opinion that you write should take a single, concrete stance on the topic.
The opinion that you write should sound like an opinion a user would write, and not like a summary of viewpoints.
Write your opinion in XML tags <opinion>...</opinion>.”

- SYSTEM_PROMPT_V2:
“You will be given information about a group of users and their thoughts on a topic.
Your task is to write an extremely concise, strong opinion that reflects a single,
clear stance reflecting the users' thoughts. The opinion should sound personal, direct,
and conversational, as if written by someone expressing their own thoughts.
Avoid summary-style language or listing multiple viewpoints.
Write the opinion in XML tags <opinion>...</opinion>.”

- SYSTEM_PROMPT_V3_VERY_HIGH_DETAIL:
“You will be given information about a group of users and their thoughts on a topic.
Your task is to write a very extremely concise, strong opinion that reflects a single,
clear stance reflecting the users' thoughts. The opinion should sound personal, direct,
and conversational, as if written by someone expressing their own thoughts.
Avoid summary-style language or listing multiple viewpoints.
The level of detail included in the opinion you write should be MODERATE.
Write the opinion in XML tags <opinion>...</opinion>.”

- SYSTEM_PROMPT_V3_MODERATE_DETAIL:
“You will be given information about a group of users and their thoughts on a topic.
Your task is to write a very extremely concise, strong opinion that reflects a single,
clear stance reflecting the users' thoughts. The opinion should sound personal, direct,
and conversational, as if written by someone expressing their own thoughts.
void summary-style language or listing multiple viewpoints.
The level of detail included in the opinion you write should be MODERATE.
Write the opinion in XML tags <opinion>...</opinion>.”

- SYSTEM_PROMPT_V3_LOW_DETAIL:
“You will be given information about a group of users and their thoughts on a topic.
Your task is to write a very extremely concise, strong opinion that reflects a single,
clear stance reflecting the users' thoughts. The opinion should sound personal, direct,
and conversational, as if written by someone expressing their own thoughts.
Avoid summary-style language or listing multiple viewpoints.
The level of detail included in the opinion you write should be LOW.
Write the opinion in XML tags <opinion>...</opinion>.”

These prompts are used to generate content based on user opinions with varying levels of detail and intensity.
"""

# Defining the system prompts for different levels of detail
SYSTEM_PROMPT_V1 = """
You will be given some information about a group of users. Your task is to write a very short opinion that all users would agree with as much as possible. The users have been pre-selected to have relatively similar opinions. Accordingly, the opinion that you write should take a single, concrete stance on the topic. The opinion that you write should sound like an opinion a user would write, and not like a summary of viewpoints. Write your opinion in XML tags <opinion>...</opinion>.
""".strip()

SYSTEM_PROMPT_V2 = """
You will be given information about a group of users and their thoughts on a topic. Your task is to write an extremely concise, strong opinion that reflects a single, clear stance reflecting the users' thoughts. The opinion should sound personal, direct, and conversational, as if written by someone expressing their own thoughts. Avoid summary-style language or listing multiple viewpoints. Write the opinion in XML tags <opinion>...</opinion>.
""".strip()

SYSTEM_PROMPT_V3_VERY_HIGH_DETAIL = """
You will be given information about a group of users and their thoughts on a topic. Your task is to write a very extremely concise, strong opinion that reflects a single, clear stance reflecting the users' thoughts. The opinion should sound personal, direct, and conversational, as if written by someone expressing their own thoughts. Avoid summary-style language or listing multiple viewpoints. The level of detail included in the opinion you write should be VERY HIGH. Write the opinion in XML tags <opinion>...</opinion>.
""".strip()

SYSTEM_PROMPT_V3_MODERATE_DETAIL = """
You will be given information about a group of users and their thoughts on a topic. Your task is to write a very extremely concise, strong opinion that reflects a single, clear stance reflecting the users' thoughts. The opinion should sound personal, direct, and conversational, as if written by someone expressing their own thoughts. Avoid summary-style language or listing multiple viewpoints. The level of detail included in the opinion you write should be MODERATE. Write the opinion in XML tags <opinion>...</opinion>.
""".strip()

SYSTEM_PROMPT_V3_LOW_DETAIL = """
You will be given information about a group of users and their thoughts on a topic. Your task is to write a very extremely concise, strong opinion that reflects a single, clear stance reflecting the users' thoughts. The opinion should sound personal, direct, and conversational, as if written by someone expressing their own thoughts. Avoid summary-style language or listing multiple viewpoints. The level of detail included in the opinion you write should be LOW. Write the opinion in XML tags <opinion>...</opinion>.
""".strip()

# Function to return the correct system prompt based on the input type
def get_system_prompt_fast_no_budget_generator(prompt_type: str) -> str:
    if prompt_type == "v1":
        return SYSTEM_PROMPT_V1
    elif prompt_type == "v2":
        return SYSTEM_PROMPT_V2
    elif prompt_type == "v3_very_high_detail":
        return SYSTEM_PROMPT_V3_VERY_HIGH_DETAIL
    elif prompt_type == "v3_moderate_detail":
        return SYSTEM_PROMPT_V3_MODERATE_DETAIL
    elif prompt_type == "v3_low_detail":
        return SYSTEM_PROMPT_V3_LOW_DETAIL
    else:
        raise ValueError(f"Invalid prompt_type: {prompt_type}")
