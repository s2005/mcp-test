# Demo MCP Server

A simple Model Context Protocol (MCP) server created for demonstration purposes, based on Morten Rand-Hendriksen's LinkedIn Learning course "Model Context Protocol (MCP): Hands-On with Agentic AI".

## Overview

This MCP server provides a collection of tools, resources, and prompts to demonstrate comprehensive MCP functionality including:

- **Tools**: Time and date utilities, greeting generation, date calculations, and learning tips
- **Resources**: MCP development tips and documentation (multiple categories: MCP, Python, Docker)
- **Prompts**: Professional prompt templates for code review, learning plans, debugging assistance, project planning, and MCP development

## Project Structure

The project follows standard Python packaging conventions with a clean separation between source code and tests:

```text
mcp-test/
├── src/                    # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── server.py          # Main MCP server implementation
│   └── client.py          # Simple MCP client for testing
├── tests/                  # Test directory
│   ├── __init__.py        # Test package initialization
│   └── tests.py           # Comprehensive test suite
├── .github/               # GitHub Actions workflows
│   └── workflows/
│       └── test.yml       # CI/CD pipeline configuration
├── pyproject.toml         # Project configuration and dependencies
├── README.md              # This file
├── uv.lock               # Dependency lock file
└── .gitignore            # Git ignore patterns
```

### Key Components

- **`src/server.py`**: The main MCP server implementation containing all tools and resources
- **`src/client.py`**: A simple synchronous MCP client used for testing and development
- **`tests/tests.py`**: Comprehensive test suite covering all server functionality
- **`pyproject.toml`**: Project configuration with dependencies, build settings, and test configuration

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
mcp dev src/server.py
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

## Available Tools

1. **get_current_time()** - Get current date and time
2. **generate_greeting(name)** - Generate personalized greeting
3. **calculate_days_until_date(target_date)** - Calculate days between dates
4. **get_learning_tips(category)** - Get learning tips for development (categories: mcp, python, docker)

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

This project includes a GitHub Actions workflow that automatically runs tests on:

- Push to main branch
- Pull requests to main branch

The workflow:

- Tests against Python versions 3.10, 3.11, and 3.12
- Installs dependencies using `uv`
- Runs the test suite with `pytest`
- Generates code coverage reports
- Uploads coverage data to Codecov

The workflow file is located at `.github/workflows/test.yml`.

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
