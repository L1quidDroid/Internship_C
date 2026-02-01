# API Reference

## Overview

The Caldera REST API provides programmatic access to the Caldera platform, enabling automation of red team operations, agent management, and data collection. The API follows RESTful principles and returns JSON-formatted responses.

This reference documents the v2 API endpoints, which provide comprehensive access to all core Caldera functionality including operations, agents, abilities, adversaries, and knowledge management.

## Authentication

The Caldera API supports two authentication methods:

### API Key Authentication

API key authentication uses a header-based approach for programmatic access. Include your API key in the request header:

**Header Name:** `KEY`

**Example Request:**
```bash
curl -H "KEY: your-api-key-here" http://localhost:8888/api/v2/agents
```

There are two types of API keys configured in Caldera:

- **Red Team API Key** (`api_key_red`): Full access permissions for red team operations
- **Blue Team API Key** (`api_key_blue`): Limited access for blue team defensive operations

API keys are configured in the main configuration file.

### Session-Based Authentication

Session-based authentication uses encrypted cookies after logging in through the web interface. This method is primarily used for browser-based access and maintains session state using the `API_SESSION` cookie.

Once authenticated, the session is maintained automatically by the browser. To log out, use the logout endpoint which clears the session cookie.

### Permission Levels

Caldera uses a permission-based access control system:

- **RED**: Full access to offensive operations and all resources
- **BLUE**: Limited access for defensive monitoring
- **APP**: Basic application access

Permissions are checked for each API request. Requests with invalid credentials receive HTTP 401 Unauthorised responses, while requests with insufficient permissions receive HTTP 403 Forbidden responses.

## Base URL

```
http://localhost:8888/api/v2
```

Replace `localhost:8888` with your Caldera server address and port. The default port is 8888.

## Common Query Parameters

Many endpoints support common query parameters for filtering and customisation:

### BaseGetAllQuerySchema

Used for retrieving lists of objects:

- `include`: Comma-separated list of fields to include in the response
- `exclude`: Comma-separated list of fields to exclude from the response
- `sort`: Field name to sort results by

### BaseGetOneQuerySchema

Used for retrieving single objects:

- `include`: Comma-separated list of fields to include in the response
- `exclude`: Comma-separated list of fields to exclude from the response

## Response Format

All API responses return JSON-formatted data. Successful responses return HTTP 200 OK (or 201 Created, 204 No Content where appropriate) with the requested data. Error responses include appropriate HTTP status codes and error details.

## Endpoints

### Health

#### GET /health

Retrieve the system health status and information about the Caldera instance.

**Description:** Returns the status of Caldera including version information and loaded plugins.

**Authentication Required:** Yes

**Query Parameters:** None

**Response Schema:**
```json
{
  "application": "Caldera",
  "version": "string",
  "access": "string",
  "plugins": [
    {
      "name": "string",
      "description": "string",
      "directory": "string",
      "enabled": boolean
    }
  ]
}
```

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/health
```

**Example Response:**
```json
{
  "application": "Caldera",
  "version": "4.2.0",
  "access": "red",
  "plugins": [
    {
      "name": "stockpile",
      "description": "A collection of abilities",
      "enabled": true
    }
  ]
}
```

---

### Agents

Agents are deployed endpoints that receive and execute commands from Caldera operations.

#### GET /agents

Retrieve all agents registered with Caldera.

**Description:** Returns a list of all stored agents with their current status and properties.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of agent objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents
```

**Response Fields:**
- `paw`: Unique agent identifier
- `group`: Agent group name
- `architecture`: System architecture
- `platform`: Operating system platform
- `executor`: Command executor type
- `privilege`: Privilege level
- `username`: User context
- `location`: Agent file path
- `pid`: Process ID
- `ppid`: Parent process ID
- `trusted`: Trust status
- `sleep_min`: Minimum sleep interval in seconds
- `sleep_max`: Maximum sleep interval in seconds
- `watchdog`: Watchdog timer value
- `pending_contact`: Pending contact name

#### GET /agents/{paw}

Retrieve a specific agent by its PAW (unique identifier).

**Description:** Returns detailed information about a specific agent.

**Authentication Required:** Yes

**Path Parameters:**
- `paw` (required): ID of the agent to retrieve

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/agents/abc123
```

#### POST /agents

Create a new agent registration.

**Description:** Registers a new agent with Caldera. This is typically called by the agent itself during initial beacon.

**Authentication Required:** Yes

**Request Body Schema (AgentSchema):**
```json
{
  "paw": "string",
  "group": "string",
  "architecture": "string",
  "platform": "string",
  "executor": "string",
  "privilege": "string",
  "username": "string",
  "location": "string",
  "pid": integer,
  "ppid": integer,
  "server": "string",
  "host": "string",
  "contact": "string",
  "exe_name": "string"
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"paw":"new-agent","group":"red","platform":"linux"}' \
  http://localhost:8888/api/v2/agents
```

#### PATCH /agents/{paw}

Update an existing agent's properties.

**Description:** Modify specific attributes of an agent. Only certain fields can be updated.

**Authentication Required:** Yes

**Path Parameters:**
- `paw` (required): ID of the agent to update

**Updatable Fields:**
- `group`: Agent group
- `trusted`: Trust status (boolean)
- `sleep_min`: Minimum sleep interval
- `sleep_max`: Maximum sleep interval
- `watchdog`: Watchdog timer
- `pending_contact`: Pending contact name

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"sleep_min":30,"sleep_max":60}' \
  http://localhost:8888/api/v2/agents/abc123
```

#### PUT /agents/{paw}

Create or update an agent.

**Description:** Updates an existing agent or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `paw` (required): ID of the agent

**Request Body Schema:** AgentSchema (partial)

#### DELETE /agents/{paw}

Delete an agent.

**Description:** Removes an agent from the system.

**Authentication Required:** Yes

**Path Parameters:**
- `paw` (required): ID of the agent to delete

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/agents/abc123
```

#### GET /deploy_commands

Retrieve all deployment commands.

**Description:** Returns deployment commands for all abilities, organised by ability ID.

**Authentication Required:** Yes

**Response Schema:** Dictionary of deployment commands keyed by ability ID

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/deploy_commands
```

#### GET /deploy_commands/{ability_id}

Retrieve deployment commands for a specific ability.

**Description:** Returns the deployment commands associated with a given ability.

**Authentication Required:** Yes

**Path Parameters:**
- `ability_id` (required): ID of the ability

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/deploy_commands/abc-123-def
```

---

### Operations

Operations represent red team attack campaigns executed by Caldera.

#### GET /operations

Retrieve all operations.

**Description:** Returns all Caldera operations from memory with their current status.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of operation objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/operations
```

**Response Fields:**
- `id`: Unique operation identifier (UUID)
- `name`: Operation name
- `state`: Current state (running, paused, finished, etc.)
- `autonomous`: Autonomous operation mode (boolean)
- `adversary`: Adversary profile used
- `planner`: Planning algorithm
- `source`: Fact source
- `jitter`: Jitter configuration
- `visibility`: Visibility settings
- `obfuscator`: Obfuscation method
- `chain`: Execution chain of links

#### GET /operations/summary

Retrieve operations with alternate property selection.

**Description:** Returns all operations with an alternate set of properties including aggregated agent and host information.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response:** Operations with additional `agents` and `hosts` fields, excluding `chain`, `host_group`, `source`, and `visibility`.

#### GET /operations/{id}

Retrieve a specific operation by ID.

**Description:** Returns detailed information about a specific operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/12345-uuid-67890
```

#### POST /operations

Create a new operation.

**Description:** Creates a new Caldera operation with the specified configuration.

**Authentication Required:** Yes

**Required Fields:**
- `name`: Operation name
- `adversary.adversary_id`: Adversary profile ID
- `planner.id`: Planner ID
- `source.id`: Source ID

**Request Body Schema (OperationSchema):**
```json
{
  "name": "string",
  "adversary": {
    "adversary_id": "string"
  },
  "planner": {
    "id": "string"
  },
  "source": {
    "id": "string"
  },
  "state": "string",
  "group": "string",
  "autonomous": boolean,
  "obfuscator": "string",
  "jitter": "string",
  "visibility": integer
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Red Team Operation",
    "adversary": {"adversary_id": "hunter"},
    "planner": {"id": "atomic"},
    "source": {"id": "basic"}
  }' \
  http://localhost:8888/api/v2/operations
```

#### PATCH /operations/{id}

Update an operation.

**Description:** Modify operation properties such as state, autonomous mode, or obfuscator.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Updatable Fields:**
- `state`: Operation state (running, paused, finished)
- `autonomous`: Autonomous mode (boolean)
- `obfuscator`: Obfuscator name

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state":"running","autonomous":true}' \
  http://localhost:8888/api/v2/operations/12345-uuid-67890
```

#### DELETE /operations/{id}

Delete an operation.

**Description:** Removes an operation and associated facts and relationships.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/12345-uuid-67890
```

#### POST /operations/{id}/report

Retrieve operation report.

**Description:** Generates and retrieves a detailed report for the specified operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Request Body:**
```json
{
  "enable_agent_output": boolean
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"enable_agent_output":true}' \
  http://localhost:8888/api/v2/operations/12345-uuid-67890/report
```

#### POST /operations/{id}/event-logs

Retrieve operation event logs.

**Description:** Returns event logs for the specified operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Request Body:**
```json
{
  "enable_agent_output": boolean
}
```

#### GET /operations/{id}/links

Retrieve all execution links for an operation.

**Description:** Returns all command execution links associated with an operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of link objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/12345-uuid-67890/links
```

#### GET /operations/{id}/links/{link_id}

Retrieve a specific link from an operation.

**Description:** Returns details of a specific execution link.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation
- `link_id` (required): UUID of the link

**Query Parameters:** BaseGetOneQuerySchema

#### GET /operations/{id}/links/{link_id}/result

Retrieve link execution result.

**Description:** Returns the result data from a specific link execution.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation
- `link_id` (required): UUID of the link

**Query Parameters:** BaseGetOneQuerySchema

**Response:** Dictionary containing the link and its results

#### PATCH /operations/{id}/links/{link_id}

Update a link within an operation.

**Description:** Modify the command or status of a specific link.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation
- `link_id` (required): UUID of the link

**Updatable Fields:**
- `command`: Command string
- `status`: Status code (integer)

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"status":0}' \
  http://localhost:8888/api/v2/operations/12345-uuid-67890/links/link-uuid
```

#### POST /operations/{id}/potential-links

Create a potential link for execution.

**Description:** Creates a potential link that can be executed by an agent.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Required Fields:**
- `paw`: Agent identifier
- `executor`: Executor type
- `ability`: Ability object

**Request Body Schema (LinkSchema)**

#### GET /operations/{id}/potential-links

Retrieve all potential links for an operation.

**Description:** Returns all potential links that could be executed.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation

**Query Parameters:** BaseGetAllQuerySchema

#### GET /operations/{id}/potential-links/{paw}

Retrieve potential links filtered by agent PAW.

**Description:** Returns potential links for a specific agent within an operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the operation
- `paw` (required): Agent PAW identifier

**Query Parameters:** BaseGetOneQuerySchema

---

### Abilities

Abilities represent individual attack techniques that can be executed by agents.

#### GET /abilities

Retrieve all abilities.

**Description:** Returns a list of all available abilities in the system.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of ability objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/abilities
```

**Response Fields:**
- `ability_id`: Unique ability identifier (UUID)
- `name`: Ability name
- `description`: Description of what the ability does
- `tactic`: MITRE ATT&CK tactic
- `technique_id`: MITRE ATT&CK technique ID
- `technique_name`: MITRE ATT&CK technique name
- `executors`: Array of executor configurations for different platforms
- `requirements`: Fact requirements for execution
- `privilege`: Required privilege level
- `access`: Access control settings

#### GET /abilities/{ability_id}

Retrieve a specific ability by ID.

**Description:** Returns detailed information about a specific ability.

**Authentication Required:** Yes

**Path Parameters:**
- `ability_id` (required): UUID of the ability

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/abilities/abc-123-def
```

#### POST /abilities

Create a new ability.

**Description:** Creates a new ability using the provided configuration.

**Authentication Required:** Yes

**Required Fields:**
- `name`: Ability name
- `tactic`: MITRE ATT&CK tactic
- `technique_name`: MITRE ATT&CK technique name
- `technique_id`: MITRE ATT&CK technique ID
- `executors`: Array of executor objects

**Request Body Schema (AbilitySchema):**
```json
{
  "name": "string",
  "description": "string",
  "tactic": "string",
  "technique_id": "string",
  "technique_name": "string",
  "executors": [
    {
      "platform": "string",
      "name": "string",
      "command": "string",
      "cleanup": "string",
      "parsers": []
    }
  ],
  "privilege": "string",
  "requirements": []
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Discovery",
    "tactic": "discovery",
    "technique_id": "T1082",
    "technique_name": "System Information Discovery",
    "executors": [
      {
        "platform": "linux",
        "name": "sh",
        "command": "uname -a"
      }
    ]
  }' \
  http://localhost:8888/api/v2/abilities
```

#### PUT /abilities/{ability_id}

Create or replace an ability.

**Description:** Replaces an existing ability or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `ability_id` (required): UUID of the ability

**Request Body Schema:** AbilitySchema (partial)

#### PATCH /abilities/{ability_id}

Update an existing ability.

**Description:** Modifies specific fields of an ability. Cannot update `ability_id`, `requirements`, `additional_info`, or `access`.

**Authentication Required:** Yes

**Path Parameters:**
- `ability_id` (required): UUID of the ability

**Request Body Schema:** AbilitySchema (partial, excludes restricted fields)

#### DELETE /abilities/{ability_id}

Delete an ability.

**Description:** Removes an ability from the system.

**Authentication Required:** Yes

**Path Parameters:**
- `ability_id` (required): UUID of the ability

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/abilities/abc-123-def
```

---

### Adversaries

Adversaries represent attack profiles containing sequences of abilities.

#### GET /adversaries

Retrieve all adversaries.

**Description:** Returns a list of all available adversaries including their atomic ordering and descriptions.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of adversary objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/adversaries
```

**Response Fields:**
- `adversary_id`: Unique adversary identifier
- `name`: Adversary name
- `description`: Adversary description
- `atomic_ordering`: Ordered list of ability IDs
- `objective`: Associated objective ID
- `tags`: Adversary tags
- `plugin`: Plugin name

#### GET /adversaries/{adversary_id}

Retrieve a specific adversary by ID.

**Description:** Returns detailed information about a specific adversary.

**Authentication Required:** Yes

**Path Parameters:**
- `adversary_id` (required): UUID of the adversary

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/adversaries/hunter
```

#### POST /adversaries

Create a new adversary.

**Description:** Creates a new adversary profile.

**Authentication Required:** Yes

**Request Body Schema (AdversarySchema):**
```json
{
  "name": "string",
  "description": "string",
  "atomic_ordering": ["ability_id1", "ability_id2"],
  "objective": "objective_id",
  "tags": ["tag1", "tag2"]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Adversary",
    "description": "Custom attack profile",
    "atomic_ordering": ["ability-1", "ability-2"]
  }' \
  http://localhost:8888/api/v2/adversaries
```

#### PATCH /adversaries/{adversary_id}

Update an existing adversary.

**Description:** Modifies adversary properties. Cannot update `adversary_id`.

**Authentication Required:** Yes

**Path Parameters:**
- `adversary_id` (required): UUID of the adversary

**Request Body Schema:** AdversarySchema (partial, excludes `adversary_id`)

#### PUT /adversaries/{adversary_id}

Create or update an adversary.

**Description:** Updates an existing adversary or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `adversary_id` (required): UUID of the adversary

**Request Body Schema:** AdversarySchema (partial)

#### DELETE /adversaries/{adversary_id}

Delete an adversary.

**Description:** Removes an adversary from the system.

**Authentication Required:** Yes

**Path Parameters:**
- `adversary_id` (required): UUID of the adversary

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/adversaries/custom-adversary
```

---

### Planners

Planners determine the logic for selecting and executing abilities during operations.

#### GET /planners

Retrieve all planners.

**Description:** Returns all available planner algorithms.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of planner objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/planners
```

**Response Fields:**
- `planner_id`: Unique planner identifier
- `name`: Planner name
- `description`: Planner description
- `module`: Python module path
- `params`: Planner parameters
- `stopping_conditions`: Stopping condition rules

#### GET /planners/{planner_id}

Retrieve a specific planner by ID.

**Description:** Returns detailed information about a specific planner.

**Authentication Required:** Yes

**Path Parameters:**
- `planner_id` (required): UUID of the planner

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/planners/atomic
```

#### PATCH /planners/{planner_id}

Update an existing planner.

**Description:** Modifies planner configuration parameters.

**Authentication Required:** Yes

**Path Parameters:**
- `planner_id` (required): UUID of the planner

**Request Body Schema:** PlannerSchema (partial)

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"params":{"max_iterations":50}}' \
  http://localhost:8888/api/v2/planners/atomic
```

---

### Objectives

Objectives define goals and completion criteria for operations.

#### GET /objectives

Retrieve all objectives.

**Description:** Returns all objectives with their goals and completion criteria.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of objective objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/objectives
```

**Response Fields:**
- `id`: Unique objective identifier (UUID)
- `name`: Objective name
- `description`: Objective description
- `goals`: Array of goal objects
- `percentage`: Completion percentage

#### GET /objectives/{id}

Retrieve a specific objective by ID.

**Description:** Returns detailed information about a specific objective.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the objective

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/objectives/objective-uuid
```

#### POST /objectives

Create a new objective.

**Description:** Creates a new objective with specified goals.

**Authentication Required:** Yes

**Request Body Schema (ObjectiveSchema):**
```json
{
  "name": "string",
  "description": "string",
  "goals": [
    {
      "target": "string",
      "count": integer,
      "achieved": boolean,
      "operator": "string",
      "value": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Exfiltration",
    "description": "Exfiltrate sensitive data",
    "goals": [{"target":"exfil.file","count":5}]
  }' \
  http://localhost:8888/api/v2/objectives
```

#### PATCH /objectives/{id}

Update an existing objective.

**Description:** Modifies objective properties. Cannot update `id` or `percentage`.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the objective

**Request Body Schema:** ObjectiveSchema (partial, excludes `id` and `percentage`)

#### PUT /objectives/{id}

Create or update an objective.

**Description:** Updates an existing objective or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the objective

**Request Body Schema:** ObjectiveSchema (partial)

---

### Facts

Facts represent pieces of discovered information during operations.

#### GET /facts

Retrieve facts by criteria.

**Description:** Returns facts matching the specified filter criteria.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:**
```json
{
  "found": [
    {
      "trait": "string",
      "value": "string",
      "source": "string",
      "score": integer,
      "collected_by": ["string"],
      "technique_id": "string",
      "origin_type": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/facts
```

**Response Fields:**
- `trait`: Fact trait/type
- `value`: Fact value
- `source`: Source operation ID
- `score`: Fact score/confidence
- `collected_by`: Array of links that collected this fact
- `technique_id`: Associated MITRE technique
- `origin_type`: Origin type (LEARNED or USER)

#### GET /facts/{operation_id}

Retrieve facts associated with an operation.

**Description:** Returns facts either user-generated or learned during a specific operation.

**Authentication Required:** Yes

**Path Parameters:**
- `operation_id` (required): UUID of the operation

**Query Parameters:** BaseGetAllQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/facts/operation-uuid
```

#### POST /facts

Create a new fact.

**Description:** Adds a user-created fact to the knowledge base.

**Authentication Required:** Yes

**Request Body Schema (FactSchema):**
```json
{
  "trait": "string",
  "value": "string",
  "source": "string"
}
```

**Response:**
```json
{
  "added": [fact_objects]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "trait": "host.name",
    "value": "webserver-01",
    "source": "operation-uuid"
  }' \
  http://localhost:8888/api/v2/facts
```

#### DELETE /facts

Delete facts by criteria.

**Description:** Removes all facts matching the specified criteria.

**Authentication Required:** Yes

**Request Body Schema:** FactSchema (partial)

**Response:**
```json
{
  "removed": [fact_objects]
}
```

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"trait":"host.name","value":"old-host"}' \
  http://localhost:8888/api/v2/facts
```

#### PATCH /facts

Update existing facts.

**Description:** Updates all facts matching the criteria with the specified updates.

**Authentication Required:** Yes

**Request Body Schema:**
```json
{
  "criteria": {
    "trait": "string",
    "value": "string"
  },
  "updates": {
    "field": "new_value"
  }
}
```

**Response:**
```json
{
  "updated": [fact_objects]
}
```

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {"trait":"host.name"},
    "updates": {"score":100}
  }' \
  http://localhost:8888/api/v2/facts
```

---

### Relationships

Relationships represent connections between facts in the knowledge base.

#### GET /relationships

Retrieve relationships by criteria.

**Description:** Returns relationships matching the specified filter criteria.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:**
```json
{
  "found": [
    {
      "source": "fact_object",
      "edge": "string",
      "target": "fact_object",
      "origin": "string",
      "score": integer
    }
  ]
}
```

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/relationships
```

**Response Fields:**
- `source`: Source fact object
- `edge`: Relationship type/edge label
- `target`: Target fact object (optional)
- `origin`: Origin operation ID
- `score`: Relationship score/confidence

#### GET /relationships/{operation_id}

Retrieve relationships associated with an operation.

**Description:** Returns relationships either user-generated or learned during a specific operation.

**Authentication Required:** Yes

**Path Parameters:**
- `operation_id` (required): UUID of the operation

**Query Parameters:** BaseGetAllQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/relationships/operation-uuid
```

#### POST /relationships

Create a new relationship.

**Description:** Adds a user-created relationship to the knowledge base.

**Authentication Required:** Yes

**Request Body Schema (RelationshipSchema):**
```json
{
  "source": {
    "trait": "string",
    "value": "string"
  },
  "edge": "string",
  "target": {
    "trait": "string",
    "value": "string"
  },
  "origin": "string"
}
```

**Response:**
```json
{
  "added": [relationship_objects]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {"trait":"host.name","value":"server-01"},
    "edge": "has_ip",
    "target": {"trait":"host.ip","value":"192.168.1.10"},
    "origin": "operation-uuid"
  }' \
  http://localhost:8888/api/v2/relationships
```

#### DELETE /relationships

Delete relationships by criteria.

**Description:** Removes all relationships matching the specified criteria.

**Authentication Required:** Yes

**Request Body Schema:** RelationshipSchema (partial)

**Response:**
```json
{
  "removed": [relationship_objects]
}
```

#### PATCH /relationships

Update existing relationships.

**Description:** Updates all relationships matching the criteria with the specified updates.

**Authentication Required:** Yes

**Request Body Schema:**
```json
{
  "criteria": {
    "edge": "string"
  },
  "updates": {
    "field": "new_value"
  }
}
```

**Response:**
```json
{
  "updated": [relationship_objects]
}
```

---

### Sources

Fact sources provide initial facts to seed operations.

#### GET /sources

Retrieve all fact sources.

**Description:** Returns all fact sources including custom-created ones.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of source objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/sources
```

**Response Fields:**
- `id`: Unique source identifier (UUID)
- `name`: Source name
- `facts`: Array of fact objects
- `adjustments`: Source adjustments
- `plugin`: Plugin name

#### GET /sources/{id}

Retrieve a specific fact source by ID.

**Description:** Returns detailed information about a specific fact source.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the source

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/sources/basic
```

#### POST /sources

Create a new fact source.

**Description:** Creates a new fact source with the specified facts.

**Authentication Required:** Yes

**Request Body Schema (SourceSchema):**
```json
{
  "name": "string",
  "facts": [
    {
      "trait": "string",
      "value": "string"
    }
  ]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Source",
    "facts": [
      {"trait":"domain.name","value":"example.com"}
    ]
  }' \
  http://localhost:8888/api/v2/sources
```

#### PATCH /sources/{id}

Update an existing fact source.

**Description:** Modifies fact source properties. Cannot update `id` or `adjustments`.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the source

**Request Body Schema:** SourceSchema (partial)

#### PUT /sources/{id}

Create or update a fact source.

**Description:** Updates an existing fact source or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the source

**Request Body Schema:** SourceSchema (partial)

#### DELETE /sources/{id}

Delete a fact source.

**Description:** Removes a fact source and associated facts and relationships.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the source

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/sources/custom-source
```

---

### Contacts

Contacts represent communication channels between agents and the Caldera server.

#### GET /contacts

Retrieve available contact reports.

**Description:** Returns a list of contacts that at least one agent has beaconed to.

**Authentication Required:** Yes

**Response Schema:** Array of contact names

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/contacts
```

#### GET /contacts/{name}

Retrieve beacon report for a specific contact.

**Description:** Returns a list of beacons made by agents to the specified contact.

**Authentication Required:** Yes

**Path Parameters:**
- `name` (required): Name of the contact (e.g., HTTP, TCP, etc.)

**Response Schema:**
```json
[
  {
    "paw": "string",
    "instructions": ["command1", "command2"],
    "date": "string"
  }
]
```

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/contacts/HTTP
```

**Response Fields:**
- `paw`: Agent PAW identifier
- `instructions`: Array of commands executed since last beacon
- `date`: UTC date/time string

#### GET /contactlist

Retrieve list of available contacts.

**Description:** Returns all configured contact mechanisms.

**Authentication Required:** Yes

**Response Schema:**
```json
[
  {
    "name": "string",
    "description": "string"
  }
]
```

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/contactlist
```

---

### Plugins

Plugins extend Caldera functionality with additional features.

#### GET /plugins

Retrieve all plugins.

**Description:** Returns all available plugins including their active status.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of plugin objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/plugins
```

**Response Fields:**
- `name`: Plugin name
- `description`: Plugin description
- `directory`: Plugin directory path
- `enabled`: Active status (boolean)
- `address`: Plugin endpoint address

#### GET /plugins/{name}

Retrieve a specific plugin by name.

**Description:** Returns detailed information about a specific plugin.

**Authentication Required:** Yes

**Path Parameters:**
- `name` (required): Name of the plugin

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/plugins/stockpile
```

---

### Configuration

Configuration endpoints manage Caldera system settings.

#### GET /config/{name}

Retrieve configuration by name.

**Description:** Returns the specified configuration file contents.

**Authentication Required:** Yes

**Path Parameters:**
- `name` (required): Name of the configuration file (e.g., main, agents)

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/config/main
```

#### PATCH /config/main

Update main configuration.

**Description:** Modifies properties in the main configuration file.

**Authentication Required:** Yes

**Request Body Schema:**
```json
{
  "prop": "string",
  "value": "any"
}
```

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"prop":"app.contact.http","value":"0.0.0.0"}' \
  http://localhost:8888/api/v2/config/main
```

**Error Responses:**
- HTTP 403 Forbidden: Property update not allowed
- HTTP 404 Not Found: Configuration not found

#### PATCH /config/agents

Update agent configuration.

**Description:** Modifies the global agent configuration settings.

**Authentication Required:** Yes

**Request Body Schema (AgentConfigUpdateSchema):**
```json
{
  "sleep_min": integer,
  "sleep_max": integer,
  "watchdog": integer,
  "untrusted_timer": integer,
  "implant_name": "string",
  "bootstrap_abilities": ["string"]
}
```

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"sleep_min":30,"sleep_max":60}' \
  http://localhost:8888/api/v2/config/agents
```

---

### Obfuscators

Obfuscators modify command syntax to evade detection.

#### GET /obfuscators

Retrieve all obfuscators.

**Description:** Returns all stored obfuscators available in the system.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of obfuscator objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/obfuscators
```

**Response Fields:**
- `name`: Obfuscator name
- `description`: Obfuscator description
- `module`: Python module path

#### GET /obfuscators/{name}

Retrieve a specific obfuscator by name.

**Description:** Returns detailed information about a specific obfuscator.

**Authentication Required:** Yes

**Path Parameters:**
- `name` (required): Name of the obfuscator

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/obfuscators/base64
```

---

### Payloads

Payloads are files used by abilities during execution.

#### GET /payloads

Retrieve all payloads.

**Description:** Returns a list of all stored payload files.

**Authentication Required:** Yes

**Query Parameters:**
- `sort` (boolean): Sort payload list alphabetically
- `exclude_plugins` (boolean): Exclude payloads from plugins
- `add_path` (boolean): Include full path in response

**Response Schema:** Array of payload filenames

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/payloads?sort=true
```

**Example Response:**
```json
[
  "payload1.exe",
  "payload2.sh",
  "config.yml"
]
```

#### POST /payloads

Upload a new payload.

**Description:** Uploads a payload file to the Caldera server.

**Authentication Required:** Yes

**Request:** Multipart form data with file field

**Response Schema:**
```json
{
  "payloads": ["filename"]
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -F "file=@/path/to/payload.exe" \
  http://localhost:8888/api/v2/payloads
```

**Notes:**
- File names are sanitised to prevent directory traversal
- Duplicate file names are automatically renamed with a numeric suffix
- Symbolic links are not allowed

#### DELETE /payloads/{name}

Delete a payload.

**Description:** Removes a payload file from the server.

**Authentication Required:** Yes

**Path Parameters:**
- `name` (required): Name of the payload file

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/payloads/old-payload.exe
```

**Error Responses:**
- HTTP 400 Bad Request: Invalid file name
- HTTP 403 Forbidden: Permission denied
- HTTP 404 Not Found: Payload not found

---

### Schedules

Schedules automate the execution of operations at specified times.

#### GET /schedules

Retrieve all schedules.

**Description:** Returns all stored scheduled operations.

**Authentication Required:** Yes

**Query Parameters:** BaseGetAllQuerySchema

**Response Schema:** Array of schedule objects

**Example Request:**
```bash
curl -H "KEY: your-api-key" http://localhost:8888/api/v2/schedules
```

**Response Fields:**
- `id`: Unique schedule identifier (UUID)
- `schedule`: Cron-style schedule expression
- `task`: Operation configuration object

#### GET /schedules/{id}

Retrieve a specific schedule by ID.

**Description:** Returns detailed information about a specific schedule.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the schedule

**Query Parameters:** BaseGetOneQuerySchema

**Example Request:**
```bash
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/schedules/schedule-uuid
```

#### POST /schedules

Create a new schedule.

**Description:** Creates a new scheduled operation.

**Authentication Required:** Yes

**Request Body Schema (ScheduleSchema):**
```json
{
  "schedule": "string",
  "task": {
    "name": "string",
    "adversary": {"adversary_id": "string"},
    "planner": {"id": "string"},
    "source": {"id": "string"}
  }
}
```

**Example Request:**
```bash
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 2 * * *",
    "task": {
      "name": "Nightly Scan",
      "adversary": {"adversary_id": "hunter"},
      "planner": {"id": "atomic"},
      "source": {"id": "basic"}
    }
  }' \
  http://localhost:8888/api/v2/schedules
```

#### PATCH /schedules/{id}

Update an existing schedule.

**Description:** Modifies schedule properties.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the schedule

**Updatable Fields:**
- `schedule`: Cron expression
- `task.autonomous`: Autonomous mode
- `task.state`: Operation state
- `task.obfuscator`: Obfuscator name

**Example Request:**
```bash
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"schedule":"0 3 * * *"}' \
  http://localhost:8888/api/v2/schedules/schedule-uuid
```

#### PUT /schedules/{id}

Create or update a schedule.

**Description:** Updates an existing schedule or creates a new one if it doesn't exist.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the schedule

**Request Body Schema:** ScheduleSchema (partial, excludes `id`)

#### DELETE /schedules/{id}

Delete a schedule.

**Description:** Removes a scheduled operation.

**Authentication Required:** Yes

**Path Parameters:**
- `id` (required): UUID of the schedule

**Response:** HTTP 204 No Content

**Example Request:**
```bash
curl -X DELETE -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/schedules/schedule-uuid
```

---

## Error Codes

The API uses standard HTTP status codes to indicate success or failure:

### Success Codes

- **200 OK**: Request succeeded, response contains requested data
- **201 Created**: Resource successfully created
- **204 No Content**: Request succeeded, no response body

### Client Error Codes

- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorised**: Authentication required or invalid credentials
- **403 Forbidden**: Authenticated but insufficient permissions
- **404 Not Found**: Requested resource does not exist

### Server Error Codes

- **500 Internal Server Error**: Unexpected server error occurred

### Error Response Format

Error responses include a JSON body with details:

```json
{
  "error": "Error message",
  "details": {
    "field": "additional context"
  }
}
```

## Rate Limiting

The Caldera API does not implement explicit rate limiting. However, excessive requests may impact server performance. Implement appropriate delays between requests in automated scripts to avoid overloading the server.

## Best Practises

### Authentication

- Store API keys securely and never commit them to version control
- Use environment variables for API key configuration
- Rotate API keys periodically
- Use session-based authentication for browser-based integrations

### Request Optimisation

- Use `include` and `exclude` query parameters to retrieve only necessary fields
- Implement pagination for large result sets when available
- Cache responses where appropriate to reduce redundant requests

### Error Handling

- Implement proper error handling for all API requests
- Check HTTP status codes before processing response data
- Log errors with sufficient context for troubleshooting
- Implement retry logic with exponential backoff for transient failures

### Data Validation

- Validate input data before sending to the API
- Follow schema requirements for request bodies
- Use UUIDs for resource identifiers where required
- Sanitise user input to prevent injection attacks

### Operation Management

- Monitor operation state transitions
- Clean up completed operations to free resources
- Use appropriate planners for different attack scenarios
- Set reasonable jitter and sleep values for agents

### Security Considerations

- Use HTTPS in production environments
- Implement network segmentation to restrict API access
- Monitor API access logs for suspicious activity
- Follow the principle of least privilege for API keys
- Regularly audit agent and operation configurations

## Examples

### Complete Operation Workflow

```bash
# 1. Create an operation
OPERATION=$(curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Reconnaissance Operation",
    "adversary": {"adversary_id": "hunter"},
    "planner": {"id": "atomic"},
    "source": {"id": "basic"},
    "group": "red"
  }' \
  http://localhost:8888/api/v2/operations)

# Extract operation ID
OP_ID=$(echo $OPERATION | jq -r '.id')

# 2. Start the operation
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state": "running"}' \
  http://localhost:8888/api/v2/operations/$OP_ID

# 3. Monitor operation links
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/operations/$OP_ID/links

# 4. Get operation report
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"enable_agent_output": true}' \
  http://localhost:8888/api/v2/operations/$OP_ID/report

# 5. Stop the operation
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"state": "finished"}' \
  http://localhost:8888/api/v2/operations/$OP_ID
```

### Managing Agents

```bash
# List all agents
curl -H "KEY: your-api-key" \
  http://localhost:8888/api/v2/agents

# Update agent sleep interval
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"sleep_min": 30, "sleep_max": 60}' \
  http://localhost:8888/api/v2/agents/agent-paw

# Set agent as trusted
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"trusted": true}' \
  http://localhost:8888/api/v2/agents/agent-paw
```

### Working with Facts

```bash
# Add a custom fact
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "trait": "host.ip",
    "value": "192.168.1.100",
    "source": "operation-uuid"
  }' \
  http://localhost:8888/api/v2/facts

# Query facts by trait
curl -H "KEY: your-api-key" \
  -G --data-urlencode "include=trait,value" \
  http://localhost:8888/api/v2/facts

# Update fact score
curl -X PATCH -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {"trait": "host.ip", "value": "192.168.1.100"},
    "updates": {"score": 100}
  }' \
  http://localhost:8888/api/v2/facts
```

### Creating Custom Abilities

```bash
# Create a new ability
curl -X POST -H "KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Network Enumeration",
    "description": "Enumerate network interfaces",
    "tactic": "discovery",
    "technique_id": "T1016",
    "technique_name": "System Network Configuration Discovery",
    "executors": [
      {
        "platform": "linux",
        "name": "sh",
        "command": "ip addr show"
      },
      {
        "platform": "windows",
        "name": "cmd",
        "command": "ipconfig /all"
      }
    ]
  }' \
  http://localhost:8888/api/v2/abilities
```

## Additional Resources

- **Caldera Documentation**: https://caldera.readthedocs.io
- **MITRE ATT&CK Framework**: https://attack.mitre.org
- **GitHub Repository**: https://github.com/mitre/caldera
- **Plugin Development Guide**: See `docs/plugins/` directory
- **API Schemas**: Available in `app/api/v2/schemas/` directory

## Changelog

This API reference documents the v2 API endpoints. For information about deprecated v1 endpoints or future API changes, consult the main Caldera documentation.

## Support

For issues, questions, or contributions:

- Submit issues on the GitHub repository
- Join the Caldera community discussions
- Review the security policy in `docs/SECURITY.md`
- Consult the user guide in `docs/user-guide/`
