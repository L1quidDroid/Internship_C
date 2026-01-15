#!/bin/bash
# Triskele Labs Purple Team Environment Shutdown Script
# Gracefully stops Caldera → ELK Stack

set -e

LOG_FILE="/tmp/tl-shutdown.log"

echo "[SHUTDOWN] Triskele Labs Purple Team Environment..." | tee -a "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Shutdown initiated" >> "$LOG_FILE"

# Function: Stop service safely
stop_service() {
    local service=$1
    echo "  Stopping $service..."
    if systemctl is-active --quiet "$service"; then
        sudo systemctl stop "$service"
        sleep 2
        if systemctl is-active --quiet "$service"; then
            echo "  ⚠️  $service still running, forcing stop..."
            sudo systemctl kill "$service"
            sleep 1
        fi
        echo "  ✅ $service stopped"
    else
        echo "  ℹ️  $service already stopped"
    fi
}

# Step 1: Stop Caldera (if running in background)
echo ""
echo "[STOP] Caldera..."
CALDERA_PID=$(pgrep -f "python.*server.py" || true)
if [ -n "$CALDERA_PID" ]; then
    echo "  Found Caldera process: $CALDERA_PID"
    kill -TERM "$CALDERA_PID" 2>/dev/null || true
    sleep 3
    
    # Force kill if still running
    if ps -p "$CALDERA_PID" > /dev/null 2>&1; then
        echo "  ⚠️  Caldera still running, forcing shutdown..."
        kill -9 "$CALDERA_PID" 2>/dev/null || true
    fi
    echo "  ✅ Caldera stopped"
else
    echo "  ℹ️  Caldera not running"
fi

# Step 2: Stop Elastic Agent (collects telemetry)
echo ""
echo "[ELK] Stopping Elastic Agent..."
stop_service elastic-agent

# Step 3: Stop Logstash
echo ""
echo "[ELK] Stopping Logstash..."
stop_service logstash

# Step 4: Stop Kibana
echo ""
echo "[ELK] Stopping Kibana..."
stop_service kibana

# Step 5: Stop Elasticsearch (last to allow data flush)
echo ""
echo "[ELK] Stopping Elasticsearch..."
stop_service elasticsearch

# Step 6: Verify all stopped
echo ""
echo "✅ Shutdown sequence complete"
echo ""
echo "[STATUS] Final state:"
systemctl is-active --quiet elasticsearch && echo "  ⚠️  elasticsearch still running" || echo "  ✅ elasticsearch stopped"
systemctl is-active --quiet kibana && echo "  ⚠️  kibana still running" || echo "  ✅ kibana stopped"
systemctl is-active --quiet logstash && echo "  ⚠️  logstash still running" || echo "  ✅ logstash stopped"
systemctl is-active --quiet elastic-agent && echo "  ⚠️  elastic-agent still running" || echo "  ✅ elastic-agent stopped"

echo ""
echo "$(date '+%Y-%m-%d %H:%M:%S') - Shutdown complete" >> "$LOG_FILE"
echo "[SHUTDOWN] Complete. Run ./tl-startup.sh to restart."
