---
name: interface-deploy
description: Local setup and run guide for MASIM Streamlit interface. Use when setting up the project for the first time.
version: 3.0.0
---

# interface-deploy — MASIM 界面本地运行指南

## 仓库

| 仓库 | 地址 | 说明 |
|------|------|------|
| lmbase | `https://github.com/AgenticFinLab/lmbase` | LLM 客户端，masim 硬依赖 |
| multiagent-simulation | `https://github.com/AgenticFinLab/multiagent-simulation` | 主项目（masim 包 + 界面） |

两个仓库均为 public，直接 clone 即可。

---

## 1 — 安装

```bash
git clone https://github.com/AgenticFinLab/lmbase.git
git clone https://github.com/AgenticFinLab/multiagent-simulation.git

# 先装 lmbase（masim 依赖它）
pip install ./lmbase

# 预装 torch CPU wheel（避免拉 2GB GPU 包；如已有 GPU 环境可跳过）
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# 装 masim
pip install ./multiagent-simulation
```

验证：

```bash
python -c "import masim, lmbase, ray, streamlit; print('OK')"
```

---

## 2 — 环境变量（可选，仅 LLM 引擎需要）

在 `multiagent-simulation/` 目录下创建 `.env`：

```
ARK_API_KEY_1=ark-xxx
ARK_API_KEY_2=ark-yyy
```

所有场景默认使用火山引擎（`ark/doubao-seed-2-0-mini-260428`），程序会自动从编号 key 中随机选取，分散限流压力。只有一个 key 时写 `ARK_API_KEY=ark-xxx` 即可。

Rule 引擎不需要 API Key，可跳过此步。

---

## 3 — 运行

```bash
cd multiagent-simulation
streamlit run masim/interface/app.py
```

浏览器自动打开 `http://localhost:8501`，即可使用。

---

## 常见问题

| 问题 | 修复 |
|------|------|
| `No module named 'lmbase'` | 先装 lmbase：`pip install ./lmbase` |
| torch 下载 2GB | 预装 CPU wheel：`pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu` |
| 拓扑图不显示 | 检查 `masim/interface/assets/d3.v7.min.js` 存在（已内置，无需外网） |
