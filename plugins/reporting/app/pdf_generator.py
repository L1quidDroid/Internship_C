"""
PDF report generator for purple team operations.

Generates professional PDF reports with Triskele Labs branding,
executive summaries, technique coverage, and tactic analysis.
Optimized for low memory usage and async execution.
"""

import asyncio
import gc
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from plugins.reporting.app.config import ReportingConfig


logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    PDF report generator for Caldera operations.
    
    Features:
    - Memory-optimized rendering (<100MB overhead)
    - ThreadPoolExecutor for CPU-bound PDF generation
    - Timeout protection via asyncio.wait_for
    - Graceful degradation on errors
    """
    
    # MITRE ATT&CK tactic ordering
    TACTIC_ORDER = [
        'reconnaissance', 'resource-development', 'initial-access',
        'execution', 'persistence', 'privilege-escalation',
        'defense-evasion', 'credential-access', 'discovery',
        'lateral-movement', 'collection', 'command-and-control',
        'exfiltration', 'impact'
    ]
    
    def __init__(self, config: ReportingConfig):
        """
        Initialize PDF generator.
        
        Args:
            config: ReportingConfig instance
        """
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Setup custom paragraph styles for Triskele branding."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='TLTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(self.config.primary_color),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='TLSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor(self.config.accent_color),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='TLBody',
            parent=self.styles['BodyText'],
            fontSize=self.config.font_size,
            textColor=colors.HexColor(self.config.text_color),
            spaceAfter=12
        ))
    
    def _build_header(self, operation) -> list:
        """
        Build report header with logo and title.
        
        Args:
            operation: Caldera operation object
            
        Returns:
            List of Platypus flowables
        """
        elements = []
        
        # Add logo if exists
        if self.config.logo_path.exists():
            try:
                logo = Image(str(self.config.logo_path), width=120, height=40)
                elements.append(logo)
                elements.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        # Title
        title = Paragraph(
            f"Purple Team Exercise Report<br/>{operation.name}",
            self.styles['TLTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_metadata_table(self, operation) -> Table:
        """
        Build operation metadata table.
        
        Args:
            operation: Caldera operation object
            
        Returns:
            ReportLab Table object
        """
        duration = 'N/A'
        if operation.start and operation.finish:
            start = datetime.fromisoformat(str(operation.start))
            finish = datetime.fromisoformat(str(operation.finish))
            duration_delta = finish - start
            duration = str(duration_delta).split('.')[0]  # Remove microseconds
        
        data = [
            ['Operation ID:', operation.id],
            ['Group:', operation.group],
            ['State:', operation.state],
            ['Start Time:', str(operation.start)[:19] if operation.start else 'N/A'],
            ['End Time:', str(operation.finish)[:19] if operation.finish else 'N/A'],
            ['Duration:', duration],
            ['Adversary:', getattr(operation.adversary, 'name', 'N/A')],
            ['Planner:', getattr(operation.planner, 'name', 'N/A')],
            ['Jitter:', getattr(operation, 'jitter', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(self.config.primary_color)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        return table
    
    def _build_executive_summary(self, operation) -> list:
        """
        Build executive summary section.
        
        Args:
            operation: Caldera operation object
            
        Returns:
            List of flowables
        """
        elements = []
        
        # Section title
        elements.append(Paragraph("Executive Summary", self.styles['TLSubtitle']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Calculate statistics
        total_techniques = len(operation.chain) if operation.chain else 0
        
        # Avoid division by zero
        if total_techniques == 0:
            success_rate = 0
            failure_rate = 0
            timeout_rate = 0
        else:
            successful = sum(1 for link in operation.chain if link.status == 0)
            failed = sum(1 for link in operation.chain if link.status == 1)
            timeout = sum(1 for link in operation.chain if link.status == -2)
            
            success_rate = (successful / total_techniques) * 100
            failure_rate = (failed / total_techniques) * 100
            timeout_rate = (timeout / total_techniques) * 100
        
        # Summary text
        summary_text = f"""
        This purple team exercise executed <b>{total_techniques}</b> techniques 
        against the <b>{operation.group}</b> environment. The operation achieved 
        a <b>{success_rate:.1f}%</b> success rate, with <b>{failure_rate:.1f}%</b> 
        failures and <b>{timeout_rate:.1f}%</b> timeouts.
        """
        
        elements.append(Paragraph(summary_text, self.styles['TLBody']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Techniques', str(total_techniques)],
            ['Successful', f"{success_rate:.1f}%"],
            ['Failed', f"{failure_rate:.1f}%"],
            ['Timed Out', f"{timeout_rate:.1f}%"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5 * inch, 1.5 * inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.accent_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_technique_table(self, operation) -> list:
        """
        Build detailed technique execution table.
        
        Args:
            operation: Caldera operation object
            
        Returns:
            List of flowables
        """
        elements = []
        
        elements.append(Paragraph("Technique Details", self.styles['TLSubtitle']))
        elements.append(Spacer(1, 0.1 * inch))
        
        if not operation.chain:
            elements.append(Paragraph("No techniques executed.", self.styles['TLBody']))
            return elements
        
        # Build table data
        data = [['ID', 'Name', 'Tactic', 'Status']]
        
        for link in operation.chain:
            technique_id = getattr(link.ability, 'technique_id', 'N/A')
            technique_name = getattr(link.ability, 'technique_name', 
                                    getattr(link.ability, 'name', 'N/A'))
            tactic = getattr(link.ability, 'tactic', 'N/A')
            
            # Status mapping
            status_map = {
                0: '✓ Success',
                1: '✗ Failed',
                -2: '⏱ Timeout'
            }
            status = status_map.get(link.status, 'Unknown')
            
            data.append([technique_id, technique_name[:30], tactic, status])
        
        # Create table
        table = Table(data, colWidths=[1 * inch, 2.5 * inch, 1.5 * inch, 1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.accent_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_tactic_coverage(self, operation) -> list:
        """
        Build MITRE ATT&CK tactic coverage analysis.
        
        Args:
            operation: Caldera operation object
            
        Returns:
            List of flowables
        """
        elements = []
        
        elements.append(Paragraph("Tactic Coverage", self.styles['TLSubtitle']))
        elements.append(Spacer(1, 0.1 * inch))
        
        if not operation.chain:
            elements.append(Paragraph("No tactics covered.", self.styles['TLBody']))
            return elements
        
        # Count tactics
        tactic_counter = Counter()
        for link in operation.chain:
            tactic = getattr(link.ability, 'tactic', None)
            if tactic:
                tactic_counter[tactic] += 1
        
        # Build table ordered by MITRE ATT&CK kill chain
        data = [['Tactic', 'Count', 'Percentage']]
        
        total = sum(tactic_counter.values())
        if total == 0:
            total = 1  # Avoid division by zero
        
        for tactic in self.TACTIC_ORDER:
            count = tactic_counter.get(tactic, 0)
            if count > 0:
                percentage = (count / total) * 100
                data.append([tactic.title(), str(count), f"{percentage:.1f}%"])
        
        # Add any tactics not in standard order
        for tactic, count in tactic_counter.items():
            if tactic not in self.TACTIC_ORDER:
                percentage = (count / total) * 100
                data.append([tactic.title(), str(count), f"{percentage:.1f}%"])
        
        table = Table(data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.accent_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_detection_summary(self, detection_data: dict) -> list:
        """
        Build SIEM detection coverage summary section.
        
        Shows correlation between executed techniques and SIEM detections
        from purple-team-logs-* Elasticsearch index.
        
        Args:
            detection_data: Dict from ELKFetcher.get_detection_data()
            
        Returns:
            List of flowables
        """
        elements = []
        
        elements.append(Paragraph("Detection Coverage", self.styles['TLSubtitle']))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Check if data available
        if not detection_data.get('available', False):
            reason = detection_data.get('reason', 'ELK data unavailable')
            elements.append(Paragraph(
                f"<i>Detection correlation unavailable: {reason}</i>",
                self.styles['TLBody']
            ))
            elements.append(Spacer(1, 0.2 * inch))
            return elements
        
        summary = detection_data.get('summary', {})
        techniques = detection_data.get('techniques', {})
        
        # Summary statistics
        detected = summary.get('detected', 0)
        evaded = summary.get('evaded', 0)
        pending = summary.get('pending', 0)
        coverage = summary.get('coverage_percent', 0.0)
        
        # Summary text
        total_techniques = len(techniques)
        summary_text = f"""
        Detection correlation analyzed <b>{total_techniques}</b> techniques from 
        Elasticsearch purple-team-logs. Current detection coverage: <b>{coverage:.1f}%</b>.
        """
        elements.append(Paragraph(summary_text, self.styles['TLBody']))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Detection summary table
        summary_data = [
            ['Detection Status', 'Count', 'Percentage'],
            ['✓ Detected', str(detected), f"{(detected / max(total_techniques, 1)) * 100:.1f}%"],
            ['✗ Evaded', str(evaded), f"{(evaded / max(total_techniques, 1)) * 100:.1f}%"],
            ['⏳ Pending', str(pending), f"{(pending / max(total_techniques, 1)) * 100:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2 * inch, 1 * inch, 1.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),  # Dark header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            # Color-code rows based on status
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#d5f5e3')),  # Green for detected
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fadbd8')),  # Red for evaded
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fef9e7')),  # Yellow for pending
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Per-technique detection status (if we have technique-level data)
        if techniques:
            elements.append(Paragraph("Technique Detection Status", self.styles['TLSubtitle']))
            elements.append(Spacer(1, 0.1 * inch))
            
            tech_data = [['Technique ID', 'Detection Status', 'Event Count']]
            
            # Sort by status (detected first, then evaded, then pending)
            status_order = {'detected': 0, 'evaded': 1, 'pending': 2}
            sorted_techniques = sorted(
                techniques.items(),
                key=lambda x: (status_order.get(x[1].get('status', 'pending'), 3), x[0])
            )
            
            for tech_id, tech_info in sorted_techniques[:30]:  # Limit to 30 techniques
                status = tech_info.get('status', 'pending')
                count = tech_info.get('count', 0)
                
                # Status display with emoji
                status_display = {
                    'detected': '✓ Detected',
                    'evaded': '✗ Evaded',
                    'pending': '⏳ Pending'
                }.get(status, status)
                
                tech_data.append([tech_id, status_display, str(count)])
            
            if len(techniques) > 30:
                tech_data.append(['...', f'+{len(techniques) - 30} more', ''])
            
            tech_table = Table(tech_data, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.accent_color)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(tech_table)
        
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _generate_pdf_sync(self, operation, filename: str, detection_data: Optional[dict] = None) -> Path:
        """
        Synchronous PDF generation (runs in ThreadPoolExecutor).
        
        Args:
            operation: Caldera operation object
            filename: Output filename
            detection_data: Optional ELK detection correlation data
            
        Returns:
            Path to generated PDF
        """
        output_path = self.config.output_dir / filename
        
        # Default empty detection data if not provided
        if detection_data is None:
            detection_data = {'available': False, 'reason': 'Not fetched'}
        
        # Choose page size
        page_sizes = {
            'LETTER': letter,
            'A4': A4,
            'LEGAL': legal
        }
        page_size = page_sizes.get(self.config.page_size, letter)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=page_size,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )
        
        # Build content
        elements = []
        
        # Header
        elements.extend(self._build_header(operation))
        
        # Metadata table
        elements.append(self._build_metadata_table(operation))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Executive summary
        if self.config.include_executive_summary:
            elements.extend(self._build_executive_summary(operation))
        
        # Tactic coverage
        if self.config.include_tactic_coverage:
            elements.extend(self._build_tactic_coverage(operation))
        
        # Detection coverage (from ELK correlation)
        elements.extend(self._build_detection_summary(detection_data))
        
        # Technique details
        if self.config.include_technique_details:
            elements.extend(self._build_technique_table(operation))
        
        # Footer
        elements.append(Spacer(1, 0.5 * inch))
        footer_text = f"Generated by {self.config.company_name} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(footer_text, self.styles['TLBody']))
        
        # Build PDF
        doc.build(elements)
        
        # Force garbage collection to free memory
        gc.collect()
        
        logger.info(f"PDF generated successfully: {output_path}")
        return output_path
    
    async def generate(self, operation, detection_data: Optional[dict] = None) -> Optional[Path]:
        """
        Generate PDF report asynchronously with timeout protection.
        
        Args:
            operation: Caldera operation object
            detection_data: Optional ELK detection correlation data
            
        Returns:
            Path to generated PDF or None on error
            
        Raises:
            asyncio.TimeoutError: If generation exceeds timeout
            ValueError: If operation is invalid
        """
        # Validate operation
        if not operation:
            raise ValueError("Operation cannot be None")
        
        if not hasattr(operation, 'id'):
            raise ValueError("Operation must have 'id' attribute")
        
        if operation.state != 'finished':
            logger.warning(f"Operation {operation.id} not finished (state: {operation.state})")
            return None
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{operation.id}_{timestamp}.pdf"
        
        try:
            # Run CPU-bound PDF generation in thread pool with timeout
            loop = asyncio.get_event_loop()
            pdf_path = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self._generate_pdf_sync,
                    operation,
                    filename,
                    detection_data
                ),
                timeout=self.config.generation_timeout
            )
            
            return pdf_path
            
        except asyncio.TimeoutError:
            logger.error(f"PDF generation timed out after {self.config.generation_timeout}s for operation {operation.id}")
            raise
        
        except Exception as e:
            logger.exception(f"PDF generation failed for operation {operation.id}: {e}")
            return None
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the PDF generator."""
        logger.info("Shutting down PDF generator...")
        self.executor.shutdown(wait=True)
        gc.collect()
        logger.info("PDF generator shutdown complete")
