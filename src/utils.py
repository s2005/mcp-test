import os
from typing import Dict, List, Optional

def load_content_from_json(json_file_path: Optional[str] = None) -> dict:
    """
    Load complete content configuration from JSON file.
    
    Args:
        json_file_path: Optional path to JSON file. If None, uses default content.json
    
    Returns:
        Dictionary containing full content configuration
    """
    # Import here to avoid circular imports
    from prompts.prompt_loader import load_content_from_json as loader_func
    return loader_func(json_file_path)

def load_tips_from_json(json_file_path: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Load tips from content configuration.
    
    Args:
        json_file_path: Optional path to JSON file. If provided, takes precedence over environment variable.
    
    Returns:
        Dictionary containing tips by category
    """
    # Use provided path or get from environment variable
    if json_file_path is None:
        json_file_path = os.getenv('TIPS_JSON_PATH')
    
    try:
        # Load complete content configuration
        content = load_content_from_json(json_file_path)
        
        # Extract tips section
        tips = content.get("tips", {})
        
        if not tips:
            print("Warning: No tips found in content configuration. Returning empty tips.")
        
        return tips
        
    except Exception as e:
        print(f"Error loading content for tips: {e}. Returning empty tips.")
        return {}

def get_default_content_path() -> str:
    """
    Get the default path to content.json file.
    
    Returns:
        Path to the default content.json file
    """
    # Get the directory containing this utils.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to default content.json
    return os.path.join(current_dir, 'data', 'content.json')

def load_default_content() -> dict:
    """
    Load the default content configuration.
    
    Returns:
        Dictionary containing default content configuration
    """
    default_path = get_default_content_path()
    return load_content_from_json(default_path)
