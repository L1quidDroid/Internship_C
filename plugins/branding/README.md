# Branding Plugin

Custom branding and visual customisation for MITRE Caldera.

## Overview

The Branding Plugin allows organisations to customise the visual appearance of their Caldera installation, including logos, colours, and other branding elements.

### Features

- **Custom Logos**: Replace default Caldera branding with organisational logos
- **Colour Schemes**: Customise interface colours to match corporate branding
- **Static Assets**: Manage custom static files for branding

## Prerequisites

```bash
# Required
- Python 3.10+
- Caldera 5.x
```

## Installation

```bash
# 1. Plugin is already in plugins/branding/

# 2. Enable plugin in conf/local.yml
plugins:
  - branding

# 3. Start Caldera
python server.py --insecure

# 4. Verify plugin loaded
grep "branding" logs/caldera.log
```

## Configuration

Place custom branding assets in the plugin's static directory.

```yaml
# conf/local.yml
plugins:
  - branding
```

## Usage

### Adding Custom Logo

1. Place your logo file in `plugins/branding/static/`
2. Configure logo path in Caldera settings
3. Restart Caldera to apply changes

### Customising Colours

Update colour schemes through plugin configuration to match your organisational branding.

## File Structure

```
plugins/branding/
├── hook.py                 # Plugin registration
├── README.md              # This file
├── __init__.py            # Package metadata
└── static/                # Custom branding assets
```

## Troubleshooting

### Branding Not Appearing

**Symptom**: Custom branding not visible in interface

**Fix**:
- Clear browser cache
- Verify assets are in correct directory
- Check file permissions on static assets
- Restart Caldera

### Logo Not Displaying

**Symptom**: Logo file not showing

**Fix**:
- Verify file format is supported (PNG, SVG, JPG)
- Check file path configuration
- Ensure file size is reasonable (less than 1 MB recommended)

## Contributing

Contributions for additional branding features are welcome. Contact your Caldera administrator for enhancement requests.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Acknowledgements

- **MITRE Caldera Team**: For the extensible framework
