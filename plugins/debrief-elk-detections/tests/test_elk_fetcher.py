"""
Unit tests for ELK detection fetcher.

Tests various scenarios:
- Successful ELK query with detection data
- Mixed detection statuses (detected/evaded/pending)
- ELK connection failures
- Empty results
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Import the function to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.debrief_elk_detections.app.elk_fetcher import fetch_detection_data_for_operations


class TestELKFetcher:
    """Test suite for ELK detection data fetcher."""
    
    @pytest.fixture
    def mock_config(self):
        """Standard configuration for tests."""
        return {
            'elk_url': 'http://test-elk:9200',
            'elk_user': 'elastic',
            'elk_pass': 'testpass',
            'elk_index': 'purple-team-logs-*',
            'elk_connection_timeout': 30,
            'max_techniques_per_query': 100,
            'field_mappings': {
                'operation_id': 'purple.operation_id',
                'technique': 'purple.technique',
                'detection_status': 'purple.detection_status',
                'rule_name': 'rule.name'
            }
        }
    
    @pytest.fixture
    def mock_elk_response_detected(self):
        """Mock ELK response with all techniques detected."""
        return {
            'hits': {
                'total': {'value': 15}
            },
            'aggregations': {
                'techniques': {
                    'buckets': [
                        {
                            'key': 'T1078',
                            'doc_count': 5,
                            'detection_status': {
                                'buckets': [{'key': 'detected', 'doc_count': 5}]
                            },
                            'rule_names': {
                                'buckets': [
                                    {'key': 'Valid Accounts Detection', 'doc_count': 5}
                                ]
                            }
                        },
                        {
                            'key': 'T1059.001',
                            'doc_count': 10,
                            'detection_status': {
                                'buckets': [{'key': 'detected', 'doc_count': 10}]
                            },
                            'rule_names': {
                                'buckets': [
                                    {'key': 'PowerShell Execution', 'doc_count': 10}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    
    @pytest.fixture
    def mock_elk_response_mixed(self):
        """Mock ELK response with mixed detection statuses."""
        return {
            'hits': {
                'total': {'value': 20}
            },
            'aggregations': {
                'techniques': {
                    'buckets': [
                        {
                            'key': 'T1078',
                            'doc_count': 5,
                            'detection_status': {
                                'buckets': [{'key': 'detected', 'doc_count': 5}]
                            },
                            'rule_names': {
                                'buckets': [{'key': 'Valid Accounts Detection', 'doc_count': 5}]
                            }
                        },
                        {
                            'key': 'T1087',
                            'doc_count': 3,
                            'detection_status': {
                                'buckets': [{'key': 'evaded', 'doc_count': 3}]
                            },
                            'rule_names': {
                                'buckets': []
                            }
                        },
                        {
                            'key': 'T1082',
                            'doc_count': 2,
                            'detection_status': {
                                'buckets': [{'key': 'pending', 'doc_count': 2}]
                            },
                            'rule_names': {
                                'buckets': []
                            }
                        }
                    ]
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_successful_query_all_detected(self, mock_config, mock_elk_response_detected):
        """Test successful ELK query with all techniques detected."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch') as mock_es_class:
            # Setup mock
            mock_es = AsyncMock()
            mock_es.search = AsyncMock(return_value=mock_elk_response_detected)
            mock_es.close = AsyncMock()
            mock_es_class.return_value = mock_es
            
            # Execute
            result = await fetch_detection_data_for_operations(
                ['op-123', 'op-456'],
                mock_config,
                None
            )
            
            # Verify
            assert result['available'] is True
            assert result['total_events'] == 15
            assert len(result['techniques']) == 2
            assert result['techniques']['T1078']['status'] == 'detected'
            assert result['techniques']['T1078']['alert_count'] == 5
            assert result['techniques']['T1078']['rule_name'] == 'Valid Accounts Detection'
            assert result['techniques']['T1059.001']['status'] == 'detected'
            
            # Verify ELK client was called correctly
            mock_es.search.assert_called_once()
            mock_es.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mixed_detection_statuses(self, mock_config, mock_elk_response_mixed):
        """Test ELK query with mixed detection statuses."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch') as mock_es_class:
            mock_es = AsyncMock()
            mock_es.search = AsyncMock(return_value=mock_elk_response_mixed)
            mock_es.close = AsyncMock()
            mock_es_class.return_value = mock_es
            
            result = await fetch_detection_data_for_operations(['op-123'], mock_config, None)
            
            assert result['available'] is True
            assert len(result['techniques']) == 3
            assert result['techniques']['T1078']['status'] == 'detected'
            assert result['techniques']['T1087']['status'] == 'evaded'
            assert result['techniques']['T1082']['status'] == 'pending'
            assert result['techniques']['T1087']['rule_name'] == 'No rule fired'
    
    @pytest.mark.asyncio
    async def test_elk_connection_failure(self, mock_config):
        """Test graceful handling of ELK connection failure."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch') as mock_es_class:
            mock_es = AsyncMock()
            from elasticsearch.exceptions import ConnectionError
            mock_es.search = AsyncMock(side_effect=ConnectionError('Connection refused'))
            mock_es.close = AsyncMock()
            mock_es_class.return_value = mock_es
            
            result = await fetch_detection_data_for_operations(['op-123'], mock_config, None)
            
            assert result['available'] is False
            assert 'Connection failed' in result['reason']
            assert result['techniques'] == {}
            mock_es.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_empty_results(self, mock_config):
        """Test handling of query with no results."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch') as mock_es_class:
            mock_es = AsyncMock()
            mock_es.search = AsyncMock(return_value={
                'hits': {'total': {'value': 0}},
                'aggregations': {'techniques': {'buckets': []}}
            })
            mock_es.close = AsyncMock()
            mock_es_class.return_value = mock_es
            
            result = await fetch_detection_data_for_operations(['op-999'], mock_config, None)
            
            assert result['available'] is True
            assert result['total_events'] == 0
            assert len(result['techniques']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_elasticsearch_library(self, mock_config):
        """Test graceful degradation when elasticsearch library not installed."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch', None):
            result = await fetch_detection_data_for_operations(['op-123'], mock_config, None)
            
            assert result['available'] is False
            assert 'elasticsearch library not installed' in result['reason']
    
    @pytest.mark.asyncio
    async def test_orchestrator_config_fallback(self, mock_config):
        """Test fallback to orchestrator config when plugin config empty."""
        with patch('plugins.debrief_elk_detections.app.elk_fetcher.AsyncElasticsearch') as mock_es_class:
            with patch('plugins.debrief_elk_detections.app.elk_fetcher.OrchestratorConfig') as mock_orc_cfg:
                # Setup orchestrator config mock
                mock_orc_cfg.load = MagicMock()
                mock_orc_cfg.ELK_URL = 'http://orchestrator-elk:9200'
                mock_orc_cfg.ELK_USER = 'elastic'
                mock_orc_cfg.ELK_PASS = 'orch-pass'
                mock_orc_cfg.ELK_API_KEY = ''
                mock_orc_cfg.ELK_VERIFY_SSL = False
                
                mock_es = AsyncMock()
                mock_es.search = AsyncMock(return_value={
                    'hits': {'total': {'value': 0}},
                    'aggregations': {'techniques': {'buckets': []}}
                })
                mock_es.close = AsyncMock()
                mock_es_class.return_value = mock_es
                
                # Test with empty plugin config
                empty_config = {'field_mappings': mock_config['field_mappings']}
                result = await fetch_detection_data_for_operations(['op-123'], empty_config, None)
                
                # Verify it used orchestrator config
                assert result['available'] is True
                mock_orc_cfg.load.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
