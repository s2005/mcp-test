"""
JSON-based prompt loader for MCP servers.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .validator import ContentValidator


class JSONPromptLoader:
    """Loads and processes prompts from JSON configuration."""

    def __init__(self, content_data: Dict[str, Any], validator: ContentValidator):
        """
        Initialize prompt loader.

        Args:
            content_data: Content configuration dictionary
            validator: Content validator instance
        """
        self.content_data = content_data
        self.validator = validator
        self.prompts = {}

        # Validate the content on initialization
        self.validator.validate_content(content_data)

    def load_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all prompts from JSON data.

        Returns:
            Dictionary mapping prompt names to their definitions
        """
        prompts_data = self.content_data.get("prompts", {})
        loaded_prompts = {}

        for category, category_prompts in prompts_data.items():
            for prompt_key, prompt_def in category_prompts.items():
                # Validate individual prompt
                self.validator.validate_prompt(prompt_def)

                # Use the name from the prompt definition, not the key
                prompt_name = prompt_def.get("name", prompt_key)
                loaded_prompts[prompt_name] = prompt_def

        self.prompts = loaded_prompts
        return loaded_prompts

    def create_prompt_function(
        self, prompt_name: str, prompt_def: Dict[str, Any]
    ) -> Callable:
        """
        Create MCP prompt function from JSON definition - simplified processing.

        Args:
            prompt_name: Name of the prompt
            prompt_def: Prompt definition dictionary

        Returns:
            Callable function that can be registered with MCP
        """

        def prompt_function(**kwargs) -> List[Dict[str, str]]:
            """
            Generated prompt function.

            Returns:
                List of message dictionaries for the prompt template
            """
            # Get argument definitions
            arg_definitions = prompt_def.get("arguments", [])

            # Validate and process arguments
            processed_args = self.validator.validate_arguments(arg_definitions, kwargs)

            # Simple template formatting without special processing
            template = prompt_def["template"]
            try:
                formatted_content = template.format(**processed_args)
            except KeyError as e:
                formatted_content = template
                print(f"Warning: Missing placeholder in template: {e}")

            # Return message with appropriate role
            role = prompt_def.get("role", "user")
            return [{"role": role, "content": formatted_content}]

        # Set function metadata
        prompt_function.__name__ = prompt_name
        prompt_function.__doc__ = prompt_def.get(
            "description", f"Generated prompt: {prompt_name}"
        )

        # Add argument information to function for MCP registration
        if "arguments" in prompt_def:
            prompt_function._mcp_arguments = prompt_def["arguments"]

        return prompt_function

    def get_prompt_names(self) -> List[str]:
        """
        Get list of all available prompt names.

        Returns:
            List of prompt names
        """
        if not self.prompts:
            self.load_prompts()
        return list(self.prompts.keys())

    def get_prompt_definition(self, prompt_name: str) -> Dict[str, Any]:
        """
        Get prompt definition by name.

        Args:
            prompt_name: Name of the prompt

        Returns:
            Prompt definition dictionary

        Raises:
            KeyError: If prompt not found
        """
        if not self.prompts:
            self.load_prompts()

        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt not found: {prompt_name}")

        return self.prompts[prompt_name]


def load_content_from_json(json_file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load content from JSON file with validation.

    Args:
        json_file_path: Path to JSON file. If None, uses default content.json

    Returns:
        Content dictionary

    Raises:
        FileNotFoundError: If JSON file not found
        ValueError: If JSON is invalid or doesn't match schema
    """
    if json_file_path is None:
        # Default to content.json in src/data/
        current_dir = Path(__file__).parent
        default_path = current_dir.parent / "data" / "content.json"
        json_path = default_path
    else:
        json_path = Path(json_file_path)

    if not json_path.exists():
        raise FileNotFoundError(f"Content file not found: {json_path}")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in content file: {e}")

    # Validate content against schema
    validator = ContentValidator()
    validator.validate_content(content)

    return content
