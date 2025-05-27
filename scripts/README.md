# Linting and Code Quality Tools

This directory contains scripts and configuration for maintaining code quality in the MCP Test project.

## Quick Start

### Using Make (Recommended)

```bash
# See all available commands
make help

# Run all linting checks
make lint

# Automatically fix linting issues
make fix-lint

# Complete development setup
make all
```

### Using Scripts Directly

```bash
# Run comprehensive linting checks
./scripts/lint.sh

# Automatically fix most linting issues
./scripts/fix-lint.sh
```

## Available Tools

### Makefile Targets

| Command | Description |
|---------|-------------|
| `make lint` | Run all linting checks without fixing |
| `make fix-lint` | Automatically fix linting issues |
| `make format` | Format code with black |
| `make check-format` | Check if code is properly formatted |
| `make type-check` | Run mypy type checking |
| `make test` | Run test suite |
| `make coverage` | Run tests with coverage report |
| `make clean` | Clean up generated files |
| `make all` | Install deps, fix lint, run tests |

### Linting Tools Used

1. **flake8** - PEP 8 style guide enforcement
2. **black** - Code formatting
3. **isort** - Import sorting
4. **autopep8** - Automatic PEP 8 fixes
5. **pyflakes** - Detect unused imports and undefined names
6. **mypy** - Static type checking

### Configuration Files

- `.flake8` - flake8 configuration
- `pyproject.toml` - Project configuration including tool settings

## Workflow Integration

### Pre-commit Workflow

```bash
# Before committing changes
make pre-commit
```

### CI/CD Integration

```bash
# For continuous integration
make ci
```

### Development Setup

```bash
# Initial setup for new developers
make setup
```

## Configuration Details

### Line Length

- Maximum line length: 88 characters (black compatible)
- Configured in `.flake8` and used consistently across all tools

### Ignored Rules

- E203: whitespace before ':' (conflicts with black)
- W503: line break before binary operator (conflicts with black)
- E501: line too long (handled by black)

### Import Organization

- Imports are automatically sorted by isort
- Standard library imports first
- Third-party imports second
- Local imports last

## Troubleshooting

### Common Issues

1. **Permission Denied on Scripts**

   ```bash
   chmod +x scripts/*.sh
   ```

2. **Missing Dependencies**

   ```bash
   make install-dev
   ```

3. **Conflicting Tool Outputs**
   Run `make fix-lint` to resolve most conflicts automatically.

### Manual Fixes

Some linting issues may require manual intervention:

- Complex logical errors
- Type annotation issues
- Architectural problems

## Adding New Linting Rules

1. Update `.flake8` configuration
2. Modify `scripts/lint.sh` for new checks
3. Update `scripts/fix-lint.sh` for automatic fixes
4. Add new Make targets if needed

## Performance Tips

- Use `make lint` for quick checks during development
- Use `make fix-lint` before committing
- Use `make all` for comprehensive validation
