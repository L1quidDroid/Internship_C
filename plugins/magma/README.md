# Magma Plugin

The UI/UX Vue.js framework for Caldera 5.

## Overview

Magma is the modern web interface for MITRE Caldera 5, built with Vue.js. It provides a responsive, intuitive user experience for managing operations, agents, adversaries, and other Caldera resources.

### Features

- **Modern UI**: Vue.js-based responsive interface
- **Hot Reloading**: Development mode with automatic updates
- **Accessibility**: Jest-axe accessibility testing
- **Code Quality**: ESLint integration for code standards
- **Component Testing**: Jest testing framework

## Prerequisites

```bash
# Required
- Node.js 20.19+ (recommended)
- Caldera 5.0.0+
- npm (comes with Node.js)
```

## Installation

### Production Use

If running Magma without development:

```bash
# In the Caldera directory
python3 server.py --build
```

The `--build` flag automatically:
- Installs dependencies
- Bundles the Vue frontend into dist directory
- Serves the bundled application via Caldera server

You will only need to use the `--build` flag again if you add plugins.

### Development

To serve the UI in development environment with hot-reloading:

```bash
# In the magma directory
npm install
npm run build

# In the Caldera directory
python3 server.py --uidev localhost
```

Access the UI at http://localhost:3000

## Configuration

```yaml
# conf/local.yml
plugins:
  - magma
```

## Usage

### Production Mode

```bash
# Build and serve
python3 server.py --build

# Access UI
# Navigate to http://localhost:8888
```

### Development Mode

```bash
# Start development server
cd plugins/magma
npm run build

# In separate terminal, start Caldera
cd ../..
python3 server.py --uidev localhost

# Access development UI
# Navigate to http://localhost:3000
```

## Testing

### Run All Tests

```bash
npm run test-all
```

### Run Accessibility Tests Only

```bash
npm run test-accessibility
```

Magma uses Jest-axe for accessibility testing, which adheres to axe-core rules. Each rule can be modified or disabled when calling the axe function.

### Code Quality

Run linting manually:

```bash
# Check for issues
npm run lint

# Auto-fix issues
npm run lintfix
```

## File Structure

```
plugins/magma/
├── package.json           # Node.js dependencies
├── README.md             # This file
├── src/
│   ├── components/       # Vue components
│   ├── tests/           # Jest tests
│   └── [vue-app-files]  # Vue application source
└── dist/                # Production build output (generated)
```

## Troubleshooting

### Build Fails

**Symptom**: npm run build returns errors

**Fix**:
- Verify Node.js version (20.19+ recommended)
- Delete node_modules and run npm install again
- Check for conflicting dependencies
- Review build logs for specific errors

### Development Server Not Starting

**Symptom**: Cannot access http://localhost:3000

**Fix**:
- Verify port 3000 is not in use
- Check npm run build completed successfully
- Ensure Caldera is running with --uidev flag
- Review terminal for error messages

### Hot Reloading Not Working

**Symptom**: Changes not reflected in browser

**Fix**:
- Verify development mode is active
- Check webpack configuration
- Clear browser cache
- Restart development server

### Accessibility Test Failures

**Symptom**: Jest-axe tests failing

**Fix**:
- Review axe-core rule violations in test output
- Update components to meet accessibility standards
- Adjust axe configuration if specific rules need modification
- Consult axe-core documentation for rule details

## Performance

| Metric | Consideration |
|--------|---------------|
| Build Time | Varies by system, typically 1-2 minutes |
| Bundle Size | Optimised for production |
| Load Time | Fast initial load with code splitting |

## Contributing

Contributions to improve the UI/UX are welcome. Follow the linting and testing guidelines when submitting changes.

## Licence

Follows MITRE Caldera licensing (Apache 2.0)

## Acknowledgements

- **MITRE Caldera Team**: For the excellent framework
- **Vue.js Community**: For the robust frontend framework
- **Jest and axe-core**: For testing and accessibility tools
