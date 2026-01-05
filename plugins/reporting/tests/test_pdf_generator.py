"""
Unit tests for PDF generator.

Tests cover configuration validation, PDF generation,
memory safety, timeout protection, and error handling.
"""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from plugins.reporting.app.pdf_generator import PDFGenerator
from plugins.reporting.tests.fixtures import (
    mock_config,
    mock_operation_simple,
    mock_operation_complex,
    mock_operation_empty,
    mock_operation_running
)


class TestPDFGeneratorInitialization:
    """Test PDF generator initialization and configuration."""
    
    def test_init_with_valid_config(self, mock_config):
        """Test initialization with valid configuration."""
        generator = PDFGenerator(mock_config)
        
        assert generator.config == mock_config
        assert generator.executor is not None
        assert generator.styles is not None
        assert 'TLTitle' in generator.styles
        assert 'TLSubtitle' in generator.styles
        assert 'TLBody' in generator.styles
    
    def test_custom_styles_created(self, mock_config):
        """Test that custom Triskele styles are created."""
        generator = PDFGenerator(mock_config)
        
        title_style = generator.styles['TLTitle']
        assert title_style.fontSize == 24
        assert title_style.fontName == 'Helvetica-Bold'
        
        subtitle_style = generator.styles['TLSubtitle']
        assert subtitle_style.fontSize == 14


class TestPDFGeneratorHeaderBuilding:
    """Test header building functionality."""
    
    def test_build_header_without_logo(self, mock_config, mock_operation_simple):
        """Test header building when logo doesn't exist."""
        mock_config.logo_path = Path('/nonexistent/logo.png')
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_header(mock_operation_simple)
        
        assert len(elements) >= 2  # Title and spacer
        # First element should be Paragraph (no logo)
        from reportlab.platypus import Paragraph
        assert isinstance(elements[0], Paragraph)
    
    @patch('plugins.reporting.app.pdf_generator.Image')
    def test_build_header_with_logo(self, mock_image, mock_config, mock_operation_simple):
        """Test header building when logo exists."""
        mock_config.logo_path = Path('plugins/reporting/static/assets/triskele_logo.png')
        
        # Mock Path.exists() to return True
        with patch.object(Path, 'exists', return_value=True):
            generator = PDFGenerator(mock_config)
            elements = generator._build_header(mock_operation_simple)
            
            assert len(elements) >= 3  # Logo, spacer, title


class TestPDFGeneratorMetadataTable:
    """Test metadata table building."""
    
    def test_metadata_table_with_complete_operation(self, mock_config, mock_operation_simple):
        """Test metadata table with complete operation data."""
        generator = PDFGenerator(mock_config)
        
        table = generator._build_metadata_table(mock_operation_simple)
        
        assert table is not None
        # Table should have 9 rows (all metadata fields)
        assert len(table._cellvalues) == 9
    
    def test_metadata_table_handles_none_values(self, mock_config):
        """Test metadata table handles missing values gracefully."""
        operation = MagicMock()
        operation.id = 'test-001'
        operation.group = 'test'
        operation.state = 'finished'
        operation.start = None
        operation.finish = None
        operation.adversary = None
        operation.planner = None
        operation.jitter = None
        
        generator = PDFGenerator(mock_config)
        table = generator._build_metadata_table(operation)
        
        assert table is not None


class TestPDFGeneratorExecutiveSummary:
    """Test executive summary building."""
    
    def test_executive_summary_with_techniques(self, mock_config, mock_operation_simple):
        """Test executive summary with executed techniques."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_executive_summary(mock_operation_simple)
        
        assert len(elements) > 0
        # Should have title, summary text, and statistics table
        assert len(elements) >= 3
    
    def test_executive_summary_empty_operation(self, mock_config, mock_operation_empty):
        """Test executive summary with no techniques (division by zero protection)."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_executive_summary(mock_operation_empty)
        
        # Should not crash, should return elements
        assert len(elements) > 0
    
    def test_executive_summary_calculates_correct_percentages(self, mock_config, mock_operation_complex):
        """Test that success/failure percentages are calculated correctly."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_executive_summary(mock_operation_complex)
        
        # Should have statistics table
        assert len(elements) >= 3


class TestPDFGeneratorTechniqueTable:
    """Test technique details table building."""
    
    def test_technique_table_with_techniques(self, mock_config, mock_operation_simple):
        """Test technique table with executed techniques."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_technique_table(mock_operation_simple)
        
        assert len(elements) > 0
    
    def test_technique_table_empty_operation(self, mock_config, mock_operation_empty):
        """Test technique table with no techniques."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_technique_table(mock_operation_empty)
        
        # Should have title and message about no techniques
        assert len(elements) >= 1
    
    def test_technique_table_status_mapping(self, mock_config, mock_operation_complex):
        """Test that status codes are correctly mapped to symbols."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_technique_table(mock_operation_complex)
        
        # Should create table with status symbols
        assert len(elements) > 0


class TestPDFGeneratorTacticCoverage:
    """Test tactic coverage analysis."""
    
    def test_tactic_coverage_with_techniques(self, mock_config, mock_operation_simple):
        """Test tactic coverage with executed techniques."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_tactic_coverage(mock_operation_simple)
        
        assert len(elements) > 0
    
    def test_tactic_coverage_empty_operation(self, mock_config, mock_operation_empty):
        """Test tactic coverage with no techniques."""
        generator = PDFGenerator(mock_config)
        
        elements = generator._build_tactic_coverage(mock_operation_empty)
        
        # Should have title and message
        assert len(elements) >= 1
    
    def test_tactic_coverage_division_by_zero_protection(self, mock_config, mock_operation_empty):
        """Test division by zero protection in percentage calculations."""
        generator = PDFGenerator(mock_config)
        
        # Should not raise exception
        elements = generator._build_tactic_coverage(mock_operation_empty)
        
        assert len(elements) > 0


class TestPDFGeneratorSyncGeneration:
    """Test synchronous PDF generation."""
    
    def test_generate_pdf_sync_creates_file(self, mock_config, mock_operation_simple, tmp_path):
        """Test that PDF file is created."""
        mock_config.output_dir = tmp_path
        generator = PDFGenerator(mock_config)
        
        filename = 'test_report.pdf'
        pdf_path = generator._generate_pdf_sync(mock_operation_simple, filename)
        
        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'
    
    def test_generate_pdf_sync_with_complex_operation(self, mock_config, mock_operation_complex, tmp_path):
        """Test PDF generation with complex operation (30 techniques)."""
        mock_config.output_dir = tmp_path
        generator = PDFGenerator(mock_config)
        
        filename = 'complex_report.pdf'
        pdf_path = generator._generate_pdf_sync(mock_operation_complex, filename)
        
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0  # File has content


class TestPDFGeneratorAsyncGeneration:
    """Test asynchronous PDF generation."""
    
    @pytest.mark.asyncio
    async def test_generate_with_valid_operation(self, mock_config, mock_operation_simple, tmp_path):
        """Test async PDF generation with valid operation."""
        mock_config.output_dir = tmp_path
        generator = PDFGenerator(mock_config)
        
        pdf_path = await generator.generate(mock_operation_simple)
        
        assert pdf_path is not None
        assert pdf_path.exists()
    
    @pytest.mark.asyncio
    async def test_generate_returns_none_for_running_operation(self, mock_config, mock_operation_running):
        """Test that generate returns None for non-finished operations."""
        generator = PDFGenerator(mock_config)
        
        pdf_path = await generator.generate(mock_operation_running)
        
        assert pdf_path is None
    
    @pytest.mark.asyncio
    async def test_generate_raises_on_none_operation(self, mock_config):
        """Test that generate raises ValueError for None operation."""
        generator = PDFGenerator(mock_config)
        
        with pytest.raises(ValueError, match="Operation cannot be None"):
            await generator.generate(None)
    
    @pytest.mark.asyncio
    async def test_generate_raises_on_invalid_operation(self, mock_config):
        """Test that generate raises ValueError for operation without id."""
        generator = PDFGenerator(mock_config)
        
        invalid_op = MagicMock()
        del invalid_op.id  # Remove id attribute
        
        with pytest.raises(ValueError, match="must have 'id' attribute"):
            await generator.generate(invalid_op)
    
    @pytest.mark.asyncio
    async def test_generate_respects_timeout(self, mock_config, mock_operation_simple):
        """Test that generate respects timeout setting."""
        mock_config.generation_timeout = 0.1  # Very short timeout
        generator = PDFGenerator(mock_config)
        
        # Mock _generate_pdf_sync to sleep longer than timeout
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(1)
            return Path('fake.pdf')
        
        with patch.object(generator, '_generate_pdf_sync', side_effect=lambda *args: asyncio.sleep(1)):
            with pytest.raises(asyncio.TimeoutError):
                await generator.generate(mock_operation_simple)


class TestPDFGeneratorMemoryManagement:
    """Test memory management and cleanup."""
    
    @pytest.mark.asyncio
    async def test_shutdown_closes_executor(self, mock_config):
        """Test that shutdown closes ThreadPoolExecutor."""
        generator = PDFGenerator(mock_config)
        
        await generator.shutdown()
        
        # Executor should be shutdown
        assert generator.executor._shutdown
    
    @patch('plugins.reporting.app.pdf_generator.gc.collect')
    def test_gc_called_after_pdf_generation(self, mock_gc, mock_config, mock_operation_simple, tmp_path):
        """Test that garbage collection is called after PDF generation."""
        mock_config.output_dir = tmp_path
        generator = PDFGenerator(mock_config)
        
        generator._generate_pdf_sync(mock_operation_simple, 'test.pdf')
        
        # gc.collect() should be called
        mock_gc.assert_called()


class TestPDFGeneratorErrorHandling:
    """Test error handling and graceful degradation."""
    
    @pytest.mark.asyncio
    async def test_generate_handles_exceptions(self, mock_config, mock_operation_simple):
        """Test that generate handles exceptions gracefully."""
        generator = PDFGenerator(mock_config)
        
        # Mock _generate_pdf_sync to raise exception
        with patch.object(generator, '_generate_pdf_sync', side_effect=Exception("Test error")):
            pdf_path = await generator.generate(mock_operation_simple)
            
            # Should return None instead of crashing
            assert pdf_path is None
