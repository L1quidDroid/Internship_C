# Troubleshooting Index

## Overview

This index provides quick access to troubleshooting resources organised by problem category. Each section includes quick diagnostic commands and links to detailed troubleshooting guides.

## Quick Diagnosis Decision Tree

```
Server not responding?
├─ Port issue → [Service Start Failures](#service-start-failures)
├─ Resource exhaustion → [Performance Issues](#performance-issues)
└─ Configuration error → [Configuration Issues](#configuration-issues)

Agents not appearing?
├─ Network/firewall → [Agent Deployment Issues](#agent-deployment-issues)
├─ Wrong server address → [Network and Connectivity](#network-and-connectivity)
└─ Contact mismatch → [Agent Deployment Issues](#agent-deployment-issues)

Operations stuck/failing?
├─ No matching abilities → [Operation Execution Issues](#operation-execution-issues)
├─ Privilege issues → [Operation Execution Issues](#operation-execution-issues)
└─ Resource constraints → [Performance Issues](#performance-issues)

ELK integration not working?
├─ Authentication failure → [ELK Integration Issues](#elk-integration-issues)
├─ Plugin not loaded → [ELK Integration Issues](#elk-integration-issues)
└─ Index pattern mismatch → [ELK Integration Issues](#elk-integration-issues)
```

## Installation Issues

### Symptoms

- Python import errors
- Missing dependencies
- Installation script failures
- Virtual environment issues

### Quick Diagnosis

```bash
# Check Python version (requires 3.9+)
python3 --version

# Verify dependencies
pip3 list

# Check virtual environment
which python3
echo $VIRTUAL_ENV
```

### Common Solutions

1. **Wrong Python version** - Install Python 3.9 or higher
2. **Missing packages** - Run `pip install -r requirements.txt`
3. **Virtual environment not activated** - Run `source venv/bin/activate`
4. **Permission errors** - Use `--user` flag or fix ownership

### Detailed Guide

[Installation Guide](../getting-started/installation.md)

## Deployment Issues

### Service Start Failures

**Symptoms:** Server won't start, port conflicts, immediate exits

**Quick Diagnosis:**

```bash
# Check if port 8888 is in use
sudo lsof -i :8888

# Check for running Caldera processes
ps aux | grep server.py

# Test port availability
nc -zv localhost 8888
```

**Quick Fixes:**

```bash
# Kill existing Caldera process
pkill -f "python.*server.py"

# Force kill if needed
pkill -9 -f "python.*server.py"

# Start server
python3 server.py --insecure
```

**See:** [Deployment Troubleshooting - Service Start Failures](../deployment/troubleshooting.md#service-start-failures)

### Elasticsearch Won't Start

**Symptoms:** `systemctl status elasticsearch` shows failed state

**Quick Diagnosis:**

```bash
# Check Elasticsearch logs
sudo journalctl -u elasticsearch -n 50

# Check disk space
df -h

# Verify configuration
sudo /usr/share/elasticsearch/bin/elasticsearch --version
```

**Quick Fixes:**

```bash
# Fix common ownership issues
sudo chown -R elasticsearch:elasticsearch /var/lib/elasticsearch
sudo chown -R elasticsearch:elasticsearch /var/log/elasticsearch

# Restart service
sudo systemctl restart elasticsearch

# Check status
sudo systemctl status elasticsearch
```

**See:** [Deployment Troubleshooting - Elasticsearch Won't Start](../deployment/troubleshooting.md#elasticsearch-wont-start)

### Kibana Won't Start

**Symptoms:** `systemctl status kibana` shows failed state

**Quick Diagnosis:**

```bash
# Check Kibana logs
sudo journalctl -u kibana -n 50

# Verify Elasticsearch is running
sudo systemctl status elasticsearch

# Check Kibana configuration
sudo grep elasticsearch.hosts /etc/kibana/kibana.yml
```

**Quick Fixes:**

```bash
# Ensure Elasticsearch is running first
sudo systemctl start elasticsearch
sleep 10

# Start Kibana
sudo systemctl start kibana

# Check status
sudo systemctl status kibana
```

**See:** [Deployment Troubleshooting - Kibana Won't Start](../deployment/troubleshooting.md#kibana-wont-start)

### Docker Deployment Issues

**Symptoms:** Container fails to start, network connectivity issues, volume mount problems

**Quick Diagnosis:**

```bash
# Check container logs
docker logs caldera

# Check container status
docker ps -a

# Inspect container
docker inspect caldera

# Check network
docker network inspect caldera_default
```

**Quick Fixes:**

```bash
# Rebuild container
docker-compose build --no-cache

# Restart containers
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs -f
```

**See:** [Deployment Troubleshooting - Docker Deployment Issues](../deployment/troubleshooting.md#docker-deployment-issues)

## Agent Deployment Issues

### Agent Not Appearing in UI

**Symptoms:** Agent deployed but not visible in Campaigns → Agents

**Quick Diagnosis:**

```bash
# Check Caldera logs for beacons
grep -i beacon logs/*.log | tail -20

# Check agent process on target (Windows)
tasklist | findstr sandcat

# Check agent process on target (Linux)
ps aux | grep sandcat

# Test connectivity from target to server
curl http://<SERVER_IP>:8888/api/v2/health
```

**Quick Fixes:**

1. **Open firewall on server:**
   ```bash
   sudo ufw allow 8888/tcp
   ```

2. **Verify server address in deployment command** - Use external IP, not localhost

3. **Check contact configuration:**
   ```yaml
   # conf/local.yml
   app.contact.http:
     - 0.0.0.0:8888  # Must be 0.0.0.0, not 127.0.0.1
   ```

**See:** [Deployment Troubleshooting - Agent Not Appearing](../deployment/troubleshooting.md#agent-not-appearing-in-ui)

### Agent Execution Fails

**Symptoms:** Operation stuck at 0%, abilities fail immediately

**Quick Diagnosis:**

```bash
# Check operation status
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID> | jq '.state'

# Check link status
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>/links | jq '.[].status'
```

**Quick Fixes:**

1. **Verify platform match** - Windows abilities require Windows agents
2. **Check privileges** - Redeploy agent with administrator/root access
3. **Disable antivirus temporarily** - Add Caldera to exclusions
4. **Use atomic planner** - Select atomic planner for sequential execution

**See:** [Deployment Troubleshooting - Agent Execution Fails](../deployment/troubleshooting.md#agent-execution-fails)

## Operation Execution Issues

### Operation Stuck at 0%

**Symptoms:** Operation starts but no progress, no abilities execute

**Quick Diagnosis:**

```bash
# Check operation state
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>

# Check available agents
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/agents

# Check operation links
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>/links
```

**Common Causes:**

1. **No matching abilities** - Agent platform doesn't match ability requirements
2. **No available agents** - Agents not active or in wrong group
3. **Privilege issues** - Abilities require elevated privileges
4. **Planner configuration** - Planner can't find eligible abilities

**Quick Fixes:**

- Verify agent platform matches adversary abilities
- Ensure agents belong to correct group (red/blue)
- Redeploy agents with elevated privileges
- Select appropriate planner (atomic for sequential)

**See:** [Operation Troubleshooting](../user-guide/operations.md#troubleshooting)

### Operation Performance Issues

**Symptoms:** Operations run slowly, high latency between commands

**Quick Diagnosis:**

```bash
# Check system resources
free -h
top

# Check network latency
ping <target-ip>

# Monitor I/O
iostat -x 1 5
```

**Quick Fixes:**

- Reduce concurrent operations to 2-3
- Use atomic planner for predictable execution
- Reduce jitter intervals if acceptable
- Check network connectivity between server and agents

**See:** [Deployment Troubleshooting - Performance Issues](../deployment/troubleshooting.md#performance-issues)

## ELK Integration Issues

### Orchestrator Not Tagging Events

**Symptoms:** Operations run but no logs appear in Elasticsearch

**Quick Diagnosis:**

```bash
# Check environment variables
echo "ELK_URL: $ELK_URL"
echo "ELK_USER: $ELK_USER"
echo "ELK_PASS: ${ELK_PASS:0:5}..."

# Check orchestrator status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

# Check Caldera logs
grep -i "orchestrator\|ELK" logs/*.log | tail -20

# Check fallback logs
ls -lh plugins/orchestrator/data/fallback_logs/
```

**Quick Fixes:**

1. **Set environment variables:**
   ```bash
   export ELK_URL="http://192.168.1.50:9200"
   export ELK_USER="elastic"
   export ELK_PASS="your-password"
   python3 server.py --insecure
   ```

2. **Enable orchestrator plugin:**
   ```yaml
   # conf/local.yml
   plugins:
     - orchestrator
   ```

3. **Test ELK connectivity:**
   ```bash
   curl -u "elastic:password" \
     "http://192.168.1.50:9200/_cluster/health"
   ```

**See:** [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md)

### Authentication Errors

**Symptoms:** `"elk.status": "error"` or `"401 Unauthorized"`

**Quick Diagnosis:**

```bash
# Test Elasticsearch credentials
curl -u "elastic:password" \
  "http://192.168.1.50:9200/_cluster/health"

# Check environment variables
cat .env.elk

# Verify API key (if using)
curl -H "Authorization: ApiKey base64-encoded-key" \
  "http://192.168.1.50:9200/"
```

**Quick Fixes:**

- Verify username and password are correct
- Check for typos or trailing spaces in credentials
- Regenerate API key in Kibana if expired
- Ensure Elasticsearch authentication is enabled

**See:** [Deployment Troubleshooting - Authentication Errors](../deployment/troubleshooting.md#authentication-errors)

### Index Pattern Mismatch

**Symptoms:** Tags sent but queries return no results

**Quick Diagnosis:**

```bash
# Check actual index names
curl -u elastic:password \
  "http://192.168.1.50:9200/_cat/indices?v" | grep -i log

# Query for purple team tags
curl -X GET "http://192.168.1.50:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"term": {"tags": "purple_team"}}, "size": 1}'
```

**Quick Fixes:**

1. **Update index pattern:**
   ```yaml
   # conf/local.yml
   plugins:
     orchestrator:
       elk_index: "winlogbeat-*"  # Match actual index
   ```

2. **Create missing index:**
   ```bash
   curl -u elastic:password -X PUT \
     "http://192.168.1.50:9200/purple-team-logs"
   ```

**See:** [Deployment Troubleshooting - Index Pattern Mismatch](../deployment/troubleshooting.md#index-pattern-mismatch)

### Event Handlers Not Firing

**Symptoms:** Operations complete but no tagging occurs

**Quick Diagnosis:**

```bash
# Check Caldera logs for event handlers
tail -100 logs/*.log | grep -i "event\|orchestrator"

# Monitor websocket events
curl http://localhost:8888/api/v2/operations/<OP_ID>

# Check plugin registration
grep "Orchestrator.*registered" logs/*.log
```

**Quick Fixes:**

- Verify orchestrator plugin loaded during startup
- Check websocket contact is running: `netstat -tulpn | grep 8080`
- Restart Caldera to re-register event handlers
- Review orchestrator logs for signature mismatch errors

**See:** [Orchestrator Troubleshooting - Event Handler Issues](../plugins/orchestrator-troubleshooting.md#issue-1-event-handler-signature-mismatch-fixed-in-this-commit)

## Performance Issues

### System Resource Exhaustion

**Symptoms:** Server unresponsive, operations fail, high memory usage

**Quick Diagnosis:**

```bash
# Check available memory
free -h

# Check CPU usage
top
htop

# Check disk space
df -h

# Monitor processes
ps aux --sort=-%mem | head -10
```

**Warning Thresholds:**

- Available memory < 1GB: Reduce concurrent operations
- Available memory < 500MB: Stop operations, restart server
- Disk usage > 90%: Clean logs and old results

**Quick Fixes:**

1. **Reduce concurrent operations** - Limit to 2-3 simultaneous operations

2. **Restart server:**
   ```bash
   ./scripts/tl-shutdown.sh
   sleep 10
   ./scripts/tl-startup.sh
   ```

3. **Clean old data:**
   ```bash
   rm -rf data/results/*
   sudo journalctl --vacuum-time=7d
   ```

4. **Add swap space:**
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

**See:** [Deployment Troubleshooting - System Resource Issues](../deployment/troubleshooting.md#system-resource-issues)

### High Memory Usage

**Symptoms:** Caldera consuming excessive memory

**Quick Diagnosis:**

```bash
# Check process memory
ps aux --sort=-%mem | head -10

# Monitor memory over time
watch -n 1 free -h

# Check for memory leaks
top -o %MEM
```

**Quick Fixes:**

- Restart server to clear memory
- Disable unused plugins
- Clear operation cache: `rm -rf data/results/*`
- Reduce concurrent operations

**See:** [Deployment Troubleshooting - High Memory Usage](../deployment/troubleshooting.md#high-memory-usage)

### Slow Operation Execution

**Symptoms:** Operations take longer than expected

**Quick Diagnosis:**

```bash
# Check system load
top
htop

# Check I/O wait
iostat -x 1 5

# Check network latency
ping <target-ip>
```

**Quick Fixes:**

- Reduce concurrent operations
- Use atomic planner for predictable execution
- Reduce jitter intervals
- Check network connectivity and latency

**See:** [Deployment Troubleshooting - Slow Operation Execution](../deployment/troubleshooting.md#slow-operation-execution)

## Network and Connectivity

### Cannot Access Web Interface Remotely

**Symptoms:** Caldera accessible on localhost but not from remote machines

**Quick Diagnosis:**

```bash
# Check listening address
netstat -tulpn | grep 8888

# Should show 0.0.0.0:8888, not 127.0.0.1:8888

# Check firewall
sudo ufw status
sudo iptables -L
```

**Quick Fixes:**

1. **Configure bind address:**
   ```yaml
   # conf/local.yml
   app.contact.http:
     - 0.0.0.0:8888  # Not 127.0.0.1
   ```

2. **Open firewall:**
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8888
   ```

3. **Cloud security groups** - Add inbound rule for port 8888

**See:** [Deployment Troubleshooting - Cannot Access Web Interface](../deployment/troubleshooting.md#cannot-access-web-interface-remotely)

### DNS Resolution Failures

**Symptoms:** "Name or service not known" errors

**Quick Diagnosis:**

```bash
# Test DNS resolution
nslookup elasticsearch
dig elasticsearch

# Check /etc/hosts
cat /etc/hosts

# Test with IP
ping 192.168.1.50
```

**Quick Fixes:**

1. **Add to hosts file:**
   ```bash
   sudo echo "192.168.1.50 elasticsearch" >> /etc/hosts
   ```

2. **Use IP addresses instead of hostnames:**
   ```bash
   export ELK_URL="http://192.168.1.50:9200"
   ```

**See:** [Deployment Troubleshooting - DNS Resolution Failures](../deployment/troubleshooting.md#dns-resolution-failures)

## Configuration Issues

### UI Shows "Loading..." Indefinitely

**Symptoms:** Web interface stuck on loading screen

**Quick Diagnosis:**

```bash
# Check browser console (F12) for errors

# Check Caldera logs
tail -f logs/*.log

# Test API connectivity
curl http://localhost:8888/api/v2/health
```

**Quick Fixes:**

1. **Clear browser cache** - Ctrl+Shift+Delete, clear cached files
2. **Hard reload** - Ctrl+Shift+R (Chrome/Edge) or Ctrl+F5 (Firefox)
3. **Rebuild UI:**
   ```bash
   cd plugins/magma
   npm install
   npm run build
   ```
4. **Check authentication** - Verify credentials in conf/local.yml

**See:** [Deployment Troubleshooting - UI Shows Loading](../deployment/troubleshooting.md#ui-shows-loading-indefinitely)

### API Endpoints Not Responding

**Symptoms:** API requests fail or timeout

**Quick Diagnosis:**

```bash
# Check if server is running
lsof -ti:8888

# Test API connectivity
curl -v http://localhost:8888/api/v2/health

# Check server logs
tail -50 logs/*.log | grep -i error
```

**Quick Fixes:**

1. **Start server:**
   ```bash
   ./scripts/tl-startup.sh
   ```

2. **Check firewall:**
   ```bash
   sudo ufw allow 8888/tcp
   ```

3. **Restart with debug logging:**
   ```bash
   pkill -f "python.*server.py"
   python3 server.py --insecure --log DEBUG
   ```

**See:** [Deployment Troubleshooting - API Endpoints Not Responding](../deployment/troubleshooting.md#api-endpoints-not-responding)

### Python Import Errors

**Symptoms:** "ModuleNotFoundError" or "ImportError" when starting server

**Quick Diagnosis:**

```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list

# Verify virtual environment
which python3
echo $VIRTUAL_ENV
```

**Quick Fixes:**

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip3 install -r requirements.txt --force-reinstall
   ```

3. **Create new virtual environment:**
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

**See:** [Deployment Troubleshooting - Python Import Errors](../deployment/troubleshooting.md#python-import-errors)

## Security Issues

### Authentication Failures

**Symptoms:** Cannot log in, 401 Unauthorized errors

**Quick Diagnosis:**

```bash
# Check credentials in configuration
grep -A 5 "users:" conf/local.yml

# Test API with key
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/health

# Check for session issues
# Clear browser cookies and retry
```

**Quick Fixes:**

- Verify username and password in conf/local.yml
- Clear browser cookies and cache
- Check API key configuration
- Restart server after changing credentials

**See:** [Configuration Guide](../getting-started/configuration.md#authentication-settings)

## Diagnostic Commands

### Complete Health Check

```bash
#!/bin/bash
echo "=== System Resources ==="
free -h
df -h

echo -e "\n=== Service Status ==="
systemctl is-active elasticsearch kibana logstash elastic-agent 2>/dev/null || echo "N/A"

echo -e "\n=== Network Connectivity ==="
nc -zv localhost 9200 2>&1 || echo "Elasticsearch not reachable"
nc -zv localhost 5601 2>&1 || echo "Kibana not reachable"
nc -zv localhost 8888 2>&1 || echo "Caldera not reachable"

echo -e "\n=== Caldera Status ==="
curl -s http://localhost:8888/api/v2/health | python3 -m json.tool 2>/dev/null || echo "Caldera API not responding"

echo -e "\n=== Orchestrator Status ==="
curl -s http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool 2>/dev/null || echo "Orchestrator not available"

echo -e "\n=== ELK Connection ==="
curl -s -u elastic:password http://192.168.1.50:9200/_cluster/health | python3 -m json.tool 2>/dev/null || echo "ELK not reachable"
```

### Environment Verification

```bash
#!/bin/bash
echo "=== Environment Variables ==="
echo "ELK_URL: ${ELK_URL:-NOT SET}"
echo "ELK_USER: ${ELK_USER:-NOT SET}"
echo "ELK_PASS: ${ELK_PASS:+CONFIGURED}"

echo -e "\n=== Python Environment ==="
which python3
python3 --version
pip3 --version

echo -e "\n=== Virtual Environment ==="
echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-NOT ACTIVATED}"

echo -e "\n=== Configuration Files ==="
ls -lh conf/local.yml .env.elk 2>/dev/null || echo "Config files missing"
```

## Getting Help

### Log Collection

Collect diagnostic information when reporting issues:

```bash
# Create diagnostic bundle
tar czf caldera-diagnostic.tar.gz \
  logs/*.log \
  conf/local.yml \
  /tmp/tl-startup.log \
  /tmp/tl-shutdown.log \
  plugins/orchestrator/data/fallback_logs/

# Sanitise sensitive data before sharing
```

### Information to Provide

When seeking help, include:

1. **Version Information:**
   ```bash
   git describe --tags
   python3 --version
   uname -a
   ```

2. **Error messages** from logs
3. **Steps to reproduce** the issue
4. **Recent configuration changes**
5. **System resource status** (memory, disk, CPU)

### Support Resources

- [FAQ](faq.md) - Frequently asked questions
- [Quick Reference](quick-reference.md) - Command and API cheat sheet
- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md)
- [Deployment Troubleshooting](../deployment/troubleshooting.md)
- [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md)

### Contact

- **Security vulnerabilities:** security@triskelelabs.com
- **GitHub Issues:** Report bugs and feature requests in the repository

## Prevention Checklist

Avoid common issues by following these practices:

- [ ] Always use startup scripts for consistent state
- [ ] Check status after startup with `./scripts/tl-status.sh`
- [ ] Monitor system resources regularly
- [ ] Keep 4GB+ RAM free for smooth operation
- [ ] Use graceful shutdown before VM reboot
- [ ] Update regularly with `git pull`
- [ ] Review logs for warnings
- [ ] Backup configuration files
- [ ] Test ELK connectivity before operations
- [ ] Document custom configuration changes
