# Testing Guide

This guide covers testing strategies, conventions, and best practices for Caldera core and plugin development. It includes examples of unit tests, integration tests, fixtures, and CI/CD integration.

## Prerequisites

Before writing tests, ensure you have:

- Python testing knowledge (pytest framework)
- Understanding of async/await testing patterns
- Familiarity with mocking and fixtures
- Development environment configured
- Test dependencies installed

## Test Environment Setup

### Installing Test Dependencies

Install development dependencies including pytest and related tools:

```bash
pip install -r requirements-dev.txt
```

Key testing dependencies:

```
pytest
pytest-aiohttp
pytest-asyncio
coverage
```

### Running Tests

#### Run All Tests

```bash
pytest tests/ -vv
```

#### Run Specific Test File

```bash
pytest tests/services/test_data_svc.py -vv
```

#### Run Specific Test Class

```bash
pytest tests/services/test_data_svc.py::TestDataService -vv
```

#### Run Specific Test Method

```bash
pytest tests/services/test_planning_svc.py::TestPlanningService::test_link_ordering -vv
```

#### Run with Coverage

```bash
coverage run -m pytest tests/ -vv
coverage report
coverage html  # Generate HTML report
```

#### Run Tests in Parallel

```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

### Using Tox

Tox automates testing across multiple Python versions:

```bash
# Install tox
pip install tox

# Run tests across all configured Python versions
tox

# Run specific environment
tox -e py310

# Run style checks
tox -e style

# Run coverage
tox -e coverage
```

Configuration is in `config/tox.ini`:

```ini
[tox]
skipsdist = True
envlist =
    py{310,311,312}
    style
    coverage
skip_missing_interpreters = true

[testenv]
description = run tests
deps =
    -rrequirements.txt
    virtualenv
    pre-commit
    pytest
    pytest-asyncio
    pytest-aiohttp
    coverage
commands =
    coverage run -p -m pytest --tb=short --asyncio-mode=auto tests -vv
```

## Test Directory Structure

Caldera follows a standardised test organisation:

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── api/                     # API endpoint tests
│   └── __init__.py
├── contacts/                # Contact protocol tests
│   └── test_contact_http.py
├── objects/                 # Object model tests
│   └── test_agent.py
├── parsers/                 # Parser tests
│   └── test_parser.py
├── planners/                # Planner tests
│   └── test_atomic.py
├── services/                # Service tests
│   ├── test_data_svc.py
│   ├── test_planning_svc.py
│   └── test_rest_svc.py
└── utility/                 # Utility tests
    └── test_base_object.py
```

Plugin tests follow similar structure:

```
plugins/yourplugin/
└── tests/
    ├── __init__.py
    ├── fixtures.py          # Plugin-specific fixtures
    ├── test_your_service.py
    └── test_integration.sh  # Shell-based integration tests
```

## Test Structure and Conventions

### Naming Conventions

**Test Files:**
- Prefix with `test_`: `test_data_svc.py`
- Mirror source structure: `app/service/data_svc.py` → `tests/services/test_data_svc.py`

**Test Classes:**
- Prefix with `Test`: `TestDataService`
- Group related tests: `TestDataServiceValidation`, `TestDataServiceStorage`

**Test Methods:**
- Prefix with `test_`: `test_no_duplicate_adversary`
- Descriptive names: `test_metadata_table_handles_none_values`
- Use underscores: `test_is_valid_operation_id_accepts_valid_formats`

### Test Organisation

Group tests using classes for better organisation:

```python
class TestDataService:
    """Tests for DataService core functionality."""
    
    def test_no_duplicate_adversary(self, event_loop, data_svc):
        """Test that duplicate adversaries are not stored."""
        # Test implementation
    
    def test_store_ability(self, event_loop, data_svc):
        """Test storing an ability."""
        # Test implementation


class TestDataServiceValidation:
    """Tests for DataService validation methods."""
    
    def test_validate_uuid_format(self, data_svc):
        """Test UUID validation accepts valid formats."""
        # Test implementation
    
    def test_validate_uuid_rejects_invalid(self, data_svc):
        """Test UUID validation rejects invalid formats."""
        # Test implementation
```

## Fixtures and Test Data Setup

### Shared Fixtures (conftest.py)

The `tests/conftest.py` file contains shared fixtures available to all tests:

```python
import pytest
import asyncio
from unittest.mock import MagicMock

from app.service.data_svc import DataService
from app.service.event_svc import EventService
from app.objects.c_adversary import Adversary
from app.objects.c_ability import Ability
from app.objects.c_agent import Agent


@pytest.fixture(scope='class')
def data_svc():
    """Provide DataService instance."""
    return DataService()


@pytest.fixture(scope='class')
def event_svc(init_base_world):
    """Provide EventService instance."""
    return EventService()


@pytest.fixture
def adversary():
    """Factory fixture for creating test adversaries."""
    def _generate_adversary(adversary_id=None, name=None, description=None, phases=None):
        if not adversary_id:
            adversary_id = str(uuid.uuid4())
        if not name:
            name = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
        if not description:
            description = "test description"
        if not phases:
            phases = dict()
        return Adversary(
            adversary_id=adversary_id,
            name=name,
            description=description,
            atomic_ordering=phases
        )
    
    return _generate_adversary


@pytest.fixture
def ability():
    """Factory fixture for creating test abilities."""
    def _generate_ability(ability_id=None, *args, **kwargs):
        if not ability_id:
            ability_id = random.randint(0, 999999)
        return Ability(*args, ability_id=ability_id, **kwargs)
    
    return _generate_ability


@pytest.fixture
def agent():
    """Factory fixture for creating test agents."""
    def _generate_agent(sleep_min=60, sleep_max=90, watchdog=0, 
                       executors=None, platform='linux', **kwargs):
        if executors is None:
            executors = ['sh']
        return Agent(
            sleep_min=sleep_min,
            sleep_max=sleep_max,
            watchdog=watchdog,
            executors=executors,
            platform=platform,
            **kwargs
        )
    
    return _generate_agent
```

### Plugin-Specific Fixtures

Create `fixtures.py` in your plugin's test directory:

```python
"""Test fixtures for orchestrator plugin."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


@pytest.fixture
def mock_logger():
    """Provide mock logger."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger


@pytest.fixture
def mock_operation():
    """Provide mock operation object."""
    operation = MagicMock()
    operation.id = 'test-operation-abc123'
    operation.name = 'Test Operation'
    operation.state = 'finished'
    operation.start = datetime(2026, 1, 15, 10, 0, 0)
    operation.finish = datetime(2026, 1, 15, 10, 30, 0)
    operation.adversary = MagicMock()
    operation.adversary.name = 'Hunter'
    operation.adversary.atomic_ordering = ['T1078', 'T1059.001']
    operation.chain = [
        MagicMock(ability=MagicMock(technique_id='T1078')),
        MagicMock(ability=MagicMock(technique_id='T1059.001'))
    ]
    return operation


@pytest.fixture
def mock_elk_client():
    """Provide mock Elasticsearch client."""
    client = AsyncMock()
    client.index = AsyncMock(return_value={'result': 'created'})
    client.search = AsyncMock(return_value={'hits': {'hits': []}})
    client.close = AsyncMock()
    return client
```

### Fixture Scopes

Pytest fixtures support different scopes:

- `function` (default): New instance per test function
- `class`: Shared across test class
- `module`: Shared across test module
- `session`: Shared across entire test session

```python
@pytest.fixture(scope='session')
def init_base_world():
    """Initialise base configuration once per session."""
    with open(os.path.join(CONFIG_DIR, 'default.yml')) as c:
        BaseWorld.apply_config('main', yaml.load(c, Loader=yaml.FullLoader))
    BaseWorld.apply_config('agents', BaseWorld.strip_yml('conf/agents.yml')[0])


@pytest.fixture(scope='class')
def data_svc():
    """Provide DataService instance shared across test class."""
    return DataService()


@pytest.fixture  # scope='function' is default
def adversary():
    """Provide new adversary for each test function."""
    def _generate_adversary(**kwargs):
        return Adversary(**kwargs)
    return _generate_adversary
```

## Unit Tests

Unit tests focus on testing individual components in isolation.

### Testing Service Methods

```python
import pytest
from app.service.data_svc import DataService
from app.objects.c_adversary import Adversary


class TestDataService:
    """Unit tests for DataService."""
    
    def test_no_duplicate_adversary(self, event_loop, data_svc):
        """Test that duplicate adversaries are prevented."""
        # Create adversary
        adversary1 = Adversary(
            adversary_id='123',
            name='test',
            description='test adversary',
            atomic_ordering=[]
        )
        
        # Store first time
        event_loop.run_until_complete(data_svc.store(adversary1))
        
        # Attempt to store duplicate
        adversary2 = Adversary(
            adversary_id='123',
            name='test',
            description='test adversary',
            atomic_ordering=[]
        )
        event_loop.run_until_complete(data_svc.store(adversary2))
        
        # Verify only one stored
        adversaries = event_loop.run_until_complete(
            data_svc.locate('adversaries')
        )
        assert len(adversaries) == 1
    
    def test_locate_by_criteria(self, event_loop, data_svc, adversary):
        """Test locating objects by criteria."""
        # Store multiple adversaries
        adv1 = adversary(name='Hunter', description='test')
        adv2 = adversary(name='Scanner', description='test')
        
        event_loop.run_until_complete(data_svc.store(adv1))
        event_loop.run_until_complete(data_svc.store(adv2))
        
        # Locate by name
        results = event_loop.run_until_complete(
            data_svc.locate('adversaries', {'name': 'Hunter'})
        )
        
        assert len(results) == 1
        assert results[0].name == 'Hunter'
```

### Testing Validation Logic

```python
class TestELKTaggerValidation:
    """Test input validation methods."""
    
    def test_is_valid_operation_id_accepts_valid_formats(self, mock_logger):
        """Test valid operation ID formats."""
        tagger = ELKTagger(mock_logger)
        
        # UUID format
        assert tagger._is_valid_operation_id('abc-123-def-456')
        
        # Alphanumeric with hyphens
        assert tagger._is_valid_operation_id('test-operation-001')
        
        # Short IDs
        assert tagger._is_valid_operation_id('abc12345')
    
    def test_is_valid_operation_id_rejects_invalid_formats(self, mock_logger):
        """Test invalid operation ID rejection."""
        tagger = ELKTagger(mock_logger)
        
        # Too short
        assert not tagger._is_valid_operation_id('abc')
        
        # Special characters
        assert not tagger._is_valid_operation_id('test@operation')
        assert not tagger._is_valid_operation_id('op/../etc/passwd')
        
        # SQL injection attempt
        assert not tagger._is_valid_operation_id("'; DROP TABLE operations--")
    
    def test_sanitise_metadata_removes_special_chars(self, mock_logger):
        """Test metadata sanitisation."""
        tagger = ELKTagger(mock_logger)
        
        metadata = {
            'operation_name': '<script>alert("xss")</script>Test Operation',
            'techniques': ['T1078', 'T1059.001', 'INVALID', 'T9999.999'],
            'tactics': ['Persistence', 'Execution', 'Invalid@Tactic'],
            'client_id': '../../../etc/passwd'
        }
        
        sanitised = tagger._sanitise_metadata(metadata)
        
        # Operation name sanitised
        assert '<script>' not in sanitised['operation_name']
        assert 'alert' not in sanitised['operation_name']
        
        # Only valid techniques kept
        assert sanitised['techniques'] == ['T1078', 'T1059.001']
        
        # Only valid tactics kept
        assert 'Persistence' in sanitised['tactics']
        assert 'Execution' in sanitised['tactics']
        assert 'Invalid@Tactic' not in sanitised['tactics']
        
        # Path traversal removed
        assert '../' not in sanitised['client_id']
```

### Testing Object Construction

```python
class TestPDFGeneratorInitialisation:
    """Test PDF generator initialisation and configuration."""
    
    def test_init_with_valid_config(self, mock_config):
        """Test initialisation with valid configuration."""
        generator = PDFGenerator(mock_config)
        
        assert generator.config == mock_config
        assert generator.executor is not None
        assert generator.styles is not None
        assert 'TLTitle' in generator.styles
        assert 'TLSubtitle' in generator.styles
        assert 'TLBody' in generator.styles
    
    def test_custom_styles_created(self, mock_config):
        """Test that custom styles are created."""
        generator = PDFGenerator(mock_config)
        
        title_style = generator.styles['TLTitle']
        assert title_style.fontSize == 24
        assert title_style.fontName == 'Helvetica-Bold'
        
        subtitle_style = generator.styles['TLSubtitle']
        assert subtitle_style.fontSize == 14
```

## Async Tests

Use `pytest-asyncio` for testing async functions.

### Async Test Functions

```python
import pytest


@pytest.mark.asyncio
async def test_async_service_method(data_svc, adversary):
    """Test async service method."""
    # Create test data
    adv = adversary(name='Test')
    
    # Call async method
    await data_svc.store(adv)
    
    # Verify
    results = await data_svc.locate('adversaries', {'name': 'Test'})
    assert len(results) == 1
```

### Testing Event Handlers

```python
@pytest.mark.asyncio
async def test_operation_completed_handler(mock_logger, mock_operation):
    """Test operation completion event handler."""
    from plugins.yourplugin.app.your_service import YourService
    
    # Create service with mock dependencies
    services = {
        'data_svc': MagicMock(),
        'event_svc': MagicMock()
    }
    
    service = YourService(services)
    
    # Simulate event
    event_data = {
        'operation_id': mock_operation.id
    }
    
    # Call handler
    await service.on_operation_completed(event_data)
    
    # Verify handler executed correctly
    mock_logger.info.assert_called()
```

## Integration Tests

Integration tests verify components work together correctly.

### Testing API Endpoints

```python
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer


@pytest.mark.asyncio
async def test_status_endpoint():
    """Test status API endpoint."""
    from plugins.yourplugin.app.your_service import YourService
    
    # Create app and register routes
    app = web.Application()
    service = YourService({})
    app.router.add_route('GET', '/plugin/yourplugin/status', 
                        service.status_endpoint)
    
    # Create test client
    async with TestClient(TestServer(app)) as client:
        # Make request
        resp = await client.get('/plugin/yourplugin/status')
        
        # Verify response
        assert resp.status == 200
        data = await resp.json()
        assert data['status'] == 'operational'


@pytest.mark.asyncio
async def test_process_endpoint_with_valid_data():
    """Test process endpoint with valid data."""
    from plugins.yourplugin.app.your_service import YourService
    
    app = web.Application()
    service = YourService({})
    app.router.add_route('POST', '/plugin/yourplugin/process', 
                        service.process_endpoint)
    
    async with TestClient(TestServer(app)) as client:
        # Make request with data
        resp = await client.post('/plugin/yourplugin/process', 
                                json={'data': 'test_value'})
        
        # Verify response
        assert resp.status == 200
        data = await resp.json()
        assert data['success'] is True


@pytest.mark.asyncio
async def test_process_endpoint_with_missing_data():
    """Test process endpoint rejects missing data."""
    from plugins.yourplugin.app.your_service import YourService
    
    app = web.Application()
    service = YourService({})
    app.router.add_route('POST', '/plugin/yourplugin/process', 
                        service.process_endpoint)
    
    async with TestClient(TestServer(app)) as client:
        # Make request without data
        resp = await client.post('/plugin/yourplugin/process', json={})
        
        # Verify error response
        assert resp.status == 400
        data = await resp.json()
        assert 'error' in data
```

### Testing Plugin Lifecycle

```python
@pytest.mark.asyncio
async def test_plugin_enable_and_disable():
    """Test plugin enable and disable hooks."""
    from plugins.yourplugin import hook
    
    # Mock services
    services = {
        'app_svc': MagicMock(),
        'event_svc': MagicMock(),
        'data_svc': MagicMock()
    }
    
    # Mock app_svc.application
    services['app_svc'].application = web.Application()
    
    # Enable plugin
    await hook.enable(services)
    
    # Verify service registered
    assert 'your_svc' in services
    
    # Verify routes registered
    app = services['app_svc'].application
    routes = [route.resource.canonical for route in app.router.routes()]
    assert '/plugin/yourplugin/status' in routes
    
    # Disable plugin
    await hook.disable(services)
    
    # Verify cleanup executed
    # (Add assertions based on your cleanup logic)
```

### Shell-Based Integration Tests

For complex integration scenarios, use shell scripts:

Create `plugins/yourplugin/tests/test_integration.sh`:

```bash
#!/bin/bash
# Integration test for yourplugin

set -e

echo "Starting integration test..."

# Start Caldera in background
python server.py --insecure &
SERVER_PID=$!

# Wait for server to start
sleep 10

# Test plugin endpoint
RESPONSE=$(curl -s http://localhost:8888/plugin/yourplugin/status)
echo "Status response: $RESPONSE"

# Verify response contains expected data
if echo "$RESPONSE" | grep -q "operational"; then
    echo "✓ Status endpoint working"
else
    echo "✗ Status endpoint failed"
    kill $SERVER_PID
    exit 1
fi

# Cleanup
kill $SERVER_PID

echo "Integration test passed"
```

Make executable:

```bash
chmod +x plugins/yourplugin/tests/test_integration.sh
```

Run:

```bash
./plugins/yourplugin/tests/test_integration.sh
```

## Mocking and Test Doubles

### Mocking External Dependencies

```python
from unittest.mock import MagicMock, AsyncMock, patch


def test_with_mocked_external_api():
    """Test with mocked external API."""
    from plugins.yourplugin.app.your_service import YourService
    
    # Create mock HTTP session
    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'result': 'success'})
    mock_session.post = AsyncMock(return_value=mock_response)
    
    # Inject mock
    service = YourService({})
    service.http_session = mock_session
    
    # Call method that uses HTTP session
    result = await service.call_external_api('test_data')
    
    # Verify
    assert result['result'] == 'success'
    mock_session.post.assert_called_once()


@patch('plugins.yourplugin.app.your_service.AsyncElasticsearch')
def test_with_patched_elasticsearch(mock_es_class):
    """Test with patched Elasticsearch client."""
    from plugins.yourplugin.app.your_service import YourService
    
    # Configure mock
    mock_client = AsyncMock()
    mock_client.index = AsyncMock(return_value={'result': 'created'})
    mock_es_class.return_value = mock_client
    
    # Create service (will use mocked Elasticsearch)
    service = YourService({})
    
    # Test method
    result = await service.index_document({'data': 'test'})
    
    # Verify
    mock_client.index.assert_called_once()
```

### Fixture Parametrisation

Test multiple scenarios with parametrised fixtures:

```python
@pytest.fixture(params=[
    {'stopping_condition_met': False, 'operation_state': 'RUNNING', 'assert_value': False},
    {'stopping_condition_met': True, 'operation_state': 'RUNNING', 'assert_value': True},
    {'stopping_condition_met': False, 'operation_state': 'FINISHED', 'assert_value': True},
])
def stop_condition_scenario(request):
    """Parametrised fixture for stop condition scenarios."""
    return request.param


def test_stop_bucket_exhaustion(stop_condition_scenario, planning_svc):
    """Test bucket exhaustion logic with multiple scenarios."""
    scenario = stop_condition_scenario
    
    # Setup operation with scenario parameters
    operation = MagicMock()
    operation.state = scenario['operation_state']
    planner = MagicMock()
    planner.stopping_condition_met = scenario['stopping_condition_met']
    
    # Test
    result = planning_svc.should_stop(operation, planner)
    
    # Verify
    assert result == scenario['assert_value']
```

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests with pytest
      run: |
        pytest tests/ -vv --asyncio-mode=auto
    
    - name: Generate coverage report
      run: |
        coverage run -m pytest tests/
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pre-commit
    
    - name: Run pre-commit hooks
      run: |
        pre-commit run --all-files
```

### Pre-Commit Hooks

Configure pre-commit hooks in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']
```

Install pre-commit:

```bash
pip install pre-commit
pre-commit install
```

Run manually:

```bash
pre-commit run --all-files
```

## Test Coverage

### Measuring Coverage

```bash
# Run tests with coverage
coverage run -m pytest tests/ -vv

# Generate terminal report
coverage report

# Generate HTML report
coverage html

# Open HTML report
open htmlcov/index.html  # macOS
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = app, plugins
omit =
    */tests/*
    */venv/*
    */virtualenv/*
    */__pycache__/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

### Coverage Thresholds

Enforce minimum coverage in CI:

```bash
coverage run -m pytest tests/
coverage report --fail-under=80
```

## Best Practices

### Test Isolation

- Each test should be independent
- Don't rely on test execution order
- Clean up test data after each test
- Use fixtures for shared setup

### Test Data Management

- Use factories for creating test objects
- Parametrise tests for multiple scenarios
- Keep test data minimal and focused
- Avoid hardcoded magic values

### Async Testing

- Always mark async tests with `@pytest.mark.asyncio`
- Use `AsyncMock` for async mocks
- Clean up async resources (sessions, connections)
- Test both success and error paths

### Mocking Guidelines

- Mock external dependencies (APIs, databases)
- Don't mock what you're testing
- Verify mock calls with assertions
- Use realistic mock data

### Performance Testing

- Identify slow tests with `pytest --durations=10`
- Mock expensive operations
- Use appropriate fixture scopes
- Consider parallel test execution

### Error Testing

Always test error conditions:

```python
def test_handles_missing_required_field():
    """Test error handling for missing required field."""
    service = YourService({})
    
    with pytest.raises(ValueError, match="Required field missing"):
        service.process_data({})  # Missing required field


@pytest.mark.asyncio
async def test_handles_network_timeout():
    """Test error handling for network timeout."""
    service = YourService({})
    
    # Mock timeout
    service.http_session.post = AsyncMock(side_effect=asyncio.TimeoutError())
    
    # Verify graceful handling
    result = await service.call_external_api('test')
    assert result is None  # Or appropriate error handling
```

## Troubleshooting Test Issues

### Tests Hang or Timeout

**Solutions:**
- Check for infinite loops
- Verify async operations complete
- Add timeouts to async operations
- Check for deadlocks in concurrent code

### Fixture Not Found

**Solutions:**
- Verify fixture is defined in `conftest.py` or test file
- Check fixture name spelling
- Ensure fixture scope is appropriate
- Import necessary modules

### Async Tests Fail

**Solutions:**
- Add `@pytest.mark.asyncio` decorator
- Use `AsyncMock` for async functions
- Ensure event loop is available
- Check pytest-asyncio configuration

### Mock Not Working

**Solutions:**
- Verify patch path is correct (where imported, not where defined)
- Check mock is applied before function call
- Use `assert_called_with()` to debug
- Verify mock return values are set correctly

### Coverage Not Accurate

**Solutions:**
- Check `.coveragerc` configuration
- Verify source paths are correct
- Run coverage with correct flags
- Check for excluded files

## Next Steps

After mastering testing basics:

1. Explore property-based testing with Hypothesis
2. Implement mutation testing with mutmut
3. Add performance benchmarks with pytest-benchmark
4. Set up continuous testing in IDE
5. Create custom pytest plugins for common patterns
6. Document testing patterns in team wiki
7. Review and improve test coverage regularly

## See Also

- [Plugin Development Guide](plugin-development.md) - Plugin creation patterns
- [CI/CD Documentation](../deployment/ci-cd.md) - Continuous integration setup
- [Code Quality Standards](../development/code-quality.md) - Coding standards and linting
- [Pytest Documentation](https://docs.pytest.org/) - Official pytest documentation
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/) - Async testing guide
