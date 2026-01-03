"""
Reporting service for automated PDF report generation.

Integrates with Caldera's event system to automatically generate
PDF reports when operations complete.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from app.service.base_service import BaseService
from plugins.reporting.app.config import ReportingConfig
from plugins.reporting.app.pdf_generator import PDFGenerator


logger = logging.getLogger(__name__)


class ReportingService(BaseService):
    """
    Service for automated purple team report generation.
    
    Features:
    - Event-driven report generation on operation completion
    - Async PDF generation with timeout protection
    - Memory-optimized for resource-constrained environments
    - Graceful error handling and fallback mechanisms
    """
    
    def __init__(self, services: dict):
        """
        Initialize reporting service.
        
        Args:
            services: Dictionary of Caldera services
        """
        self.log = self.add_service('report_svc', self)
        
        # Get required services
        self.data_svc = services.get('data_svc')
        self.event_svc = services.get('event_svc')
        
        # Load configuration
        try:
            self.config = ReportingConfig()
            is_valid, errors = self.config.validate()
            
            if not is_valid:
                self.log.error(f"Invalid reporting configuration: {errors}")
                raise ValueError(f"Configuration validation failed: {errors}")
            
            self.log.info(f"Reporting configuration loaded: {self.config}")
            
        except Exception as e:
            self.log.error(f"Failed to load reporting configuration: {e}")
            raise
        
        # Initialize PDF generator
        self.pdf_generator = PDFGenerator(self.config)
        
        # Track active report generations
        self.active_reports = set()
        
        self.log.info("Reporting service initialized successfully")
    
    async def on_operation_completed(self, operation_id: str) -> None:
        """
        Event handler for operation completion.
        
        Automatically generates PDF report when operation finishes.
        
        Args:
            operation_id: ID of completed operation
        """
        if operation_id in self.active_reports:
            self.log.debug(f"Report already being generated for operation {operation_id}")
            return
        
        self.active_reports.add(operation_id)
        
        try:
            # Fetch operation from data service
            operations = await self.data_svc.locate('operations', match=dict(id=operation_id))
            
            if not operations:
                self.log.warning(f"Operation {operation_id} not found")
                return
            
            operation = operations[0]
            
            # Validate operation state
            if operation.state != 'finished':
                self.log.info(f"Operation {operation_id} not finished yet (state: {operation.state})")
                return
            
            self.log.info(f"Generating PDF report for operation {operation_id}...")
            
            # Generate PDF asynchronously
            pdf_path = await self.pdf_generator.generate(operation)
            
            if pdf_path:
                self.log.info(f"PDF report generated successfully: {pdf_path}")
                
                # Optional: Store report metadata in operation
                # operation.report_path = str(pdf_path)
                # await self.data_svc.store(operation)
            else:
                self.log.warning(f"PDF generation returned None for operation {operation_id}")
        
        except asyncio.TimeoutError:
            self.log.error(
                f"PDF generation timed out for operation {operation_id} "
                f"after {self.config.generation_timeout}s"
            )
        
        except Exception as e:
            self.log.exception(f"Failed to generate report for operation {operation_id}: {e}")
        
        finally:
            self.active_reports.discard(operation_id)
    
    async def generate_report_manual(self, operation_id: str) -> Optional[Path]:
        """
        Manually trigger report generation for an operation.
        
        Args:
            operation_id: ID of operation to generate report for
            
        Returns:
            Path to generated PDF or None on error
        """
        try:
            # Fetch operation
            operations = await self.data_svc.locate('operations', match=dict(id=operation_id))
            
            if not operations:
                self.log.error(f"Operation {operation_id} not found")
                return None
            
            operation = operations[0]
            
            # Generate PDF
            self.log.info(f"Manually generating PDF for operation {operation_id}")
            pdf_path = await self.pdf_generator.generate(operation)
            
            if pdf_path:
                self.log.info(f"Manual PDF generation successful: {pdf_path}")
            
            return pdf_path
        
        except Exception as e:
            self.log.exception(f"Manual report generation failed for {operation_id}: {e}")
            return None
    
    async def list_reports(self) -> list[dict]:
        """
        List all generated reports.
        
        Returns:
            List of report metadata dictionaries
        """
        reports = []
        
        try:
            report_dir = self.config.output_dir
            
            if not report_dir.exists():
                return reports
            
            for pdf_file in report_dir.glob('*.pdf'):
                reports.append({
                    'filename': pdf_file.name,
                    'path': str(pdf_file),
                    'size': pdf_file.stat().st_size,
                    'created': pdf_file.stat().st_mtime
                })
            
            # Sort by creation time (newest first)
            reports.sort(key=lambda r: r['created'], reverse=True)
        
        except Exception as e:
            self.log.exception(f"Failed to list reports: {e}")
        
        return reports
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the reporting service."""
        self.log.info("Shutting down reporting service...")
        
        # Wait for active reports to complete (with timeout)
        if self.active_reports:
            self.log.info(f"Waiting for {len(self.active_reports)} active reports to complete...")
            
            try:
                await asyncio.wait_for(
                    self._wait_for_active_reports(),
                    timeout=self.config.generation_timeout * 2
                )
            except asyncio.TimeoutError:
                self.log.warning("Timeout waiting for active reports to complete")
        
        # Shutdown PDF generator
        await self.pdf_generator.shutdown()
        
        self.log.info("Reporting service shutdown complete")
    
    async def _wait_for_active_reports(self) -> None:
        """Wait for all active reports to complete."""
        while self.active_reports:
            await asyncio.sleep(0.5)
