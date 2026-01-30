# Debrief ELK Detections Plugin - Deployment Guide

## Overview
This guide covers production deployment of the debrief-elk-detections plugin for Caldera 5.0+. The plugin integrates MITRE debrief reports with Elasticsearch detection correlation to provide purple-team coverage analysis.

---

## Pre-Flight Checklist

### 1. Environment Requirements
- [ ] **Caldera**: Version 5.0 or higher installed
- [ ] **Python**: 3.9+ with pip
- [ ] **Elasticsearch**: 8.11.0+ cluster accessible from Caldera server
- [ ] **Network**: Caldera server can reach ELK cluster on configured port (default 9200)
- [ ] **Permissions**: Read access to `purple-team-logs-*` index in ELK

### 2. ELK Schema Validation
Verify the orchestrator plugin has created the required index schema:

```bash
# Check index exists and has purple.* fields
curl -X GET "http://your-elk:9200/purple-team-logs-*/_mapping" | jq '.[] | .mappings.properties.purple'

# Expected output should show:
# {
#   "operation_id": { "type": "keyword" },
#   "technique": { "type": "keyword" },
#   "detection_status": { "type": "keyword" },
#   ...
# }
```

If missing, ensure the orchestrator plugin is running and has ingested at least one detection event.

### 3. Dependencies Check
```bash
cd /path/to/caldera

# Verify required Python packages
pip list | grep -E "elasticsearch|reportlab|lxml"

# Expected output:
# elasticsearch    8.11.0
# reportlab        4.0.4
# lxml            ~4.9.1
```

If missing, install with:
```bash
pip install -r requirements.txt
```

---

## Installation Steps

### Step 1: Clone MITRE Debrief Plugin
```bash
cd plugins/
git clone https://github.com/mitre/debrief.git
```

### Step 2: Verify Plugin Files
```bash
# Check debrief-elk-detections structure
ls -la plugins/debrief-elk-detections/

# Expected files:
# hook.py
# README.md
# DEPLOYMENT.md (this file)
# .env.example
# conf/default.yml
# app/elk_fetcher.py
# app/debrief-sections/elk_detection_coverage.py
# tests/test_elk_fetcher.py
# tests/integration_test.sh
# tests/benchmark.py
```

### Step 3: Configure Credentials

#### Option A: Environment Variables (Recommended)
```bash
# Copy environment template
cp plugins/debrief-elk-detections/.env.example .env.caldera

# Edit with your actual credentials
vi .env.caldera

# Required variables:
# ELK_URL=https://your-elk.domain.com:9200
# ELK_USER=elastic
# ELK_PASSWORD=your_password_here
# OR use API key:
# ELK_API_KEY=your_base64_api_key
```

**CRITICAL**: Add `.env.caldera` to `.gitignore` to prevent credential leaks!

```bash
echo ".env.caldera" >> .gitignore
```

#### Option B: Direct Configuration (NOT Recommended for Production)
Edit `plugins/debrief-elk-detections/conf/default.yml`:
```yaml
debrief_elk_detections:
  elk_url: "https://your-elk:9200"
  elk_user: "elastic"
  elk_pass: "your_password"
  elk_verify_ssl: true
  elk_ca_cert: "/etc/caldera/certs/elk-ca.pem"
```

### Step 4: Enable Plugins in Caldera
Edit `conf/local.yml`:
```yaml
plugins:
  - stockpile
  - atomic
  - orchestrator  # Required: provides purple-team logging
  - debrief       # Required: provides report framework
  - debrief-elk-detections  # New: adds detection coverage section
```

**Order matters**: Ensure `debrief` is listed before `debrief-elk-detections`.

### Step 5: Production Security Hardening

#### A. Generate Read-Only ELK API Key
```bash
curl -X POST "https://your-elk:9200/_security/api_key" \
  -u elastic:password \
  -H "Content-Type: application/json" \
  -d '{
    "name": "caldera-debrief-readonly",
    "role_descriptors": {
      "debrief-reader": {
        "cluster": ["monitor"],
        "index": [{
          "names": ["purple-team-logs-*"],
          "privileges": ["read"]
        }]
      }
    },
    "expiration": "90d"
  }'

# Save the returned API key to .env.caldera:
# ELK_API_KEY=<base64_encoded_key_from_response>
```

#### B. Configure SSL/TLS
Edit `plugins/debrief-elk-detections/conf/default.yml`:
```yaml
debrief_elk_detections:
  elk_url: "https://your-elk:9200"  # HTTPS only!
  elk_verify_ssl: true
  elk_ca_cert: "/etc/caldera/certs/elk-ca.pem"
```

Copy ELK CA certificate to Caldera server:
```bash
# From ELK server
scp /etc/elasticsearch/certs/ca/ca.crt caldera-server:/etc/caldera/certs/elk-ca.pem

# Set permissions
chmod 644 /etc/caldera/certs/elk-ca.pem
```

#### C. Restrict File Permissions
```bash
chmod 600 .env.caldera
chmod 600 /etc/caldera/certs/elk-ca.pem
chown caldera:caldera .env.caldera
```

---

## Verification Steps

### Test 1: Plugin Loading
```bash
# Start Caldera
source .env.caldera && ./server.py

# Check logs for successful plugin load
tail -f logs/caldera.log | grep -i debrief
# Expected: "debrief-elk-detections plugin enabled"
```

### Test 2: ELK Connectivity
```bash
# Run integration tests
bash plugins/debrief-elk-detections/tests/integration_test.sh

# Expected output:
# ✓ All files exist
# ✓ Python syntax valid
# ✓ Imports successful
# ✓ ELK connectivity verified
```

### Test 3: Schema Validation
```bash
# Check Caldera logs for schema validation
grep "ELK schema validation" logs/caldera.log

# Expected: "ELK schema validation passed for index: purple-team-logs-*"
# Warning: If you see "missing required fields", the orchestrator schema is incomplete
```

### Test 4: Section Discovery
```bash
# Access Caldera GUI: http://localhost:8888
# Navigate to "Debrief" -> "Configure Report"
# Verify "ELK Detection Coverage" section appears in available sections
```

### Test 5: End-to-End Operation Test
1. **Create Operation**:
   - Navigate to "Operations" tab
   - Create new operation with atomic/stockpile adversary
   - Start operation and wait for completion

2. **Generate Report**:
   - Navigate to "Debrief" tab
   - Select completed operation
   - Enable "ELK Detection Coverage" section
   - Click "Generate PDF"

3. **Verify Output**:
   - PDF should include section with detection table
   - Techniques should show detected/evaded/pending status
   - ELK rule names should be populated
   - Check logs: `grep "Fetched detection data" logs/caldera.log`

### Test 6: Performance Validation
```bash
# Run benchmark tests
python plugins/debrief-elk-detections/tests/benchmark.py

# Target metrics:
# - ELK query time: < 3 seconds
# - PDF generation time: < 10 seconds
# - Memory usage: < 500 MB delta
```

---

## Troubleshooting Guide

### Issue 1: Plugin Not Loading
**Symptoms**: Debrief section doesn't appear in GUI

**Diagnosis**:
```bash
grep -i "error.*debrief" logs/caldera.log
ls -la plugins/debrief-elk-detections/app/debrief-sections/
```

**Solutions**:
- Verify `debrief` plugin is enabled BEFORE `debrief-elk-detections` in conf/local.yml
- Check file exists: `plugins/debrief-elk-detections/app/debrief-sections/elk_detection_coverage.py`
- Ensure class name is `DebriefReportSection` (case-sensitive)
- Restart Caldera: `./server.py`

---

### Issue 2: ELK Connection Failures
**Symptoms**: Section generates but shows "Detection data unavailable"

**Diagnosis**:
```bash
# Check ELK connectivity from Caldera server
curl -u elastic:password https://your-elk:9200/_cluster/health

# Check Caldera logs
grep "ELK connection failed" logs/caldera.log
```

**Solutions**:
- Verify ELK_URL is accessible: `telnet your-elk 9200`
- Check credentials: `echo $ELK_PASSWORD` (should match ELK)
- SSL issues: Set `elk_verify_ssl: false` for testing (NOT production)
- Firewall: Ensure port 9200 is open between Caldera and ELK
- API key expired: Regenerate with longer expiration

---

### Issue 3: Missing Detection Data
**Symptoms**: PDF generates but detection table is empty

**Diagnosis**:
```bash
# Check if orchestrator has logged data for this operation
curl -X GET "http://your-elk:9200/purple-team-logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "match": {
        "purple.operation_id": "YOUR_OPERATION_UUID"
      }
    },
    "size": 1
  }'
```

**Solutions**:
- Verify orchestrator plugin is enabled and running
- Check operation UUID matches between Caldera and ELK
- Ensure operation executed techniques (not empty adversary)
- Check ELK index pattern: `elk_index: "purple-team-logs-*"` in config
- Verify time range: Orchestrator may have delay in ingestion (wait 30s)

---

### Issue 4: Schema Validation Errors
**Symptoms**: Log shows "ELK schema validation failed - missing required fields"

**Diagnosis**:
```bash
# Check which fields are missing
curl -X GET "http://your-elk:9200/purple-team-logs-*/_mapping" | \
  jq '.[] | .mappings.properties.purple.properties | keys'
```

**Solutions**:
- Update orchestrator plugin to latest version (schema may have changed)
- Manually create index template with required fields:
  ```bash
  curl -X PUT "http://your-elk:9200/_index_template/purple-team-logs" \
    -H 'Content-Type: application/json' \
    -d @plugins/orchestrator/conf/elk_index_template.json
  ```
- Override field mappings in config if orchestrator uses different field names:
  ```yaml
  debrief_elk_detections:
    field_mappings:
      operation_id: "your_custom_field"
      technique: "mitre.technique_id"
      detection_status: "alert.status"
  ```

---

### Issue 5: PDF Generation Timeout
**Symptoms**: Report generation fails with timeout error after 30+ seconds

**Diagnosis**:
```bash
# Check ELK query performance
grep "Query took" logs/caldera.log

# Monitor ELK cluster health
curl "http://your-elk:9200/_cluster/health"
```

**Solutions**:
- Increase timeout: `elk_connection_timeout: 60` in config
- Reduce query scope: `max_techniques_per_query: 50` (default 100)
- Check ELK cluster resources (CPU/memory)
- Add index optimization:
  ```bash
  curl -X POST "http://your-elk:9200/purple-team-logs-*/_forcemerge?max_num_segments=1"
  ```
- Enable query caching in default.yml:
  ```yaml
  cache_detection_data: true
  cache_ttl_minutes: 60
  ```

---

### Issue 6: SSL Certificate Verification Failures
**Symptoms**: "SSL: CERTIFICATE_VERIFY_FAILED" in logs

**Diagnosis**:
```bash
# Test SSL handshake
openssl s_client -connect your-elk:9200 -CAfile /etc/caldera/certs/elk-ca.pem

# Check certificate validity
openssl x509 -in /etc/caldera/certs/elk-ca.pem -text -noout
```

**Solutions**:
- Verify CA certificate is correct: Should match ELK's CA
- Check certificate permissions: `chmod 644 /etc/caldera/certs/elk-ca.pem`
- Hostname mismatch: Ensure `elk_url` uses same hostname as certificate CN
- Self-signed cert: Add to system trust store or disable verification (testing only):
  ```yaml
  elk_verify_ssl: false  # DANGEROUS - only for dev/test!
  ```

---

## Performance Tuning

### For Large Deployments (1000+ techniques per operation)
```yaml
debrief_elk_detections:
  max_techniques_per_query: 500  # Increase from default 100
  elk_connection_timeout: 90     # Increase timeout
  cache_detection_data: true     # Enable caching
  cache_ttl_minutes: 120         # Cache for 2 hours
```

### For High-Frequency Reporting (Multiple concurrent PDF generations)
- Use ELK API key pooling (multiple keys with rate limits)
- Enable Caldera's async workers: `workers: 4` in conf/default.yml
- Add Redis caching layer for detection data

### For Multi-Tenant Environments
- Use separate API keys per tenant/project
- Configure field mapping per tenant:
  ```yaml
  field_mappings:
    operation_id: "tenant1.operation_id"
  ```

---

## Monitoring & Maintenance

### Health Checks
Add to monitoring system (Prometheus, Nagios, etc.):

```bash
# Check ELK connectivity
curl -f http://localhost:8888/api/v2/health/elk || alert

# Check plugin status
grep "debrief-elk-detections plugin enabled" logs/caldera.log || alert

# Check recent report generation
ls -lt /tmp/caldera/reports/*.pdf | head -n 1 | awk '{print $6, $7, $8}'
```

### Log Rotation
```bash
# Add to /etc/logrotate.d/caldera
/path/to/caldera/logs/caldera.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

### API Key Rotation
Schedule quarterly rotation:
```bash
# 1. Generate new API key (see Step 5A)
# 2. Update .env.caldera with new key
# 3. Restart Caldera: systemctl restart caldera
# 4. Revoke old key:
curl -X DELETE "https://your-elk:9200/_security/api_key" \
  -u elastic:password \
  -H "Content-Type: application/json" \
  -d '{"ids": ["old_key_id"]}'
```

---

## Rollback Procedure

If deployment causes issues, rollback with:

```bash
# 1. Stop Caldera
pkill -f server.py

# 2. Disable plugin
vi conf/local.yml
# Remove 'debrief-elk-detections' from plugins list

# 3. Restore original reporting plugin (if backed up)
rm -rf plugins/reporting
cp -r plugins/reporting.backup plugins/reporting

# 4. Restart Caldera
./server.py

# 5. Verify debrief GUI loads without ELK section
```

---

## Production Deployment Checklist

Before going live:

- [ ] ELK API key configured with read-only permissions
- [ ] SSL/TLS enabled with valid certificates
- [ ] `.env.caldera` added to `.gitignore`
- [ ] File permissions set (600 for credentials)
- [ ] Schema validation passing
- [ ] Integration tests successful
- [ ] Performance benchmarks within targets
- [ ] End-to-end operation test completed
- [ ] Monitoring/alerting configured
- [ ] Rollback procedure documented and tested
- [ ] Team trained on new debrief section usage

---

## Support & Troubleshooting

For issues not covered here:

1. **Check Logs**: `tail -f logs/caldera.log | grep -i debrief`
2. **Run Diagnostics**: `bash plugins/debrief-elk-detections/tests/integration_test.sh`
3. **Review Architecture**: See `ARCHITECTURE.md` for system design
4. **GitHub Issues**: https://github.com/mitre/caldera/issues
5. **Slack Community**: Join MITRE Caldera Slack workspace

---

## Additional Resources

- [Caldera Plugin Development Guide](https://caldera.readthedocs.io/en/latest/Plugin-library.html)
- [MITRE Debrief Plugin Docs](https://github.com/mitre/debrief/blob/master/README.md)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Purple Team Logging Best Practices](docs/PURPLE_TEAM_USER_GUIDE.md)
