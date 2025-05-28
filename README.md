# Test MCP Server

A test Model Context Protocol (MCP) server created for demonstration purposes, based on Morten Rand-Hendriksen's LinkedIn Learning course "Model Context Protocol (MCP): Hands-On with Agentic AI".

## Overview

This MCP server provides a collection of tools, resources, and prompts to test MCP functionality including:

- **Tools**: Time and date utilities, greeting generation, date calculations, and learning tips
- **Resources**: MCP development tips and documentation (multiple categories: MCP, Python, Docker)
- **Prompts**: Professional prompt templates for code review, learning plans, debugging assistance, project planning, and MCP development

## Project Structure

The project follows standard Python packaging conventions with a clean separation between source code and tests:

```text
mcp-test/
├── src/                   # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── server.py          # Main MCP server entry point (~70 lines)
│   ├── client.py          # Simple MCP client for testing
│   ├── utils.py           # Utility functions for tips loading
│   ├── tools/             # MCP tools directory
│   │   ├── __init__.py
│   │   ├── time_tools.py  # Time-related tools
│   │   ├── greeting_tools.py # Greeting generation tool
│   │   └── tips_tools.py  # Learning tips tool
│   ├── resources/         # MCP resources directory
│   │   ├── __init__.py
│   │   └── tips_resources.py # Tips-related resources
│   └── prompts/           # MCP prompts directory
│       ├── __init__.py
│       ├── development_prompts.py # Code review, MCP development
│       ├── learning_prompts.py    # Learning plans, debugging
│       └── planning_prompts.py    # Project planning
├── tests/                  # Test directory
│   ├── __init__.py         # Test package initialization
│   └── tests.py            # Comprehensive test suite
├── docs/                   # Documentation
│   └── refactoring_plan.md # Detailed refactoring documentation
├── .github/                # GitHub Actions workflows
│   └── workflows/
│       ├── test.yml        # Automated CI/CD pipeline
│       └── ci.yml          # Manual CI pipeline with configurable options
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── uv.lock                 # Dependency lock file
└── .gitignore              # Git ignore patterns
```

### Key Components

- **`src/server.py`**: Main MCP server entry point with modular component registration (~70 lines)
- **`src/utils.py`**: Utility functions for tips loading and data management
- **`src/tools/`**: Modular MCP tools organized by functionality
  - `time_tools.py`: Date/time utilities (`get_current_time`, `calculate_days_until_date`)
  - `greeting_tools.py`: Greeting generation (`generate_greeting`)
  - `tips_tools.py`: Learning tips retrieval (`get_learning_tips`)
- **`src/resources/`**: MCP resources for content access
  - `tips_resources.py`: Tips-based resources (`tips://mcp-test`, `tips://category/{category}`)
- **`src/prompts/`**: Professional prompt templates organized by domain
  - `development_prompts.py`: Code review and MCP development prompts
  - `learning_prompts.py`: Learning plans and debugging assistance prompts
  - `planning_prompts.py`: Project planning and architecture prompts
- **`src/client.py`**: Simple synchronous MCP client for testing and development
- **`tests/`**: Comprehensive test suite covering all server functionality
- **`docs/`**: Documentation including detailed refactoring plans
- **`pyproject.toml`**: Project configuration with dependencies, build settings, and test configuration

### Architecture Benefits

- ✅ **Separation of concerns** - each module has a single responsibility
- ✅ **Maintainability** - easier to find and modify specific functionality  
- ✅ **Testability** - individual components can be unit tested
- ✅ **Scalability** - easy to add new tools/resources/prompts
- ✅ **Code reuse** - utilities can be shared across modules
- ✅ **Clear organization** - logical grouping by functionality

## Setup

1. **Install uv** (Python project manager):

   **MacOS / Linux:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Navigate to the project directory:**

   ```bash
   cd D:\mcp\my.python\mcp-test
   ```

3. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate

   ```

4. **Install dependencies from pyproject.toml:**

   ```bash
   uv sync
   ```

## Running the Server

### Development Mode (MCP Inspector)

Test your server using the MCP Inspector:

```bash
# Basic usage
mcp dev src/server.py

# With custom tips file using command-line argument
mcp dev src/server.py -- --json-file tests/data/tips_categories.json
```

### Direct Execution

You can also run the server directly with Python:

```bash
# Basic usage (uses environment variable if set)
python src/server.py

# With custom tips file
python src/server.py --json-file tests/data/tips_categories.json

# Using short form argument
python src/server.py -j /path/to/your/custom_tips.json
```

### Install in Claude Desktop

1. Install the server:

   ```bash
   mcp install src/server.py
   ```

2. Find the full path to `uv`:

   ```bash
   where uv  # Windows
   which uv  # MacOS/Linux
   ```

3. Open Claude Desktop config:
   - Go to Claude Settings → Developer → Edit Config
   - Or edit: `%AppData%\Claude\claude_desktop_config.json` (Windows)

4. Add your server configuration:

   ```json
   {
     "mcpServers": {
       "mcp-test": {
         "command": "C:\\Users\\YourUser\\.local\\bin\\uv.exe",
         "args": [
           "run",
           "--with",
           "mcp[cli]",
           "mcp",
           "run",
           "D:\\mcp\\my.python\\mcp-test\\src\\server.py"
         ]
       }
     }
   }
   ```

5. Restart Claude Desktop

## Configuration

### Tips Content

The server loads learning tips from a JSON file that can be specified in two ways:

1. **Command-line argument** (takes precedence)
2. **Environment variable** (fallback option)

#### Command-Line Arguments

You can specify the JSON file path directly when starting the server using command-line arguments:

**Short form:**

```bash
python src/server.py -j /path/to/your/tips_categories.json
```

**Long form:**

```bash
python src/server.py --json-file /path/to/your/tips_categories.json
```

**Help:**

```bash
python src/server.py --help
```

#### Setting the Environment Variable

If no command-line argument is provided, the server will fall back to using the `TIPS_JSON_PATH` environment variable.

**Windows (Command Prompt):**

```cmd
set TIPS_JSON_PATH=d:\mcp\my.python\mcp-test\tests\data\tips_categories.json
```

**Windows (Git Bash):**

```bash
export TIPS_JSON_PATH="d:/mcp/my.python/mcp-test/tests/data/tips_categories.json"
```

**MacOS/Linux (Bash):**

```bash
export TIPS_JSON_PATH="/path/to/your/tips_categories.json"
```

#### JSON File Format

The tips JSON file should follow this structure:

```json
{
    "category_name": [
        "Tip 1 for this category",
        "Tip 2 for this category",
        "Tip 3 for this category"
    ],
    "another_category": [
        "Another tip",
        "Yet another tip"
    ]
}
```

If the environment variable is not set or the file cannot be loaded, the server will fall back to default tips for MCP, Python, and Docker categories.

**Important:** Command-line arguments always take precedence over environment variables. If you specify both a `--json-file` argument and set the `TIPS_JSON_PATH` environment variable, the command-line argument will be used.

#### Example JSON File

A sample `tips_categories.json` file is included in the `tests/data` folder with default tips for:

- **mcp**: Model Context Protocol development tips
- **python**: Python programming best practices
- **docker**: Docker containerization tips

You can modify this file or create your own with additional categories and tips.

## Running Tests

The project includes a comprehensive test suite to ensure all functionality works correctly:

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/tests.py -v
```

The test suite covers:

- All MCP server tools and functionality
- Resource retrieval and formatting
- Prompt template generation and parameter handling
- Error handling and edge cases
- Client-server communication

## Code Quality and Linting

This project maintains high code quality standards through automated linting and formatting tools. For detailed information about linting setup, configuration, and usage:

- **Quick Reference**: See [`LINTING_SETUP.md`](LINTING_SETUP.md) for implementation summary and features
- **Detailed Usage Guide**: See [`scripts/README.md`](scripts/README.md) for comprehensive usage instructions

### Quick Commands

```bash
# Run all linting checks
make lint

# Automatically fix linting issues
make fix-lint

# Complete development workflow
make all
```

The project uses flake8, black, isort, autopep8, pyflakes, and mypy to ensure consistent code formatting, PEP 8 compliance, and type safety.

## Available Tools

1. **get_current_time()** - Get current date and time
2. **generate_greeting(name)** - Generate personalized greeting
3. **calculate_days_until_date(target_date)** - Calculate days between dates
4. **get_learning_tips(category)** - Get learning tips for development (categories: mcp, python, docker)

**Tip:** Use the `--json-file` argument to load custom tip categories when starting the server:

```bash
python src/server.py --json-file my_custom_tips.json
```

## Available Resources

1. **tips://mcp** - MCP development learning tips
2. **tips://category/{category}** - Category-specific learning tips (mcp, python, docker)

## Available Prompts

The server provides 5 professional prompt templates for common development and learning workflows:

### 1. Code Review Prompt (`code_review_prompt`)

Generate structured code review requests with customizable parameters.

**Parameters:**

- `language` (optional, default: "python") - Programming language for review
- `code_type` (optional, default: "function") - Type of code (function, class, module, etc.)

**Usage:** Provides a comprehensive template for requesting detailed code reviews including quality, performance, security, and maintainability analysis.

### 2. Learning Plan Prompt (`learning_plan_prompt`)

Create personalized learning plans for any technology or skill.

**Parameters:**

- `topic` (required) - The subject or technology to learn
- `skill_level` (optional, default: "beginner") - Current skill level (beginner, intermediate, advanced)
- `timeframe` (optional, default: "1 month") - Available learning time

**Usage:** Generates detailed learning plans with objectives, prerequisites, weekly breakdowns, resources, and assessment strategies.

### 3. Debugging Assistant Prompt (`debugging_assistant_prompt`)

Get systematic debugging guidance for different types of errors.

**Parameters:**

- `language` (optional, default: "python") - Programming language
- `error_type` (optional, default: "runtime") - Type of error (runtime, syntax, logic, performance)

**Usage:** Provides structured debugging approaches with specific methodologies based on error type and language.

### 4. Project Planning Prompt (`project_planning_prompt`)

Generate comprehensive project plans and architecture guidance.

**Parameters:**

- `project_type` (required) - Type of project (web app, API, mobile app, data pipeline, etc.)
- `team_size` (optional, default: "1-3") - Development team size
- `timeline` (optional, default: "1-3 months") - Project timeline

**Usage:** Creates detailed project plans including architecture design, development phases, technical specifications, and best practices.

### 5. MCP Development Prompt (`mcp_development_prompt`)

Get assistance with Model Context Protocol development.

**Parameters:**

- `component_type` (optional, default: "tool") - MCP component type (tool, resource, prompt, server)
- `complexity` (optional, default: "intermediate") - Complexity level (beginner, intermediate, advanced)

**Usage:** Provides guidance for building MCP components with FastMCP, including implementation approaches, protocol compliance, code examples, and testing strategies.

## CI/CD

This project includes two GitHub Actions workflows:

### Automated Testing (`test.yml`)

Automatically runs tests on:

- Push to main branch
- Pull requests to main branch

The workflow:

- Tests against Python versions 3.10, 3.11, 3.12, and 3.13
- Installs dependencies using `uv`
- Runs the test suite with `pytest`
- Generates code coverage reports

### Manual CI Pipeline (`ci.yml`)

A comprehensive CI pipeline that can be triggered manually via GitHub Actions UI:

- **Configurable Python Version**: Choose from 3.10, 3.11, 3.12, or 3.13 (default: 3.12)
- **Optional Coverage Reports**: Enable/disable coverage report generation
- **Full CI Suite**: Runs `make ci` which includes:
  - Development dependency installation
  - Complete linting checks (flake8, black, isort, mypy)
  - Full test suite with coverage
- **Artifacts**: Uploads HTML coverage reports and optionally sends coverage to Codecov

To trigger the manual CI pipeline:

1. Go to the "Actions" tab in your GitHub repository
2. Select "CI Pipeline" workflow
3. Click "Run workflow"
4. Choose your desired Python version and coverage options
5. Click "Run workflow" to start

## Example Usage in Claude

Once configured, you can use the server's capabilities through different types of interactions:

### Tool Examples

- "What time is it?"
- "Greet me with my name John"
- "How many days until Christmas 2024?"
- "Give me some learning tips for MCP"
- "Give me some Python development tips"
- "Give me some Docker tips"

### Resource Examples

- Ask Claude to access MCP development tips through the tips://mcp resource
- Request category-specific tips using tips://category/python, tips://category/docker, etc.

### Prompt Examples

- "Use the code review prompt to help me review my Python function"
- "Create a learning plan for FastAPI using the learning plan prompt"
- "Help me debug this JavaScript performance issue using the debugging assistant prompt"
- "Plan a mobile app project for a 5-person team using the project planning prompt"
- "Guide me through building an MCP tool using the MCP development prompt"

**Note:** Prompts provide structured templates that guide interactions and ensure comprehensive coverage of important topics.

## Course Information

This server is created as part of the LinkedIn Learning course:
**"Model Context Protocol (MCP): Hands-On with Agentic AI"**
by **Morten Rand-Hendriksen**

Course Repository: <https://github.com/LinkedInLearning/model-context-protocol-mcp-hands-on-with-agentic-ai-2034200>

## License

This demo is for educational purposes based on the LinkedIn Learning course materials.
