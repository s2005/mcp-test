import json
import os

import pytest
from jsonschema import ValidationError, validate


def load_schema():
    """Load the content schema from file."""
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "data", "content_schema.json"
    )
    with open(schema_path, "r") as f:
        return json.load(f)


def load_content():
    """Load the existing content.json file."""
    content_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "data", "content.json"
    )
    with open(content_path, "r") as f:
        return json.load(f)


class TestSchemaValidation:
    """Test suite for content schema validation."""

    def test_schema_validates_existing_content(self):
        """Test that the schema validates the existing content.json file."""
        schema = load_schema()
        content = load_content()

        # Should not raise any exception
        validate(instance=content, schema=schema)

    def test_schema_validates_messages_section(self):
        """Test that the schema validates the new messages section."""
        schema = load_schema()

        # Valid content with messages section
        valid_content = {
            "tips": {"mcp": ["Test tip with MCP"]},
            "messages": {
                "greetings": [
                    "Hello {name}! Welcome to MCP!",
                    "Hi {name}! Ready to explore?",
                ]
            },
            "prompts": {
                "development": {
                    "test_prompt": {
                        "name": "test_prompt",
                        "description": "A test prompt",
                        "template": "Test template",
                        "role": "user",
                    }
                }
            },
        }

        # Should not raise any exception
        validate(instance=valid_content, schema=schema)

    def test_schema_rejects_invalid_greetings(self):
        """Test that the schema rejects greeting messages without {name} placeholder."""
        schema = load_schema()

        # Invalid content - greeting without {name} placeholder
        invalid_content = {
            "messages": {
                "greetings": ["Hello! Welcome to MCP!"]  # Missing {name} placeholder
            }
        }

        with pytest.raises(ValidationError):
            validate(instance=invalid_content, schema=schema)

    def test_schema_rejects_empty_greetings(self):
        """Test that the schema rejects empty greetings array."""
        schema = load_schema()

        # Invalid content - empty greetings array
        invalid_content = {"messages": {"greetings": []}}  # Empty array not allowed

        with pytest.raises(ValidationError):
            validate(instance=invalid_content, schema=schema)

    def test_schema_allows_custom_message_categories(self):
        """Test that the schema allows custom message categories."""
        schema = load_schema()

        # Valid content with custom message category
        valid_content = {
            "messages": {
                "greetings": ["Hello {name}!"],
                "farewells": ["Goodbye!", "See you later!"],
                "custom_messages": ["Custom message 1", "Custom message 2"],
            }
        }

        # Should not raise any exception
        validate(instance=valid_content, schema=schema)

    def test_schema_validates_minimal_content(self):
        """Test that the schema validates minimal valid content."""
        schema = load_schema()

        # Minimal valid content
        minimal_content = {}

        # Should not raise any exception - all properties are optional
        validate(instance=minimal_content, schema=schema)

    def test_schema_validates_tips_only(self):
        """Test that the schema validates content with only tips."""
        schema = load_schema()

        # Content with only tips
        tips_only = {
            "tips": {
                "python": ["Use virtual environments"],
                "docker": ["Use multi-stage builds"],
            }
        }

        # Should not raise any exception
        validate(instance=tips_only, schema=schema)

    def test_schema_validates_prompts_only(self):
        """Test that the schema validates content with only prompts."""
        schema = load_schema()

        # Content with only prompts
        prompts_only = {
            "prompts": {
                "development": {
                    "test_prompt": {
                        "name": "test_prompt",
                        "description": "A test prompt",
                        "template": "Test template for {param}",
                        "arguments": [
                            {
                                "name": "param",
                                "description": "Test parameter",
                                "required": True,
                                "type": "string",
                            }
                        ],
                        "role": "user",
                    }
                }
            }
        }

        # Should not raise any exception
        validate(instance=prompts_only, schema=schema)
