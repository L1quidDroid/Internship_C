# Sandcat Plugin

The default cross-platform agent for MITRE Caldera operations.

## Overview

Sandcat is the default agent plugin for Caldera, providing a lightweight, cross-platform implant for executing adversary operations. Written in Go, Sandcat supports Windows, Linux, and macOS platforms.

### Features

- **Cross-Platform**: Supports Windows, Linux, and macOS
- **Lightweight**: Minimal resource footprint
- **Extensible**: Support for agent extensions
- **Reliable**: Production-tested in numerous operations
- **Beacon-Based**: Configurable beacon intervals for C2 communication

## Prerequisites

```bash
# For using pre-built agents
- Caldera 5.x
- Target system (Windows, Linux, or macOS)

# For building from source
- Go 1.19+
- Make (for build automation)
```

## Installation

```bash
# 1. Plugin is already in plugins/sandcat/

# 2. Enable plugin in conf/local.yml
plugins:
  - sandcat

# 3. Start Caldera
python server.py --insecure

# 4. Download agents from Caldera UI
# Navigate to Agents tab -> Download Sandcat
```

## Configuration

```yaml
# conf/local.yml
plugins:
  - sandcat

# Optional: Configure default beacon interval
sandcat:
  beacon_interval: 60  # seconds
```

## Usage

### Deploying Agents

1. **Download Agent**: From Caldera UI, navigate to Agents and select appropriate platform
2. **Transfer to Target**: Copy agent binary to target system
3. **Execute Agent**: Run the agent with appropriate permissions
4. **Verify Connection**: Agent should beacon back to Caldera

### Platform-Specific Deployment

#### Windows

```powershell
# Download and execute
.\sandcat.exe -server http://caldera-server:8888
```

#### Linux/macOS

```bash
# Download and execute
chmod +x sandcat
./sandcat -server http://caldera-server:8888
```

### Agent Extensions

Sandcat supports extensions for additional capabilities. Extensions are built separately and loaded at runtime.

## Building from Source

```bash
# Navigate to sandcat directory
cd plugins/sandcat

# Build for all platforms
make build

# Build for specific platform
make build-windows
make build-linux
make build-darwin
```

## File Structure

```
plugins/sandcat/
├── hook.py                 # Plugin registration
├── README.md              # This file
├── Makefile               # Build automation
├── app/
│   └── [agent-code]       # Go source code
├── payloads/
│   └── [compiled-agents]  # Pre-built binaries
└── gocat/
    └── [extensions]       # Agent extensions
```

## Troubleshooting

### Agent Not Beaconing

**Symptom**: Agent does not appear in Caldera UI

**Fix**:
- Verify Caldera server URL is correct
- Check network connectivity from target to Caldera
- Ensure firewall allows outbound connections
- Verify agent has execution permissions
- Check agent logs for error messages

### Build Failures

**Symptom**: Make build fails

**Fix**:
- Verify Go is installed (go version)
- Check Go version is 1.19 or higher
- Ensure all dependencies are available
- Review build logs for specific errors

### Agent Crashes

**Symptom**: Agent terminates unexpectedly

**Fix**:
- Check target system logs
- Verify sufficient permissions for operation
- Ensure beacon interval is appropriate
- Review Caldera logs for errors

### Extension Loading Issues

**Symptom**: Extensions not loading

**Fix**:
- Verify extension compatibility with Sandcat version
- Check extension is in correct directory
- Ensure extension is built for correct platform
- Review extension logs for errors

## Security Considerations

- **Transport Encryption**: Use HTTPS for C2 communication in production
- **Agent Permissions**: Run with minimum required privileges
- **Beacon Jitter**: Configure jitter to avoid detection patterns
- **Cleanup**: Ensure proper cleanup after operations

## Performance

| Metric | Typical Value |
|--------|---------------|
| Memory Usage | 10-20 MB |
| CPU Usage | Less than 1% idle |
| Beacon Overhead | Minimal network traffic |
| Startup Time | Less than 1 second |

## Contributing

Contributions to improve Sandcat are welcome. For build workflow changes, refer to the GitHub Actions workflows.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Documentation

Full documentation available at: https://caldera.readthedocs.io/en/latest/Plugin-library.html#sandcat

## Acknowledgements

- **MITRE Caldera Team**: For the excellent framework
- **Go Community**: For the robust programming language
