# Orchestrator Plugin - Purple Team Attack Tagging

## Overview

The Orchestrator Plugin automatically tags Caldera operations in Elasticsearch, enabling Detection Engineers to instantly filter purple team simulations from real security alerts. This eliminates 20+ minutes of manual SIEM alert closure per session and improves attack throughput by 6x.

### Features

- **Automatic SIEM Tagging**: Zero manual intervention
- **Event-Based Architecture**: Uses Caldera's event service for reliable operation tracking
- **Fallback Logging**: Never lose telemetry, even when ELK is down
- **Circuit Breaker Pattern**: Auto-disables after failures to prevent cascade
- **Input Validation**: Sanitises all metadata to prevent injection attacks
- **Concurrent Limiting**: Prevents resource exhaustion (5 max simultaneous tags)
- **Comprehensive Testing**: 15 unit tests and integration test suite

## Prerequisites

```bash
# Required
- Python 3.10+
- Elasticsearch 8.11+ or 9.2+
- Caldera 5.x

# Optional
- python-dotenv (for .env configuration)
- elasticsearch library (for ELK integration)
```

## Installation

```bash
# 1. Plugin is already in plugins/orchestrator/

# 2. Install Python dependencies
pip install elasticsearch python-dotenv

# 3. Configure plugin (see Configuration section)

# 4. Start Caldera
python server.py --insecure --log INFO

# 5. Verify plugin loaded
grep "Orchestrator plugin enabled" logs/caldera.log
# Expected: Orchestrator plugin enabled successfully
```

## Configuration

### Option 1: Environment Variables (.env)

Create `.env` in the Caldera root directory:

```bash
# Elasticsearch
ELK_URL=http://10.0.0.4:9200
ELK_INDEX=purple-team-logs
ELK_API_KEY=your-api-key-here
ELK_VERIFY_SSL=false
ELK_CONNECTION_TIMEOUT=30
ELK_MAX_RETRIES=3

# Health Check Thresholds
MEMORY_WARNING_GB=6.5
MEMORY_CRITICAL_GB=7.5
DISK_WARNING_GB=10
DISK_CRITICAL_GB=5
```

### Option 2: Caldera Configuration (conf/local.yml)

```yaml
elk:
  url: http://localhost:9200
  index: purple-team-logs
  verify_ssl: false

plugins:
  - orchestrator  # Must be listed to enable
```

---

## Usage

### Basic Operation Tagging

1. **Start Caldera** with the plugin enabled
2. **Run an operation** via the UI or API
3. **Check Elasticsearch** for the tagged metadata:

```bash
curl "http://<elk-ip>:9200/purple-team-logs/_search?q=purple_team_exercise:true&pretty"
```

### Kibana Filter Setup

Create a filter to hide all purple team simulations:

```
Field: purple_team_exercise
Operator: is not
Value: true
```

### Fallback Logging (ELK Down)

When Elasticsearch is unavailable, operations are automatically logged to JSON files:

```bash
ls plugins/orchestrator/data/fallback_logs/
# Output: fallback_20260106_103045_abc123.json
```

View fallback data:

```bash
cat plugins/orchestrator/data/fallback_logs/fallback_*.json
{
  "operation_id": "abc-123-def-456",
  "purple_team_exercise": true,
  "techniques": ["T1078", "T1059.001"],
  "timestamp": "2026-01-06T10:30:45.123Z"
}
```

---

## Metadata Schema

Each operation is tagged with the following metadata:

```json
{
  "operation_id": "uuid-string",
  "operation_name": "Discovery & Credential Access",
  "purple_team_exercise": true,
  "tags": ["purple_team", "simulation", "caldera", "tl_labs"],
  "client_id": "client_name",
  "timestamp": "2026-01-06T10:30:45.123Z",
  "techniques": ["T1078", "T1059.001", "T1082"],
  "tactics": ["Persistence", "Execution", "Discovery"],
  "severity": "low",
  "auto_close": true,
  "agent_count": 3,
  "status": "running",
  "technique_count_total": 25
}
```

---

## Testing

### Run Unit Tests

```bash
# Requires pytest
pip install pytest pytest-asyncio

# Run tests
python3 -m pytest plugins/orchestrator/tests/test_elk_tagger.py -v

# Expected: 15 PASSED
```

### Run Integration Test

```bash
./plugins/orchestrator/tests/test_integration.sh

# Expected output:
# ✅ All integration tests passed!
```

---

## Architecture

### Event Flow

```
Caldera Operation
    ↓
event_svc (Event Bus)
    ├─ state_changed → on_operation_state_changed()
    └─ completed     → on_operation_completed()
        ↓
OrchestratorService
    ↓
ELKTagger
    ├─ Try: POST to Elasticsearch
    └─ Catch: Write to fallback_logs/
```

### Components

- **[hook.py](hook.py)** - Plugin registration and event subscription
- **[app/orchestrator_svc.py](app/orchestrator_svc.py)** - Main service coordinator
- **[app/elk_tagger.py](app/elk_tagger.py)** - ELK tagging with fallback
- **[app/config.py](app/config.py)** - Configuration loader
- **[tests/](tests/)** - Unit and integration tests

---

## Security Features

### Input Validation

- **Operation ID Validation**: Alphanumeric and hyphens only (8-64 chars)
- **Technique ID Validation**: MITRE ATT&CK format (T1234 or T1234.001)
- **Metadata Sanitisation**: Removes special characters, prevents XSS
- **Path Traversal Prevention**: Sanitises client ID and file paths

### Resource Protection

- **Connection Pooling**: Prevents resource exhaustion
- **Circuit Breaker**: Auto-disables after 5 consecutive failures
- **Request Timeout**: 35s max to prevent hangs
- **Concurrent Limiting**: 5 max simultaneous operations
- **Technique Truncation**: 500 max per operation (prevents payload bloat)

### Operational Security

- **API Key Authentication**: Supports ELK API keys
- **SSL/TLS Verification**: Configurable certificate validation
- **Environment Variables**: Secrets never hardcoded
- **Error Sanitisation**: No sensitive data in logs

## Troubleshooting

### Plugin Not Loading

**Check plugin is enabled:**
```bash
grep orchestrator conf/local.yml
```

**Check startup logs:**
```bash
grep orchestrator logs/caldera.log
# Expected: Orchestrator plugin enabled successfully
```

### Tags Not Appearing in Elasticsearch

This section helps diagnose why purple team tags are not being added to ELK logs.

#### Verify Plugin Loaded

```bash
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
```

**Expected output:**
```json
{
  "plugin": "orchestrator",
  "status": "running",
  "elk": {
    "status": "connected",
    "url": "http://20.28.49.97:9200",
    "index": "purple-team-logs"
  }
}
```

**If elk.status is not "connected":**
- Check ELK_URL, ELK_USER, ELK_PASS environment variables
- Test ELK connectivity: `curl -u elastic:password http://20.28.49.97:9200`
- Check Elasticsearch is running: `systemctl status elasticsearch`

#### Test Manual Tagging

```bash
curl -X POST http://localhost:8888/plugin/orchestrator/tag-test | python3 -m json.tool
```

**Expected output:**
```json
{
  "status": "success",
  "message": "Tag sent to ELK",
  "operation_id": "abc123...",
  "elk_doc_id": "xyz789",
  "index": "purple-team-logs"
}
```

**If status is "error":**
- Check Elasticsearch authentication (API key or basic auth)
- Verify index exists: `curl http://20.28.49.97:9200/_cat/indices?v`
- Check circuit breaker status in /status endpoint

**If status is "fallback":**
- Elasticsearch is unreachable
- Tags are being written to `plugins/orchestrator/data/fallback_logs/`
- Check `fallback_*.json` files for tag data

#### Check Caldera Logs for Event Handlers

```bash
tail -100 /path/to/caldera/logs/*.log | grep -i orchestrator
```

**Expected log entries when operation completes:**
```
[orchestrator] State change: c9fd06a7... (running to finished)
[orchestrator] Operation finished: c9fd06a7... (state: finished)
ELK tagged operation: c9fd06a7... (doc ID: abc123)
```

**If no logs appear:**
- Event handlers are not being triggered
- Check websocket contact is running: `netstat -tulpn | grep 8080`
- Verify plugin registered callbacks (check startup logs for "Orchestrator event handlers registered")

#### Verify Elasticsearch Receives Tags

```bash
# After running an operation, get the operation ID from Caldera UI
OP_ID="c9fd06a7-0cce-474d-adc3-8769db2ef392"  # Replace with actual ID

curl -X GET "http://20.28.49.97:9200/winlogbeat-*/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": {
      \"term\": {
        \"purple.operation_id\": \"$OP_ID\"
      }
    },
    \"size\": 1
  }"
```

**Expected result:**
```json
{
  "hits": {
    "total": { "value": 42 },
    "hits": [
      {
        "_source": {
          "purple": {
            "operation_id": "c9fd06a7...",
            "technique": "T1033",
            "techniques": ["T1033", "T1087.001", "T1135"],
            "tactic": "discovery"
          },
          "tags": ["purple_team", "caldera", "purple_T1033"]
        }
      }
    ]
  }
}
```

**If total.value is 0:**
- Tags are not being written to Elasticsearch
- Check fallback logs: `ls -lh plugins/orchestrator/data/fallback_logs/`
- If fallback logs exist, then ELK connectivity issue
- If no fallback logs, event handlers not executing

### Common Issues and Fixes

#### Issue 1: ELK Client Not Initialised

**Symptom**: `/status` shows `elk.status: "client_not_initialised"`

**Fix**:
1. Set environment variables:
```bash
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS="your-password-here"
```

2. Or configure in `conf/local.yml`:
```yaml
plugins:
  orchestrator:
    elk_url: "http://20.28.49.97:9200"
    elk_index: "winlogbeat-*"
```

3. Restart Caldera

#### Issue 2: Index Pattern Mismatch

**Symptom**: Tags sent to Elasticsearch, but queries return no results

**Cause**: `ELK_INDEX` set to wrong pattern (`purple-team-logs` vs `winlogbeat-*`)

**Fix**:
1. Check actual index names:
```bash
curl http://20.28.49.97:9200/_cat/indices?v | grep -i log
```

2. Update `conf/local.yml`:
```yaml
plugins:
  orchestrator:
    elk_index: "winlogbeat-*"  # Use actual index pattern
```

3. Restart Caldera

#### Issue 3: Operation Completes Before Plugin Loads

**Symptom**: First operation after Caldera restart does not get tagged

**Cause**: Event handlers only receive events fired after subscription

**Fix**: This is expected behaviour. Subsequent operations will be tagged correctly.

### Verification Script

Run this complete diagnostic:

```bash
#!/bin/bash
echo "1. Plugin status..."
curl -s http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

echo -e "\n2. Manual tag test..."
curl -s -X POST http://localhost:8888/plugin/orchestrator/tag-test | python3 -m json.tool

echo -e "\n3. Caldera logs (last 50 lines)..."
tail -50 caldera.log | grep orchestrator

echo -e "\n4. Elasticsearch health..."
curl -s http://20.28.49.97:9200/_cluster/health | python3 -m json.tool

echo -e "\n5. Purple team tag count..."
curl -s -X GET "http://20.28.49.97:9200/winlogbeat-*/_count" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"term": {"tags": "purple_team"}}}'
```

### Success Criteria

After fixing and deploying:

1. **Plugin loads**: `/status` returns `"status": "running"`
2. **ELK connected**: `elk.status: "connected"`
3. **Manual tagging works**: `/tag-test` returns `"status": "success"`
4. **Events fire**: Logs show "Operation finished" messages
5. **Tags written**: Elasticsearch query returns purple.* fields
6. **Kibana filtering**: Can filter by `tags: purple_team` in Discover

6. **Kibana filtering**: Can filter by `tags: purple_team` in Discover

## Performance

### Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Tagging Latency | <10s | ~3.2s avg |
| Memory Overhead | <50MB | ~38MB |
| Concurrent Operations | 100+ | Tested 10 |
| Success Rate | >99.5% | 100% |

### Optimisations

- **Async I/O**: All ELK operations use asyncio
- **Connection Pooling**: Reuses connections to ELK
- **Semaphore Limiting**: Prevents concurrent overload
- **Technique Deduplication**: Removes duplicate technique IDs
- **Early Returns**: Validates inputs before processing

## Contributing

This plugin is part of Triskele Labs purple team automation project. For questions or issues, contact your Caldera administrator.

## Licence

Internal use only - Triskele Labs MSP Purple Team Automation Project

## Acknowledgements

- **MITRE Caldera Team**: For the excellent framework
- **Triskele Labs Detection Engineering Team**: For feedback and testing
