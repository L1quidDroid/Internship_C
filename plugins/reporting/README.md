# Reporting Plugin

Automated PDF report generation for MITRE Caldera purple team operations.

## Overview

The Reporting plugin automatically generates professional PDF reports when Caldera operations complete. Reports include executive summaries, MITRE ATT&CK technique coverage, tactic analysis, and detailed execution results.

**Key Features:**
- 🔄 **Automatic Report Generation** - Triggered on operation completion
- 📊 **Executive Summaries** - Success metrics and statistics
- 🎨 **Triskele Labs Branding** - Custom colors and logo
- ⚡ **Memory Optimized** - <100MB overhead, suitable for constrained environments
- ⏱️ **Timeout Protection** - Configurable generation timeouts
- 🔧 **REST API** - Manual report generation and listing

---

## Quick Start

### 1. Install Dependencies

```bash
pip install reportlab
```

### 2. Configure Plugin

Add to `conf/local.yml`:

```yaml
reporting:
  output_dir: plugins/reporting/data/reports
  page_size: LETTER
  font_name: Helvetica
  font_size: 10
  max_workers: 3
  generation_timeout: 30
  max_memory_mb: 100
  company_name: Triskele Labs
  logo_path: plugins/reporting/static/assets/triskele_logo.png
  primary_color: '#0f3460'
  accent_color: '#16a085'
  text_color: '#1F2937'
  include_executive_summary: true
  include_tactic_coverage: true
  include_technique_details: true
```

### 3. Enable Plugin

Add to `conf/local.yml`:

```yaml
plugins:
  - reporting
```

### 4. Start Caldera

```bash
python server.py --insecure
```

Reports are automatically generated in `plugins/reporting/data/reports/` when operations finish.

---

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | string | `plugins/reporting/data/reports` | Directory for generated PDFs |
| `page_size` | string | `LETTER` | PDF page size (LETTER, A4, LEGAL) |
| `font_name` | string | `Helvetica` | Base font family |
| `font_size` | int | `10` | Base font size (8-14) |
| `max_workers` | int | `3` | ThreadPoolExecutor workers (1-10) |
| `generation_timeout` | int | `30` | PDF generation timeout in seconds (5-300) |
| `max_memory_mb` | int | `100` | Maximum memory overhead (50-500) |
| `company_name` | string | `Triskele Labs` | Company name for branding |
| `logo_path` | string | `plugins/reporting/static/assets/triskele_logo.png` | Path to company logo |
| `primary_color` | string | `#0f3460` | Primary brand color (hex) |
| `accent_color` | string | `#16a085` | Accent brand color (hex) |
| `text_color` | string | `#1F2937` | Text color (hex) |
| `include_executive_summary` | bool | `true` | Include executive summary section |
| `include_tactic_coverage` | bool | `true` | Include MITRE ATT&CK tactic analysis |
| `include_technique_details` | bool | `true` | Include detailed technique table |

---

## REST API

### Generate Report Manually

```bash
POST /api/v2/reports/generate
Content-Type: application/json

{
  "operation_id": "op-123-456"
}
```

**Response:**
```json
{
  "status": "success",
  "operation_id": "op-123-456",
  "report_path": "plugins/reporting/data/reports/report_op-123-456_20250103_143022.pdf"
}
```

### List Generated Reports

```bash
GET /api/v2/reports/list
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "reports": [
    {
      "filename": "report_op-123-456_20250103_143022.pdf",
      "path": "plugins/reporting/data/reports/report_op-123-456_20250103_143022.pdf",
      "size": 125440,
      "created": 1704297022.5
    }
  ]
}
```

---

## Architecture

```
plugins/reporting/
├── __init__.py              # Plugin metadata
├── hook.py                  # Caldera plugin registration
├── app/
│   ├── config.py            # Configuration loader
│   ├── pdf_generator.py     # Core PDF generation logic
│   └── report_svc.py        # Service layer (event handling)
├── tests/
│   ├── fixtures.py          # Test fixtures (mock operations)
│   └── test_pdf_generator.py  # Unit tests (22 tests)
├── static/assets/           # Logo and branding assets
└── data/reports/            # Generated PDF reports
```

### Event Flow

1. **Operation Completes** → Caldera fires `operation.completed` event
2. **Event Handler** → `report_svc.on_operation_completed()` receives event
3. **Data Fetch** → Service fetches operation from `data_svc`
4. **PDF Generation** → `pdf_generator.generate()` creates PDF in thread pool
5. **Storage** → PDF saved to `output_dir` with timestamp

---

## Report Contents

### 1. Header
- Triskele Labs logo (120x40px)
- Operation name and title

### 2. Metadata Table
- Operation ID, group, state
- Start/end times and duration
- Adversary, planner, jitter settings

### 3. Executive Summary
- Total techniques executed
- Success/failure/timeout rates
- Key statistics table

### 4. Tactic Coverage
- MITRE ATT&CK tactics covered
- Technique count per tactic
- Coverage percentages

### 5. Technique Details
- Technique ID and name
- Tactic category
- Execution status (✓/✗/⏱)

### 6. Footer
- Company name
- Generation timestamp

---

## Performance Benchmarks

| Operation Size | Techniques | Generation Time | Memory Usage | PDF Size |
|----------------|------------|-----------------|--------------|----------|
| Small | 1-5 | <2s | ~50MB | ~20KB |
| Medium | 6-15 | <3s | ~60MB | ~40KB |
| Large | 16-30 | <5s | ~80MB | ~80KB |
| Extra Large | 31-50 | <8s | ~95MB | ~120KB |

**Test Environment:** 8GB RAM VM, Python 3.10, Ubuntu 22.04

---

## Testing

### Run Unit Tests

```bash
cd /Users/tonyto/Documents/GitHub/Triskele\ Labs/Internship_C
python3 -m pytest plugins/reporting/tests/test_pdf_generator.py -v
```

**Expected Output:**
```
======= 22 passed in 2.45s =======
```

### Test Coverage

- ✅ Configuration validation
- ✅ PDF header building
- ✅ Metadata table generation
- ✅ Executive summary calculation
- ✅ Technique table rendering
- ✅ Tactic coverage analysis
- ✅ Async generation with timeout
- ✅ Memory management (gc.collect)
- ✅ Error handling and graceful degradation
- ✅ Division-by-zero protection

---

## Troubleshooting

### PDF Not Generated

**Symptom:** Operation completes but no PDF created

**Solutions:**
1. Check logs: `tail -f logs/caldera.log | grep reporting`
2. Verify output directory permissions: `ls -la plugins/reporting/data/reports/`
3. Confirm operation state is `finished`: Check operation in Caldera UI
4. Check event subscription: Look for "subscribed to operation.completed" in logs

### Generation Timeout

**Symptom:** `PDF generation timed out after 30s`

**Solutions:**
1. Increase timeout: Set `generation_timeout: 60` in config
2. Reduce workers: Set `max_workers: 2` (less CPU contention)
3. Check system load: `top` or `htop`

### Memory Issues

**Symptom:** OOM errors or excessive memory usage

**Solutions:**
1. Reduce max_memory_mb: Set `max_memory_mb: 50`
2. Reduce max_workers: Set `max_workers: 2`
3. Disable optional sections: Set `include_technique_details: false`

### Logo Not Displaying

**Symptom:** PDF header missing logo

**Solutions:**
1. Verify logo exists: `ls plugins/reporting/static/assets/triskele_logo.png`
2. Check file format: Must be PNG (120x40px recommended)
3. Verify path in config: Ensure `logo_path` is correct

### REST API 404

**Symptom:** `/api/v2/reports/generate` returns 404

**Solutions:**
1. Confirm plugin enabled: Check `conf/local.yml` plugins list
2. Check aiohttp import: Verify `from aiohttp import web` succeeds
3. Review startup logs: Look for "REST API endpoints registered"

---

## Security Considerations

- ✅ **No User Input in PDFs** - All data from trusted Caldera operations
- ✅ **Output Directory Validation** - Write permissions checked on startup
- ✅ **Timeout Protection** - Prevents DoS via slow PDF generation
- ✅ **Memory Limits** - Configurable overhead prevents resource exhaustion
- ✅ **Error Logging** - Exceptions logged but not exposed to users

---

## Roadmap

### v1.1 (Future)
- [ ] Custom report templates (YAML-based)
- [ ] Multi-format export (HTML, Markdown, JSON)
- [ ] Email delivery integration
- [ ] Report scheduling (daily/weekly summaries)
- [ ] Technique timeline visualization

### v1.2 (Future)
- [ ] Comparison reports (multiple operations)
- [ ] Trend analysis across time
- [ ] Custom branding per client
- [ ] Digital signatures for report integrity

---

## Contributing

Report issues or suggest features at: https://github.com/L1quidDroid/Internship_C/issues

---

## License

Same as MITRE Caldera (Apache 2.0)

---

## Acknowledgments

- **MITRE Caldera Team** - Event system architecture
- **ReportLab** - PDF generation library
- **Triskele Labs** - Purple team automation vision

---

**Version:** 1.0.0  
**Author:** Tony To  
**Last Updated:** January 3, 2025
