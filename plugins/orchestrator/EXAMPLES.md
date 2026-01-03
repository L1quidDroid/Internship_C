# Orchestrator Plugin Usage Examples

## Example 1: Basic Operation Tagging

```bash
# 1. Start Caldera
python server.py --insecure --log INFO

# 2. Run operation via UI
# Navigate to: http://localhost:8888
# Operations → Create Operation → Select "Discovery" adversary → Start

# 3. Verify tagging in Kibana
curl "http://<elk-ip>:9200/purple-team-logs/_search?q=purple_team_exercise:true&pretty"

# Expected response:
{
  "hits": {
    "total": {"value": 1},
    "hits": [{
      "_source": {
        "operation_id": "abc-123-def-456",
        "purple_team_exercise": true,
        "techniques": ["T1078", "T1082"],
        "client_id": "acme_corp"
      }
    }]
  }
}
```

## Example 2: Kibana Filter for Detection Engineers

```
# In Kibana Discover:
1. Click "+ Add filter"
2. Field: purple_team_exercise
3. Operator: is not
4. Value: true
5. Click "Save"
6. Name: "Hide Purple Team Simulations"

# Result: Only real attacks visible in dashboard
```

## Example 3: Fallback Logging (ELK Down Scenario)

```bash
# 1. Stop Elasticsearch (simulate outage)
sudo systemctl stop elasticsearch

# 2. Run Caldera operation
# (via UI or API)

# 3. Check fallback logs
ls -lh plugins/orchestrator/data/fallback_logs/

# Expected output:
# -rw-r--r-- 1 tony tony 1.2K Jan  6 10:35 fallback_20260106_103045_abc123.json

# 4. View fallback data
cat plugins/orchestrator/data/fallback_logs/fallback_20260106_103045_abc123.json

{
  "operation_id": "abc-123-def-456",
  "operation_name": "Discovery & Credential Access",
  "purple_team_exercise": true,
  "techniques": ["T1078", "T1059.001"],
  "timestamp": "2026-01-06T10:30:45.123Z"
}

# 5. Restart Elasticsearch
sudo systemctl start elasticsearch

# 6. Manually import fallback logs (if needed)
# Future enhancement: import script
```

## Example 4: Verify Tagging Performance

```bash
# 1. Enable debug logging
export CALDERA_LOG_LEVEL=DEBUG

# 2. Run operation and check logs
tail -f logs/caldera.log | grep -i orchestrator

# Expected logs:
# [INFO] Tagging operation: abc-123-def...
# [INFO] ELK tagged operation: abc-123... (doc ID: elk-doc-xyz)

# 3. Verify latency <10 seconds
# Latency = (ELK POST timestamp) - (operation start timestamp)
```

## Example 5: Circuit Breaker Behavior

```bash
# 1. Misconfigure ELK URL (simulate permanent failure)
export ELK_URL=http://invalid:9200

# 2. Run 6 operations consecutively

# 3. Check logs for circuit breaker
tail -f logs/caldera.log | grep -i circuit

# Expected after 5 failures:
# [ERROR] Circuit breaker opened after 5 failures
# [INFO] Fallback log written: fallback_...json (ELK unavailable)

# 4. Fix configuration
export ELK_URL=http://10.0.0.4:9200

# 5. Circuit breaker auto-resets on next successful tag
```

## Troubleshooting

### Issue: Tags Not Appearing in Kibana

```bash
# 1. Check ELK connectivity
curl http://<elk-ip>:9200/_cluster/health?pretty

# 2. Verify index exists
curl http://<elk-ip>:9200/purple-team-logs?pretty

# 3. Check Caldera logs
grep -i "ELK tagged" logs/caldera.log

# 4. Check fallback logs (ELK might be down)
ls plugins/orchestrator/data/fallback_logs/
```

### Issue: High Memory Usage

```bash
# 1. Check ELK client connection pooling
grep -i "ELK client" logs/caldera.log

# 2. Monitor memory
watch -n 5 'free -h && ps aux --sort=-%mem | grep python | head -5'

# 3. Reduce concurrent operations if needed
# (Semaphore in elk_tagger.py limits to 5 concurrent tags)
```

### Issue: Plugin Not Loading

```bash
# 1. Check plugin is enabled in conf/local.yml
grep orchestrator conf/local.yml

# 2. Check startup logs
grep orchestrator logs/caldera.log

# Expected:
# [INFO] Orchestrator configuration validated
# [INFO] ✅ Orchestrator plugin enabled successfully

# 3. Verify dependencies installed
pip list | grep elasticsearch
```

## Configuration Reference

### Environment Variables (.env)

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

### Plugin Configuration (conf/local.yml)

```yaml
elk:
  url: http://localhost:9200
  index: purple-team-logs
  verify_ssl: false

plugins:
  - orchestrator  # Enable plugin
```
