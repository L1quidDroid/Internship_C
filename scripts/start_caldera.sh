#!/bin/bash
# Caldera Startup Script with ELK Authentication

echo " Starting Caldera with Orchestrator Plugin..."

# Load ELK credentials
if [ -f .env.elk ]; then
    source .env.elk
else
    echo "⚠️  Warning: .env.elk not found, ELK authentication may fail"
fi

# Verify credentials are set
if [ -z "$ELK_URL" ] || [ -z "$ELK_USER" ] || [ -z "$ELK_PASS" ]; then
    echo "❌ ERROR: ELK credentials not set!"
    echo "   Please create .env.elk with:"
    echo "   export ELK_URL=\"http://20.28.49.97:9200\""
    echo "   export ELK_USER=\"elastic\""
    echo "   export ELK_PASS=\"your-password\""
    exit 1
fi

# Start Caldera
python server.py --insecure --log INFO
