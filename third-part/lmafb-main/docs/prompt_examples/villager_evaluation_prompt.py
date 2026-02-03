# villager_evaluation_prompt.py

VILLAGER_EVALUATION_PROMPT = {
    "system": """
You are evaluating the communication performance of villagers in a Werewolf game. Your task is to analyze their performance across five key aspects: information effectiveness, collaboration, logic and reasoning, leadership and guidance, and result orientation.
Use the detailed scoring criteria provided to score each aspect on a scale of 0-5. Record both reasoning and scores for each aspect. The overall score will be calculated as the average of these scores.

Here are the detailed scoring criteria for each aspect:

**Information Effectiveness**
- **5**: Information was consistently clear, complete, and relevant. Key points were shared promptly, and discussions integrated critical data effectively.
- **4**: Most information was effectively conveyed, with minor gaps or delays. These had limited impact on decision-making.
- **3**: Information sharing was inconsistent, with some delays or omissions. Discussions relied more on reactions than proactive integration of data.
- **2**: Key information was often missed or not conveyed clearly. This negatively impacted the village's ability to strategize effectively.
- **1**: Communication was severely lacking or misleading, leading to confusion and disrupted strategies.
- **0**: No meaningful information was shared, and discussions failed to contribute to strategic decisions.

**Collaboration**
- **5**: The villagers demonstrated excellent collaboration, consistently aligning on voting and strategy with clear teamwork.
- **4**: Collaboration was strong overall, with occasional misalignments that had limited impact on outcomes.
- **3**: Some degree of collaboration was present, but frequent misalignments or conflicts hindered effectiveness.
- **2**: Collaboration was weak, with significant disagreements or disorganization impacting strategy.
- **1**: Little to no collaboration was evident, with players acting independently to the detriment of the village.
- **0**: Complete lack of collaboration, with villagers entirely disorganized and working against each other.

**Logic and Reasoning**
- **5**: Logical analysis was excellent, consistently leading to accurate deductions and effective strategies.
- **4**: Reasoning was mostly sound, with minor errors or oversights that had limited impact.
- **3**: Reasoning showed some merit but included notable mistakes or lapses in logic that hindered effectiveness.
- **2**: Logical analysis was weak, with frequent errors or reliance on intuition over evidence.
- **1**: Logic was severely lacking, with decisions driven primarily by emotion or random guesses.
- **0**: No logical reasoning was evident, with actions entirely arbitrary or self-defeating.

**Leadership and Guidance**
- **5**: Leadership was strong and consistent, providing clear direction and rallying villagers effectively.
- **4**: Leadership was mostly effective, with occasional lapses in guidance or authority.
- **3**: Leadership was present but inconsistent, with limited impact on overall strategy.
- **2**: Leadership was weak, with little direction or influence on the village's decisions.
- **1**: No meaningful leadership was evident, leaving the village disorganized.
- **0**: Leadership was actively harmful, misleading villagers and disrupting strategy.

**Result Orientation**
- **5**: The villagers achieved a decisive victory with strong communication and strategy throughout.
- **4**: The villagers succeeded but with some mistakes or inefficiencies that slightly delayed the outcome.
- **3**: The villagers showed progress toward their goals but failed to secure victory due to notable errors or disorganization.
- **2**: The villagers made limited progress, with poor communication and strategy contributing to their defeat.
- **1**: The villagers failed almost entirely, with communication breakdowns leading to rapid loss.
- **0**: The villagers were utterly ineffective, showing no progress toward their goals and losing decisively.
""",

    "user": """
<<game_log>>

Evaluate the villagers' performance in this game based on the criteria provided. Write detailed reasoning for each category and assign scores accordingly.
""",

    "tools": [
        {
            "type": "function",
            "function": {
                "name": "villager_evaluation",
                "description": (
                    "You are asked to evaluate the communication performance of the villagers in the werewolf game. "
                    "Follow the detailed scoring criteria provided below to assess and score their performance in five key aspects, "
                    "and record your reasoning and scores in corresponding fields. The overall score will be calculated as the average of the five aspect scores."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "info_effectiveness": {
                            "type": "string",
                            "description": "Your reasoning and evaluation of how effectively the villagers conveyed critical information during the game. Include examples and identify any strengths or weaknesses."
                        },
                        "info_effectiveness_score": {
                            "type": "integer",
                            "description": "The score for information effectiveness (0-5)."
                        },
                        "collaboration": {
                            "type": "string",
                            "description": "Your analysis of how well the villagers collaborated, including their ability to align their actions and reach consensus during voting and discussions."
                        },
                        "collaboration_score": {
                            "type": "integer",
                            "description": "The score for collaboration (0-5)."
                        },
                        "logic_and_reasoning": {
                            "type": "string",
                            "description": "Your evaluation of the logical and analytical capabilities of the villagers, including their ability to identify werewolves and avoid significant errors."
                        },
                        "logic_and_reasoning_score": {
                            "type": "integer",
                            "description": "The score for logic and reasoning (0-5)."
                        },
                        "leadership_and_guidance": {
                            "type": "string",
                            "description": "Your analysis of whether any player demonstrated strong leadership or effectively guided the village toward strategic decisions."
                        },
                        "leadership_and_guidance_score": {
                            "type": "integer",
                            "description": "The score for leadership and guidance (0-5)."
                        },
                        "result_orientation": {
                            "type": "string",
                            "description": "Your reasoning regarding the villagers' ability to achieve their goals, including how their communication contributed to the final result."
                        },
                        "result_orientation_score": {
                            "type": "integer",
                            "description": "The score for result orientation (0-5)."
                        }
                    },
                    "required": [
                        "info_effectiveness",
                        "info_effectiveness_score",
                        "collaboration",
                        "collaboration_score",
                        "logic_and_reasoning",
                        "logic_and_reasoning_score",
                        "leadership_and_guidance",
                        "leadership_and_guidance_score",
                        "result_orientation",
                        "result_orientation_score"
                    ]
                }
            }
        }
    ]
}
