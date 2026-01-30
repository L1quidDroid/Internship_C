#!/bin/bash
# Triskele Labs Purple Team Environment Startup Script
# Starts ELK Stack → Caldera → Validates functionality

set -e

CALDERA_DIR="/home/tonyto/caldera"
VENV_PATH="${CALDERA_DIR}/.venv"
LOG_FILE="/tmp/tl-startup.log"

echo "[STARTUP] Triskele Labs Purple Team Environment Starting..." | tee -a "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Startup initiated" >> "$LOG_FILE"

# Function: Check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo "  ✅ $service is running"
        return 0
    else
        echo "  ❌ $service failed to start"
        return 1
    fi
}

# Function: Wait for port
wait_for_port() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo "   Waiting for $name (port $port)..."
    while ! nc -z localhost "$port" 2>/dev/null; do
        sleep 1
        ((attempt++))
        if [ $attempt -ge $max_attempts ]; then
            echo "   $name did not start (timeout)"
            return 1
        fi
    done
    echo "   OK $name is ready on port $port"
    return 0
}

# Step 1: Check VM resources
echo ""
echo "[CHECK] VM resources..."
AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
if [ "$AVAILABLE_MEM" -lt 4 ]; then
    echo "    Warning: Only ${AVAILABLE_MEM}GB RAM available (recommend 4GB+)"
else
    echo "   Memory available: ${AVAILABLE_MEM}GB"
fi

# Step 2: Start ELK Stack
echo ""
echo "[ELK] Starting ELK Stack..."

echo "  Starting Elasticsearch..."
sudo systemctl start elasticsearch
sleep 3
check_service elasticsearch || exit 1

echo "  Starting Kibana..."
sudo systemctl start kibana
check_service kibana || exit 1

echo "  Starting Logstash..."
sudo systemctl start logstash
check_service logstash || exit 1

echo "  Starting Elastic Agent..."
sudo systemctl start elastic-agent
check_service elastic-agent || exit 1

# Step 3: Wait for ELK ports
echo ""
echo "[VERIFY] ELK connectivity..."
wait_for_port 9200 "Elasticsearch" || exit 1
wait_for_port 5601 "Kibana" || exit 1

# Verify Elasticsearch cluster health
ES_HEALTH=$(curl -s localhost:9200/_cluster/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
if [ "$ES_HEALTH" = "green" ] || [ "$ES_HEALTH" = "yellow" ]; then
    echo "   Elasticsearch cluster: $ES_HEALTH"
else
    echo "  Elasticsearch cluster unhealthy: $ES_HEALTH"
    exit 1
fi

# Step 4: Update Caldera codebase
echo ""
echo "[UPDATE] Caldera from GitHub..."
cd "$CALDERA_DIR" || exit 1
git pull origin main 2>&1 | tee -a "$LOG_FILE" | grep -E "Already up to date|Updating|Fast-forward" || true

# Step 5: Activate virtual environment
echo ""
echo "[VENV] Python virtual environment..."
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "   OK Virtual environment activated: $VENV_PATH"
else
    echo "   Virtual environment not found: $VENV_PATH"
    echo "  Creating new virtual environment..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
fi

# Step 6: Install/upgrade dependencies
echo ""
echo "[DEPS] Installing Caldera dependencies..."
pip3 install -q -r requirements.txt --upgrade 2>&1 | grep -E "Successfully installed|Requirement already satisfied" | head -5 || echo "  Dependencies checked"

# Step 7: Load ELK credentials
echo ""
echo "[AUTH] Loading ELK credentials..."
if [ -f "$CALDERA_DIR/.env.elk" ]; then
    source "$CALDERA_DIR/.env.elk"
    echo "   ELK credentials loaded"
    echo "     ELK_URL: $ELK_URL"
    echo "     ELK_USER: $ELK_USER"
    echo "     ELK_PASS: ${ELK_PASS:0:5}***"
else
    echo "    Warning: .env.elk not found, orchestrator may not connect to ELK"
fi

# Step 8: Load Caldera credentials
if [ -f "$CALDERA_DIR/conf/local.yml" ]; then
    echo "   OK Caldera config found: conf/local.yml"
else
    echo "    Warning: conf/local.yml not found"
fi

# Step 9: Start Caldera
echo ""
echo "[START] Caldera server..."
echo "  Command: python3 server.py --insecure --log INFO"
echo "  (Press Ctrl+C to stop)"
echo ""

# Log final status
echo "$(date '+%Y-%m-%d %H:%M:%S') - Startup complete, launching Caldera" >> "$LOG_FILE"
echo "OK ELK Stack: Running"
echo "OK Elasticsearch: http://localhost:9200"
echo "OK Kibana: http://localhost:5601"
echo "OK Starting Caldera on http://localhost:8888"
echo ""

# Start Caldera (foreground)
python3 server.py --insecure --log INFO
