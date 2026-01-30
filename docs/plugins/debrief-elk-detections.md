# Debrief ELK Detection Coverage Plugin

Adds SIEM detection correlation to MITRE Caldera Debrief reports, providing purple-team validation of detection coverage.

## Features

- **Per-technique detection status**: Shows which techniques were detected, evaded, or pending
- **ELK integration**: Queries `purple-team-logs-*` Elasticsearch index
- **Color-coded PDF tables**: Visual representation of detection coverage
- **Multi-operation support**: Aggregates detections across selected operations
- **Graceful degradation**: Reports generate even if ELK unavailable

## Installation

```bash
# Plugin dependencies already included in main requirements.txt
# Ensure elasticsearch>=8.0.0 is installed

# Enable plugin in conf/local.yml
plugins:
  - debrief
  - debrief-elk-detections
```

## Configuration

Configure ELK connection in `conf/local.yml` (overrides `conf/default.yml`):

```yaml
debrief_elk_detections:
  # ELK connection (falls back to orchestrator config if not specified)
  elk_url: "${ELK_URL}"
  elk_user: "${ELK_USER}"
  elk_pass: "${ELK_PASSWORD}"
  
  # Detection thresholds
  min_alert_count: 1
  pending_timeout_hours: 24
  
  # Branding
  company_name: "Triskele Labs"
```

### Production SSL/TLS Configuration

For production deployments, **always enable SSL/TLS** for ELK connections:

```yaml
debrief_elk_detections:
  elk_url: "https://your-elk.domain.com:9200"  # Use HTTPS
  elk_verify_ssl: true  # Enable certificate verification
  elk_ca_cert: "/etc/caldera/certs/elk-ca.pem"  # Path to CA certificate
  
  # Use API key authentication (recommended over user/pass)
  elk_api_key: "${ELK_API_KEY}"  # Read-only API key
```

**Generate read-only API key in Elasticsearch:**
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
    }
  }'
```

## Usage

1. **Enable plugins**: Add `debrief` and `debrief-elk-detections` to `conf/local.yml`
2. **Run operations**: Execute Caldera operations with orchestrator plugin active
3. **Generate report**:
   - Navigate to `/plugin/debrief/gui`
   - Select operation(s)
   - Check "ELK Detection Coverage" section
   - Click "Download PDF"

## ELK Schema Requirements

The plugin queries Elasticsearch for these fields:

- `purple.operation_id` (keyword) - Caldera operation UUID
- `purple.technique` (keyword) - MITRE ATT&CK technique ID (T1234)
- `purple.detection_status` (keyword) - detected/evaded/pending
- `rule.name` (keyword) - SIEM detection rule name

These fields are automatically populated by the orchestrator plugin during operation execution.

## Report Output

The detection coverage section includes:

- **Detection Table**: Technique | Name | Status | Rule Triggered | Alert Count
- **Summary Statistics**: Overall detection percentage, evaded/pending counts
- **Color Coding**:
  - 🟢 Green: Technique detected
  - 🔴 Red: Technique evaded detection
  - 🟠 Orange: Pending analysis (no alerts yet)

## Troubleshooting

### Section not appearing in debrief GUI

- Verify plugin enabled in `conf/local.yml`
- Check Caldera logs for plugin loading errors
- Restart Caldera: `python server.py --insecure`

### "Detection correlation unavailable" message

- Verify ELK connection settings in `conf/local.yml`
- Test ELK connectivity: `curl http://your-elk:9200`
- Check orchestrator plugin is enabled and configured
- Review Caldera logs for ELK connection errors

### Empty detection data

- Ensure operations have `purple.*` fields in ELK
- Verify orchestrator plugin tagged operation in ELK
- Check ELK index exists: `purple-team-logs-*`
- Confirm operation UUIDs match between Caldera and ELK

## Architecture

```
plugins/debrief-elk-detections/
├── hook.py                          # Plugin registration
├── conf/
│   └── default.yml                  # Configuration
├── app/
│   ├── elk_fetcher.py              # ELK query logic
│   └── debrief-sections/
│       └── elk_detection_coverage.py  # Report section (auto-discovered)
└── README.md
```

The debrief plugin automatically discovers sections in `app/debrief-sections/` across all enabled plugins.

## Security Considerations

- **Credentials**: Use environment variables for ELK passwords
- **SSL/TLS**: Enable `elk_verify_ssl: true` for production
- **Read-only access**: Use dedicated ELK API key with minimal permissions
- **Input validation**: Operation IDs validated before ELK queries

## Performance

- **Target**: <3s ELK query for 30-technique operations
- **Caching**: Configurable (default: disabled)
- **Max techniques**: 100 per query (configurable)

## Contributing

Developed by Triskele Labs for purple-team engagements. For issues or enhancements, contact your Caldera administrator.

## License

Follows MITRE Caldera licensing (Apache 2.0)
