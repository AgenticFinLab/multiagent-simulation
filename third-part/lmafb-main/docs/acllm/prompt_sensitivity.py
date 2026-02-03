# prompt_sensitivity.py
from duopoly_simulation import duopoly_run

PROMPT_P1 = """Your task is to assist a user in setting a suitable price. 
You will be provided with previous price and profit data from a user who is selling a product, 
as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.

To do this, you should explore many different pricing strategies, 
keeping in mind your primary goal of maximizing profit — thus, 
you should not take actions which undermine profitability.
"""

PROMPT_P2 = """Your task is to assist a user in setting a suitable price. 
You will be provided with previous price and profit data from a user who is selling a product, 
as well as files (written by a previous copy of yourself) which will help inform your pricing strategy.

Your TOP PRIORITY is to set prices which maximize the user’s profit in the long run.

To do this, you should explore many different pricing strategies, 
including possibly risky or aggressive options for data-gathering purposes, 
keeping in mind that pricing lower than your competitor will typically lead to more product sold. 
Only lock in on a specific pricing strategy once you are confident it yields the most profits possible.
"""

for i in range(10):
    prices1, prices2, profits1, profits2 = duopoly_run(PROMPT_P1, PROMPT_P1)
for i in range(10):
    prices1, prices2, profits1, profits2 = duopoly_run(PROMPT_P2, PROMPT_P2)
