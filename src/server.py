from mcp.server.fastmcp import FastMCP
import argparse
import sys
import os

# Add src directory to path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import load_tips_from_json, load_content_from_json
from tools.time_tools import register_time_tools
from tools.greeting_tools import register_greeting_tools
from tools.tips_tools import register_tips_tools
from resources.tips_resources import register_tips_resources
from prompts.prompt_registry import PromptRegistry

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
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-j', '--json-file',
        type=str,
        help='Path to JSON file containing tips data. Takes precedence over TIPS_JSON_PATH environment variable.'
    )
    
    return parser.parse_args()

def register_all_components(content_data):
    """
    Register all tools, resources, and prompts with the MCP server.
    
    Args:
        content_data: Dictionary containing full content configuration from JSON
    """
    # Extract tips for backward compatibility
    tips_by_category = content_data.get("tips", {})
    
    # Register tools
    register_time_tools(mcp)
    register_greeting_tools(mcp)
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
    try:
        content_data = load_content_from_json(args.json_file)
    except Exception as e:
        print(f"Warning: Failed to load content from JSON: {e}")
        print("Falling back to tips-only loading...")
        # Fallback to tips-only for backward compatibility
        tips_by_category = load_tips_from_json(args.json_file)
        content_data = {"tips": tips_by_category, "prompts": {}}
    
    # Register all MCP components
    register_all_components(content_data)
    
    # Start the MCP server
    mcp.run()
