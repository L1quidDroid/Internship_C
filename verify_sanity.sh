#!/usr/bin/env bash
#
# Production Sanity Check for Triskele Labs Caldera
# Run this before deploying to TL VM
#
set -e

echo "=================================================="
echo "  TRISKELE LABS CALDERA - SANITY CHECK"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Compile all Python files
echo -e "${YELLOW}[1/4] Compiling Python files...${NC}"
if python3 -m compileall . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python syntax OK${NC}"
else
    echo -e "${RED}❌ Syntax errors found${NC}"
    python3 -m compileall . 2>&1 | grep "SyntaxError"
    exit 1
fi

# Step 2: Import all 7 plugins
echo -e "${YELLOW}[2/4] Testing plugin imports...${NC}"
python3 - << 'EOF'
import sys
import importlib

plugins = [
    ("atomic", "plugins.atomic.hook"),
    ("branding", "plugins.branding.hook"),
    ("magma", "plugins.magma.hook"),
    ("orchestrator", "plugins.orchestrator.hook"),
    ("reporting", "plugins.reporting.hook"),
    ("sandcat", "plugins.sandcat.hook"),
    ("stockpile", "plugins.stockpile.hook"),
]

failed = []
for name, module in plugins:
    try:
        importlib.import_module(module)
        print(f"✅ {name:15s} imported successfully")
    except Exception as e:
        print(f"❌ {name:15s} FAILED: {str(e)[:60]}")
        failed.append(name)

if failed:
    print(f"\n❌ Failed plugins: {', '.join(failed)}")
    sys.exit(1)
else:
    print("\n✅ All 7 plugins imported successfully")
EOF

# Step 3: Check critical files exist
echo -e "${YELLOW}[3/4] Verifying critical files...${NC}"
critical_files=(
    "plugins/orchestrator/app/orchestrator_svc.py"
    "plugins/reporting/app/report_svc.py"
    "plugins/reporting/app/pdf_generator.py"
    "plugins/branding/static/css/triskele.css"
    "plugins/branding/static/js/branding.js"
    "plugins/reporting/static/assets/triskele_logo.png"
    "conf/default.yml"
)

all_exist=true
for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ MISSING: $file"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo -e "${RED}❌ Critical files missing${NC}"
    exit 1
fi

# Step 4: Check dependencies
echo -e "${YELLOW}[4/4] Checking Python dependencies...${NC}"
python3 - << 'EOF'
import sys

required = [
    "aiohttp",
    "yaml",
    "marshmallow",
    "reportlab",
    "dotenv",
    "elasticsearch"
]

missing = []
for module in required:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError:
        print(f"  ❌ MISSING: {module}")
        missing.append(module)

if missing:
    print(f"\n❌ Install missing: pip install {' '.join(missing)}")
    sys.exit(1)
EOF

echo ""
echo "=================================================="
echo -e "${GREEN}✅ ALL SANITY CHECKS PASSED${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Start server: python server.py --insecure"
echo "  2. Check logs for 7 plugin 'enabled' messages"
echo "  3. Run golden operation (see TOMORROW.md)"
echo ""
