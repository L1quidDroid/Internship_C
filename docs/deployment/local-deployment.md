---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes deployment approaches used during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production deployment guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Local Deployment Guide

This guide covers deploying this internship project on a local Ubuntu VM or development environment for testing and portfolio demonstration purposes.

## Prerequisites

### System Requirements

- **Operating System:** Ubuntu Server or Debian-based distribution
- **Memory:** Minimum 4GB RAM available, 8GB recommended
- **Disk Space:** 50GB free for logs and data
- **Network:** Ports 8888, 8443, 9200, 5601 accessible
- **Python:** 3.8 or higher
- **Git:** Latest version

### Required Components

- Elasticsearch (external or local)
- Kibana (external or local)
- Logstash (external or local)
- Elastic Agent (external or local)

## Initial Setup

### Clone Repository

```bash
cd /home/tonyto
git clone <repository-url>
cd caldera
```

### Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Configure Caldera

Create local configuration file:

```bash
cp conf/default.yml conf/local.yml
```

Edit `conf/local.yml` to set:
- Admin credentials
- Enabled plugins (magma, sandcat, stockpile, atomic, orchestrator, branding, reporting)
- Contact methods (HTTP, websocket)
- Port bindings

### Configure ELK Credentials

Create environment variables file:

```bash
cat > .env.elk << 'EOF'
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='your-password-here'
EOF

chmod 600 .env.elk
```

**Security Note:** Never commit `.env.elk` to version control. This file is automatically gitignored.

### Initial Build

Run first-time setup to create database and plugin configurations:

```bash
python3 server.py --build
```

## Starting the Environment

### Automated Startup Script

The `tl-startup.sh` script orchestrates the complete startup sequence:

```bash
#!/bin/bash
# Triskele Labs Purple Team Environment Startup Script
# Starts ELK Stack → Caldera → Validates functionality

set -e

CALDERA_DIR="/home/tonyto/caldera"
VENV_PATH="${CALDERA_DIR}/.venv"
LOG_FILE="/tmp/tl-startup.log"

echo "[STARTUP] Triskele Labs Purple Team Environment Starting..." | tee -a "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Startup initiated" >> "$LOG_FILE"

# Step 1: Check VM resources
echo ""
echo "[CHECK] VM resources..."
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEM" -lt 4 ]; then
    echo "    Warning: Only ${AVAILABLE_MEM}GB RAM available (recommend 4GB+)"
else
    echo "   Memory available: ${AVAILABLE_MEM}GB"
fi

# Step 2: Start ELK Stack
echo ""
echo "[ELK] Starting ELK Stack..."

echo "  Starting Elasticsearch..."
sudo systemctl start elasticsearch
sleep 3

echo "  Starting Kibana..."
sudo systemctl start kibana

echo "  Starting Logstash..."
sudo systemctl start logstash

echo "  Starting Elastic Agent..."
sudo systemctl start elastic-agent

# Step 3: Wait for ELK ports
echo ""
echo "[VERIFY] ELK connectivity..."
# Wait for Elasticsearch (port 9200)
# Wait for Kibana (port 5601)

# Step 4: Update Caldera codebase
echo ""
echo "[UPDATE] Caldera from GitHub..."
cd "$CALDERA_DIR" || exit 1
git pull origin main

# Step 5: Activate virtual environment
echo ""
echo "[VENV] Python virtual environment..."
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "   OK Virtual environment activated: $VENV_PATH"
else
    echo "   Creating new virtual environment..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
fi

# Step 6: Install/upgrade dependencies
echo ""
echo "[DEPS] Installing Caldera dependencies..."
pip3 install -q -r requirements.txt --upgrade

# Step 7: Load ELK credentials
echo ""
echo "[AUTH] Loading ELK credentials..."
if [ -f "$CALDERA_DIR/.env.elk" ]; then
    source "$CALDERA_DIR/.env.elk"
    echo "   ELK credentials loaded"
else
    echo "    Warning: .env.elk not found, orchestrator may not connect to ELK"
fi

# Step 8: Start Caldera
echo ""
echo "[START] Caldera server..."
echo "  Command: python3 server.py --insecure --log INFO"
echo "  (Press Ctrl+C to stop)"
echo ""

echo "OK Starting Caldera on http://localhost:8888"
python3 server.py --insecure --log INFO
```

### Manual Startup

If you need to start components individually:

```bash
# Start ELK services
sudo systemctl start elasticsearch
sudo systemctl start kibana
sudo systemctl start logstash
sudo systemctl start elastic-agent

# Wait for services to initialise
sleep 10

# Verify Elasticsearch
curl localhost:9200/_cluster/health

# Start Caldera
cd /path/to/caldera
source .venv/bin/activate
source .env.elk
python3 server.py --insecure --log INFO
```

## Startup Process Details

### Resource Verification

The startup script checks available memory:

```bash
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEM" -lt 4 ]; then
    echo "Warning: Only ${AVAILABLE_MEM}GB RAM available"
fi
```

**Warning Thresholds:**
- Available < 1GB: Reduce concurrent operations
- Available < 500MB: Stop operations, restart server

### Service Health Checks

The script waits for critical ports with timeout:

```bash
wait_for_port() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    while ! nc -z localhost "$port" 2>/dev/null; do
        sleep 1
        ((attempt++))
        if [ $attempt -ge $max_attempts ]; then
            echo "   $name did not start (timeout)"
            return 1
        fi
    done
    echo "   OK $name is ready on port $port"
}
```

### Elasticsearch Cluster Health

After Elasticsearch starts, the script validates cluster status:

```bash
ES_HEALTH=$(curl -s localhost:9200/_cluster/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")

if [ "$ES_HEALTH" = "green" ] || [ "$ES_HEALTH" = "yellow" ]; then
    echo "   Elasticsearch cluster: $ES_HEALTH"
else
    echo "  Elasticsearch cluster unhealthy: $ES_HEALTH"
    exit 1
fi
```

**Note:** Yellow status is acceptable for single-node deployments.

### Automatic Updates

The startup script pulls the latest code from GitHub:

```bash
cd "$CALDERA_DIR" || exit 1
git pull origin main
```

To disable automatic updates, comment out this section in the script.

### Dependency Management

Python dependencies are automatically upgraded during startup:

```bash
pip3 install -q -r requirements.txt --upgrade
```

## Verifying Deployment

### System Health Check

Use the status script to verify all components:

```bash
../scripts/tl-status.sh
```

Expected output:

```
System Resources:
  Memory: 5.2G available / 8.0G total
  Disk: 42G available on /

ELK Stack Services:
  elasticsearch: running
  kibana: running
  logstash: running
  elastic-agent: running

Network Connectivity:
  Elasticsearch (port 9200): reachable
  Kibana (port 5601): reachable
  Caldera (port 8888): reachable

Elasticsearch Cluster:
  Cluster: purplePracCluster
  Status: yellow
  Nodes: 1

Caldera Server:
  Running (PID: 12345)
  Web interface: http://localhost:8888

All systems operational
```

### API Health Check

Test Caldera API connectivity:

```bash
curl -s http://localhost:8888/api/v2/health | jq
```

Expected response:

```json
{
  "status": "healthy",
  "plugins": ["magma", "sandcat", "stockpile", "atomic", "orchestrator", "branding", "reporting"]
}
```

### Orchestrator Plugin Status

Verify ELK integration:

```bash
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
```

Expected output:

```json
{
  "plugin": "orchestrator",
  "status": "running",
  "elk": {
    "status": "connected",
    "cluster_name": "purplePracCluster"
  }
}
```

## Stopping the Environment

### Graceful Shutdown Script

Use the shutdown script to stop all services in reverse order:

```bash
../scripts/tl-shutdown.sh
```

The script performs:

1. Stop Caldera server (SIGTERM, force kill if needed)
2. Stop Elastic Agent
3. Stop Logstash
4. Stop Kibana
5. Stop Elasticsearch (last to allow data flush)

### Manual Shutdown

Stop services individually:

```bash
# Stop Caldera
pkill -f "python.*server.py"

# Stop ELK services
sudo systemctl stop elastic-agent
sudo systemctl stop logstash
sudo systemctl stop kibana
sudo systemctl stop elasticsearch
```

## Daily Workflow

### Morning Startup

```bash
../scripts/tl-startup.sh
# Wait for "Starting Caldera on http://localhost:8888"
# Open browser to localhost:8888
```

### Check Health

```bash
../scripts/tl-status.sh
```

### Evening Shutdown

```bash
# Stop Caldera with Ctrl+C (if running in foreground)
# OR run full shutdown:
../scripts/tl-shutdown.sh
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8888
sudo lsof -i :8888

# Kill existing Caldera
pkill -f "python.*server.py"

# Restart
../scripts/tl-startup.sh
```

### Elasticsearch Won't Start

```bash
# Check logs
sudo journalctl -u elasticsearch -n 50

# Common fix: Out of disk space
df -h
# If / is >90% full, clean up:
sudo apt-get clean
sudo journalctl --vacuum-time=7d
```

### Memory Issues

```bash
# Check available memory
free -h

# If <2GB available, restart services:
../scripts/tl-shutdown.sh
sleep 10
../scripts/tl-startup.sh
```

### UI Shows "Loading..." Indefinitely

**Cause:** Vue router authentication loop

**Solution:**
- Clear browser cache
- Re-login to Caldera interface

### Agent Not Appearing

**Cause:** Firewall blocking port 8888

**Solution:**
- Open port in firewall rules
- Or use SSH tunnel for remote access

## Log Files

### Startup Logs

```bash
tail -f /tmp/tl-startup.log
```

### Shutdown Logs

```bash
tail -f /tmp/tl-shutdown.log
```

### Caldera Application Logs

```bash
tail -f logs/*.log
```

### Orchestrator Plugin Logs

```bash
grep -i orchestrator logs/*.log | tail -20
```

## Command Aliases

Add these aliases to `~/.bashrc` for quick access:

```bash
# Triskele Labs Purple Team aliases
alias tl-start='cd /home/tonyto/caldera && ../scripts/tl-startup.sh'
alias tl-stop='cd /home/tonyto/caldera && ../scripts/tl-shutdown.sh'
alias tl-check='cd /home/tonyto/caldera && ../scripts/tl-status.sh'
alias tl-logs='tail -f /tmp/tl-startup.log /tmp/tl-shutdown.log'

# Quick Caldera access
alias caldera='cd /home/tonyto/caldera'
```

Reload shell configuration:

```bash
source ~/.bashrc
```

Usage:

```bash
tl-start   # Start environment
tl-check   # Check status
tl-stop    # Shutdown
```

## Script Locations

Ensure scripts are in the Caldera root directory:

```
/home/tonyto/caldera/
├── tl-startup.sh      ← Full startup
├── tl-shutdown.sh     ← Graceful shutdown
├── tl-status.sh       ← Health check
├── .env.elk           ← ELK credentials (gitignored)
└── conf/
    └── local.yml      ← Caldera config (gitignored)
```

Make scripts executable:

```bash
chmod +x tl-startup.sh tl-shutdown.sh tl-status.sh
```

## Best Practices

1. **Always use startup script** - Ensures consistent state
2. **Check status after startup** - Run `tl-status.sh` to verify
3. **Graceful shutdown** - Use `tl-shutdown.sh` before VM reboot
4. **Monitor resources** - Keep 4GB+ RAM free for smooth operation
5. **Update regularly** - Git pull is automated in startup script
6. **Log review** - Check `/tmp/tl-startup.log` for issues

## Resource Optimisation

### Memory Allocation Strategy

The platform is designed for constrained environments:

```
┌──────────────────────────────────────────────┐
│        Memory Allocation Strategy            │
├──────────────────────────────────────────────┤
│  Caldera Core Server      │  ~1.5 GB         │
│  Plugin Overhead          │  ~0.5 GB         │
│  Active Operations        │  ~1.0 GB         │
│  System Reserve           │  ~1.0 GB         │
│  ELK Stack (External)     │  Offloaded       │
├──────────────────────────────────────────────┤
│  Available Headroom       │  ~3.7 GB         │
└──────────────────────────────────────────────┘
```

### Optimisation Techniques

- Disabled non-essential plugins (training, emu, access)
- Asynchronous operation processing via `aiohttp`
- Lazy-loading of ability definitions
- External SIEM integration (no local log storage)
- Limit concurrent operations to 2-3 for optimal performance

## Security Considerations

### Credentials Management

- `.env.elk` contains sensitive credentials - never commit to Git
- `conf/local.yml` contains admin passwords - never commit to Git
- Both files are automatically gitignored
- Credentials are environment-specific, not shared between systems
- For production, use ELK API keys instead of passwords

### File Permissions

Secure credential files:

```bash
chmod 600 .env.elk
chmod 600 conf/local.yml
```

### Network Security

- Run behind firewall or VPN for secure development environments
- Use `--insecure` flag only for development environments
- Configure HTTPS in production (ports 8443)
- Restrict access to management ports (9200, 5601)

## Next Steps

- [Docker Deployment](docker-deployment.md) - Container-based deployment
- [ELK Integration](elk-integration.md) - Configure SIEM tagging
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## See Also

- [Configuration Guide](../getting-started/configuration.md)
- [TL Scripts README](../guides/TL_SCRIPTS_README.md)
- [Purple Team User Guide](../PURPLE_TEAM_USER_GUIDE.md)
