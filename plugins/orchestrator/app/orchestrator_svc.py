"""
Orchestrator service coordinator.

Subscribes to operation events and delegates to specialized services (ELK tagger, health checker).
"""

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
    
    def __init__(self, services: Dict[str, Any]):
        """
        Initialize orchestrator service.
        
        Args:
            services: Caldera service registry
        """
        # Create logger using BaseService pattern
        from app.utility.base_service import BaseService
        self.log = BaseService.add_service(self, 'orchestrator_svc', self)
        
        # Store service references
        self.services = services
        self.data_svc = services.get('data_svc')
        
        # Initialize ELK tagger
        self.elk_tagger = ELKTagger(self.log)
        
        self.log.info('OrchestratorService initialized')
    
    async def on_operation_state_changed(self, operation, **kwargs):
        """
        Event handler: Tag operation when state changes.
        
        Called by Caldera event_svc when operation state changes.
        Subscribed to exchange='operation', queue='state_changed'.
        
        Args:
            operation: Caldera operation object
            **kwargs: Event metadata
        """
        try:
            self.log.info(f'Tagging operation: {operation.id[:16]}...')
            await self.elk_tagger.tag(operation)
        except Exception as e:
            # Non-fatal error (don't break operation)
            self.log.error(f'Operation tagging failed (non-fatal): {str(e)[:100]}')
    
    async def on_operation_completed(self, operation, **kwargs):
        """
        Event handler: Handle operation completion.
        
        Called by Caldera event_svc when operation completes.
        Subscribed to exchange='operation', queue='completed'.
        
        Args:
            operation: Caldera operation object
            **kwargs: Event metadata
        """
        try:
            self.log.info(f'Operation finished: {operation.id[:16]}... (state: {operation.state})')
            
            # Update operation status in ELK
            # (Re-tag with final state)
            await self.elk_tagger.tag(operation)
            
            # TODO: Trigger PDF report generation (Feature 2)
            
        except Exception as e:
            self.log.error(f'Operation finish handling failed: {str(e)[:100]}')
    
    async def shutdown(self):
        """Shutdown orchestrator service and cleanup resources."""
        self.log.info('Shutting down orchestrator service...')
        
        try:
            # Close ELK client
            await self.elk_tagger.close()
            self.log.info('ELK client closed')
        except Exception as e:
            self.log.error(f'Error during shutdown: {e}')
