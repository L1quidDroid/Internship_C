"""
Orchestrator service coordinator.

Subscribes to operation events and delegates to specialized services (ELK tagger, health checker).
"""

import json
import logging
from typing import Dict, Any

from plugins.orchestrator.app.elk_tagger import ELKTagger


class OrchestratorService:
    """
    Orchestrator plugin service.
    
    Responsibilities:
    - Subscribe to operation events via event_svc
    - Coordinate ELK tagging
    - Provide health check API (Phase 5)
    """
    
    _services = {}  # Class-level service registry
    
    def __init__(self, services: Dict[str, Any]):
        """
        Initialize orchestrator service.
        
        Args:
            services: Caldera service registry
        """
        # Create logger using standard logging
        self.log = logging.getLogger('orchestrator_svc')
        
        # Store service references
        self.services = services
        self.data_svc = services.get('data_svc')
        
        # Initialize ELK tagger
        self.elk_tagger = ELKTagger(self.log)
        
        self.log.info('OrchestratorService initialized')
    
    async def on_operation_state_changed(self, socket, path, services):
        """
        Event handler: Tag operation when state changes.
        
        Called by Caldera event_svc when operation state changes.
        Subscribed to exchange='operation', queue='state_changed'.
        
        Args:
            socket: Websocket connection object
            path: Websocket path (e.g., '/operation/state_changed')
            services: Caldera service registry
        """
        try:
            # Read and parse JSON message from websocket
            message_data = await socket.recv()
            event_data = json.loads(message_data)
            
            # Extract event parameters
            op_id = event_data.get('op')
            from_state = event_data.get('from_state')
            to_state = event_data.get('to_state')
            
            if not op_id:
                self.log.warning('[orchestrator] State change event missing operation ID')
                return
            
            self.log.info(f'[orchestrator] State change: {op_id[:16]}... ({from_state} → {to_state})')
            
            # Fetch operation object from data_svc using ID
            data_svc = services.get('data_svc')
            if not data_svc:
                self.log.error('[orchestrator] data_svc not available')
                return
            
            operations = await data_svc.locate('operations', match=dict(id=op_id))
            if not operations:
                self.log.warning(f'[orchestrator] Operation not found: {op_id[:16]}...')
                return
            
            operation = operations[0]
            await self.elk_tagger.tag(operation)
            
        except Exception as e:
            # Non-fatal error (don't break operation)
            self.log.error(f'[orchestrator] Operation tagging failed (non-fatal): {e}', exc_info=True)
    
    async def on_operation_completed(self, socket, path, services):
        """
        Event handler: Handle operation completion.
        
        Called by Caldera event_svc when operation completes.
        Subscribed to exchange='operation', queue='completed'.
        
        Args:
            socket: Websocket connection object
            path: Websocket path (e.g., '/operation/completed')
            services: Caldera service registry
        """
        try:
            # Read and parse JSON message from websocket
            message_data = await socket.recv()
            event_data = json.loads(message_data)
            
            # Extract operation ID from event data
            op_id = event_data.get('op')
            
            if not op_id:
                self.log.warning('[orchestrator] Completed event missing operation ID')
                return
            
            # Fetch operation object from data_svc using ID
            data_svc = services.get('data_svc')
            if not data_svc:
                self.log.error('[orchestrator] data_svc not available')
                return
            
            operations = await data_svc.locate('operations', match=dict(id=op_id))
            if not operations:
                self.log.warning(f'[orchestrator] Operation not found: {op_id[:16]}...')
                return
            
            operation = operations[0]
            self.log.info(f'[orchestrator] Operation finished: {op_id[:16]}... (state: {operation.state})')
            
            # Update operation status in ELK (re-tag with final state)
            await self.elk_tagger.tag(operation)
            
            # Note: PDF report generation is handled automatically by the reporting plugin
            # via event subscription (reporting plugin listens to operation.completed events)
            self.log.debug(f'[orchestrator] Operation completion handled. Report generation delegated to reporting plugin event handler.')
            
        except Exception as e:
            self.log.error(f'[orchestrator] Operation finish handling failed: {e}', exc_info=True)
    
    async def shutdown(self):
        """Shutdown orchestrator service and cleanup resources."""
        self.log.info('Shutting down orchestrator service...')
        
        try:
            # Close ELK client
            await self.elk_tagger.close()
            self.log.info('ELK client closed')
        except Exception as e:
            self.log.error(f'Error during shutdown: {e}')
    
    async def status_endpoint(self, request):
        """
        GET /plugin/orchestrator/status - Health check endpoint.
        
        Returns:
            JSON with ELK connectivity, circuit breaker state, config
        """
        from aiohttp import web
        from plugins.orchestrator.app.config import OrchestratorConfig
        
        elk_status = 'unknown'
        elk_error = None
        
        # Test ELK connectivity
        if self.elk_tagger.elk_client:
            try:
                info = await self.elk_tagger.elk_client.info()
                elk_status = 'connected'
            except Exception as e:
                elk_status = 'error'
                elk_error = str(e)[:200]
        else:
            elk_status = 'client_not_initialized'
        
        status = {
            'plugin': 'orchestrator',
            'status': 'running',
            'elk': {
                'status': elk_status,
                'error': elk_error,
                'url': OrchestratorConfig.ELK_URL,
                'index': OrchestratorConfig.ELK_INDEX,
                'circuit_breaker_open': self.elk_tagger._circuit_open,
                'failure_count': self.elk_tagger._failure_count
            },
            'fallback_dir': str(OrchestratorConfig.FALLBACK_LOG_DIR)
        }
        
        return web.json_response(status)
    
    async def tag_test_endpoint(self, request):
        """
        POST /plugin/orchestrator/tag-test - Manual tagging test.
        
        Creates mock operation data and sends to ELK for testing.
        
        Returns:
            JSON with tagging result
        """
        from aiohttp import web
        from datetime import datetime
        import uuid
        
        # Create mock operation-like object for testing
        class MockOperation:
            def __init__(self):
                self.id = str(uuid.uuid4())
                self.name = 'orchestrator-tag-test'
                self.state = 'finished'
                self.group = 'test-client'
                self.chain = []
                self.agents = []
        
        mock_op = MockOperation()
        
        try:
            result = await self.elk_tagger.tag(mock_op)
            
            if result:
                return web.json_response({
                    'status': 'success',
                    'message': 'Tag sent to ELK',
                    'operation_id': mock_op.id,
                    'elk_doc_id': result.get('_id'),
                    'index': result.get('_index')
                })
            else:
                return web.json_response({
                    'status': 'fallback',
                    'message': 'ELK unavailable, written to fallback log',
                    'operation_id': mock_op.id,
                    'fallback_dir': str(self.elk_tagger.fallback_dir)
                })
                
        except Exception as e:
            self.log.error(f'Tag test failed: {e}', exc_info=True)
            return web.json_response({
                'status': 'error',
                'message': str(e)[:500],
                'operation_id': mock_op.id
            }, status=500)
