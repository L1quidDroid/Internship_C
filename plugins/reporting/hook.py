"""
Reporting plugin hook for MITRE Caldera.

Registers the reporting service and subscribes to operation events
for automatic PDF report generation.
"""

import logging

from plugins.reporting.app.report_svc import ReportingService


name = 'Reporting'
description = 'Automated PDF report generation for purple team exercises'
address = '/plugin/reporting/gui'
access = None


logger = logging.getLogger(__name__)


async def enable(services: dict):
    """
    Enable the reporting plugin.
    
    Initializes the reporting service and subscribes to operation
    completion events for automatic report generation.
    
    Args:
        services: Dictionary of Caldera services
    """
    try:
        # Initialize reporting service
        report_svc = ReportingService(services)
        
        # Register service with Caldera
        services['report_svc'] = report_svc
        
        # Subscribe to operation completion events
        event_svc = services.get('event_svc')
        
        if event_svc:
            # Subscribe to 'operation' exchange, 'completed' queue
            await event_svc.observe_event(
                callback=report_svc.on_operation_completed,
                exchange='operation',
                queue='completed'
            )
            
            logger.info("Reporting plugin subscribed to operation.completed events")
        else:
            logger.warning("Event service not available, automatic reporting disabled")
        
        # Register REST API endpoints
        app_svc = services.get('app_svc')
        
        if app_svc:
            app_svc.application.router.add_route(
                'POST',
                '/api/v2/reports/generate',
                handle_generate_report(report_svc)
            )
            
            app_svc.application.router.add_route(
                'GET',
                '/api/v2/reports/list',
                handle_list_reports(report_svc)
            )
            
            logger.info("Reporting plugin REST API endpoints registered")
        
        logger.info("Reporting plugin enabled successfully")
    
    except Exception as e:
        logger.exception(f"Failed to enable reporting plugin: {e}")
        raise


def handle_generate_report(report_svc: ReportingService):
    """
    Create REST API handler for manual report generation.
    
    Args:
        report_svc: ReportingService instance
        
    Returns:
        Async request handler function
    """
    async def handler(request):
        """Handle POST /api/v2/reports/generate"""
        try:
            data = await request.json()
            operation_id = data.get('operation_id')
            
            if not operation_id:
                return web.json_response(
                    {'error': 'operation_id required'},
                    status=400
                )
            
            pdf_path = await report_svc.generate_report_manual(operation_id)
            
            if pdf_path:
                return web.json_response({
                    'status': 'success',
                    'operation_id': operation_id,
                    'report_path': str(pdf_path)
                })
            else:
                return web.json_response(
                    {'error': 'Report generation failed'},
                    status=500
                )
        
        except Exception as e:
            logger.exception(f"Error in generate_report handler: {e}")
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    return handler


def handle_list_reports(report_svc: ReportingService):
    """
    Create REST API handler for listing reports.
    
    Args:
        report_svc: ReportingService instance
        
    Returns:
        Async request handler function
    """
    async def handler(request):
        """Handle GET /api/v2/reports/list"""
        try:
            reports = await report_svc.list_reports()
            
            return web.json_response({
                'status': 'success',
                'count': len(reports),
                'reports': reports
            })
        
        except Exception as e:
            logger.exception(f"Error in list_reports handler: {e}")
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    return handler


# Import aiohttp web for REST API handlers
try:
    from aiohttp import web
except ImportError:
    logger.warning("aiohttp not available, REST API handlers disabled")
    web = None
