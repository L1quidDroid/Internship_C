"""
Debrief ELK Detection Coverage Plugin Hook.

This plugin adds an 'ELK Detection Coverage' section to Caldera Debrief reports.
Queries purple-team-logs-* index for detection validation and correlation.

No API routes needed—debrief auto-discovers sections in app/debrief-sections/.
"""

import logging
from app.utility.base_world import BaseWorld

name = 'debrief-elk-detections'
description = 'ELK detection correlation section for Caldera Debrief reports'
address = None  # No dedicated UI
access = BaseWorld.Access.RED


async def enable(services):
    """
    Load configuration and enable section discovery by debrief plugin.
    
    The debrief plugin will automatically discover sections in:
    plugins/debrief-elk-detections/app/debrief-sections/*.py
    """
    logger = logging.getLogger('debrief-elk-detections')
    
    try:
        # Load plugin configuration
        config_path = 'plugins/debrief-elk-detections/conf/default.yml'
        config_data = BaseWorld.strip_yml(config_path)
        
        if config_data:
            BaseWorld.apply_config('debrief_elk_detections', config_data[0])
            logger.info('✅ Debrief-ELK-Detections: Configuration loaded from %s', config_path)
        else:
            logger.warning('⚠️ Debrief-ELK-Detections: No configuration found at %s', config_path)
        
        logger.info('✅ Debrief-ELK-Detections: Section ready for discovery by debrief plugin')
        
    except Exception as e:
        logger.error('❌ Failed to load Debrief-ELK-Detections configuration: %s', e, exc_info=True)


async def disable(services):
    """Cleanup on plugin disable."""
    logger = logging.getLogger('debrief-elk-detections')
    logger.info('Debrief-ELK-Detections plugin disabled')
