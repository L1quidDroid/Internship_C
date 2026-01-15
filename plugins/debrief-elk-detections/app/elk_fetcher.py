"""
ELK Detection Fetcher for Debrief Plugin.

Queries Elasticsearch purple-team-logs-* index to correlate Caldera operations
with SIEM detection events. Provides detection coverage metrics for debrief reports.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ConnectionError, TransportError
except ImportError:
    AsyncElasticsearch = None
    ConnectionError = Exception
    TransportError = Exception


async def fetch_detection_data_for_operations(operation_ids: List[str], config: dict, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Query ELK for detection status of techniques across multiple operations.
    
    Args:
        operation_ids: List of Caldera operation UUIDs
        config: Plugin configuration dict with ELK settings
        logger: Python logger instance
    
    Returns:
        Dict mapping technique_id -> {status, rule_name, alert_count, tactic, coverage}
    """
    log = logger or logging.getLogger('debrief.elk_detections')
    
    # Validate operation IDs to prevent injection attacks
    validated_ids = []
    for op_id in operation_ids:
        try:
            # Ensure it's a valid UUID format
            uuid.UUID(op_id)
            validated_ids.append(op_id)
        except (ValueError, AttributeError) as e:
            log.warning(f'Invalid operation ID format: {op_id} - {e}')
            continue
    
    if not validated_ids:
        log.error('No valid operation IDs provided after validation')
        return {'available': False, 'reason': 'Invalid operation IDs', 'techniques': {}}
    
    if not AsyncElasticsearch:
        log.warning('elasticsearch library not installed, detection data unavailable')
        return {'available': False, 'reason': 'elasticsearch library not installed', 'techniques': {}}
    
    # Get ELK connection settings (fallback to orchestrator config)
    elk_url, elk_user, elk_pass, elk_api_key, verify_ssl = _get_elk_config(config, log)
    
    if not elk_url:
        return {'available': False, 'reason': 'ELK not configured', 'techniques': {}}
    
    # Initialize Elasticsearch client
    client_kwargs = {
        'hosts': [elk_url],
        'verify_certs': verify_ssl,
        'request_timeout': config.get('elk_connection_timeout', 30),
        'max_retries': 2,
        'retry_on_timeout': True
    }
    
    if elk_api_key:
        client_kwargs['api_key'] = elk_api_key
    elif elk_user and elk_pass:
        client_kwargs['basic_auth'] = (elk_user, elk_pass)
    
    es = AsyncElasticsearch(**client_kwargs)
    
    try:
        # Validate ELK schema to detect orchestrator drift
        index_pattern = config.get('elk_index', 'purple-team-logs-*')
        await _validate_elk_schema(es, index_pattern, config, log)
        
        # Build query for multiple operations
        field_mappings = config.get('field_mappings', {})
        operation_field = field_mappings.get('operation_id', 'purple.operation_id')
        technique_field = field_mappings.get('technique', 'purple.technique')
        status_field = field_mappings.get('detection_status', 'purple.detection_status')
        rule_field = field_mappings.get('rule_name', 'rule.name')
        
        query = {
            'bool': {
                'must': [
                    {'terms': {f'{operation_field}.keyword': validated_ids}},
                    {'exists': {'field': technique_field}}
                ]
            }
        }
        
        # Search with aggregations
        index_pattern = config.get('elk_index', 'purple-team-logs-*')
        response = await es.search(
            index=index_pattern,
            query=query,
            size=0,  # We only want aggregations
            aggs={
                'techniques': {
                    'terms': {
                        'field': f'{technique_field}.keyword',
                        'size': config.get('max_techniques_per_query', 100)
                    },
                    'aggs': {
                        'detection_status': {
                            'terms': {
                                'field': f'{status_field}.keyword',
                                'size': 10
                            }
                        },
                        'rule_names': {
                            'terms': {
                                'field': f'{rule_field}.keyword',
                                'size': 3
                            }
                        }
                    }
                }
            }
        )
        
        # Parse aggregations into technique map
        detections = {}
        total_events = response.get('hits', {}).get('total', {}).get('value', 0)
        
        for bucket in response.get('aggregations', {}).get('techniques', {}).get('buckets', []):
            technique_id = bucket['key']
            alert_count = bucket['doc_count']
            
            # Determine primary status (detected > evaded > pending)
            status_buckets = bucket.get('detection_status', {}).get('buckets', [])
            status = 'pending'
            if any(s['key'].lower() == 'detected' for s in status_buckets):
                status = 'detected'
            elif any(s['key'].lower() == 'evaded' for s in status_buckets):
                status = 'evaded'
            
            # Extract rule names
            rule_buckets = bucket.get('rule_names', {}).get('buckets', [])
            rule_names = [r['key'] for r in rule_buckets[:3]]
            rule_name = rule_names[0] if rule_names else 'No rule fired'
            
            detections[technique_id] = {
                'status': status,
                'rule_name': rule_name,
                'rule_names': rule_names,
                'alert_count': alert_count,
                'coverage': 100.0 if status == 'detected' else 0.0
            }
        
        log.info(f'Fetched detection data for {len(detections)} techniques across {len(validated_ids)} operations ({total_events} events)')
        
        return {
            'available': True,
            'techniques': detections,
            'total_events': total_events,
            'queried_at': datetime.utcnow().isoformat() + 'Z'
        }
        
    except (ConnectionError, TransportError) as e:
        log.warning(f'ELK connection failed: {e}')
        return {'available': False, 'reason': f'Connection failed: {str(e)[:100]}', 'techniques': {}}
    
    except Exception as e:
        log.error(f'Failed to fetch detection data: {e}', exc_info=True)
        return {'available': False, 'reason': f'Query failed: {str(e)[:100]}', 'techniques': {}}
    
    finally:
        await es.close()


def _get_elk_config(config: dict, log: logging.Logger) -> tuple:
    """
    Get ELK connection settings from config or orchestrator fallback.
    
    Returns:
        Tuple of (elk_url, elk_user, elk_pass, elk_api_key, verify_ssl)
    """
    # Try plugin-specific config first
    elk_url = config.get('elk_url')
    elk_user = config.get('elk_user')
    elk_pass = config.get('elk_pass')
    elk_api_key = config.get('elk_api_key')
    verify_ssl = config.get('elk_verify_ssl', False)
    
    # Fallback to orchestrator config
    if not elk_url:
        try:
            from plugins.orchestrator.app.config import OrchestratorConfig
            OrchestratorConfig.load()
            
            elk_url = OrchestratorConfig.ELK_URL
            elk_user = OrchestratorConfig.ELK_USER
            elk_pass = OrchestratorConfig.ELK_PASS
            elk_api_key = OrchestratorConfig.ELK_API_KEY
            verify_ssl = OrchestratorConfig.ELK_VERIFY_SSL
            
            log.debug('Using orchestrator ELK config')
            
        except ImportError:
            log.warning('Orchestrator config not available and no plugin-specific ELK config provided')
    
    return elk_url, elk_user, elk_pass, elk_api_key, verify_ssl


async def _validate_elk_schema(es: AsyncElasticsearch, index_pattern: str, config: dict, log: logging.Logger):
    """
    Validate that required purple.* fields exist in ELK index mappings.
    Detects orchestrator schema drift to prevent query failures.
    
    Raises:
        ValueError if critical fields are missing
    """
    try:
        # Get index mappings
        mappings = await es.indices.get_mapping(index=index_pattern, ignore_unavailable=True)
        
        if not mappings:
            log.warning(f'No indices found matching pattern: {index_pattern}')
            return
        
        # Check first available index (they should all have the same schema)
        first_index = list(mappings.keys())[0]
        properties = mappings[first_index]['mappings'].get('properties', {})
        
        # Extract required fields from config
        field_mappings = config.get('field_mappings', {})
        required_fields = {
            'operation_id': field_mappings.get('operation_id', 'purple.operation_id'),
            'technique': field_mappings.get('technique', 'purple.technique'),
            'detection_status': field_mappings.get('detection_status', 'purple.detection_status'),
        }
        
        missing_fields = []
        
        # Check if nested purple.* fields exist
        for field_name, field_path in required_fields.items():
            if '.' in field_path:
                # Nested field (e.g., purple.operation_id)
                parent, child = field_path.split('.', 1)
                
                if parent not in properties:
                    missing_fields.append(field_path)
                elif 'properties' in properties[parent]:
                    # Check child field exists
                    child_props = properties[parent]['properties']
                    if child not in child_props:
                        missing_fields.append(field_path)
            else:
                # Top-level field
                if field_path not in properties:
                    missing_fields.append(field_path)
        
        if missing_fields:
            error_msg = f"ELK schema validation failed - missing required fields: {', '.join(missing_fields)}. Check orchestrator plugin schema or update field_mappings in config."
            log.error(error_msg)
            raise ValueError(error_msg)
        
        log.debug(f'ELK schema validation passed for index: {first_index}')
        
    except Exception as e:
        log.warning(f'Schema validation skipped due to error: {e}')
        # Don't fail hard - allow queries to proceed and fail naturally if schema is wrong
            return (None, None, None, None, False)
    
    return (elk_url, elk_user, elk_pass, elk_api_key, verify_ssl)
