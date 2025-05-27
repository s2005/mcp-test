"""
Dynamic prompt registration system for MCP servers.
"""

from typing import Any, Dict

from .prompt_loader import JSONPromptLoader
from .validator import ContentValidator


class PromptRegistry:
    """Registers prompts dynamically from JSON configuration."""

    def __init__(self):
        """Initialize the prompt registry."""
        self.registered_prompts = {}

    def register_prompts_from_json(self, mcp, content_data: Dict[str, Any]) -> None:
        """
        Register all prompts from JSON with MCP server.

        Args:
            mcp: FastMCP server instance
            content_data: Content configuration dictionary
        """
        # Create validator and loader
        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        # Load all prompts
        prompts = loader.load_prompts()

        # Register each prompt with MCP
        for prompt_name, prompt_def in prompts.items():
            self._register_single_prompt(mcp, loader, prompt_name, prompt_def)

    def _register_single_prompt(
        self,
        mcp,
        loader: JSONPromptLoader,
        prompt_name: str,
        prompt_def: Dict[str, Any],
    ) -> None:
        """
        Register a single prompt with the MCP server.

        Args:
            mcp: FastMCP server instance
            loader: JSONPromptLoader instance
            prompt_name: Name of the prompt
            prompt_def: Prompt definition dictionary
        """
        # Create the prompt function
        prompt_function = loader.create_prompt_function(prompt_name, prompt_def)

        # Add type annotations for FastMCP
        self._add_mcp_annotations(prompt_function, prompt_def)

        # Register with MCP using decorator
        decorated_function = mcp.prompt()(prompt_function)

        # Store reference
        self.registered_prompts[prompt_name] = {
            "function": decorated_function,
            "definition": prompt_def,
        }

        print(f"Registered prompt: {prompt_name}")

    def _add_mcp_annotations(self, func, prompt_def: Dict[str, Any]) -> None:
        """
        Add MCP-specific annotations to the function.

        Args:
            func: Function to annotate
            prompt_def: Prompt definition dictionary
        """
        # Add function signature based on arguments
        arguments = prompt_def.get("arguments", [])

        # Create parameter annotations
        if arguments:
            annotations = {}
            for arg in arguments:
                arg_name = arg["name"]
                arg_type = arg.get("type", "string")

                # Map JSON types to Python types
                if arg_type == "string":
                    python_type = str
                elif arg_type == "number":
                    python_type = float
                elif arg_type == "boolean":
                    python_type = bool
                else:
                    python_type = str

                annotations[arg_name] = python_type

            # Add annotations to function
            func.__annotations__ = annotations

        # Add docstring with argument information
        if arguments:
            docstring_parts = [prompt_def.get("description", "Generated prompt")]
            docstring_parts.append("\nArgs:")

            for arg in arguments:
                arg_name = arg["name"]
                arg_desc = arg.get("description", "")
                arg_default = arg.get("default")
                required = arg.get("required", False)

                if required:
                    arg_line = f"    {arg_name}: {arg_desc}"
                else:
                    arg_line = f"    {arg_name}: {arg_desc} (default: {arg_default})"

                docstring_parts.append(arg_line)

            docstring_parts.append("\nReturns:")
            docstring_parts.append(
                "    List of message dictionaries for the prompt template"
            )

            func.__doc__ = "\n".join(docstring_parts)

    def get_registered_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered prompts.

        Returns:
            Dictionary of registered prompts
        """
        return self.registered_prompts

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
        if prompt_name not in self.registered_prompts:
            raise KeyError(f"Prompt not registered: {prompt_name}")

        return self.registered_prompts[prompt_name]["definition"]
