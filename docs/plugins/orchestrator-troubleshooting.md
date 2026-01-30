# Orchestrator Plugin - Troubleshooting Guide

## Problem: Tags Not Appearing in Elasticsearch

This guide helps diagnose why purple team tags aren't being added to ELK logs.

---

## Quick Diagnostic Checklist

Run these commands on the Ubuntu VM to check each component:

### 1. Verify Plugin Loaded
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

**If elk.status != "connected":**
- Check ELK_URL, ELK_USER, ELK_PASS environment variables
- Test ELK connectivity: `curl -u elastic:password http://20.28.49.97:9200`
- Check Elasticsearch is running: `systemctl status elasticsearch`

---

### 2. Test Manual Tagging (Bypass Events)
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

**If status == "error":**
- Check Elasticsearch authentication (API key or basic auth)
- Verify index exists: `curl http://20.28.49.97:9200/_cat/indices?v`
- Check circuit breaker status in /status endpoint

**If status == "fallback":**
- Elasticsearch is unreachable
- Tags are being written to `plugins/orchestrator/data/fallback_logs/`
- Check `fallback_*.json` files for tag data

---

### 3. Check Caldera Logs for Event Handlers
```bash
tail -100 /path/to/caldera/logs/*.log | grep -i orchestrator
```

**Expected log entries when operation completes:**
```
[orchestrator] State change: c9fd06a7... (running → finished)
[orchestrator] Operation finished: c9fd06a7... (state: finished)
ELK tagged operation: c9fd06a7... (doc ID: abc123)
```

**If no logs appear:**
- Event handlers are not being triggered
- Check websocket contact is running: `netstat -tulpn | grep 8080`
- Verify plugin registered callbacks (check startup logs for "✅ Orchestrator event handlers registered")

**If seeing "missing operation ID" warnings:**
- Event message is not being parsed correctly (THIS WAS THE BUG - NOW FIXED)
- Verify orchestrator_svc.py uses `socket.recv()` to read JSON

---

### 4. Monitor Websocket Events (Advanced)
```python
# Run this in Python shell on Caldera server
import asyncio
import websockets
import json

async def monitor_events():
    uri = "ws://localhost:8080/operation/completed"
    try:
        async with websockets.connect(uri) as ws:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                print(f"✅ Event received: op={data.get('op')}, timestamp={data.get('metadata', {}).get('timestamp')}")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(monitor_events())
```

**Press Ctrl+C to stop, then run an operation in Caldera UI**

**If connection refused:**
- Websocket contact not started
- Check `conf/local.yml` for `app.contact.websocket` setting (default: 0.0.0.0:8080)

**If no events appear:**
- Operations are not firing completion events
- Check Caldera version compatibility (5.0+ required)

---

### 5. Verify Elasticsearch Receives Tags
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

**If total.value == 0:**
- Tags are not being written to Elasticsearch
- Check fallback logs: `ls -lh plugins/orchestrator/data/fallback_logs/`
- If fallback logs exist → ELK connectivity issue
- If no fallback logs → event handlers not executing

---

## Common Issues & Fixes

### Issue 1: "Event handler signature mismatch" (FIXED in this commit)
**Symptom:** Logs show operation completion events, but no tagging occurs

**Cause:** Event handlers expected `(op, **kwargs)` but received `(socket, path, services)`

**Fix:** Updated signatures to:
```python
async def on_operation_completed(self, socket, path, services):
    message_data = await socket.recv()
    event_data = json.loads(message_data)
    op_id = event_data.get('op')
    # ... process event
```

**Verification:**
```bash
python3 plugins/orchestrator/test_event_handler.py
# Should output: ✅ ALL TESTS PASSED
```

---

### Issue 2: "ELK client not initialised"
**Symptom:** `/status` shows `elk.status: "client_not_initialised"`

**Fix:**
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

---

### Issue 3: "Index pattern mismatch"
**Symptom:** Tags sent to Elasticsearch, but queries return no results

**Cause:** `ELK_INDEX` set to wrong pattern (`purple-team-logs` vs `winlogbeat-*`)

**Fix:**
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

---

### Issue 4: "Operation completes before plugin loads"
**Symptom:** First operation after Caldera restart doesn't get tagged

**Cause:** Event handlers only receive events fired AFTER subscription

**Fix:** This is expected behavior. Subsequent operations will be tagged correctly.

**Workaround:** Use manual tagging API for historical operations:
```bash
# Get operation JSON from Caldera
OP_JSON=$(curl http://localhost:8888/api/v2/operations/<op-id>)

# Manually trigger tagging (custom script needed)
# Or re-run the operation
```

---

## Verification Script

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

---

## Success Criteria

After fixing and deploying:

1. **Plugin loads:** ✅ `/status` returns `"status": "running"`
2. **ELK connected:** ✅ `elk.status: "connected"`
3. **Manual tagging works:** ✅ `/tag-test` returns `"status": "success"`
4. **Events fire:** ✅ Logs show "Operation finished" messages
5. **Tags written:** ✅ Elasticsearch query returns purple.* fields
6. **Kibana filtering:** ✅ Can filter by `tags: purple_team` in Discover

---

## Contact for Issues

If problems persist after following this guide:

1. Collect diagnostic output:
```bash
bash plugins/orchestrator/deploy_and_verify.sh > diagnostic.log 2>&1
```

2. Check for Python errors:
```bash
tail -100 caldera.log | grep -A 5 "Traceback\|Exception\|Error"
```

3. Share:
   - `diagnostic.log`
   - Caldera version
   - Elasticsearch version
   - Sample operation JSON (from test reports)

---

## Reference: Event Flow Diagram

```
[Caldera Operation]
      ↓ (completes)
[Operation.close()]
      ↓ (fires event)
[event_svc.fire_event(exchange='operation', queue='completed', op=<uuid>)]
      ↓ (serialises to JSON)
[Websocket: {"op": "<uuid>", "metadata": {...}}]
      ↓ (dispatches to handlers)
[orchestrator_svc.on_operation_completed(socket, path, services)]
      ↓ (reads socket)
[await socket.recv() → JSON data]
      ↓ (parses)
[json.loads() → {'op': '<uuid>'}]
      ↓ (fetches operation)
[data_svc.locate('operations', id=<uuid>)]
      ↓ (tags)
[elk_tagger.tag(operation)]
      ↓ (writes to ELK)
[Elasticsearch: purple.* fields added]
```
