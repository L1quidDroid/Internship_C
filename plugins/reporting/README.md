# Reporting Plugin

Automated PDF report generation for MITRE Caldera purple team operations.

## Features

- **Auto-generation**: Reports generated automatically when operations complete
- **ELK Integration**: Detection coverage correlation from `purple-team-logs-*` index
- **Professional PDFs**: Triskele Labs branded reports with ATT&CK analysis
- **Performance**: <8s generation for 30-technique operations

## Installation

```bash
# Install dependencies
pip install -r plugins/reporting/requirements.txt

# Ensure plugin is enabled in conf/local.yml
plugins:
  - reporting
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/plugin/reporting/generate` | Generate PDF for operation |
| GET | `/plugin/reporting/list` | List all generated reports |
| GET | `/plugin/reporting/download/{op_id}` | Download PDF by operation ID |

### Generate Report

```bash
curl -X POST http://localhost:8888/plugin/reporting/generate \
  -H "Content-Type: application/json" \
  -d '{"operation_id": "abc-123-def-456"}'
```

**Response:**
```json
{
  "success": true,
  "pdf_path": "plugins/reporting/data/reports/report_abc-123_20260108_143045.pdf",
  "generation_time_ms": 4230,
  "pdf_size_kb": 42.5
}
```

### List Reports

```bash
curl http://localhost:8888/plugin/reporting/list
```

### Download Report

```bash
curl -O http://localhost:8888/plugin/reporting/download/abc-123-def-456
```

## Configuration

Add to `conf/local.yml`:

```yaml
reporting:
  output_dir: "plugins/reporting/data/reports"
  max_workers: 3
  generation_timeout: 30
  company_name: "Triskele Labs"
  logo_path: "plugins/reporting/static/assets/triskele_logo.png"
  
  # Report content options
  include_executive_summary: true
  include_tactic_coverage: true
  include_technique_details: true
  
  # Page settings
  page_size: "LETTER"  # LETTER, A4, LEGAL
  font_size: 10
  
  # Branding colors
  primary_color: "#0f3460"
  accent_color: "#16a085"
  text_color: "#2c3e50"
```

## PDF Contents

1. **Header** - Logo and operation title
2. **Metadata Table** - Operation ID, group, duration, adversary, planner
3. **Executive Summary** - Success/failure percentages, technique count
4. **Tactic Coverage** - MITRE ATT&CK kill chain analysis
5. **Detection Coverage** - ELK correlation results (detected/evaded/pending)
6. **Technique Details** - Full technique execution table

## ELK Integration

The reporting plugin integrates with the orchestrator plugin's ELK configuration to fetch detection data:

```yaml
# Uses orchestrator's ELK settings from conf/local.yml
plugins:
  orchestrator:
    elk_url: "http://20.28.49.97:9200"
    elk_user: "elastic"
    elk_pass: "your-password"
```

Queries `purple-team-logs-*` index for:
- `purple.operation_id` matching the Caldera operation
- `purple.detection_status` (detected/evaded/pending)
- `purple.technique` for per-technique breakdown

## Auto-Generation

Reports are automatically generated when operations complete:

1. Operation finishes (state = `finished`)
2. Event system triggers `on_operation_completed`
3. ELK detection data fetched (if available)
4. PDF generated and saved to `output_dir`
5. Logs show efficiency metrics

**Performance Target:** <8.5s total (event → PDF)

## File Structure

```
plugins/reporting/
├── hook.py                 # Plugin registration
├── requirements.txt        # Dependencies
├── README.md              # This file
├── __init__.py            # Package metadata
├── app/
│   ├── report_svc.py      # Main service (API handlers)
│   ├── pdf_generator.py   # ReportLab PDF generation
│   ├── elk_fetcher.py     # ELK detection correlation
│   └── config.py          # Configuration loader
├── static/
│   └── assets/
│       └── triskele_logo.png
├── data/
│   └── reports/           # Generated PDFs
└── tests/
    ├── test_pdf_generator.py
    ├── fixtures.py
    └── test_integration.sh
```

## Testing

```bash
# Unit tests
pytest plugins/reporting/tests/

# Integration test (requires running Caldera)
bash plugins/reporting/tests/test_integration.sh

# Manual API test
curl -X POST http://localhost:8888/plugin/reporting/generate \
  -d '{"operation_id": "your-operation-id"}'
```

## Troubleshooting

### Report not generating
- Check operation state is `finished`
- Verify `plugins/reporting/data/reports/` directory exists
- Check Caldera logs for `[reporting]` errors

### Detection data unavailable
- ELK connection failed (check network/auth)
- Reports still generate with "Detection correlation unavailable" placeholder
- Verify orchestrator plugin ELK config is correct

### Performance issues
- Generation >8s usually means large operation (>100 techniques)
- Check `max_workers` setting
- Monitor memory usage (target: <100MB per report)
