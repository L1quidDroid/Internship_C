"""Unit tests for ELK tagger service."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import json

from plugins.orchestrator.app.elk_tagger import ELKTagger
from plugins.orchestrator.app.config import OrchestratorConfig
from plugins.orchestrator.tests.fixtures import (
    mock_logger,
    mock_operation,
    mock_operation_empty_chain,
    mock_elk_client
)


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
    
    def test_sanitize_metadata_removes_special_chars(self, mock_logger):
        """Test metadata sanitization."""
        tagger = ELKTagger(mock_logger)
        
        metadata = {
            'operation_name': '<script>alert("xss")</script>Test Operation',
            'techniques': ['T1078', 'T1059.001', 'INVALID', 'T9999.999'],
            'tactics': ['Persistence', 'Execution', 'Invalid@Tactic'],
            'client_id': '../../../etc/passwd'
        }
        
        sanitized = tagger._sanitize_metadata(metadata)
        
        # Operation name sanitized
        assert '<script>' not in sanitized['operation_name']
        assert 'alert' not in sanitized['operation_name']
        
        # Only valid techniques kept
        assert sanitized['techniques'] == ['T1078', 'T1059.001']
        
        # Only valid tactics kept
        assert 'Persistence' in sanitized['tactics']
        assert 'Execution' in sanitized['tactics']
        assert 'Invalid@Tactic' not in sanitized['tactics']
        
        # Path traversal removed
        assert '../' not in sanitized['client_id']


class TestELKTaggerMetadata:
    """Test metadata building."""
    
    def test_build_metadata_structure(self, mock_logger, mock_operation):
        """Test metadata has correct structure."""
        tagger = ELKTagger(mock_logger)
        metadata = tagger._build_metadata(mock_operation)
        
        # Required fields present
        assert 'operation_id' in metadata
        assert 'operation_name' in metadata
        assert 'purple_team_exercise' in metadata
        assert 'timestamp' in metadata
        assert 'techniques' in metadata
        assert 'tactics' in metadata
        
        # Correct values
        assert metadata['operation_id'] == 'test-operation-abc123'
        assert metadata['purple_team_exercise'] is True
        assert metadata['client_id'] == 'client_acme'
        assert 'T1078' in metadata['techniques']
        assert 'T1059.001' in metadata['techniques']
        assert 'Persistence' in metadata['tactics']
    
    def test_build_metadata_handles_empty_chain(self, mock_logger, mock_operation_empty_chain):
        """Test metadata with no techniques."""
        tagger = ELKTagger(mock_logger)
        metadata = tagger._build_metadata(mock_operation_empty_chain)
        
        assert metadata['techniques'] == []
        assert metadata['tactics'] == []
        assert metadata['agent_count'] == 0
    
    def test_build_metadata_deduplicates_techniques(self, mock_logger):
        """Test duplicate technique removal."""
        op = MagicMock()
        op.id = 'test-123'
        op.name = 'Test'
        op.group = 'client'
        op.agents = []
        op.state = 'running'
        
        # Duplicate techniques
        link1 = MagicMock()
        link1.ability.technique_id = 'T1078'
        link1.ability.tactic = 'Persistence'
        
        link2 = MagicMock()
        link2.ability.technique_id = 'T1078'  # Duplicate
        link2.ability.tactic = 'Persistence'
        
        op.chain = [link1, link2]
        
        tagger = ELKTagger(mock_logger)
        metadata = tagger._build_metadata(op)
        
        # Only one T1078
        assert metadata['techniques'].count('T1078') == 1
    
    def test_build_metadata_truncates_large_technique_lists(self, mock_logger):
        """Test technique list truncation at 500."""
        op = MagicMock()
        op.id = 'test-123'
        op.name = 'Test'
        op.group = 'client'
        op.agents = []
        op.state = 'running'
        
        # Create 600 unique techniques
        op.chain = []
        for i in range(600):
            link = MagicMock()
            link.ability.technique_id = f'T{1000 + i}'
            link.ability.tactic = 'Discovery'
            op.chain.append(link)
        
        tagger = ELKTagger(mock_logger)
        metadata = tagger._build_metadata(op)
        
        # Truncated to 500
        assert len(metadata['techniques']) == 500
        # Total count preserved
        assert metadata['technique_count_total'] == 600


@pytest.mark.asyncio
class TestELKTaggerTagging:
    """Test tagging functionality."""
    
    async def test_tag_successful_elk_post(self, mock_logger, mock_operation, mock_elk_client):
        """Test successful ELK tagging."""
        tagger = ELKTagger(mock_logger)
        tagger.elk_client = mock_elk_client
        
        response = await tagger.tag(mock_operation)
        
        # ELK client called
        assert mock_elk_client.index.called
        
        # Response returned
        assert response is not None
        assert response['_id'] == 'elk-doc-123'
        
        # Logger called
        assert mock_logger.info.called
    
    async def test_tag_handles_none_operation(self, mock_logger):
        """Test None operation handling."""
        tagger = ELKTagger(mock_logger)
        
        response = await tagger.tag(None)
        
        assert response is None
        assert mock_logger.warning.called
    
    async def test_tag_handles_invalid_operation_id(self, mock_logger):
        """Test invalid operation ID handling."""
        op = MagicMock()
        op.id = 'invalid@id'
        
        tagger = ELKTagger(mock_logger)
        response = await tagger.tag(op)
        
        assert response is None
        assert mock_logger.warning.called
    
    async def test_tag_creates_fallback_on_elk_failure(self, mock_logger, mock_operation, tmp_path):
        """Test fallback logging when ELK fails."""
        # Mock failing ELK client
        elk_client = AsyncMock()
        from plugins.orchestrator.app.elk_tagger import ConnectionError as ELKConnectionError
        elk_client.index = AsyncMock(side_effect=ELKConnectionError('ELK unreachable'))
        
        tagger = ELKTagger(mock_logger)
        tagger.elk_client = elk_client
        tagger.fallback_dir = tmp_path  # Use pytest temp directory
        
        response = await tagger.tag(mock_operation)
        
        # Returns None (fallback used)
        assert response is None
        
        # Fallback file created
        fallback_files = list(tmp_path.glob('fallback_*.json'))
        assert len(fallback_files) == 1
        
        # Fallback contains correct data
        with open(fallback_files[0]) as f:
            data = json.load(f)
        assert data['operation_id'] == 'test-operation-abc123'
        assert data['purple_team_exercise'] is True
    
    async def test_tag_circuit_breaker_opens_after_failures(self, mock_logger, mock_operation):
        """Test circuit breaker pattern."""
        # Mock failing ELK client
        elk_client = AsyncMock()
        from plugins.orchestrator.app.elk_tagger import ConnectionError as ELKConnectionError
        elk_client.index = AsyncMock(side_effect=ELKConnectionError('ELK down'))
        
        tagger = ELKTagger(mock_logger)
        tagger.elk_client = elk_client
        tagger.fallback_dir = Path('/tmp')  # Use /tmp for test
        tagger._max_failures = 3  # Lower threshold for test
        
        # Trigger failures
        for _ in range(4):
            await tagger.tag(mock_operation)
        
        # Circuit should be open
        assert tagger._circuit_open is True
        assert tagger._failure_count >= 3


@pytest.mark.asyncio
class TestELKTaggerCleanup:
    """Test cleanup and resource management."""
    
    async def test_close_client(self, mock_logger, mock_elk_client):
        """Test ELK client cleanup."""
        tagger = ELKTagger(mock_logger)
        tagger.elk_client = mock_elk_client
        
        await tagger.close()
        
        assert mock_elk_client.close.called
