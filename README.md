# Purple Team Automation - Internship Project

**Internship Portoflio Project** 
*Tony To | Triskele Labs Internship (January-February 2026)*

[![Status](https://img.shields.io/badge/Status-Educational%20Project-blue)]() [![License](https://img.shields.io/badge/License-Educational%20Portfolio-green)]()

---

## ⚠️ Project Disclaimer

**This is an internship learning project, NOT production software.**

- **Purpose**: Demonstrate software development and detection engineering skills
- **Context**: Educational exercise completed during Triskele Labs internship
- **Status**: Portfolio proof-of-concept showcasing technical capabilities
- **NOT**: Production-ready, officially supported, or intended for operational deployment

**Author**: Tony To (Detection Engineering & Automation Intern)  
**Organisation**: Triskele Labs (Internship Programme)  
**Timeline**: January-February 2026

See [INTERNSHIP_DISCLAIMER.md](INTERNSHIP_DISCLAIMER.md) for complete legal information.

---

## Project Overview

During my internship at Triskele Labs, I developed custom Caldera plugins to demonstrate software development capabilities and detection engineering concepts learned throughout the programme.

### Software Development Skills Demonstrated

**Backend Development**:
- Python async/await patterns for concurrent operations
- Event-driven architecture with pub/sub messaging
- RESTful API design and implementation
- Database integration (object store, fact store)
- Error handling and graceful degradation patterns

**Frontend Integration**:
- Vue.js 3 component development
- Single Page Application (SPA) architecture
- REST API consumption and state management
- Responsive UI design

**DevOps & Infrastructure**:
- Docker containerisation and orchestration
- Environment configuration management
- CI/CD pipeline integration
- System monitoring and logging

### Detection Engineering Concepts Learned

**SIEM Integration**:
- Elasticsearch Query DSL for threat hunting
- Real-time event correlation and tagging
- Detection coverage gap analysis
- Alert enrichment and contextualisation

**Purple Team Methodologies**:
- MITRE ATT&CK framework mapping
- Adversary emulation planning and execution
- Detection validation through controlled testing
- Coverage analysis and reporting

**Security Automation**:
- Automated detection tagging in SIEM
- Detection coverage reporting
- Event-driven security workflows
- Sanitisation and input validation

### Custom Plugins Built

1. **Orchestrator Plugin**: Event-driven SIEM tagging system
   - Automatic Elasticsearch integration
   - Operation lifecycle tracking
   - Circuit breaker patterns for resilience
   - Fallback logging mechanisms

2. **Reporting Plugin**: Detection coverage analysis
   - PDF generation with ReportLab
   - ELK detection correlation
   - Visual coverage gap identification
   - Multi-operation aggregation

3. **Branding Plugin**: UI customisation framework
   - Theme management system
   - Dynamic branding injection
   - Asset management

4. **Debrief-ELK Plugin**: SIEM detection validation
   - Per-technique detection status
   - Color-coded coverage visualisation
   - Graceful degradation when SIEM unavailable

---

## Quick Start (Development Environment)

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

**Note**: All documentation describes educational work developed during an internship, not production systems.

### Getting Started

For portfolio reviewers and technical interviewers:

- [Installation Guide](docs/getting-started/installation.md) - System requirements and setup
- [Quick Start Guide](docs/getting-started/quick-start.md) - Get operational in 10 minutes
- [Configuration Reference](docs/getting-started/configuration.md) - Environment and system configuration

### Usabout the features I built

Learn how to use the platform effectively:

- [Platform Overview](docs/user-guide/overview.md) - Architecture and core concepts
- [Agent Management](docs/user-guide/agents.md) - Deploy and manage agents across environments
- [Running Operations](docs/user-guide/operations.md) - Execute adversary emulation campaigns
- [Reporting and Analysis](docs/user-guide/reporting.md) - Generate and interpret results

### Technical Reference

For developers and system integrators:

- [System Architecture](docs/architecture/system-overview.md) - Component architecture and data flow
- [API Reference](docs/technical/api-reference.md) - REST API endpoints and authentication
- [Datvelopment Environment Setup

Setting up the development/learning environment:

- [Local Setup](docs/deployment/local-deployment.md) - Standalone development server
- [Docker Setup](docs/deployment/docker-deployment.md) - Containerised development
- [ELK Integration](docs/deployment/elk-integration.md) - SIEM integration for learning
- [Troubleshooting](docs/deployment/troubleshooting.md) - Common setup deployment
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
## Key Technical Achievements

### Software Development

**Architecture & Design Patterns**:
- Implemented event-driven architecture with pub/sub pattern for real-time SIEM integration
- Developed circuit breaker pattern for resilient external service integration
- Built plugin-based modular architecture with clear separation of concerns
- Applied dependency injection for testability and maintainability

**Python Development**:
- Async/await patterns for concurrent API calls and database operations
- Decorator patterns for authentication and authorisation
- Context managers for resource lifecycle management
- Type hints and comprehensive error handling

**API Development**:
- RESTful endpoint design following OpenAPI specifications
- Request validation and sanitisation
- API versioning and backwards compatibility

### Detection Engineering

**SIEM Correlation**:
- Elasticsearch integration for real-time event correlation
- Query optimisation for large-scale log analysis
- Detection rule development and validation
- Alert enrichment with MITRE ATT&CK context

**Purple Team Operations**:
- Adversary emulation workflow automation
- MITRE ATT&CK technique mapping and execution
- Detection coverage gap analysis methodology
- Purple team reporting and metric visualisation

**Security Automation**:
- Automated detection validation framework
- Operation tagging for SIEM alert filtering
- Detection coverage reporting pipeline
- Input validation and sanitisation practices

### DevOps & Infrastructure

**Containerisation**:
- Service dependency management
- Volume management for data persistence
- Network isolation and port mapping

**Configuration Management**:
- YAML-based configuration system
- Environment variable injection
- Secrets management patterns
- Multi-environment configuration support

**Monitoring & Logging**:
- Structured logging with Python logging module
- Log aggregation and analysis
- Error tracking and debugging workflows
- Performance monitoring and optimisation

---

## Skills Demonstrated

This internship project showcases competencies in:

**Software Development**:
- Backend development (Python, async/await, REST APIs)
- Frontend integration (Vue.js, SPA architecture)
- Database design (object stores, Elasticsearch)
- Testing (unit tests, integration tests, fixtures)
- Version control (Git, branching strategies)
- Documentation (technical writing, API docs)

**Detection Engineering**:
- SIEM integration (Elasticsearch/ELK Stack)
- MITRE ATT&CK framework application
- Purple team methodologies
- Detection validation and coverage analysis
- Security event correlation
- Threat intelligence integration

**Security & DevOps**:
- Secure coding practices
- Input validation and sanitisation
- Docker containerisation
- CI/CD pipeline integration
- Infrastructure as code
- System architecture design

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
├── require Notice

This is educational software developed in a controlled lab environment. It is NOT intended for use in real security operations.

For questions about this internship project, see [INTERNSHIP_DISCLAIMER.md](INTERNSHIP_DISCLAIMER.md).

## License

Educational/Portfolio License - See [LICENSE](LICENSE) for details.

**Summary**: This code is shared for portfolio review and educational purposes only. Not licensed for commercial use, production deployment, or public distribution.

---

## Technical Deep Dive

### 1. Orchestrator Plugin - SIEM Integration

**Problem Solved**: Manual SIEM alert triaging was taking time per purple team exercise, requiring analyst to manually identify and close alerts generated by controlled testing.

**Solution Architecture**:
- Event-driven architecture listening to Caldera operation lifecycle
- Automatic Elasticsearch document enrichment with operation metadata
- Circuit breaker pattern preventing cascade failures
- Fallback logging when SIEM unavailable

**Technologies**: Python async/await, Elasticsearch Python client, aiohttp, event-driven pub/sub

**Key Learnings**:
- Asynchronous error handling and retry logic
- Service resilience patterns (circuit breaker, fallback)
- Real-time event correlation in SIEM
- API integration with external services

### 2. Reporting Plugin - Detection Coverage Analysis

**Problem Solved**: No automated way to visualise which MITRE ATT&CK techniques were detected vs. evaded during purple team exercises.

**Solution Architecture**:
- PDF generation pipeline with ReportLab
- Elasticsearch query aggregation for detection correlation
- Color-coded coverage matrices
- Multi-operation comparison capabilities

**Technologies**: ReportLab (PDF generation), Elasticsearch Query DSL, Python data analysis, Jinja2 templating

**Key Learnings**:
- Document generation and layout design
- Complex Elasticsearch aggregations
- Data visualisation for security metrics
- Report automation pipeline design

### 3. Debrief-ELK Plugin - Detection Validation

**Problem Solved**: Purple team reports didn't show which techniques were actually detected by the SIEM.

**Solution Architecture**:
- SIEM detection correlation engine
- Per-technique detection status tracking
- Graceful degradation when ELK unavailable
- Integration with existing Caldera debrief system

**Technologies**: Elasticsearch integration, Python data structures, plugin hooks

**Key Learnings**:
- Detection validation methodologies
- MITRE ATT&CK technique correlation
- Plugin architecture and hooks
- Defensive coding for service availability

---

## What I Learned

### Software Development Concepts

**Architecture Patterns**:
- Event-driven architecture for real-time systems
- Plugin architecture for extensibility
- Microservices communication patterns
- Service-oriented architecture (SOA)

**Python Engineering**:
- Asynchronous programming (async/await, event loops)
- Decorator patterns for cross-cutting concerns
- Context managers for resource management
- Type hints for code quality
- Testing strategies (unit, integration, mocking)

**API & Integration**:
- RESTful API design principles
- API authentication and authorisation
- External service integration patterns
- Error handling and retry logic

### Detection Engineering Principles

**SIEM Operations**:
- Elasticsearch Query for threat hunting
- Log correlation and enrichment techniques
- Detection rule development workflow
- SIEM performance optimisation

**Purple Team Methodology**:
- Adversary emulation planning
- MITRE ATT&CK framework application
- Detection coverage measurement
- Purple team metrics and reporting

**Security Automation**:
- Automated detection validation
- Operation lifecycle tracking
- Coverage gap identification
- Detection engineering pipeline automation

### Professional Development

**Problem-Solving Approach**:
- Requirements gathering and analysis
- Technical design and architecture
- Implementation and testing
- Documentation and knowledge transfer

**Development Practices**:
- Git workflow and version control
- Code review and peer feedback
- Technical documentation writing
- Debugging and troubleshooting methodologies

**See [internship-blog/](internship-blog/) for detailed development challenges, solutions, and lessons learned.**

---

## System Requirements

- **Python** - 3.9 or higher
- **Elasticsearch** - 8.11.0 or higher
- **Memory** - 4GB RAM minimum, 8GB recommended
- **Operating System** - Linux, macOS, Windows with WSL

---

## Contact

**About This Project**: tonyto02@proton.me  
**Portfolio**: https://tonyt.pages.dev/  
**LinkedIn**: https://www.linkedin.com/in/tony-to1/

---

## Acknowledgements

**Organisation**: Triskele Labs (Internship Programme)  
**Based On**: MITRE Caldera Framework (open source)  
**Supervisor**: Triskele Labs Security Team

Thank you to my supervisor and the Triskele Labs team for mentorship and guidance during this learning experience.

---

**DISCLAIMER**: This repository documents an internship learning project completed at Triskele Labs between January-February 2026. This is a learning exercise and proof-of-concept implementation, NOT production software or official Triskele Labs intellectual property. All code and documentation are for educational portfolio purposes only, see [Security Policy](docs/SECURITY.md).

## Licence

See [LICENSE](LICENSE) for details.

## Support

For assistance:

- Review the [FAQ](docs/reference/faq.md) for common questions
- Check the [Troubleshooting Guide](docs/reference/troubleshooting.md) for known issues
- Consult the [Security Policy](docs/SECURITY.md) for security-related matters
