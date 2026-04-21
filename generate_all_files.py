#!/usr/bin/env python3
"""Complete scenario file generator.

Generates ALL files for each scenario following the project structure:
- examples/{Scenario}/__init__.py
- examples/{Scenario}/{Variant}/__init__.py
- examples/{Scenario}/{Variant}/players.py  (Rule only for unique logic)
- examples/{Scenario}/{Variant}/run_*.py
- examples/{Scenario}/{Variant}/analysis.py
- examples/{Scenario}/{Variant}/explain.md
- examples/{Scenario}/{Variant}/analysis.md
- examples/{Scenario}/LLM/prompts.py
- configs/{Scenario}/{Variant}/simulation.yml
- configs/{Scenario}/{Variant}/players.yml
- configs/{Scenario}/{Variant}/topology.yml
- configs/{Scenario}/{Variant}/persona.yml

For LLM/RuleLLM/Rag: players.py and analysis.py import from Rule variant.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import scenario definitions
sys.path.insert(0, BASE_DIR)
from generate_scenarios import SCENARIOS


def to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    result = []
    for i, c in enumerate(name):
        if c.isupper() and i > 0:
            result.append("_")
        result.append(c.lower())
    return "".join(result)


def generate_package_init(name: str, info: dict) -> None:
    """Generate examples/{Scenario}/__init__.py"""
    content = f'''"""{name} Simulation Package

{info['phenomenon']}

Variants:
    Rule:       Deterministic rule-based agents
    LLM:        LLM-driven agent decisions
    RuleLLM:    Hybrid rules + LLM judgment
    Rag:        RAG-augmented with knowledge base
"""
'''
    path = f"{BASE_DIR}/examples/{name}/__init__.py"
    with open(path, "w") as f:
        f.write(content)


def generate_rule_players(name: str, info: dict) -> None:
    """Generate examples/{Scenario}/Rule/players.py with full agent logic."""
    name_lower = info["name_lower"]
    agents = info["agents"]
    market_params = info["market_params"]

    theory_lines = []
    for t in info["theories"]:
        theory_lines.append(f"- {t}")
    theory_block = "\n".join(theory_lines)

    agent_descriptions = []
    for agent_name, agent_info in agents.items():
        agent_descriptions.append(f"- {agent_name}: {agent_info['description']}")
    agent_block = "\n".join(agent_descriptions)

    market_methods = """    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "price" not in self.state.custom_state:
            self._initialize_market_state()
        
        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()
    
    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        
        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]
    
    def _extract_orders(self, observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append({
                    "agent_id": msg.get("from"),
                    "action": msg.get("action"),
                    "quantity": msg.get("quantity"),
                    "agent_type": msg.get("agent_type"),
                })
        return orders
    
    def _clear_market(self, orders: list) -> dict:
        import random
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        
        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell
        
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        
        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        
        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)
        
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5
        
        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }
    
    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])
    
    def _log_market_state(self) -> None:
        import logging
        logger = logging.getLogger("{name}")
        logger.debug(
            "Round %%d: price=%%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )
    
    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        
        from masim.player.base import Action
        return Action(outbounds=[market_update])"""

    investor_classes = []
    for agent_name, agent_info in agents.items():
        stability = agent_info["type"]
        params_str = agent_info["params"]

        investor_classes.append(
            f'''
class {agent_name}(GeneralPlayer):
    """
    {agent_info['description']}
    
    Theoretical Basis: {agent_info['theory']}
    Market Role: {stability}
    
    Parameters from config:
        {params_str}
    """
    
    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()
        
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")
    
    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        self.state.custom_state["price_history"] = []
    
    async def step(self):
        price = self.state.custom_state.get("price", {market_params['initial_price']})
        fundamental = self.state.custom_state.get("fundamental", {market_params['fundamental_value']})
        deviation = self.state.custom_state.get("deviation", 0.0)
        
        decision = self._make_decision(price, fundamental, deviation)
        
        from masim.player.base import Action
        order = {{
            "type": "order",
            "action": decision["action"],
            "quantity": decision["quantity"],
            "agent_type": "{stability}",
        }}
        return Action(outbounds=[order])
    
    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Implement {agent_name} strategy logic."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        
        action = "hold"
        quantity = 0
        
        # Strategy-specific logic should be implemented here
        # based on the theoretical model for this agent type
        
        return {{"action": action, "quantity": quantity}}'''
        )

    all_classes = "\n".join(investor_classes)
    all_names = ", ".join([f"{a}" for a in agents.keys()] + ["Market"])

    content = f'''"""{name} Rule-Based Simulation

{info['phenomenon']}

Theoretical Foundation:
{theory_block}

Key Dynamics:
{agent_block}

Parameters from config (see configs/{name}/Rule/players.yml):
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("{name}")


class Market(GeneralPlayer):
    """
    Market agent for {name} simulation.
    
    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε
    
    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion strength  
        - F: Fundamental value
        - ε: Random noise
    """
{market_methods}

{all_classes}


__all__ = [{", ".join([f'"{n}"' for n in ["Market"] + list(agents.keys())])}]
'''

    path = f"{BASE_DIR}/examples/{name}/Rule/players.py"
    with open(path, "w") as f:
        f.write(content)


def generate_rule_run(name: str, info: dict) -> None:
    """Generate Rule run script."""
    name_lower = info["name_lower"]

    content = f'''#!/usr/bin/env python
"""{name} Rule-Based Simulation Runner

{info['phenomenon']}

Usage:
    python examples/{name}/Rule/run_{name_lower}.py \\
        -c configs/{name}/Rule/simulation.yml
"""

import argparse
import asyncio

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


async def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run {name} Rule-Based Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/{name}/Rule/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\\n" + "=" * 70)
    print("{name} Simulation - Rule-Based Agents")
    print("=" * 70)
    print("Phenomenon: {info['phenomenon']}")
    print("Rounds:     %%s" %% config.setting["total_rounds"])
    print("=" * 70 + "\\n")
    
    simulator = GeneralSimulator(config)
    
    try:
        await simulator.setup()
        results = await simulator.run()
        print("\\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
'''

    path = f"{BASE_DIR}/examples/{name}/Rule/run_{name_lower}.py"
    with open(path, "w") as f:
        f.write(content)


def generate_rule_analysis(name: str, info: dict) -> None:
    """Generate Rule analysis script."""
    name_lower = info["name_lower"]

    content = f'''#!/usr/bin/env python
"""{name} Simulation Analysis

Analyze the {name} simulation results.

Usage:
    python examples/{name}/Rule/analysis.py \\
        -c configs/{name}/Rule/simulation.yml
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config


def load_simulation_data(config: dict) -> dict:
    """Load simulation data from experiment records."""
    record_path = config["setting"]["record_path"]
    data = {{"prices": [], "fundamentals": [], "volumes": []}}
    
    market_path = os.path.join(record_path, "market")
    if os.path.exists(market_path):
        for filename in sorted(os.listdir(market_path)):
            if filename.endswith(".json"):
                with open(os.path.join(market_path, filename), "r") as f:
                    record = json.load(f)
                    custom = record.get("custom_state", {{}})
                    data["prices"].append(custom.get("price", 0))
                    data["fundamentals"].append(custom.get("fundamental", 0))
    
    return data


def calculate_metrics(data: dict) -> dict:
    """Calculate simulation metrics."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    
    if len(prices) == 0:
        return {{}}
    
    returns = np.diff(prices) / prices[:-1]
    deviation = (prices - fundamentals) / fundamentals
    
    return {{
        "price_metrics": {{
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
            "max_drawdown_pct": float(np.min(returns) * 100) if len(returns) > 0 else 0,
        }},
        "deviation_metrics": {{
            "max_deviation_pct": float(np.max(np.abs(deviation)) * 100) if len(deviation) > 0 else 0,
            "mean_deviation_pct": float(np.mean(np.abs(deviation)) * 100) if len(deviation) > 0 else 0,
        }},
        "volatility": {{
            "annualized_pct": float(np.std(returns) * np.sqrt(252) * 100) if len(returns) > 0 else 0,
        }},
    }}


def create_visualizations(data: dict, output_path: str) -> None:
    """Create analysis plots."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    
    if len(prices) == 0:
        return
    
    rounds = np.arange(len(prices))
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("{name} Simulation Analysis", fontsize=14, fontweight="bold")
    
    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(rounds, fundamentals, label="Fundamental", color="blue", linestyle="--")
    axes[0, 0].set_title("Price vs Fundamental")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    if len(fundamentals) > 0 and fundamentals[0] > 0:
        deviation = (prices - fundamentals) / fundamentals * 100
        axes[0, 1].plot(rounds, deviation, color="purple")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].set_title("Price Deviation (%)")
        axes[0, 1].grid(True, alpha=0.3)
    
    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        axes[1, 0].plot(rounds[1:], returns, color="red", alpha=0.7)
        axes[1, 0].set_title("Returns (%)")
        axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].hist(returns if len(prices) > 1 else [0], bins=30, color="steelblue", alpha=0.7)
    axes[1, 1].set_title("Return Distribution")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "{name_lower}_analysis.png"), dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze {name} simulation results")
    parser.add_argument("-c", "--config", type=str, default="configs/{name}/Rule/simulation.yml")
    args = parser.parse_args()
    
    config = load_config(args.config)
    data = load_simulation_data(config)
    
    if not data["prices"]:
        print("No simulation data found. Run simulation first.")
        return
    
    metrics = calculate_metrics(data)
    
    analysis_path = os.path.join(config["setting"]["record_path"], "analysis")
    os.makedirs(analysis_path, exist_ok=True)
    
    create_visualizations(data, analysis_path)
    
    with open(os.path.join(analysis_path, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    
    print("Analysis complete. Results in:", analysis_path)


if __name__ == "__main__":
    main()
'''

    path = f"{BASE_DIR}/examples/{name}/Rule/analysis.py"
    with open(path, "w") as f:
        f.write(content)


def generate_variant_players(name: str, variant: str, info: dict) -> None:
    """Generate LLM/RuleLLM/Rag players.py that imports from Rule."""
    name_lower = info["name_lower"]
    agents = info["agents"]

    llm_classes = []
    for agent_name in agents:
        llm_classes.append(
            f'''class LLM{agent_name}(LLMInvestor):
    """LLM-driven {agent_name}."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "{to_snake(agent_name)}"'''
        )

    llm_classes_str = "\n\n".join(llm_classes)
    all_names = ["Market", "LLMInvestor"] + [f"LLM{a}" for a in agents]

    content = f'''"""{name} {variant} Simulation

{info['phenomenon']}

Design:
- Market: Rule-based (same as Rule variant)
- Investors: {"LLM-driven" if variant == "LLM" else "Hybrid rule+LLM" if variant == "RuleLLM" else "RAG-augmented LLM"} with personas from prompts.py
"""

import json
import logging
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_client import LLMClient

from examples.{name}.{variant}.prompts import format_user_prompt, get_prompt
from examples.{name}.Rule.players import Market

logger = logging.getLogger("{name}.{variant}")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven investors."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_client = None
        self.agent_type = ""
    
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()
        
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")
    
    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        
        llm_config = extras.get("llm", {{}})
        self.llm_client = LLMClient(
            model=llm_config.get("model", "doubao-pro-32k"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
        )
        self.agent_type = extras.get("agent_type", "")
    
    async def step(self):
        if not self.llm_client or not self.agent_type:
            return Action(outbounds=[])
        
        system_prompt = get_prompt(self.agent_type)
        if not system_prompt:
            return Action(outbounds=[])
        
        user_prompt = self._format_user_prompt()
        
        try:
            response = await self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500,
            )
            
            raw_decision = self._parse_decision(response)
            decision = self._validate_decision(raw_decision)
            self._update_portfolio(decision)
            
            order = {{
                "type": "order",
                "action": decision["action"],
                "quantity": decision["quantity"],
                "agent_type": self.agent_type,
            }}
            return Action(outbounds=[order])
        except Exception as e:
            logger.error("LLM call failed: %%s", e)
            return Action(outbounds=[])
    
    def _format_user_prompt(self) -> str:
        price = self.state.custom_state.get("price", 100.0)
        fundamental = self.state.custom_state.get("fundamental", 100.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state.get("cash", 0.0)
        position = self.state.custom_state.get("position", 0)
        round_num = self.state.custom_state.get("round", 0)
        
        return format_user_prompt(
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            round_num=round_num,
        )
    
    def _parse_decision(self, response: str) -> dict:
        try:
            start = response.find("<decision>")
            end = response.find("</decision>")
            if start != -1 and end != -1:
                json_str = response[start + 10:end].strip()
                return json.loads(json_str)
            start = response.find("{{")
            end = response.rfind("}}")
            if start != -1 and end != -1:
                return json.loads(response[start:end + 1])
        except json.JSONDecodeError:
            pass
        return {{"action": "hold", "quantity": 0}}
    
    def _validate_decision(self, decision: dict) -> dict:
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        
        valid_actions = ["buy", "sell", "hold", "market_making"]
        if action not in valid_actions:
            action = "hold"
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0
        quantity = max(0, min(quantity, 5000))
        
        if action == "buy":
            price = self.state.custom_state.get("price", 100.0)
            cash = self.state.custom_state.get("cash", 0.0)
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        
        if action == "sell":
            position = self.state.custom_state.get("position", 0)
            quantity = min(quantity, position)
        
        return {{"action": action, "quantity": quantity}}
    
    def _update_portfolio(self, decision: dict) -> None:
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        price = self.state.custom_state.get("price", 100.0)
        
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity


{llm_classes_str}


__all__ = [{", ".join([f'"{n}"' for n in all_names])}]
'''

    path = f"{BASE_DIR}/examples/{name}/{variant}/players.py"
    with open(path, "w") as f:
        f.write(content)


def generate_variant_analysis(name: str, variant: str, info: dict) -> None:
    """Generate thin analysis wrapper."""
    content = f'''#!/usr/bin/env python
"""{name} {variant} Simulation Analysis

Usage:
    python examples/{name}/{variant}/analysis.py \\
        -c configs/{name}/{variant}/simulation.yml
"""

from examples.{name}.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
'''

    path = f"{BASE_DIR}/examples/{name}/{variant}/analysis.py"
    with open(path, "w") as f:
        f.write(content)


def generate_variant_init(name: str, variant: str, info: dict) -> None:
    """Generate __init__.py for variant."""
    agents = info["agents"]

    if variant == "Rule":
        imports = ", ".join(["Market"] + list(agents.keys()))
    else:
        imports = ", ".join(["Market", "LLMInvestor"] + [f"LLM{a}" for a in agents])

    content = f'''"""{name} {variant} Variant"""

from examples.{name}.{variant}.players import {imports}

__all__ = [{", ".join([f'"{n}"' for n in imports.split(", ")])}]
'''

    path = f"{BASE_DIR}/examples/{name}/{variant}/__init__.py"
    with open(path, "w") as f:
        f.write(content)


def generate_variant_run(name: str, variant: str, info: dict) -> None:
    """Generate run script for variant."""
    name_lower = info["name_lower"]

    if variant == "Rule":
        import_block = """from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging"""
        run_title = "Rule-Based Agents"
    else:
        import_block = """import os

from dotenv import load_dotenv

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging"""
        dotenv_call = "    load_dotenv()\n"
        run_title = f"{variant} Agents"

    dotenv_call = "    load_dotenv()\n" if variant != "Rule" else ""

    content = f'''#!/usr/bin/env python
"""{name} {variant} Simulation Runner

{info['phenomenon']}

Usage:
    python examples/{name}/{variant}/run_{name_lower}_{variant.lower()}.py \\
        -c configs/{name}/{variant}/simulation.yml
"""

import argparse
import asyncio

{import_block}


async def main():
{dotenv_call}    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Run {name} {variant} Simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/{name}/{variant}/simulation.yml",
    )
    args = parser.parse_args()
    
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    
    print("\\n" + "=" * 70)
    print("{name} Simulation - {run_title}")
    print("=" * 70)
    print("Rounds:     %%s" %% config.setting["total_rounds"])
    print("=" * 70 + "\\n")
    
    simulator = GeneralSimulator(config)
    
    try:
        await simulator.setup()
        results = await simulator.run()
        print("\\n" + "=" * 70)
        print("Simulation Complete!")
        print("=" * 70)
    finally:
        await simulator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
'''

    if variant == "Rule":
        filename = f"run_{name_lower}.py"
    else:
        filename = f"run_{name_lower}_{variant.lower()}.py"

    path = f"{BASE_DIR}/examples/{name}/{variant}/{filename}"
    with open(path, "w") as f:
        f.write(content)


def generate_prompts(name: str, info: dict) -> None:
    """Generate prompts.py for LLM variant."""
    agents = info["agents"]

    prompts = {}
    for agent_name, agent_info in agents.items():
        snake_name = to_snake(agent_name)
        prompts[
            snake_name
        ] = f'''"""You are a {agent_info['description']} in financial markets.

CORE BELIEF: "{agent_info['theory']}"

YOUR PSYCHOLOGY:
You are a {agent_info['type']} market participant. {agent_info['description']}.
Your behavior is grounded in the theory: {agent_info['theory']}.

YOUR STRATEGY:
1. Monitor market conditions and your private signals
2. Apply your strategy logic based on your theoretical model
3. Make trading decisions consistent with your behavioral profile
4. Manage risk according to your parameters

HOW YOU INTERPRET MARKET DATA:
- Price rising: Assess based on your strategy
- Price falling: Assess based on your strategy
- Price near fundamental: Assess based on your strategy
- High volatility: Assess based on your risk parameters

RISK PROFILE: {agent_info['type']} participant with specific risk parameters.

CONSTRAINTS:
- Cannot spend more than available cash
- Cannot sell more shares than held
- Must act within your strategy framework

OUTPUT FORMAT:
<analysis>Your reasoning about current market conditions</analysis>
<decision>{{"action": "buy" or "sell" or "hold", "quantity": integer}}</decision>
"""'''

    prompts_dict_str = "{\n"
    for snake_name, prompt in prompts.items():
        prompts_dict_str += f'    "{snake_name}": """{prompt}""",\n\n'
    prompts_dict_str += "}\n"

    content = f'''"""{name} LLM Prompts

System prompts for LLM-driven agents in the {name} simulation.

CRITICAL: These prompts define INVESTOR PERSONALITY ONLY.
They do NOT mention the specific phenomenon being simulated.
"""

AGENT_PROMPTS = {prompts_dict_str}


def get_prompt(agent_type: str) -> str:
    """Get system prompt for agent type."""
    return AGENT_PROMPTS.get(agent_type, "")


def format_user_prompt(
    price: float,
    fundamental: float,
    deviation: float,
    cash: float,
    position: int,
    round_num: int,
) -> str:
    """Format user prompt with market and portfolio data."""
    portfolio_value = cash + position * price
    return f"""Current Market State (Round {{round_num}}):
- Current Price: ${{price:.2f}}
- Fundamental Value: ${{fundamental:.2f}}
- Price Deviation: {{deviation*100:+.2f}}%
- Your Cash: ${{cash:.2f}}
- Your Position: {{position}} shares
- Portfolio Value: ${{portfolio_value:.2f}}

Based on your trading strategy and current market conditions, what action do you take?

Provide your analysis and decision in the specified format."""
'''

    for variant in ["LLM", "RuleLLM", "Rag"]:
        path = f"{BASE_DIR}/examples/{name}/{variant}/prompts.py"
        with open(path, "w") as f:
            f.write(content)


def generate_config_simulation(name: str, variant: str, info: dict) -> None:
    """Generate simulation.yml config."""
    name_lower = info["name_lower"]

    llm_block = ""
    if variant in ["LLM", "RuleLLM", "Rag"]:
        llm_block = """
llm:
  model: "doubao-pro-32k"
  temperature: 0.3
  max_tokens: 500
  timeout: 30
"""

    msg_timeout = "5000" if variant == "Rule" else "30000"

    content = f"""# {name} {variant} Simulation Configuration
#
# {info['phenomenon']}
#
# Usage:
#   python examples/{name}/{variant}/run_{name_lower}{"_" + variant.lower() if variant != "Rule" else ""}.py \\
#       -c configs/{name}/{variant}/simulation.yml

setting:
  name: "{name}-{variant}"
  description: "{info['description']}"
  total_rounds: 200
  
  record_path: "EXPERIMENT/{name}/{variant}/records"
  storage_path: "EXPERIMENT/{name}/{variant}/communication"
  
  log_level: "INFO"
  log_to_file: true
  log_path: "EXPERIMENT/{name}/{variant}/logs"

environment:
  dotenv_path: ".env"
  workspace: "."
{llm_block}
ray:
  namespace: "{name_lower}_{variant.lower()}"
  ignore_reinit_error: true
  object_store_memory: 536870912
  num_cpus: 4

players: !include players.yml
topology: !include topology.yml

communication:
  storage_path: "EXPERIMENT/{name}/{variant}/communication"
  record_messages: true
  message_timeout_ms: {msg_timeout}
  max_retries: 3
"""

    path = f"{BASE_DIR}/configs/{name}/{variant}/simulation.yml"
    with open(path, "w") as f:
        f.write(content)


def generate_config_players(name: str, variant: str, info: dict) -> None:
    """Generate players.yml config."""
    agents = info["agents"]
    market_params = info["market_params"]
    name_lower = info["name_lower"]

    # Determine class names based on variant
    if variant == "Rule":
        market_class = f"examples.{name}.Rule.players:Market"
    else:
        market_class = f"examples.{name}.{variant}.players:Market"

    content = f"""# {name} {variant} Agent Configuration

market:
  name: "Market"
  class: "{market_class}"
  num_instances: 1
  config:
    identity: "market"
    role: coordinator
    extras:
      initial_price: {market_params['initial_price']}
      fundamental_value: {market_params['fundamental_value']}
      price_impact: {market_params['price_impact']}
      mean_reversion: {market_params['mean_reversion']}
      noise_std: {market_params['noise_std']}

"""

    for i, (agent_name, agent_info) in enumerate(agents.items()):
        snake_name = to_snake(agent_name)

        if variant == "Rule":
            agent_class = f"examples.{name}.Rule.players:{agent_name}"
        else:
            agent_class = f"examples.{name}.{variant}.players:LLM{agent_name}"

        num_instances = 2 if agent_info["type"] in ["destabilizing", "neutral"] else 1

        llm_extras = ""
        if variant in ["LLM", "RuleLLM", "Rag"]:
            llm_extras = (
                """
      agent_type: "%s"
      llm:
        model: "doubao-pro-32k"
"""
                % snake_name
            )

        initial_cash = 1000000
        initial_position = 0

        content += f"""{snake_name}_{i+1}:
  name: "{agent_name} {i+1}"
  class: "{agent_class}"
  num_instances: {num_instances}
  config:
    identity: "{snake_name}_{i+1}"
    role: player
    extras:
      initial_cash: {initial_cash}.00
      initial_position: {initial_position}{llm_extras}

"""

    path = f"{BASE_DIR}/configs/{name}/{variant}/players.yml"
    with open(path, "w") as f:
        f.write(content)


def generate_config_topology(name: str, variant: str, info: dict) -> None:
    """Generate topology.yml config."""
    agents = info["agents"]

    agent_identities = []
    for i, (agent_name, agent_info) in enumerate(agents.items()):
        snake_name = to_snake(agent_name)
        num = 2 if agent_info["type"] in ["destabilizing", "neutral"] else 1
        for j in range(1, num + 1):
            agent_identities.append(f"{snake_name}_{i+1}_{j}")

    investor_list = "\n".join([f"      - {aid}" for aid in agent_identities])
    order_connections = "\n".join(
        [
            f"  - from: {aid}\n    to: market\n    bidirectional: false\n    message_type: order"
            for aid in agent_identities
        ]
    )
    execution_list = "\n".join([f"    - {aid}" for aid in agent_identities])

    content = f"""# {name} {variant} Communication Topology

graph:
  type: star
  center: market

connections:
  - from: market
    to:
{investor_list}
    bidirectional: false
    message_type: market_update

{order_connections}

broadcast:
  enabled: true
  from: market
  to: all_players
  message_type: market_update

execution:
  order:
    - market
{execution_list}
"""

    path = f"{BASE_DIR}/configs/{name}/{variant}/topology.yml"
    with open(path, "w") as f:
        f.write(content)


def generate_config_persona(name: str, variant: str, info: dict) -> None:
    """Generate persona.yml config."""
    agents = info["agents"]

    content = f"""# {name} {variant} Persona Configuration

market:
  type: proxy
  checkpoint_dir: "EXPERIMENT/{name}/{variant}/records/market/checkpoints"
  record_path: "EXPERIMENT/{name}/{variant}/records/market"
  monitoring:
    record_path: "EXPERIMENT/{name}/{variant}/monitoring/market"

"""

    for i, (agent_name, agent_info) in enumerate(agents.items()):
        snake_name = to_snake(agent_name)
        num = 2 if agent_info["type"] in ["destabilizing", "neutral"] else 1
        for j in range(1, num + 1):
            aid = f"{snake_name}_{i+1}_{j}"
            content += f"""{aid}:
  type: player
  checkpoint_dir: "EXPERIMENT/{name}/{variant}/records/{aid}/checkpoints"
  record_path: "EXPERIMENT/{name}/{variant}/records/{aid}"
  monitoring:
    record_path: "EXPERIMENT/{name}/{variant}/monitoring/{aid}"

"""

    path = f"{BASE_DIR}/configs/{name}/{variant}/persona.yml"
    with open(path, "w") as f:
        f.write(content)


def generate_explain_md(name: str, info: dict) -> None:
    """Generate explain.md for Rule variant (shared across variants)."""
    theories_text = "\n".join([f"- {t}" for t in info["theories"]])
    agents_text = "\n"

    for agent_name, agent_info in info["agents"].items():
        agents_text += f"""### {agent_name}
**Theoretical Basis**: {agent_info['theory']}
**Market Role**: {agent_info['type']}
**Description**: {agent_info['description']}
**Parameters**: {agent_info['params']}

"""

    content = f"""# {name} Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | {info['phenomenon']} |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | {info['description']} |
| **Academic Value** | Understanding {info['phenomenon'].split('.')[0].lower()} through multi-agent simulation |

## Theoretical Foundation

{theories_text}

## Agent Descriptions
{agents_text}
## Usage

### Rule Variant
```bash
python examples/{name}/Rule/run_{info['name_lower']}.py \\
    -c configs/{name}/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/{name}/LLM/run_{info['name_lower']}_llm.py \\
    -c configs/{name}/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/{name}/RuleLLM/run_{info['name_lower']}_rulellm.py \\
    -c configs/{name}/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/{name}/Rag/run_{info['name_lower']}_rag.py \\
    -c configs/{name}/Rag/simulation.yml
```

## References

{theories_text}
"""

    path = f"{BASE_DIR}/examples/{name}/Rule/explain.md"
    with open(path, "w") as f:
        f.write(content)

    # Copy to other variants
    for variant in ["LLM", "RuleLLM", "Rag"]:
        with open(f"{BASE_DIR}/examples/{name}/{variant}/explain.md", "w") as f:
            f.write(content)

    # Also generate analysis.md
    analysis_content = f"""# {name} Analysis Guide

## Metrics

| Metric | Description | Expected Range |
|--------|-------------|----------------|
| Price deviation | Deviation from fundamental | Varies by scenario |
| Max drawdown | Largest peak-to-trough decline | Varies by scenario |
| Volatility | Annualized return volatility | Varies by scenario |

## Visualization Guide

1. **Price vs Fundamental**: Shows whether agents create mispricings
2. **Deviation Plot**: Magnitude and persistence of mispricings
3. **Return Distribution**: Should show fat tails for behavioral scenarios

## Troubleshooting

- **No phenomenon observed**: Adjust agent parameters
- **Too extreme**: Add more stabilizing agents or increase mean reversion
- **Too stable**: Increase destabilizing agent parameters

## References

{theories_text}
"""

    for variant in ["Rule", "LLM", "RuleLLM", "Rag"]:
        with open(f"{BASE_DIR}/examples/{name}/{variant}/analysis.md", "w") as f:
            f.write(analysis_content)


def generate_scenario(name: str, info: dict) -> int:
    """Generate all files for a single scenario. Returns file count."""
    count = 0

    # Package init
    generate_package_init(name, info)
    count += 1

    # Rule variant (full implementation)
    generate_rule_players(name, info)
    generate_rule_run(name, info)
    generate_rule_analysis(name, info)
    generate_variant_init(name, "Rule", info)
    count += 4

    # Other variants (thin wrappers)
    for variant in ["LLM", "RuleLLM", "Rag"]:
        generate_variant_players(name, variant, info)
        generate_variant_analysis(name, variant, info)
        generate_variant_run(name, variant, info)
        generate_variant_init(name, variant, info)
        count += 4

    # Prompts (shared across LLM/RuleLLM/Rag)
    generate_prompts(name, info)
    count += 3

    # Documentation
    generate_explain_md(name, info)
    count += 8  # explain.md + analysis.md for each variant

    # Config files
    for variant in ["Rule", "LLM", "RuleLLM", "Rag"]:
        generate_config_simulation(name, variant, info)
        generate_config_players(name, variant, info)
        generate_config_topology(name, variant, info)
        generate_config_persona(name, variant, info)
        count += 4

    return count


def main():
    """Generate all scenarios."""
    print("=" * 70)
    print("Complete Scenario File Generator")
    print("=" * 70)

    total_files = 0

    for name, info in SCENARIOS.items():
        print(f"\nGenerating: {name}")
        count = generate_scenario(name, info)
        total_files += count
        print(f"  Generated {count} files")

    print("\n" + "=" * 70)
    print(f"Total: {len(SCENARIOS)} scenarios, {total_files} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
