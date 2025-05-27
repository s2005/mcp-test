#!/bin/bash
# lint.sh - Comprehensive linting script for Python project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SRC_DIR="src"
TEST_DIR="tests"

echo -e "${BLUE}=== Python Linting Suite ===${NC}"
echo "Checking directories: $SRC_DIR/ $TEST_DIR/"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run linter with error handling
run_linter() {
    local linter_name="$1"
    local command="$2"
    
    echo -e "${YELLOW}Running $linter_name...${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ $linter_name passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $linter_name found issues${NC}"
        return 1
    fi
}

# Ensure we're in the project root
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}Error: pyproject.toml not found. Run this script from the project root.${NC}"
    exit 1
fi

# Install dev dependencies if needed
echo -e "${BLUE}Ensuring dev dependencies are installed...${NC}"
uv sync --group dev

echo -e "\n${BLUE}=== Syntax Check ===${NC}"
find $SRC_DIR/ -name "*.py" -exec python -m py_compile {} \;
find $TEST_DIR/ -name "*.py" -exec python -m py_compile {} \;
echo -e "${GREEN}✓ Syntax check passed${NC}"

echo -e "\n${BLUE}=== Code Style Checks ===${NC}"

# Run flake8
run_linter "flake8" "uv run flake8 $SRC_DIR/ $TEST_DIR/ --max-line-length=88 --extend-ignore=E203,W503 --statistics"

# Run black check
run_linter "black (check)" "uv run black --check --diff $SRC_DIR/ $TEST_DIR/"

# Run pyflakes for import issues
run_linter "pyflakes" "uv run python -m pyflakes $SRC_DIR/ $TEST_DIR/"

# Run mypy if available
if command_exists mypy; then
    run_linter "mypy" "uv run mypy $SRC_DIR/ --ignore-missing-imports --no-strict-optional"
fi

# Run isort check if available
if uv run python -c "import isort" 2>/dev/null; then
    run_linter "isort (check)" "uv run isort --check-only --diff $SRC_DIR/ $TEST_DIR/"
fi

echo -e "\n${GREEN}=== All linting checks completed! ===${NC}"
