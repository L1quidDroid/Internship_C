# Component Architecture

Detailed technical documentation of the platform's internal components, including service layer architecture, object models, and plugin system design.

## Prerequisites

Before reviewing this document, ensure familiarity with:

- [System Overview](system-overview.md) for high-level architecture context
- Python asyncio programming patterns
- Object-oriented design principles
- RESTful API concepts
- Event-driven architecture patterns

## Service Layer Architecture

The platform implements a service-oriented architecture with eight core services providing distinct capabilities. All services inherit from `BaseService` and register themselves in a global service registry for dependency injection.

### Service Registry Pattern

Services are accessed via dependency injection:

```python
# Service registration (during initialization)
self.log = self.add_service('service_name', self)

# Service retrieval (from any component)
data_svc = self.get_service('data_svc')
```

This pattern enables loose coupling and testability across the platform.

### Core Services

#### app_svc (Application Service)

**Purpose**: Manages application lifecycle, plugin system, and agent trust verification

**Key Responsibilities**:
- Plugin loading and lifecycle management
- Agent trust monitoring and timeout detection
- Scheduled operation execution via cron expressions
- Ability file watching for hot-reload
- Operation resumption after server restart
- Application error tracking

**Main Methods**:
- `load_plugins(plugins)`: Load and initialise specified plugins
- `load_plugin_expansions(plugins)`: Execute plugin expansion hooks
- `start_sniffer_untrusted_agents()`: Monitor agent heartbeats for trust status
- `run_scheduler()`: Process scheduled operations
- `resume_operations()`: Restart paused operations after server start
- `watch_ability_files()`: Monitor ability files for changes

**Integration Points**:
- Uses `data_svc` for plugin and agent storage
- Uses `contact_svc` for agent communication
- Uses `event_svc` for system events
- Manages plugin lifecycle through Plugin objects

#### auth_svc (Authentication Service)

**Purpose**: Handles user authentication, authorisation, and session management

**Key Responsibilities**:
- User login and logout processing
- Session token generation and validation
- Permission level enforcement
- Login handler registration for custom authentication
- CORS and API key management

**Authorisation Levels**:
- **APP**: General application access
- **RED**: Red team operation capabilities
- **BLUE**: Blue team analysis and reporting
- **ADMIN**: Full system administration

**Main Methods**:
- `login_user(request)`: Authenticate user credentials
- `logout_user(request)`: Invalidate user session
- `get_permissions(request)`: Retrieve user permission levels
- `apply(app, users)`: Configure authentication middleware
- `set_login_handlers(services)`: Register custom login providers

**Integration Points**:
- Middleware for aiohttp request processing
- Session storage in application context
- User configuration from YAML files

#### contact_svc (Contact Service)

**Purpose**: Manages agent communication protocols and heartbeat processing

**Key Responsibilities**:
- C2 protocol registration and lifecycle
- Agent heartbeat handling and instruction delivery
- Agent bootstrap process for new beacons
- Result collection from agent execution
- Agent trust verification
- Tunnel management for peer-to-peer communications

**Supported Protocols**:
- HTTP/HTTPS (standard web traffic)
- TCP (raw socket communication)
- UDP (connectionless datagrams)
- WebSocket (bidirectional real-time)
- DNS (DNS query-based C2)
- FTP (file transfer protocol)
- Slack (messaging platform)
- Gist (GitHub-based dead drop)

**Main Methods**:
- `register_contact(contact)`: Enable C2 protocol
- `deregister_contacts()`: Shutdown all C2 channels
- `handle_heartbeat(**kwargs)`: Process agent beacon
- `build_filename()`: Generate agent payload filename

**Heartbeat Processing Flow**:
1. Receive beacon with agent metadata and results
2. Sanitise agent PAW (unique identifier)
3. Update existing agent or create new agent object
4. Process execution results and link completion
5. Fire completion events for monitoring
6. Return instructions for next execution cycle
7. Bootstrap new agents with initial configuration

**Integration Points**:
- Uses `data_svc` to locate and store agents
- Uses `app_svc` to find operations with links
- Uses `event_svc` for agent and link events
- Reports heartbeat activity for logging

#### data_svc (Data Service)

**Purpose**: Manages the in-memory object store and persistence layer

**Key Responsibilities**:
- Object storage and retrieval (CRUD operations)
- State persistence to disk (pickle serialisation)
- State restoration on server startup
- Data loading from YAML/JSON files
- Backup and destroy operations
- Object matching and searching

**Object Store Schema**:
```python
{
    'agents': [],          # Active and historical agents
    'planners': [],        # Planning algorithms
    'adversaries': [],     # Attack profiles
    'abilities': [],       # Atomic techniques
    'sources': [],         # Fact sources
    'operations': [],      # Running and completed operations
    'schedules': [],       # Scheduled operations
    'plugins': [],         # Loaded plugins
    'obfuscators': [],     # Command obfuscation modules
    'objectives': [],      # Operation goals
    'data_encoders': []    # Encoding schemes
}
```

**Main Methods**:
- `store(c_object)`: Add or update object in store
- `locate(object_name, match)`: Find objects by criteria
- `remove(object_name, match)`: Delete matching objects
- `save_state()`: Persist store to disk
- `restore_state()`: Load store from disk
- `load_data(plugins)`: Import YAML/JSON data files
- `destroy()`: Backup and reset all data

**Persistence Strategy**:
- Primary storage: In-memory Python dictionaries (fast access)
- Backup storage: Pickled file at `data/object_store`
- Configuration data: YAML files in `data/` subdirectories
- Results and payloads: File system storage

**Integration Points**:
- All services use `data_svc` for object persistence
- Plugin data directories for isolated storage
- File system for abilities, adversaries, sources

#### event_svc (Event Service)

**Purpose**: Provides WebSocket-based event bus for system-wide notifications

**Key Responsibilities**:
- Event publication to subscribers
- Observer pattern implementation
- Global listener registration
- Exchange and queue routing
- Asynchronous event delivery

**Event Structure**:
- **Exchange**: Event category (e.g., 'operation', 'agent', 'link')
- **Queue**: Event type (e.g., 'completed', 'added', 'state_changed')
- **Metadata**: Timestamp and context information
- **Payload**: Event-specific data

**Main Methods**:
- `fire_event(exchange, queue, **kwargs)`: Publish event
- `observe_event(callback, exchange, queue)`: Subscribe to events
- `register_global_event_listener(callback)`: Subscribe to all events
- `notify_global_event_listeners(event, **kwargs)`: Broadcast to global listeners

**Event Flow**:
```
Component fires event
    ↓
Event Service receives
    ↓
WebSocket connection to handlers
    ↓
Registered callbacks executed
    ↓
Global listeners notified
```

**Common Events**:
- `agent/added`: New agent beacon received
- `link/completed`: Ability execution finished
- `operation/state_changed`: Operation status updated
- `operation/completed`: Operation finished
- `system/ready`: Server startup complete

**Integration Points**:
- Uses `contact_svc` WebSocket contact for delivery
- All services fire events for state changes
- Plugins subscribe for custom workflows

#### file_svc (File Service)

**Purpose**: Manages payload storage, delivery, and dynamic compilation

**Key Responsibilities**:
- Standard payload file serving
- Special payload dynamic generation
- Agent executable compilation
- File upload and download handling
- Extension-based payload categorisation

**Payload Types**:
- **Standard Payloads**: Static files served directly
- **Special Payloads**: Dynamically generated (e.g., compiled agents)
- **Extensions**: Files organised by type for agent filtering

**Main Methods**:
- `add_special_payload(name, function)`: Register dynamic payload
- `get_file(name)`: Retrieve payload by name
- `save_file(filename, content, location)`: Store file to disk
- `read_file(filename, location)`: Load file from disk

**Special Payload Example**:
```python
# Sandcat plugin registers dynamic compilation
await file_svc.add_special_payload(
    'sandcat.go', 
    sand_svc.dynamically_compile_executable
)
```

When requested, `sandcat.go` is compiled with agent-specific configuration rather than served as static file.

**Integration Points**:
- Plugin payload directories
- REST API file endpoints
- Agent payload delivery during bootstrap

#### knowledge_svc (Knowledge Service)

**Purpose**: Manages fact storage, relationships, and knowledge base queries

**Key Responsibilities**:
- Fact storage and retrieval
- Fact relationship management
- Knowledge graph traversal
- Fact seeding for operations
- Relationship rule processing

**Fact Structure**:
- **Trait**: Fact category (e.g., 'host.ip.address', 'domain.user.name')
- **Value**: Fact data (e.g., '192.168.1.10', 'admin')
- **Score**: Confidence level (0-100)
- **Source**: Origin type (SEEDED, LEARNED, INFERRED)

**Main Methods**:
- `add_fact(fact)`: Store new fact
- `get_facts(criteria)`: Query facts by filters
- `update_fact(fact)`: Modify existing fact
- `get_relationships()`: Retrieve fact relationships
- `save_state()`: Persist knowledge base
- `restore_state()`: Load knowledge base

**Fact Relationships**:
Facts can be linked with relationship edges:
- `has`: Ownership relationship
- `uses`: Utilisation relationship
- `belongs_to`: Membership relationship

Example: `host.ip.address(192.168.1.10)` --[has]--> `domain.user.name(admin)`

**Integration Points**:
- Operations seed facts from Source objects
- Learning service extracts facts from results
- Planners use facts to populate ability variables

#### learning_svc (Learning Service)

**Purpose**: Extracts facts from execution results using parser modules

**Key Responsibilities**:
- Parser module management
- Fact extraction from command output
- Relationship discovery between facts
- Link scoring based on fact yield
- Learning model maintenance

**Parser System**:
Parsers are Python modules in `app/learning/` that implement:
```python
class Parser:
    def parse(self, blob):
        # Extract facts from command output
        return [Fact(...), Fact(...)]
```

**Main Methods**:
- `learn(facts, link, blob, operation)`: Parse results and extract facts
- `build_model()`: Analyse abilities to build relationship model
- `add_parsers(directory)`: Load parser modules

**Fact Extraction Flow**:
1. Link completes with result output
2. Learning service receives encoded output
3. Each parser processes output
4. Extracted facts stored via link
5. Relationship model identifies fact pairs
6. Relationships created between matching facts
7. Link score updated based on fact count

**Integration Points**:
- Contact service invokes learning after result collection
- Facts stored in knowledge service
- Operation links updated with extracted data

#### planning_svc (Planning Service)

**Purpose**: Generates ability links for operations based on planner logic

**Key Responsibilities**:
- Link generation from abilities
- Bucket execution management
- Stopping condition evaluation
- Next-bucket decision logic
- Link completion monitoring

**Planning Concepts**:

**Buckets**: Ability groups for execution ordering (e.g., 'collection', 'exfiltration')

**Links**: Executable ability instances with:
- Agent assignment
- Populated fact variables
- Executor selection
- Status tracking

**Main Methods**:
- `get_links(operation, buckets, agent)`: Generate executable links
- `exhaust_bucket(planner, bucket, operation, agent)`: Execute all bucket abilities
- `wait_for_links_and_monitor(planner, operation, link_ids)`: Track completion
- `default_next_bucket(current, state_machine)`: Determine next bucket
- `add_ability_to_bucket(ability, bucket)`: Categorise ability

**Bucket Execution Modes**:
- **Serial**: Execute links one at a time, waiting for completion
- **Batch**: Push all links immediately, wait for batch completion

**Integration Points**:
- Planners invoke planning service for link generation
- Operations apply links for execution
- Stopping conditions evaluated after link completion

#### rest_svc (REST Service)

**Purpose**: Implements REST API endpoint logic and business operations

**Key Responsibilities**:
- Object CRUD operations via API
- Operation management and control
- Link manipulation and task assignment
- Report generation
- Configuration updates

**Main Methods**:
- `display_objects(object_name, filters)`: List objects with criteria
- `create_operation(access, data)`: Start new operation
- `update_operation(**kwargs)`: Modify running operation
- `delete_operation(data)`: Remove operation
- `persist_ability(access, data)`: Save ability definition
- `apply_potential_link(link)`: Execute manual link
- `display_operation_report(data)`: Generate operation report
- `task_agent_with_ability(**kwargs)`: Manual agent tasking

**Integration Points**:
- REST API routes delegate to rest_svc methods
- Uses data_svc for object storage
- Uses app_svc for operation management
- Uses auth_svc for permission enforcement

## Object Model

### First-Class Objects

First-class objects inherit from `FirstClassObjectInterface` and `BaseObject`, providing:
- Unique identification via hash
- Store/retrieve operations
- Match filtering
- Schema-based serialisation

#### Agent

**Purpose**: Represents deployed endpoint running on target system

**Key Attributes**:
- `paw`: Unique agent identifier
- `host`: Hostname of target system
- `platform`: Operating system (windows, linux, darwin)
- `executors`: Available command executors (psh, sh, cmd)
- `privilege`: User privilege level (User, Elevated, SYSTEM)
- `group`: Operational grouping (red, blue, custom)
- `trusted`: Trust status for autonomous operations
- `sleep_min/max`: Heartbeat timing configuration
- `contact`: C2 protocol in use

**Lifecycle**:
1. Initial beacon received via contact protocol
2. Agent object created and stored
3. Bootstrap process assigns initial facts
4. Heartbeat loop begins for instruction delivery
5. Trust status monitored for timeout
6. Agent marked untrusted if heartbeat stops
7. Historical agent data retained

**Integration Points**:
- Contact service manages heartbeats
- Operations assign agents to adversary profiles
- Links execute on specific agents
- Knowledge service stores agent-specific facts

#### Operation

**Purpose**: Represents running adversary emulation campaign

**Key Attributes**:
- `id`: Unique operation identifier
- `name`: Human-readable operation name
- `adversary`: Attack profile being executed
- `planner`: Planning algorithm controlling execution
- `state`: Current status (running, paused, finished)
- `agents`: Assigned agents for operation
- `chain`: Executed and pending links
- `source`: Fact source for intelligence
- `objective`: Goal-based completion criteria
- `autonomous`: Autonomous execution flag

**State Machine**:
```
created → running → (paused) → finished
                  ↓
               out_of_time
```

**Main Methods**:
- `apply(link)`: Add link to operation chain
- `wait_for_links_completion(link_ids)`: Block until links finish
- `is_finished()`: Check completion status
- `has_link(link_id)`: Verify link membership

**Integration Points**:
- Planners generate links for operations
- Agents execute operation links
- Event service notifies state changes
- Report generation from completed operations

#### Ability

**Purpose**: Atomic adversary technique mapped to MITRE ATT&CK

**Key Attributes**:
- `ability_id`: Unique identifier (often ATT&CK T-number)
- `name`: Technique name
- `description`: Capability description
- `tactic`: ATT&CK tactic (discovery, lateral-movement)
- `technique_id`: ATT&CK technique ID
- `technique_name`: ATT&CK technique name
- `executors`: Platform-specific implementations
- `requirements`: Fact prerequisites
- `privilege`: Required privilege level
- `buckets`: Planning categorisation tags

**Executor Structure**:
Each executor provides platform-specific implementation:
- `platform`: Target OS (windows, linux, darwin)
- `name`: Executor type (psh, sh, cmd)
- `command`: Command template with fact variables
- `parsers`: Output parsing configuration
- `payloads`: Required payload files
- `timeout`: Execution timeout

**Integration Points**:
- Adversaries contain ability collections
- Planners generate links from abilities
- Learning service parses ability output
- Stockpile plugin provides ability library

#### Adversary

**Purpose**: Collection of abilities forming coherent attack profile

**Key Attributes**:
- `adversary_id`: Unique identifier
- `name`: Profile name
- `description`: Attack scenario description
- `atomic_ordering`: Ability execution sequence
- `objective`: Associated objective for goal-based execution
- `tags`: Categorisation and filtering tags

**Main Methods**:
- `has_ability(ability_id)`: Check ability membership
- `add_ability(ability)`: Include ability in profile

**Integration Points**:
- Operations execute adversary profiles
- Planners iterate adversary abilities
- Objectives define adversary goals

#### Planner

**Purpose**: Decision logic controlling operation execution flow

**Key Attributes**:
- `planner_id`: Unique identifier
- `name`: Planner name
- `description`: Strategy description
- `module`: Python module path for implementation
- `params`: Configuration parameters
- `stopping_conditions`: Criteria for halting execution

**Built-in Planners**:
- **Atomic**: Sequential execution in defined order
- **Batch**: Parallel execution of all abilities
- **Buckets**: Categorised execution by tactic

**Integration Points**:
- Operations specify planner for execution strategy
- Planning service implements planner logic
- Stopping conditions evaluated during execution

#### Objective

**Purpose**: Goal-based operation completion criteria

**Key Attributes**:
- `id`: Unique identifier
- `name`: Objective name
- `description`: Goal description
- `goals`: Target facts to collect
- `percentage`: Completion threshold (0-100)

**Goal Structure**:
Each goal defines fact target:
- `target`: Fact trait to collect
- `count`: Required fact instances
- `value`: Optional specific value match
- `achieved`: Current achievement status

**Integration Points**:
- Operations use objectives for goal-based execution
- Planners check objective completion
- Fact collection contributes to goal achievement

#### Source

**Purpose**: Fact collection for operation intelligence seeding

**Key Attributes**:
- `id`: Unique identifier
- `name`: Source name
- `facts`: Fact collection
- `adjustments`: Fact modification rules
- `rules`: Fact generation rules

**Main Methods**:
- `add_fact(fact)`: Include fact in source
- `remove_fact(trait, value)`: Delete matching fact

**Integration Points**:
- Operations seed facts from sources
- Knowledge service stores source facts
- Adjustments modify facts during seeding

#### Plugin

**Purpose**: Modular extension providing additional capabilities

**Key Attributes**:
- `name`: Plugin name
- `description`: Capability description
- `address`: Web UI endpoint (if applicable)
- `enabled`: Activation status
- `data_dir`: Plugin-specific data directory
- `access`: Required permission level

**Plugin Lifecycle**:
1. Discovery: Plugin found in `plugins/` directory
2. Load: Import `hook.py` module
3. Enable: Execute `enable(services)` function
4. Expand: Execute `expansion(services)` if defined
5. Destroy: Execute `destroy(services)` on shutdown

**Hook Module Functions**:
- `enable(services)`: Register routes, services, functionality
- `expansion(services)`: Post-load expansion (optional)
- `destroy(services)`: Cleanup on shutdown (optional)

**Integration Points**:
- App service manages plugin lifecycle
- Data service provides plugin data directories
- REST API serves plugin endpoints

### Second-Class Objects

Second-class objects are embedded within first-class objects and do not have independent storage.

#### Link

**Purpose**: Executable ability instance with specific context

**Key Attributes**:
- `id`: Unique link identifier
- `ability`: Source ability reference
- `executor`: Selected executor for platform
- `paw`: Assigned agent PAW
- `command`: Populated command with facts
- `status`: Execution status (0=success, -1=pending, >0=error)
- `score`: Link value based on fact yield
- `facts`: Collected facts from execution
- `relationships`: Discovered fact relationships
- `output`: Execution result data

**Status Values**:
- `-5`: Link discarded (requirements not met)
- `-4`: Link collected (queued for execution)
- `-3`: High-value target (prioritised)
- `-2`: Untrusted agent (execution blocked)
- `-1`: Pending execution
- `0`: Success
- `1`: Error or failure
- `124`: Timeout
- `EXECUTE`: Special code for manual execution

**Integration Points**:
- Operations contain link chains
- Agents execute links
- Learning service extracts facts from links
- Planning service generates links

#### Fact

**Purpose**: Single piece of operational intelligence

**Key Attributes**:
- `trait`: Fact category/type
- `value`: Fact data
- `score`: Confidence/reliability (0-100)
- `source`: Origin type (SEEDED, LEARNED, INFERRED)
- `links`: Links that discovered/used this fact

**Origin Types**:
- `SEEDED`: Manually provided or from source
- `LEARNED`: Extracted from command output
- `INFERRED`: Derived from relationships

**Integration Points**:
- Knowledge service stores facts
- Links populate ability variables with facts
- Learning service creates facts from results

#### Executor

**Purpose**: Platform-specific ability implementation

**Key Attributes**:
- `name`: Executor type (psh, sh, cmd, proc)
- `platform`: Target OS
- `command`: Command template
- `code`: Inline script content
- `language`: Scripting language
- `parsers`: Output parsing modules
- `payloads`: Required files
- `timeout`: Execution time limit
- `variations`: Alternative implementations

**Integration Points**:
- Abilities contain executor collections
- Agents filter executors by capability
- Links select executor for platform

#### Instruction

**Purpose**: Agent command delivery wrapper

**Key Attributes**:
- `id`: Link identifier
- `command`: Encoded command
- `executor`: Executor name
- `timeout`: Execution timeout
- `payloads`: Required payload list

**Integration Points**:
- Contact service builds instructions from links
- Agents receive instructions in heartbeat response
- Results reference instruction ID

#### Result

**Purpose**: Agent command execution output

**Key Attributes**:
- `id`: Link identifier
- `output`: Encoded command output
- `status`: Exit code
- `pid`: Process ID

**Integration Points**:
- Agents submit results in heartbeat
- Contact service processes results
- Learning service parses results for facts

## Plugin System Architecture

### Core Plugins

#### Magma

**Purpose**: Vue.js frontend interface

**Capabilities**:
- Modern single-page application
- Operation management UI
- Agent monitoring dashboard
- Adversary and ability management
- Real-time operation status updates

**Implementation**:
- Vue.js framework
- REST API client for backend
- WebSocket for real-time updates
- Static asset serving

#### Sandcat

**Purpose**: Cross-platform agent implementation

**Capabilities**:
- GoLang-based agent for portability
- Multi-platform support (Windows, Linux, macOS)
- Dynamic compilation with configuration
- Multiple executor support
- Autonomous operation capability

**Implementation**:
- GoLang source in plugin directory
- Dynamic compilation via file_svc
- C2 protocol selection at compile time
- Platform-specific executors

#### Stockpile

**Purpose**: Adversary profiles and abilities library

**Capabilities**:
- MITRE ATT&CK mapped abilities
- Pre-configured adversary profiles
- Multi-platform technique implementations
- Fact-based ability parameterisation

**Implementation**:
- YAML ability definitions
- YAML adversary profiles
- Parser modules for fact extraction
- Payload files for technique execution

#### Atomic

**Purpose**: MITRE Atomic Red Team integration

**Capabilities**:
- Atomic test import and translation
- ATT&CK technique coverage
- Community-driven test library
- Automated ability generation

**Implementation**:
- Atomic test parsing
- Ability conversion logic
- YAML output generation

#### Orchestrator

**Purpose**: Automated workflow and SIEM tagging

**Capabilities**:
- Operation event monitoring
- Elasticsearch event tagging
- Detection coverage tracking
- Automated purple team workflows

**Implementation**:
- Event service subscription
- Elasticsearch API client
- Link completion processing
- Technique ID tagging

#### Branding

**Purpose**: Custom theming and visual identity

**Capabilities**:
- Logo and colour customisation
- CSS theme overrides
- Banner customisation
- Custom terminology

**Implementation**:
- Template overrides
- Static asset replacement
- Configuration-driven branding

#### Reporting

**Purpose**: PDF and HTML report generation

**Capabilities**:
- Operation summary reports
- Detection coverage reports
- Technique execution details
- Exfiltration file listings

**Implementation**:
- ReportLab PDF generation
- HTML template rendering
- Multi-threaded report building
- Plugin-based report sections

### Plugin Development Patterns

#### Hook Module Structure

Every plugin requires `hook.py` with:

```python
name = 'PluginName'
description = 'Plugin description'
address = '/plugin/endpoint/path'  # or None for backend-only

async def enable(services):
    # Plugin initialisation
    # Register routes, services, etc.
    pass

async def expansion(services):  # Optional
    # Post-load expansion
    pass

async def destroy(services):  # Optional
    # Cleanup on shutdown
    pass
```

#### Service Access

Plugins access core services via registry:

```python
async def enable(services):
    data_svc = services.get('data_svc')
    app_svc = services.get('app_svc')
    
    # Register custom service
    custom_svc = CustomService(services)
    services['custom_svc'] = custom_svc
```

#### Route Registration

HTTP routes registered via aiohttp:

```python
async def enable(services):
    app = services.get('app_svc').application
    
    # GET /plugin/example/status
    app.router.add_route('GET', '/plugin/example/status', 
                         handler_function)
```

#### Event Subscription

Subscribe to system events:

```python
async def enable(services):
    event_svc = services.get('event_svc')
    
    await event_svc.observe_event(
        callback=event_handler,
        exchange='operation',
        queue='completed'
    )
```

## Component Interactions

### Agent Registration Flow

```
1. Agent beacons to C2 protocol endpoint
   ↓
2. Contact service receives heartbeat
   ↓
3. PAW sanitisation and validation
   ↓
4. Check if agent exists in data_svc
   ↓
5. New agent: Create Agent object, bootstrap, store
   Existing agent: Update metadata, process results
   ↓
6. Generate instructions from operation links
   ↓
7. Return instructions in heartbeat response
   ↓
8. Fire agent/added or agent/updated event
```

### Operation Execution Flow

```
1. User creates operation via API
   ↓
2. Operation stored in data_svc
   ↓
3. Planner begins link generation
   ↓
4. Planning service generates links from abilities
   ↓
5. Links filtered by agent capability and facts
   ↓
6. Operation applies links to chain
   ↓
7. Links delivered to agents via heartbeat
   ↓
8. Agents execute commands, return results
   ↓
9. Contact service processes results
   ↓
10. Learning service extracts facts
    ↓
11. Knowledge service stores facts
    ↓
12. Link status updated to success/failure
    ↓
13. Planner generates next links
    ↓
14. Repeat until operation complete or stopped
```

### Fact Collection and Usage

```
1. Operation starts with seeded facts from source
   ↓
2. Link executes on agent with fact variables
   ↓
3. Result returned with command output
   ↓
4. Learning service parses output with parsers
   ↓
5. New facts extracted and stored
   ↓
6. Relationships identified between facts
   ↓
7. Link scored based on fact yield
   ↓
8. Future links use discovered facts for variables
   ↓
9. Objective goals evaluated against collected facts
```

### Plugin Loading Sequence

```
1. App service discovers plugins in plugins/ directory
   ↓
2. Plugin objects created and stored
   ↓
3. Plugin.load_plugin() imports hook module
   ↓
4. Plugin metadata extracted (name, description, address)
   ↓
5. Enabled plugins have enable(services) called
   ↓
6. Plugin registers routes, services, handlers
   ↓
7. Data service loads plugin data files
   ↓
8. Plugin expansion(services) called if defined
   ↓
9. Plugin fully operational
```

## See Also

### Architecture Documentation

- [System Overview](system-overview.md) - High-level architecture and deployment
- [Data Flow Diagrams](data-flow.md) - Process flows and sequences

### Implementation Guides

- [API Reference](/docs/technical/api-reference.md) - REST API endpoints
- [Database Schema](/docs/technical/database-schema.md) - Object relationships
- [Plugin Development](/docs/development/plugin-development.md) - Creating plugins
- [Testing Guide](/docs/development/testing.md) - Component testing

### User Documentation

- [Platform Overview](/docs/user-guide/overview.md) - User-focused concepts
- [Running Operations](/docs/user-guide/operations.md) - Operation management
- [Agent Management](/docs/user-guide/agents.md) - Agent deployment
