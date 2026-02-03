"""
LLMAlgorithmicMarket: Large Language Model-Driven Market Clearing Engine

An algorithmic market that uses Large Language Models to determine equilibrium
prices and volumes based on investor orders and market microstructure dynamics.

Implements Walrasian/auction-based clearing via LLM reasoning about:
- Order flow aggregation and matching
- Price impact (temporary and permanent)
- Bid-ask spread dynamics
- Market maker behavior
- Excess demand balancing


Academic References
Classical Market Microstructure Theory:

[1] Walras, L. (1874).
    "Elements of Pure Economics."
    Original formulation of Walrasian equilibrium concept.

    Theoretical foundation: Markets clear at price where quantity demanded
    equals quantity supplied. LLM used to compute this equilibrium.

[2] Kyle, A. S. (1985).
    "Continuous Auctions and Insider Trading."
    Econometrica, 53(6), 1315-1335.

    Introduces strategic trading and price impact model:
    Price change = λ * net order flow
    Foundation for temporary and permanent impact parameters.

[3] Glosten, L. R., & Milgrom, P. R. (1985).
    "Bid, Ask and Transaction Prices in a Specialist Market with
     Heterogeneously Informed Traders."
    Journal of Financial Economics, 14(1), 71-100.

    Derives bid-ask spread as function of information asymmetry.
    Shows spread compensates market maker for adverse selection risk.

[4] O'Hara, M. (2015).
    "High Frequency Market Microstructure."
    Journal of Financial Economics, 116(2), 257-270.

    Reviews modern market microstructure with high-frequency trading.
    Discusses permanent vs temporary impact and price formation.

[5] Huang, A., Wang, H., & Yang, Y. (2023).
    "GPT goes to Wall Street: Roles, Promises, and Challenges for Generative AI
     in Financial Decision-Making."
    arXiv preprint arXiv:2307.10485.

    Evaluates LLM capabilities for financial reasoning and decision-making.
    Shows LLMs can aggregate complex market information.


Walrasian Clearing Process:

1. Order Aggregation:
   - Collect buy/sell orders from all investors
   - Aggregate into demand and supply curves

2. Equilibrium Computation:
   - Find price P* where Quantity Demanded = Quantity Supplied
   - LLM reasons about order flow and market conditions

3. Price Impact:
   - Temporary impact: λ_temp * (net_order_flow)^α
     (Recovers as market maker adjusts inventory)

   - Permanent impact: λ_perm * (net_order_flow)
     (Information content of trades moves price permanently)

4. Bid-Ask Spread:
   - Compensates market maker for:
     * Adverse selection (informed vs uninformed traders)
     * Inventory risk
     * Operating costs

5. Market Dynamics:
   - Noise traders add randomness
   - Supply elasticity determines volume response to prices
   - True drift and volatility represent fundamental value process

"""
import os
import json
import asyncio
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

from llmgt.utils.llm_init import init_llm_client
from llmgt.communication.base import I2MMessage
from llmgt.market.general import GeneralMarket
from llmgt.market import base


class LLMAlgorithmicMarket(GeneralMarket):
    """
    Large Language Model-Driven Algorithmic Market Clearing Engine

    This market uses LLMs to determine equilibrium prices and volumes through
    reasoning about order flow, market microstructure, and price impacts.

    Implements a Walrasian/auction-based clearing mechanism where:

    1. Investors submit buy/sell orders
    2. LLM aggregates orders and market state information
    3. LLM reasons about equilibrium price that clears the market
    4. LLM computes price impacts and bid-ask spreads
    5. Price is updated and market state is reported back to investors

    This creates a feedback loop where investor expectations of prices
    influence their orders, and actual prices reflect the aggregate
    order flow (mediated by LLM reasoning).
    """

    def __init__(self, config, investor_ids):
        super().__init__(config, investor_ids)
        self.llm_api_config = config.extras["llm_api"]

        # Load API key from environment variables
        load_dotenv()
        self.llm_api_config["api_key"] = os.getenv("API_KEY")

        # Initialize LLM Client
        # Initialize OpenAI-compatible LLM client
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )
        self.decision_prompt = config.extras["decision_prompt"]

        # Core market parameters
        self.market_name = config.extras["market_name"]
        self.initial_price = config.extras["initial_price"]
        self.price = self.initial_price
        self.price_floor = config.extras["price_floor"]
        self.true_drift = config.extras["true_drift"]
        self.true_volatility = config.extras["true_volatility"]
        self.dt = config.extras["dt"]
        self.risk_free_rate = config.extras["risk_free_rate"]

        # Market mechanism parameters
        self.total_shares = config.extras["total_shares_outstanding"]
        self.clearing_mechanism = config.extras["clearing_mechanism"]
        self.supply_elasticity = config.extras["supply_elasticity"]

        # Impact model
        self.temp_impact_coef = config.extras["temporary_impact_coef"]
        self.temp_impact_exp = config.extras["temporary_impact_exponent"]
        self.perm_impact_coef = config.extras["permanent_impact_coef"]

        # Market maker / noise
        self.has_market_maker = config.extras["has_market_maker"]
        self.market_maker_spread = config.extras["market_maker_spread"]
        self.market_maker_depth = config.extras["market_maker_depth"]

        # Noise traders
        self.noise_trader_fraction = config.extras["noise_trader_fraction"]
        self.noise_trader_volatility = config.extras["noise_trader_volatility"]

        # Tracking
        self.price_history = [self.price]
        self.volume_history = []
        self.computation_delay = config.extras["computation_delay"]

    def __getstate__(self):
        """
        Prepare object for serialization (called by Ray before pickling).

        Called when Ray needs to serialize this object
        1. Copy all object attributes
        2. Delete llm_client (contains thread lock, cannot be serialized)
        3. Keep llm_api_config for reinitialization
        4. Return a serializable dictionary
        """
        # Get all properties of an object
        state = self.__dict__.copy()

        # Delete un-serialize LLM clients
        # Ray will reinitialize it when __setstate__() is called in the remote worker process.
        del state['client']

        return state

    def __setstate__(self, state):
        """
        Restore object from serialization (called by Ray after unpickling).

        When Ray deserializes an object in a remote worker process, the following strategies are invoked:
        1. Restore all saved attributes.
        2. Reinitialize llm_client using the saved llm_api_config.
        3. The object is fully available in the remote process.
        """
        # Restore object properties
        self.__dict__.update(state)

        # Reinitialize the LLM client
        # This is performed in the remote worker process, allowing secure use of API keys.
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )

    async def decide(self, messages: list[I2MMessage]) -> base.MarketDecision:
        """
        Perform market clearing via LLM-driven equilibrium reasoning.

        This is the core market clearing routine. It:

        1. Extracts all investor orders from incoming messages
        2. Formats orders and market state into natural language
        3. Sends to LLM for equilibrium price computation
        4. Parses LLM's structured response
        5. Updates market state (price, volume, impacts)
        6. Computes diagnostics (realized volatility)
        7. Returns decision with market outcomes
        """
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # Extract orders from investors
        # ===================================================================
        # Extract orders from investors
        # ===================================================================
        investor_orders = []

        for msg in messages:
            investor_id = msg.investor_id
            decision_content = msg.decision_content

            # Debug output
            print(f"\n[DEBUG] Message from {investor_id}")
            print(f"[DEBUG] decision_content type: {type(decision_content)}")

            # Handle both object and dict
            if isinstance(decision_content, dict):
                print(f"[DEBUG] It's a dict")
                action_dict = decision_content['action']
            else:
                print(f"[DEBUG] It's an object")
                action_dict = decision_content.action

            print(f"[DEBUG] action_dict: {action_dict}")
            print(f"[DEBUG] action_dict type: {type(action_dict)}")

            # Iterate over markets
            for market_id, order in action_dict.items():
                print(f"[DEBUG] market_id: {market_id}")
                print(f"[DEBUG] order type: {type(order)}")
                print(f"[DEBUG] order value: {order}")

                # This is where it crashes - order is a string!
                investor_orders.append({
                    "investor": investor_id,
                    "order_type": order["order_type"],  # ← Line 225: crashes here
                    "shares": order["shares"],
                    "price": order["price"],
                })

        orders_text = "\n".join(
            [f"- {o['investor']}: {o['order_type']} {o['shares']:.2f} @ ${o['price']:.2f}" for o in investor_orders]
        )

        # Build prompt for the LLM
        market_state_text = f"""
        Market Name: {self.market_name}
        Current Price: ${self.price:.2f}
        Risk-Free Rate: {self.risk_free_rate:.2%}
        True Drift μ: {self.true_drift:.2%}
        True Volatility σ: {self.true_volatility:.2%}
        Supply Elasticity η: {self.supply_elasticity}
        Temporary Impact Coef: {self.temp_impact_coef}
        Permanent Impact Coef: {self.perm_impact_coef}
        """

        llm_input = (
            self.decision_prompt
            + "\n---\nIncoming Orders:\n"
            + orders_text
            + "\n---\nMarket Parameters:\n"
            + market_state_text
            + "\nPlease compute the new clearing price, total volume, excess demand, "
              "temporary and permanent price impact, and bid–ask spread.\n"
              "Respond in JSON format with the following keys:\n"
              "{clearing_price, total_volume, excess_demand, temp_impact, perm_impact, spread, reasoning}"
        )

        # Call the LLM
        messages = [
            {
                "role": "system",
                "content": "You are a market clearing engine. You MUST respond with valid JSON only. No markdown, "
                           "no explanations outside JSON, no code fences."
            },
            {"role": "user", "content": llm_input}
        ]

        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500
        )

        content = resp.choices[0].message.content.strip()

        # Parse LLM output
        result = json.loads(content)

        clearing_price = max(result.get("clearing_price", self.price_floor), self.price_floor)
        total_volume = result.get("total_volume", 0)
        excess_demand = result.get("excess_demand", 0)
        temp_impact = result.get("temp_impact", 0.0)
        perm_impact = result.get("perm_impact", 0.0)
        spread = result.get("spread", self.market_maker_spread)
        reasoning = result.get("reasoning", "LLM generated clearing summary.")

        # Update price
        self.price = clearing_price
        self.price_history.append(self.price)
        self.volume_history.append(total_volume)

        # Compute realized volatility (rolling window)
        if len(self.price_history) > 2:
            log_returns = np.diff(np.log(self.price_history[-10:]))
            realized_vol = np.std(log_returns) * np.sqrt(252)
        else:
            realized_vol = 0.0

        # Build structured decision
        decision = base.MarketDecision(
            clearing={"price": self.price, "volume": total_volume},
            reason=reasoning,
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
            additions={
                "excess_demand": excess_demand,
                "temporary_impact": temp_impact,
                "permanent_impact": perm_impact,
                "bid_ask_spread": spread,
                "realized_volatility": realized_vol,
            },
        )

        self._round_index += 1
        decision.ensure_valid()
        return decision
