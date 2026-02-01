# ELK Integration Guide

This guide covers integrating the Triskele Labs Command Center with Elasticsearch, Logstash, and Kibana (ELK Stack) for automated SIEM tagging and purple team exercise tracking.

## Prerequisites

### Required Components

- Elasticsearch cluster (single-node or multi-node)
- Kibana for visualisation
- Logstash for log processing (optional)
- Elastic Agent for data collection (optional)
- Network connectivity between Caldera and Elasticsearch

### Elasticsearch Requirements

- Elasticsearch 8.x or higher
- Index pattern for security logs (e.g., `winlogbeat-*`, `purple-team-logs`)
- API access with appropriate permissions
- Sufficient disk space for indexed data

### Caldera Requirements

- Orchestrator plugin enabled
- Python requests library installed
- Environment variables configured for ELK access

## Authentication Setup

### Environment Variables Method (Recommended)

Create `.env.elk` file in Caldera root directory:

```bash
cat > .env.elk << 'EOF'
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='your-password-here'
EOF

# Secure the file
chmod 600 .env.elk
```

**Security Notes:**
- Never commit `.env.elk` to version control
- File is automatically gitignored
- Use restrictive file permissions (600)
- Consider using API keys instead of passwords for production

Source credentials before starting Caldera:

```bash
source .env.elk
python3 server.py --insecure --log INFO
```

### Configuration File Method

Alternatively, configure in `conf/local.yml`:

```yaml
plugins:
  orchestrator:
    elk_url: "http://20.28.49.97:9200"
    elk_user: "elastic"
    elk_pass: "your-password-here"
    elk_index: "purple-team-logs"
```

**Note:** This method stores credentials in plaintext. Prefer environment variables for production.

### API Key Method (Production)

Generate API key in Kibana for enhanced security:

```bash
# In Kibana Dev Tools, create API key
POST /_security/api_key
{
  "name": "caldera-orchestrator",
  "role_descriptors": {
    "caldera_writer": {
      "cluster": ["monitor"],
      "index": [
        {
          "names": ["purple-team-logs", "winlogbeat-*"],
          "privileges": ["write", "create_index"]
        }
      ]
    }
  }
}
```

Configure in `.env.elk`:

```bash
export ELK_URL="http://20.28.49.97:9200"
export ELK_API_KEY="encoded-api-key-here"
# Remove ELK_USER and ELK_PASS when using API key
```

## Verifying Connectivity

### Test Elasticsearch Connection

```bash
# Test authentication
curl -u "elastic:your-password" "http://20.28.49.97:9200/_cluster/health?pretty"
```

Expected response:

```json
{
  "cluster_name" : "purplePracCluster",
  "status" : "yellow",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "active_primary_shards" : 5,
  "active_shards" : 5,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 0
}
```

**Note:** Yellow status is acceptable for single-node deployments.

### Check Available Indices

```bash
curl -u "elastic:your-password" "http://20.28.49.97:9200/_cat/indices?v"
```

Look for indices like `winlogbeat-*` or `purple-team-logs`.

### Verify Orchestrator Status

After starting Caldera with credentials:

```bash
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool
```

Expected output:

```json
{
  "plugin": "orchestrator",
  "status": "running",
  "elk": {
    "status": "connected",
    "url": "http://20.28.49.97:9200",
    "index": "purple-team-logs",
    "cluster_name": "purplePracCluster"
  }
}
```

**Status Values:**
- `connected` - Successfully connected to Elasticsearch
- `error` - Authentication or connection failure
- `client_not_initialised` - Environment variables not set
- `circuit_breaker_open` - Too many connection failures

## SIEM Tagging Workflow

### Overview

The Orchestrator plugin automatically tags security logs with purple team metadata when operations run:

1. Operation starts in Caldera
2. Orchestrator hooks into operation lifecycle events
3. Tags are sent to Elasticsearch with operation metadata
4. Logs are enriched with `purple.*` fields
5. SOC analysts filter tagged events in Kibana

### Tag Structure

Each tagged log includes purple team metadata:

```json
{
  "@timestamp": "2026-02-01T14:30:00.000Z",
  "event.category": "process",
  "purple": {
    "operation_id": "c9fd06a7-0cce-474d-adc3-8769db2ef392",
    "operation_name": "PURPLE-ACME-20260201",
    "link_id": "abc123-def456",
    "technique": "T1033",
    "techniques": ["T1033", "T1087.001"],
    "tactic": "discovery",
    "success": true,
    "agent_paw": "agent-hostname",
    "timestamp": "2026-02-01T14:30:00Z"
  },
  "tags": ["purple_team", "caldera", "purple_T1033"],
  "host": {
    "name": "target-system"
  }
}
```

### Operation-Level Tags

When an operation starts or completes:

```bash
# Query operation-level tags
curl -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_id:*&size=1&pretty"
```

### Link-Level Tags (Individual Attacks)

Each executed ability (attack) receives a unique tag:

```bash
# Query individual attack tags
curl -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.link_id:*&size=1&pretty"
```

### Technique-Specific Queries

Filter logs by MITRE ATT&CK technique:

```bash
# Find all T1033 (System Owner/User Discovery) events
curl -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.technique:T1033&pretty"

# Find successful attacks
curl -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.success:true&pretty"

# Find specific operation
curl -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_name:PURPLE-ACME-20260201&pretty"
```

## Index Configuration

### Create Purple Team Index

Create dedicated index for purple team logs:

```bash
curl -u elastic:password -X PUT "http://20.28.49.97:9200/purple-team-logs" \
  -H 'Content-Type: application/json' \
  -d '{
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "purple": {
          "properties": {
            "operation_id": { "type": "keyword" },
            "operation_name": { "type": "keyword" },
            "link_id": { "type": "keyword" },
            "technique": { "type": "keyword" },
            "techniques": { "type": "keyword" },
            "tactic": { "type": "keyword" },
            "success": { "type": "boolean" },
            "agent_paw": { "type": "keyword" },
            "timestamp": { "type": "date" }
          }
        },
        "tags": { "type": "keyword" }
      }
    }
  }'
```

### Index Lifecycle Management

Configure ILM policy to manage log retention:

```bash
curl -u elastic:password -X PUT "http://20.28.49.97:9200/_ilm/policy/purple-team-policy" \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover": {
              "max_size": "50GB",
              "max_age": "30d"
            }
          }
        },
        "delete": {
          "min_age": "90d",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  }'
```

## Kibana Visualisation

### Create Index Pattern

1. Navigate to Kibana: `http://20.28.49.97:5601`
2. Go to **Stack Management** → **Index Patterns**
3. Click **Create index pattern**
4. Enter pattern: `purple-team-logs`
5. Select time field: `@timestamp`
6. Click **Create index pattern**

### Discover Purple Team Events

1. Navigate to **Discover**
2. Select `purple-team-logs` index pattern
3. Add filters:
   - `purple.operation_id` exists
   - `tags` includes `purple_team`

### Create Saved Search

Filter for purple team exercises:

```
tags: purple_team AND purple.operation_id: *
```

Save as "Purple Team Exercises".

### Build Dashboard

Create visualisations:

1. **Operations Timeline** - Line chart of `@timestamp` grouped by `purple.operation_name`
2. **Technique Coverage** - Pie chart of `purple.technique`
3. **Success Rate** - Metric showing percentage where `purple.success: true`
4. **Tactic Distribution** - Bar chart of `purple.tactic`

### Alert Rules

Create alert for untagged suspicious activity:

```
event.category: (process OR network OR file) AND NOT tags: purple_team
```

This identifies genuine threats vs. purple team exercises.

## Troubleshooting

### Purple Team Logs Not Appearing

**Symptom:** Operations run but no logs in ELK

**Diagnosis:**

```bash
# 1. Check if env vars are set
echo "ELK_URL: $ELK_URL"
echo "ELK_USER: $ELK_USER"
echo "ELK_PASS: ${ELK_PASS:0:5}..."

# 2. Check orchestrator status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

# 3. Check Caldera logs
grep -i "orchestrator\|ELK" logs/*.log | tail -20

# 4. Check fallback logs (if ELK fails)
ls -lh plugins/orchestrator/data/fallback_logs/
```

**Fix:**

Ensure credentials are exported before starting Caldera:

```bash
source .env.elk
python3 server.py --insecure --log INFO
```

### Authentication Errors

**Error:** `"elk.status": "error"` or `"401 Unauthorized"`

**Diagnosis:**

```bash
# Verify credentials work
curl -u "elastic:YOUR_PASSWORD" "http://20.28.49.97:9200/_cluster/health"
```

**Fix:**

If credentials are correct, restart Caldera with proper environment:

```bash
source .env.elk && python3 server.py --insecure --log INFO
```

### Circuit Breaker Open

**Error:** `"circuit_breaker_open": true`

**Cause:** 5+ consecutive ELK connection failures

**Fix:**

1. Resolve network or authentication issue
2. Restart Caldera (circuit breaker resets on startup)

```bash
pkill -f "python.*server.py"
source .env.elk
python3 server.py --insecure --log INFO
```

### Index Pattern Mismatch

**Symptom:** Tags sent to Elasticsearch, but queries return no results

**Cause:** `ELK_INDEX` set to wrong pattern

**Diagnosis:**

```bash
# Check actual index names
curl -u elastic:password "http://20.28.49.97:9200/_cat/indices?v" | grep -i log
```

**Fix:**

Update configuration to match actual index pattern:

```yaml
plugins:
  orchestrator:
    elk_index: "winlogbeat-*"  # Use actual index pattern
```

Restart Caldera.

### Event Handler Not Firing

**Symptom:** Logs show operation completion events, but no tagging occurs

**Diagnosis:**

```bash
# Check Caldera logs for event handlers
tail -100 logs/*.log | grep -i orchestrator
```

Expected log entries when operation completes:

```
[orchestrator] State change: c9fd06a7... (running → finished)
[orchestrator] Operation finished: c9fd06a7...
ELK tagged operation: c9fd06a7... (doc ID: abc123)
```

**Fix:**

Verify Orchestrator plugin is enabled in `conf/local.yml`:

```yaml
plugins:
  - orchestrator
```

Restart Caldera.

### Fallback Logs Created

**Symptom:** Files appear in `plugins/orchestrator/data/fallback_logs/`

**Cause:** Elasticsearch unreachable, tags written to local files as backup

**Fix:**

1. Resolve ELK connectivity issue
2. Tags in fallback logs can be manually imported:

```bash
# Each fallback log is JSON
cat plugins/orchestrator/data/fallback_logs/fallback_*.json

# Import to Elasticsearch
curl -u elastic:password -X POST "http://20.28.49.97:9200/purple-team-logs/_doc" \
  -H 'Content-Type: application/json' \
  -d @plugins/orchestrator/data/fallback_logs/fallback_20260201.json
```

## Verification Checklist

After configuring ELK integration:

- [ ] Orchestrator status shows `"elk.status": "connected"`
- [ ] Environment variables are set and exported
- [ ] Test operation tags logs successfully
- [ ] Elasticsearch query returns purple team documents
- [ ] Kibana can filter by `tags: purple_team`
- [ ] Individual attacks have unique `purple.link_id` values

### Quick Verification Script

```bash
#!/bin/bash
echo "1. Plugin status..."
curl -s http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

echo -e "\n2. ELK connectivity..."
curl -s -u elastic:password "http://20.28.49.97:9200/_cluster/health" | python3 -m json.tool

echo -e "\n3. Purple team tag count..."
curl -s -u elastic:password -X GET "http://20.28.49.97:9200/purple-team-logs/_count" \
  -H 'Content-Type: application/json' \
  -d '{"query": {"term": {"tags": "purple_team"}}}'

echo -e "\n4. Recent purple team events..."
curl -s -u elastic:password "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_id:*&size=5&sort=@timestamp:desc&pretty"
```

## Advanced Configuration

### Custom Tag Fields

Modify Orchestrator to add custom fields:

```python
# plugins/orchestrator/app/elk_tagger.py
def generate_tags(self, operation):
    return {
        "purple": {
            "operation_id": operation.id,
            "operation_name": operation.name,
            "custom_field": "custom_value",
            "environment": "production",
            "client": "ACME Corp"
        }
    }
```

### Multiple ELK Targets

Send tags to multiple Elasticsearch clusters:

```bash
export ELK_URL_PRIMARY="http://elk1.example.com:9200"
export ELK_URL_SECONDARY="http://elk2.example.com:9200"
export ELK_USER="elastic"
export ELK_PASS="password"
```

Modify Orchestrator to send to both targets.

### Logstash Integration

Use Logstash pipeline to enrich purple team tags:

```ruby
# /etc/logstash/conf.d/purple-team-enrichment.conf
filter {
  if [tags] and "purple_team" in [tags] {
    mutate {
      add_field => {
        "alert_suppression" => "true"
        "auto_close" => "true"
        "confidence" => "high"
      }
    }
  }
}
```

Restart Logstash:

```bash
sudo systemctl restart logstash
```

## SOC Analyst Workflow

### Before Automated Tagging

1. Alert fires in SIEM
2. Analyst investigates source
3. Cross-reference with purple team schedule
4. Manually close alert
5. **Time: 5-10 minutes per alert**

### After Automated Tagging

1. Alert fires with `purple_team` tag
2. Filter: `tags: purple_team`
3. Auto-acknowledged
4. Bulk auto-close
5. **Time: 0 minutes per alert**

### Kibana Filter Examples

Exclude purple team events from alert view:

```
NOT tags: purple_team
```

Show only genuine threats:

```
event.category: (process OR network OR file) AND NOT tags: purple_team
```

View purple team activity summary:

```
tags: purple_team AND purple.operation_id: *
```

## File Structure

```
Internship_C/
├── .env.elk                  ← ELK credentials (gitignored)
├── plugins/orchestrator/
│   ├── app/
│   │   ├── config.py         ← Loads env vars
│   │   ├── elk_tagger.py     ← Tags operations/links
│   │   └── orchestrator_svc.py
│   └── data/
│       └── fallback_logs/    ← Backup logs if ELK fails
└── conf/
    └── local.yml             ← Plugin configuration
```

## Best Practices

### Security

1. **Use API keys** instead of passwords for production
2. **Restrict network access** to Elasticsearch cluster
3. **Enable TLS/SSL** for encrypted communication
4. **Rotate credentials** regularly
5. **Audit access logs** to detect unauthorised access

### Performance

1. **Use bulk API** for multiple tags (future enhancement)
2. **Configure index sharding** appropriately for load
3. **Monitor cluster health** regularly
4. **Implement ILM policies** for log retention
5. **Use dedicated index** for purple team logs

### Operational

1. **Test connectivity** before starting operations
2. **Monitor fallback logs** for unreachable ELK
3. **Review tagged events** in Kibana regularly
4. **Document custom fields** added to tags
5. **Coordinate with SOC** on tag usage

## Performance Considerations

### Network Latency

For remote Elasticsearch clusters, network latency affects tagging speed:

- Local network: < 10ms per tag
- Remote network: 50-200ms per tag
- Use async requests to avoid blocking operations

### Bulk Tagging

For operations with many links (100+), consider bulk indexing:

```python
# Pseudo-code for future enhancement
def bulk_tag_operation(links):
    bulk_body = []
    for link in links:
        bulk_body.append({"index": {"_index": "purple-team-logs"}})
        bulk_body.append(generate_tag(link))
    
    requests.post(f"{ELK_URL}/_bulk", data=bulk_body)
```

### Resource Usage

ELK integration adds minimal overhead:

- Memory: ~50MB for Orchestrator plugin
- CPU: Negligible (async HTTP requests)
- Network: ~1KB per tagged event

## Next Steps

- [Local Deployment](local-deployment.md) - Deploy Caldera locally
- [Docker Deployment](docker-deployment.md) - Deploy with containers
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## See Also

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Orchestrator Plugin](../plugins/orchestrator.md)
- [Purple Team User Guide](../PURPLE_TEAM_USER_GUIDE.md)
