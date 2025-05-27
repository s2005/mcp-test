"""
Consolidated prompt registration for all prompt categories.

This module provides a single entry point for registering all prompts
from JSON configuration data, replacing the previous category-specific
prompt files.
"""

from typing import Any, Dict

from .prompt_registry import PromptRegistry


def register_all_prompts(mcp, content_data: Dict[str, Any]) -> None:
    """
    Register all prompts from JSON configuration with the MCP server.

    This function consolidates prompt registration that was previously
    split across development_prompts.py, learning_prompts.py, and
    planning_prompts.py files.

    Args:
        mcp: FastMCP server instance
        content_data: Content configuration dictionary containing prompts
    """
    prompt_registry = PromptRegistry()
    prompt_registry.register_prompts_from_json(mcp, content_data)


def get_prompt_categories(content_data: Dict[str, Any]) -> list:
    """
    Get list of available prompt categories from content data.

    Args:
        content_data: Content configuration dictionary

    Returns:
        List of prompt category names
    """
    prompts_data = content_data.get("prompts", {})
    return list(prompts_data.keys())


def get_prompts_by_category(
    content_data: Dict[str, Any], category: str
) -> Dict[str, Any]:
    """
    Get all prompts for a specific category.

    Args:
        content_data: Content configuration dictionary
        category: Category name (e.g., 'development', 'learning', 'planning')

    Returns:
        Dictionary of prompts in the specified category
    """
    prompts_data = content_data.get("prompts", {})
    return prompts_data.get(category, {})


def validate_prompt_structure(content_data: Dict[str, Any]) -> bool:
    """
    Validate that the content data has proper prompt structure.

    Args:
        content_data: Content configuration dictionary

    Returns:
        True if structure is valid, False otherwise
    """
    if not isinstance(content_data, dict):
        return False

    prompts_data = content_data.get("prompts", {})
    if not isinstance(prompts_data, dict):
        return False

    # Check that each category contains valid prompt definitions
    for category, prompts in prompts_data.items():
        if not isinstance(prompts, dict):
            return False

        for prompt_name, prompt_def in prompts.items():
            if not isinstance(prompt_def, dict):
                return False

            # Check required fields
            if "template" not in prompt_def:
                return False

    return True
