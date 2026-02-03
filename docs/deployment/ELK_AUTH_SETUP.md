# ELK Authentication Setup for Orchestrator Plugin

## Quick Start (Dev Environment)

### 1. Set Environment Variables

```bash
# Source the credentials file
source .env.elk

# OR export manually
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='ms4FiYr-C1bx0F1=GFrM'
```

### 2. Start Caldera

```bash
# Option A: Use startup script (recommended)
../scripts/start_caldera.sh

# Option B: Manual start (ensure env vars are set first)
source .env.elk && python server.py --insecure --log INFO
```

### 3. Verify Orchestrator Connection

```bash
# Check orchestrator status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

# Expected output:
# {
#   "elk": {
#     "status": "connected",  ← Should be "connected"
#     "cluster_name": "purplePracCluster"
#   }
# }
```

## Development Environment (Learning Setup)

**⚠️ INTERNSHIP PROJECT**: This section describes development environment setup for learning purposes.

### 1. On VM: Create `.env.elk` File

```bash
ssh user@tl-vm
cd /path/to/caldera

# Create .env.elk with secure credentials
cat > .env.elk << 'EOF'
export ELK_URL="http://20.28.49.97:9200"
export ELK_USER="elastic"
export ELK_PASS='ms4FiYr-C1bx0F1=GFrM'
EOF

# Secure the file
chmod 600 .env.elk
```

### 2. Verify ELK Connectivity

```bash
# Test authentication
curl -u "elastic:ms4FiYr-C1bx0F1=GFrM" "http://20.28.49.97:9200/_cluster/health?pretty"

# Should return cluster status (green/yellow)
```

### 3. Start Caldera with Credentials

```bash
# Use startup script
../scripts/start_caldera.sh

# OR manually
source .env.elk && python server.py --insecure --log INFO
```

## Troubleshooting

### Purple Team Logs Not Appearing

**Symptom:** Operations run but no logs in ELK

**Diagnosis:**
```bash
# 1. Check if env vars are set in current shell
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
```bash
# Ensure credentials are exported BEFORE starting Caldera
source .env.elk

# Restart Caldera
../scripts/start_caldera.sh
```

### Authentication Errors

**Error:** `"elk.status": "error"` or `"401 Unauthorized"`

**Fix:**
```bash
# Verify credentials work
curl -u "elastic:YOUR_PASSWORD" "http://20.28.49.97:9200/_cluster/health"

# If successful, credentials are correct
# Restart Caldera with: source .env.elk && python server.py
```

### Circuit Breaker Open

**Error:** `"circuit_breaker_open": true`

**Cause:** 5+ consecutive ELK connection failures

**Fix:**
```bash
# 1. Fix network/auth issue
# 2. Restart Caldera (circuit breaker resets on startup)
../scripts/start_caldera.sh
```

## Verification Checklist

After starting Caldera:

- [ ] ✅ Orchestrator status shows `"elk.status": "connected"`
- [ ] ✅ Run operation → Check logs: `grep "ELK tagged" logs/*.log`
- [ ] ✅ Query ELK: `curl -u elastic:PASS "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_id:*"`
- [ ] ✅ Individual attacks tagged: `curl ... "?q=purple.link_id:*"`

## Security Notes

- ⚠️ **Never commit** `.env.elk` or credentials to Git
- ⚠️ `.env.*` is gitignored automatically
- ⚠️ For production, use API keys instead of passwords:
  ```bash
  # Generate API key in Kibana
  export ELK_API_KEY="your-api-key-here"
  # Remove ELK_USER and ELK_PASS
  ```

## File Structure

```
Internship_C/
├── .env.elk                  ← ELK credentials (gitignored)
├── start_caldera.sh          ← Startup script (sources .env.elk)
├── plugins/orchestrator/
│   ├── app/
│   │   ├── config.py         ← Loads env vars
│   │   ├── elk_tagger.py     ← Tags operations/links
│   │   └── orchestrator_svc.py
│   └── data/
│       └── fallback_logs/    ← Backup logs if ELK fails
```

## Testing Individual Attack Tagging

After running an operation:

```bash
# Query operation-level tag
curl -u elastic:PASS "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.operation_id:*&size=1&pretty"

# Query individual attack (link-level tag)
curl -u elastic:PASS "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.link_id:*&size=1&pretty"

# Filter by technique
curl -u elastic:PASS "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.technique:T1033&pretty"

# Find successful attacks
curl -u elastic:PASS "http://20.28.49.97:9200/purple-team-logs/_search?q=purple.success:true&pretty"
```
