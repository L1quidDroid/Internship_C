#!/bin/bash
# Triskele Labs Purple Team Environment Status Check
# Validates ELK Stack, Caldera, and connectivity

echo "[STATUS] Triskele Labs Purple Team Environment"
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Function: Check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo "  ✅ $service: running"
        return 0
    else
        echo "  ❌ $service: stopped"
        return 1
    fi
}

# Function: Check port
check_port() {
    local port=$1
    local name=$2
    if nc -z localhost "$port" 2>/dev/null; then
        echo "  ✅ $name (port $port): reachable"
        return 0
    else
        echo "  ❌ $name (port $port): unreachable"
        return 1
    fi
}

# System Resources
echo "[RESOURCES] System:"
FREE_MEM=$(free -h | awk '/^Mem:/{print $7}')
TOTAL_MEM=$(free -h | awk '/^Mem:/{print $2}')
echo "  Memory: $FREE_MEM available / $TOTAL_MEM total"

DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
echo "  Disk: $DISK_AVAIL available on /"
echo ""

# ELK Services
echo "[ELK] Stack Services:"
check_service elasticsearch
check_service kibana
check_service logstash
check_service elastic-agent
echo ""

# Network Ports
echo "[NETWORK] Connectivity:"
check_port 9200 "Elasticsearch"
check_port 5601 "Kibana"
check_port 8888 "Caldera"
echo ""

# Elasticsearch Health
echo "[CLUSTER] Elasticsearch:"
if nc -z localhost 9200 2>/dev/null; then
    ES_HEALTH=$(curl -s localhost:9200/_cluster/health 2>/dev/null)
    if [ -n "$ES_HEALTH" ]; then
        CLUSTER_NAME=$(echo "$ES_HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cluster_name','unknown'))" 2>/dev/null || echo "unknown")
        CLUSTER_STATUS=$(echo "$ES_HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
        NODE_COUNT=$(echo "$ES_HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('number_of_nodes','?'))" 2>/dev/null || echo "?")
        
        echo "  Cluster: $CLUSTER_NAME"
        echo "  Status: $CLUSTER_STATUS"
        echo "  Nodes: $NODE_COUNT"
    else
        echo "  ❌ Unable to query cluster health"
    fi
else
    echo "  ❌ Elasticsearch not responding"
fi
echo ""

# Caldera Process
echo "[CALDERA] Server:"
CALDERA_PID=$(pgrep -f "python.*server.py" 2>/dev/null || true)
if [ -n "$CALDERA_PID" ]; then
    echo "  ✅ Running (PID: $CALDERA_PID)"
    if nc -z localhost 8888 2>/dev/null; then
        echo "  ✅ Web interface: http://localhost:8888"
    else
        echo "  ⚠️  Process running but port 8888 not responding"
    fi
else
    echo "  ❌ Not running"
fi
echo ""

# Purple Team Logs
echo "[LOGS] Purple Team in ELK:"
if nc -z localhost 9200 2>/dev/null; then
    DOC_COUNT=$(curl -s "localhost:9200/purple-team-logs/_count" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('count','?'))" 2>/dev/null || echo "?")
    echo "  Documents: $DOC_COUNT"
else
    echo "  ❌ Cannot query (Elasticsearch offline)"
fi
echo ""

# Overall Status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ALL_SERVICES_UP=true
systemctl is-active --quiet elasticsearch || ALL_SERVICES_UP=false
systemctl is-active --quiet kibana || ALL_SERVICES_UP=false
systemctl is-active --quiet logstash || ALL_SERVICES_UP=false
[ -n "$CALDERA_PID" ] || ALL_SERVICES_UP=false

if [ "$ALL_SERVICES_UP" = true ]; then
    echo "OK All systems operational"
else
    echo "⚠️  Some systems offline. Run: ./tl-startup.sh"
fi
