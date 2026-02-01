# Configuration Reference

## Overview

This document provides comprehensive configuration guidance for the Triskele Labs Purple Team Environment. Configuration is managed through YAML files and environment variables.

## Configuration Files

### Primary Configuration

**File:** `conf/default.yml`

Default configuration shipped with the platform. Do not modify this file directly.

**File:** `conf/local.yml`

Local overrides for customisation. Create this file to override default settings:

```bash
cp conf/default.yml conf/local.yml
```

### Configuration Hierarchy

Settings are loaded in this order (later sources override earlier):

1. `conf/default.yml` - Defaults
2. `conf/local.yml` - Local overrides
3. Environment variables - Runtime overrides

## Core Server Configuration

### Network Settings

```yaml
host: 0.0.0.0                    # Bind address (0.0.0.0 for all interfaces)
port: 8888                       # HTTP port
ssl_port: 8443                   # HTTPS port (if using SSL)
ssl_cert: null                   # Path to SSL certificate
ssl_key: null                    # Path to SSL private key
```

**Production Recommendations:**
- Bind to specific interface for security
- Enable SSL/TLS for production deployments
- Use reverse proxy (nginx, Apache) for SSL termination

### Authentication Settings

```yaml
users:
  admin:
    password: admin              # Change this immediately
  blue:
    password: admin
  red:
    password: admin

api_key_red: ADMIN123           # API key for red team operations
api_key_blue: ADMIN123          # API key for blue team operations
```

**Security Best Practices:**
- Change all default passwords on first installation
- Use strong passwords (16+ characters, mixed case, numbers, symbols)
- Rotate API keys regularly
- Implement role-based access control

### Plugin Configuration

```yaml
plugins:
  - atomic                       # Atomic Red Team integration
  - branding                     # UI customisation
  - debrief                      # Operation analytics
  - debrief-elk-detections      # ELK detection correlation
  - magma                        # Frontend UI
  - orchestrator                 # Workflow automation
  - reporting                    # Report generation
  - sandcat                      # Agent implementation
  - stockpile                    # Ability repository
```

**Plugin Management:**
- Comment out plugins to disable (prefix with `#`)
- Plugin load order may affect functionality
- Some plugins have dependencies on others

### Operation Settings

```yaml
operation:
  planner: atomic                # Default planner
  jitter: 2/8                   # Delay between commands (min/max seconds)
  obfuscation: plain-text       # Default obfuscator
  autonomous: true              # Allow autonomous fact usage
```

**Jitter Configuration:**
- Format: `min/max` in seconds
- Example: `2/8` means random delay between 2-8 seconds
- Increase jitter to reduce detection likelihood
- Decrease jitter for faster operation execution

### Agent Configuration

```yaml
agents:
  implant_name: splunkd         # Process name for stealth
  bootstrap_abilities:          # Abilities to run on agent startup
    - privilege/escalation/ask
  deadman_abilities:            # Abilities to run on agent disconnect
    - utility/remove-splunkd
  watchdog: 0                   # Watchdog timer (0 = disabled)
  untrusted_timer: 90           # Mark agent untrusted after N seconds
  implant_command: ''           # Custom startup command
  contact_tcp_port: 7010        # TCP contact port
  contact_udp_port: 7011        # UDP contact port
  contact_http_port: 8888       # HTTP contact port
  contact_websocket_port: 7012  # WebSocket contact port
```

**Agent Stealth Configuration:**
- Change `implant_name` to blend with environment
- Common process names: `svchost`, `explorer`, `system`, `splunkd`
- Configure deadman abilities to clean up on disconnection

## Environment Variables

### ELK Stack Integration

Create `.env` file from template:

```bash
cp .env.example .env
```

**Elasticsearch Connection:**

```bash
# Connection URL (include protocol and port)
ELK_URL=http://192.168.1.50:9200

# Index pattern for purple team logs
ELK_INDEX=purple-team-logs
```

**Authentication (Choose One Method):**

Method 1: API Key (Recommended)

```bash
# Generate API key in Elasticsearch
ELK_API_KEY=your-base64-encoded-api-key-here
```

Generate API key using Elasticsearch API:

```bash
curl -X POST "http://localhost:9200/_security/api_key" \
  -H "Content-Type: application/json" \
  -u elastic:password \
  -d '{
    "name": "caldera-integration",
    "role_descriptors": {
      "caldera_writer": {
        "cluster": ["monitor"],
        "index": [{
          "names": ["purple-team-*"],
          "privileges": ["write", "create_index"]
        }]
      }
    }
  }'
```

Method 2: Basic Authentication

```bash
# Username and password
ELK_USER=elastic
ELK_PASS=your-elasticsearch-password
```

**TLS/SSL Configuration:**

```bash
# Enable/disable SSL verification
ELK_VERIFY_SSL=true

# Path to CA certificate (if using self-signed certs)
ELK_CA_CERT_PATH=/path/to/ca.crt
```

**Connection Tuning:**

```bash
# Connection timeout in seconds
ELK_CONNECTION_TIMEOUT=30

# Maximum retry attempts
ELK_MAX_RETRIES=3
```

### Caldera Server Overrides

```bash
# Override YAML configuration via environment
CALDERA_HOST=0.0.0.0
CALDERA_PORT=8888
```

### Debug Settings

```bash
# Enable verbose logging for plugins
ORCHESTRATOR_DEBUG=true
REPORTING_DEBUG=true
DEBRIEF_DEBUG=true
```

## Plugin-Specific Configuration

### Orchestrator Plugin

**File:** `plugins/orchestrator/conf/config.yml`

```yaml
orchestrator:
  enabled: true
  auto_tag_siem: true           # Automatically tag SIEM events
  circuit_breaker:
    enabled: true
    failure_threshold: 3        # Consecutive failures before circuit opens
    timeout: 60                 # Reset timeout in seconds
  event_handlers:
    operation_start: true       # Hook: operation start
    operation_finish: true      # Hook: operation finish
    link_execute: true          # Hook: command execution
```

### Reporting Plugin

**File:** `plugins/reporting/conf/config.yml`

```yaml
reporting:
  output_dir: /tmp/caldera/reports
  formats:
    - pdf
    - html
    - json
  pdf:
    include_cover_page: true
    include_toc: true
    include_facts: true
    include_screenshots: false
  performance:
    max_parallel_renders: 2
    timeout_seconds: 120
```

### Branding Plugin

**File:** `plugins/branding/conf/config.yml`

```yaml
branding:
  company_name: Triskele Labs
  logo_path: plugins/branding/static/img/logo.svg
  primary_color: '#10B981'      # Triskele Green
  secondary_color: '#059669'
  footer_text: 'Triskele Labs | Purple Team Operations'
  watermark: 'CONFIDENTIAL'
```

## Agent Configuration Files

### Agent Profiles

**File:** `conf/agents.yml`

```yaml
agents:
  - paw: 'auto-generated-uuid'
    host: 'hostname'
    username: 'current-user'
    architecture: 'x86_64'
    platform: 'windows'
    server: 'http://caldera-server:8888'
    group: 'red'
    location: 'C:\Users\Public\splunkd.exe'
    pid: 1234
    ppid: 5678
    executors:
      - cmd
      - psh
      - pwsh
    privilege: 'Elevated'
    exe_name: 'splunkd.exe'
    sleep_min: 3
    sleep_max: 3
    watchdog: 0
```

## Data Source Configuration

### Fact Sources

**Directory:** `data/sources/`

Example source definition:

```yaml
id: d1b490f0-f3e9-4f42-9c67-1f1e0a7f9c3a
name: Custom Facts
facts:
  - trait: host.ip.address
    value: 192.168.1.100
  - trait: domain.admin.user
    value: administrator
  - trait: file.sensitive.path
    value: 'C:\Users\Admin\Documents\passwords.txt'
```

## Ability Configuration

### Ability Definitions

**Directory:** `data/abilities/`

Example ability YAML:

```yaml
id: 90c2efaa-8205-480d-8bb6-61d90dbaf81c
name: System Information Discovery
description: Collect basic system information
tactic: discovery
technique:
  attack_id: T1082
  name: System Information Discovery
platforms:
  windows:
    psh:
      command: |
        Get-ComputerInfo | Select-Object -Property CsName,OsName,OsVersion
  linux:
    sh:
      command: |
        uname -a; cat /etc/os-release
  darwin:
    sh:
      command: |
        uname -a; sw_vers
```

## Adversary Configuration

### Adversary Profiles

**Directory:** `data/adversaries/`

Example adversary YAML:

```yaml
id: de07d389-9f6c-4f4d-b554-5c42e6e5f3c9
name: Network Discovery
description: Reconnaissance and discovery techniques
atomic_ordering:
  - 90c2efaa-8205-480d-8bb6-61d90dbaf81c  # System Information Discovery
  - c0da588f-79f0-4263-8998-7496b1a40596  # Network Configuration Discovery
  - 7e150503-88b7-4ca6-8a09-e7d3e9e97e3a  # Process Discovery
  - 3b5db901-2cb8-4df7-8043-c4628a6a5d5a  # File Discovery
objective: Perform network reconnaissance
tags:
  - discovery
  - reconnaissance
  - low-impact
```

## Performance Tuning

### Memory Optimisation

```yaml
# conf/local.yml
app.cache.size: 256              # Cache size in MB
app.operation.max_concurrent: 3  # Maximum concurrent operations
app.database.pool_size: 10       # Database connection pool size
```

### Network Optimisation

```yaml
# Agent communication tuning
agents:
  heartbeat_interval: 60         # Agent check-in interval (seconds)
  command_timeout: 120           # Command execution timeout (seconds)
  download_chunk_size: 1048576   # File download chunk size (bytes)
```

## Logging Configuration

### Log Levels

```yaml
logging:
  level: INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: logs/caldera.log
  max_bytes: 10485760           # 10MB
  backup_count: 5               # Keep 5 rotated logs
```

### Component-Specific Logging

```yaml
logging:
  components:
    app.service.data_svc: DEBUG
    app.service.planning_svc: INFO
    app.service.rest_svc: WARNING
```

## Backup and Restore

### Data Directories

Key directories to backup:

```
data/abilities/          # Custom abilities
data/adversaries/        # Adversary profiles
data/sources/            # Fact sources
data/results/            # Operation results
conf/local.yml           # Local configuration
.env                     # Environment variables
```

### Backup Script

```bash
#!/bin/bash
BACKUP_DIR="/backup/caldera-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

cp -r data/abilities $BACKUP_DIR/
cp -r data/adversaries $BACKUP_DIR/
cp -r data/sources $BACKUP_DIR/
cp -r data/results $BACKUP_DIR/
cp conf/local.yml $BACKUP_DIR/
cp .env $BACKUP_DIR/

tar -czf "$BACKUP_DIR.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR
```

## Troubleshooting Configuration Issues

### Validate YAML Syntax

```bash
# Check for YAML syntax errors
python3 -c "
import yaml
with open('conf/local.yml', 'r') as f:
    config = yaml.safe_load(f)
    print('Configuration valid')
"
```

### View Active Configuration

```bash
# Query active configuration via API
curl http://localhost:8888/api/v2/config | jq
```

### Reset to Defaults

```bash
# Remove local overrides
rm conf/local.yml

# Restart server to load defaults
./scripts/tl-shutdown.sh
./scripts/tl-startup.sh
```

## See Also

- [Installation Guide](installation.md) - Initial setup procedures
- [Quick Start Guide](quick-start.md) - Get operational quickly
- [Deployment Guide](../deployment/local-deployment.md) - Production deployment
- [API Reference](../technical/api-reference.md) - Programmatic configuration
