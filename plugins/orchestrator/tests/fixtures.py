"""Pytest fixtures for orchestrator plugin tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


@pytest.fixture
def mock_logger():
    """Mock Python logger."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    return logger


@pytest.fixture
def mock_operation():
    """Mock Caldera operation with complete attributes."""
    op = MagicMock()
    op.id = 'test-operation-abc123'
    op.name = 'Discovery & Credential Access'
    op.group = 'client_acme'
    op.state = 'running'
    op.start = datetime(2026, 1, 6, 10, 0, 0)
    op.finish = None
    op.agents = ['agent1', 'agent2']
    
    # Mock technique chain
    link1 = MagicMock()
    link1.ability.technique_id = 'T1078'
    link1.ability.name = 'Valid Accounts'
    link1.ability.tactic = 'Persistence'
    link1.status = 0
    
    link2 = MagicMock()
    link2.ability.technique_id = 'T1059.001'
    link2.ability.name = 'PowerShell'
    link2.ability.tactic = 'Execution'
    link2.status = 0
    
    op.chain = [link1, link2]
    
    return op


@pytest.fixture
def mock_operation_empty_chain():
    """Mock operation with no techniques."""
    op = MagicMock()
    op.id = 'empty-op-123'
    op.name = 'Empty Operation'
    op.group = 'test_client'
    op.state = 'finished'
    op.agents = []
    op.chain = []
    return op


@pytest.fixture
def mock_elk_client():
    """Mock AsyncElasticsearch client."""
    client = AsyncMock()
    
    # Mock successful index response
    client.index = AsyncMock(return_value={
        '_id': 'elk-doc-123',
        '_index': 'purple-team-logs',
        'result': 'created'
    })
    
    client.close = AsyncMock()
    
    return client
