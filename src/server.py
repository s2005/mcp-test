import argparse
import os
import sys

from mcp.server.fastmcp import FastMCP

from content.content_manager import ContentManager
from prompts.prompt_registry import PromptRegistry
from resources.tips_resources import register_tips_resources
from tools.greeting_tools import register_greeting_tools
from tools.time_tools import register_time_tools
from tools.tips_tools import register_tips_tools
from utils import load_content_from_json

# Add src directory to path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Create an MCP server
mcp = FastMCP("MCP test")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="MCP test server - Model Context Protocol implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-j",
        "--json-file",
        type=str,
        help="Path to JSON file containing tips data. Takes precedence over TIPS_JSON_PATH environment variable.",
    )

    return parser.parse_args()


def register_all_components(content_data):
    """
    Register all tools, resources, and prompts with the MCP server.

    Args:
        content_data: Dictionary containing full content configuration from JSON
    """
    # Initialize ContentManager for centralized content access
    content_manager = ContentManager(content_data)

    # Extract tips for tools and resources
    tips_by_category = content_data.get("tips", {})

    # Register tools
    register_time_tools(mcp)
    register_greeting_tools(mcp, content_manager)
    register_tips_tools(mcp, tips_by_category)

    # Register resources
    register_tips_resources(mcp, tips_by_category)

    # Register prompts using new JSON-based system
    prompt_registry = PromptRegistry()
    prompt_registry.register_prompts_from_json(mcp, content_data)


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Load full content configuration from JSON
    content_data = load_content_from_json(args.json_file)

    # Register all MCP components
    register_all_components(content_data)

    # Start the MCP server
    mcp.run()
