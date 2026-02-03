# Contributing Guidelines

## Reporting Issues

When reporting issues, please provide:

* Detailed description of what should have happened
* Supporting information (stack traces, errors, logs)
* Steps to replicate the issue
* Operating system and Python version

## Development Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/L1quidDroid/Internship_C.git --recursive
cd command-center
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install --install-hooks
```

## Development Workflow

We use the feature branch Git flow:

1. Fork this repository
2. Create a feature branch from master
3. Make your changes with descriptive commits
4. Submit a merge request

**Guidelines:**
* Each merge request should solve one problem
* Branch names and commits should be descriptive
* Tests must cover all code changes
* New tests should fail without your patch

## Running Tests

### Run All Tests

```bash
python -m pytest --asyncio-mode=auto
```

This runs all unit tests in your current development environment.

### Run Tests Across Multiple Python Versions

We use `tox` to test across multiple Python versions:

```bash
tox
```

This will only run if the required Python interpreters are installed on your system.

## Code Coverage

### Generate Coverage Reports

```bash
coverage run -m pytest
coverage report
coverage html
```

View the coverage report: `htmlcov/index.html`

## Code Quality Standards

* Follow PEP 8 style guidelines
* Use Australian English spelling in documentation
* Write clear, descriptive commit messages
* Include docstrings for all public functions and classes
* Ensure all tests pass before submitting pull requests

## See Also

- [Testing Guide](development/testing.md) - Comprehensive testing documentation
- [Plugin Development](development/plugin-development.md) - Creating custom plugins
- [Architecture Overview](architecture/system-overview.md) - Understanding the codebase