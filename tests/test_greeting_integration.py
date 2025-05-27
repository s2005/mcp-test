"""Integration tests for externalized greeting tools."""

import json
import os
import tempfile

from src.content.content_manager import ContentManager
from src.tools.greeting_tools import register_greeting_tools


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self):
        self.tools = {}

    def tool(self):
        """Decorator for registering tools."""

        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class TestGreetingIntegration:
    """Integration tests for greeting tools with ContentManager."""

    def test_greeting_tool_uses_json_content(self):
        """Test that greeting tool generates messages from JSON content."""
        # Create test content
        test_content = {
            "messages": {
                "greetings": [
                    "Hello {name}! Welcome to testing!",
                    "Hi {name}! This is a test greeting!",
                ]
            },
            "tips": {"mcp": ["Test tip"]},
            "prompts": {},
        }

        # Initialize ContentManager and mock MCP
        content_manager = ContentManager(test_content)
        mock_mcp = MockMCP()

        # Register greeting tools
        register_greeting_tools(mock_mcp, content_manager)

        # Test that tool was registered
        assert "generate_greeting" in mock_mcp.tools

        # Test greeting generation
        greeting_func = mock_mcp.tools["generate_greeting"]
        greeting = greeting_func("TestUser")

        # Verify greeting is from JSON content
        assert "TestUser" in greeting
        assert any(
            template.format(name="TestUser") == greeting
            for template in test_content["messages"]["greetings"]
        )

    def test_greeting_tool_with_default_name(self):
        """Test greeting tool with default name parameter."""
        test_content = {"messages": {"greetings": ["Hello {name}! Welcome!"]}}

        content_manager = ContentManager(test_content)
        mock_mcp = MockMCP()
        register_greeting_tools(mock_mcp, content_manager)

        greeting_func = mock_mcp.tools["generate_greeting"]
        greeting = greeting_func()  # No name provided, should use default "User"

        assert "User" in greeting
        assert greeting == "Hello User! Welcome!"

    def test_greeting_tool_fallback_behavior(self):
        """Test greeting tool fallback when no greetings are configured."""
        # Content with no greetings
        test_content = {"tips": {"mcp": ["Test tip"]}, "prompts": {}}

        content_manager = ContentManager(test_content)
        mock_mcp = MockMCP()
        register_greeting_tools(mock_mcp, content_manager)

        greeting_func = mock_mcp.tools["generate_greeting"]
        greeting = greeting_func("TestUser")

        # Should use fallback greeting
        assert greeting == "Hello TestUser! Welcome to the MCP test server!"

    def test_greeting_tool_with_multiple_templates(self):
        """Test that greeting tool randomly selects from multiple templates."""
        test_content = {
            "messages": {
                "greetings": [
                    "Hello {name}! Option 1",
                    "Hi {name}! Option 2",
                    "Greetings {name}! Option 3",
                    "Hey {name}! Option 4",
                ]
            }
        }

        content_manager = ContentManager(test_content)
        mock_mcp = MockMCP()
        register_greeting_tools(mock_mcp, content_manager)

        greeting_func = mock_mcp.tools["generate_greeting"]

        # Generate multiple greetings to test randomness
        greetings = [greeting_func("TestUser") for _ in range(20)]

        # All greetings should contain the name
        assert all("TestUser" in greeting for greeting in greetings)

        # With 20 generations, we should likely see multiple different greetings
        unique_greetings = set(greetings)
        assert len(unique_greetings) > 1  # Should have some variety

        # All greetings should be valid options
        expected_greetings = {
            "Hello TestUser! Option 1",
            "Hi TestUser! Option 2",
            "Greetings TestUser! Option 3",
            "Hey TestUser! Option 4",
        }
        assert unique_greetings.issubset(expected_greetings)

    def test_dynamic_content_loading(self):
        """Test greeting integration with dynamically loaded content."""
        # Create dynamic content
        dynamic_content = {
            "messages": {
                "greetings": [
                    "Welcome {name} to our dynamic test!",
                    "Hello {name}! This content was loaded dynamically.",
                ]
            },
            "tips": {"testing": ["Dynamic test tip"]},
            "prompts": {},
        }

        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(dynamic_content, f)
            temp_file = f.name

        try:
            # Load content from file
            with open(temp_file, "r") as f:
                loaded_content = json.load(f)

            # Test integration
            content_manager = ContentManager(loaded_content)
            mock_mcp = MockMCP()
            register_greeting_tools(mock_mcp, content_manager)

            greeting_func = mock_mcp.tools["generate_greeting"]
            greeting = greeting_func("DynamicUser")

            assert "DynamicUser" in greeting
            assert any(
                template.format(name="DynamicUser") == greeting
                for template in dynamic_content["messages"]["greetings"]
            )

        finally:
            # Clean up
            os.unlink(temp_file)

    def test_greeting_tool_empty_greetings_list(self):
        """Test greeting tool behavior with empty greetings list."""
        test_content = {"messages": {"greetings": []}}  # Empty list

        content_manager = ContentManager(test_content)
        mock_mcp = MockMCP()
        register_greeting_tools(mock_mcp, content_manager)

        greeting_func = mock_mcp.tools["generate_greeting"]
        greeting = greeting_func("TestUser")

        # Should use fallback
        assert greeting == "Hello TestUser! Welcome to the MCP test server!"
