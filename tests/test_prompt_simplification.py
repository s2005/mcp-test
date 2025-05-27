"""Tests for prompt loader simplification."""

from src.prompts.prompt_loader import JSONPromptLoader
from src.prompts.validator import ContentValidator


class TestPromptSimplification:
    """Test suite for simplified prompt loader functionality."""

    def test_simple_template_substitution(self):
        """Test that prompt loader uses simple template substitution."""
        content_data = {
            "prompts": {
                "test": {
                    "simple_prompt": {
                        "name": "simple_prompt",
                        "description": "A simple test prompt",
                        "template": "Hello {name}! Your skill level is {skill_level}.",
                        "arguments": [
                            {
                                "name": "name",
                                "description": "User name",
                                "required": True,
                                "type": "string",
                            },
                            {
                                "name": "skill_level",
                                "description": "User skill level",
                                "required": False,
                                "default": "beginner",
                                "type": "string",
                            },
                        ],
                        "role": "user",
                    }
                }
            }
        }

        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        # Load prompts
        prompts = loader.load_prompts()
        assert "simple_prompt" in prompts

        # Create prompt function
        prompt_func = loader.create_prompt_function(
            "simple_prompt", prompts["simple_prompt"]
        )

        # Test simple substitution
        result = prompt_func(name="TestUser", skill_level="intermediate")

        assert len(result) == 1
        assert result[0]["role"] == "user"
        assert (
            result[0]["content"] == "Hello TestUser! Your skill level is intermediate."
        )

    def test_no_complex_processing_methods_exist(self):
        """Test that complex processing methods have been removed."""
        content_data = {"prompts": {}}
        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        # These methods should no longer exist
        assert not hasattr(loader, "_process_mcp_development_args")
        assert not hasattr(loader, "_process_debugging_args")
        assert not hasattr(loader, "_preprocess_template")
        assert not hasattr(loader, "_prepare_template_args")

    def test_existing_prompt_functionality_preserved(self):
        """Test that existing prompt functionality is preserved."""
        content_data = {
            "prompts": {
                "development": {
                    "test_prompt": {
                        "name": "test_prompt",
                        "description": "Test development prompt",
                        "template": "Review this {language} code for {focus_area}.",
                        "arguments": [
                            {
                                "name": "language",
                                "description": "Programming language",
                                "required": True,
                                "type": "string",
                            },
                            {
                                "name": "focus_area",
                                "description": "Review focus area",
                                "required": False,
                                "default": "best practices",
                                "type": "string",
                            },
                        ],
                        "role": "user",
                    }
                }
            }
        }

        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        # Load and test prompt
        prompts = loader.load_prompts()
        prompt_func = loader.create_prompt_function(
            "test_prompt", prompts["test_prompt"]
        )

        result = prompt_func(language="Python", focus_area="security")

        assert len(result) == 1
        assert result[0]["content"] == "Review this Python code for security."
        assert result[0]["role"] == "user"

    def test_missing_placeholder_handling(self):
        """Test graceful handling of missing template placeholders."""
        content_data = {
            "prompts": {
                "test": {
                    "incomplete_prompt": {
                        "name": "incomplete_prompt",
                        "description": "Prompt with missing placeholder",
                        "template": "Hello {name}! Your level is {missing_param}.",
                        "arguments": [
                            {
                                "name": "name",
                                "description": "User name",
                                "required": True,
                                "type": "string",
                            }
                        ],
                        "role": "user",
                    }
                }
            }
        }

        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        prompts = loader.load_prompts()
        prompt_func = loader.create_prompt_function(
            "incomplete_prompt", prompts["incomplete_prompt"]
        )

        # Should handle missing placeholder gracefully
        result = prompt_func(name="TestUser")

        assert len(result) == 1
        # Should return original template when formatting fails
        assert result[0]["content"] == "Hello {name}! Your level is {missing_param}."

    def test_dynamic_prompts_with_various_templates(self):
        """Test various prompt templates with simple substitution."""
        test_cases = [
            {
                "template": "Simple message: {message}",
                "args": {"message": "Hello World"},
                "expected": "Simple message: Hello World",
                "arguments": [
                    {
                        "name": "message",
                        "description": "Message to display",
                        "required": True,
                        "type": "string",
                    }
                ],
            },
            {
                "template": "Multi-param: {param1} and {param2}",
                "args": {"param1": "first", "param2": "second"},
                "expected": "Multi-param: first and second",
                "arguments": [
                    {
                        "name": "param1",
                        "description": "First parameter",
                        "required": True,
                        "type": "string",
                    },
                    {
                        "name": "param2",
                        "description": "Second parameter",
                        "required": True,
                        "type": "string",
                    },
                ],
            },
            {
                "template": "No parameters",
                "args": {},
                "expected": "No parameters",
                "arguments": [],
            },
            {
                "template": "Default value test: {optional}",
                "args": {},
                "expected": "Default value test: default_value",
                "arguments": [
                    {
                        "name": "optional",
                        "description": "Optional parameter",
                        "required": False,
                        "default": "default_value",
                        "type": "string",
                    }
                ],
            },
        ]

        for i, test_case in enumerate(test_cases):
            content_data = {
                "prompts": {
                    "test": {
                        f"test_prompt_{i}": {
                            "name": f"test_prompt_{i}",
                            "description": f"Test prompt {i}",
                            "template": test_case["template"],
                            "arguments": test_case["arguments"],
                            "role": "user",
                        }
                    }
                }
            }

            validator = ContentValidator()
            loader = JSONPromptLoader(content_data, validator)

            prompts = loader.load_prompts()
            prompt_func = loader.create_prompt_function(
                f"test_prompt_{i}", prompts[f"test_prompt_{i}"]
            )

            result = prompt_func(**test_case["args"])

            assert result[0]["content"] == test_case["expected"]

    def test_prompt_function_metadata(self):
        """Test that prompt function metadata is set correctly."""
        content_data = {
            "prompts": {
                "test": {
                    "metadata_test": {
                        "name": "metadata_test",
                        "description": "Test prompt for metadata",
                        "template": "Test template",
                        "arguments": [
                            {
                                "name": "test_arg",
                                "description": "Test argument",
                                "required": False,
                                "type": "string",
                            }
                        ],
                        "role": "assistant",
                    }
                }
            }
        }

        validator = ContentValidator()
        loader = JSONPromptLoader(content_data, validator)

        prompts = loader.load_prompts()
        prompt_func = loader.create_prompt_function(
            "metadata_test", prompts["metadata_test"]
        )

        # Check function metadata
        assert prompt_func.__name__ == "metadata_test"
        assert prompt_func.__doc__ == "Test prompt for metadata"
        assert hasattr(prompt_func, "_mcp_arguments")
        assert len(prompt_func._mcp_arguments) == 1
        assert prompt_func._mcp_arguments[0]["name"] == "test_arg"

        # Test function execution
        result = prompt_func()
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "Test template"
