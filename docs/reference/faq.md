# Frequently Asked Questions

## Installation and Configuration

### How do I install the Triskele Labs Command Center?

Clone the repository, create a Python virtual environment, install dependencies, and configure the platform:

```bash
git clone https://github.com/triskele-labs/command-center.git
cd command-center
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp conf/default.yml conf/local.yml
```

See the [Installation Guide](../getting-started/installation.md) for complete instructions.

### What are the minimum system requirements?

- Python 3.9 or higher
- 4GB RAM minimum, 8GB recommended
- 2GB disk space for application and data
- Port 8888 available for web interface
- Linux, macOS, or Windows with WSL

### How do I change the default port from 8888?

Edit `conf/local.yml`:

```yaml
host: 0.0.0.0
port: 8889  # Change to desired port
```

Restart the server for changes to take effect.

### How do I change default passwords?

Edit `conf/local.yml`:

```yaml
users:
  admin:
    password: your-strong-password-here
  blue:
    password: your-strong-password-here
  red:
    password: your-strong-password-here
```

Use strong passwords with 16+ characters, mixed case, numbers, and symbols. Change passwords immediately after installation.

### Which plugins do I need for purple team operations?

The lean core configuration includes seven essential plugins:

- `magma` - Frontend UI
- `sandcat` - Agent implementation
- `stockpile` - Ability repository
- `atomic` - Atomic Red Team integration
- `orchestrator` - Workflow automation
- `branding` - UI customisation
- `reporting` - Report generation

Additional plugins like `debrief` and `debrief-elk-detections` provide enhanced analytics and ELK integration.

### How do I disable unused plugins?

Comment out unwanted plugins in `conf/local.yml`:

```yaml
plugins:
  - magma
  - sandcat
  - stockpile
  # - atomic  # Disabled
  # - emu     # Disabled
```

Restart the server to apply changes.

### Where are configuration files located?

- `conf/default.yml` - Default configuration (do not modify)
- `conf/local.yml` - Local overrides (create from default.yml)
- `.env.elk` - ELK integration credentials (optional)

Configuration hierarchy: defaults → local.yml → environment variables.

## Agent Deployment

### How do I deploy agents without RDP access?

Use the one-liner enrolment feature from the Agents page. Generate platform-specific commands and execute via:

- Remote PowerShell (WinRM) for Windows
- SSH for Linux/macOS
- RMM tools (ConnectWise, Datto, NinjaRMM)
- GPO startup scripts
- Configuration management tools (Ansible, Puppet, Chef)

See [Agent Deployment Guide](../user-guide/agents.md) for detailed instructions.

### Why don't my agents appear in the UI?

Common causes:

1. **Firewall blocking agent beacons** - Ensure port 8888 is open on both server and target systems
2. **Wrong server address** - Use external IP or hostname, not localhost or 127.0.0.1
3. **Agent process crashed** - Check target system logs and restart agent
4. **Contact method mismatch** - Verify HTTP contact is enabled in `conf/local.yml`

Check connectivity: `curl http://<SERVER_IP>:8888/api/v2/health`

### How long does it take for agents to appear?

Agents typically appear within 30-60 seconds of deployment. Default beacon interval is 60 seconds. Check the Agents page or query the API:

```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents
```

### Can I adjust agent beacon intervals?

Yes, modify sleep intervals after agent enrolment through the UI or API. Lower intervals increase responsiveness but generate more network traffic. Recommended range: 30-300 seconds.

### How do I remove or decommission agents?

Delete agents through the UI (Agents page) or via API:

```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/agents/<PAW>
```

Also terminate the agent process on the target system.

### What platforms are supported for agents?

Sandcat agent supports:

- Windows (x86, x64)
- Linux (x86, x64, ARM)
- macOS (Intel, Apple Silicon)

Platform is automatically detected during deployment.

## Operations

### How do I create and run an operation?

Navigate to Operations page, click "Create Operation", configure parameters (name, adversary, planner, group), and click "Start". Operations execute abilities sequentially or in parallel based on planner configuration.

See [Running Operations](../user-guide/operations.md) for details.

### What's the difference between planners?

- `atomic` - Sequential execution, abilities run one at a time
- `batch` - Parallel execution, multiple abilities run simultaneously
- `buckets` - Time-bucketed execution with jitter

Use `atomic` for predictable execution order. Use `batch` for faster completion in resource-sufficient environments.

### Why is my operation stuck at 0%?

Common causes:

1. **No matching abilities** - Verify agent platform matches ability requirements (Windows abilities need Windows agents)
2. **Privilege issues** - Some abilities require administrator/root access
3. **Antivirus blocking** - Add Caldera to antivirus exclusions
4. **No available agents** - Ensure agents are active and belong to the correct group

Check operation status via API:

```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/<OP_ID>
```

### How do I stop a running operation?

Use the UI "Stop" button or update operation state via API:

```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state": "paused"}' \
  http://localhost:8888/api/v2/operations/<OP_ID>
```

### How many concurrent operations can I run?

Recommended limit: 2-3 concurrent operations in constrained environments (4-8GB RAM). Monitor system resources and reduce concurrency if experiencing performance issues.

### Can operations run autonomously with learned facts?

Yes, enable autonomous mode in operation configuration. The planner uses learned facts to populate ability parameters automatically. Configure in `conf/local.yml`:

```yaml
operation:
  autonomous: true
```

### How do I schedule operations to run automatically?

Use the Orchestrator plugin to create automated workflows. Configure scheduled executions programmatically via the API or implement custom scheduling logic.

## ELK Integration

### How do I integrate with Elasticsearch?

Set environment variables before starting Caldera:

```bash
export ELK_URL="http://192.168.1.50:9200"
export ELK_USER="elastic"
export ELK_PASS="your-password-here"
export ELK_INDEX="winlogbeat-*"
```

Or configure in `conf/local.yml`:

```yaml
plugins:
  orchestrator:
    elk_url: "http://192.168.1.50:9200"
    elk_index: "winlogbeat-*"
```

See [ELK Integration Guide](../deployment/elk-integration.md) for complete setup.

### Why aren't my operations tagging SIEM events?

Common causes:

1. **Environment variables not set** - Ensure ELK_URL, ELK_USER, ELK_PASS are exported before starting Caldera
2. **Orchestrator plugin not loaded** - Verify orchestrator is listed in plugins configuration
3. **ELK authentication failure** - Test credentials manually with curl
4. **Index pattern mismatch** - Verify ELK_INDEX matches actual Elasticsearch indices

Check orchestrator status:

```bash
curl http://localhost:8888/plugin/orchestrator/status
```

See [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md) for diagnostic steps.

### What gets tagged in Elasticsearch?

The Orchestrator adds purple team metadata to matching events:

```json
{
  "purple": {
    "operation_id": "abc123...",
    "technique": "T1033",
    "techniques": ["T1033", "T1087.001"],
    "tactic": "discovery"
  },
  "tags": ["purple_team", "caldera", "purple_T1033"]
}
```

SOC analysts can filter alerts using `tags: purple_team` to auto-acknowledge purple team exercises.

### How do I verify tags are being written?

Query Elasticsearch for purple team tags:

```bash
curl -X GET "http://192.168.1.50:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": { "tags": "purple_team" }
    },
    "size": 10
  }'
```

### What happens if Elasticsearch is unavailable?

The Orchestrator implements a circuit breaker pattern. When ELK is unreachable, tags are written to fallback logs at:

```
plugins/orchestrator/data/fallback_logs/fallback_*.json
```

Tags can be replayed to Elasticsearch when connectivity is restored.

## Performance and Resources

### How much memory does Caldera require?

- Caldera Core: approximately 1.5GB
- Plugin Overhead: approximately 0.5GB
- Active Operations: approximately 1GB (variable)
- System Reserve: approximately 1GB
- Recommended Headroom: 3-4GB

Total recommended: 8GB RAM for smooth operation with multiple concurrent operations.

### What should I do if the server becomes unresponsive?

1. Check available memory: `free -h`
2. If available < 1GB, reduce concurrent operations
3. If available < 500MB, stop operations and restart server
4. Use graceful shutdown: `./scripts/tl-shutdown.sh`
5. Wait 10 seconds and restart: `./scripts/tl-startup.sh`

### How do I optimise performance in constrained environments?

- Disable unused plugins
- Limit concurrent operations to 2-3
- Use atomic planner for sequential execution
- Clear old operation results: `rm -rf data/results/*`
- Add swap space if memory is limited
- Offload ELK Stack to separate VM

### Why is operation execution slow?

Common causes:

1. **High network latency** - Check connectivity between Caldera and agents
2. **Resource constraints** - Monitor system load with `top` or `htop`
3. **Concurrent operations** - Reduce number of simultaneous operations
4. **Large jitter values** - Review jitter configuration in operation settings

Optimise by using atomic planner and reducing jitter intervals.

### How do I monitor system resources?

```bash
# Check memory
free -h

# Check CPU and process usage
top
htop

# Check disk usage
df -h

# Check I/O wait
iostat -x 1 5

# Monitor network
iftop
```

Use the status script: `./scripts/tl-status.sh`

## Network and Connectivity

### How do I access the web interface remotely?

Configure bind address in `conf/local.yml`:

```yaml
host: 0.0.0.0  # Listen on all interfaces (not 127.0.0.1)
port: 8888
```

Configure firewall to allow access:

```bash
# Allow specific IP range
sudo ufw allow from 192.168.1.0/24 to any port 8888

# Or allow all (not recommended for production)
sudo ufw allow 8888/tcp
```

For cloud deployments, configure security group inbound rules.

### Can I use SSL/TLS?

Yes, configure SSL in `conf/local.yml`:

```yaml
ssl_port: 8443
ssl_cert: /path/to/certificate.crt
ssl_key: /path/to/private.key
```

Or use a reverse proxy (nginx, Apache) for SSL termination.

### How do I test API connectivity?

```bash
# Health check
curl http://localhost:8888/api/v2/health

# With API key
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents

# Verbose output
curl -v http://localhost:8888/api/v2/health
```

### What ports need to be open?

- **8888** - HTTP web interface and API (default)
- **8443** - HTTPS (if SSL enabled)
- **8080** - WebSocket contact (if using websocket contact method)
- **7010** - TCP contact (if using TCP contact method)

Configure additional ports based on contact methods used.

## Reporting

### How do I generate reports?

Navigate to Operations page, select completed operation, click "Generate Report". Choose format (PDF, HTML, JSON) and configure options. Download report when generation completes.

Alternatively, use the API:

```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "pdf",
    "include_facts": true
  }' \
  http://localhost:8888/api/v2/reports \
  --output report.pdf
```

See [Reporting Guide](../user-guide/reporting.md) for details.

### Why is my PDF report empty?

Common causes:

1. **Operation has no executed links** - Ensure operation ran to completion
2. **Report generation failed** - Check Caldera logs for errors
3. **Missing dependencies** - Verify reporting plugin is loaded

Check operation status: `curl http://localhost:8888/api/v2/operations/<OP_ID>`

### Can I customise report branding?

Yes, the Branding plugin allows customisation of logos, colours, and styling. Configure branding assets in the plugin configuration and templates.

### What report formats are supported?

- **PDF** - Executive presentation format
- **HTML** - Web embedding and interactive viewing
- **JSON** - Data integration and programmatic processing

## Troubleshooting

### The UI shows "Loading..." indefinitely

Common causes:

1. **Browser cache issues** - Clear browser cache and hard reload (Ctrl+Shift+R)
2. **Authentication loop** - Clear cookies and re-login
3. **JavaScript errors** - Check browser console (F12) for errors
4. **Build issues** - Rebuild Magma plugin: `cd plugins/magma && npm install && npm run build`

### How do I enable debug logging?

Start server with debug flag:

```bash
python3 server.py --insecure --log DEBUG
```

Or configure in `conf/local.yml`:

```yaml
logging:
  level: DEBUG
```

Logs are written to `logs/*.log`. Monitor with: `tail -f logs/*.log`

### Where can I find error logs?

- Caldera logs: `logs/*.log`
- Elasticsearch logs: `/var/log/elasticsearch/`
- Kibana logs: `/var/log/kibana/`
- System logs: `sudo journalctl -u <service-name>`

Use grep to filter: `tail -100 logs/*.log | grep -i error`

### How do I report bugs or request features?

- GitHub Issues: Report bugs and feature requests in the repository
- Security vulnerabilities: Email security@triskelelabs.com
- General support: Consult documentation and community resources

Provide diagnostic information when reporting issues:

```bash
# Collect diagnostic bundle
tar czf diagnostic.tar.gz logs/*.log conf/local.yml
```

### The server won't start

Common causes:

1. **Port already in use** - Check with `sudo lsof -i :8888` and kill conflicting process
2. **Missing dependencies** - Reinstall: `pip install -r requirements.txt`
3. **Configuration errors** - Validate YAML syntax in conf/local.yml
4. **Permission issues** - Ensure user has write permissions to data/ and logs/

Check server logs for specific error messages.

### How do I perform a clean restart?

```bash
# Stop server
./scripts/tl-shutdown.sh

# Wait for graceful shutdown
sleep 10

# Clear cache (optional)
rm -rf data/results/*

# Restart
./scripts/tl-startup.sh

# Verify
./scripts/tl-status.sh
```

## Advanced Topics

### Can I extend Caldera with custom plugins?

Yes, Caldera supports custom plugin development. See [Plugin Development Guide](../development/plugin-development.md) for architecture patterns and implementation details.

### How do I integrate with other SIEM platforms?

The Orchestrator plugin provides the framework for SIEM integration. Extend the SIEM connector to support additional platforms by implementing custom tagging logic. Reference the ELK connector implementation as a template.

### Can I run Caldera in Docker?

Yes, Docker deployment is supported. See [Docker Deployment Guide](../deployment/docker-deployment.md) for container configuration and orchestration instructions.

### How do I backup and restore data?

Backup critical directories:

```bash
tar czf caldera-backup.tar.gz \
  conf/local.yml \
  data/abilities/ \
  data/adversaries/ \
  data/objectives/ \
  data/sources/
```

Restore by extracting to the same paths. Do not backup `data/results/` as it contains transient operation data.

### How do I upgrade to a new version?

```bash
# Backup configuration and data
tar czf backup.tar.gz conf/local.yml data/

# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart server
./scripts/tl-shutdown.sh
./scripts/tl-startup.sh
```

Review release notes for breaking changes or migration steps.

## See Also

- [Installation Guide](../getting-started/installation.md)
- [Configuration Reference](../getting-started/configuration.md)
- [Troubleshooting Index](troubleshooting.md)
- [Quick Reference](quick-reference.md)
- [Deployment Troubleshooting](../deployment/troubleshooting.md)
- [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md)
