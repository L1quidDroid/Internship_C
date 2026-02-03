---

**⚠️ INTERNSHIP PROJECT DOCUMENTATION**

This document describes Docker deployment approaches used during a Triskele Labs internship (January-February 2026) by Tony To. This is educational documentation for portfolio purposes, NOT official Triskele Labs documentation or production deployment guidance.

**Status**: Learning Exercise | **NOT FOR**: Production Use

See [INTERNSHIP_DISCLAIMER.md](../../INTERNSHIP_DISCLAIMER.md) for complete information.

---

# Docker Deployment Guide

This guide covers deploying this internship project using Docker containers for portable, consistent testing and development environments.

## Prerequisites

### System Requirements

- **Docker:** Latest stable version
- **Docker Compose:** Latest stable version
- **Memory:** 8GB RAM minimum for container host
- **Disk Space:** 20GB for images and volumes
- **Network:** Ports 8888, 8443, 7010-7012, 8853, 8022, 2222 accessible

### Install Docker

Ubuntu/Debian:

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install ca-certificates curl gnupg

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker run hello-world
```

### Add User to Docker Group

Allow running Docker without sudo:

```bash
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world
```

## Build Configuration

### Dockerfile Overview

The Dockerfile uses a multi-stage build process for efficiency:

#### Stage 1: UI Build

Builds the Vue.js frontend (Magma plugin):

```dockerfile
FROM node:23 AS ui-build

WORKDIR /usr/src/app

ADD . .
# Build VueJS front-end
RUN (cd plugins/magma; npm install && npm run build)
```

#### Stage 2: Runtime

Contains all dependencies required by Caldera:

```dockerfile
FROM debian:bookworm-slim AS runtime

# Build variant: full or slim
ARG VARIANT=full
ENV VARIANT=${VARIANT}

WORKDIR /usr/src/app

# Copy source code and compiled UI
ADD . .
COPY --from=ui-build /usr/src/app/plugins/magma/dist /usr/src/app/plugins/magma/dist

# Install system dependencies
RUN apt-get update && \
apt-get --no-install-recommends -y install git curl unzip python3-dev python3-pip mingw-w64 zlib1g gcc && \
rm -rf /var/lib/apt/lists/*

# Install Golang from source
RUN curl -k -L https://go.dev/dl/go1.25.0.linux-amd64.tar.gz -o go.tar.gz && \
tar -C /usr/local -xzf go.tar.gz && rm go.tar.gz
ENV PATH="$PATH:/usr/local/go/bin"

# Install Python dependencies
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Install Go dependencies for Sandcat
RUN cd /usr/src/app/plugins/sandcat/gocat; go mod tidy && go mod download

# Update Sandcat agents
RUN cd /usr/src/app/plugins/sandcat; ./update-agents.sh

STOPSIGNAL SIGINT

# Default HTTP port for web interface and agent beacons
EXPOSE 8888
```

### Build Variants

#### Full Variant (Default)

Includes all dependencies for offline operation:

- Atomic Red Team repository (large dataset)
- EMU adversary emulation plans
- Pre-compiled Sandcat agents for all platforms

```bash
docker build --build-arg VARIANT=full -t caldera:latest .
```

#### Slim Variant

Excludes large dependencies that can be downloaded on-demand:

- Atomic and EMU plugins disabled by default
- Requires internet connection for on-demand downloads
- Smaller image size for faster deployment

```bash
docker build --build-arg VARIANT=slim -t caldera:slim .
```

### Build Arguments

#### VARIANT

Controls included dependencies:

- `full` - Suitable for offline use, includes all resources
- `slim` - Smaller image, requires internet for some plugins

#### TZ

Sets container timezone (default: UTC):

```bash
docker build --build-arg TZ="Australia/Sydney" -t caldera:latest .
```

## Docker Compose Deployment

### Configuration File

The `docker-compose.yml` file defines the service configuration:

```yaml
version: '3'

services:
  caldera:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        TZ: "UTC"
        VARIANT: "full"
    image: caldera:latest
    ports:
      - "8888:8888"   # HTTP web interface
      - "8443:8443"   # HTTPS web interface
      - "7010:7010"   # TCP contact
      - "7011:7011/udp"  # UDP contact
      - "7012:7012"   # Websocket contact
      - "8853:8853"   # DNS-over-HTTPS contact
      - "8022:8022"   # SSH contact
      - "2222:2222"   # FTP contact
    volumes:
      - ./:/usr/src/app
    command: --log DEBUG
```

### Port Mappings

| Port | Protocol | Purpose |
|------|----------|---------|
| 8888 | TCP | HTTP web interface and agent beacons |
| 8443 | TCP | HTTPS web interface (production) |
| 7010 | TCP | TCP contact for agents |
| 7011 | UDP | UDP contact for agents |
| 7012 | TCP | Websocket contact for events |
| 8853 | TCP | DNS-over-HTTPS contact |
| 8022 | TCP | SSH contact for agents |
| 2222 | TCP | FTP contact for agents |

### Volume Mounts

The compose file mounts the current directory as a volume:

```yaml
volumes:
  - ./:/usr/src/app
```

**Benefits:**
- Code changes reflect immediately (no rebuild required)
- Data persists between container restarts
- Configuration files accessible from host

**Security Note:** Do not mount volumes in production that expose sensitive files.

## Building the Image

### Build with Docker Compose

```bash
cd /path/to/caldera
docker-compose build
```

This executes the build process defined in `docker-compose.yml`.

### Build with Docker CLI

For more control over build process:

```bash
# Full variant
docker build -t caldera:latest .

# Slim variant
docker build --build-arg VARIANT=slim -t caldera:slim .

# Custom timezone
docker build --build-arg TZ="Australia/Melbourne" -t caldera:latest .

# Multiple build arguments
docker build \
  --build-arg VARIANT=full \
  --build-arg TZ="Australia/Brisbane" \
  -t caldera:latest .
```

### Build Cache

Docker caches layers for faster subsequent builds. To force a clean build:

```bash
docker build --no-cache -t caldera:latest .
```

### Multi-Architecture Builds

Build for multiple platforms (requires buildx):

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t caldera:latest .
```

## Running the Container

### Start with Docker Compose

```bash
docker-compose up
```

Run in detached mode (background):

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

### Start with Docker CLI

```bash
docker run -d \
  --name caldera \
  -p 8888:8888 \
  -p 8443:8443 \
  -v $(pwd):/usr/src/app \
  caldera:latest \
  --log INFO
```

### Custom Command Arguments

Override default command arguments:

```bash
# Debug logging
docker-compose run caldera --log DEBUG

# Insecure mode (development only)
docker-compose run caldera --insecure --log INFO

# Build mode (first-time setup)
docker-compose run caldera --build
```

## Managing Containers

### View Running Containers

```bash
docker ps
```

### Stop Containers

```bash
# With Docker Compose
docker-compose down

# With Docker CLI
docker stop caldera
```

### Restart Containers

```bash
# With Docker Compose
docker-compose restart

# With Docker CLI
docker restart caldera
```

### Remove Containers

```bash
# Remove stopped container
docker rm caldera

# Force remove running container
docker rm -f caldera

# Remove all stopped containers
docker container prune
```

## Accessing the Container

### Execute Commands in Container

```bash
# Interactive shell
docker exec -it caldera /bin/bash

# Run single command
docker exec caldera ls -la /usr/src/app

# Check Python version
docker exec caldera python3 --version

# View installed packages
docker exec caldera pip3 list
```

### View Container Logs

```bash
# All logs
docker logs caldera

# Follow logs (real-time)
docker logs -f caldera

# Last 100 lines
docker logs --tail 100 caldera

# Logs with timestamps
docker logs -t caldera
```

## Data Persistence

### Using Volumes

For learning environment setup, use named volumes for data persistence:

```yaml
version: '3'

services:
  caldera:
    image: caldera:latest
    volumes:
      - caldera-data:/usr/src/app/data
      - caldera-logs:/usr/src/app/logs
      - caldera-conf:/usr/src/app/conf
    ports:
      - "8888:8888"

volumes:
  caldera-data:
  caldera-logs:
  caldera-conf:
```

### Backup Data

```bash
# Create backup of named volume
docker run --rm -v caldera-data:/data -v $(pwd):/backup \
  debian:bookworm-slim \
  tar czf /backup/caldera-data-backup.tar.gz -C /data .

# Restore backup
docker run --rm -v caldera-data:/data -v $(pwd):/backup \
  debian:bookworm-slim \
  tar xzf /backup/caldera-data-backup.tar.gz -C /data
```

## Environment Variables

### Configuration via .env File

Create `.env` file in the same directory as `docker-compose.yml`:

```bash
# ELK Integration
ELK_URL=http://elasticsearch:9200
ELK_USER=elastic
ELK_PASS=your-password-here

# Caldera Configuration
CALDERA_HOST=0.0.0.0
CALDERA_PORT=8888
```

Reference in `docker-compose.yml`:

```yaml
services:
  caldera:
    env_file:
      - .env
    environment:
      - ELK_URL=${ELK_URL}
      - ELK_USER=${ELK_USER}
      - ELK_PASS=${ELK_PASS}
```

### Pass Environment Variables

```bash
# Via Docker Compose
docker-compose run -e ELK_URL=http://elk:9200 caldera

# Via Docker CLI
docker run -e ELK_URL=http://elk:9200 -e ELK_USER=elastic caldera:latest
```

## Network Configuration

### Default Bridge Network

By default, containers use Docker's bridge network:

```bash
docker network inspect bridge
```

### Custom Network

Create isolated network for Caldera stack:

```yaml
version: '3'

services:
  caldera:
    image: caldera:latest
    networks:
      - caldera-net

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    networks:
      - caldera-net

networks:
  caldera-net:
    driver: bridge
```

### Host Network Mode

Use host networking for better performance (Linux only):

```yaml
services:
  caldera:
    image: caldera:latest
    network_mode: host
```

**Note:** Port mappings are ignored in host mode.

## Integration with ELK Stack

### Docker Compose with ELK

Complete stack with Caldera and ELK:

```yaml
version: '3'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es-data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  caldera:
    build: .
    image: caldera:latest
    ports:
      - "8888:8888"
    environment:
      - ELK_URL=http://elasticsearch:9200
      - ELK_USER=elastic
      - ELK_PASS=changeme
    depends_on:
      - elasticsearch
      - kibana

volumes:
  es-data:
```

Start the complete stack:

```bash
docker-compose up -d
```

## Troubleshooting

### Container Fails to Start

Check logs for errors:

```bash
docker logs caldera
```

Common issues:
- Port already in use: Change port mappings
- Insufficient memory: Increase Docker memory limit
- Permission errors: Check volume mount permissions

### Image Build Failures

**Error:** "failed to solve with frontend dockerfile.v0"

**Solution:** Update Docker to latest version

**Error:** "no space left on device"

**Solution:** Clean up unused images and containers:

```bash
docker system prune -a
```

### Network Connectivity Issues

Test container network:

```bash
# Check container IP
docker inspect caldera | grep IPAddress

# Test connectivity from container
docker exec caldera curl http://elasticsearch:9200
```

### Performance Issues

Check resource usage:

```bash
docker stats caldera
```

Increase container memory limit in `docker-compose.yml`:

```yaml
services:
  caldera:
    image: caldera:latest
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### .dockerignore Importance

The `.dockerignore` file prevents local build artifacts from interfering:

```
# Ignore local builds
*.pyc
__pycache__/
.venv/
node_modules/
.git/
.env*
conf/local.yml
```

Without proper `.dockerignore`, builds may include unwanted files.

## Best Practices

### Security

1. **Never expose containers directly to internet** - Use reverse proxy
2. **Change default credentials** - Configure in `conf/local.yml`
3. **Use secrets management** - Docker secrets or external vault
4. **Regular updates** - Rebuild images with latest base images
5. **Scan images** - Use `docker scan caldera:latest` for vulnerabilities

### Resource Management

1. **Set memory limits** - Prevent container from consuming all host memory
2. **Use multi-stage builds** - Reduce final image size
3. **Clean up regularly** - Remove unused images and containers
4. **Monitor resource usage** - Use `docker stats` to track consumption

### Development Workflow

1. **Use volume mounts** - For live code reloading
2. **Separate environments** - Different compose files for dev/prod
3. **Tag images properly** - Use semantic versioning
4. **Document customisations** - Maintain clear build documentation

## Development Environment Setup

**⚠️ INTERNSHIP PROJECT**: This section describes development environment setup for portfolio demonstration, NOT production deployment guidance.

### Production-Ready Compose File

```yaml
version: '3'

services:
  caldera:
    build:
      context: .
      args:
        VARIANT: full
        TZ: "UTC"
    image: caldera:production
    restart: always
    ports:
      - "8443:8443"  # HTTPS only
    volumes:
      - caldera-conf:/usr/src/app/conf:ro
      - caldera-data:/usr/src/app/data
      - caldera-logs:/usr/src/app/logs
    environment:
      - ELK_URL=${ELK_URL}
      - ELK_USER=${ELK_USER}
      - ELK_PASS=${ELK_PASS}
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  caldera-conf:
  caldera-data:
  caldera-logs:
```

### Health Checks

Add health check to ensure container is functioning:

```yaml
services:
  caldera:
    image: caldera:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/api/v2/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Logging Configuration

Configure Docker logging driver:

```yaml
services:
  caldera:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Next Steps

- [Local Deployment](local-deployment.md) - Deploy without containers
- [ELK Integration](elk-integration.md) - Configure SIEM tagging
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## See Also

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Configuration Guide](../getting-started/configuration.md)
