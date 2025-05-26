# Demo MCP Server

A simple Model Context Protocol (MCP) server created for demonstration purposes, based on Morten Rand-Hendriksen's LinkedIn Learning course "Model Context Protocol (MCP): Hands-On with Agentic AI".

## Overview

This MCP server provides a collection of simple tools to demonstrate MCP functionality including:

- Time and date utilities
- Greeting generation
- Date calculations
- Learning tips (multiple categories: MCP, Python, Docker)
- MCP resources for tips and documentation

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
- Error handling and edge cases
- Client-server communication
- Resource retrieval

## Available Tools

1. **get_current_time()** - Get current date and time
2. **generate_greeting(name)** - Generate personalized greeting
3. **calculate_days_until_date(target_date)** - Calculate days between dates
4. **get_learning_tips(category)** - Get learning tips for development (categories: mcp, python, docker)

## Available Resources

1. **tips://mcp** - MCP development learning tips
2. **tips://category/{category}** - Category-specific learning tips (mcp, python, docker)

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

Once configured, you can use prompts like:

- "What time is it?"
- "Greet me with my name John"
- "How many days until Christmas 2024?"
- "Give me some learning tips for MCP"
- "Give me some Python development tips"
- "Give me some Docker tips"

## Course Information

This server is created as part of the LinkedIn Learning course:
**"Model Context Protocol (MCP): Hands-On with Agentic AI"**
by **Morten Rand-Hendriksen**

Course Repository: <https://github.com/LinkedInLearning/model-context-protocol-mcp-hands-on-with-agentic-ai-2034200>

## License

This demo is for educational purposes based on the LinkedIn Learning course materials.
