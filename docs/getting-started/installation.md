# Installation Guide

## Overview

This guide covers the installation and initial setup of the Triskele Labs Purple Team Environment. The platform requires Python 3.9 or higher and can optionally integrate with an Elasticsearch Stack for SIEM correlation.

## Prerequisites

### System Requirements

- **Operating System** - Linux, macOS, or Windows with WSL
- **Python** - Version 3.9 or higher
- **Memory** - Minimum 4GB RAM, 8GB recommended
- **Disk Space** - Minimum 2GB for application and data
- **Network** - Port 8888 available for web interface

### Optional Components

- **Elasticsearch** - Version 8.11.0 or higher (for SIEM integration)
- **Git** - For source code management
- **curl** - For API testing and agent deployment

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/triskele-labs/command-center.git
cd command-center
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Verify Installation

```bash
# Run sanity checks
./scripts/verify_sanity.sh

# Expected output:
# ✓ Python version: 3.9+
# ✓ Dependencies installed
# ✓ Configuration files present
# ✓ Port 8888 available
```

### Step 5: Initial Configuration

Create local configuration file:

```bash
cp conf/default.yml conf/local.yml
```

Edit `conf/local.yml` to customise settings:

```yaml
host: 0.0.0.0
port: 8888
plugins:
  - atomic
  - branding
  - debrief
  - magma
  - orchestrator
  - reporting
  - sandcat
  - stockpile
```

### Step 6: Start the Server

```bash
# Start Caldera server only
python3 server.py --insecure

# Or use the startup script for full environment
./scripts/tl-startup.sh
```

### Step 7: Verify Server is Running

```bash
# Check server health
curl http://localhost:8888/api/v2/health

# Expected response:
# {
#   "status": "healthy",
#   "plugins": ["magma", "sandcat", "stockpile", ...]
# }
```

### Step 8: Access Web Interface

Open your browser to:

```
http://localhost:8888
```

Default credentials:
- **Username:** admin
- **Password:** admin

**Important:** Change the default password immediately after first login.

## ELK Stack Integration (Optional)

### Prerequisites

Running Elasticsearch instance with:
- Elasticsearch 8.11.0 or higher
- Kibana (optional, for visualisation)
- Logstash or Elastic Agent (for log ingestion)

### Configuration Steps

1. Create environment configuration file:

```bash
cp .env.example .env
```

2. Edit `.env` with your Elasticsearch details:

```bash
# Elasticsearch Configuration
ELK_HOST=192.168.1.50
ELK_PORT=9200
ELK_INDEX=purple-team-*

# Authentication - Choose one method:

# Method 1: API Key (Recommended)
ELK_API_KEY=your-api-key-here
ELK_USE_API_KEY=true

# Method 2: Basic Authentication
# ELK_USERNAME=elastic
# ELK_PASSWORD=your-password
# ELK_USE_API_KEY=false

# TLS/SSL Configuration
ELK_USE_TLS=true
ELK_VERIFY_SSL=true
# ELK_CA_CERT_PATH=/path/to/ca.crt

# Connection Settings
ELK_CONNECTION_TIMEOUT=30
ELK_MAX_RETRIES=3
```

3. Verify ELK connectivity:

```bash
# Test connection
python3 -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()

elk_host = os.getenv('ELK_HOST')
elk_port = os.getenv('ELK_PORT')

response = requests.get(f'http://{elk_host}:{elk_port}/_cluster/health')
print(f'ELK Status: {response.json()[\"status\"]}')
"
```

4. Restart the server to load environment variables:

```bash
./scripts/tl-shutdown.sh
./scripts/tl-startup.sh
```

## Docker Installation (Alternative)

For containerised deployment:

### Step 1: Build Docker Image

```bash
cd config
docker build -t triskele-caldera:latest -f Dockerfile ..
```

### Step 2: Run Container

```bash
docker run -d \
  --name caldera \
  -p 8888:8888 \
  -p 8443:8443 \
  -v $(pwd)/data:/app/data \
  triskele-caldera:latest
```

### Step 3: Verify Container

```bash
docker logs caldera
docker exec caldera curl http://localhost:8888/api/v2/health
```

For Docker Compose deployment, see [Docker Deployment Guide](../deployment/docker-deployment.md).

## Post-Installation Steps

### Change Default Credentials

1. Log in to web interface at `http://localhost:8888`
2. Navigate to **Settings** > **Users**
3. Change admin password
4. Create additional user accounts as needed

### Configure Firewall Rules

```bash
# Allow Caldera web interface
sudo ufw allow 8888/tcp

# Allow agent communication (if using alternative ports)
sudo ufw allow 7010/tcp
sudo ufw allow 7011/udp
sudo ufw allow 7012/tcp
```

### Enable Automated Startup (Optional)

Create systemd service file:

```bash
sudo nano /etc/systemd/system/caldera.service
```

Add content:

```ini
[Unit]
Description=Triskele Labs Caldera Server
After=network.target

[Service]
Type=simple
User=caldera
WorkingDirectory=/opt/command-center
ExecStart=/opt/command-center/venv/bin/python3 server.py --insecure
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable caldera
sudo systemctl start caldera
```

## Troubleshooting

### Port 8888 Already in Use

```bash
# Find process using port
lsof -ti:8888

# Kill process
kill -9 $(lsof -ti:8888)
```

### Dependencies Installation Fails

```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Permission Denied Errors

```bash
# Ensure scripts are executable
chmod +x scripts/*.sh

# Run with appropriate permissions
sudo ./scripts/tl-startup.sh
```

### Server Fails to Start

Check logs for errors:

```bash
# View recent logs
tail -f logs/caldera.log

# Check for common issues:
# - Port already in use
# - Missing dependencies
# - Configuration file errors
# - Insufficient permissions
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Get operational in 10 minutes
- [Configuration Reference](configuration.md) - Detailed configuration options
- [Agent Management](../user-guide/agents.md) - Deploy your first agents
- [Running Operations](../user-guide/operations.md) - Execute adversary emulation

## See Also

- [Docker Deployment](../deployment/docker-deployment.md) - Container orchestration
- [ELK Integration](../deployment/elk-integration.md) - SIEM correlation setup
- [Troubleshooting](../deployment/troubleshooting.md) - Common issues and solutions
