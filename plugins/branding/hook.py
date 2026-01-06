"""
Triskele Labs Branding Plugin for MITRE Caldera 5.x

This plugin injects custom CSS and JavaScript to rebrand the Caldera UI
with Triskele Labs branding colors, logos, and styling.

Author: Tony To (Internship)
Version: 1.1
Date: January 2025
"""

import os
import logging
from aiohttp import web

# Plugin metadata
name = 'Branding'
description = 'Triskele Labs UI branding and customization'
address = '/branding/static'
access = None  # No access restriction for static files

# Setup logging
logger = logging.getLogger(__name__)


async def enable(services):
    """
    Enable the branding plugin.
    
    Registers static file routes for CSS, JS, and images.
    
    Args:
        services: Dictionary of Caldera core services
    """
    app_svc = services.get('app_svc')
    
    if not app_svc:
        logger.error('app_svc not available, cannot enable branding plugin')
        return
    
    # Get plugin directory
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(plugin_dir, 'static')
    
    # Verify static directory exists
    if not os.path.exists(static_dir):
        logger.error(f'Static directory not found: {static_dir}')
        return
    
    # Register static file routes
    app = app_svc.application
    
    # Add static routes for CSS, JS, and images
    app.router.add_static(
        '/branding/static',
        static_dir,
        name='branding_static',
        show_index=False
    )
    
    logger.info(f'Branding plugin enabled - serving static files from {static_dir}')
    logger.info('Static routes:')
    logger.info('  - CSS: /branding/static/css/triskele.css')
    logger.info('  - JS:  /branding/static/js/branding.js')
    logger.info('  - IMG: /branding/static/img/')
    
    # Add middleware to inject branding into HTML responses
    @web.middleware
    async def branding_middleware(request, handler):
        """Inject branding CSS and JS into HTML responses."""
        # Skip middleware for Magma Vue SPA routes (already has branding in build)
        if request.path == '/' or request.path.startswith('/assets/'):
            return await handler(request)
        
        response = await handler(request)
        
        # Only modify HTML responses
        if (response.content_type == 'text/html' and 
            hasattr(response, 'text')):
            try:
                html = response.text
                
                # Inject CSS before </head>
                css_inject = '''
    <link rel="stylesheet" href="/branding/static/css/triskele.css">
'''
                if '</head>' in html and '/branding/static/css/triskele.css' not in html:
                    html = html.replace('</head>', css_inject + '</head>')
                
                # Inject JS before </body>
                js_inject = '''
    <script src="/branding/static/js/branding.js"></script>
'''
                if '</body>' in html and '/branding/static/js/branding.js' not in html:
                    html = html.replace('</body>', js_inject + '</body>')
                
                # Return modified response
                return web.Response(
                    text=html,
                    content_type='text/html',
                    status=response.status
                )
            except Exception as e:
                logger.warning(f'Failed to inject branding: {e}')
        
        return response
    
    # Register middleware with app for automatic HTML injection
    app.middlewares.append(branding_middleware)
    logger.info('✅ Branding middleware registered and active')
    
    # Log available files
    for subdir in ['css', 'js', 'img']:
        subdir_path = os.path.join(static_dir, subdir)
        if os.path.exists(subdir_path):
            files = os.listdir(subdir_path)
            logger.info(f'  {subdir}/: {files}')
