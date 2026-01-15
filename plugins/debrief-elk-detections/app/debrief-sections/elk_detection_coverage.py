"""
ELK Detection Coverage Section for Caldera Debrief.

Queries purple-team-logs-* index for detection validation and generates
a comprehensive detection coverage table showing which techniques were
detected, evaded, or pending analysis.
"""

import logging
from html import escape
from collections import defaultdict
from typing import List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import KeepTogether

from app.utility.base_world import BaseWorld
from plugins.debrief.app.utility.base_report_section import BaseReportSection

# Import elk_fetcher from parent app directory
import sys
import os
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
import elk_fetcher


class DebriefReportSection(BaseReportSection):
    """
    ELK Detection Coverage section for debrief reports.
    
    Displays detection correlation from purple-team-logs-* index:
    - Per-technique detection status (detected/evaded/pending)
    - Alert counts and rule names
    - Overall detection coverage percentage
    """
    
    def __init__(self):
        super().__init__()
        self.id = 'elk-detection-coverage'
        self.display_name = 'ELK Detection Coverage'
        self.description = (
            'Detection correlation from SIEM showing which techniques were detected, '
            'evaded, or are pending analysis. Queries purple-team-logs-* Elasticsearch index.'
        )
        self.log = logging.getLogger('debrief.elk_detection_coverage')
        
        # Load plugin configuration
        self.config = BaseWorld.get_config(prop='debrief_elk_detections', name='main') or {}
        
        # Table styling
        self.cell_style = ParagraphStyle(
            name='DetectionCell',
            parent=None,
            fontName='Helvetica',
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            wordWrap='CJK',
        )
        
        self.header_style = ParagraphStyle(
            name='DetectionHeader',
            parent=None,
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
        )
    
    async def generate_section_elements(self, styles, operations, agents, graph_files):
        """
        Generate PDF flowables for ELK detection correlation section.
        
        Args:
            styles: ReportLab StyleSheet
            operations: List of Caldera Operation objects
            agents: Runtime agents (unused)
            graph_files: SVG graphs (unused)
        
        Returns:
            List of ReportLab Flowable objects
        """
        flowables = []
        
        # Section title and description
        section_title = self.config.get('section_title', 'ELK Detection Coverage Analysis')
        flowables.append(Paragraph(section_title, styles['Heading2']))
        flowables.append(Paragraph(self.description, styles['Normal']))
        flowables.append(Spacer(1, 12))
        
        # Fetch detection data from ELK
        op_ids = [str(op.id) for op in operations]
        
        try:
            detection_result = await elk_fetcher.fetch_detection_data_for_operations(op_ids, self.config, self.log)
        except Exception as e:
            self.log.error(f'ELK fetch failed: {e}', exc_info=True)
            flowables.append(Paragraph(
                f'<i>Detection correlation unavailable: {str(e)[:100]}</i>',
                styles['Normal']
            ))
            return flowables
        
        if not detection_result.get('available'):
            reason = detection_result.get('reason', 'Unknown error')
            flowables.append(Paragraph(
                f'<i>Detection correlation unavailable: {reason}</i>',
                styles['Normal']
            ))
            return flowables
        
        # Build detection table from operation chains
        table_data = self._build_detection_table(operations, detection_result.get('techniques', {}))
        
        if not table_data:
            flowables.append(Paragraph(
                '<i>No techniques executed in selected operations</i>',
                styles['Normal']
            ))
            return flowables
        
        # Add table header
        header = [
            Paragraph('<b>Technique</b>', self.header_style),
            Paragraph('<b>Name</b>', self.header_style),
            Paragraph('<b>Status</b>', self.header_style),
            Paragraph('<b>Rule Triggered</b>', self.header_style),
            Paragraph('<b>Alert Count</b>', self.header_style),
        ]
        table_data.insert(0, header)
        
        # Create table with optimized column widths
        col_widths = [0.9*inch, 2.5*inch, 1.0*inch, 2.2*inch, 0.9*inch]
        detection_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        detection_table.setStyle(self._get_table_style())
        
        flowables.append(detection_table)
        flowables.append(Spacer(1, 12))
        
        # Add summary statistics
        stats = self._calculate_stats(detection_result.get('techniques', {}))
        summary_text = self._build_summary_text(stats, detection_result.get('total_events', 0))
        flowables.append(Paragraph(summary_text, styles['Normal']))
        
        return flowables
    
    def _build_detection_table(self, operations, detection_data):
        """
        Extract technique execution + ELK correlation into table rows.
        
        Args:
            operations: List of Caldera Operation objects
            detection_data: Dict mapping technique_id -> detection info
        
        Returns:
            List of table rows (each row is a list of Paragraph objects)
        """
        rows = []
        seen_techniques = set()
        
        for op in operations:
            for link in getattr(op, 'chain', []):
                ability = getattr(link, 'ability', None)
                if not ability:
                    continue
                
                technique_id = getattr(ability, 'technique_id', None)
                technique_name = getattr(ability, 'technique_name', getattr(ability, 'name', 'Unknown'))
                
                if not technique_id or technique_id in seen_techniques:
                    continue
                
                seen_techniques.add(technique_id)
                
                # Lookup ELK detection match
                detection = detection_data.get(technique_id, {})
                status = detection.get('status', 'pending')
                rule_name = detection.get('rule_name', 'N/A')
                alert_count = detection.get('alert_count', 0)
                
                # Sanitize data to prevent PDF injection
                safe_technique_id = escape(str(technique_id))
                safe_technique_name = escape(str(technique_name))
                safe_rule_name = escape(str(rule_name))
                
                # Build row with styled cells
                rows.append([
                    Paragraph(safe_technique_id, self.cell_style),
                    Paragraph(safe_technique_name, self.cell_style),
                    self._status_cell(status),
                    Paragraph(safe_rule_name, self.cell_style),
                    Paragraph(str(alert_count), self.cell_style),
                ])
        
        return rows
    
    def _status_cell(self, status: str):
        """
        Create color-coded status cell.
        
        Args:
            status: Detection status (detected/evaded/pending)
        
        Returns:
            Paragraph with colored status text
        """
        color_config = self.config.get('colors', {})
        
        status_map = {
            'detected': {
                'text': '✓ Detected',
                'color': color_config.get('detected', '#28a745')
            },
            'evaded': {
                'text': '✗ Evaded',
                'color': color_config.get('evaded', '#dc3545')
            },
            'pending': {
                'text': '⧗ Pending',
                'color': color_config.get('pending', '#ffc107')
            }
        }
        
        info = status_map.get(status.lower(), {'text': status, 'color': '#6c757d'})
        styled_text = f'<font color="{info["color"]}" size="9"><b>{info["text"]}</b></font>'
        
        return Paragraph(styled_text, self.cell_style)
    
    def _get_table_style(self):
        """Define table styling for detection coverage table."""
        return TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Alert count column centered
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ])
    
    def _calculate_stats(self, detection_data):
        """
        Calculate summary statistics for detection coverage.
        
        Args:
            detection_data: Dict mapping technique_id -> detection info
        
        Returns:
            Dict with stats (total, detected, evaded, pending, coverage_pct)
        """
        total = len(detection_data)
        detected = sum(1 for d in detection_data.values() if d.get('status') == 'detected')
        evaded = sum(1 for d in detection_data.values() if d.get('status') == 'evaded')
        pending = total - detected - evaded
        
        coverage_pct = (detected / total * 100) if total > 0 else 0.0
        
        return {
            'total': total,
            'detected': detected,
            'evaded': evaded,
            'pending': pending,
            'coverage_pct': coverage_pct
        }
    
    def _build_summary_text(self, stats, total_events):
        """Build summary paragraph text with detection statistics."""
        return (
            f'<b>Detection Summary:</b> '
            f'{stats["detected"]} of {stats["total"]} techniques detected '
            f'({stats["coverage_pct"]:.1f}% coverage). '
            f'{stats["evaded"]} evaded, {stats["pending"]} pending analysis. '
            f'Total SIEM events correlated: {total_events}.'
        )
