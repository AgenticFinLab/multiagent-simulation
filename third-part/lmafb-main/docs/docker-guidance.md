# Docker Deployment Guide

This document provides a complete guide for deploying the LMAFB project using Docker and Ray distributed framework.

## Prerequisites

- Docker installed and running
- Sufficient system resources (minimum 8GB RAM recommended)
- Active network connection (for pulling images and cloning repository)

## Deployment Steps

### 1. Create Docker Network

```bash
docker network create ray-net 2>/dev/null || true
```

This creates a Docker network named `ray-net` for communication between Ray cluster nodes.

### 2. Start Ray Head Node

```bash
docker run -itd --name ray-head --hostname ray-head --network ray-net \
  -p 8265:8265 -p 10001-10020:10001-10020 \
  --shm-size=2g \
  rayproject/ray:latest-py312 \
  bash -lc 'ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 && tail -f /dev/null'
```

**Parameter explanation:**
- `--name ray-head`: Container name
- `--hostname ray-head`: Hostname
- `-p 8265:8265`: Ray Dashboard port mapping
- `-p 10001-10020:10001-10020`: Reserved port range
- `--shm-size=2g`: Shared memory size (Head node requires more memory)

### 3. Start Worker Nodes

**Worker 1:**
```bash
docker run -itd --name ray-w1 --hostname ray-w1 --network ray-net \
  --shm-size=1g \
  rayproject/ray:latest-py312 \
  bash -lc 'ray start --address="ray-head:6379" && tail -f /dev/null'
```

**Worker 2:**
```bash
docker run -itd --name ray-w2 --hostname ray-w2 --network ray-net \
  --shm-size=1g \
  rayproject/ray:latest-py312 \
  bash -lc 'ray start --address="ray-head:6379" && tail -f /dev/null'
```

### 4. Verify Ray Cluster

Run the following command to verify the cluster is working properly:

```bash
docker exec -it ray-head python - <<'PY'
import ray, os
ray.init(address="auto")

@ray.remote
def f(i): 
    return (os.uname().nodename, i*i)

print(ray.get([f.remote(i) for i in range(6)]))
PY
```

**Expected output:** You should see tasks distributed across different nodes (ray-head, ray-w1, ray-w2).

### 5. Clone Project Code

Clone the LMAFB project on all nodes:

```bash
# Head node
docker exec -it ray-head bash -lc "\
cd /home/ray && \
git clone -b reorganization https://YUYANG0915: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@github.com/AgenticFinLab/lmafb.git"

# Worker 1
docker exec -it ray-w1 bash -lc "\
cd /home/ray && \
git clone -b reorganization https://YUYANG0915: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@github.com/AgenticFinLab/lmafb.git"

# Worker 2
docker exec -it ray-w2 bash -lc "\
cd /home/ray && \
git clone -b reorganization https://YUYANG0915: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@github.com/AgenticFinLab/lmafb.git"
```

### 6. Verify Code Clone

```bash
docker exec -it ray-head bash -lc "cd /home/ray/lmafb && ls -la"
```

### 7. Install Dependencies

Install Python dependencies on all nodes:

```bash
# Head node
docker exec -it ray-head bash -lc "cd /home/ray/lmafb && pip install -r requirements.txt"

# Worker 1
docker exec -it ray-w1 bash -lc "cd /home/ray/lmafb && pip install -U pip && pip install -r requirements.txt || true"

# Worker 2
docker exec -it ray-w2 bash -lc "cd /home/ray/lmafb && pip install -U pip && pip install -r requirements.txt || true"
```

## Updating Code

### Method 1: Simple Pull (Recommended for clean repositories)

```bash
docker exec -it ray-head bash -lc "cd /home/ray/lmafb && git pull origin reorganization"
```

### Method 2: Force Update (Recommended when conflicts exist)

This method will **discard all local changes** and force sync with the remote repository:

**Update Head node:**
```bash
docker exec -it ray-head bash -lc "\
cd /home/ray/lmafb && \
git fetch origin reorganization && \
git checkout reorganization && \
git reset --hard origin/reorganization && \
git clean -fd"
```

**Update all Worker nodes:**
```bash
for c in ray-w1 ray-w2; do
  docker exec -it $c bash -lc "\
  cd /home/ray/lmafb && \
  git fetch origin reorganization && \
  git checkout reorganization && \
  git reset --hard origin/reorganization && \
  git clean -fd" || true
done
```

**Restart containers after update:**
```bash
docker restart ray-head ray-w1 ray-w2
```

> ⚠️ **Warning:** Force update will permanently delete all local modifications and untracked files. Make sure to backup any important changes before proceeding.

## Running the Simulation

### Launch Simulation Components

Start each component in the following order:

**1. Start Investor (on Worker 1):**
```bash
docker exec -it ray-w1 bash -lc "cd /home/ray/lmafb && PYTHONPATH=. python examples/Demo/run_investor.py -c examples/Demo/config.yaml -b . -p demo_simulation"
```

**2. Start Market (on Worker 2):**
```bash
docker exec -it ray-w2 bash -lc "cd /home/ray/lmafb && PYTHONPATH=. python examples/Demo/run_market.py -c examples/Demo/config.yaml -b . -p demo_simulation"
```

**3. Start Simulator (on Head node):**
```bash
docker exec -it ray-head bash -lc "cd /home/ray/lmafb && PYTHONPATH=. python examples/Demo/run_simulator.py -c examples/Demo/config.yaml -b . -p demo_simulation"
```

## Monitoring and Management

### Access Ray Dashboard

Open in browser: `http://localhost:8265`

The Dashboard provides:
- Cluster status
- Task execution status
- Resource usage
- Log information

### View Container Logs

```bash
# View Head node logs
docker logs ray-head

# View Worker node logs
docker logs ray-w1
docker logs ray-w2
```

### Enter Container

```bash
# Enter Head node
docker exec -it ray-head bash

# Enter Worker node
docker exec -it ray-w1 bash
docker exec -it ray-w2 bash
```

## Common Operations

### Stop Cluster

```bash
docker stop ray-head ray-w1 ray-w2
```

### Start Stopped Cluster

```bash
docker start ray-head ray-w1 ray-w2
```

### Restart Cluster

```bash
docker restart ray-head ray-w1 ray-w2
```

### Remove Cluster Completely

```bash
# Stop and remove all containers
docker rm -f ray-head ray-w1 ray-w2

# Remove network
docker network rm ray-net
```

### Force Remove Ray Cluster (Nuclear Option)

If containers are stuck or unresponsive:

```bash
# Force stop all Ray containers
docker kill ray-head ray-w1 ray-w2 2>/dev/null || true

# Force remove all Ray containers
docker rm -f ray-head ray-w1 ray-w2 2>/dev/null || true

# Remove network
docker network rm ray-net 2>/dev/null || true

# Clean up any orphaned volumes (optional)
docker volume prune -f
```

## Troubleshooting

### Issue: Worker Cannot Connect to Head Node

**Solution:**
1. Check network connection: `docker network inspect ray-net`
2. Confirm Head node is running: `docker ps | grep ray-head`
3. Check Ray service status: `docker exec -it ray-head ray status`

### Issue: Out of Memory

**Solution:**
- Increase `--shm-size` parameter value
- Reduce number of concurrent tasks
- Add more Worker nodes

### Issue: Dependency Installation Failed

**Solution:**
1. Check network connection
2. Update pip: `pip install -U pip`
3. Install failed packages individually: `pip install <package_name>`

### Issue: Git Conflicts or Stale Code

**Solution:**
Use the force update method described in the [Updating Code](#updating-code) section to reset the repository to match the remote branch exactly.

### Issue: Container Won't Stop or Remove

**Solution:**
```bash
# Force kill the container
docker kill <container_name>

# Force remove the container
docker rm -f <container_name>
```

## Configuration Details

### Port Mapping

| Port | Purpose |
|------|---------|
| 8265 | Ray Dashboard Web UI |
| 6379 | Ray GCS Server |
| 10001-10020 | Reserved ports (for distributed communication) |

### Resource Configuration

Adjust according to actual needs:
- `--shm-size`: Shared memory size (recommended: 2g for Head node, 1g for Worker nodes)
- CPU/Memory limits can be set via `--cpus` and `--memory` parameters

## Best Practices

1. **Production Deployment Recommendations:**
   - Use Docker Compose or Kubernetes for cluster management
   - Configure persistent storage volumes
   - Set up automatic restart policies
   - Use secret management tools to protect sensitive information

2. **Performance Optimization:**
   - Adjust Worker count based on workload
   - Monitor resource usage and scale dynamically
   - Utilize Ray's auto-scaling features

3. **Security Recommendations:**
   - Never hardcode credentials in code
   - Use private networks
   - Regularly update images and dependencies

4. **Code Update Strategy:**
   - Use simple `git pull` for routine updates
   - Use force update when dealing with conflicts or corrupt state
   - Always restart containers after significant code changes
   - Consider implementing a CI/CD pipeline for automated deployments

## Quick Reference Commands

```bash
# Setup cluster from scratch
docker network create ray-net 2>/dev/null || true
# ... (run head and worker containers)

# Force update all nodes
for c in ray-head ray-w1 ray-w2; do
  docker exec -it $c bash -lc "cd /home/ray/lmafb && git fetch origin reorganization && git checkout reorganization && git reset --hard origin/reorganization && git clean -fd" || true
done
docker restart ray-head ray-w1 ray-w2

# Complete teardown
docker rm -f ray-head ray-w1 ray-w2
docker network rm ray-net
```

## References

- [Ray Official Documentation](https://docs.ray.io/)
- [Docker Official Documentation](https://docs.docker.com/)
- [Git Official Documentation](https://git-scm.com/doc)
- LMAFB Project Repository: https://github.com/AgenticFinLab/lmafb

---

For questions or suggestions, please submit an Issue to the project repository.