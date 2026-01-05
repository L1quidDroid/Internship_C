"""
Test fixtures for reporting plugin tests.

Provides mock Caldera objects (operations, agents, abilities, links)
for comprehensive unit testing without requiring a full Caldera instance.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import pytest


@pytest.fixture
def mock_config():
    """Mock ReportingConfig object."""
    config = MagicMock()
    config.output_dir = Path('plugins/reporting/data/reports')
    config.page_size = 'LETTER'
    config.font_name = 'Helvetica'
    config.font_size = 10
    config.max_workers = 3
    config.generation_timeout = 30
    config.max_memory_mb = 100
    config.company_name = 'Triskele Labs'
    config.logo_path = Path('plugins/reporting/static/assets/triskele_logo.png')
    config.primary_color = '#0f3460'
    config.accent_color = '#16a085'
    config.text_color = '#1F2937'
    config.include_executive_summary = True
    config.include_tactic_coverage = True
    config.include_technique_details = True
    return config


@pytest.fixture
def mock_ability_t1078():
    """Mock ability for T1078 (Valid Accounts)."""
    ability = MagicMock()
    ability.ability_id = 'abc-123'
    ability.name = 'Valid Accounts'
    ability.description = 'Use valid credentials to authenticate'
    ability.tactic = 'persistence'
    ability.technique_id = 'T1078'
    ability.technique_name = 'Valid Accounts'
    return ability


@pytest.fixture
def mock_ability_t1059():
    """Mock ability for T1059.001 (PowerShell)."""
    ability = MagicMock()
    ability.ability_id = 'def-456'
    ability.name = 'PowerShell Execution'
    ability.description = 'Execute commands via PowerShell'
    ability.tactic = 'execution'
    ability.technique_id = 'T1059.001'
    ability.technique_name = 'Command and Scripting Interpreter: PowerShell'
    return ability


@pytest.fixture
def mock_ability_t1018():
    """Mock ability for T1018 (Remote System Discovery)."""
    ability = MagicMock()
    ability.ability_id = 'ghi-789'
    ability.name = 'Network Discovery'
    ability.description = 'Discover remote systems'
    ability.tactic = 'discovery'
    ability.technique_id = 'T1018'
    ability.technique_name = 'Remote System Discovery'
    return ability


@pytest.fixture
def mock_link_success(mock_ability_t1078):
    """Mock successful link (executed technique)."""
    link = MagicMock()
    link.ability = mock_ability_t1078
    link.status = 0  # Success
    link.finish = datetime.now().isoformat()
    link.command = 'net user /domain'
    link.output = 'User accounts for \\\\DOMAIN\n\nAdministrator...'
    return link


@pytest.fixture
def mock_link_failed(mock_ability_t1059):
    """Mock failed link."""
    link = MagicMock()
    link.ability = mock_ability_t1059
    link.status = 1  # Failed
    link.finish = datetime.now().isoformat()
    link.command = 'powershell.exe -Command "Get-Process"'
    link.output = 'Access Denied'
    return link


@pytest.fixture
def mock_link_timeout(mock_ability_t1018):
    """Mock timed-out link."""
    link = MagicMock()
    link.ability = mock_ability_t1018
    link.status = -2  # Timeout
    link.finish = datetime.now().isoformat()
    link.command = 'ping -n 1000 192.168.1.1'
    link.output = ''
    return link


@pytest.fixture
def mock_agent():
    """Mock Caldera agent."""
    agent = MagicMock()
    agent.paw = 'agent-001'
    agent.platform = 'windows'
    agent.host = 'WORKSTATION-01'
    agent.username = 'testuser'
    agent.privilege = 'User'
    agent.last_seen = datetime.now().isoformat()
    return agent


@pytest.fixture
def mock_operation_simple(mock_agent, mock_link_success):
    """Mock simple operation with 1 successful technique."""
    operation = MagicMock()
    operation.id = 'op-simple-001'
    operation.name = 'Test Operation - Simple'
    operation.group = 'client_demo'
    operation.adversary = MagicMock(name='Demo Adversary', description='Test adversary')
    operation.jitter = '2/8'
    operation.source = MagicMock(name='basic')
    operation.planner = MagicMock(name='atomic')
    operation.state = 'finished'
    operation.start = datetime.now() - timedelta(minutes=5)
    operation.finish = datetime.now()
    operation.chain = [mock_link_success]
    operation.agents = [mock_agent]
    return operation


@pytest.fixture
def mock_operation_complex(
    mock_agent,
    mock_link_success,
    mock_link_failed,
    mock_link_timeout,
    mock_ability_t1078,
    mock_ability_t1059,
    mock_ability_t1018
):
    """Mock complex operation with 30 techniques (mixed success/failure)."""
    operation = MagicMock()
    operation.id = 'op-complex-001'
    operation.name = 'Purple Team Exercise - Q1 2025'
    operation.group = 'acme_corp'
    operation.adversary = MagicMock(
        name='APT Simulation',
        description='Advanced persistent threat simulation'
    )
    operation.jitter = '4/8'
    operation.source = MagicMock(name='adversary_profile')
    operation.planner = MagicMock(name='batch')
    operation.state = 'finished'
    operation.start = datetime.now() - timedelta(hours=2)
    operation.finish = datetime.now()
    
    # Create 30 links (20 success, 8 failed, 2 timeout)
    links = []
    for i in range(20):
        link = MagicMock()
        link.ability = mock_ability_t1078
        link.status = 0
        link.finish = (datetime.now() - timedelta(minutes=120-i*4)).isoformat()
        link.command = f'test_command_{i}'
        link.output = f'Output {i}'
        links.append(link)
    
    for i in range(8):
        link = MagicMock()
        link.ability = mock_ability_t1059
        link.status = 1
        link.finish = (datetime.now() - timedelta(minutes=80-i*4)).isoformat()
        link.command = f'failed_command_{i}'
        link.output = 'Access Denied'
        links.append(link)
    
    for i in range(2):
        link = MagicMock()
        link.ability = mock_ability_t1018
        link.status = -2
        link.finish = (datetime.now() - timedelta(minutes=40-i*4)).isoformat()
        link.command = f'timeout_command_{i}'
        link.output = ''
        links.append(link)
    
    operation.chain = links
    operation.agents = [mock_agent]
    
    return operation


@pytest.fixture
def mock_operation_empty():
    """Mock operation with no techniques executed."""
    operation = MagicMock()
    operation.id = 'op-empty-001'
    operation.name = 'Empty Operation'
    operation.group = 'test'
    operation.adversary = MagicMock(name='Test', description='Test')
    operation.state = 'finished'
    operation.start = datetime.now()
    operation.finish = datetime.now()
    operation.chain = []
    operation.agents = []
    return operation


@pytest.fixture
def mock_operation_running():
    """Mock operation that is still running (not finished)."""
    operation = MagicMock()
    operation.id = 'op-running-001'
    operation.name = 'Running Operation'
    operation.state = 'running'
    operation.start = datetime.now() - timedelta(minutes=10)
    operation.finish = None
    operation.chain = []
    return operation
