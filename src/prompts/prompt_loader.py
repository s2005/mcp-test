"""
JSON-based prompt loader for MCP servers.
"""

import json
from typing import Dict, Any, List, Callable, Optional
from pathlib import Path
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
    
    def create_prompt_function(self, prompt_name: str, prompt_def: Dict[str, Any]) -> Callable:
        """
        Create MCP prompt function from JSON definition.
        
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
            
            # Handle special processing for certain prompts
            if "mcp_development_prompt" in prompt_name:
                processed_args = self._process_mcp_development_args(processed_args)
            elif "debugging_assistant_prompt" in prompt_name:
                processed_args = self._process_debugging_args(processed_args)
            
            # Format template with processed arguments
            template = prompt_def["template"]
            try:
                # Pre-process template to handle method calls like .upper()
                preprocessed_template = self._preprocess_template(template, processed_args)
                formatted_content = preprocessed_template.format(**processed_args)
            except KeyError as e:
                # Handle missing placeholders gracefully
                formatted_content = template
                print(f"Warning: Missing placeholder in template: {e}")
            
            # Return message with appropriate role
            role = prompt_def.get("role", "user")
            return [
                {
                    "role": role,
                    "content": formatted_content
                }
            ]
        
        # Set function metadata
        prompt_function.__name__ = prompt_name
        prompt_function.__doc__ = prompt_def.get("description", f"Generated prompt: {prompt_name}")
        
        # Add argument information to function for MCP registration
        if "arguments" in prompt_def:
            prompt_function._mcp_arguments = prompt_def["arguments"]
        
        return prompt_function
    
    def _prepare_template_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare template arguments by adding variations with method calls.
        
        This handles template expressions like {variable.upper()} by creating
        additional keys with the method applied.
        
        Args:
            args: Original arguments dictionary
            
        Returns:
            Enhanced arguments dictionary with method variations
        """
        import re
        enhanced_args = args.copy()
        
        # For each string argument, add common method variations
        for key, value in args.items():
            if isinstance(value, str):
                # Create keys for method calls that can be used in templates
                enhanced_args[f"{key}.upper()"] = value.upper()
                enhanced_args[f"{key}.lower()"] = value.lower()
                enhanced_args[f"{key}.title()"] = value.title()
                enhanced_args[f"{key}.capitalize()"] = value.capitalize()
        
        return enhanced_args
    
    def _preprocess_template(self, template: str, args: Dict[str, Any]) -> str:
        """
        Preprocess template to handle method calls like {variable.upper()}.
        
        Args:
            template: Template string with potential method calls
            args: Arguments dictionary
            
        Returns:
            Preprocessed template string
        """
        import re
        
        # Find all method call patterns like {variable.method()}
        method_pattern = r'\{(\w+)\.(\w+)\(\)\}'
        
        def replace_method_call(match):
            var_name = match.group(1)
            method_name = match.group(2)
            
            if var_name in args and isinstance(args[var_name], str):
                value = args[var_name]
                if method_name == 'upper':
                    return value.upper()
                elif method_name == 'lower':
                    return value.lower()
                elif method_name == 'title':
                    return value.title()
                elif method_name == 'capitalize':
                    return value.capitalize()
            
            # If we can't resolve it, return the original
            return match.group(0)
        
        # Replace all method calls in the template
        return re.sub(method_pattern, replace_method_call, template)
    
    def _process_mcp_development_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process arguments specific to MCP development prompt."""
        component_type = args.get("component_type", "tool")
        
        # Component guidance mapping
        component_guidance = {
            "tool": "functions that can be called by the LLM to perform actions",
            "resource": "static or dynamic content that can be accessed by the LLM", 
            "prompt": "template messages that help structure LLM interactions",
            "server": "complete MCP server with multiple tools, resources, and prompts"
        }
        
        args["component_guidance"] = component_guidance.get(component_type, "MCP components")
        return args
    
    def _process_debugging_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Process arguments specific to debugging assistant prompt."""
        error_type = args.get("error_type", "runtime")
        
        # Debugging steps mapping
        debugging_steps = {
            "runtime": "stack trace analysis, variable inspection, and runtime state examination",
            "syntax": "code parsing, syntax validation, and formatting issues",
            "logic": "algorithm review, test case analysis, and expected vs actual behavior",
            "performance": "profiling, bottleneck identification, and optimization opportunities"
        }
        
        args["debugging_steps"] = debugging_steps.get(error_type, "general debugging methodology")
        return args
    
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
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in content file: {e}")
    
    # Validate content against schema
    validator = ContentValidator()
    validator.validate_content(content)
    
    return content
