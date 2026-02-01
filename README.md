# Triskele Labs Purple Team Environment

A Caldera-based purple team automation platform for managed service providers with integrated ELK Stack detection correlation.

## Quick Start

```bash
# Start the full environment (ELK + Caldera)
./scripts/tl-startup.sh

# Check system status
./scripts/tl-status.sh

# Graceful shutdown
./scripts/tl-shutdown.sh
```

Access the web interface at `http://localhost:8888` after startup.

## Documentation

### Getting Started

New to the platform? Start here:

- [Installation Guide](docs/getting-started/installation.md) - System requirements and setup
- [Quick Start Guide](docs/getting-started/quick-start.md) - Get operational in 10 minutes
- [Configuration Reference](docs/getting-started/configuration.md) - Environment and system configuration

### User Guide

Learn how to use the platform effectively:

- [Platform Overview](docs/user-guide/overview.md) - Architecture and core concepts
- [Agent Management](docs/user-guide/agents.md) - Deploy and manage agents across environments
- [Running Operations](docs/user-guide/operations.md) - Execute adversary emulation campaigns
- [Reporting and Analysis](docs/user-guide/reporting.md) - Generate and interpret results

### Technical Reference

For developers and system integrators:

- [System Architecture](docs/architecture/system-overview.md) - Component architecture and data flow
- [API Reference](docs/technical/api-reference.md) - REST API endpoints and authentication
- [Database Schema](docs/technical/database-schema.md) - Data structures and relationships

### Deployment

Production deployment guidance:

- [Local Deployment](docs/deployment/local-deployment.md) - Standalone server installation
- [Docker Deployment](docs/deployment/docker-deployment.md) - Containerised deployment
- [ELK Integration](docs/deployment/elk-integration.md) - SIEM correlation setup
- [Troubleshooting](docs/deployment/troubleshooting.md) - Common deployment issues

### Development

Contributing to the project:

- [Plugin Development](docs/development/plugin-development.md) - Create custom plugins
- [Contributing Guidelines](docs/CONTRIBUTING.md) - How to contribute code
- [Testing Guide](docs/development/testing.md) - Test suite and quality standards

### Reference

Quick access documentation:

- [FAQ](docs/reference/faq.md) - Frequently asked questions
- [Troubleshooting Index](docs/reference/troubleshooting.md) - Common issues and solutions
- [Quick Reference](docs/reference/quick-reference.md) - Command and API cheat sheet

## Features

- **Purple Team Automation** - Automated adversary emulation with MITRE ATT&CK framework
- **SIEM Integration** - Real-time ELK Stack detection correlation and tagging
- **One-Liner Agent Deployment** - Simplified agent enrolment across platforms
- **Detection Coverage Reports** - PDF reports identifying detection gaps
- **Lean Core Architecture** - 7-plugin design optimised for managed service providers

## System Requirements

- **Python** - 3.9 or higher
- **Elasticsearch** - 8.11.0 or higher
- **Memory** - 4GB RAM minimum, 8GB recommended
- **Operating System** - Linux, macOS, Windows with WSL

## Architecture

The platform employs a modular architecture with seven core plugins:

- **Magma** - Vue.js 3 frontend interface
- **Sandcat** - Cross-platform agent (GoLang)
- **Stockpile** - Adversary profiles and abilities library
- **Atomic** - MITRE Atomic Red Team integration
- **Orchestrator** - Automated workflow and SIEM tagging
- **Branding** - Custom theming and visual identity
- **Reporting** - PDF and HTML report generation

For detailed architecture documentation, see [System Architecture](docs/architecture/system-overview.md).

## Repository Structure

```
├── app/                        # Main application source code
│   ├── api/                    # REST API handlers
│   ├── contacts/               # Agent communication protocols
│   ├── objects/                # Core data models
│   ├── planners/               # Operation planning algorithms
│   └── service/                # Business logic services
├── config/                     # Configuration files
│   ├── conf/                   # YAML configuration
│   ├── docker-compose.yml      # Container orchestration
│   └── Dockerfile              # Container image definition
├── data/                       # Runtime data storage
│   ├── abilities/              # Technique definitions
│   ├── adversaries/            # Adversary profiles
│   ├── results/                # Operation results
│   └── sources/                # Fact sources
├── docs/                       # Documentation
│   ├── architecture/           # Architecture specifications
│   ├── deployment/             # Deployment guides
│   ├── development/            # Developer documentation
│   ├── getting-started/        # Beginner guides
│   ├── guides/                 # Operational guides
│   ├── plugins/                # Plugin documentation
│   ├── reference/              # Quick reference materials
│   ├── technical/              # Technical specifications
│   └── user-guide/             # End-user documentation
├── plugins/                    # Caldera plugins
│   ├── atomic/                 # Atomic Red Team integration
│   ├── branding/               # UI customisation
│   ├── debrief/                # Operation analytics
│   ├── magma/                  # Frontend UI
│   ├── orchestrator/           # Workflow automation
│   ├── reporting/              # Report generation
│   ├── sandcat/                # Agent implementation
│   └── stockpile/              # Ability repository
├── scripts/                    # Automation scripts
├── static/                     # Web assets
├── templates/                  # HTML templates
├── tests/                      # Test suite
├── requirements.txt            # Python dependencies
└── server.py                   # Main server entry point
```

## Security

This platform is designed for authorised security testing and purple team operations. Users are responsible for ensuring appropriate authorisation before conducting any testing activities.

For security vulnerability reports, see [Security Policy](docs/SECURITY.md).

## Licence

See [LICENSE](LICENSE) for details.

## Support

For assistance:

- Review the [FAQ](docs/reference/faq.md) for common questions
- Check the [Troubleshooting Guide](docs/reference/troubleshooting.md) for known issues
- Consult the [Security Policy](docs/SECURITY.md) for security-related matters
