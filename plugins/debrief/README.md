# Debrief Plugin

A Caldera plugin for gathering overall campaign information and analytics for operations.

## Overview

The Debrief Plugin provides comprehensive post-operation analysis and reporting capabilities for MITRE Caldera. It offers centralised views of operation metadata, graphical displays of operations, techniques and tactics used, and facts discovered during operations. The plugin supports export of campaign information and analytics in PDF format.

### Features

- **Operation Analytics**: Comprehensive view of operation metadata and results
- **Graphical Displays**: Visual representations of attack paths, tactics, and facts
- **PDF Export**: Professional PDF reports for operations
- **Technique Analysis**: Detailed breakdown of techniques and tactics used
- **Facts Discovery**: Visualisation of facts discovered during operations

## Prerequisites

```bash
# Required
- Python 3.10+
- Caldera 5.x
- ReportLab (PDF generation)

# Optional
- Additional debrief section plugins (e.g., debrief-elk-detections)
```

## Installation

```bash
# 1. Plugin is already in plugins/debrief/

# 2. Enable plugin in conf/local.yml
plugins:
  - debrief

# 3. Start Caldera
python server.py --insecure

# 4. Verify plugin loaded
grep "debrief" logs/caldera.log
```

## Configuration

```yaml
# conf/local.yml
plugins:
  - debrief
```

## Usage

### Accessing Debrief Interface

1. Navigate to `/plugin/debrief/gui` in your browser
2. Select operation(s) to analyse
3. View operation overview, attack paths, and analytics
4. Download PDF report if needed

### PDF Report Generation

1. Select completed operation(s)
2. Click "Download PDF" button
3. PDF includes:
   - Operation overview
   - Attack path graph
   - Tactics graph
   - Steps table
   - Tactics and techniques table
   - Facts graph

### Example Report

An example generated PDF for an operation with both successful and unsuccessful steps can be found in the plugin documentation.

## Report Sections

The debrief interface and PDF reports include:

- **Operation Overview**: Metadata, duration, success rates
- **Attack Path Graph**: Visual representation of attack execution flow
- **Tactics Graph**: Distribution of tactics used
- **Steps Table**: Detailed step-by-step execution log
- **Tactics and Techniques Table**: ATT&CK framework mapping
- **Facts Graph**: Discovered facts and relationships

## Extensibility

The debrief plugin supports additional sections through other plugins. Sections in `app/debrief-sections/` across all enabled plugins are automatically discovered and included in reports.

## File Structure

```
plugins/debrief/
├── hook.py                 # Plugin registration
├── README.md              # This file
├── __init__.py            # Package metadata
├── app/
│   └── [debrief-services] # Debrief logic and PDF generation
├── docs/
│   └── [example-reports]  # Example generated reports
└── static/
    └── [ui-assets]        # Web interface assets
```

## Troubleshooting

### Debrief Interface Not Loading

**Symptom**: Cannot access debrief GUI

**Fix**:
- Verify plugin is enabled in conf/local.yml
- Check Caldera logs for errors
- Ensure browser JavaScript is enabled
- Try clearing browser cache

### PDF Generation Fails

**Symptom**: PDF download returns error

**Fix**:
- Verify operation has completed
- Check ReportLab is installed
- Review logs for specific error messages
- Ensure sufficient disk space for PDF output

### Graphs Not Displaying

**Symptom**: Visualisations not rendering

**Fix**:
- Check browser console for JavaScript errors
- Verify operation has execution data
- Ensure required data fields are populated
- Try refreshing the page

## Performance

| Metric | Consideration |
|--------|---------------|
| PDF Generation | Varies by operation size |
| Graph Rendering | Depends on operation complexity |
| Data Loading | Optimised for typical operations |

## Contributing

Contributions for additional debrief sections and visualisations are welcome. Contact your Caldera administrator for enhancement requests.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Acknowledgements

- **MITRE Caldera Team**: For the excellent framework
- **Community Contributors**: For ongoing enhancements
