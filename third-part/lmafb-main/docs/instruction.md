# Multi-Agent Market Simulation - Quick Start Guide

## Prerequisites
- **3 Tencent Cloud servers** with SSH access
  - **Instance Type**: Standard S5 (SA2.LARGE8) or higher
    - 4 vCPU cores
    - 8 GiB memory
    - 2.5GHz/3.1GHz processor
  - **Operating System**: Ubuntu Server 24.04 LTS 64-bit
  - **Storage**: 50 GiB SSD (standard cloud disk)
- GitHub repository: `git@github.com:AgenticFinLab/lmafb.git`
- **SSH key authentication** (recommended) or GitHub Personal Access Token

## Recommended Server Configuration

### Production Configuration (Recommended)
- **Instance Type**: Standard S5 - S5.MEDIUM4 (新客专享)
- **Specs**: 
  - vCPU: 2 cores
  - Memory: 4 GiB
  - Processor: 2.5GHz/3.1GHz
  - Architecture: X86
- **Availability Zone**: Guangzhou Zone 6 (广州六区)
- **Operating System**: Ubuntu Server 24.04 LTS 64-bit
- **Storage**: 50 GiB SSD (standard cloud disk)
- **Cost**: ¥534/month per instance
- **Total Cost for 4 Nodes**: **¥2136/month**
  
### Configuration Notes
- **Minimum 3 nodes required**: 1 head node + 2 worker nodes
- **Network**: Internal network connectivity between nodes
- **Discount**: New customer discount (8.7折) applied
- **Instance Family**: Standard (标准型)

### Why This Configuration?
- ✅ Cost-effective for research workloads
- ✅ Sufficient memory for 3-5 investors + 2-3 markets
- ✅ Low latency within same availability zone (Guangzhou Zone 6)
- ⚠️ For full 8 investors + 8 markets, consider upgrading to 4C8G

---

## Setup (One-time)

### Step 0: Setup SSH Key for GitHub (Recommended Method)

**On each server (Head Node, Worker Node 1, Worker Node 2):**
```bash
# SSH to the server
ssh <username>@<node-ip>

# 1) Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
# Press Enter for all prompts (use default location and no passphrase)

# 2) Display and copy the public key
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output (starts with `ssh-ed25519 ...`)**

**Add to GitHub:**
1. Go to GitHub → Settings → SSH and GPG keys → New SSH key
2. Add keys from each server (name them for easy identification):
   - Title: `tencent-head` (for head node)
   - Title: `tencent-worker1` (for worker 1)
   - Title: `tencent-worker2` (for worker 2)
3. Paste the corresponding public key into each

**Verify SSH connection:**
```bash
# Test GitHub SSH connection
ssh -T git@github.com

# Expected output:
# Hi <your-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

---

### Step 1: Clone Repository

**On Head Node:**
```bash
# SSH to head node
ssh <username>@<head-node-ip>

# Clone project using SSH
cd ~
git clone git@github.com:AgenticFinLab/lmafb.git
cd lmafb

# Create virtual environment
python3 -m venv ray-venv
source ray-venv/bin/activate

# Install dependencies
pip install ray numpy pandas pyyaml python-dotenv torch
```

**Repeat on Worker Nodes (Worker 1 and Worker 2)**

---

### Step 2: Start Ray Cluster

**On Head Node:**
```bash
ray start --head --port=6379
```

**On Worker Node 1:**
```bash
ssh <username>@<worker1-ip>
ray start --address='<head-node-ip>:6379'
```

**On Worker Node 2:**
```bash
ssh <username>@<worker2-ip>
ray start --address='<head-node-ip>:6379'
```

---

## Running Simulation

Open **3 terminal windows**, run these commands **in order**:

### Terminal 1: Start Investors
```bash
ssh <username>@<any-node-ip>
cd ~/lmafb
source ~/ray-venv/bin/activate
PYTHONPATH=. python examples/Demo/run_investor.py -c examples/Demo/config.yml -b . -p demo_simulation
```
**⚠️ Keep this terminal running!**

### Terminal 2: Start Markets
```bash
ssh <username>@<any-node-ip>
cd ~/lmafb
source ~/ray-venv/bin/activate
PYTHONPATH=. python examples/Demo/run_market.py -c examples/Demo/config.yml -b . -p demo_simulation
```
**⚠️ Keep this terminal running!**

### Terminal 3: Run Simulator
```bash
ssh <username>@<any-node-ip>
cd ~/lmafb
source ~/ray-venv/bin/activate
PYTHONPATH=. python examples/Demo/run_simulator.py -c examples/Demo/config.yml -b . -p demo_simulation
```

---

## Expected Output

**Terminal 1:**
```
[INFO] 🏗️ Created an investor Demo::pension_fund_alpha
[INFO] 🚀 Launched #8 investors
[INFO] ✅ Holding process for detached actors. Press Ctrl+C to exit.
```

**Terminal 2:**
```
[INFO] 🏗️ Created a market Demo::equity_market
[INFO] 🚀 Launched #8 markets
[INFO] ✅ Holding process for detached actors. Press Ctrl+C to exit.
```

**Terminal 3:**
```
[INFO] 🚀 Starting simulation...
[INFO] 🚀 Starting round 1
[INFO] ✅ Completed simulation round 1
...
[INFO] ✅ Simulation completed successfully!
[INFO] 💾 Saved results to: ~/demo_results/demo_simulation_results.json
```

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Servers** | 3 nodes | 3 nodes |
| **vCPU** | 2 cores | 4 cores |
| **Memory** | 4 GiB | 8 GiB |
| **Storage** | 50 GiB SSD | 50 GiB SSD |
| **OS** | Ubuntu 20.04+ | Ubuntu 24.04 LTS |
| **Python** | 3.8+ | 3.10+ |
| **Network** | Standard | Standard |

### Estimated Costs (Tencent Cloud)
- **Minimum Setup** (2C4G × 3): ~¥366-400/month
- **Recommended Setup** (4C8G × 3): ~¥690-864/month
- **Note**: Prices shown include discount promotions

---

## Workflow Diagram
```
┌─────────────────────────────────────────────────┐
│              Execution Workflow                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Terminal 1                                  │
│     └─> Launch 8 Investor Actors                │
│         └─> Stay Running (Detached)             │
│                                                 │
│  2. Terminal 2                                  │
│     └─> Launch 8 Market Actors                  │
│         └─> Stay Running (Detached)             │
│                                                 │
│  3. Terminal 3                                  │
│     └─> Start Simulation Coordinator            │
│         └─> Connect to Actors                   │
│         └─> Run N Rounds                        │
│         └─> Save Results                        │
│         └─> Exit                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Quick Commands
```bash
# Update code from GitHub
cd ~/lmafb
git pull

# Stop Ray cluster
ray stop --force

# Check Ray cluster status
ray status

# View simulation results
cat ~/demo_results/demo_simulation_results.json

# Check system resources
free -h        # Memory usage
df -h          # Disk usage
htop           # CPU and process monitor
```

---

## Alternative: Using GitHub Token (If SSH not preferred)

### Generate Personal Access Token:
1. Go to GitHub: Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the generated token (save it securely!)

### Clone using Token:
```bash
# Clone with token
git clone https://<your-token>@github.com/AgenticFinLab/lmafb.git

# Or with username
git clone https://<your-username>:<your-token>@github.com/AgenticFinLab/lmafb.git

# Example:
git clone https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/AgenticFinLab/lmafb.git
```

### Store credentials:
```bash
# Save credentials to avoid re-entering token
git config --global credential.helper store
git pull  # Enter token once, it will be saved
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Permission denied (publickey)` | Verify SSH key added to GitHub: `ssh -T git@github.com` |
| `Host key verification failed` | Accept GitHub's fingerprint: `ssh-keyscan github.com >> ~/.ssh/known_hosts` |
| `ModuleNotFoundError: No module named 'llmgt'` | Ensure `PYTHONPATH=.` is set before python command |
| `Connection refused` to Ray | Restart Ray: `ray stop --force && ray start --head --port=6379` |
| `OutOfMemoryError` | Upgrade to 8GB instances or reduce actors in config files |
| `Actor not found` | Run terminals in correct order: 1→2→3 |
| `Permission denied` (file) | Check file permissions: `chmod -R 755 ~/lmafb` |

### Memory Issues
If experiencing OOM errors:
1. **Upgrade servers** to 4C8G configuration (¥288/month per node)
2. **Reduce actors**: Edit `investors.yml` (keep 3-4) and `markets.yml` (keep 2-3)
3. **Increase memory threshold**: `RAY_memory_usage_threshold=0.98 ray start --head`

---

## SSH Key Troubleshooting

**If SSH connection to GitHub fails:**
```bash
# Check if SSH agent is running
eval "$(ssh-agent -s)"

# Add your SSH key to the agent
ssh-add ~/.ssh/id_ed25519

# Test connection with verbose output
ssh -Tv git@github.com

# Verify key was added to GitHub
# Go to: https://github.com/settings/keys
# You should see your key listed there
```

**Check SSH key permissions:**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

---

## Configuration Placeholders

Before running, replace these placeholders:

| Placeholder | Description | Example |
|------------|-------------|---------|
| `<username>` | SSH username | `ubuntu`, `root` |
| `<head-node-ip>` | Head node IP address | `172.16.0.12` |
| `<worker1-ip>` | Worker node 1 IP | `172.16.0.11` |
| `<worker2-ip>` | Worker node 2 IP | `172.16.0.9` |
| `<node-ip>` | Any node IP address | Any of the above |
| `<any-node-ip>` | Node to run terminal on | Any cluster node |
| `your.email@example.com` | Your email for SSH key | `michael_yuyang@berkeley.edu` |

---

## Complete Setup Example

**Example workflow for a new server:**
```bash
# 1. SSH to server
ssh ubuntu@172.16.0.12

# 2. Generate SSH key
ssh-keygen -t ed25519 -C "michael_yuyang@berkeley.edu"
# Press Enter 3 times

# 3. Display public key
cat ~/.ssh/id_ed25519.pub
# Copy the output

# 4. Add to GitHub (in browser)
# GitHub → Settings → SSH keys → New SSH key → Paste → Save

# 5. Test connection
ssh -T git@github.com
# Should see: "successfully authenticated"

# 6. Clone repository
cd ~
git clone git@github.com:AgenticFinLab/lmafb.git
cd lmafb

# 7. Setup environment
python3 -m venv ray-venv
source ray-venv/bin/activate
pip install ray numpy pandas pyyaml python-dotenv torch

# 8. Start Ray (if head node)
ray start --head --port=6379

# Done! Ready to run simulation
```

---

*Project Lead: Yuyang Dai | Advisor: Prof. Sijia Chen*  
*Repository: AgenticFinLab/lmafb*  
*Last Updated: 2025-10-16*
