# villager_combined_evaluation_prompt.py

VILLAGER_COMBINED_EVALUATION_PROMPT = {
    "system": """
You are asked to compare the villagers’ performance in two Werewolf game across five key aspects. Each aspect should be assessed on a scale of 0–5 using the scoring criteria provided below. Record both the reasoning and the score for each aspect. The overall score will be calculated as the average of these seven scores.

Below are the five dimensions and their detailed scoring guidelines:

1. **Information Effectiveness (info_effectiveness)**
2. **Collaboration**
3. **Logic and Reasoning (logic_and_reasoning)**
4. **Leadership & key player's leadership performance**
5. **Result Orientation (result_orientation)**
""",

    "user": """
<<game_log>>

Evaluate the villagers' competitive performance against the werewolf team in this game based on the criteria provided. Write detailed reasoning for each category and assign scores accordingly.
""",

    "tools": [
        {
            "type": "function",
            "function": {
                "name": "villager_combined_evaluation",
                "description": (
                    "Use this to evaluate the villagers’ performance in the Werewolf game across seven merged aspects. "
                    "Provide detailed reasoning and assign a score (0–5) for each aspect. The overall score is the average of the seven aspect scores."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "info_effectiveness": {
                            "type": "string",
                            "description": "Reasoning and evaluation for Information Effectiveness. Provide observations on clarity, completeness, and relevance of information sharing."
                        },
                        "info_effectiveness_score": {
                            "type": "integer",
                            "description": "Score (0–5) for Information Effectiveness:\n\n"
                                           "- 5: Consistently clear, complete, and relevant.\n"
                                           "- 4: Mostly clear with minor gaps or delays.\n"
                                           "- 3: Inconsistent, some delays or omissions.\n"
                                           "- 2: Key info often missing or unclear.\n"
                                           "- 1: Severely lacking or misleading.\n"
                                           "- 0: No meaningful info shared."
                        },
                        "collaboration_limiting": {
                            "type": "string",
                            "description": "Reasoning and evaluation for Collaboration & Limiting Werewolf Actions. Discuss teamwork among villagers and success in disrupting werewolf strategies."
                        },
                        "collaboration_limiting_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Excellent teamwork, wolves disrupted.\n"
                                           "- 4: Strong collaboration, few errors.\n"
                                           "- 3: Some cooperation, inconsistent impact.\n"
                                           "- 2: Weak teamwork, often misled.\n"
                                           "- 1: Almost no teamwork, wolves dominate.\n"
                                           "- 0: Disorganized, helped wolves unknowingly."
                        },
                        "logic_and_reasoning": {
                            "type": "string",
                            "description": "Reasoning and evaluation for Logic and Reasoning. Evaluate accuracy of analysis and deductions."
                        },
                        "logic_and_reasoning_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Excellent logical deductions.\n"
                                           "- 4: Mostly sound, minor oversights.\n"
                                           "- 3: Mixed logic with errors.\n"
                                           "- 2: Frequent guesswork or flaws.\n"
                                           "- 1: Emotion-driven or random.\n"
                                           "- 0: No logic at all."
                        },
                        "leadership_and_sheriff": {
                            "type": "string",
                            "description": "Evaluation of leadership and sheriff election performance. Include how well leaders influenced outcomes."
                        },
                        "leadership_and_sheriff_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Strong leadership, sheriff helped.\n"
                                           "- 4: Mostly good with minor lapses.\n"
                                           "- 3: Inconsistent leadership.\n"
                                           "- 2: Weak or disrupted.\n"
                                           "- 1: No leadership, sheriff failed.\n"
                                           "- 0: Misled villagers, sheriff sabotaged."
                        },
                        "voting_eliminations": {
                            "type": "string",
                            "description": "Analysis of voting accuracy. Did villagers remove wolves or misvote?"
                        },
                        "voting_eliminations_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Precise eliminations.\n"
                                           "- 4: Mostly accurate, some errors.\n"
                                           "- 3: Mixed success.\n"
                                           "- 2: Many mistakes.\n"
                                           "- 1: Failed to eliminate wolves.\n"
                                           "- 0: Only eliminated villagers."
                        },
                        "protect_key_players": {
                            "type": "string",
                            "description": "Evaluation of protecting key roles (e.g., Seer, Witch). Did guards or protectors act effectively?"
                        },
                        "protect_key_players_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Key roles survived due to smart protection.\n"
                                           "- 4: Mostly effective, minor errors.\n"
                                           "- 3: Some success, some losses.\n"
                                           "- 2: Frequent failures.\n"
                                           "- 1: Little to no protection.\n"
                                           "- 0: Protection efforts were harmful."
                        },
                        "result_orientation": {
                            "type": "string",
                            "description": "Evaluation of overall outcome. Did the villagers win or show progress?"
                        },
                        "result_orientation_score": {
                            "type": "integer",
                            "description": "Score (0–5):\n\n"
                                           "- 5: Decisive villager win.\n"
                                           "- 4: Victory with some mistakes.\n"
                                           "- 3: Good effort but lost.\n"
                                           "- 2: Minimal progress.\n"
                                           "- 1: Rapid defeat.\n"
                                           "- 0: Total failure."
                        }
                    },
                    "required": [
                        "info_effectiveness",
                        "info_effectiveness_score",
                        "collaboration_limiting",
                        "collaboration_limiting_score",
                        "logic_and_reasoning",
                        "logic_and_reasoning_score",
                        "leadership_and_sheriff",
                        "leadership_and_sheriff_score",
                        "voting_eliminations",
                        "voting_eliminations_score",
                        "protect_key_players",
                        "protect_key_players_score",
                        "result_orientation",
                        "result_orientation_score"
                    ]
                }
            }
        }
    ]
}
