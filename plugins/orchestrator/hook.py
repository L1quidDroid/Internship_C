"""
Orchestrator plugin event registration.

Registers with Caldera plugin system and subscribes to operation events via event_svc.
Provides debug API endpoints: /plugin/orchestrator/status and /plugin/orchestrator/tag-test
"""

import logging

name = 'Orchestrator'
description = 'TL Labs Purple Team Automation - Attack Tagging & Orchestration'
address = None  # No GUI endpoint (backend service only)


async def enable(services):
    """
    Enable orchestrator plugin.
    
    Called by Caldera when plugin loads.
    Registers event handlers and debug API routes.
    
    Args:
        services: Caldera service registry
    """
    from plugins.orchestrator.app.orchestrator_svc import OrchestratorService
    from plugins.orchestrator.app.config import OrchestratorConfig
    
    log = logging.getLogger('orchestrator')
    
    try:
        # Validate configuration
        OrchestratorConfig.validate()
        log.info('Orchestrator configuration validated')
        
        # Initialize service
        orchestrator_svc = OrchestratorService(services)
        services['orchestrator_svc'] = orchestrator_svc
        
        # Register debug API routes (aiohttp)
        app_svc = services.get('app_svc')
        if app_svc and hasattr(app_svc, 'application'):
            app = app_svc.application
            
            # GET /plugin/orchestrator/status - Health check
            app.router.add_route('GET', '/plugin/orchestrator/status', 
                               orchestrator_svc.status_endpoint)
            
            # POST /plugin/orchestrator/tag-test - Manual tag test
            app.router.add_route('POST', '/plugin/orchestrator/tag-test', 
                               orchestrator_svc.tag_test_endpoint)
            
            # Also support GET for easy browser testing
            app.router.add_route('GET', '/plugin/orchestrator/tag-test', 
                               orchestrator_svc.tag_test_endpoint)
            
            log.info('✅ Orchestrator API routes registered:')
            log.info('   GET  /plugin/orchestrator/status')
            log.info('   POST /plugin/orchestrator/tag-test')
        else:
            log.warning('app_svc not available, API routes not registered')
        
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
            
            await event_svc.observe_event(
                callback=orchestrator_svc.on_link_status_changed,
                exchange='link',
                queue='status_changed'
            )
            
            log.info('✅ Orchestrator event handlers registered:')
            log.info('   operation/state_changed')
            log.info('   operation/completed')
            log.info('   link/status_changed (granular attack tagging)')
        else:
            log.warning('event_svc not available, event subscriptions skipped')
        
        log.info('✅ Orchestrator plugin enabled successfully')
        log.info(f'   ELK URL: {OrchestratorConfig.ELK_URL}')
        log.info(f'   ELK Index: {OrchestratorConfig.ELK_INDEX}')
        
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
    orchestrator_svc = services.get('orchestrator_svc')
    
    if orchestrator_svc:
        await orchestrator_svc.shutdown()
        log = logging.getLogger('orchestrator')
        log.info('Orchestrator plugin disabled')
