# Triskele Labs Purple Team Environment Scripts

## Quick Start

```bash
# Start everything (ELK → Caldera)
./tl-startup.sh

# Check system status
./tl-status.sh

# Graceful shutdown (Caldera → ELK)
./tl-shutdown.sh
```

## Scripts Overview

### 🚀 `tl-startup.sh` - Full Environment Startup
Starts the complete purple team environment in the correct order:

1. **Resource Check** - Verifies 4GB+ RAM available
2. **ELK Stack** - Starts elasticsearch → kibana → logstash → elastic-agent
3. **Health Checks** - Waits for ports 9200, 5601, verifies cluster health
4. **Git Update** - Pulls latest code from GitHub
5. **Python Environment** - Activates .venv, installs dependencies
6. **Load Credentials** - Sources .env.elk for orchestrator
7. **Start Caldera** - Launches server on http://localhost:8888

**Usage:**
```bash
./tl-startup.sh
# Starts all services and runs Caldera in foreground
# Press Ctrl+C to stop Caldera (ELK keeps running)
```

**Features:**
- ✅ Automatic health checks with 30s timeout
- ✅ Cluster status validation (green/yellow acceptable)
- ✅ Dependency auto-upgrade
- ✅ Startup logged to `/tmp/tl-startup.log`

---

### 🛑 `tl-shutdown.sh` - Graceful Shutdown
Stops all services in reverse order to ensure data integrity:

1. **Caldera** - Stops server gracefully (SIGTERM), force kills if needed
2. **Elastic Agent** - Stops telemetry collection
3. **Logstash** - Stops log processing
4. **Kibana** - Stops visualization dashboard
5. **Elasticsearch** - Stops last to allow data flush

**Usage:**
```bash
./tl-shutdown.sh
# Stops all services cleanly
```

**Features:**
- ✅ Graceful shutdown with SIGTERM
- ✅ Force kill fallback if service hangs
- ✅ Verification of stopped state
- ✅ Shutdown logged to `/tmp/tl-shutdown.log`

---

### 📊 `tl-status.sh` - System Health Check
Displays comprehensive environment status:

- **System Resources** - RAM, disk space
- **Service Status** - elasticsearch, kibana, logstash, elastic-agent
- **Network Ports** - 9200, 5601, 8888 reachability
- **Cluster Health** - ES cluster name, status, node count
- **Caldera Process** - PID, web interface availability
- **Purple Logs** - Document count in purple-team-logs index

**Usage:**
```bash
./tl-status.sh
# Shows current state of all components
```

**Sample Output:**
```
📊 Triskele Labs Purple Team Environment Status

🖥️  System Resources:
  Memory: 5.2G available / 8.0G total
  Disk: 42G available on /

🔷 ELK Stack Services:
  ✅ elasticsearch: running
  ✅ kibana: running
  ✅ logstash: running
  ✅ elastic-agent: running

🌐 Network Connectivity:
  ✅ Elasticsearch (port 9200): reachable
  ✅ Kibana (port 5601): reachable
  ✅ Caldera (port 8888): reachable

💚 Elasticsearch Cluster:
  Cluster: purplePracCluster
  Status: yellow
  Nodes: 1

🎯 Caldera Server:
  ✅ Running (PID: 12345)
  ✅ Web interface: http://localhost:8888

📝 Purple Team Logs in ELK:
  Documents: 42

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All systems operational
```

---

## TL VM Setup (First Time)

### 1. Clone Repository
```bash
cd /home/tonyto
git clone <triskele-caldera-repo>
cd caldera
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### 3. Configure ELK Credentials
```bash
# Create .env.elk file
cat > .env.elk << 'EOF'
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='ms4FiYr-C1bx0F1=GFrM'
EOF

# Secure the file
chmod 600 .env.elk
```

### 4. Configure Caldera
```bash
# Copy example config
cp conf/default.yml conf/local.yml

# Edit conf/local.yml - set admin credentials, enable plugins
vim conf/local.yml
```

### 5. Initial Build
```bash
python3 server.py --build
# First-time setup, creates database and plugin configs
```

### 6. Test Startup
```bash
./tl-startup.sh
# Verify all services start successfully
```

---

## Daily Workflow

### Morning Startup
```bash
./tl-startup.sh
# Wait for "Starting Caldera on http://localhost:8888"
# Open browser to localhost:8888
```

### Check Health
```bash
# In another terminal
./tl-status.sh
```

### Run Operations
```bash
# Via Caldera GUI at http://localhost:8888
# 1. Deploy Sandcat agent
# 2. Create operation (e.g., T1078 - Valid Accounts)
# 3. Run operation
# 4. Check purple-team-logs in Kibana
```

### Verify Purple Team Tagging
```bash
# Query operation-level tags
curl "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_id:*&size=1&pretty"

# Query individual attack tags (new feature!)
curl "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.link_id:*&size=1&pretty"
```

### Evening Shutdown
```bash
# Stop Caldera with Ctrl+C (if running in foreground)
# OR run full shutdown:
./tl-shutdown.sh
```

---

## Troubleshooting

### Startup Fails - Port Already in Use
```bash
# Check what's using port 8888
sudo lsof -i :8888

# Kill existing Caldera
pkill -f "python.*server.py"

# Restart
./tl-startup.sh
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

### Orchestrator Not Tagging
```bash
# Check status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

# Look for:
# "elk": { "status": "connected" }  ← Should be connected

# If not connected, verify credentials:
echo $ELK_URL
echo $ELK_USER
echo $ELK_PASS

# Re-source if missing:
source .env.elk
```

### Memory Issues
```bash
# Check available memory
free -h

# If <2GB available, restart services:
./tl-shutdown.sh
sleep 10
./tl-startup.sh
```

---

## Alias Setup (Optional)

Add to `~/.bashrc` for quick access:

```bash
# Triskele Labs Purple Team aliases
alias tl-start='cd /home/tonyto/caldera && ./tl-startup.sh'
alias tl-stop='cd /home/tonyto/caldera && ./tl-shutdown.sh'
alias tl-check='cd /home/tonyto/caldera && ./tl-status.sh'
alias tl-logs='tail -f /tmp/tl-startup.log /tmp/tl-shutdown.log'

# Quick Caldera access
alias caldera='cd /home/tonyto/caldera'
```

Reload:
```bash
source ~/.bashrc
```

Now you can run:
```bash
tl-start   # Start environment
tl-check   # Check status
tl-stop    # Shutdown
```

---

## Script Locations

All scripts should be in Caldera root directory:
```
/home/tonyto/caldera/
├── tl-startup.sh      ← Full startup
├── tl-shutdown.sh     ← Graceful shutdown
├── tl-status.sh       ← Health check
├── .env.elk           ← ELK credentials (gitignored)
└── conf/
    └── local.yml      ← Caldera config (gitignored)
```

---

## Deployment from GitHub

```bash
# On TL VM
cd /home/tonyto/caldera
git pull origin main

# Ensure scripts are executable
chmod +x tl-startup.sh tl-shutdown.sh tl-status.sh

# Verify .env.elk exists (if not, create it)
[ -f .env.elk ] || cat > .env.elk << 'EOF'
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='ms4FiYr-C1bx0F1=GFrM'
EOF

# Start environment
./tl-startup.sh
```

---

## Best Practices

1. **Always use startup script** - Ensures consistent state
2. **Check status after startup** - Run `./tl-status.sh` to verify
3. **Graceful shutdown** - Use `./tl-shutdown.sh` before VM reboot
4. **Monitor resources** - Keep 4GB+ RAM free for smooth operation
5. **Update regularly** - `git pull` is automated in startup script
6. **Log review** - Check `/tmp/tl-startup.log` for issues

---

## Security Notes

- ⚠️ `.env.elk` contains credentials - **never commit to Git**
- ⚠️ `conf/local.yml` contains admin passwords - **never commit to Git**
- ✅ Both files are in `.gitignore`
- ✅ Credentials are VM-specific (not shared with dev laptop)
- ℹ️ For production, use ELK API keys instead of passwords
