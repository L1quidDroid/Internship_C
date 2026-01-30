# Triskele Labs Purple Team Environment

A Caldera-based purple team automation platform for MSPs with integrated ELK Stack detection correlation.

## Quick Start

```bash
# Start the full environment (ELK + Caldera)
./scripts/tl-startup.sh

# Check system status
./scripts/tl-status.sh

# Graceful shutdown
./scripts/tl-shutdown.sh
```

## Documentation

- **[User Guide](docs/PURPLE_TEAM_USER_GUIDE.md)** - Complete guide to purple team workflows
- **[Scripts Guide](docs/guides/TL_SCRIPTS_README.md)** - Shell scripts reference
- **[ELK Authentication Setup](docs/deployment/ELK_AUTH_SETUP.md)** - ELK integration configuration
- **[Deployment Guide](docs/deployment/debrief-elk-detections.md)** - Production deployment checklist
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute to this project
- **[Security](docs/SECURITY.md)** - Vulnerability disclosure policy

## Plugin Documentation

- **[Orchestrator Plugin](docs/plugins/orchestrator.md)** - SIEM tagging and correlation
- **[Orchestrator Troubleshooting](docs/plugins/orchestrator-troubleshooting.md)** - Debug guide
- **[Debrief ELK Detections](docs/plugins/debrief-elk-detections.md)** - Detection coverage reporting

## Repository Structure

```
├── app/                        # Main application source code
├── tests/                      # Test suite
├── scripts/                    # Automation scripts (startup, shutdown, status)
├── config/                     # Configuration files (conf, docker, etc.)
├── docs/                       # Documentation
│   ├── guides/                 # User and operational guides
│   ├── deployment/             # Deployment and setup documentation
│   ├── plugins/                # Plugin-specific documentation
│   └── architecture/           # Architecture diagrams and specs (future)
├── plugins/                    # Caldera plugins
├── data/                       # Data storage (abilities, results, etc.)
├── static/                     # Static web assets
├── templates/                  # HTML templates
├── requirements.txt            # Python dependencies
└── server.py                   # Main server entry point
```

## Features

- **Purple Team Automation**: Automated adversary emulation with ATT&CK framework
- **SIEM Integration**: Real-time ELK Stack detection correlation
- **One-Liner Agent Deployment**: Simplified agent enrollment
- **Detection Coverage Reports**: PDF reports with detection gaps
- **Lean Core Architecture**: 7-plugin design optimized for MSPs

## System Requirements

- **Python**: 3.9+
- **Elasticsearch**: 8.11.0+
- **Memory**: 4GB+ RAM recommended
- **OS**: Linux, macOS, Windows (with WSL)

## License

See [LICENSE](LICENSE) for details.

## Support

For questions or issues, refer to:
- [Troubleshooting Guide](docs/plugins/orchestrator-troubleshooting.md)
- [Security Policy](docs/SECURITY.md)
