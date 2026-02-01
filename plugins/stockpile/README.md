# Stockpile Plugin

A plugin supplying Caldera with TTPs and adversary profiles.

## Overview

Stockpile is the default TTP (Tactics, Techniques, and Procedures) library for MITRE Caldera, providing a comprehensive collection of abilities and adversary profiles for purple team operations. It includes abilities across the entire ATT&CK framework and pre-configured adversary profiles.

### Features

- **Comprehensive TTP Library**: Abilities covering all ATT&CK tactics
- **Adversary Profiles**: Pre-configured adversary emulation profiles
- **Collection and Exfiltration**: Advanced file search, compression, and exfiltration capabilities
- **Multi-Platform**: Abilities for Windows, Linux, and macOS
- **Cloud Integration**: AWS S3, Dropbox, and GitHub exfiltration support

## Prerequisites

```bash
# Required
- Python 3.10+
- Caldera 5.x

# Optional (for specific abilities)
- AWS CLI (for S3 exfiltration)
- Git (for GitHub exfiltration)
- FTP client (for FTP exfiltration)
```

## Installation

```bash
# 1. Plugin is already in plugins/stockpile/

# 2. Enable plugin in conf/local.yml
plugins:
  - stockpile

# 3. Start Caldera
python server.py --insecure

# 4. Verify plugin loaded
grep "stockpile" logs/caldera.log
```

## Configuration

```yaml
# conf/local.yml
plugins:
  - stockpile
```

## Usage

### Using Abilities

Abilities are automatically loaded and available in the Caldera UI. Select abilities when creating operations or use pre-configured adversary profiles.

### Adversary Profiles

Stockpile includes adversary profiles that chain abilities together to emulate real-world attack scenarios. Access these profiles in the Adversaries tab.

### Collection and Exfiltration Abilities

The plugin includes advanced collection and exfiltration abilities:

- **Advanced File Search and Stager**: Locate and stage files for exfiltration
- **Find Git Repositories**: Discover and compress Git repositories
- **Compress Staged Directory**: Password-protected compression
- **Split Archives**: Break large archives into smaller files
- **Exfiltration Methods**:
  - FTP exfiltration
  - Dropbox exfiltration
  - GitHub repository and Gist exfiltration
  - AWS S3 exfiltration and transfer
  - Scheduled exfiltration

For detailed configuration of collection and exfiltration abilities, refer to the examples in [docs/Exfiltration-How-Tos.md](docs/Exfiltration-How-Tos.md).

## File Structure

```
plugins/stockpile/
├── hook.py                 # Plugin registration
├── README.md              # This file
├── data/
│   ├── abilities/         # TTP definitions
│   ├── adversaries/       # Adversary profiles
│   ├── payloads/         # Supporting payloads
│   └── sources/          # Fact sources
└── docs/
    └── Exfiltration-How-Tos.md  # Exfiltration examples
```

## Known Issues

### ARM Architecture Limitation

The `donut-shellcode` Python package is not currently supported for ARM chip architectures. This package cannot be installed on newer Mac systems with M-series chips. Abilities requiring this package will not function on ARM systems.

## Troubleshooting

### Abilities Not Loading

**Symptom**: Stockpile abilities not appearing in UI

**Fix**:
- Verify plugin is enabled in conf/local.yml
- Check Caldera logs for parsing errors
- Ensure ability YAML files are valid
- Restart Caldera

### Exfiltration Abilities Failing

**Symptom**: Exfiltration to cloud services fails

**Fix**:
- Verify credentials are configured correctly
- Check network connectivity to destination
- Ensure required tools are installed (AWS CLI, git, etc.)
- Review ability configuration in docs/Exfiltration-How-Tos.md

### Payload Not Found

**Symptom**: Ability fails with payload not found error

**Fix**:
- Verify payload exists in data/payloads/
- Check payload file permissions
- Ensure payload is referenced correctly in ability definition
- Review Caldera logs for specific payload errors

## Security Considerations

- **Credential Management**: Use secure methods for storing cloud service credentials
- **Encryption**: Use password-protected archives for sensitive data
- **Network Security**: Be aware of exfiltration traffic patterns
- **Cleanup**: Ensure proper cleanup of staged files and exfiltrated data

## Performance

| Metric | Consideration |
|--------|---------------|
| Ability Execution | Varies by ability complexity |
| Compression Time | Depends on data size |
| Exfiltration Speed | Limited by network bandwidth |

## Documentation

Full documentation available at: https://github.com/mitre/caldera/wiki/Plugin:-stockpile

Additional examples for exfiltration abilities available in: [docs/Exfiltration-How-Tos.md](docs/Exfiltration-How-Tos.md)

## Contributing

Contributions of new abilities and adversary profiles are welcome. Follow existing ability formats when submitting new TTPs.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Acknowledgements

- **MITRE Caldera Team**: For the excellent framework
- **ATT&CK Team**: For the comprehensive framework
- **Community Contributors**: For additional abilities and profiles
