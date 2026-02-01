# Deployment Troubleshooting Guide

This guide covers common deployment issues and their solutions for the Triskele Labs Command Center.

## System Resource Issues

### Insufficient Memory

**Symptom:** Server becomes unresponsive or operations fail to complete

**Diagnosis:**

```bash
# Check available memory
free -h
```

Expected output:

```
              total        used        free      shared  buff/cache   available
Mem:           7.7G        3.2G        1.5G         200M        3.0G        4.0G
Swap:          2.0G        100M        1.9G
```

**Warning Thresholds:**
- Available < 1GB: Reduce concurrent operations
- Available < 500MB: Stop operations, restart server

**Solutions:**

1. **Reduce concurrent operations:**
   - Limit to 2-3 simultaneous operations
   - Wait for operations to complete before starting new ones

2. **Restart services:**
   ```bash
   ../scripts/tl-shutdown.sh
   sleep 10
   ../scripts/tl-startup.sh
   ```

3. **Disable unused plugins:**
   ```yaml
   # conf/local.yml
   plugins:
     - magma
     - sandcat
     - stockpile
     - orchestrator
     # Comment out unused plugins
     # - atomic
     # - emu
   ```

4. **Add swap space:**
   ```bash
   # Create 4GB swap file
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # Make permanent
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

### Disk Space Issues

**Symptom:** "No space left on device" errors

**Diagnosis:**

```bash
df -h
```

**Solutions:**

1. **Clean log files:**
   ```bash
   # Remove old logs
   sudo journalctl --vacuum-time=7d
   
   # Clean Caldera logs
   cd /path/to/caldera
   rm -f logs/*.log.1
   rm -f logs/*.log.2
   ```

2. **Remove old operation results:**
   ```bash
   cd /path/to/caldera
   rm -rf data/results/*
   ```

3. **Clean package cache:**
   ```bash
   sudo apt-get clean
   sudo apt-get autoclean
   ```

4. **Find large files:**
   ```bash
   sudo du -h /var | sort -rh | head -20
   ```

## Service Start Failures

### Port Already in Use

**Symptom:** "Address already in use" or "Port 8888 is already allocated"

**Diagnosis:**

```bash
# Check what's using port 8888
sudo lsof -i :8888

# Or with netstat
sudo netstat -tulpn | grep 8888
```

**Solutions:**

1. **Kill existing Caldera process:**
   ```bash
   pkill -f "python.*server.py"
   
   # Force kill if needed
   pkill -9 -f "python.*server.py"
   ```

2. **Kill process by PID:**
   ```bash
   # Get PID from lsof output
   sudo kill -9 <PID>
   ```

3. **Use different port:**
   ```yaml
   # conf/local.yml
   app.contact.http:
     - 0.0.0.0:8889  # Changed from 8888
   ```

### Elasticsearch Won't Start

**Symptom:** `systemctl status elasticsearch` shows failed state

**Diagnosis:**

```bash
# Check logs
sudo journalctl -u elasticsearch -n 50

# Check configuration
sudo /usr/share/elasticsearch/bin/elasticsearch --version
```

**Common Causes and Solutions:**

1. **Out of disk space:**
   ```bash
   df -h
   # Clean up space as described above
   ```

2. **Configuration error:**
   ```bash
   # Validate configuration
   sudo /usr/share/elasticsearch/bin/elasticsearch-keystore list
   
   # Reset to defaults
   sudo cp /etc/elasticsearch/elasticsearch.yml.bak /etc/elasticsearch/elasticsearch.yml
   ```

3. **Insufficient memory:**
   ```bash
   # Reduce heap size for constrained environments
   sudo vim /etc/elasticsearch/jvm.options
   # Change:
   # -Xms4g to -Xms2g
   # -Xmx4g to -Xmx2g
   
   sudo systemctl restart elasticsearch
   ```

4. **Permission issues:**
   ```bash
   # Fix ownership
   sudo chown -R elasticsearch:elasticsearch /var/lib/elasticsearch
   sudo chown -R elasticsearch:elasticsearch /var/log/elasticsearch
   
   sudo systemctl restart elasticsearch
   ```

### Kibana Won't Start

**Symptom:** `systemctl status kibana` shows failed state

**Diagnosis:**

```bash
# Check logs
sudo journalctl -u kibana -n 50

# Check Kibana log file
sudo tail -100 /var/log/kibana/kibana.log
```

**Solutions:**

1. **Elasticsearch not running:**
   ```bash
   # Ensure Elasticsearch is running first
   sudo systemctl status elasticsearch
   sudo systemctl start elasticsearch
   
   # Wait for Elasticsearch to be ready
   sleep 10
   
   # Start Kibana
   sudo systemctl start kibana
   ```

2. **Connection refused:**
   ```bash
   # Verify Elasticsearch URL in config
   sudo grep elasticsearch.hosts /etc/kibana/kibana.yml
   
   # Should be: ["http://localhost:9200"]
   ```

3. **Permission issues:**
   ```bash
   sudo chown -R kibana:kibana /var/lib/kibana
   sudo chown -R kibana:kibana /var/log/kibana
   
   sudo systemctl restart kibana
   ```

## Caldera Server Issues

### UI Shows "Loading..." Indefinitely

**Symptom:** Web interface stuck on loading screen

**Diagnosis:**

```bash
# Check browser console for errors (F12 in browser)
# Check Caldera logs
tail -f logs/*.log
```

**Solutions:**

1. **Clear browser cache:**
   - Chrome/Edge: Ctrl+Shift+Delete → Clear cached images and files
   - Firefox: Ctrl+Shift+Delete → Cache

2. **Force reload:**
   - Chrome/Edge: Ctrl+Shift+R
   - Firefox: Ctrl+F5

3. **Rebuild UI:**
   ```bash
   cd plugins/magma
   npm install
   npm run build
   
   cd ../..
   python3 server.py --build
   ```

4. **Check authentication:**
   ```bash
   # Verify credentials in conf/local.yml
   grep -A 5 "users:" conf/local.yml
   ```

### API Endpoints Not Responding

**Symptom:** `curl http://localhost:8888/api/v2/health` fails or times out

**Diagnosis:**

```bash
# Check if server is running
lsof -ti:8888

# Check server logs for errors
tail -50 logs/*.log | grep -i error

# Test localhost connectivity
curl -v http://localhost:8888/api/v2/health
```

**Solutions:**

1. **Server not started:**
   ```bash
   ../scripts/tl-startup.sh
   ```

2. **Firewall blocking:**
   ```bash
   # Check firewall status
   sudo ufw status
   
   # Allow port 8888
   sudo ufw allow 8888/tcp
   ```

3. **Restart server:**
   ```bash
   pkill -f "python.*server.py"
   python3 server.py --insecure --log DEBUG
   ```

### Python Import Errors

**Symptom:** "ModuleNotFoundError" or "ImportError" when starting server

**Diagnosis:**

```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list

# Verify virtual environment
which python3
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Reinstall dependencies:**
   ```bash
   pip3 install -r requirements.txt
   
   # Force reinstall
   pip3 install -r requirements.txt --force-reinstall
   ```

3. **Create new virtual environment:**
   ```bash
   deactivate
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```

## Agent Deployment Issues

### Agent Not Appearing in UI

**Symptom:** Agent deployed but not visible in Campaigns → Agents

**Diagnosis:**

```bash
# Check if agent process is running on target
# Windows:
tasklist | findstr sandcat

# Linux:
ps aux | grep sandcat

# Check Caldera logs for beacon
grep -i beacon logs/*.log | tail -20
```

**Solutions:**

1. **Firewall blocking agent beacons:**
   ```bash
   # On Caldera server
   sudo ufw allow 8888/tcp
   
   # On target (Windows)
   netsh advfirewall firewall add rule name="Caldera Agent" dir=in action=allow protocol=TCP localport=8888
   ```

2. **Wrong server address:**
   - Verify agent one-liner uses correct server IP
   - Use external IP, not 127.0.0.1 or localhost

3. **Agent crashed:**
   - Check target system logs
   - Restart agent manually
   - Verify platform matches (Windows agent on Windows, etc.)

4. **Contact method mismatch:**
   ```yaml
   # conf/local.yml - Ensure HTTP contact enabled
   app.contact.http:
     - 0.0.0.0:8888
   ```

### Agent Execution Fails

**Symptom:** Operation stuck at 0% or abilities fail immediately

**Diagnosis:**

```bash
# Check operation status
curl http://localhost:8888/api/v2/operations/<OP_ID> | jq '.state'

# Check link status
curl http://localhost:8888/api/v2/operations/<OP_ID>/links | jq '.[].status'
```

**Solutions:**

1. **No matching abilities:**
   - Verify agent platform matches ability requirements
   - Windows abilities require Windows agent
   - Check ability executor (psh, cmd, sh, bash)

2. **Privilege issues:**
   - Some abilities require administrator/root
   - Redeploy agent with elevated privileges

3. **Antivirus blocking:**
   - Add Caldera to antivirus exclusions
   - Use obfuscator to evade detection

4. **Operation planner issue:**
   ```yaml
   # Use atomic planner for sequential execution
   # When creating operation, select: atomic
   ```

## ELK Integration Issues

### Orchestrator Not Tagging

**Symptom:** Operations run but no logs in Elasticsearch

**Diagnosis:**

```bash
# Check environment variables
echo "ELK_URL: $ELK_URL"
echo "ELK_USER: $ELK_USER"
echo "ELK_PASS: ${ELK_PASS:0:5}..."

# Check orchestrator status
curl http://localhost:8888/plugin/orchestrator/status | python3 -m json.tool

# Check Caldera logs
grep -i "orchestrator\|ELK" logs/*.log | tail -20

# Check fallback logs
ls -lh plugins/orchestrator/data/fallback_logs/
```

**Solutions:**

1. **Environment variables not set:**
   ```bash
   # Source credentials before starting Caldera
   source .env.elk
   python3 server.py --insecure --log INFO
   ```

2. **Orchestrator plugin not loaded:**
   ```yaml
   # conf/local.yml
   plugins:
     - orchestrator  # Ensure this is listed
   ```

3. **ELK authentication failure:**
   ```bash
   # Test credentials manually
   curl -u "elastic:YOUR_PASSWORD" "http://20.28.49.97:9200/_cluster/health"
   
   # If successful, credentials are correct
   ```

4. **Circuit breaker open:**
   ```bash
   # Restart Caldera to reset circuit breaker
   pkill -f "python.*server.py"
   source .env.elk
   python3 server.py --insecure --log INFO
   ```

### Authentication Errors

**Symptom:** `"elk.status": "error"` or `"401 Unauthorized"`

**Diagnosis:**

```bash
# Verify Elasticsearch is accessible
curl -u "elastic:password" "http://20.28.49.97:9200/_cluster/health"

# Check for typos in credentials
cat .env.elk
```

**Solutions:**

1. **Incorrect credentials:**
   - Verify username and password
   - Check for special characters needing escaping
   - Ensure no trailing spaces in .env.elk

2. **API key expired:**
   - Generate new API key in Kibana
   - Update .env.elk with new key

3. **Elasticsearch authentication disabled:**
   ```yaml
   # /etc/elasticsearch/elasticsearch.yml
   xpack.security.enabled: true
   ```

### Index Pattern Mismatch

**Symptom:** Tags sent but queries return no results

**Diagnosis:**

```bash
# Check actual index names
curl -u elastic:password "http://20.28.49.97:9200/_cat/indices?v" | grep -i log

# Check configured index
grep elk_index conf/local.yml
```

**Solutions:**

1. **Update index pattern:**
   ```yaml
   # conf/local.yml
   plugins:
     orchestrator:
       elk_index: "winlogbeat-*"  # Match actual index
   ```

2. **Create missing index:**
   ```bash
   curl -u elastic:password -X PUT "http://20.28.49.97:9200/purple-team-logs"
   ```

## Docker Deployment Issues

### Container Fails to Start

**Symptom:** `docker-compose up` exits immediately

**Diagnosis:**

```bash
# Check container logs
docker logs caldera

# Check container status
docker ps -a
```

**Solutions:**

1. **Port conflict:**
   ```bash
   # Find process using port
   sudo lsof -i :8888
   
   # Change port in docker-compose.yml
   ports:
     - "8889:8888"
   ```

2. **Build failed:**
   ```bash
   # Rebuild with no cache
   docker-compose build --no-cache
   ```

3. **Permission denied:**
   ```bash
   # Fix volume permissions
   sudo chown -R $USER:$USER .
   ```

### Network Connectivity in Containers

**Symptom:** Container cannot reach Elasticsearch or other services

**Diagnosis:**

```bash
# Test from inside container
docker exec caldera curl http://elasticsearch:9200

# Check network
docker network inspect caldera_default
```

**Solutions:**

1. **Use service names:**
   ```bash
   # In .env or docker-compose.yml
   ELK_URL=http://elasticsearch:9200  # Use service name, not localhost
   ```

2. **Create custom network:**
   ```yaml
   # docker-compose.yml
   networks:
     - caldera-net
   
   networks:
     caldera-net:
       driver: bridge
   ```

3. **Use host network (Linux only):**
   ```yaml
   # docker-compose.yml
   network_mode: host
   ```

### Volume Mount Issues

**Symptom:** Changes to files not reflected in container

**Diagnosis:**

```bash
# Check volume mounts
docker inspect caldera | grep -A 10 Mounts
```

**Solutions:**

1. **Rebuild container:**
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Verify volume path:**
   ```yaml
   # docker-compose.yml
   volumes:
     - ./conf:/usr/src/app/conf  # Use absolute paths if needed
   ```

## Network and Connectivity

### Cannot Access Web Interface Remotely

**Symptom:** Caldera accessible on localhost but not from remote machines

**Diagnosis:**

```bash
# Check listening address
netstat -tulpn | grep 8888

# Should show 0.0.0.0:8888, not 127.0.0.1:8888
```

**Solutions:**

1. **Configure bind address:**
   ```yaml
   # conf/local.yml
   app.contact.http:
     - 0.0.0.0:8888  # Not 127.0.0.1
   ```

2. **Firewall rules:**
   ```bash
   # Allow access from specific IP
   sudo ufw allow from 192.168.1.0/24 to any port 8888
   
   # Or allow all (not recommended for production)
   sudo ufw allow 8888/tcp
   ```

3. **Cloud provider security groups:**
   - Add inbound rule for port 8888
   - Allow TCP from source IP range

### DNS Resolution Failures

**Symptom:** "Name or service not known" errors

**Diagnosis:**

```bash
# Test DNS resolution
nslookup elasticsearch
dig elasticsearch

# Check /etc/hosts
cat /etc/hosts
```

**Solutions:**

1. **Add to hosts file:**
   ```bash
   sudo echo "20.28.49.97 elasticsearch" >> /etc/hosts
   ```

2. **Use IP addresses:**
   ```bash
   export ELK_URL="http://20.28.49.97:9200"  # Use IP instead of hostname
   ```

## Performance Issues

### Slow Operation Execution

**Symptom:** Operations take much longer than expected

**Diagnosis:**

```bash
# Check system load
top
htop

# Check I/O wait
iostat -x 1 5

# Check network latency
ping <target-ip>
```

**Solutions:**

1. **Reduce concurrent operations:**
   - Limit to 2-3 operations simultaneously
   - Wait for completion before starting new ones

2. **Optimise planner settings:**
   ```yaml
   # Use atomic planner for predictable execution
   # Avoid bucket planner in constrained environments
   ```

3. **Check network latency:**
   - High latency between Caldera and agents slows execution
   - Consider deploying Caldera closer to targets

### High Memory Usage

**Symptom:** Server consuming excessive memory

**Diagnosis:**

```bash
# Check process memory
ps aux --sort=-%mem | head -10

# Monitor memory over time
watch -n 1 free -h
```

**Solutions:**

1. **Restart server:**
   ```bash
   ../scripts/tl-shutdown.sh
   ../scripts/tl-startup.sh
   ```

2. **Disable unused plugins:**
   - Comment out plugins in conf/local.yml
   - Reduce plugin overhead

3. **Clear operation cache:**
   ```bash
   rm -rf data/results/*
   ```

## Debugging Techniques

### Enable Debug Logging

```bash
# Start with debug logging
python3 server.py --insecure --log DEBUG

# Or modify conf/local.yml
logging:
  level: DEBUG
```

### Tail All Logs

```bash
# Monitor all log files
tail -f logs/*.log

# Filter for specific plugin
tail -f logs/*.log | grep orchestrator
```

### Python Debugging

```python
# Add to code for interactive debugging
import pdb; pdb.set_trace()
```

### Network Traffic Analysis

```bash
# Capture HTTP traffic
sudo tcpdump -i any -A port 8888

# Monitor agent beacons
sudo tcpdump -i any -A port 8888 | grep -i beacon
```

## Diagnostic Scripts

### Complete Health Check

```bash
#!/bin/bash
echo "=== System Resources ==="
free -h
df -h

echo -e "\n=== Service Status ==="
systemctl is-active elasticsearch kibana logstash elastic-agent

echo -e "\n=== Network Connectivity ==="
nc -zv localhost 9200
nc -zv localhost 5601
nc -zv localhost 8888

echo -e "\n=== Caldera Status ==="
curl -s http://localhost:8888/api/v2/health | jq

echo -e "\n=== Orchestrator Status ==="
curl -s http://localhost:8888/plugin/orchestrator/status | jq

echo -e "\n=== ELK Connection ==="
curl -s -u elastic:password http://20.28.49.97:9200/_cluster/health | jq
```

### Environment Verification

```bash
#!/bin/bash
echo "=== Environment Variables ==="
echo "ELK_URL: ${ELK_URL:-NOT SET}"
echo "ELK_USER: ${ELK_USER:-NOT SET}"
echo "ELK_PASS: ${ELK_PASS:+CONFIGURED}"

echo -e "\n=== Python Environment ==="
which python3
python3 --version
pip3 --version

echo -e "\n=== Virtual Environment ==="
echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-NOT ACTIVATED}"

echo -e "\n=== Configuration Files ==="
ls -lh conf/local.yml .env.elk 2>/dev/null || echo "Config files missing"
```

## Getting Help

### Log Collection

When reporting issues, collect diagnostic information:

```bash
# Create diagnostic bundle
tar czf caldera-diagnostic.tar.gz \
  logs/*.log \
  conf/local.yml \
  /tmp/tl-startup.log \
  /tmp/tl-shutdown.log \
  plugins/orchestrator/data/fallback_logs/

# Sanitise sensitive data before sharing
```

### Common Information Needed

When seeking help, provide:

1. Caldera version: `git describe --tags`
2. Python version: `python3 --version`
3. Operating system: `uname -a`
4. Error messages from logs
5. Steps to reproduce issue
6. Recent configuration changes

### Community Resources

- GitHub Issues: Report bugs and feature requests
- Documentation: Reference official guides
- Security Issues: security@triskelelabs.com (for security vulnerabilities)

## Prevention Checklist

Avoid common issues by following these practices:

- [ ] Always use startup scripts for consistent state
- [ ] Check status after startup with `tl-status.sh`
- [ ] Monitor system resources regularly
- [ ] Keep 4GB+ RAM free for smooth operation
- [ ] Use graceful shutdown before VM reboot
- [ ] Update regularly with `git pull`
- [ ] Review logs for warnings
- [ ] Backup configuration files
- [ ] Test ELK connectivity before operations
- [ ] Document custom configuration changes

## Next Steps

- [Local Deployment](local-deployment.md) - Deploy Caldera locally
- [Docker Deployment](docker-deployment.md) - Deploy with containers
- [ELK Integration](elk-integration.md) - Configure SIEM tagging

## See Also

- [Configuration Guide](../getting-started/configuration.md)
- [TL Scripts README](../guides/TL_SCRIPTS_README.md)
- [Orchestrator Troubleshooting](../plugins/orchestrator-troubleshooting.md)
- [Purple Team User Guide](../PURPLE_TEAM_USER_GUIDE.md)
