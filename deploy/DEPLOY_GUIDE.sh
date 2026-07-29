#!/bin/bash
# ==============================================================================
# MASIM 完整部署流程 — 华为云 ECS (8 CPU / 32G RAM)
# ==============================================================================
# 架构:  Browser → Nginx:80 → Streamlit (8502)
# 限制:  最多 4 个并发用户 (Nginx limit_conn)
#        最多 4 个并行模拟 (文件锁信号量) — 每个人可同时跑自己的
# ==============================================================================
# 使用方式:
#   方式一: 直接作为脚本执行  →  bash deploy/DEPLOY_GUIDE.sh
#   方式二: 逐段复制粘贴到终端 (推荐首次部署时这样做，方便排查)
# ==============================================================================
set -e

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 0: 登录服务器 & 基础确认                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

# ssh root@<你的华为云公网IP>

echo "=========================================="
echo " Phase 0: 环境检查"
echo "=========================================="

# 确认项目目录存在
cd /opt/masim/multiagent-simulation
echo "✓ 工作目录: $(pwd)"

# 确认 Python 虚拟环境存在
if [ -f /opt/masim/venv/bin/python ]; then
    echo "✓ Python venv: $(/opt/masim/venv/bin/python --version)"
else
    echo "✗ 找不到 /opt/masim/venv/bin/python，请先创建虚拟环境"
    exit 1
fi

# 确认 Nginx 已安装
if command -v nginx &>/dev/null; then
    echo "✓ Nginx: $(nginx -v 2>&1)"
else
    echo "→ Nginx 未安装，正在安装..."
    sudo apt-get update -qq && sudo apt-get install -y nginx
fi

echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 1: 停止旧服务                                                          ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 1: 停止旧服务"
echo "=========================================="

# 停止旧的单实例 masim 服务（如果存在）
if systemctl is-active --quiet masim 2>/dev/null; then
    echo "→ 检测到旧服务 masim，正在停止..."
    sudo systemctl stop masim
    sudo systemctl disable masim
    echo "✓ 旧服务 masim 已停止并禁用"
else
    echo "→ 旧服务 masim 未在运行，跳过"
fi

# 停止可能存在的旧多实例（历史遗留）
for port in 8502 8503 8504 8505; do
    if systemctl is-active --quiet masim@${port} 2>/dev/null; then
        sudo systemctl stop masim@${port}
        echo "→ 已停止 masim@${port}"
    fi
done

echo "✓ 所有旧进程已清理"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 2: 拉取最新代码                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 2: 拉取最新代码"
echo "=========================================="

git pull origin main
echo ""

# 关键文件验证
echo "--- 验证关键文件 ---"
[ -f masim/interface/app.py ] && echo "  ✓ app.py" || echo "  ✗ app.py 缺失!"
[ -f masim/interface/components/online_badge.py ] && echo "  ✓ online_badge.py" || echo "  ✗ online_badge.py 缺失!"
[ -f deploy/masim-nginx.conf ] && echo "  ✓ masim-nginx.conf" || echo "  ✗ nginx配置缺失!"
[ -f deploy/masim@.service ] && echo "  ✓ masim@.service" || echo "  ✗ service文件缺失!"

echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 3: 安装 / 更新 Python 依赖                                             ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 3: Python 依赖"
echo "=========================================="

source /opt/masim/venv/bin/activate
pip install -r requirements.txt --quiet --no-warn-script-location
deactivate

echo "✓ Python 依赖已更新"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 4: 部署 systemd 服务 (1 个 Streamlit 实例)                             ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 4: 部署 systemd 服务"
echo "=========================================="

# 复制模板服务文件
sudo cp deploy/masim@.service /etc/systemd/system/
sudo systemctl daemon-reload

# 禁用多余的旧实例 (从多实例架构升级到单实例)
for port in 8503 8504 8505; do
    sudo systemctl disable masim@${port} 2>/dev/null || true
done

# 启用单实例
sudo systemctl enable masim@8502

echo "✓ systemd 模板已安装，masim@8502 已启用"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 5: 部署 Nginx 配置 (4人并发限制)                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 5: 部署 Nginx 配置"
echo "=========================================="

# 确保目录结构存在
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

# 检查 nginx.conf 是否 include sites-enabled
if grep -q "sites-enabled" /etc/nginx/nginx.conf; then
    echo "  ✓ nginx.conf 已包含 sites-enabled"
else
    echo "  → 添加 sites-enabled include..."
    sudo sed -i '/http {/a\    include /etc/nginx/sites-enabled/*;' /etc/nginx/nginx.conf 2>/dev/null || true
fi

# 部署配置文件
sudo cp deploy/masim-nginx.conf /etc/nginx/sites-available/masim

# 清理旧链接，建新链接
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/masim
sudo ln -sf /etc/nginx/sites-available/masim /etc/nginx/sites-enabled/masim

# 语法检测
echo "--- Nginx 配置测试 ---"
sudo nginx -t

echo "✓ Nginx 配置已部署"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 6: 写入环境变量 & 启动服务                                              ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 6: 启动服务"
echo "=========================================="

# 写入容量配置
sudo mkdir -p /opt/masim
cat <<EOF | sudo tee /opt/masim/masim.env > /dev/null
# MASIM 服务器容量配置 (8C/32G, 4 用户, 4 并发模拟)
MASIM_MAX_USERS=4
MASIM_MAX_CONCURRENT_SIMS=4
EOF
echo "✓ 环境变量已写入 /opt/masim/masim.env"

# 启动 Streamlit
sudo systemctl start masim@8502

# 重载 Nginx
sudo systemctl reload nginx

echo "✓ masim@8502 已启动"
echo "✓ Nginx 已重载"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 7: 全面验证                                                            ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " Phase 7: 全面验证"
echo "=========================================="

# 等待 Streamlit 启动完成
echo "→ 等待 5 秒让 Streamlit 完全启动..."
sleep 5

# 7.1 systemd 状态
echo ""
echo "--- 7.1 Systemd 服务状态 ---"
ALL_OK=true
if systemctl is-active --quiet masim@8502; then
    echo "  ✓ masim@8502 — 运行中"
else
    echo "  ✗ masim@8502 — 失败!"
    echo "    最近日志:"
    journalctl -u masim@8502 --no-pager -n 5 | sed 's/^/    /'
    ALL_OK=false
fi

# 7.2 端口直连
echo ""
echo "--- 7.2 端口直连测试 ---"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://127.0.0.1:8502/_stcore/health 2>/dev/null || echo "000")
if [ "$code" = "200" ]; then
    echo "  ✓ 127.0.0.1:8502 → HTTP ${code}"
else
    echo "  ✗ 127.0.0.1:8502 → HTTP ${code} (期望200)"
    ALL_OK=false
fi

# 7.3 Nginx 代理
echo ""
echo "--- 7.3 Nginx 反向代理测试 ---"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://127.0.0.1/ 2>/dev/null || echo "000")
if [ "$code" = "200" ] || [ "$code" = "302" ]; then
    echo "  ✓ Nginx → backend: HTTP ${code}"
else
    echo "  ✗ Nginx → backend: HTTP ${code} (期望 200 或 302)"
    ALL_OK=false
fi

# 7.4 并发限制确认
echo ""
echo "--- 7.4 并发限制配置确认 ---"
grep "limit_conn masim_total" /etc/nginx/sites-available/masim | sed 's/^/  /'
echo "  → 超过 4 个并发连接时，新访客将看到 503 页面"
grep "MASIM_MAX_CONCURRENT_SIMS" /opt/masim/masim.env | sed 's/^/  /'
echo "  → 4 个用户可同时各自跑一个模拟，互不排队"

# 7.5 防火墙 / 安全组提醒
echo ""
echo "--- 7.5 网络访问检查 ---"
if command -v ufw &>/dev/null; then
    sudo ufw status | grep -E "80|Anywhere" | head -3 | sed 's/^/  /'
fi
echo "  ⚠ 请确认华为云安全组已放行: TCP 入方向 80 端口"
echo ""

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║ Phase 8: 部署完成 — 总结                                                     ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

echo "=========================================="
echo " 部署完成!"
echo "=========================================="
echo ""
echo " 架构:"
echo "   Browser → Nginx:80 → Streamlit (8502)"
echo ""
echo " 限制:"
echo "   • 最多 4 个并发用户 (Nginx limit_conn)"
echo "   • 最多 4 个并行模拟 (文件锁 /tmp/masim_sim_slots/)"
echo "   • 单实例内存上限 28G (systemd MemoryMax)"
echo ""
echo " 访问地址:"
echo "   http://<公网IP>/"
echo ""
echo " ┌──────────────────────────────────────────────────────────────┐"
echo " │ 日常运维命令                                                   │"
echo " ├──────────────────────────────────────────────────────────────┤"
echo " │ 查看状态:   systemctl status masim@8502                       │"
echo " │ 查看日志:   journalctl -u masim@8502 -f                       │"
echo " │ 重启:       systemctl restart masim@8502                      │"
echo " │ 停止:       systemctl stop masim@8502                         │"
echo " │ 更新代码:   cd /opt/masim/multiagent-simulation && \\           │"
echo " │             git pull && systemctl restart masim@8502           │"
echo " │ 调整容量:   sudo bash deploy/set-max-users.sh <N>             │"
echo " │ Nginx重载:  nginx -t && systemctl reload nginx                │"
echo " └──────────────────────────────────────────────────────────────┘"
echo ""

if [ "$ALL_OK" = true ]; then
    echo " ✅ 所有检查通过! 现在可以通过浏览器访问了。"
else
    echo " ⚠️  部分检查未通过，请查看上面的错误信息排查。"
fi
