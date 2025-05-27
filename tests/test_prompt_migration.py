"""
Tests for the prompt migration from code to JSON.
"""

import pytest
import json
from pathlib import Path
from src.prompts.validator import ContentValidator
from src.prompts.prompt_loader import JSONPromptLoader, load_content_from_json
from src.prompts.prompt_registry import PromptRegistry

class TestPromptMigration:
    """Test the prompt migration functionality."""

    def test_content_schema_validation(self):
        """Test that the content schema validates correctly."""
        validator = ContentValidator()
        
        # Load the actual content.json file
        content = load_content_from_json()
        
        # Should not raise an exception
        validator.validate_content(content)
        
        # Verify it has both tips and prompts
        assert "tips" in content
        assert "prompts" in content

    def test_prompt_loader(self):
        """Test that prompts can be loaded from JSON."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Load all prompts
        prompts = loader.load_prompts()
        
        # Should have all 5 prompts
        expected_prompts = {
            "code_review_prompt",
            "mcp_development_prompt",
            "learning_plan_prompt",
            "debugging_assistant_prompt",
            "project_planning_prompt"
        }
        
        assert set(prompts.keys()) == expected_prompts
        
        # Test prompt function creation
        for prompt_name, prompt_def in prompts.items():
            func = loader.create_prompt_function(prompt_name, prompt_def)
            assert callable(func)
            assert func.__name__ == prompt_name
            assert func.__doc__ is not None

    def test_code_review_prompt_function(self):
        """Test the code review prompt function works correctly."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Get the code review prompt
        prompts = loader.load_prompts()
        prompt_def = prompts["code_review_prompt"]
        func = loader.create_prompt_function("code_review_prompt", prompt_def)
        
        # Test with default arguments
        result = func()
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert "python" in result[0]["content"].lower()
        assert "function" in result[0]["content"].lower()
        
        # Test with custom arguments
        result = func(language="javascript", code_type="class")
        assert "javascript" in result[0]["content"].lower()
        assert "class" in result[0]["content"].lower()

    def test_learning_plan_prompt_function(self):
        """Test the learning plan prompt function works correctly."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Get the learning plan prompt
        prompts = loader.load_prompts()
        prompt_def = prompts["learning_plan_prompt"]
        func = loader.create_prompt_function("learning_plan_prompt", prompt_def)
        
        # Test with required topic argument
        result = func(topic="Docker")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert "Docker" in result[0]["content"]
        assert "beginner" in result[0]["content"]  # default skill level
        assert "1 month" in result[0]["content"]   # default timeframe

    def test_argument_validation(self):
        """Test that argument validation works correctly."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Get the learning plan prompt (has required argument)
        prompts = loader.load_prompts()
        prompt_def = prompts["learning_plan_prompt"]
        func = loader.create_prompt_function("learning_plan_prompt", prompt_def)
        
        # Should raise error for missing required argument
        with pytest.raises(ValueError, match="Required argument missing: topic"):
            func()
        
        # Should work with required argument
        result = func(topic="Python")
        assert "Python" in result[0]["content"]

    def test_mcp_development_prompt_special_processing(self):
        """Test that MCP development prompt gets special processing."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Get the MCP development prompt
        prompts = loader.load_prompts()
        prompt_def = prompts["mcp_development_prompt"]
        func = loader.create_prompt_function("mcp_development_prompt", prompt_def)
        
        # Test with tool component type
        result = func(component_type="tool")
        content_text = result[0]["content"]
        assert "functions that can be called by the LLM" in content_text
        
        # Test with resource component type
        result = func(component_type="resource")
        content_text = result[0]["content"]
        assert "static or dynamic content" in content_text

    def test_debugging_prompt_special_processing(self):
        """Test that debugging prompt gets special processing."""
        content = load_content_from_json()
        validator = ContentValidator()
        loader = JSONPromptLoader(content, validator)
        
        # Get the debugging prompt
        prompts = loader.load_prompts()
        prompt_def = prompts["debugging_assistant_prompt"]
        func = loader.create_prompt_function("debugging_assistant_prompt", prompt_def)
        
        # Test with runtime error type
        result = func(error_type="runtime")
        content_text = result[0]["content"]
        assert "stack trace analysis" in content_text
        
        # Test with syntax error type
        result = func(error_type="syntax")
        content_text = result[0]["content"]
        assert "code parsing" in content_text

    def test_prompt_registry(self):
        """Test that the prompt registry works correctly."""
        content = load_content_from_json()
        registry = PromptRegistry()
        
        # Mock MCP server for testing
        class MockMCP:
            def __init__(self):
                self.registered_prompts = []
            
            def prompt(self):
                def decorator(func):
                    self.registered_prompts.append(func)
                    return func
                return decorator
        
        mock_mcp = MockMCP()
        
        # Register prompts
        registry.register_prompts_from_json(mock_mcp, content)
        
        # Should have registered 5 prompts
        assert len(mock_mcp.registered_prompts) == 5
        
        # Should have stored prompt definitions
        registered_prompts = registry.get_registered_prompts()
        assert len(registered_prompts) == 5

if __name__ == "__main__":
    pytest.main([__file__])
