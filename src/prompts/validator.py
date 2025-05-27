"""
Content validation utilities for JSON-based configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError


class ContentValidator:
    """Validates content configuration against JSON schema."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize validator with schema.
        
        Args:
            schema_path: Path to JSON schema file. If None, uses default schema.
        """
        if schema_path is None:
            # Default to schema in src/data/content_schema.json
            current_dir = Path(__file__).parent
            default_schema_path = current_dir.parent / "data" / "content_schema.json"
            self.schema_path = default_schema_path
        else:
            self.schema_path = Path(schema_path)
        
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
    
    def validate_content(self, content: Dict[str, Any]) -> None:
        """
        Validate content against schema.
        
        Args:
            content: Content dictionary to validate
            
        Raises:
            ValidationError: If content doesn't match schema
        """
        try:
            validate(instance=content, schema=self.schema)
        except ValidationError as e:
            raise ValidationError(f"Content validation failed: {e.message}")
    
    def validate_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """
        Validate a single prompt definition.
        
        Args:
            prompt_data: Prompt definition dictionary
            
        Raises:
            ValidationError: If prompt doesn't match schema
        """
        # Extract the prompt definition schema but keep the full schema context
        prompt_schema_def = self.schema.get("definitions", {}).get("prompt", {})
        if not prompt_schema_def:
            raise ValueError("Prompt schema definition not found")
        
        # Create a complete schema with definitions for reference resolution
        full_prompt_schema = {
            **prompt_schema_def,
            "definitions": self.schema.get("definitions", {})
        }
        
        try:
            validate(instance=prompt_data, schema=full_prompt_schema)
        except ValidationError as e:
            raise ValidationError(f"Prompt validation failed: {e.message}")
    
    def validate_arguments(self, prompt_args: list, provided_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and process prompt arguments.
        
        Args:
            prompt_args: List of argument definitions from prompt
            provided_args: Arguments provided by user
            
        Returns:
            Processed arguments with defaults applied
            
        Raises:
            ValueError: If required arguments are missing or types don't match
        """
        processed_args = {}
        
        # Create lookup for argument definitions
        arg_definitions = {arg["name"]: arg for arg in prompt_args}
        
        # Check all provided arguments are valid
        for arg_name in provided_args:
            if arg_name not in arg_definitions:
                raise ValueError(f"Unknown argument: {arg_name}")
        
        # Process each defined argument
        for arg_def in prompt_args:
            arg_name = arg_def["name"]
            is_required = arg_def.get("required", False)
            default_value = arg_def.get("default")
            expected_type = arg_def.get("type", "string")
            
            if arg_name in provided_args:
                value = provided_args[arg_name]
                # Basic type checking
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Argument '{arg_name}' must be a string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Argument '{arg_name}' must be a number")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Argument '{arg_name}' must be a boolean")
                
                processed_args[arg_name] = value
            elif is_required:
                raise ValueError(f"Required argument missing: {arg_name}")
            elif default_value is not None:
                processed_args[arg_name] = default_value
        
        return processed_args
