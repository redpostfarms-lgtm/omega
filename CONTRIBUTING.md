# Contributing to Omega Gatekeeper

Thank you for your interest in contributing to the Omega Gatekeeper project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct that promotes a welcoming and inclusive environment. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/omega.git`
3. Add upstream remote: `git remote add upstream https://github.com/redpostfarms-lgtm/omega.git`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.9 or higher (3.11 recommended)
- Git
- Virtual environment tool (venv, conda, etc.)

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

## Making Changes

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Test your changes** thoroughly

4. **Commit your changes** with clear, descriptive messages

## Testing

Run the test suite before submitting:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_specific.py

# Run with markers
pytest -m "not slow"
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the existing test structure

## Code Style

We use automated tools to maintain code quality:

### Python

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .

# Run all checks
black . && ruff check . && mypy .
```

### Style Guidelines

- Use type hints for function signatures
- Write docstrings for public functions/classes
- Follow PEP 8 naming conventions
- Keep functions focused and single-purpose
- Use meaningful variable names

## Commit Guidelines

We follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(swarm): add heartbeat monitoring system

Implement WebSocket-based heartbeat system for drone monitoring
with automatic reconnection and status tracking.

Closes #123
```

```bash
fix(ci): resolve cache-dependency-path configuration

Update GitHub Actions workflow to support multiple requirements
files with proper fallback logic.
```

## Pull Request Process

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/examples if applicable
   - Test results

4. **Address review feedback** promptly

5. **Ensure CI passes** before requesting final review

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] CI/CD pipeline passes

## Questions or Issues?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Contact maintainers for urgent matters

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Omega Gatekeeper! 🚀
