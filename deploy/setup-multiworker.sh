#!/bin/bash
# ==============================================================================
# MASIM Multi-Worker Deployment Script
# Server: Huawei ECS 8 CPUs / 32G RAM
# Architecture: 4 Streamlit workers + Nginx load balancer + concurrency limit
# ==============================================================================
set -e

echo "=== MASIM Multi-Worker Deployment ==="
echo ""

# --- 1. Stop existing service ---
echo "[1/6] Stopping existing masim service..."
sudo systemctl stop masim 2>/dev/null || true
sudo systemctl disable masim 2>/dev/null || true

# --- 2. Install template service ---
echo "[2/6] Installing systemd template service..."
sudo cp /opt/masim/multiagent-simulation/deploy/masim@.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable 4 instances (ports 8502-8505)
sudo systemctl enable masim@8502 masim@8503 masim@8504 masim@8505

# --- 3. Install Nginx config ---
echo "[3/6] Installing Nginx configuration..."
sudo cp /opt/masim/multiagent-simulation/deploy/masim-nginx.conf /etc/nginx/sites-available/masim

# Remove old config if exists
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/masim 2>/dev/null || true
sudo ln -sf /etc/nginx/sites-available/masim /etc/nginx/sites-enabled/masim

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# --- 4. Start all instances ---
echo "[4/6] Starting 4 Streamlit workers..."
sudo systemctl start masim@8502
sudo systemctl start masim@8503
sudo systemctl start masim@8504
sudo systemctl start masim@8505

# --- 5. Verify ---
echo "[5/6] Verifying..."
sleep 3
for port in 8502 8503 8504 8505; do
    if sudo systemctl is-active --quiet masim@${port}; then
        echo "  ✓ masim@${port} is running"
    else
        echo "  ✗ masim@${port} FAILED"
        sudo systemctl status masim@${port} --no-pager -l | tail -5
    fi
done

echo ""
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/ | grep -q "200\|302"; then
    echo "  ✓ Nginx proxy is working (HTTP 200/302)"
else
    echo "  ⚠ Nginx not responding on port 80, check: sudo nginx -t"
fi

# --- 6. Summary ---
echo ""
echo "[6/6] Deployment complete!"
echo ""
echo "Architecture:"
echo "  Browser → Nginx:80 → ip_hash → 4 Streamlit workers (8502-8505)"
echo "  Max concurrent simulations: 2 (file-lock semaphore)"
echo ""
echo "Management commands:"
echo "  Status:      sudo systemctl status 'masim@*'"
echo "  Restart all: sudo systemctl restart masim@8502 masim@8503 masim@8504 masim@8505"
echo "  Logs:        sudo journalctl -u masim@8502 -f"
echo "  Stop all:    sudo systemctl stop masim@8502 masim@8503 masim@8504 masim@8505"
echo ""
echo "After git pull:"
echo "  sudo systemctl restart masim@8502 masim@8503 masim@8504 masim@8505"
