# Atomic Plugin

A plugin supplying Caldera with TTPs from the Atomic Red Team project.

## Overview

The Atomic Plugin integrates Atomic Red Team tests into MITRE Caldera, providing a comprehensive library of attack techniques for purple team operations. It automatically imports Atomic Red Team test definitions and converts them into Caldera abilities.

### Features

- **Atomic Red Team Integration**: Imports TTPs from the Atomic Red Team project
- **Automatic Payload Handling**: Catches PathToAtomicsFolder usages and imports files as payloads
- **Tactic Mapping**: Creates mappings and imports abilities under corresponding tactics
- **Path Fixing**: Automatically fixes path usages for imported files

## Prerequisites

```bash
# Required
- Python 3.10+
- Caldera 5.x
- Atomic Red Team repository

# Optional
- Git (for cloning Atomic Red Team)
```

## Installation

```bash
# 1. Plugin is already in plugins/atomic/

# 2. Enable plugin in conf/local.yml
plugins:
  - atomic

# 3. Start Caldera
python server.py --insecure

# 4. Verify plugin loaded
grep "atomic" logs/caldera.log
```

## Configuration

Configuration options for importing Atomic Red Team tests.

```yaml
# conf/local.yml
plugins:
  - atomic
```

## Usage

### Importing Atomic Red Team Tests

The plugin automatically imports Atomic Red Team tests when enabled. Tests are converted to Caldera abilities and organised by tactic.

### Path Handling

When importing tests from Atomic Red Team, the plugin handles `$PathToAtomicsFolder` usages:

- If the path points to an existing file, it imports the file as a payload and fixes path usages
- If the path points to a directory or non-existent file, it ingests the usage as-is without processing

### Tactic Mapping

ART tests specify techniques they address. The plugin creates mappings and imports abilities under corresponding tactics. When multiple tactics match and the specific tactic is unclear, abilities are categorised under a "multiple" tactic category.

## Known Issues

- When a command or cleanup expands over multiple lines with one of them being a comment, it can disrupt the command or cleanup (as multiple lines are reduced into one with semi-colons)
- Some PathToAtomicsFolder usages pointing to directories or non-existent files are not processed further

## File Structure

```
plugins/atomic/
├── hook.py                 # Plugin registration
├── README.md              # This file
└── app/
    └── [service-files]    # Import and processing logic
```

## Troubleshooting

### Import Fails

**Symptom**: Atomic Red Team tests not importing

**Fix**:
- Verify Atomic Red Team repository is accessible
- Check Caldera logs for import errors
- Ensure plugin is enabled in conf/local.yml

### Path Resolution Issues

**Symptom**: PathToAtomicsFolder not resolving correctly

**Fix**:
- Check that referenced files exist in Atomic Red Team repository
- Verify file paths are correct in test definitions
- Review logs for path resolution warnings

## Contributing

Contributions to improve Atomic Red Team integration are welcome. Contact your Caldera administrator for enhancement requests.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Acknowledgements

- **Atomic Red Team**: For the comprehensive TTP library (https://github.com/redcanaryco/atomic-red-team)
- **AtomicCaldera**: For integration inspiration (https://github.com/xenoscr/atomiccaldera)
- **MITRE Caldera Team**: For the excellent framework
