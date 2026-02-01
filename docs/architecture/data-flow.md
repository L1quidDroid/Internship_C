# Data Flow

Comprehensive documentation of data and process flows within the platform, including agent communication, operation execution, fact collection, SIEM integration, and event processing.

## Prerequisites

Before reviewing this document, ensure familiarity with:

- [System Overview](system-overview.md) for architectural context
- [Component Architecture](component-architecture.md) for service and object details
- MITRE ATT&CK framework concepts
- Asynchronous programming patterns

## Agent Communication Flow

### Initial Agent Beacon

The initial beacon establishes agent registration and begins the heartbeat cycle.

```
┌─────────────┐                                    ┌──────────────────┐
│   Agent     │                                    │  Caldera Server  │
│  (Target)   │                                    │                  │
└──────┬──────┘                                    └────────┬─────────┘
       │                                                    │
       │ 1. Initial HTTP POST /beacon                      │
       │    Body: {platform, executors, host, etc.}        │
       ├──────────────────────────────────────────────────>│
       │                                                    │
       │                              2. contact_svc        │
       │                                 receives beacon    │
       │                                                    │
       │                              3. Sanitise PAW       │
       │                                 identifier         │
       │                                                    │
       │                              4. Check data_svc     │
       │                                 for existing agent │
       │                                                    │
       │                              5. Agent not found:   │
       │                                 Create new Agent   │
       │                                 object             │
       │                                                    │
       │                              6. Store agent in     │
       │                                 data_svc           │
       │                                                    │
       │                              7. agent.bootstrap()  │
       │                                 - Assign initial   │
       │                                   facts            │
       │                                 - Set trust status │
       │                                                    │
       │                              8. Check for deadman  │
       │                                 abilities          │
       │                                                    │
       │                              9. Fire event:        │
       │                                 agent/added        │
       │                                                    │
       │                              10. Generate initial  │
       │                                  instructions      │
       │                                                    │
       │ 11. Response: {sleep, instructions[], paw}        │
       │<──────────────────────────────────────────────────┤
       │                                                    │
       │ 12. Sleep for jittered interval                   │
       │                                                    │
       │ 13. Next heartbeat begins                         │
       │                                                    │
```

**Key Steps**:

1. Agent sends initial beacon with platform metadata
2. Contact service receives via registered C2 protocol
3. PAW (unique ID) sanitised for security
4. Data service queried for existing agent
5. New agent object created with default configuration
6. Agent stored in object store
7. Bootstrap process assigns default facts (server, group, location)
8. Deadman abilities checked and assigned if enabled
9. Event fired for monitoring and plugin integration
10. Initial instructions generated (typically empty)
11. Response includes sleep timing and instruction list
12. Agent sleeps with jitter before next beacon
13. Heartbeat cycle continues

### Heartbeat Cycle with Instructions

Ongoing heartbeat cycle for instruction delivery and result collection.

```
┌─────────────┐                                    ┌──────────────────┐
│   Agent     │                                    │  Caldera Server  │
└──────┬──────┘                                    └────────┬─────────┘
       │                                                    │
       │ 1. POST /beacon                                   │
       │    Body: {paw, results[], platform, etc.}         │
       ├──────────────────────────────────────────────────>│
       │                                                    │
       │                              2. Update agent       │
       │                                 last_seen timestamp│
       │                                                    │
       │                              3. Process results[]  │
       │                                 for each result:   │
       │                                                    │
       │                              4. Save Result object │
       │                                 to data_svc        │
       │                                                    │
       │                              5. Find operation     │
       │                                 with link_id       │
       │                                                    │
       │                              6. Fire event:        │
       │                                 link/completed     │
       │                                                    │
       │                              7. learning_svc.learn()│
       │                                 - Parse output     │
       │                                 - Extract facts    │
       │                                 - Store facts      │
       │                                                    │
       │                              8. Get active         │
       │                                 operations for     │
       │                                 this agent         │
       │                                                    │
       │                              9. Generate next      │
       │                                 instructions from  │
       │                                 pending links      │
       │                                                    │
       │                              10. Mark links as     │
       │                                  delivered         │
       │                                                    │
       │ 11. Response: {sleep, instructions[]}             │
       │     instructions: [{id, command, executor, ...}]  │
       │<──────────────────────────────────────────────────┤
       │                                                    │
       │ 12. Execute each instruction                      │
       │                                                    │
       │ 13. Collect results and encode                    │
       │                                                    │
       │ 14. Sleep for jittered interval                   │
       │                                                    │
       │ 15. Next heartbeat with results                   │
       │                                                    │
```

**Key Steps**:

1. Agent beacons with previous results
2. Agent metadata updated (last_seen, etc.)
3. Results array processed sequentially
4. Each result stored as Result object
5. Operation located by link ID
6. Link completion event fired
7. Learning service parses output for facts
8. Active operations for agent retrieved
9. Next instructions generated from pending links
10. Links marked as delivered to agent
11. Response contains new instructions
12. Agent executes commands asynchronously
13. Results collected and encoded
14. Sleep period with jitter
15. Cycle repeats

### Trust Verification Flow

Background process monitoring agent trust status.

```
Time: t=0 (Agent Active)
┌─────────────┐                    ┌──────────────────┐
│   Agent     │◄──────heartbeat────┤  Caldera Server  │
│  (Trusted)  │                    │  trust_timer=60s │
└─────────────┘                    └──────────────────┘

Time: t=30s (Agent Still Active)
┌─────────────┐                    ┌──────────────────┐
│   Agent     │◄──────heartbeat────┤  Caldera Server  │
│  (Trusted)  │                    │  last_seen=t+30s │
└─────────────┘                    └──────────────────┘

Time: t=90s (Agent Silent, Trust Expired)
┌─────────────┐                    ┌──────────────────┐
│   Agent     │                    │  Caldera Server  │
│ (Untrusted) │   X (no contact)   │  trust_timer     │
└─────────────┘                    │  exceeded        │
                                   │                  │
                                   │  1. Mark agent   │
                                   │     untrusted    │
                                   │                  │
                                   │  2. Find all ops │
                                   │     with agent   │
                                   │                  │
                                   │  3. Update ops   │
                                   │     untrusted    │
                                   │     agent list   │
                                   └──────────────────┘

Background Monitoring (Continuous):
┌──────────────────────────────────────────────────────┐
│  app_svc.start_sniffer_untrusted_agents()            │
│                                                       │
│  While True:                                          │
│    1. Sleep for untrusted_timer + 1                  │
│    2. Get all trusted agents                         │
│    3. For each agent:                                │
│       - Calculate silence_time                       │
│       - If silence_time > untrusted_timer:           │
│         * Set agent.trusted = 0                      │
│         * Update operations with untrusted agent     │
│    4. Sleep 15 seconds                               │
│    5. Repeat                                          │
└──────────────────────────────────────────────────────┘
```

**Trust Logic**:

- Agents start as `trusted=True` upon registration
- Last trusted heartbeat timestamp tracked
- Background task checks all trusted agents
- Silence time calculated as `now - last_trusted_seen`
- If silence exceeds `untrusted_timer + agent.sleep_max`, agent marked untrusted
- Operations updated to reflect untrusted agent
- Untrusted agents do not receive new links

## Operation Execution Flow

### Operation Creation and Initialisation

```
┌────────────┐                                     ┌──────────────────┐
│   User/API │                                     │  Caldera Server  │
└──────┬─────┘                                     └────────┬─────────┘
       │                                                    │
       │ 1. POST /api/rest                                 │
       │    {index: 'operations', name, adversary,         │
       │     planner, source, agents, ...}                 │
       ├──────────────────────────────────────────────────>│
       │                                                    │
       │                              2. rest_svc.          │
       │                                 create_operation() │
       │                                                    │
       │                              3. Validate adversary,│
       │                                 planner, source    │
       │                                 exist in data_svc  │
       │                                                    │
       │                              4. Create Operation   │
       │                                 object             │
       │                                                    │
       │                              5. Set operation state│
       │                                 = 'running'        │
       │                                                    │
       │                              6. Seed facts from    │
       │                                 source into        │
       │                                 knowledge_svc      │
       │                                                    │
       │                              7. Store operation in │
       │                                 data_svc           │
       │                                                    │
       │                              8. Fire event:        │
       │                                 operation/         │
       │                                 state_changed      │
       │                                                    │
       │                              9. Planner begins     │
       │                                 execution loop     │
       │                                                    │
       │ 10. Response: {operation object with id}          │
       │<──────────────────────────────────────────────────┤
       │                                                    │
```

**Key Steps**:

1. User submits operation creation request
2. REST service handles operation creation
3. Referenced objects validated
4. Operation object created with unique ID
5. State set to 'running' to begin execution
6. Source facts seeded into knowledge base
7. Operation persisted to object store
8. State change event fired
9. Planner execution loop begins
10. Operation object returned to user

### Planner Execution Loop

The planner controls link generation and execution flow.

```
┌──────────────────────────────────────────────────────┐
│  Planner Execution Loop (Atomic Planner Example)     │
└──────────────────────────────────────────────────────┘

State Machine: collection → lateral-movement → exfiltration

┌─────────────────────────────────────────────────────┐
│  Step 1: Begin with first bucket                    │
│  Current bucket: 'collection'                        │
│                                                       │
│  1. planning_svc.get_links(operation, ['collection'],│
│                            agent=None)               │
│     - Retrieve abilities tagged 'collection'         │
│     - Filter by agent capabilities                   │
│     - Filter by requirements (facts available)       │
│     - Generate Link objects with:                    │
│       * Populated fact variables                     │
│       * Selected executor for platform               │
│       * Command with variable substitution           │
│                                                       │
│  2. For each link:                                   │
│     operation.apply(link)                            │
│     - Append link to operation.chain                 │
│     - Link delivered to agent in next heartbeat      │
│                                                       │
│  3. Wait for all links to complete                   │
│     operation.wait_for_links_completion(link_ids)    │
│     - Blocks until all links status != -1            │
│                                                       │
│  4. Check stopping conditions                        │
│     - Objective goals met?                           │
│     - Planner-specific conditions?                   │
│     - User manually stopped?                         │
│                                                       │
│  5. If not stopped, determine next bucket            │
│     next_bucket = planner.default_next_bucket(       │
│         'collection', state_machine)                 │
│     → Returns: 'lateral-movement'                    │
│                                                       │
│  6. Repeat for 'lateral-movement' bucket             │
│                                                       │
│  7. Continue until:                                  │
│     - All buckets exhausted                          │
│     - Stopping conditions met                        │
│     - Operation manually stopped                     │
│     - Timeout reached                                │
│                                                       │
│  8. Set operation.state = 'finished'                 │
│                                                       │
│  9. Fire event: operation/completed                  │
└─────────────────────────────────────────────────────┘
```

**Bucket Execution Strategies**:

**Serial Execution** (batch=False):
- Generate one link at a time
- Wait for completion before next link
- Check stopping conditions after each link
- Slower but allows fine-grained control

**Batch Execution** (batch=True):
- Generate all bucket links immediately
- Push all to operation chain
- Wait for entire batch completion
- Check stopping conditions after batch
- Faster but less granular control

### Link Generation Process

Detailed process for creating executable links from abilities.

```
Input: Ability, Agent, Operation
                  ↓
┌─────────────────────────────────────────────────────┐
│  planning_svc.get_links() Internal Process          │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Filter abilities by bucket tags
       ↓
    [ability1, ability2, ability3]
       │
       │ 2. For each ability, filter executors by agent platform
       ↓
    ability1: {executors: [psh, cmd]} → agent.platform=windows → [psh, cmd]
    ability2: {executors: [sh]} → agent.platform=windows → [] (skip)
       │
       │ 3. For each executor, check requirements
       ↓
    Requirement: {module: 'domain.user.name'}
      → Query knowledge_svc for facts with trait='domain.user.name'
      → Found: [admin, user1, user2]
       │
       │ 4. For each fact combination, create Link
       ↓
    Link 1: ability1, executor=psh, facts={domain.user.name: admin}
    Link 2: ability1, executor=psh, facts={domain.user.name: user1}
    Link 3: ability1, executor=psh, facts={domain.user.name: user2}
       │
       │ 5. Populate link command with facts
       ↓
    Command template: "net user #{domain.user.name}"
    Link 1 command:   "net user admin"
    Link 2 command:   "net user user1"
    Link 3 command:   "net user user2"
       │
       │ 6. Check link not already in operation chain
       ↓
    Filter duplicates based on (ability_id, agent, facts hash)
       │
       │ 7. Apply obfuscator if configured
       ↓
    Obfuscator modifies command syntax (optional)
       │
       │ 8. Return link collection
       ↓
    Output: [Link1, Link2, Link3]
```

**Link Filtering Criteria**:

- Agent executor availability (psh, sh, cmd, proc)
- Agent privilege level (User, Elevated, SYSTEM)
- Fact availability for requirements
- Platform compatibility
- Duplicate prevention
- Trust status (untrusted agents excluded)

## Fact Collection and Usage Flow

### Fact Seeding from Source

```
Operation Creation
       ↓
Source specified
       ↓
┌─────────────────────────────────────────────────────┐
│  Fact Seeding Process                               │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Retrieve Source object from data_svc
       ↓
    Source: {
      name: "basic_knowledge",
      facts: [
        {trait: "host.ip.address", value: "192.168.1.10"},
        {trait: "domain.user.name", value: "admin"}
      ]
    }
       │
       │ 2. Apply source adjustments (if any)
       ↓
    Adjustments modify fact values based on rules
       │
       │ 3. Store facts in knowledge_svc
       ↓
    knowledge_svc.add_fact(fact) for each fact
       │
       │ 4. Facts marked with source=SEEDED
       ↓
    Fact {trait, value, score=100, source=SEEDED}
       │
       │ 5. Facts available for link generation
       ↓
    Links can use seeded facts for requirements
```

### Fact Extraction from Results

```
Agent Returns Result
       ↓
Result: {
  id: "link-uuid",
  output: "base64-encoded-command-output",
  status: 0
}
       ↓
┌─────────────────────────────────────────────────────┐
│  learning_svc.learn() Process                       │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Decode base64 output
       ↓
    Raw output: "Computer: WIN-SERVER\nUser: admin\nIP: 192.168.1.10"
       │
       │ 2. Load all parsers from app/learning/
       ↓
    Parsers: [p_ip.Parser(), p_path.Parser(), ...]
       │
       │ 3. Each parser processes output
       ↓
    p_ip.Parser():
      Regex: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
      Matches: ['192.168.1.10']
      Returns: [Fact(trait='host.ip.address', value='192.168.1.10')]
       │
       │ 4. Collect all extracted facts
       ↓
    Found facts: [
      Fact(trait='host.ip.address', value='192.168.1.10'),
      Fact(trait='domain.user.name', value='admin')
    ]
       │
       │ 5. Check learning model for relationships
       ↓
    Model: {('host.ip.address', 'domain.user.name')}
      → Match found, create relationship
       │
       │ 6. Create Relationship objects
       ↓
    Relationship(
      source=Fact(host.ip.address, 192.168.1.10),
      edge='has',
      target=Fact(domain.user.name, admin)
    )
       │
       │ 7. Store relationships via link
       ↓
    link.create_relationships([relationship], operation)
       │
       │ 8. Store uncorrelated facts
       ↓
    link.save_fact(operation, fact, score=1)
       │
       │ 9. Update link score based on fact count
       ↓
    link.score += len(found_facts)
       │
       │ 10. Facts available for future links
       ↓
    knowledge_svc contains new LEARNED facts
```

**Parser Module Example**:

```python
# app/learning/p_ip.py
import re
from app.objects.secondclass.c_fact import Fact

class Parser:
    def parse(self, blob):
        """Extract IP addresses from command output."""
        regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        matches = re.findall(regex, blob)
        return [Fact(trait='host.ip.address', value=ip) 
                for ip in matches]
```

### Fact Usage in Link Generation

```
Link Generation Request
       ↓
Ability: {
  ability_id: "whoami",
  executors: [{
    command: "whoami /user /priv #{domain.user.name}",
    requirements: [{module: 'domain.user.name'}]
  }]
}
       ↓
┌─────────────────────────────────────────────────────┐
│  Fact Resolution for Link                           │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Parse requirements from ability
       ↓
    Requirements: [Requirement(module='domain.user.name')]
       │
       │ 2. Query knowledge_svc for matching facts
       ↓
    Query: knowledge_svc.get_facts(
             criteria={'trait': 'domain.user.name'}
           )
    Results: [
      Fact(trait='domain.user.name', value='admin', source=SEEDED),
      Fact(trait='domain.user.name', value='user1', source=LEARNED),
      Fact(trait='domain.user.name', value='user2', source=LEARNED)
    ]
       │
       │ 3. For each fact, create Link variant
       ↓
    Link 1: facts={'domain.user.name': 'admin'}
    Link 2: facts={'domain.user.name': 'user1'}
    Link 3: facts={'domain.user.name': 'user2'}
       │
       │ 4. Substitute facts into command template
       ↓
    Command template: "whoami /user /priv #{domain.user.name}"
    Link 1 command:   "whoami /user /priv admin"
    Link 2 command:   "whoami /user /priv user1"
    Link 3 command:   "whoami /user /priv user2"
       │
       │ 5. Links ready for execution
       ↓
    Return: [Link1, Link2, Link3]
```

## SIEM Tagging Workflow

### Orchestrator Plugin Event Processing

The Orchestrator plugin provides automated SIEM tagging for detection correlation.

```
Link Execution Completes
       ↓
event_svc.fire_event(
  exchange='link',
  queue='completed',
  link_id='uuid',
  agent='host$user',
  access='red'
)
       ↓
┌─────────────────────────────────────────────────────┐
│  Orchestrator Plugin Event Handler                  │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Event received by registered observer
       ↓
    orchestrator_svc.handle_link_completed(
      socket, path, services
    )
       │
       │ 2. Parse event data
       ↓
    Event data: {
      link_id: 'uuid',
      agent: 'WIN-SERVER$admin',
      access: 'red',
      metadata: {timestamp: 1612345678.123}
    }
       │
       │ 3. Retrieve link from operation
       ↓
    app_svc.find_link(link_id)
    Link: {
      ability: {technique_id: 'T1087.002'},
      status: 0 (success),
      timestamp: '2025-02-01 10:30:45'
    }
       │
       │ 4. Extract technique information
       ↓
    Technique ID: 'T1087.002'
    Technique Name: 'Domain Account Discovery'
    Tactic: 'Discovery'
       │
       │ 5. Build Elasticsearch query
       ↓
    Query: {
      index: 'winlogbeat-*',
      query: {
        bool: {
          must: [
            {match: {'agent.hostname': 'WIN-SERVER'}},
            {range: {'@timestamp': {
               gte: '2025-02-01T10:30:40',
               lte: '2025-02-01T10:30:50'
            }}}
          ]
        }
      }
    }
       │
       │ 6. Query Elasticsearch for matching events
       ↓
    Results: [
      {_id: 'evt1', _index: 'winlogbeat-2025.02.01'},
      {_id: 'evt2', _index: 'winlogbeat-2025.02.01'}
    ]
       │
       │ 7. For each event, update with technique tag
       ↓
    POST /_update/{index}/{id}
    Body: {
      script: {
        source: "
          if (!ctx._source.containsKey('caldera')) {
            ctx._source.caldera = [:];
          }
          if (!ctx._source.caldera.containsKey('technique_ids')) {
            ctx._source.caldera.technique_ids = [];
          }
          if (!ctx._source.caldera.technique_ids.contains(params.tid)) {
            ctx._source.caldera.technique_ids.add(params.tid);
          }
        ",
        params: {tid: 'T1087.002'}
      }
    }
       │
       │ 8. Log tagging results
       ↓
    Log: "Tagged 2 events for technique T1087.002"
       │
       │ 9. Events now queryable by technique
       ↓
    Query: caldera.technique_ids: "T1087.002"
    → Returns: All events associated with this technique
```

### Detection Coverage Report Generation

```
User Requests Coverage Report
       ↓
POST /plugin/debrief/generate
Body: {operation_id: 'op-uuid'}
       ↓
┌─────────────────────────────────────────────────────┐
│  Detection Coverage Report Section                  │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Retrieve operation from data_svc
       ↓
    Operation: {
      id: 'op-uuid',
      chain: [Link1, Link2, Link3, ...],
      start: '2025-02-01 10:00:00',
      finish: '2025-02-01 11:00:00'
    }
       │
       │ 2. Extract all executed techniques
       ↓
    Techniques: ['T1087.002', 'T1069.001', 'T1210']
       │
       │ 3. For each technique, query Elasticsearch
       ↓
    Query: {
      query: {
        bool: {
          must: [
            {term: {'caldera.technique_ids': 'T1087.002'}},
            {range: {'@timestamp': {
               gte: '2025-02-01T10:00:00',
               lte: '2025-02-01T11:00:00'
            }}}
          ]
        }
      },
      aggs: {
        detections: {
          terms: {field: 'event.code'}
        }
      }
    }
       │
       │ 4. Aggregate detection results
       ↓
    T1087.002: {
      total_events: 15,
      detected: true,
      detection_rules: ['4104', '4688'],
      event_count_by_rule: {'4104': 10, '4688': 5}
    }
    T1069.001: {
      total_events: 0,
      detected: false,
      detection_rules: [],
      event_count_by_rule: {}
    }
       │
       │ 5. Calculate coverage statistics
       ↓
    Total techniques: 3
    Detected techniques: 2
    Coverage percentage: 66.7%
    Detection gaps: ['T1069.001']
       │
       │ 6. Generate PDF report section
       ↓
    Section content:
      - Coverage summary table
      - Detection gap list with recommendations
      - Technique-by-technique breakdown
      - Event distribution charts
       │
       │ 7. Return report to user
       ↓
    PDF file with detection coverage analysis
```

## Report Generation Flow

### PDF Report Creation Process

```
User Requests Report
       ↓
POST /plugin/reporting/generate
Body: {
  operation_id: 'op-uuid',
  report_type: 'operation_summary'
}
       ↓
┌─────────────────────────────────────────────────────┐
│  Reporting Plugin - Main Thread                     │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Validate operation exists
       ↓
    data_svc.locate('operations', match={'id': 'op-uuid'})
       │
       │ 2. Create report job ID
       ↓
    job_id = str(uuid.uuid4())
       │
       │ 3. Submit to thread pool executor
       ↓
    executor.submit(generate_report_worker, job_id, operation)
       │
       │ 4. Return job_id to user immediately
       ↓
    Response: {job_id: 'job-uuid', status: 'processing'}
       │
       │ (Report generation continues in background thread)
       │
┌─────────────────────────────────────────────────────┐
│  Report Worker Thread                               │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Retrieve operation details
       ↓
    Operation: {
      name: 'APT29 Emulation',
      adversary: {...},
      agents: [...],
      chain: [...]
    }
       │
       │ 2. Initialise PDF canvas (ReportLab)
       ↓
    canvas = Canvas('report.pdf', pagesize=A4)
       │
       │ 3. Add branding and header
       ↓
    canvas.drawImage('logo.png', x, y)
    canvas.drawString(x, y, 'Operation Report')
       │
       │ 4. Iterate report sections
       ↓
    sections = [
      ExecutiveSummarySection(),
      OperationDetailsSection(),
      TechniqueBreakdownSection(),
      DetectionCoverageSection(),  # From debrief-elk-detections plugin
      ExfiltrationSection(),
      AppendixSection()
    ]
       │
       │ 5. For each section:
       ↓
    section.generate_section_elements(operation, canvas, **kwargs)
      → Returns: [Paragraph(), Table(), Image(), ...]
       │
       │ 6. Add elements to PDF
       ↓
    for element in elements:
      element.drawOn(canvas, x, y)
      y -= element.height
      if y < margin:
        canvas.showPage()  # New page
        y = page_height - margin
       │
       │ 7. Finalise PDF
       ↓
    canvas.save()
       │
       │ 8. Store report file
       ↓
    file_svc.save_file(
      filename=f'report-{job_id}.pdf',
      content=pdf_bytes,
      location='reports'
    )
       │
       │ 9. Update job status
       ↓
    job_status[job_id] = {
      status: 'completed',
      file_path: 'reports/report-{job_id}.pdf'
    }
       │
       │ 10. User polls for completion
       ↓
    GET /plugin/reporting/status/{job_id}
    Response: {status: 'completed', download_url: '/file/download/...'}
```

### Plugin-Based Report Section Architecture

```
Report Section Interface
       ↓
┌─────────────────────────────────────────────────────┐
│  Custom Report Section (Plugin Extension)           │
│  Example: ELKDetectionCoverageSection               │
└─────────────────────────────────────────────────────┘
       │
       │ Class inherits from ReportSectionInterface
       ↓
    class ELKDetectionCoverageSection(ReportSectionInterface):
        def generate_section_elements(self, operation, 
                                      canvas, **kwargs):
       │
       │ 1. Query Elasticsearch for coverage data
       ↓
        es_client = get_elasticsearch_client()
        techniques = extract_techniques(operation)
        coverage = query_coverage(es_client, techniques)
       │
       │ 2. Build PDF elements
       ↓
        elements = []
        
        # Title
        elements.append(
          Paragraph('Detection Coverage Analysis', 
                   style='Heading1')
        )
        
        # Summary table
        table_data = [
          ['Technique', 'Events', 'Detected'],
          ['T1087.002', '15', '✓'],
          ['T1069.001', '0', '✗']
        ]
        elements.append(Table(table_data))
        
        # Gap recommendations
        for gap in coverage.gaps:
          elements.append(
            Paragraph(f'Detection Gap: {gap.technique_id}',
                     style='Heading2')
          )
          elements.append(
            Paragraph(gap.recommendation,
                     style='BodyText')
          )
       │
       │ 3. Return elements to report generator
       ↓
        return elements
```

## Event Processing Pipeline

### Event Publication Flow

```
Component Action
       ↓
event_svc.fire_event(
  exchange='operation',
  queue='state_changed',
  operation_id='op-uuid',
  old_state='running',
  new_state='paused'
)
       ↓
┌─────────────────────────────────────────────────────┐
│  event_svc.fire_event() Internal Process            │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Set default exchange/queue if not provided
       ↓
    exchange = exchange or 'caldera'
    queue = queue or 'general'
       │
       │ 2. Add timestamp metadata
       ↓
    metadata = {
      timestamp: datetime.now(timezone.utc).timestamp()
    }
    callback_kwargs.update(metadata=metadata)
       │
       │ 3. Build WebSocket URI
       ↓
    uri = f'ws://{websocket_endpoint}/{exchange}/{queue}'
    Example: 'ws://localhost:8888/operation/state_changed'
       │
       │ 4. Notify global event listeners (if any)
       ↓
    if global_listeners:
      for listener in global_listeners:
        listener(f'{exchange}/{queue}', **callback_kwargs)
       │
       │ 5. Serialise event data to JSON
       ↓
    json_data = json.dumps(callback_kwargs)
       │
       │ 6. Connect to WebSocket endpoint
       ↓
    async with websockets.connect(uri) as websocket:
      await websocket.send(json_data)
       │
       │ 7. WebSocket handler receives event
       ↓
    contact_websocket.handler receives message
       │
       │ 8. Handler dispatches to registered callbacks
       ↓
    for handle in handler.handles:
      if handle.tag == f'{exchange}/{queue}':
        await handle.run(socket, path, services)
```

### Event Subscription and Handling

```
Plugin Registration
       ↓
async def enable(services):
  event_svc = services.get('event_svc')
  
  await event_svc.observe_event(
    callback=my_event_handler,
    exchange='operation',
    queue='completed'
  )
       ↓
┌─────────────────────────────────────────────────────┐
│  event_svc.observe_event() Internal Process         │
└─────────────────────────────────────────────────────┘
       │
       │ 1. Build event path
       ↓
    path = f'{exchange}/{queue}'
    Example: 'operation/completed'
       │
       │ 2. Create handle object
       ↓
    handle = _Handle(
      tag='operation/completed',
      callback=my_event_handler
    )
       │
       │ 3. Register with WebSocket contact
       ↓
    ws_contact = await contact_svc.get_contact('websocket')
    ws_contact.handler.handles.append(handle)
       │
       │ 4. Handle ready to receive events
       ↓
┌─────────────────────────────────────────────────────┐
│  Event Received and Dispatched                      │
└─────────────────────────────────────────────────────┘
       │
       │ 1. WebSocket receives message on path
       ↓
    Path: 'operation/completed'
    Data: {operation_id: 'op-uuid', ...}
       │
       │ 2. Handler finds matching handle by tag
       ↓
    handles = [h for h in handler.handles 
               if h.tag == 'operation/completed']
       │
       │ 3. Execute callback for each handle
       ↓
    for handle in handles:
      await handle.callback(socket, path, services)
       │
       │ 4. Callback processes event
       ↓
    async def my_event_handler(socket, path, services):
      data = json.loads(await socket.recv())
      operation_id = data['operation_id']
      # Plugin-specific processing
      await generate_report(operation_id)
```

### Common Event Patterns

**Operation Lifecycle Events**:

```
operation/state_changed: {
  operation_id: 'uuid',
  old_state: 'running',
  new_state: 'paused'
}

operation/completed: {
  operation_id: 'uuid',
  finish_timestamp: '2025-02-01T11:00:00',
  total_links: 45,
  successful_links: 42
}
```

**Agent Lifecycle Events**:

```
agent/added: {
  agent: 'WIN-SERVER$admin',
  paw: 'sanitised-paw-id',
  platform: 'windows',
  executors: ['psh', 'cmd']
}

agent/updated: {
  agent: 'WIN-SERVER$admin',
  paw: 'sanitised-paw-id',
  last_seen: '2025-02-01T10:35:22'
}
```

**Link Execution Events**:

```
link/completed: {
  link_id: 'link-uuid',
  agent: 'WIN-SERVER$admin',
  ability_id: 'T1087.002',
  status: 0,
  access: 'red'
}
```

**System Events**:

```
system/ready: {
  timestamp: '2025-02-01T09:00:00',
  plugins_loaded: ['magma', 'sandcat', 'orchestrator']
}
```

## See Also

### Architecture Documentation

- [System Overview](system-overview.md) - High-level architecture and components
- [Component Architecture](component-architecture.md) - Service and object details

### Implementation References

- [API Reference](/docs/technical/api-reference.md) - REST API endpoints
- [Database Schema](/docs/technical/database-schema.md) - Object relationships

### User Guides

- [Running Operations](/docs/user-guide/operations.md) - Operation management
- [Agent Management](/docs/user-guide/agents.md) - Agent deployment and monitoring
- [Reporting and Analysis](/docs/user-guide/reporting.md) - Report generation

### Plugin Development

- [Plugin Development Guide](/docs/development/plugin-development.md) - Custom plugins
- [Event System Reference](/docs/technical/event-system.md) - Event patterns
- [Orchestrator Plugin](/docs/plugins/orchestrator-troubleshooting.md) - SIEM integration
