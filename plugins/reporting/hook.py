"""
Caldera plugin registration hook for PDF reporting.

Dependency Safety:
- Gracefully handles missing dependencies (reportlab, pillow, psutil)
- If import fails → plugin disabled, Caldera server continues running
- Logs clear error message with installation instructions

Thread Safety:
- Uses ReportService singleton ThreadPoolExecutor
- No thread leaks on server shutdown
"""

import logging

# Plugin metadata (always defined, even if imports fail)
name = 'Reporting'
description = 'Automated PDF report generation for purple team operations'
address = '/plugin/reporting/gui'
access = None

# Global flag: plugin enabled status
_plugin_enabled = False
_import_error_message = None

# ✅ DEPENDENCY SAFETY: Try imports, disable plugin if missing
try:
    from plugins.reporting.app.report_svc import ReportService
    _plugin_enabled = True
except ImportError as e:
    _import_error_message = str(e)
    _plugin_enabled = False
except Exception as e:
    _import_error_message = f"Unexpected error: {str(e)}"
    _plugin_enabled = False


async def enable(services):
    """
    Called by Caldera when plugin is enabled (server startup).
    
    Graceful Degradation:
        - If dependencies missing → log error, skip registration
        - Caldera server continues running (other plugins unaffected)
        - User sees clear error message with fix instructions
    
    Thread Safety:
        - ReportService uses singleton ThreadPoolExecutor
        - Registered routes use async handlers (non-blocking)
    
    Returns:
        None (modifies services dict in-place)
    """
    logger = services.get('app_svc').get_logger() if services.get('app_svc') else logging.getLogger(__name__)
    
    # Check if plugin dependencies available
    if not _plugin_enabled:
        logger.error(
            f'❌ Reporting plugin DISABLED: Missing dependencies\n'
            f'   Error: {_import_error_message}\n'
            f'   Fix: pip install reportlab pillow psutil\n'
            f'   Then restart Caldera: python server.py --insecure'
        )
        return  # Exit early, don't register routes/events
    
    logger.info('🔧 Initializing Reporting plugin...')
    
    # Extract Caldera services
    app = services.get('app_svc').application
    event_svc = services.get('event_svc')
    
    try:
        # Create service instance (initializes ThreadPoolExecutor)
        report_svc = ReportService(services)
        
        # Register REST API routes
        app.router.add_route(
            'POST',
            '/plugin/reporting/generate',
            report_svc.generate_report_api
        )
        logger.info('✅ Reporting plugin: REST API registered at POST /plugin/reporting/generate')
        
        app.router.add_route(
            'GET',
            '/plugin/reporting/list',
            report_svc.list_reports
        )
        logger.info('✅ Reporting plugin: REST API registered at GET /plugin/reporting/list')
        
        # Subscribe to operation completion events
        if event_svc:
            await event_svc.observe_event(
                callback=report_svc.on_operation_completed,
                exchange='operation',
                queue='completed'
            )
            logger.info('✅ Reporting plugin: Subscribed to operation.completed events')
        else:
            logger.warning('⚠️ event_svc not available—auto-generation disabled')
        
        # Store service reference for cleanup
        services['report_svc'] = report_svc
        
        logger.info('✅ Reporting plugin loaded successfully')
        
    except Exception as e:
        logger.error(f'❌ Failed to initialize Reporting plugin: {e}', exc_info=True)
        # Don't re-raise—allow Caldera to continue starting


async def disable(services):
    """
    Called by Caldera when plugin is disabled (server shutdown).
    
    Thread Safety:
        - Calls report_svc.shutdown() → executor.shutdown(wait=True)
        - Waits for pending reports (max 30s)
        - Prevents thread leaks
    """
    logger = services.get('app_svc').get_logger() if services.get('app_svc') else logging.getLogger(__name__)
    
    if not _plugin_enabled:
        logger.debug('Reporting plugin was not enabled, skipping disable')
        return
    
    logger.info('🔧 Disabling Reporting plugin...')
    
    report_svc = services.get('report_svc')
    
    if report_svc:
        try:
            await report_svc.shutdown()
            logger.info('✅ Reporting plugin disabled successfully')
        except Exception as e:
            logger.error(f'❌ Error during Reporting plugin shutdown: {e}', exc_info=True)
    else:
        logger.warning('report_svc not found in services (may have failed during enable)')
