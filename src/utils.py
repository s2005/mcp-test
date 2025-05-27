import json
import os
from typing import Dict, List, Optional

def load_tips_from_json(json_file_path: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Load tips from JSON file specified by parameter or environment variable.
    
    Args:
        json_file_path: Optional path to JSON file. If provided, takes precedence over environment variable.
    
    Returns:
        Dictionary containing tips by category
    """
    # Default fallback tips
    default_tips = {
        "mcp-test": [
            "Configure this server by adding it to your MCP client configuration file",
            "Set the TIPS_JSON_PATH environment variable to load custom tips from a JSON file",
            "Use 'uv run src/server.py' to start the server in development mode",
            "Test the server tools using get_current_time, generate_greeting, and get_tips functions",
            "The server provides tips categorized by technology - add more categories as needed",
            "Extend functionality by adding new @mcp.tool() decorated functions to the server"
        ]
    }
    
    # Use provided path or get from environment variable
    if json_file_path is None:
        json_file_path = os.getenv('TIPS_JSON_PATH')
    
    if not json_file_path:
        print("Warning: No JSON file path provided via command line or TIPS_JSON_PATH environment variable. Using default tips.")
        return default_tips
    
    try:
        # Check if file exists
        if not os.path.exists(json_file_path):
            print(f"Warning: Tips file not found at {json_file_path}. Using default tips.")
            return default_tips
        
        # Load tips from JSON file
        with open(json_file_path, 'r', encoding='utf-8') as file:
            tips_data = json.load(file)
            
        # Validate that the loaded data is a dictionary
        if not isinstance(tips_data, dict):
            print(f"Error: Tips file format invalid. Expected dictionary, got {type(tips_data)}. Using default tips.")
            return default_tips
            
        # Validate that all values are lists
        for category, tips in tips_data.items():
            if not isinstance(tips, list):
                print(f"Error: Category '{category}' should contain a list of tips. Using default tips.")
                return default_tips
                
        print(f"Successfully loaded tips from {json_file_path}")
        return tips_data
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file_path}: {e}. Using default tips.")
        return default_tips
    except Exception as e:
        print(f"Error loading tips from {json_file_path}: {e}. Using default tips.")
        return default_tips
