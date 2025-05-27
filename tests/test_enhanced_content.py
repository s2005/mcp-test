"""Tests for enhanced content.json with messages section."""

import json
import os

from jsonschema import validate

from src.content.content_manager import ContentManager


def load_schema():
    """Load the content schema from file."""
    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "data", "content_schema.json"
    )
    with open(schema_path, "r") as f:
        return json.load(f)


def load_content():
    """Load the enhanced content.json file."""
    content_path = os.path.join(
        os.path.dirname(__file__), "..", "src", "data", "content.json"
    )
    with open(content_path, "r") as f:
        return json.load(f)


class TestEnhancedContent:
    """Test suite for enhanced content with messages section."""

    def test_enhanced_content_validates_against_schema(self):
        """Test that enhanced content.json validates against the schema."""
        schema = load_schema()
        content = load_content()

        # Should not raise any exception
        validate(instance=content, schema=schema)

    def test_content_has_messages_section(self):
        """Test that content.json contains the messages section."""
        content = load_content()

        assert "messages" in content
        assert isinstance(content["messages"], dict)

    def test_content_has_greetings(self):
        """Test that content.json contains greeting messages."""
        content = load_content()

        assert "greetings" in content["messages"]
        greetings = content["messages"]["greetings"]

        assert isinstance(greetings, list)
        assert len(greetings) > 0

        # Check that all greetings contain {name} placeholder
        for greeting in greetings:
            assert "{name}" in greeting
            assert isinstance(greeting, str)
            assert len(greeting) > 0

    def test_content_manager_can_access_new_content(self):
        """Test that ContentManager can access all new content sections."""
        content = load_content()
        manager = ContentManager(content)

        # Test greetings access
        greetings = manager.get_greetings()
        assert len(greetings) == 4
        assert all("{name}" in greeting for greeting in greetings)

        # Test that original content still works
        mcp_tips = manager.get_tips("mcp")
        assert len(mcp_tips) > 0

        python_tips = manager.get_tips("python")
        assert len(python_tips) > 0

        docker_tips = manager.get_tips("docker")
        assert len(docker_tips) > 0

    def test_no_regression_in_existing_functionality(self):
        """Test that existing prompt/tips functionality is preserved."""
        content = load_content()
        manager = ContentManager(content)

        # Test tips functionality
        all_tips = manager.get_all_tips()
        assert "mcp" in all_tips
        assert "python" in all_tips
        assert "docker" in all_tips

        tip_categories = manager.get_tip_categories()
        assert len(tip_categories) >= 3

        # Test prompts functionality
        all_prompts = manager.get_prompts()
        assert "development" in all_prompts
        assert "learning" in all_prompts
        assert "planning" in all_prompts

        prompt_categories = manager.get_prompt_categories()
        assert len(prompt_categories) >= 3

    def test_greeting_message_content(self):
        """Test the specific content of greeting messages."""
        content = load_content()
        greetings = content["messages"]["greetings"]

        expected_greetings = [
            "Hello {name}! Welcome to the MCP test server!",
            "Hi there, {name}! Great to see you using MCP!",
            "Greetings {name}! Hope you're having a fantastic day!",
            "Hey {name}! Ready to explore Model Context Protocol?",
        ]

        assert len(greetings) == len(expected_greetings)
        for expected in expected_greetings:
            assert expected in greetings

    def test_content_structure_integrity(self):
        """Test that the overall content structure is maintained."""
        content = load_content()

        # Check main sections exist
        assert "messages" in content
        assert "tips" in content
        assert "prompts" in content

        # Check messages structure
        messages = content["messages"]
        assert "greetings" in messages
        assert isinstance(messages["greetings"], list)

        # Check tips structure
        tips = content["tips"]
        assert isinstance(tips, dict)
        assert len(tips) > 0

        # Check prompts structure
        prompts = content["prompts"]
        assert isinstance(prompts, dict)
        assert len(prompts) > 0
