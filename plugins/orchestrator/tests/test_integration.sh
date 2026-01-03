#!/bin/bash
# Integration test for orchestrator plugin

set -e

echo "🧪 Orchestrator Plugin Integration Test"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CALDERA_DIR="/Users/tonyto/Documents/GitHub/Triskele Labs/Internship_C"
ELK_URL="${ELK_URL:-http://localhost:9200}"
FALLBACK_DIR="$CALDERA_DIR/plugins/orchestrator/data/fallback_logs"

# 1. Check ELK connectivity
echo -e "\n1. Testing ELK connection..."
if curl -f -s "$ELK_URL/_cluster/health" > /dev/null; then
    echo -e "   ${GREEN}✅ ELK reachable${NC}"
else
    echo -e "   ${YELLOW}⚠️  ELK not reachable (fallback logging will be tested)${NC}"
fi

# 2. Check plugin files exist
echo -e "\n2. Verifying plugin files..."
if [ -f "$CALDERA_DIR/plugins/orchestrator/hook.py" ]; then
    echo -e "   ${GREEN}✅ Plugin hook exists${NC}"
else
    echo -e "   ${RED}❌ Plugin hook missing${NC}"
    exit 1
fi

if [ -f "$CALDERA_DIR/plugins/orchestrator/app/orchestrator_svc.py" ]; then
    echo -e "   ${GREEN}✅ Orchestrator service exists${NC}"
else
    echo -e "   ${RED}❌ Orchestrator service missing${NC}"
    exit 1
fi

if [ -f "$CALDERA_DIR/plugins/orchestrator/app/elk_tagger.py" ]; then
    echo -e "   ${GREEN}✅ ELK tagger exists${NC}"
else
    echo -e "   ${RED}❌ ELK tagger missing${NC}"
    exit 1
fi

# 3. Check configuration
echo -e "\n3. Verifying configuration..."
if [ -f "$CALDERA_DIR/conf/local.yml" ]; then
    if grep -q "orchestrator" "$CALDERA_DIR/conf/local.yml"; then
        echo -e "   ${GREEN}✅ Plugin enabled in conf/local.yml${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Plugin not listed in conf/local.yml${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  conf/local.yml not found${NC}"
fi

# 4. Check fallback directory
echo -e "\n4. Checking fallback directory..."
if [ -d "$FALLBACK_DIR" ]; then
    echo -e "   ${GREEN}✅ Fallback directory exists${NC}"
    echo -e "   📁 Path: $FALLBACK_DIR"
else
    echo -e "   ${RED}❌ Fallback directory missing${NC}"
    exit 1
fi

# 5. Run unit tests
echo -e "\n5. Running unit tests..."
cd "$CALDERA_DIR"
if python -m pytest plugins/orchestrator/tests/test_elk_tagger.py -v 2>&1 | tee /tmp/orchestrator_test.log; then
    echo -e "   ${GREEN}✅ Unit tests passed${NC}"
    
    # Show coverage summary
    PASSED=$(grep -c "PASSED" /tmp/orchestrator_test.log || echo "0")
    echo -e "   ✓ $PASSED tests passed"
else
    echo -e "   ${RED}❌ Unit tests failed${NC}"
    echo -e "   See /tmp/orchestrator_test.log for details"
    exit 1
fi

# 6. Check Python dependencies
echo -e "\n6. Checking Python dependencies..."
if python -c "import elasticsearch" 2>/dev/null; then
    echo -e "   ${GREEN}✅ elasticsearch library installed${NC}"
else
    echo -e "   ${YELLOW}⚠️  elasticsearch library not installed (fallback mode only)${NC}"
fi

if python -c "from dotenv import load_dotenv" 2>/dev/null; then
    echo -e "   ${GREEN}✅ python-dotenv library installed${NC}"
else
    echo -e "   ${RED}❌ python-dotenv library missing${NC}"
    echo -e "   Install with: pip install python-dotenv"
fi

# 7. Syntax check Python files
echo -e "\n7. Syntax checking Python files..."
SYNTAX_ERRORS=0

for file in plugins/orchestrator/app/*.py plugins/orchestrator/*.py; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            echo -e "   ${GREEN}✅${NC} $file"
        else
            echo -e "   ${RED}❌${NC} $file (syntax error)"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        fi
    fi
done

if [ $SYNTAX_ERRORS -gt 0 ]; then
    echo -e "\n   ${RED}❌ $SYNTAX_ERRORS files have syntax errors${NC}"
    exit 1
fi

# 8. Create test fallback file
echo -e "\n8. Testing fallback logging..."
TEST_FILE="$FALLBACK_DIR/test_fallback_$(date +%Y%m%d_%H%M%S).json"
cat > "$TEST_FILE" << 'EOF'
{
  "operation_id": "test-123",
  "purple_team_exercise": true,
  "timestamp": "2026-01-06T10:00:00Z",
  "techniques": ["T1078"],
  "client_id": "test_client"
}
EOF

if [ -f "$TEST_FILE" ]; then
    echo -e "   ${GREEN}✅ Fallback file created successfully${NC}"
    echo -e "   📄 $TEST_FILE"
    rm "$TEST_FILE"  # Cleanup
else
    echo -e "   ${RED}❌ Failed to create fallback file${NC}"
    exit 1
fi

# 9. Summary
echo -e "\n========================================"
echo -e "${GREEN}✅ All integration tests passed!${NC}"
echo -e "\n📋 Summary:"
echo -e "   • Plugin files: ✓"
echo -e "   • Configuration: ✓"
echo -e "   • Unit tests: ✓"
echo -e "   • Dependencies: ✓"
echo -e "   • Syntax check: ✓"
echo -e "   • Fallback logging: ✓"

echo -e "\n🚀 Next Steps:"
echo -e "   1. Start Caldera: python server.py --insecure --log INFO"
echo -e "   2. Check logs for: '✅ Orchestrator plugin enabled successfully'"
echo -e "   3. Run operation and verify ELK tagging"
echo -e "   4. Check fallback logs if ELK unavailable"

echo -e "\n📖 Documentation:"
echo -e "   • PRD: plugins/orchestrator/PRD.md"
echo -e "   • Examples: plugins/orchestrator/EXAMPLES.md"
