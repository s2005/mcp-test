#!/bin/bash
# fix-lint.sh - Automatically fix linting issues

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

echo -e "${BLUE}=== Auto-fixing Python Code Issues ===${NC}"
echo "Processing directories: $SRC_DIR/ $TEST_DIR/"
echo

# Ensure we're in the project root
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}Error: pyproject.toml not found. Run this script from the project root.${NC}"
    exit 1
fi

# Install dev dependencies if needed
echo -e "${BLUE}Ensuring dev dependencies are installed...${NC}"
uv sync --group dev

echo -e "\n${YELLOW}=== Running auto-formatters ===${NC}"

# Fix import sorting with isort
if uv run python -c "import isort" 2>/dev/null; then
    echo -e "${YELLOW}Fixing import order with isort...${NC}"
    uv run isort $SRC_DIR/ $TEST_DIR/
    echo -e "${GREEN}✓ Import order fixed${NC}"
else
    echo -e "${YELLOW}Installing isort...${NC}"
    uv add --group dev isort
    echo -e "${YELLOW}Fixing import order with isort...${NC}"
    uv run isort $SRC_DIR/ $TEST_DIR/
    echo -e "${GREEN}✓ Import order fixed${NC}"
fi

# Fix code formatting with black
echo -e "${YELLOW}Formatting code with black...${NC}"
uv run black $SRC_DIR/ $TEST_DIR/
echo -e "${GREEN}✓ Code formatting applied${NC}"

# Fix some flake8 issues automatically with autopep8
if uv run python -c "import autopep8" 2>/dev/null; then
    echo -e "${YELLOW}Applying autopep8 fixes...${NC}"
    uv run autopep8 --in-place --recursive --max-line-length=88 $SRC_DIR/ $TEST_DIR/
    echo -e "${GREEN}✓ autopep8 fixes applied${NC}"
else
    echo -e "${YELLOW}Installing autopep8...${NC}"
    uv add --group dev autopep8
    echo -e "${YELLOW}Applying autopep8 fixes...${NC}"
    uv run autopep8 --in-place --recursive --max-line-length=88 $SRC_DIR/ $TEST_DIR/
    echo -e "${GREEN}✓ autopep8 fixes applied${NC}"
fi

echo -e "\n${BLUE}=== Running final validation ===${NC}"

# Run syntax check
echo -e "${YELLOW}Checking syntax...${NC}"
find $SRC_DIR/ -name "*.py" -exec python -m py_compile {} \;
find $TEST_DIR/ -name "*.py" -exec python -m py_compile {} \;
echo -e "${GREEN}✓ Syntax is valid${NC}"

# Quick lint check
echo -e "${YELLOW}Running quick lint check...${NC}"
if uv run flake8 $SRC_DIR/ $TEST_DIR/ --max-line-length=88 --extend-ignore=E203,W503 --statistics; then
    echo -e "${GREEN}✓ Most linting issues have been resolved${NC}"
else
    echo -e "${YELLOW}⚠ Some linting issues may remain - run ./scripts/lint.sh for details${NC}"
fi

echo -e "\n${GREEN}=== Auto-fix completed! ===${NC}"
echo -e "${BLUE}Run './scripts/lint.sh' to see remaining issues (if any)${NC}"
