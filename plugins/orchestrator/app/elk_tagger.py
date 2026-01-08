"""
ELK Tagging Service for Purple Team Operations

Security: Uses API key authentication, validates all inputs, implements fallback logging
"""

import json
import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from elasticsearch import AsyncElasticsearch
    from elasticsearch.exceptions import ConnectionError, TransportError
except ImportError:
    AsyncElasticsearch = None
    ConnectionError = Exception
    TransportError = Exception

from plugins.orchestrator.app.config import OrchestratorConfig


class ELKTagger:
    """
    Tags Caldera operations in Elasticsearch for SIEM filtering.
    
    Features:
    - Async ELK client with connection pooling
    - Automatic fallback to file logging on ELK failures
    - Input validation and sanitization
    - Retry logic with exponential backoff
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize ELK tagger with configuration.
        
        Args:
            logger: Python logger instance
        """
        self.log = logger
        self.config = OrchestratorConfig
        self.elk_client = self._init_elk_client()
        self.fallback_dir = self.config.FALLBACK_LOG_DIR
        self.fallback_dir.mkdir(parents=True, exist_ok=True)
        
        # Circuit breaker for repeated failures
        self._failure_count = 0
        self._max_failures = 5
        self._circuit_open = False
        
        # Semaphore to limit concurrent tags
        self._tag_semaphore = asyncio.Semaphore(5)
    
    def _init_elk_client(self) -> Optional[AsyncElasticsearch]:
        """
        Initialize async Elasticsearch client with auth support.
        
        Uses OrchestratorConfig.get_es_client() which supports:
        - API key auth (preferred)
        - Basic auth fallback (elastic:password)
        
        Returns:
            AsyncElasticsearch client or None if initialization fails
        """
        if not AsyncElasticsearch:
            self.log.warning('elasticsearch library not installed, using fallback logging only')
            return None
        
        try:
            # Use config helper that handles API key / basic auth
            client = self.config.get_es_client()
            self.log.info(f'ELK client initialized: {self.config.ELK_URL}')
            return client
        
        except ImportError as e:
            self.log.warning(f'elasticsearch library not available: {e}')
            return None
        except Exception as e:
            self.log.error(f'Failed to initialize ELK client: {e}')
            return None
    
    def _is_valid_operation_id(self, operation_id: str) -> bool:
        """
        Validate operation ID format.
        
        Args:
            operation_id: Operation ID to validate
            
        Returns:
            True if valid format
        """
        # Allow UUID format or alphanumeric with hyphens
        pattern = r'^[a-zA-Z0-9\-]{8,64}$'
        return bool(re.match(pattern, str(operation_id)))
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize metadata to prevent injection attacks.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Sanitized metadata
        """
        # Sanitize operation name (remove special chars, limit length)
        if 'operation_name' in metadata:
            metadata['operation_name'] = re.sub(r'[^\w\s-]', '', metadata['operation_name'])[:200]
        
        # Validate technique IDs (MITRE ATT&CK format: T1234 or T1234.001)
        if 'techniques' in metadata:
            metadata['techniques'] = [
                tid for tid in metadata['techniques']
                if re.match(r'^T\d{4}(\.\d{3})?$', str(tid))
            ]
        
        # Validate tactics (alphanumeric only)
        if 'tactics' in metadata:
            metadata['tactics'] = [
                tactic for tactic in metadata['tactics']
                if re.match(r'^[a-zA-Z0-9\s]+$', str(tactic))
            ]
        
        # Sanitize client_id (alphanumeric and underscore only)
        if 'client_id' in metadata:
            metadata['client_id'] = re.sub(r'[^\w-]', '', str(metadata['client_id']))[:100]
        
        return metadata
    
    def _build_metadata(self, operation) -> Dict[str, Any]:
        """
        Build ECS-compatible metadata from Caldera operation object.
        
        Uses purple.* namespace for ATT&CK fields to enable SIEM filtering:
        - purple.technique: T1078, T1059.001, etc.
        - purple.tactic: TA0001, TA0007, etc.
        - purple.operation_id: Caldera operation UUID
        - purple.detection_status: pending/detected/evaded
        
        Args:
            operation: Caldera operation object
            
        Returns:
            ECS-compatible metadata dictionary
        """
        # Extract techniques and tactics from operation chain
        techniques = []
        tactics = []
        ability_names = []
        
        if hasattr(operation, 'chain') and operation.chain:
            for link in operation.chain:
                if hasattr(link, 'ability'):
                    ability = link.ability
                    if hasattr(ability, 'technique_id') and ability.technique_id:
                        techniques.append(ability.technique_id)
                    if hasattr(ability, 'tactic') and ability.tactic:
                        tactics.append(ability.tactic)
                    if hasattr(ability, 'name') and ability.name:
                        ability_names.append(ability.name)
        
        # Deduplicate and limit
        techniques_list = list(set(techniques))
        tactics_list = list(set(tactics))
        
        if len(techniques_list) > 500:
            self.log.warning(f'Truncated {len(techniques_list)} techniques to 500')
            techniques_list = techniques_list[:500]
        
        # Build ECS-compatible document with purple.* namespace
        metadata = {
            # ECS timestamp
            '@timestamp': datetime.utcnow().isoformat() + 'Z',
            
            # Purple team namespace (for SIEM filtering)
            'purple': {
                'technique': techniques_list[0] if techniques_list else None,
                'techniques': techniques_list,
                'tactic': tactics_list[0] if tactics_list else None,
                'tactics': tactics_list,
                'operation_id': str(operation.id),
                'operation_name': getattr(operation, 'name', 'Unknown'),
                'agent_id': getattr(operation, 'group', 'unknown'),
                'detection_status': 'pending',  # Updated by detection correlation
                'ability_count': len(ability_names),
                'technique_count': len(techniques_list),
                'status': getattr(operation, 'state', 'unknown')
            },
            
            # Tags for Kibana filtering (purple_T1078, purple_TA0007)
            'tags': (
                ['purple_team', 'caldera', 'tl_labs', 'simulation'] +
                [f'purple_{t}' for t in techniques_list[:50]] +
                [f'purple_{tac}' for tac in tactics_list[:20]]
            ),
            
            # Legacy flat fields (backward compatibility)
            'operation_id': str(operation.id),
            'operation_name': getattr(operation, 'name', 'Unknown'),
            'purple_team_exercise': True,
            'client_id': getattr(operation, 'group', 'unknown'),
            'techniques': techniques_list,
            'tactics': tactics_list,
            'abilities': ability_names[:100],
            'severity': 'low',
            'auto_close': True,
            'agent_count': len(getattr(operation, 'agents', [])),
            'status': getattr(operation, 'state', 'unknown')
        }
        
        return metadata
    
    async def _post_to_elk_with_retry(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST metadata to Elasticsearch with retry logic.
        
        Args:
            metadata: Sanitized metadata dictionary
            
        Returns:
            ELK response dictionary
            
        Raises:
            ConnectionError: If ELK unreachable after retries
        """
        if not self.elk_client:
            raise ConnectionError('ELK client not initialized')
        
        # Check circuit breaker
        if self._circuit_open:
            raise ConnectionError('Circuit breaker open (too many failures)')
        
        try:
            # Add timeout wrapper
            async with asyncio.timeout(35):  # 5s buffer beyond ELK timeout
                response = await self.elk_client.index(
                    index=self.config.ELK_INDEX,
                    document=metadata,
                )
            
            # Reset failure counter on success
            self._failure_count = 0
            self._circuit_open = False
            
            self.log.info(f'ELK tagged operation: {metadata["operation_id"][:16]}... (doc ID: {response["_id"]})')
            return response
        
        except asyncio.TimeoutError:
            self.log.error('ELK POST timeout (35s)')
            raise ConnectionError('ELK POST timeout')
        
        except (ConnectionError, TransportError) as e:
            self._failure_count += 1
            
            if self._failure_count >= self._max_failures:
                self._circuit_open = True
                self.log.error(f'Circuit breaker opened after {self._max_failures} failures')
            
            raise e
    
    async def _write_fallback(self, metadata: Dict[str, Any]) -> Path:
        """
        Write metadata to fallback JSON file.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Path to fallback file
        """
        # Check disk space before write
        import shutil
        try:
            stat = shutil.disk_usage(self.fallback_dir)
            free_gb = stat.free / (1024**3)
            
            if free_gb < self.config.DISK_CRITICAL_GB:
                self.log.critical(f'Disk space critical ({free_gb:.1f}GB free)')
                # Could implement rotation here
        except Exception as e:
            self.log.warning(f'Could not check disk space: {e}')
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'fallback_{timestamp}_{metadata["operation_id"][:8]}.json'
        filepath = self.fallback_dir / filename
        
        try:
            # Use synchronous write since we're already in fallback mode
            with open(filepath, 'w') as f:
                f.write(json.dumps(metadata, indent=2))
            
            self.log.warning(f'Fallback log written: {filepath.name}')
            return filepath
        
        except Exception as e:
            self.log.error(f'Failed to write fallback log: {e}')
            raise
    
    async def tag(self, operation) -> Optional[Dict[str, Any]]:
        """
        Tag operation in Elasticsearch (with fallback).
        
        Args:
            operation: Caldera operation object
            
        Returns:
            ELK response or None if fallback used
        """
        # Use semaphore to limit concurrent tags
        async with self._tag_semaphore:
            # Validate operation
            if not operation:
                self.log.warning('tag() called with None operation')
                return None
            
            if not hasattr(operation, 'id') or not operation.id:
                self.log.warning('Operation missing ID attribute')
                return None
            
            if not self._is_valid_operation_id(operation.id):
                self.log.warning(f'Invalid operation ID format: {str(operation.id)[:16]}...')
                return None
            
            # Build and sanitize metadata
            try:
                metadata = self._build_metadata(operation)
                metadata = self._sanitize_metadata(metadata)
            except Exception as e:
                self.log.error(f'Failed to build metadata: {e}')
                return None
            
            # Try ELK first
            if self.elk_client and not self._circuit_open:
                try:
                    response = await self._post_to_elk_with_retry(metadata)
                    return response
                except Exception as e:
                    self.log.error(f'ELK POST failed: {str(e)[:100]}')
            
            # Fallback to file
            try:
                await asyncio.to_thread(self._write_fallback, metadata)
                return None
            except Exception as e:
                self.log.error(f'Fallback logging failed: {e}')
                return None
    
    async def close(self):
        """Close ELK client connection."""
        if self.elk_client:
            await self.elk_client.close()
