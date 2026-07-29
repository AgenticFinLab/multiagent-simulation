#!/usr/bin/env bash
# ============================================================
# set-max-users.sh — 一键设置 MASIM 服务器容量 (单实例架构)
#
# 用法:
#   sudo bash deploy/set-max-users.sh <最大用户数> [最大并发模拟数]
#
# 示例:
#   sudo bash deploy/set-max-users.sh 4        # 4人，默认4个并发模拟
#   sudo bash deploy/set-max-users.sh 6 4      # 6人，4个并发模拟
#   sudo bash deploy/set-max-users.sh 8 4      # 8人，4个并发模拟
#
# 自动完成:
#   1. 生成 Nginx 配置（连接数上限 + 503 满载提示页）
#   2. 写入环境变量文件（Streamlit 读取的并发模拟上限 + 在线徽章分母）
#   3. Reload Nginx + 重启单实例 Streamlit (masim@8502)
#
# 说明:
#   - 单实例架构下无需 ip_hash，所有连接直达 8502。
#   - 默认并发模拟数 = 用户数 (每个人可以同时跑自己的模拟)。
#     可用第二个参数手动覆盖，例如 8 用户 / 4 模拟以节省资源。
# ============================================================

set -euo pipefail

# --- 参数检查 ---
if [ $# -lt 1 ] || ! [[ "$1" =~ ^[0-9]+$ ]] || [ "$1" -lt 1 ]; then
    echo "用法: sudo bash $0 <最大用户数> [最大并发模拟数]"
    echo ""
    echo "示例:"
    echo "  sudo bash $0 4        # 4人上限，默认4个并发模拟"
    echo "  sudo bash $0 6 4      # 6人上限，4个并发模拟"
    echo "  sudo bash $0 8 4      # 8人上限，4个并发模拟"
    exit 1
fi

MAX_USERS="$1"

# 默认并发模拟数 = 用户数 (每人可以同时开自己的)
DEFAULT_SIMS="$MAX_USERS"
MAX_SIMS="${2:-$DEFAULT_SIMS}"

# --- 权限检查 ---
if [ "$(id -u)" -ne 0 ]; then
    echo "错误: 需要 root 权限，请用 sudo 运行"
    exit 1
fi

# --- 路径 ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/masim-nginx.conf.template"
NGINX_CONF="/etc/nginx/sites-available/masim"
NGINX_ENABLED="/etc/nginx/sites-enabled/masim"
ENV_FILE="/opt/masim/masim.env"

# --- 1. 生成 Nginx 配置 ---
if [ ! -f "$TEMPLATE" ]; then
    echo "错误: 找不到模板文件 $TEMPLATE"
    exit 1
fi

sed "s/{{MAX_USERS}}/$MAX_USERS/g" "$TEMPLATE" > "$NGINX_CONF"

if [ ! -L "$NGINX_ENABLED" ]; then
    ln -sf "$NGINX_CONF" "$NGINX_ENABLED"
fi

echo "[1/3] Nginx 配置已生成 (最大 $MAX_USERS 连接)"

# --- 2. 写入环境变量文件 ---
cat > "$ENV_FILE" <<EOF
# MASIM 服务器容量配置
# 由 set-max-users.sh 自动生成，请勿手动编辑
MASIM_MAX_USERS=$MAX_USERS
MASIM_MAX_CONCURRENT_SIMS=$MAX_SIMS
EOF

echo "[2/3] 环境变量已写入 $ENV_FILE (并发模拟上限: $MAX_SIMS)"

# --- 3. 重载服务 ---
echo "[3/3] 重载服务..."

# Nginx
if nginx -t 2>&1; then
    systemctl reload nginx
    echo "      Nginx reload ✓"
else
    echo "❌ Nginx 配置测试失败，中止"
    exit 1
fi

# Streamlit 单实例 (需要重启才能读到新的环境变量)
if systemctl is-active --quiet "masim@8502"; then
    systemctl restart "masim@8502"
    echo "      Streamlit restart ✓ (masim@8502)"
else
    echo "      (masim@8502 未运行，跳过重启)"
fi

# --- 完成 ---
echo ""
echo "════════════════════════════════════════"
echo "  ✅ 设置完成"
echo "  最大并发用户:  $MAX_USERS"
echo "  最大并发模拟:  $MAX_SIMS"
echo "════════════════════════════════════════"
