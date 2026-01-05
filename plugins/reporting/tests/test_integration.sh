#!/usr/bin/env bash
#
# Integration test script for the Reporting plugin
# Validates plugin structure, configuration, and PDF generation
#

set -e

PLUGIN_DIR="plugins/reporting"
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Reporting Plugin Integration Tests ===${NC}\n"

# Test 1: Plugin structure validation
echo -e "${YELLOW}[1/6] Validating plugin directory structure...${NC}"

required_files=(
    "$PLUGIN_DIR/__init__.py"
    "$PLUGIN_DIR/hook.py"
    "$PLUGIN_DIR/app/__init__.py"
    "$PLUGIN_DIR/app/config.py"
    "$PLUGIN_DIR/app/pdf_generator.py"
    "$PLUGIN_DIR/app/report_svc.py"
    "$PLUGIN_DIR/tests/__init__.py"
    "$PLUGIN_DIR/tests/fixtures.py"
    "$PLUGIN_DIR/tests/test_pdf_generator.py"
    "$PLUGIN_DIR/README.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ All required files present${NC}\n"

# Test 2: Python syntax validation
echo -e "${YELLOW}[2/6] Checking Python syntax...${NC}"

python3 -m py_compile "$PLUGIN_DIR/hook.py"
python3 -m py_compile "$PLUGIN_DIR/app/config.py"
python3 -m py_compile "$PLUGIN_DIR/app/pdf_generator.py"
python3 -m py_compile "$PLUGIN_DIR/app/report_svc.py"
python3 -m py_compile "$PLUGIN_DIR/tests/fixtures.py"
python3 -m py_compile "$PLUGIN_DIR/tests/test_pdf_generator.py"

echo -e "${GREEN}✓ All Python files have valid syntax${NC}\n"

# Test 3: Import validation (skip report_svc as it requires Caldera)
echo -e "${YELLOW}[3/6] Validating imports...${NC}"

python3 -c "from plugins.reporting.app.config import ReportingConfig"
python3 -c "from plugins.reporting.app.pdf_generator import PDFGenerator"
# Note: report_svc import requires full Caldera environment

echo -e "${GREEN}✓ Core imports successful${NC}\n"

# Test 4: Configuration validation
echo -e "${YELLOW}[4/6] Testing configuration validation logic...${NC}"

python3 << 'EOF'
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, '.')

# Mock BaseWorld to avoid Caldera dependency
with patch('plugins.reporting.app.config.BaseWorld') as mock_base:
    mock_base.get_config.return_value = {}
    
    from plugins.reporting.app.config import ReportingConfig
    
    config = ReportingConfig()
    is_valid, errors = config.validate()
    
    if not is_valid:
        print(f"Configuration validation failed: {errors}")
        sys.exit(1)
    
    print(f"Configuration valid: {config}")
EOF

echo -e "${GREEN}✓ Configuration validation passed${NC}\n"

# Test 5: Unit tests
echo -e "${YELLOW}[5/6] Running unit tests...${NC}"

if command -v pytest &> /dev/null; then
    python3 -m pytest "$PLUGIN_DIR/tests/test_pdf_generator.py" -v --tb=short
    echo -e "${GREEN}✓ All unit tests passed${NC}\n"
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping unit tests${NC}"
    echo -e "${YELLOW}  (Tests will run when Caldera venv is activated)${NC}\n"
fi

# Test 6: PDF generation test
echo -e "${YELLOW}[6/6] Testing PDF generation...${NC}"

python3 << 'EOF'
import sys
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

sys.path.insert(0, '.')

# Mock BaseWorld to avoid Caldera dependency
with patch('plugins.reporting.app.config.BaseWorld') as mock_base:
    mock_base.get_config.return_value = {}
    
    from plugins.reporting.app.config import ReportingConfig
    from plugins.reporting.app.pdf_generator import PDFGenerator
    
    # Create mock operation
    operation = MagicMock()
    operation.id = 'integration-test-001'
    operation.name = 'Integration Test Operation'
    operation.group = 'test_group'
    operation.state = 'finished'
    operation.start = datetime.now() - timedelta(minutes=10)
    operation.finish = datetime.now()
    operation.adversary = MagicMock(name='Test Adversary', description='Test')
    operation.planner = MagicMock(name='atomic')
    operation.jitter = '2/8'
    
    # Create mock link (technique)
    link = MagicMock()
    link.ability = MagicMock()
    link.ability.ability_id = 'test-123'
    link.ability.name = 'Test Technique'
    link.ability.technique_id = 'T1078'
    link.ability.technique_name = 'Valid Accounts'
    link.ability.tactic = 'persistence'
    link.status = 0
    link.finish = datetime.now().isoformat()
    link.command = 'echo "test"'
    link.output = 'test output'
    
    operation.chain = [link]
    operation.agents = []
    
    # Generate PDF
    async def test():
        config = ReportingConfig()
        generator = PDFGenerator(config)
        
        pdf_path = await generator.generate(operation)
        
        if not pdf_path or not pdf_path.exists():
            print(f"PDF generation failed")
            sys.exit(1)
        
        print(f"PDF generated successfully: {pdf_path}")
        print(f"PDF size: {pdf_path.stat().st_size} bytes")
        
        # Cleanup
        await generator.shutdown()
        pdf_path.unlink()
    
    asyncio.run(test())
EOF

echo -e "${GREEN}✓ PDF generation successful${NC}\n"

# Summary
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}All integration tests passed! ✓${NC}"
echo -e "${GREEN}==================================${NC}"
echo -e ""
echo -e "Plugin is ready for deployment."
echo -e "To enable: Add 'reporting' to plugins list in conf/local.yml"
echo -e ""
