# System Overview - Internship Project Documentation

**⚠️ EDUCATIONAL PROJECT**: This documentation describes an internship learning project, NOT production software.

**Author**: Tony To (Intern - Detection Engineer and Automation Officer)  
**Organisation**: Triskele Labs (Internship Programme)  
**Timeline**: January-February 2026  
**Status**: Educational/Portfolio Documentation

---

Comprehensive architectural overview of the purple team automation internship project, demonstrating Caldera plugin development with ELK Stack integration patterns learned during the internship.

## Prerequisites

Before reviewing this document, ensure familiarity with:

- MITRE ATT&CK framework fundamentals
- Adversary emulation concepts
- Basic SIEM and detection engineering principles
- Python asynchronous programming patterns (asyncio)
- RESTful API architectures

## Platform Architecture (Learning Exercise)

This project demonstrates a server-centric architecture with distributed agents and modular plugin system learned during the internship. The core server orchestrates operations, manages agent communications, and coordinates with external SIEM infrastructure.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Web Interface (Vue.js) - Educational Customisation  │
│                    Magma Plugin Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API (Learning)
┌──────────────────────┴──────────────────────────────────────┐
│         Core Server (Python/aiohttp) - Internship Study     │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ REST API   │  │ Service Layer│  │ Plugin System    │    │
│  │ (v1 & v2)  │  │ (8 Services) │  │ (7 Plugins Dev)  │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │     Event System (WebSocket-based) - Learning      │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │     Object Store (In-Memory + Persistent)          │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────┬──────────────────────┬─────────────────┬────┘
               │                      │                 │
               │ C2 Protocols         │ REST API        │ Events
               │ (HTTP/TCP/UDP/       │ (Learning)      │ (Study)
               │  WebSocket/etc)      │                 │
┌──────────────┴──────────────────┐  │  ┌──────────────┴─────┐
│   Agents (Sandcat - GoLang)     │  │  │  ELK Stack         │
│   - Test Environments           │  │  │  (Elasticsearch)   │
│   - Learning Exercise           │  │  │  - Detection tags  │
│   - Cross-platform study        │  │  │  - Learning Lab    │
└─────────────────────────────────┘  │  └────────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          │  File System        │
                          │  - Abilities        │
                          │  - Payloads         │
                          │  - Results          │
                          │  - Configuration    │
                          └─────────────────────┘
```

**Note**: This architecture diagram represents an educational implementation, not a production system.

### Core Components

#### Server Application

The main server (`server.py`) provides:

- **Asynchronous HTTP Server**: Built on aiohttp framework for concurrent request handling
- **Service Orchestration**: Initialises and coordinates 8 core services
- **Plugin Management**: Loads and enables modular plugins during startup
- **State Persistence**: Manages server state through object store serialisation
- **Scheduler**: Executes scheduled operations via cron-based timing

#### Service Layer

Eight core services provide foundational capabilities:

- **app_svc**: Application lifecycle, plugin loading, agent trust management
- **auth_svc**: Authentication, authorisation, session management
- **contact_svc**: Agent communication protocol handling and heartbeat processing
- **data_svc**: Object store management, persistence, data loading
- **event_svc**: WebSocket-based event bus for system-wide notifications
- **file_svc**: Payload delivery, file management, dynamic compilation
- **knowledge_svc**: Fact storage, knowledge base, relationship tracking
- **learning_svc**: Parser management, fact extraction, relationship learning
- **planning_svc**: Operation planning, link generation, bucket execution
- **rest_svc**: REST API endpoint implementations

#### Object Model

First-class objects represent core entities:

- **Agent**: Deployed endpoint running on target systems
- **Ability**: Atomic adversary technique (mapped to ATT&CK)
- **Adversary**: Collection of abilities forming attack profile
- **Operation**: Running emulation campaign with specific adversary
- **Planner**: Decision logic controlling operation execution flow
- **Objective**: Goal-based operation completion criteria
- **Source**: Fact collection for operation intelligence
- **Plugin**: Modular extension providing additional capabilities

#### Data Stores

Multiple storage layers persist platform state:

- **In-Memory RAM**: Primary object store for active operations (Python dictionaries)
- **Object Store**: Pickled persistence file (`data/object_store`)
- **File System**: YAML/JSON configurations, abilities, adversaries, payloads
- **Result Storage**: Operation outputs and exfiltrated data (`data/results/`)

## Technology Stack

### Core Technologies

- **Python**: Server implementation language
- **aiohttp**: Asynchronous HTTP server framework
- **asyncio**: Concurrency model for non-blocking operations
- **marshmallow**: Object serialisation and validation
- **GoLang**: Agent (Sandcat) implementation language
- **Vue.js**: Modern frontend framework (Magma plugin)
- **WebSocket**: Real-time event communication protocol

### Supporting Libraries

- **aiohttp-jinja2**: Template rendering for legacy UI
- **croniter**: Cron expression parsing for scheduling
- **PyYAML**: Configuration and data file parsing
- **Rich**: Enhanced terminal logging and formatting
- **marshmallow**: Schema validation and object marshalling

### External Integrations

- **Elasticsearch**: SIEM backend for detection correlation
- **Docker**: Containerised deployment option
- **Git**: Plugin version control and distribution

## Deployment Topologies

### Standalone Deployment

Single server running all components:

```
┌─────────────────────────────────────────┐
│         Server (localhost:8888)         │
│  - All services running in one process  │
│  - SQLite/File-based storage           │
│  - Suitable for testing/development    │
└─────────────────────────────────────────┘
```

**Use Cases**: Development, testing, small-scale evaluations

**Characteristics**:
- Quick setup with minimal configuration
- All data stored locally
- No external dependencies required
- Limited scalability

### Docker Deployment

Containerised server with optional ELK integration:

```
┌──────────────────┐     ┌──────────────────┐
│  Caldera         │────▶│  Elasticsearch   │
│  Container       │     │  Container       │
│  (Port 8888)     │     │  (Port 9200)     │
└──────────────────┘     └──────────────────┘
         │
         │ Volume Mount
         ▼
┌──────────────────┐
│  Host File       │
│  System          │
│  (./data, etc)   │
└──────────────────┘
```

**Use Cases**: Learning environment setup, development and testing purposes

**Characteristics**:
- Isolated runtime environment
- Simplified dependency management
- Easy replication for portfolio demonstrations
- Network-based ELK integration

### Distributed Deployment

Enterprise deployment with separated concerns:

```
┌──────────────────┐     ┌──────────────────┐
│  Frontend        │────▶│  Caldera API     │
│  (Magma/Nginx)   │     │  Server Cluster  │
└──────────────────┘     └─────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
         ┌──────────▼────┐  ┌──────▼────┐  ┌─────▼──────┐
         │ Elasticsearch │  │   File    │  │   Agents   │
         │    Cluster    │  │   Storage │  │  (Targets) │
         └───────────────┘  └───────────┘  └────────────┘
```

**Use Cases**: Large-scale purple team operations, multi-tenant environments

**Characteristics**:
- Horizontal scalability
- High availability options
- Centralised logging and monitoring
- Role-based access control

## Integration Points

### ELK Stack Integration

The platform integrates with Elasticsearch for detection correlation:

**Orchestrator Plugin Workflow**:

1. Operation executes abilities against targets
2. Links complete with technique IDs (T-numbers)
3. Orchestrator tags Elasticsearch events with `caldera_technique_id`
4. Detection coverage reports query tagged events
5. Gap analysis identifies missing detections

**Configuration Requirements**:

- Elasticsearch endpoint (`ELASTICSEARCH_URL`)
- Authentication credentials
- Index pattern matching agent data
- Time-based indexing for correlation

### External System Access

**File System Access**:
- Payload storage and retrieval
- Result exfiltration
- Configuration management
- Plugin data directories

**Network Communications**:
- Agent C2 channels (multiple protocols)
- REST API for automation
- WebSocket for real-time updates
- Elasticsearch API for SIEM correlation

## Security Architecture

### Authentication and Authorisation

**Authentication Methods**:
- Username/password authentication
- Session-based authentication tokens
- Configurable login handlers

**Authorisation Levels**:
- **Red Access**: Offensive operation capabilities
- **Blue Access**: Defensive analysis and reporting
- **App Access**: Plugin and service management
- **Admin Access**: Full system control

### Communication Security

**Agent Communications**:
- Multiple C2 protocol options (HTTP, TCP, UDP, WebSocket, DNS, FTP)
- Configurable encryption per protocol
- Agent trust verification system
- Heartbeat-based liveness detection

**API Security**:
- CORS configuration for web access
- API key authentication options
- Request validation middleware
- Role-based endpoint access

### Data Security

**Sensitive Data Handling**:
- Credentials stored in configuration files
- Results encrypted at rest (optional)
- Payload obfuscation support
- Agent communication encoding

**Operational Security**:
- Agent jitter for evasion
- Configurable sleep timers
- Deadman ability support for cleanup
- Untrusted agent timeout detection

## System Scalability

### Performance Characteristics

**Concurrent Operations**:
- Asynchronous processing enables hundreds of concurrent agents
- WebSocket event bus supports real-time updates
- In-memory object store provides fast access
- Background task scheduling for non-blocking operations

**Resource Utilisation**:
- Memory-based object store (consider RAM requirements)
- File I/O for payloads and results
- CPU usage scales with active operations
- Network bandwidth for agent communications

### Scaling Considerations

**Vertical Scaling**:
- Increase server RAM for larger object stores
- CPU cores improve concurrent operation handling
- Disk I/O for result storage and payload delivery

**Horizontal Scaling**:
- Stateless API design enables load balancing
- Shared file storage for multi-server deployments
- Distributed agent management across servers
- Elasticsearch clustering for SIEM capacity

## System Lifecycle

### Startup Sequence

1. **Configuration Loading**: Parse YAML configuration files
2. **Service Initialisation**: Create service instances and register
3. **State Restoration**: Load persisted object store from disk
4. **Plugin Loading**: Enable configured plugins in order
5. **Data Loading**: Import abilities, adversaries, payloads from YAML
6. **Contact Registration**: Initialise agent communication protocols
7. **API Enablement**: Start REST API and WebSocket endpoints
8. **Scheduler Activation**: Begin scheduled task processing
9. **Ready Event**: Fire system ready event for integrations

### Runtime Operations

**Continuous Processes**:
- Agent heartbeat monitoring and trust verification
- Scheduled operation execution
- Learning model updates from fact extraction
- Ability file monitoring for hot-reload
- Event processing and notification

**Background Tasks**:
- Untrusted agent detection
- Operation state persistence
- Result file management
- Plugin expansion execution

### Shutdown Sequence

**Graceful Shutdown**:
1. Stop accepting new operations
2. Complete running operations or pause
3. Save object store state to disk
4. Deregister contact protocols
5. Close database connections
6. Terminate background tasks
7. Shutdown HTTP server

## See Also

### Implementation Documentation

- [Component Architecture](component-architecture.md) - Detailed service and object descriptions
- [Data Flow Diagrams](data-flow.md) - Process flows and sequence diagrams
- [API Reference](/docs/technical/api-reference.md) - REST API endpoint documentation
- [Database Schema](/docs/technical/database-schema.md) - Object model relationships

### Deployment Guides

- [Docker Deployment](/docs/deployment/docker-deployment.md) - Container setup and configuration
- [ELK Integration](/docs/deployment/elk-integration.md) - SIEM correlation configuration
- [Configuration Reference](/docs/getting-started/configuration.md) - System settings

### Development Resources

- [Plugin Development](/docs/development/plugin-development.md) - Creating custom plugins
- [Contributing Guidelines](/docs/CONTRIBUTING.md) - Development standards
- [Testing Guide](/docs/development/testing.md) - Test framework and practices
