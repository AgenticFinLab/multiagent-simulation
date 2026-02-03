
## Financial Behavior Research with LLMs

> This repository tracks the progress and findings of research into financial behavior using Large Language Models (LLMs). The repo, named `lmafb`, stands for 'LLMs in Agentic Finance Behavior'.


---

## 📂 Project Structure

```
lmafb/
│
├── docs/                    # Documentation, figures, and experiment notes
│
├── examples/                # Example implementations and experiments
│   ├── AlgorithmicBase/     # Classical algorithmic investor baselines (non-LLM)
│   ├── Collusion/           # Multi-agent collusion experiments (Cartel, Price Fixing, etc.)
│   ├── Demo/                # Simple simulation demos for testing
│   └── PromptBase/          # Prompt-based LLM investor framework (Rational, Behavioral, Learning, etc.)
│
└── llmgt/                   # Our basic framework
    ├── communication/       # The communication protocols
    ├── investor/            # The basic implementation logic of investors
    ├── market/              # The basic implementation logic of markets
    ├── proxy/               # The proxy to define how to transfer messages between investors and markets
    ├── ray_general/         # The final codes that can combine the logics above and let investors run in an async way
    └── utils/               # Some basic tools we use in this project
```

---

## 🚀 Core Features

* **Distributed Multi-Agent Simulation**
  Powered by Ray; supports hundreds of investors and market agents running in parallel.

* **LLM-Driven Financial Agents**
  Supports OpenAI, Qwen, and DeepSeek models through unified prompt-based configuration.

* **Modular Investor Architecture**
  Includes Rational, Behavioral, Learning, and Market-Reactive investors.

* **Market Dynamics Framework**
  Supports Walrasian auctions, GBM price models, and endogenous impact factors.

* **Unified Messages Protocol**
  Uses `InvestorDecision` ↔ `MarketDecision` schema for consistent inter-agent communication.

---




## ⚙️ Configuration Example

Each simulation is controlled via YAML configuration files.  
For security and flexibility, never hardcode API keys in YAML. Instead, use **environment variables**.

Below are two recommended approaches:

#### Local Development

1. **Store secrets in a `.env` file** (add to `.gitignore`):
   ```env
   # .env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   DEEPSEEK_API_KEY=sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
   QWEN_API_KEY=sk-5azzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
   ```

2. **Update your YAML config to omit the `api_key` field** (or use a placeholder):
   ```yaml
   conservative_investor:
     class: "examples.PromptBase.prompt_investor:LLMRationalInvestor"
     market: ["stock_market"]
     config:
       llm_api:
         provider: "openai"
         model: "gpt-4o"
         # api_key: <- OMIT THIS FIELD
   ```

3. **In your Python code**, load the key at runtime:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()  # Load .env at the very start of your app

   # Later, when initializing the LLM client:
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       raise ValueError("OPENAI_API_KEY not found in environment variables.")
   ```

> 📝 The `openai`, `anthropic`, and other SDKs automatically read `OPENAI_API_KEY` from the environment if not explicitly passed, so you may not even need to reference it in code.

#### Production Deployment

1. **Do NOT include `.env` in production images**. Instead, set environment variables externally.

2. **Keep the same YAML config** (without `api_key`):
   ```yaml
   conservative_investor:
     class: "examples.PromptBase.prompt_investor:LLMRationalInvestor"
     market: ["stock_market"]
     config:
       llm_api:
         provider: "openai"
         model: "gpt-4o"
         # api_key: <- still omitted
   ```

3. **Set secrets via environment at runtime**:

   - **Linux/macOS shell**:
     ```bash
     export OPENAI_API_KEY=sk-...
     python run_simulation.py
     ```

   - **Docker**:
     ```bash
     docker run -e OPENAI_API_KEY=sk-... your-image
     ```
     Or use an `env_file` (never commit this file!):
     ```bash
     docker run --env-file ./prod-secrets.env your-image
     ```

4. **Your Python code remains unchanged** — it still uses `os.getenv("OPENAI_API_KEY")`, which now reads from the system environment.

---


## 🌟 Here please explain the differences between Local Quick Start, Local Docker Mode, and Multi-server Mode

---


## 🧪 Local Quick Start

🌟 You can quickly try this project on your local computer. Please run the following commands in the **`root`** directory of the project.

#### 1.Activate Python Environment


You can set up the environment using either **`venv`** (Python's built-in virtual environment) or **`conda`**. Choose the method that best fits your workflow.



- **Using `venv`**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  
   # On Windows: .venv/Scripts/activate
   ```

- **Using `conda`**
   ```bash
   conda create -n lmafb python=3.11  # adjust Python version as needed
   conda activate lmafb
   ```



#### 2. Install the package in editable mode
   ```bash
   pip install -e .
   ```

   > 💡 **Note**: Using `pip install -e .` with conda is common when you're actively developing a package, as it installs your project in "editable" mode—changes to your code take effect immediately without reinstalling.
---

#### 3. Launch Ray cluster
```bash
ray start --head
```


If a Ray cluster is already running, stop it first before starting a new one to **avoid naming conflicts or port issues**
```bash
ray stop
ray stop --force
```



### 🔹 Example Workflows - Run Algorithmic Simulation


> 💡 **Tip:** Each simulation requires **three separate terminals**. Run one command per terminal (investor, market, simulator) in parallel, not sequentially in the same terminal.


**Steps & Commands:**

#### 1. Run rational simulation
```console
# Run Inverstor
python examples/AlgorithmBase/rational/run_investor.py -c examples/AlgorithmBase/rational/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/AlgorithmBase/rational/run_market.py -c examples/AlgorithmBase/rational/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/AlgorithmBase/rational/run_simulator.py -c examples/AlgorithmBase/rational/config.yml -b . -p algorithmic_simulation
```

#### 2. Run behavioral simulation
```console
# Run Inverstor
python examples/AlgorithmBase/behavior/run_investor.py -c examples/AlgorithmBase/behavior/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/AlgorithmBase/behavior/run_market.py -c examples/AlgorithmBase/behavior/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/AlgorithmBase/behavior/run_simulator.py -c examples/AlgorithmBase/behavior/config.yml -b . -p algorithmic_simulation
```

#### 3. Run info investor
```console
# Run Inverstor
python examples/AlgorithmBase/info/run_investor.py -c examples/AlgorithmBase/info/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/AlgorithmBase/info/run_market.py -c examples/AlgorithmBase/info/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/AlgorithmBase/info/run_simulator.py -c examples/AlgorithmBase/info/config.yml -b . -p algorithmic_simulation
```

#### 4. Run market_reactive simulation
```console
# Run Inverstor
python examples/AlgorithmBase/market_reactive/run_investor.py -c examples/AlgorithmBase/market_reactive/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/AlgorithmBase/market_reactive/run_market.py -c examples/AlgorithmBase/market_reactive/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/AlgorithmBase/market_reactive/run_simulator.py -c examples/AlgorithmBase/market_reactive/config.yml -b . -p algorithmic_simulation
```

### 🔹 Example Workflows -  Run Prompt-Based Simulation

**Steps & Commands:**

#### 1. Run rational simulation
```console
# Run Inverstor
python examples/PromptBase/rational/run_investor.py -c examples/PromptBase/rational/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/PromptBase/rational/run_market.py -c examples/PromptBase/rational/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/PromptBase/rational/run_simulator.py -c examples/PromptBase/rational/config.yml -b . -p algorithmic_simulation
```


#### 2. Run behavioral simulation
```console
# Run Inverstor
python examples/PromptBase/behavior/run_investor.py -c examples/PromptBase/behavior/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/PromptBase/behavior/run_market.py -c examples/PromptBase/behavior/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/PromptBase/behavior/run_simulator.py -c examples/PromptBase/behavior/config.yml -b . -p algorithmic_simulation
```


#### 3. Run info investor
```console
# Run Inverstor
python examples/PromptBase/info/run_investor.py -c examples/PromptBase/info/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/PromptBase/info/run_market.py -c examples/PromptBase/info/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/PromptBase/info/run_simulator.py -c examples/PromptBase/info/config.yml -b . -p algorithmic_simulation
```


#### 4. Run market_reactive simulation
```console
# Run Inverstor
python examples/PromptBase/market_reactive/run_investor.py -c examples/PromptBase/market_reactive/config.yml -b . -p algorithmic_simulation

# Run Market
python examples/PromptBase/market_reactive/run_market.py -c examples/PromptBase/market_reactive/config.yml -b . -p algorithmic_simulation

# Run Simulator
python examples/PromptBase/market_reactive/run_simulator.py -c examples/PromptBase/market_reactive/config.yml -b . -p algorithmic_simulation

```

---




## 🧪 Local Docker Mode

---



## 🧪 Multi-server Mode

---



## 📘 Documentation

See detailed docs in [docker-guidance](https://github.com/AgenticFinLab/lmafb/blob/main/docs/docker-guidance.md).

> ⚠️ If you want to run via servers, please choose Tencent servers, for details, please check: [instruction](https://github.com/AgenticFinLab/lmafb/blob/main/docs/instruction.md)

---
