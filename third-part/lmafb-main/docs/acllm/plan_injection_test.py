# plan_injection_test.py
def inject_plan(agent: LLMPriceAgent, injected_sentence: str):
    # compare with the previous price and the price now, find the price differences
    agent.memory[-1]["plan"] = injected_sentence
