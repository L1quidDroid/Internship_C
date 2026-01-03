"""
Orchestrator plugin event registration.

Registers with Caldera plugin system and subscribes to operation events via event_svc.
"""

name = 'Orchestrator'
description = 'TL Labs Purple Team Automation - Attack Tagging & Orchestration'
address = None  # No GUI endpoint (backend service only)


async def enable(services):
    """
    Enable orchestrator plugin.
    
    Called by Caldera when plugin loads.
    
    Args:
        services: Caldera service registry
    """
    from plugins.orchestrator.app.orchestrator_svc import OrchestratorService
    from plugins.orchestrator.app.config import OrchestratorConfig
    from app.utility.base_service import BaseService
    
    log = BaseService.create_logger('orchestrator')
    
    try:
        # Validate configuration
        OrchestratorConfig.validate()
        log.info('Orchestrator configuration validated')
        
        # Initialize service
        orchestrator_svc = OrchestratorService(services)
        services['orchestrator_svc'] = orchestrator_svc
        
        # Subscribe to operation events via event_svc
        event_svc = services.get('event_svc')
        
        if event_svc:
            await event_svc.observe_event(
                callback=orchestrator_svc.on_operation_state_changed,
                exchange='operation',
                queue='state_changed'
            )
            
            await event_svc.observe_event(
                callback=orchestrator_svc.on_operation_completed,
                exchange='operation',
                queue='completed'
            )
            
            log.info('✅ Orchestrator plugin enabled successfully')
            log.info(f'   ELK URL: {OrchestratorConfig.ELK_URL}')
            log.info(f'   ELK Index: {OrchestratorConfig.ELK_INDEX}')
        else:
            log.warning('event_svc not available, event subscriptions skipped')
        
    except Exception as e:
        log.error(f'❌ Orchestrator plugin failed to load: {e}')
        raise


async def disable(services):
    """
    Disable orchestrator plugin.
    
    Called by Caldera when plugin unloads.
    
    Args:
        services: Caldera service registry
    """
    from app.utility.base_service import BaseService
    
    orchestrator_svc = services.get('orchestrator_svc')
    
    if orchestrator_svc:
        await orchestrator_svc.shutdown()
        log = BaseService.create_logger('orchestrator')
        log.info('Orchestrator plugin disabled')
