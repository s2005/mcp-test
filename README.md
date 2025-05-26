# Demo MCP Server

A simple Model Context Protocol (MCP) server created for demonstration purposes, based on Morten Rand-Hendriksen's LinkedIn Learning course "Model Context Protocol (MCP): Hands-On with Agentic AI".

## Overview

This MCP server provides a collection of simple tools to demonstrate MCP functionality including:

- Time and date utilities
- Greeting generation
- Date calculations
- Simple todo creation
- Learning tips
- Server information

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
mcp dev server.py
```

### Install in Claude Desktop

1. Install the server:

   ```bash
   mcp install server.py
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
           "D:\\mcp\\my.python\\mcp-test\\server.py"
         ]
       }
     }
   }
   ```

5. Restart Claude Desktop

## Available Tools

1. **get_current_time()** - Get current date and time
2. **generate_greeting(name)** - Generate personalized greeting
3. **calculate_days_until_date(target_date)** - Calculate days between dates
4. **create_simple_todo(task, priority)** - Create todo items
5. **get_learning_tips()** - Get MCP learning tips
6. **demo_info()** - Get server information

## Example Usage in Claude

Once configured, you can use prompts like:

- "What time is it?"
- "Greet me with my name John"
- "How many days until Christmas 2024?"
- "Create a todo to learn MCP with high priority"
- "Give me some learning tips for MCP"
- "Tell me about this demo server"

## Course Information

This server is created as part of the LinkedIn Learning course:
**"Model Context Protocol (MCP): Hands-On with Agentic AI"**
by **Morten Rand-Hendriksen**

Course Repository: <https://github.com/LinkedInLearning/model-context-protocol-mcp-hands-on-with-agentic-ai-2034200>

## License

This demo is for educational purposes based on the LinkedIn Learning course materials.
