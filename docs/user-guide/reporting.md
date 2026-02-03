---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes work completed during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production software guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Report Generation and Customisation

## Introduction

This guide covers the generation of branded assessment reports developed during this internship project. The custom reporting plugin demonstrates PDF generation capabilities for educational purposes.

## Prerequisites

- Completed operation with `finished` state
- Branding plugin configured (installed by default)
- Access to reporting interface
- Understanding of report format requirements

## Report Generation Overview

### Available Report Formats

The reporting system supports multiple output formats for different use cases:

| Format | Use Case | Characteristics |
|--------|----------|-----------------|
| PDF | Executive presentation | Professional layout, embedded branding |
| JSON | Data integration | Machine-readable, programmatic access |
| HTML | Web embedding | Interactive, browser-based viewing |

### Report Content

Generated reports include:

- **Executive Summary**: High-level findings and metrics
- **Operation Details**: Configuration and scope information
- **Technique Results**: Detailed execution outcomes
- **MITRE ATT&CK Mapping**: Technique coverage matrix
- **Recommendations**: Security improvement guidance
- **Appendices**: Technical details and evidence (optional)

## Step-by-Step Report Generation

### Step 1: Verify Operation Completion

Ensure the operation has completed execution before generating reports.

#### Via Web Interface

Navigate to **Campaigns → Operations** and verify operation state shows `finished`.

#### Via API

```bash
curl http://localhost:8888/api/v2/operations/<OP_ID> | jq '.state'
# Expected output: "finished"
```

**Note**: Reports can be generated for running operations, but results will be incomplete.

### Step 2: Access Reporting Interface

Navigate to the operations management interface:

```
http://localhost:8888/operations
```

Locate the completed operation in the operations list.

### Step 3: Initiate Report Generation

Select the target operation and choose **"Generate Report"** from the available actions.

### Step 4: Configure Report Options

Select report format and optional content inclusion:

#### Report Format Selection

Choose the appropriate format for your use case:

- **PDF**: For client deliverables and executive presentations
- **JSON**: For integration with other systems or custom processing
- **HTML**: For web-based review or embedding in portals

#### Content Options

Configure optional report elements:

- **Include Facts**: Incorporate discovered facts and intelligence
- **Include Screenshots**: Embed technique execution screenshots (increases file size)
- **Include Raw Output**: Append raw technique output (technical detail)
- **Redact Sensitive Data**: Automatically remove IP addresses and hostnames

### Step 5: Download Generated Report

After generation completes, download the report file. Reports are named using the convention:

```
PURPLE_TEAM_REPORT_<OPERATION_NAME>_<DATE>.<FORMAT>
```

## Report API Endpoint

Generate reports programmatically using the REST API.

### PDF Report Generation

```bash
# Generate PDF report
curl -X POST http://localhost:8888/api/v2/reports \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "pdf",
    "include_facts": true,
    "include_screenshots": false
  }' \
  --output "PURPLE_TEAM_REPORT.pdf"
```

### JSON Report Generation

```bash
# Generate JSON report
curl -X POST http://localhost:8888/api/v2/reports \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "<OP_ID>",
    "format": "json",
    "include_facts": true
  }' \
  | jq '.' > report.json
```

### Batch Report Generation

Generate reports for multiple operations:

```bash
# Generate reports for all completed operations
for op_id in $(curl -s http://localhost:8888/api/v2/operations | jq -r '.[] | select(.state=="finished") | .id'); do
  curl -X POST http://localhost:8888/api/v2/reports \
    -H "Content-Type: application/json" \
    -d "{\"operation_id\": \"$op_id\", \"format\": \"pdf\"}" \
    --output "report_${op_id}.pdf"
done
```

## Branding Configuration

The Branding plugin automatically applies customised visual identity to generated reports.

### Automatic Branding Elements

The following branding elements are applied automatically:

- **Header**: Triskele Labs logo (SVG format)
- **Colour Scheme**: Triskele Green (#10B981) accents throughout document
- **Footer**: Copyright notice and website link
- **Watermark**: "CONFIDENTIAL - CLIENT NAME" overlay
- **Typography**: Consistent font hierarchy and styling

### Custom Branding Configuration

Customise branding elements for specific clients or engagements by modifying the branding plugin configuration.

#### Logo Customisation

Replace the default logo by updating the branding configuration:

1. Navigate to plugin configuration: `plugins/branding/conf/config.yml`
2. Update logo path:

```yaml
branding:
  logo:
    path: /path/to/custom/logo.svg
    height: 60px
    width: auto
```

#### Colour Scheme Customisation

Modify colour scheme for client-specific branding:

```yaml
branding:
  colours:
    primary: "#10B981"      # Triskele Green
    secondary: "#1F2937"    # Dark Grey
    accent: "#3B82F6"       # Blue
    background: "#FFFFFF"   # White
    text: "#111827"         # Near Black
```

#### Watermark Configuration

Configure client-specific watermarks:

```yaml
branding:
  watermark:
    enabled: true
    text: "CONFIDENTIAL - {client_name}"
    opacity: 0.1
    colour: "#9CA3AF"
```

## Triskele Design System

Reports utilise the Triskele design system for consistent, professional presentation.

### Report Structure

```
┌────────────────────────────────────────────────────────────┐
│  ⟨ ⟩  TRISKELE LABS                                       │
│       Purple Team Assessment Report                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Client: ACME Corporation                                  │
│  Assessment Date: January 2026                             │
│  Classification: CONFIDENTIAL                              │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  EXECUTIVE SUMMARY                                         │
│  ══════════════════                                        │
│  Techniques Executed: 34                                   │
│  Successful: 31 (91%)                                      │
│  Blocked: 3 (9%)                                           │
│                                                            │
│  [████████████████████░░] 91% Success Rate                │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  © Triskele Labs | https://triskelelabs.com               │
└────────────────────────────────────────────────────────────┘
```

### Design Principles

The Triskele design system emphasises:

- **Clarity**: Information hierarchy supports quick comprehension
- **Consistency**: Uniform styling across all report elements
- **Professionalism**: Executive-appropriate presentation
- **Accessibility**: High contrast ratios and readable typography
- **Brand Alignment**: Visual identity reflects Triskele Labs brand

### Typography Standards

Report typography follows consistent hierarchy:

- **Headings**: Bold, clear hierarchy (H1-H4)
- **Body Text**: Readable font size (11-12pt)
- **Code Blocks**: Monospace font for technical content
- **Captions**: Smaller text for supplementary information

### Colour Usage

Colours are applied strategically throughout reports:

- **Triskele Green (#10B981)**: Success indicators, highlights, section accents
- **Red (#EF4444)**: Failed techniques, high-severity findings
- **Yellow (#F59E0B)**: Warnings, medium-severity findings
- **Blue (#3B82F6)**: Information callouts, neutral indicators
- **Grey Scale**: Text hierarchy, backgrounds, borders

## Report Content Customisation

### Executive Summary Customisation

Tailor executive summary content for specific audiences:

```python
# Example: Custom executive summary generation
from plugins.reporting.app.report_generator import ReportGenerator

generator = ReportGenerator()
generator.set_executive_summary_template({
    "title": "Purple Team Assessment - {client_name}",
    "sections": [
        "overview",
        "key_findings",
        "risk_rating",
        "recommendations"
    ],
    "focus": "executive"  # or "technical"
})
```

### Section Inclusion

Control which report sections are included:

```yaml
report:
  sections:
    - executive_summary
    - operation_details
    - technique_results
    - mitre_coverage
    - recommendations
    - technical_appendix  # optional
    - evidence_appendix   # optional
```

### Recommendations Customisation

Customise security recommendations based on findings:

- **Automated Recommendations**: Generated based on failed/blocked techniques
- **Manual Recommendations**: Added through reporting interface or API
- **Priority Ranking**: High/Medium/Low severity classification
- **Implementation Guidance**: Actionable steps for remediation

## Report Distribution

### Secure Distribution

Implement secure distribution practices:

- **Encryption**: Encrypt PDF reports with password protection
- **Secure Transfer**: Utilise secure file transfer methods (SFTP, encrypted email)
- **Access Control**: Restrict report access to authorised personnel
- **Retention Policy**: Define report retention and disposal procedures

### Automated Distribution

Configure automated report distribution:

```python
# Example: Automated report distribution
async def distribute_report(operation_id, recipients):
    # Generate report
    report = await generate_report(operation_id, format="pdf")
    
    # Encrypt report
    encrypted_report = encrypt_pdf(report, password=generate_password())
    
    # Distribute via secure channel
    for recipient in recipients:
        await send_secure_email(
            to=recipient,
            subject=f"Purple Team Assessment Report - {operation_id}",
            attachment=encrypted_report,
            password_hint="Contact SOC for decryption password"
        )
```

## Report Quality Assurance

### Pre-Distribution Checklist

Verify report quality before distribution:

- [ ] All operation data accurately represented
- [ ] Client-specific branding applied correctly
- [ ] Sensitive data redacted as appropriate
- [ ] Technical accuracy reviewed
- [ ] Grammar and spelling checked
- [ ] Visual formatting consistent
- [ ] File size appropriate for distribution method

### Common Quality Issues

Address common report quality issues:

- **Missing Data**: Ensure operation completed successfully before report generation
- **Branding Inconsistency**: Verify branding plugin configuration
- **Large File Size**: Exclude screenshots or compress images
- **Formatting Problems**: Review HTML/CSS templates for errors

## Troubleshooting

### PDF Report Empty or Incomplete

**Possible Causes**:
- Operation has no executed techniques
- Report generation failed mid-process
- Template configuration error

**Resolution**:
1. Verify operation contains executed links: `curl http://localhost:8888/api/v2/operations/<OP_ID>/links`
2. Check server logs for report generation errors
3. Review report template configuration

### Branding Not Applied

**Possible Causes**:
- Branding plugin not loaded
- Configuration file errors
- Asset files missing

**Resolution**:
1. Verify branding plugin is enabled in configuration
2. Check branding configuration file syntax
3. Confirm logo and asset files exist at configured paths

### Report Generation Timeout

**Possible Causes**:
- Large operation data set
- System resource constraints
- Network issues with external resources

**Resolution**:
1. Reduce report content by excluding screenshots/raw output
2. Generate during low-usage periods
3. Increase report generation timeout in configuration

## Next Steps

- [Configure custom branding](../guides/branding-customisation.md)
- [Advanced report templates](../guides/report-templates.md)
- [Report automation workflows](../guides/automation.md)

## See Also

- [Operations Management](operations.md)
- [Branding Plugin Documentation](../plugins/branding.md)
- [API Reference - Reports](../reference/api.md#reports)
- [Design System Guidelines](../reference/design-system.md)
