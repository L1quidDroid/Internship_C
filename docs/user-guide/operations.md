---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes work completed during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production software guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Operations Management

## Introduction

This guide covers the creation, configuration, and execution of automated purple team operations developed during this internship project. The custom Orchestrator plugin demonstrates workflow automation capabilities for educational purposes.

## Prerequisites

- Active agents deployed and communicating with Command Center
- Adversary profiles configured in Stockpile plugin
- Understanding of MITRE ATT&CK framework
- SIEM integration configured (optional, for automated tagging)

## Operations Overview

### What is an Operation?

An operation represents a coordinated execution of adversary techniques against enrolled agents. Operations utilise:

- **Adversary Profiles**: Pre-defined sequences of techniques
- **Planners**: Logic determining technique execution order
- **Fact Sources**: Data sources providing operational context
- **Agents**: Target systems executing techniques

### Operation Lifecycle

```
Create → Configure → Start → Execute → Complete → Report
```

## Creating an Operation

### Step 1: Navigate to Operations Interface

Access the operations management interface:

```
http://localhost:8888/operations
```

Alternatively: **Campaigns → Operations**

### Step 2: Initiate Operation Creation

Select **"Create Operation"** to open the configuration interface.

### Step 3: Configure Operation Parameters

Configure the following parameters:

| Field | Description | Recommended Value |
|-------|-------------|-------------------|
| Name | Operation identifier | `PURPLE-<CLIENT>-<DATE>` |
| Adversary | Pre-built attack profile | Select from Stockpile |
| Planner | Execution sequencing logic | `atomic` (sequential) or `batch` |
| Fact Source | Operational data source | `basic` or client-specific |
| Auto-close | Automatic completion | `Enabled` |
| Obfuscator | Technique obfuscation | `plain-text` (for visibility) |

#### Naming Conventions

Adopt consistent naming conventions for operational clarity:

- **Client-Based**: `PURPLE-ACME-20260108`
- **Technique-Based**: `DISCOVERY-PHASE-001`
- **Environment-Based**: `PROD-ASSESSMENT-Q1`

### Step 4: Select Adversary Profile

Adversary profiles define the sequence and scope of techniques executed during an operation.

#### Pre-configured Profiles

The Stockpile plugin includes several pre-configured adversary profiles:

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

#### Custom Adversary Profiles

Create custom profiles by defining technique sequences aligned to specific attack scenarios or compliance frameworks.

### Step 5: Start Operation Execution

After configuration:

1. Review operation parameters
2. Verify target agent availability
3. Select **"Start"** to begin automated execution

The operation will proceed through configured techniques, adapting based on planner logic and fact source data.

## Orchestrator Consolidated Workflow

The Orchestrator plugin enables fully automated purple team workflows, eliminating manual intervention between operation stages.

### Automated Workflow Sequence

The consolidated workflow automates the following sequence:

1. **Agent Verification**: Confirm target agents are active and communicating
2. **Operation Execution**: Execute adversary techniques against enrolled agents
3. **SIEM Tagging**: Automatically tag generated security events
4. **Report Generation**: Produce assessment reports upon completion

### Programmatic Operation Control

The Orchestrator utilises the REST API for programmatic operation management:

```python
# Simplified workflow implementation
async def execute_consolidated_workflow(services):
    """
    Automated purple team workflow execution
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

## API-Driven Operation Control

The Command Center provides RESTful API endpoints for programmatic operation management.

### Starting an Operation

```bash
# Start operation via REST API
curl -X PATCH http://localhost:8888/api/v2/operations/<OP_ID> \
  -H "Content-Type: application/json" \
  -d '{"state": "running"}'
```

### Monitoring Operation Status

```bash
# Check operation status
curl http://localhost:8888/api/v2/operations/<OP_ID>

# Response includes current state
{
  "id": "<OP_ID>",
  "name": "PURPLE-ACME-20260108",
  "state": "running",
  "adversary": {...},
  "agents": [...]
}
```

### Retrieving Execution Results

```bash
# List all techniques executed
curl http://localhost:8888/api/v2/operations/<OP_ID>/links

# Response includes execution details
[
  {
    "id": "<LINK_ID>",
    "ability": "T1016",
    "status": "success",
    "output": "..."
  },
  ...
]
```

## Intelligent SIEM Tagging

The intelligent SIEM tagging feature eliminates manual alert closure by automatically tagging simulated attack logs with identifying metadata.

### Overview

When an operation begins, the Orchestrator automatically notifies the SIEM, creating a tagged time window for all generated events.

### SIEM Integration Hook

The `post_operation_start` hook triggers SIEM notification:

```python
# orchestrator/hook.py
from plugins.orchestrator.app.siem_connector import SIEMConnector

class OrchestratorService:
    
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

### ELK Configuration

Configure ELK integration through environment variables:

```bash
export ELK_HOST="192.168.1.50"
export ELK_PORT="9200"
export ELK_INDEX="purple-team-*"
export ELK_API_KEY="your-api-key-here"

python3 server.py --insecure
```

### SIEM Tag Structure

Events generated during operations receive the following tag structure:

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

### SOC Analyst Workflow Impact

The automated tagging significantly reduces SOC analyst workload:

| Before (Manual) | After (Automated) |
|-----------------|-------------------|
| Alert fires in SIEM | Alert fires with tag |
| Analyst investigates | Filter: `purple_team_exercise=true` |
| Cross-reference with PT schedule | Auto-acknowledged |
| Manually close alert | Bulk auto-close |
| **Time: 5-10 min/alert** | **Time: 0 min/alert** |

### SIEM Filter Configuration

Configure SIEM rules to automatically handle tagged events:

```
# Example: ELK query to filter purple team events
triskele.purple_team_exercise: true

# Auto-close rule configuration
if triskele.purple_team_exercise == true and triskele.auto_close == true:
    alert.status = "acknowledged"
    alert.assignee = "purple_team_automation"
```

## Operation Best Practices

### Planning Operations

- **Scope Definition**: Clearly define operation objectives and success criteria
- **Stakeholder Notification**: Inform relevant parties of scheduled operations
- **Baseline Documentation**: Document normal system behaviour for comparison
- **Timing Consideration**: Schedule operations during appropriate windows

### Execution Monitoring

- **Real-Time Monitoring**: Monitor operation progress through Command Center interface
- **Resource Monitoring**: Verify target system performance during execution
- **SIEM Correlation**: Confirm security events are being generated and tagged
- **Intervention Readiness**: Prepare to pause or stop operations if issues arise

### Post-Operation Activities

- **Results Review**: Analyse execution results for successful and failed techniques
- **SIEM Verification**: Confirm all events properly tagged and correlated
- **Report Generation**: Generate assessment reports while operation context is fresh
- **Lessons Learned**: Document operational insights for future improvements

## Troubleshooting

### Operation Stuck at 0% Progress

**Possible Causes**:
- No matching abilities for agent platform
- Agent connectivity issues
- Planner configuration problems

**Resolution**:
1. Verify agent platform matches ability requirements
2. Confirm agent is active and communicating
3. Review planner configuration and fact sources

### Techniques Failing to Execute

**Possible Causes**:
- Insufficient privileges on target system
- Security controls blocking execution
- Missing dependencies for technique

**Resolution**:
1. Review technique requirements and prerequisites
2. Verify agent running with appropriate privileges
3. Check technique output for specific error messages

### SIEM Tags Not Appearing

**Possible Causes**:
- ELK configuration incorrect
- Network connectivity to SIEM
- Index pattern mismatch

**Resolution**:
1. Verify ELK environment variables are set correctly
2. Test connectivity: `curl http://$ELK_HOST:$ELK_PORT/_cluster/health`
3. Confirm index pattern matches ELK configuration

## Next Steps

- [Generate assessment reports](reporting.md)
- [Configure custom adversary profiles](../guides/adversary-profiles.md)
- [Advanced operation configuration](../guides/advanced-operations.md)

## See Also

- [Agent Management](agents.md)
- [System Architecture Overview](overview.md)
- [API Reference - Operations](../reference/api.md#operations)
- [MITRE ATT&CK Integration](../technical/mitre-attack.md)
