from mcp.server.fastmcp import FastMCP
import argparse
import sys
import os

# Add src directory to path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import load_tips_from_json
from tools.time_tools import register_time_tools
from tools.greeting_tools import register_greeting_tools
from tools.tips_tools import register_tips_tools
from resources.tips_resources import register_tips_resources
from prompts.development_prompts import register_development_prompts
from prompts.learning_prompts import register_learning_prompts
from prompts.planning_prompts import register_planning_prompts

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

def register_all_components(tips_by_category):
    """
    Register all tools, resources, and prompts with the MCP server.
    
    Args:
        tips_by_category: Dictionary containing tips data loaded from JSON
    """
    # Register tools
    register_time_tools(mcp)
    register_greeting_tools(mcp)
    register_tips_tools(mcp, tips_by_category)
    
    # Register resources
    register_tips_resources(mcp, tips_by_category)
    
    # Register prompts
    register_development_prompts(mcp)
    register_learning_prompts(mcp)
    register_planning_prompts(mcp)

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Load tips with the provided JSON file path (if any)
    tips_by_category = load_tips_from_json(args.json_file)
    
    # Register all MCP components
    register_all_components(tips_by_category)
    
    # Start the MCP server
    mcp.run()
