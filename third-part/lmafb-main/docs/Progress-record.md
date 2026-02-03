
## Progress Record for the Research of Behavior in Finance of LLMs


---


> [*Initial exploration of LLMs in behanvior in Finance*], [July 19, 2025], [**Yuyang Dai**]:

To present an initial exploration of the behavior of LLMs in finance, LLMs such as GPT-4o, Qwen and DeepSeek are used to analyze the **consensus** behavior of these models in a financial context. 

<details>
<summary><strong>Details:</strong></summary>

<details>
<summary><strong>Setup</strong></summary>

- **Data**: The questions recorded in the [`QuestionSettings.md`](file/QuestionSettings.xlsx) file are used to test the LLMs.
- **Models**: The models used in this exploration are GPT-4o, Qwen, Deepseek.....
- **Run**: Following the instruction below to get the result:

    ```
    python examples/Consensus/main.py
    
    ```
</details>

<details>
<summary><strong>Findings</strong></summary>

Based on the obtained `Results`, the following findings are made:

- _finding1_: When GPT-4o is consistently used as the consensus agent across multiple rounds, the process eventually converges to a single value. Interestingly, this final consensus value tends to be lower than the values proposed by individual models acting independently.
- _finding2_: When the role of the consensus agent rotates among the three models (GPT-4o, Qwen, DeepSeek), I find that GPT-4o’s consensus decision is typically closer to its own independent decision, whereas the consensus decisions made by Qwen and DeepSeek tend to diverge more significantly from their respective independent outputs.
</details>

</details>

---

> [*Advanced exploration of LLMs in behanvior in Finance*], [Sep 4, 2025], [**Yuyang Dai**]:

In this phase, the research extended to the development of a more advanced simulation framework to model investor behavior and market dynamics. The approach integrates various layers, from a simple baseline model to complex multi-agent dynamics, incorporating reinforcement learning and advanced prompt engineering to enhance decision-making in financial markets.

<details>
<summary><strong>Details:</strong></summary>

<details>
<summary><strong>Setup</strong></summary>

- **Key Components**:
  - **InvestorBase**: This module defines the abstract BaseInvestor class, which forms the foundation for all investor agents in the simulation. It manages the investor’s state, processes incoming market messages, and handles decision-making. Investors are responsible for making decisions based on market conditions and responding to the market with their investment strategies. The class tracks each decision's history, ensuring investors make informed and sequential decisions over multiple simulation rounds.
  - **MarketBase**: The BaseMarket module serves as the foundation for all market implementations in the simulation. It manages the interaction between multiple investors and processes the decisions made by investors to update the market. The module handles market clearing, price setting, and resource allocation, and generates new messages for investors based on its decisions. Markets also track the history of investor decisions and adjust policies according to market conditions in each round of simulation.
  - **Ray Simulation**: The Ray Simulation module is responsible for orchestrating the entire simulation process. It ensures that Ray is initialized correctly and connects the market and investor proxies in the Ray environment. The module manages the simulation’s execution across multiple rounds, dispatching messages between investors and markets and collecting responses. It coordinates the decision-making process for both investors and markets, allowing for parallel processing and real-time interaction between agents.
  - **Communication Protocols**: This module defines the protocols for message encoding and decoding between investors and markets. M2ICommProtocol and I2MCommProtocol facilitate the exchange of business messages, with each protocol defining how to encode and decode messages at the wire level. These protocols ensure that messages are properly formatted and transmitted between market and investor actors, supporting the asynchronous nature of the simulation and enabling clear communication during decision-making.
  - **Investor Proxy**: The Investor Proxy module implements a Ray actor that hosts the BaseInvestor class. It acts as an intermediary between the simulation framework and individual investor agents. The proxy processes market messages, decodes them into business messages, and handles the decision-making process for the investor. Once the investor has made a decision, the proxy builds and sends the investor’s response back to the market, ensuring that each investor can operate independently and asynchronously within the simulation.
  - **Market Proxy**: The Market Proxy module is a Ray actor that hosts the BaseMarket class and manages market-level decision-making. It processes investor messages, decodes them, and applies the market rules to make decisions on market clearing, price setting, and resource allocation. The proxy then generates new market messages to be sent back to the investors. It enables the market to operate asynchronously in parallel with multiple investors, ensuring that decisions can be made at scale in the simulation.

</details>

<details>
<summary><strong>Findings</strong></summary>

- **Next Steps**:
  - **Market-Investor Price Bidding Model (Baseline) 【Achieved】**：The simplest model shows that each investor adjusts their bid and ask prices based on their respective strategies (e.g., arbitrage, conservative investing, high-frequency trading). Market liquidity and price volatility are key influences, but no explicit collusion behavior emerges. The decisions are made using a linear weighting approach to balance risk and reward, ensuring that investors respond to price fluctuations and liquidity conditions.
  - **Advanced Financial Market Simulation**：As the complexity of the model increases, including advanced mathematical formulations, investors' actions become more intricate. Price impact, liquidity, and volatility adjustments are modeled in a sophisticated manner. The model simulates several rounds of bidding to assess whether collusion or emergent price manipulation behaviors begin to form as the interactions continue. Collusion is detected using specialized mathematical techniques that quantify price alignment and potential manipulation.
  - **Reinforcement Learning Integration**：By incorporating reinforcement learning (RL), the agents adjust their bidding strategies dynamically based on the observed market conditions and their own past decisions. This adaptability leads to more strategic decision-making and provides a way to study how market forces evolve and how agents learn to optimize their strategies over time.
  - **Advanced Prompt Engineering**：Using advanced prompt techniques, the market and investor models can be enhanced to reflect complex behaviors and decision-making processes. These prompts provide agents with contextual information about market conditions, guiding them toward more informed strategic decisions.
  - **Multi-Agent Dynamic Adjustment**：The final model layer introduces multi-agent dynamics, where each investor continually adapts its behavior based on interactions with other agents and the evolving market conditions. This ensures a more realistic simulation of market forces, as the behaviors of one investor influence others, leading to complex emergent phenomena like price convergence, volatility, and potential collusion.
</details>


</details>

---





