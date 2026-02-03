# Simulation Scenarios for Multi-Agent Collusion

This repository contains several market simulation scenarios where multiple agents (companies) participate in collusive behavior. Each scenario represents a different form of economic collusion, including price fixing, tacit collusion, price leadership, and more. The code leverages LangGraph agents and various market dynamics to simulate these behaviors.

## Available Scenarios
0. **Demo:**
   A short version that can run our framework successfully and help everyone to better understand our framework.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Demo/run_investor.py -c examples/Demo/config.yml -b Experiments -p demo_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Demo/run_market.py -c examples/Demo/config.yml -b Experiments -p demo_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Demo/run_simulator.py -c examples/Demo/config.yml -b Experiments -p demo_simulation
      ```
   

1. **Cartel Collusion:**
   Simulates a scenario where companies form a cartel and agree on a fixed price to avoid competition.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Cartel/run_investor.py -c examples/Collusion/Cartel/config.yml -b . -p cartel_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Cartel/run_market.py -c examples/Collusion/Cartel/config.yml -b . -p cartel_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Cartel/run_simulator.py -c examples/Collusion/Cartel/config.yml -b . -p cartel_simulation
      ```
   - Expectation: The agents will follow the cartel's price agreement, avoiding undercutting. The system tracks price stability and cartel behavior.
   
2. **Bid Rigging:**
   Models the behavior of companies manipulating the bidding process to ensure pre-determined winners.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Bid_Rigging/run_investor.py -c examples/Collusion/Bid_Rigging/config.yml -b . -p bid_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Bid_Rigging/run_market.py -c examples/Collusion/Bid_Rigging/config.yml -b . -p bid_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Bid_Rigging/run_simulator.py -c examples/Collusion/Bid_Rigging/config.yml -b . -p bid_simulation
      ```
   - Expectation: The agents will coordinate their bids to favor pre-agreed winners, while the system tracks the manipulated bidding process and evaluates deviations.
3. **Market Division:**
   Simulates firms dividing the market into segments and setting prices within their designated regions without competing with each other.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Market_Division/run_investor.py -c examples/Collusion/Market_Division/config.yml -b . -p division_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Market_Division/run_market.py -c examples/Collusion/Market_Division/config.yml -b . -p division_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Market_Division/run_simulator.py -c examples/Collusion/Market_Division/config.yml -b . -p division_simulation
      ```
   - Expectation: The agents will set prices in different market segments, avoiding overlap. The system tracks market share allocation and evaluates compliance with the division.
4. **Price Fixing:**
   Simulates collusive behavior where firms coordinate on a fixed price and penalize deviations from the agreed price.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Fixing/run_investor.py -c examples/Collusion/Price_Fixing/config.yml -b . -p fixing_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Fixing/run_market.py -c examples/Collusion/Price_Fixing/config.yml -b . -p fixing_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Fixing/run_simulator.py -c examples/Collusion/Price_Fixing/config.yml -b . -p fixing_simulation
      ```
   - Expectation: The agents will maintain the fixed price and penalize any deviations. The system monitors price stability and collusion breakdowns when deviations exceed the set thresholds.
5. **Price Leadership:**
   In this scenario, a dominant firm (leader) sets the price, and other firms (followers) adjust their prices accordingly.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Leadership/run_investor.py -c examples/Collusion/Price_Leadership/config.yml -b . -p leadership_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Leadership/run_market.py -c examples/Collusion/Price_Leadership/config.yml -b . -p leadership_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Price_Leadership/run_simulator.py -c examples/Collusion/Price_Leadership/config.yml -b . -p leadership_simulation
      ```
   - Expectation: The leader will set the price, and followers will adapt. The system evaluates how closely the followers align with the leader’s price and tracks market behavior.
6. **Parallel Conduct:**
   Simulates a situation where firms independently set prices based on market conditions, but their prices converge over time without explicit communication.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Parallel_Conduct/run_investor.py -c examples/Collusion/Parallel_Conduct/config.yml -b . -p parallel_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Parallel_Conduct/run_market.py -c examples/Collusion/Parallel_Conduct/config.yml -b . -p parallel_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Parallel_Conduct/run_simulator.py -c examples/Collusion/Parallel_Conduct/config.yml -b . -p parallel_simulation
      ```
   - Expectation: Firms independently make pricing decisions, but their prices tend to converge over time as they adjust to market signals and each other’s behavior.
7. **Tacit Collusion:**
   In this scenario, firms avoid aggressive competition and implicitly coordinate their pricing strategies based on observed market trends.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Tacit/run_investor.py -c examples/Collusion/Tacit/config.yml -b . -p tacit_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Tacit/run_market.py -c examples/Collusion/Tacit/config.yml -b . -p tacit_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Tacit/run_simulator.py -c examples/Collusion/Tacit/config.yml -b . -p tacit_simulation
      ```
   - Expectation: The agents will avoid price wars and implicitly coordinate by observing each other's pricing and market behavior. The system tracks price stability and collusion dynamics.
8. **Algorithmic Collusion:**
   Simulates algorithm-driven firms that adjust their prices using pricing algorithms, implicitly coordinating prices based on market data.
   - Running:
     -run_investor.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Algorithmic/run_investor.py -c examples/Collusion/Algorithmic/config.yml -b . -p algorithmic_simulation
      ```
     -run_market.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Algorithmic/run_market.py -c examples/Collusion/Algorithmic/config.yml -b . -p algorithmic_simulation
      ```
     -run_simulator.py
      ```bash
      PYTHONPATH=. python examples/Collusion/Algorithmic/run_simulator.py -c examples/Collusion/Algorithmic/config.yml -b . -p algorithmic_simulation
      ```
   - Expectation: Firms use algorithms to adjust their prices based on market data, implicitly coordinating their pricing decisions. The system tracks the effectiveness of algorithmic pricing coordination.



