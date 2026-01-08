"""
ELK Detection Fetcher for Reporting Plugin.

Queries Elasticsearch purple-team-logs-* index to correlate Caldera operations
with SIEM detection events. Provides detection coverage metrics for PDF reports.

Reuses authentication pattern from orchestrator plugin config.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ConnectionError, TransportError
except ImportError:
    AsyncElasticsearch = None
    ConnectionError = Exception
    TransportError = Exception


class ELKFetcher:
    """
    Fetches detection data from Elasticsearch for report generation.
    
    Features:
    - Async Elasticsearch client with connection pooling
    - Queries purple-team-logs-* for operation correlation
    - Graceful fallback when ELK unavailable
    - Detection status aggregation (detected/evaded/pending)
    """
    
    def __init__(self, config, logger: Optional[logging.Logger] = None):
        """
        Initialize ELK fetcher with configuration.
        
        Args:
            config: ReportingConfig or dict with ELK settings
            logger: Python logger instance
        """
        self.log = logger or logging.getLogger('reporting.elk_fetcher')
        self.config = config
        self.elk_client = self._init_elk_client()
        
        # Track connection state
        self._connected = False
        self._last_error = None
    
    def _init_elk_client(self) -> Optional[AsyncElasticsearch]:
        """
        Initialize async Elasticsearch client.
        
        Reuses orchestrator's ELK configuration if available.
        
        Returns:
            AsyncElasticsearch client or None if unavailable
        """
        if not AsyncElasticsearch:
            self.log.warning('elasticsearch library not installed, detection data unavailable')
            return None
        
        try:
            # Try to import orchestrator config for ELK settings
            try:
                from plugins.orchestrator.app.config import OrchestratorConfig
                OrchestratorConfig.load()
                
                elk_url = OrchestratorConfig.ELK_URL
                elk_user = OrchestratorConfig.ELK_USER
                elk_pass = OrchestratorConfig.ELK_PASS
                elk_api_key = OrchestratorConfig.ELK_API_KEY
                verify_ssl = OrchestratorConfig.ELK_VERIFY_SSL
                
                self.log.info(f'Using orchestrator ELK config: {elk_url}')
                
            except ImportError:
                # Fallback to defaults
                elk_url = 'http://localhost:9200'
                elk_user = 'elastic'
                elk_pass = ''
                elk_api_key = ''
                verify_ssl = False
                self.log.warning('Orchestrator config not available, using defaults')
            
            # Build client kwargs
            client_kwargs = {
                'hosts': [elk_url],
                'verify_certs': verify_ssl,
                'request_timeout': 30,
                'max_retries': 2,
                'retry_on_timeout': True
            }
            
            # API key auth (preferred)
            if elk_api_key:
                client_kwargs['api_key'] = elk_api_key
            # Basic auth fallback
            elif elk_user and elk_pass:
                client_kwargs['basic_auth'] = (elk_user, elk_pass)
            
            client = AsyncElasticsearch(**client_kwargs)
            self.log.info(f'ELK client initialized for reporting: {elk_url}')
            return client
        
        except Exception as e:
            self.log.error(f'Failed to initialize ELK client: {e}')
            self._last_error = str(e)
            return None
    
    async def get_detection_data(self, operation_id: str) -> Dict[str, Any]:
        """
        Fetch detection data for a Caldera operation.
        
        Queries purple-team-logs-* for documents matching the operation ID,
        aggregates detection status by technique.
        
        Args:
            operation_id: Caldera operation UUID
            
        Returns:
            Dict with detection metrics:
            {
                'available': bool,
                'total_events': int,
                'techniques': {
                    'T1078': {'status': 'detected', 'count': 3},
                    'T1059.001': {'status': 'pending', 'count': 1}
                },
                'summary': {
                    'detected': 5,
                    'evaded': 2,
                    'pending': 3,
                    'coverage_percent': 50.0
                }
            }
        """
        if not self.elk_client:
            return self._empty_detection_data('ELK client not available')
        
        try:
            # Query purple-team-logs-* for this operation
            query = {
                'bool': {
                    'should': [
                        {'term': {'purple.operation_id': operation_id}},
                        {'term': {'operation_id': operation_id}},
                        {'match': {'tags': f'purple_{operation_id[:8]}'}}
                    ],
                    'minimum_should_match': 1
                }
            }
            
            # Search with aggregations
            response = await self.elk_client.search(
                index='purple-team-logs-*,auditbeat-*',
                query=query,
                size=100,
                aggs={
                    'by_technique': {
                        'terms': {
                            'field': 'purple.technique',
                            'size': 500
                        },
                        'aggs': {
                            'detection_status': {
                                'terms': {
                                    'field': 'purple.detection_status',
                                    'size': 10
                                }
                            }
                        }
                    },
                    'by_status': {
                        'terms': {
                            'field': 'purple.detection_status',
                            'size': 10
                        }
                    }
                }
            )
            
            self._connected = True
            return self._parse_detection_response(response)
        
        except (ConnectionError, TransportError) as e:
            self.log.warning(f'ELK connection failed: {e}')
            self._connected = False
            self._last_error = str(e)
            return self._empty_detection_data(f'ELK connection failed: {str(e)[:100]}')
        
        except Exception as e:
            self.log.error(f'Failed to fetch detection data: {e}')
            self._last_error = str(e)
            return self._empty_detection_data(f'Query failed: {str(e)[:100]}')
    
    def _parse_detection_response(self, response: Dict) -> Dict[str, Any]:
        """
        Parse Elasticsearch response into detection metrics.
        
        Args:
            response: Raw ES search response
            
        Returns:
            Structured detection data dict
        """
        hits = response.get('hits', {})
        total_events = hits.get('total', {}).get('value', 0)
        
        techniques = {}
        summary = {'detected': 0, 'evaded': 0, 'pending': 0}
        
        # Parse technique aggregations
        aggs = response.get('aggregations', {})
        by_technique = aggs.get('by_technique', {}).get('buckets', [])
        
        for bucket in by_technique:
            technique_id = bucket.get('key')
            if not technique_id:
                continue
            
            # Get detection status for this technique
            status_buckets = bucket.get('detection_status', {}).get('buckets', [])
            status = 'pending'  # Default
            
            for status_bucket in status_buckets:
                s = status_bucket.get('key', '').lower()
                if s in ('detected', 'evaded', 'pending'):
                    status = s
                    break
            
            techniques[technique_id] = {
                'status': status,
                'count': bucket.get('doc_count', 0)
            }
        
        # Parse overall status summary
        by_status = aggs.get('by_status', {}).get('buckets', [])
        for bucket in by_status:
            status = bucket.get('key', '').lower()
            count = bucket.get('doc_count', 0)
            if status in summary:
                summary[status] = count
        
        # Calculate coverage percentage
        total_techniques = len(techniques)
        if total_techniques > 0:
            detected_count = sum(1 for t in techniques.values() if t['status'] == 'detected')
            summary['coverage_percent'] = round((detected_count / total_techniques) * 100, 1)
        else:
            summary['coverage_percent'] = 0.0
        
        return {
            'available': True,
            'total_events': total_events,
            'techniques': techniques,
            'summary': summary,
            'queried_at': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _empty_detection_data(self, reason: str) -> Dict[str, Any]:
        """
        Return empty detection data structure when ELK unavailable.
        
        Args:
            reason: Why data is unavailable
            
        Returns:
            Empty detection data dict
        """
        return {
            'available': False,
            'reason': reason,
            'total_events': 0,
            'techniques': {},
            'summary': {
                'detected': 0,
                'evaded': 0,
                'pending': 0,
                'coverage_percent': 0.0
            }
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test ELK connectivity for health checks.
        
        Returns:
            Connection status dict
        """
        if not self.elk_client:
            return {
                'status': 'unavailable',
                'error': 'ELK client not initialized',
                'last_error': self._last_error
            }
        
        try:
            info = await self.elk_client.info()
            self._connected = True
            return {
                'status': 'connected',
                'cluster_name': info.get('cluster_name'),
                'version': info.get('version', {}).get('number')
            }
        except Exception as e:
            self._connected = False
            self._last_error = str(e)
            return {
                'status': 'error',
                'error': str(e)[:200]
            }
    
    async def close(self):
        """Close ELK client connection."""
        if self.elk_client:
            await self.elk_client.close()
            self.log.info('ELK client closed')
