---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes plugin development work completed during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production software guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Plugin Development Guide

This guide documents the plugin development approaches and patterns demonstrated in this internship project, including architecture patterns, hook implementations, and API integration examples.

## Prerequisites

Before developing a Caldera plugin, ensure you have:

- Python knowledge (async/await, decorators, logging)
- Familiarity with aiohttp web framework
- Understanding of Caldera's service architecture
- Access to the Caldera codebase
- Development environment with Python installed
- Basic understanding of YAML configuration files

## Plugin Architecture

### Directory Structure

A Caldera plugin follows a standardised directory structure:

```
plugins/
└── your_plugin/
    ├── hook.py                  # Plugin registration and lifecycle
    ├── requirements.txt         # Python dependencies
    ├── README.md               # Plugin documentation
    ├── __init__.py
    ├── app/                    # Core plugin logic
    │   ├── __init__.py
    │   ├── config.py           # Configuration management
    │   └── your_service.py     # Main service implementation
    ├── data/                   # Plugin data files
    │   ├── abilities/          # Custom abilities (optional)
    │   ├── adversaries/        # Custom adversaries (optional)
    │   └── planners/           # Custom planners (optional)
    ├── static/                 # Static web assets (optional)
    │   ├── css/
    │   ├── js/
    │   └── img/
    ├── templates/              # HTML templates (optional)
    └── tests/                  # Plugin tests
        ├── __init__.py
        ├── fixtures.py
        └── test_your_service.py
```

### Core Files

#### hook.py

The `hook.py` file is the entry point for your plugin. It defines plugin metadata and lifecycle hooks.

**Minimal Example:**

```python
import logging

# Plugin metadata
name = 'YourPlugin'
description = 'Brief description of your plugin functionality'
address = '/plugin/yourplugin/gui'  # GUI endpoint or None for backend-only
access = None  # Access level (optional)

async def enable(services):
    """
    Called when plugin is enabled during Caldera startup.
    
    Args:
        services: Dictionary of Caldera services
    """
    logger = logging.getLogger('yourplugin')
    logger.info('Initialising YourPlugin...')
    
    # Your plugin initialisation logic here
    
    logger.info('YourPlugin enabled successfully')


async def disable(services):
    """
    Called when plugin is disabled during Caldera shutdown.
    
    Args:
        services: Dictionary of Caldera services
    """
    logger = logging.getLogger('yourplugin')
    logger.info('Disabling YourPlugin...')
    
    # Your plugin cleanup logic here
    
    logger.info('YourPlugin disabled')
```

**Advanced Example with Service Registration:**

```python
import logging

name = 'Orchestrator'
description = 'TL Labs Purple Team Automation - Attack Tagging & Orchestration'
address = None  # No GUI endpoint (backend service only)


async def enable(services):
    """
    Enable orchestrator plugin.
    
    Called by Caldera when plugin loads.
    Registers event handlers and debug API routes.
    
    Args:
        services: Caldera service registry
    """
    from plugins.orchestrator.app.orchestrator_svc import OrchestratorService
    from plugins.orchestrator.app.config import OrchestratorConfig
    
    log = logging.getLogger('orchestrator')
    
    try:
        # Validate configuration
        OrchestratorConfig.validate()
        log.info('Orchestrator configuration validated')
        
        # Initialise service
        orchestrator_svc = OrchestratorService(services)
        services['orchestrator_svc'] = orchestrator_svc
        
        # Register debug API routes (aiohttp)
        app_svc = services.get('app_svc')
        if app_svc and hasattr(app_svc, 'application'):
            app = app_svc.application
            
            # GET /plugin/orchestrator/status - Health check
            app.router.add_route('GET', '/plugin/orchestrator/status', 
                               orchestrator_svc.status_endpoint)
            
            # POST /plugin/orchestrator/tag-test - Manual tag test
            app.router.add_route('POST', '/plugin/orchestrator/tag-test', 
                               orchestrator_svc.tag_test_endpoint)
            
            log.info('Orchestrator API routes registered')
        else:
            log.warning('app_svc not available, API routes not registered')
        
        # Subscribe to operation events via event_svc
        event_svc = services.get('event_svc')
        
        if event_svc:
            await event_svc.observe_event(
                callback=orchestrator_svc.on_operation_state_changed,
                exchange='operation',
                queue='state_changed'
            )
            
            await event_svc.observe_event(
                callback=orchestrator_svc.on_operation_completed,
                exchange='operation',
                queue='completed'
            )
            
            await event_svc.observe_event(
                callback=orchestrator_svc.on_link_status_changed,
                exchange='link',
                queue='status_changed'
            )
            
            log.info('Orchestrator event handlers registered')
        else:
            log.warning('event_svc not available, event subscriptions skipped')
        
        log.info('Orchestrator plugin enabled successfully')
        
    except Exception as e:
        log.error(f'Orchestrator plugin failed to load: {e}')
        raise


async def disable(services):
    """
    Disable orchestrator plugin.
    
    Called by Caldera when plugin unloads.
    
    Args:
        services: Caldera service registry
    """
    orchestrator_svc = services.get('orchestrator_svc')
    
    if orchestrator_svc:
        await orchestrator_svc.shutdown()
        log = logging.getLogger('orchestrator')
        log.info('Orchestrator plugin disabled')
```

## Available Hook Methods

Caldera plugins can subscribe to various lifecycle and event hooks:

### Lifecycle Hooks

#### enable(services)

Called when the plugin is loaded during Caldera startup.

**Use Cases:**
- Initialise plugin services
- Register API routes
- Subscribe to events
- Load configuration
- Validate dependencies

**Parameters:**
- `services` (dict): Caldera service registry containing core services

**Common Services:**
- `app_svc`: Application service (aiohttp application)
- `event_svc`: Event service (pub/sub system)
- `data_svc`: Data service (object storage)
- `auth_svc`: Authentication service
- `contact_svc`: Contact service (agent communication)
- `planning_svc`: Planning service (operation planning)
- `rest_svc`: REST API service

#### disable(services)

Called when the plugin is unloaded during Caldera shutdown.

**Use Cases:**
- Clean up resources
- Close connections
- Stop background tasks
- Save state

### Event Hooks

Plugins can subscribe to events using `event_svc.observe_event()`:

#### Operation Events

```python
# Operation state changed (running, paused, etc.)
await event_svc.observe_event(
    callback=your_handler,
    exchange='operation',
    queue='state_changed'
)

# Operation completed
await event_svc.observe_event(
    callback=your_handler,
    exchange='operation',
    queue='completed'
)
```

#### Link Events

```python
# Link status changed (executing, finished, failed)
await event_svc.observe_event(
    callback=your_handler,
    exchange='link',
    queue='status_changed'
)
```

#### Agent Events

```python
# New agent registered
await event_svc.observe_event(
    callback=your_handler,
    exchange='agent',
    queue='registered'
)
```

### Event Handler Pattern

```python
async def on_operation_completed(self, event_data):
    """
    Handle operation completion event.
    
    Args:
        event_data: Dictionary containing event information
    """
    operation_id = event_data.get('operation_id')
    
    # Your event handling logic
    self.logger.info(f'Operation {operation_id} completed')
```

## Configuration Management

### Configuration File Pattern

Create a `config.py` module to manage plugin configuration:

```python
"""Configuration loader for your plugin.

Uses Caldera's BaseWorld config system to read from conf/local.yml.
"""

import os
import logging
from pathlib import Path

try:
    from app.utility.base_world import BaseWorld
except ImportError:
    BaseWorld = None


class YourPluginConfig:
    """
    Your plugin configuration.
    
    Reads from conf/local.yml under plugins.yourplugin.* keys.
    Falls back to environment variables if BaseWorld unavailable.
    """
    
    _log = logging.getLogger('yourplugin.config')
    
    # Default values (override via conf/local.yml or env vars)
    EXTERNAL_API_URL = 'http://localhost:8080'
    EXTERNAL_API_KEY = ''  # Set via environment variable
    TIMEOUT = 30
    MAX_RETRIES = 3
    
    @classmethod
    def _get_config(cls, key: str, default=None):
        """
        Get config value from BaseWorld or environment.
        
        Args:
            key: Config key (e.g., 'api_url')
            default: Default value if not found
            
        Returns:
            Config value
        """
        # Try BaseWorld config first (conf/local.yml)
        if BaseWorld:
            try:
                caldera_key = f'plugins.yourplugin.{key}'
                value = BaseWorld.get_config(caldera_key)
                if value is not None:
                    return value
            except Exception:
                pass
        
        # Fall back to environment variable
        env_key = f'YOURPLUGIN_{key.upper()}'
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        return default
    
    @classmethod
    def load(cls):
        """Load configuration from BaseWorld/environment."""
        cls.EXTERNAL_API_URL = cls._get_config('api_url', cls.EXTERNAL_API_URL)
        cls.EXTERNAL_API_KEY = cls._get_config('api_key', cls.EXTERNAL_API_KEY)
        
        # Boolean/int conversions
        timeout = cls._get_config('timeout', cls.TIMEOUT)
        cls.TIMEOUT = int(timeout) if timeout else cls.TIMEOUT
        
        retries = cls._get_config('max_retries', cls.MAX_RETRIES)
        cls.MAX_RETRIES = int(retries) if retries else cls.MAX_RETRIES
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        cls.load()
        
        if not cls.EXTERNAL_API_KEY:
            raise ValueError('YOURPLUGIN_API_KEY environment variable required')
        
        if cls.TIMEOUT <= 0:
            raise ValueError('Timeout must be positive')
```

### Configuration in conf/local.yml

Add plugin configuration to `conf/local.yml`:

```yaml
plugins:
  yourplugin:
    api_url: 'https://external-api.example.com'
    timeout: 60
    max_retries: 5
```

## API Integration Patterns

### Registering REST API Routes

```python
async def enable(services):
    """Enable plugin and register API routes."""
    from plugins.yourplugin.app.your_service import YourService
    
    app_svc = services.get('app_svc')
    if app_svc and hasattr(app_svc, 'application'):
        app = app_svc.application
        
        # Initialise service
        your_svc = YourService(services)
        services['your_svc'] = your_svc
        
        # Register routes
        app.router.add_route('GET', '/plugin/yourplugin/status', 
                           your_svc.status_endpoint)
        app.router.add_route('POST', '/plugin/yourplugin/process', 
                           your_svc.process_endpoint)
        app.router.add_route('GET', '/plugin/yourplugin/results/{id}', 
                           your_svc.results_endpoint)
```

### API Endpoint Implementation

```python
from aiohttp import web
import logging


class YourService:
    """Service implementing plugin functionality."""
    
    def __init__(self, services):
        """
        Initialise service.
        
        Args:
            services: Caldera service registry
        """
        self.services = services
        self.logger = logging.getLogger('yourplugin.service')
    
    async def status_endpoint(self, request):
        """
        Health check endpoint.
        
        GET /plugin/yourplugin/status
        
        Returns:
            JSON response with status information
        """
        try:
            status = {
                'plugin': 'yourplugin',
                'status': 'operational',
                'version': '1.0.0'
            }
            return web.json_response(status)
        except Exception as e:
            self.logger.error(f'Status check failed: {e}')
            return web.json_response(
                {'error': 'Internal error'},
                status=500
            )
    
    async def process_endpoint(self, request):
        """
        Process data endpoint.
        
        POST /plugin/yourplugin/process
        Body: {"data": "value"}
        
        Returns:
            JSON response with processing results
        """
        try:
            body = await request.json()
            data = body.get('data')
            
            if not data:
                return web.json_response(
                    {'error': 'Missing data parameter'},
                    status=400
                )
            
            # Process data
            result = await self._process_data(data)
            
            return web.json_response({
                'success': True,
                'result': result
            })
        except Exception as e:
            self.logger.error(f'Processing failed: {e}')
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    async def results_endpoint(self, request):
        """
        Get results by ID endpoint.
        
        GET /plugin/yourplugin/results/{id}
        
        Returns:
            JSON response with results
        """
        try:
            result_id = request.match_info['id']
            
            # Retrieve results
            results = await self._get_results(result_id)
            
            if not results:
                return web.json_response(
                    {'error': 'Results not found'},
                    status=404
                )
            
            return web.json_response(results)
        except Exception as e:
            self.logger.error(f'Failed to retrieve results: {e}')
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    async def _process_data(self, data):
        """Process data implementation."""
        # Your processing logic
        return {'processed': data}
    
    async def _get_results(self, result_id):
        """Retrieve results implementation."""
        # Your retrieval logic
        return {'id': result_id, 'data': 'example'}
```

### Graceful Dependency Handling

Handle missing dependencies gracefully to prevent plugin failures from breaking Caldera:

```python
import logging

name = 'YourPlugin'
description = 'Description of your plugin'
address = '/plugin/yourplugin/gui'
access = None

_plugin_enabled = False
_import_error_message = None

# Try imports, disable plugin if missing
try:
    from plugins.yourplugin.app.your_service import YourService
    _plugin_enabled = True
except ImportError as e:
    _import_error_message = str(e)
    _plugin_enabled = False
except Exception as e:
    _import_error_message = f"Unexpected error: {str(e)}"
    _plugin_enabled = False


async def enable(services):
    """Called by Caldera when plugin is enabled."""
    logger = logging.getLogger('yourplugin')
    
    # Check if plugin dependencies available
    if not _plugin_enabled:
        logger.error(
            f'YourPlugin DISABLED: Missing dependencies\n'
            f'   Error: {_import_error_message}\n'
            f'   Fix: pip install -r plugins/yourplugin/requirements.txt\n'
            f'   Then restart Caldera: python server.py --insecure'
        )
        return  # Exit early, don't register routes/events
    
    logger.info('Initialising YourPlugin...')
    
    # Your plugin initialisation logic
    
    logger.info('YourPlugin loaded successfully')


async def disable(services):
    """Called by Caldera when plugin is disabled."""
    logger = logging.getLogger('yourplugin')
    
    if not _plugin_enabled:
        logger.debug('YourPlugin was not enabled, skipping disable')
        return
    
    logger.info('Disabling YourPlugin...')
    
    # Your plugin cleanup logic
    
    logger.info('YourPlugin disabled successfully')
```

## Step-by-Step Tutorial: Creating a Simple Plugin

This tutorial demonstrates creating a simple logging plugin that tracks operation events.

### Step 1: Create Plugin Directory Structure

```bash
cd plugins
mkdir -p operation_logger/app
mkdir -p operation_logger/data
mkdir -p operation_logger/tests
touch operation_logger/__init__.py
touch operation_logger/app/__init__.py
touch operation_logger/tests/__init__.py
```

### Step 2: Create hook.py

Create `plugins/operation_logger/hook.py`:

```python
import logging

name = 'OperationLogger'
description = 'Logs operation events to file for audit purposes'
address = None  # Backend-only plugin
access = None

async def enable(services):
    """Enable operation logger plugin."""
    from plugins.operation_logger.app.logger_svc import LoggerService
    
    log = logging.getLogger('operation_logger')
    log.info('Initialising Operation Logger plugin...')
    
    try:
        # Create service
        logger_svc = LoggerService(services)
        services['logger_svc'] = logger_svc
        
        # Subscribe to operation events
        event_svc = services.get('event_svc')
        if event_svc:
            await event_svc.observe_event(
                callback=logger_svc.on_operation_completed,
                exchange='operation',
                queue='completed'
            )
            log.info('Operation Logger subscribed to operation events')
        
        log.info('Operation Logger plugin enabled successfully')
    except Exception as e:
        log.error(f'Operation Logger failed to load: {e}')
        raise


async def disable(services):
    """Disable operation logger plugin."""
    logger_svc = services.get('logger_svc')
    
    if logger_svc:
        logger_svc.close()
        log = logging.getLogger('operation_logger')
        log.info('Operation Logger plugin disabled')
```

### Step 3: Create Service Implementation

Create `plugins/operation_logger/app/logger_svc.py`:

```python
import logging
from pathlib import Path
from datetime import datetime
import json


class LoggerService:
    """Service that logs operation events to file."""
    
    def __init__(self, services):
        """
        Initialise logger service.
        
        Args:
            services: Caldera service registry
        """
        self.services = services
        self.logger = logging.getLogger('operation_logger.service')
        
        # Create log directory
        self.log_dir = Path('plugins/operation_logger/data/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Open log file
        self.log_file = self.log_dir / 'operations.jsonl'
        self.file_handle = open(self.log_file, 'a')
        
        self.logger.info(f'Logging to {self.log_file}')
    
    async def on_operation_completed(self, event_data):
        """
        Handle operation completion event.
        
        Args:
            event_data: Dictionary containing operation information
        """
        try:
            operation_id = event_data.get('operation_id')
            
            # Get operation details from data_svc
            data_svc = self.services.get('data_svc')
            operations = await data_svc.locate('operations', 
                                              {'id': operation_id})
            
            if not operations:
                self.logger.warning(f'Operation {operation_id} not found')
                return
            
            operation = operations[0]
            
            # Build log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'operation_completed',
                'operation_id': operation.id,
                'operation_name': operation.name,
                'state': operation.state,
                'start': operation.start.isoformat() if operation.start else None,
                'finish': operation.finish.isoformat() if operation.finish else None,
                'adversary': operation.adversary.name if operation.adversary else None,
                'agent_count': len(operation.agents),
                'link_count': len(operation.chain)
            }
            
            # Write to file
            self.file_handle.write(json.dumps(log_entry) + '\n')
            self.file_handle.flush()
            
            self.logger.info(f'Logged operation {operation_id}')
        except Exception as e:
            self.logger.error(f'Failed to log operation: {e}')
    
    def close(self):
        """Close log file."""
        if self.file_handle:
            self.file_handle.close()
            self.logger.info('Log file closed')
```

### Step 4: Create requirements.txt

Create `plugins/operation_logger/requirements.txt`:

```
# No additional dependencies required
```

### Step 5: Create README.md

Create `plugins/operation_logger/README.md`:

```markdown
# Operation Logger Plugin

Logs operation completion events to a JSON Lines file for audit and analysis purposes.

## Features

- Tracks operation completion events
- Logs operation metadata (name, state, duration, etc.)
- Writes to JSON Lines format for easy processing

## Configuration

No configuration required. Logs are written to:
`plugins/operation_logger/data/logs/operations.jsonl`

## Usage

Enable the plugin in `conf/local.yml`:

yaml
plugins:
  - operation_logger


Logs will be automatically written when operations complete.

## Log Format

Each log entry is a JSON object:

json
{
  "timestamp": "2026-01-15T10:30:00.123456",
  "event": "operation_completed",
  "operation_id": "abc-123-def-456",
  "operation_name": "Test Operation",
  "state": "finished",
  "start": "2026-01-15T10:00:00.000000",
  "finish": "2026-01-15T10:30:00.123456",
  "adversary": "Hunter",
  "agent_count": 3,
  "link_count": 15
}

```

### Step 6: Enable the Plugin

Add to `conf/local.yml`:

```yaml
plugins:
  - operation_logger
```

### Step 7: Test the Plugin

Start Caldera and verify the plugin loads:

```bash
python server.py --insecure
```

Check logs for:
```
[operation_logger] Initialising Operation Logger plugin...
[operation_logger] Operation Logger subscribed to operation events
[operation_logger] Logging to plugins/operation_logger/data/logs/operations.jsonl
[operation_logger] Operation Logger plugin enabled successfully
```

Run an operation and verify log entries are created.

## Troubleshooting Common Issues

### Plugin Not Loading

**Symptom:** Plugin doesn't appear in Caldera logs

**Solutions:**
1. Verify plugin is listed in `conf/local.yml` under `plugins:`
2. Check for syntax errors in `hook.py`
3. Ensure `__init__.py` exists in plugin directory
4. Review Caldera startup logs for import errors

### Import Errors

**Symptom:** `ImportError` or `ModuleNotFoundError` in logs

**Solutions:**
1. Verify all dependencies are installed: `pip install -r requirements.txt`
2. Check Python path includes plugin directory
3. Ensure `__init__.py` files exist in all subdirectories
4. Use absolute imports: `from plugins.yourplugin.app.service import Service`

### Service Not Available

**Symptom:** `services.get('your_svc')` returns `None`

**Solutions:**
1. Verify service is added to services dict in `enable()`: `services['your_svc'] = your_svc`
2. Check service initialisation doesn't raise exceptions
3. Ensure plugin loads before plugins that depend on it

### Event Handlers Not Triggered

**Symptom:** Event callback never executes

**Solutions:**
1. Verify event subscription uses correct exchange and queue names
2. Check event handler signature matches expected format
3. Ensure event_svc is available: `if event_svc:`
4. Add debug logging to handler to verify it's registered
5. Check for exceptions in handler (use try/except)

### API Routes Not Accessible

**Symptom:** `404 Not Found` when accessing plugin endpoints

**Solutions:**
1. Verify routes are registered with correct HTTP method and path
2. Check app_svc is available: `if app_svc and hasattr(app_svc, 'application'):`
3. Ensure route path matches URL (case-sensitive)
4. Verify handler function is async: `async def handler(request):`
5. Check for route conflicts with other plugins

### Configuration Not Loading

**Symptom:** Default values used instead of config from `conf/local.yml`

**Solutions:**
1. Verify config key path: `plugins.yourplugin.setting_name`
2. Check YAML syntax in `conf/local.yml`
3. Ensure `BaseWorld.get_config()` is called with correct key
4. Verify config is loaded before use: `YourConfig.load()`
5. Check environment variables are set correctly

### Resource Cleanup Issues

**Symptom:** Resource leaks, connections not closed on shutdown

**Solutions:**
1. Implement proper cleanup in `disable()` hook
2. Close file handles, database connections, HTTP sessions
3. Cancel background tasks: `task.cancel()`
4. Use context managers where possible: `async with`
5. Add try/except in `disable()` to handle cleanup errors gracefully

### Thread Safety Issues

**Symptom:** Race conditions, concurrent access errors

**Solutions:**
1. Use asyncio primitives: `asyncio.Lock()`, `asyncio.Queue()`
2. Avoid shared mutable state between async tasks
3. Use ThreadPoolExecutor for CPU-bound work
4. Ensure database connections are per-task or pooled
5. Test with concurrent operations

### Performance Problems

**Symptom:** Plugin slows down Caldera

**Solutions:**
1. Profile code to identify bottlenecks
2. Move blocking I/O to background tasks: `asyncio.create_task()`
3. Use connection pooling for external services
4. Implement caching for frequently accessed data
5. Add timeout protection for external API calls
6. Limit concurrent operations with semaphores

### Logging Best Practices

**Issues:** Logs too verbose or missing critical information

**Solutions:**
1. Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
2. Include context in log messages (operation IDs, etc.)
3. Avoid logging sensitive data (passwords, tokens)
4. Use structured logging for easier parsing
5. Create logger per module: `logging.getLogger('yourplugin.module')`

## Next Steps

After creating your plugin:

1. Write comprehensive tests (see [testing.md](testing.md))
2. Document API endpoints and configuration options
3. Create example configurations and use cases
4. Consider publishing to community plugin repository
5. Review security implications (input validation, access control)
6. Add monitoring and health checks
7. Plan for upgrades and backward compatibility

## See Also

- [Testing Guide](testing.md) - Plugin testing strategies
- [Caldera Service Architecture](../architecture/services.md) - Core service patterns
- [API Documentation](../reference/api.md) - REST API reference
- [Event System](../reference/events.md) - Event types and patterns
- [Configuration Guide](../getting-started/configuration.md) - Configuration management
