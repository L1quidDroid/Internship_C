---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes work completed during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production software guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# System Architecture Overview

## Introduction

This internship project employs a streamlined architecture developed as a learning exercise in security automation. This document outlines the project's core architecture, resource considerations, and key capabilities demonstrated during the internship.

## Prerequisites

- Basic understanding of purple team operations
- Familiarity with security automation concepts
- Access to Triskele Labs Command Center instance

## The 7-Plugin Lean Core

The Triskele Labs Command Center utilises a "Lean Core" architecture consisting of seven essential plugins designed to maximise functionality while minimising resource consumption.

| Plugin | Function | Resource Impact |
|--------|----------|-----------------|
| **Magma** | Vue.js 3 frontend UI | Primary interface |
| **Sandcat** | Cross-platform agent (GoLang) | Lightweight agent deployment |
| **Stockpile** | Adversary profiles & abilities library | Attack playbook repository |
| **Atomic** | Atomic Red Team integration | 796+ pre-built techniques |
| **Orchestrator** | Automated workflow engine | Operation scheduling |
| **Branding** | Custom UI/reporting theming | Visual identity |
| **Reporting** | PDF/HTML report generation | Executive deliverables |

### Architecture Benefits

The lean core approach delivers several key advantages:

- **Resource Efficiency**: Minimal memory footprint enables deployment in constrained environments
- **Focused Functionality**: Each plugin serves a specific, well-defined purpose
- **Reduced Complexity**: Simplified architecture reduces maintenance overhead
- **Improved Reliability**: Fewer components means fewer potential failure points

## Resource Optimisation Strategy

The platform is designed to operate efficiently within resource-constrained environments, maintaining performance with limited system resources.

### Memory Allocation

```
┌─────────────────────────────────────────────────────────┐
│              Memory Allocation Strategy                  │
├─────────────────────────────────────────────────────────┤
│  Caldera Core Server      │  ~1.5 GB                    │
│  Plugin Overhead          │  ~0.5 GB                    │
│  Active Operations        │  ~1.0 GB (variable)         │
│  System Reserve           │  ~1.0 GB                    │
│  ELK Stack (External)     │  Offloaded to separate VM   │
├─────────────────────────────────────────────────────────┤
│  Available Headroom       │  ~3.7 GB                    │
└─────────────────────────────────────────────────────────┘
```

### Key Optimisation Techniques

The platform implements several strategies to maximise performance within resource constraints:

- **Plugin Optimisation**: Non-essential plugins (training, emu, access) are disabled by default
- **Asynchronous Processing**: Operation processing utilises `aiohttp` for non-blocking execution
- **Lazy Loading**: Ability definitions are loaded on-demand rather than pre-loaded
- **External Integration**: SIEM integration eliminates local log storage requirements

### Performance Considerations

When operating the platform, monitor resource usage and adjust operational parameters accordingly:

- Limit concurrent operations to 2-3 for optimal performance
- Schedule resource-intensive operations during off-peak hours
- Regularly review and archive completed operation data
- Utilise external systems (SIEM, reporting storage) to reduce local storage burden

## Platform Capabilities

### Purple Team Automation

The platform provides comprehensive purple team automation capabilities:

- **Agent Deployment**: Streamlined agent deployment across multiple platforms
- **Attack Simulation**: Automated execution of adversary techniques
- **Detection Validation**: Verify security control effectiveness
- **Reporting**: Generate executive-ready reports with customised branding

### Integration Architecture

The platform integrates with enterprise security infrastructure:

- **SIEM Integration**: Automated tagging and correlation with security events
- **API-Driven Control**: RESTful API for programmatic operation management
- **External Tool Support**: Compatible with RMM tools, orchestration platforms, and security frameworks

### Scalability Model

The platform scales through distributed architecture:

- **Lightweight Agents**: Minimal footprint on target systems
- **Centralised Control**: Single command center manages multiple agents
- **External Processing**: Offload resource-intensive tasks to dedicated infrastructure
- **Horizontal Scaling**: Deploy additional agent handlers as needed

## Next Steps

- [Deploy and manage agents](agents.md)
- [Create and execute operations](operations.md)
- [Generate branded reports](reporting.md)

## See Also

- [Configuration Guide](../getting-started/configuration.md)
- [Plugin Architecture](../architecture/plugins.md)
- [API Reference](../reference/api.md)
