#!/usr/bin/env python3
"""
Test MCP tools functionality
"""

import datetime
from typing import Generator

import pytest

from src.client import SimpleMCPClient


@pytest.fixture
def mcp_client() -> Generator[SimpleMCPClient, None, None]:
    """
    Create and initialize SimpleMCPClient for testing.

    Yields:
        Initialized SimpleMCPClient instance    Handles:
        - Server startup
        - Client initialization
        - Cleanup on test completion
    """
    client = SimpleMCPClient()

    try:
        # Start server
        server_started = client.start_server("python", ["src/server.py"])
        assert server_started, "Failed to start MCP server"

        # Initialize client
        initialized = client.initialize()
        assert initialized, "Failed to initialize MCP client"

        yield client

    finally:
        # Always clean up, even if test fails
        client.close()


def test_get_current_time(mcp_client: SimpleMCPClient) -> None:
    """Test that get_current_time returns a properly formatted datetime string"""
    # Call get_current_time tool
    result = mcp_client.call_tool("get_current_time")

    # Check for standard JSON-RPC error format
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result['error']}"

    # Check for FastMCP error format
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Verify FastMCP response structure
    assert "content" in result, f"Expected 'content' in result, got: {result}"
    assert result["content"], f"Expected non-empty content, got: {result['content']}"
    assert (
        len(result["content"]) > 0
    ), f"Expected content array with items, got: {result['content']}"

    # Extract and verify result format (YYYY-MM-DD HH:MM:SS)
    actual_result = result["content"][0]["text"]

    # Verify it's a valid datetime format
    try:
        datetime.datetime.strptime(actual_result, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pytest.fail(
            f"Expected datetime format 'YYYY-MM-DD HH:MM:SS', got: '{actual_result}'"
        )


def test_generate_greeting_default(mcp_client: SimpleMCPClient) -> None:
    """Test generate_greeting with default name parameter"""
    # Call generate_greeting without parameters
    result = mcp_client.call_tool("generate_greeting")

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Verify response structure
    assert "content" in result, f"Expected 'content' in result, got: {result}"
    assert result[
        "content"
        # Extract greeting message
    ], f"Expected non-empty content, got: {result['content']}"
    greeting = result["content"][0]["text"]

    # Should contain "User" as default name
    assert "User" in greeting, f"Expected 'User' in greeting, got: '{greeting}'"
    # Should be a greeting message (more flexible assertion)
    assert any(
        word in greeting.lower() for word in ["hello", "hi", "greetings", "hey"]
    ), f"Expected greeting words in: '{greeting}'"


def test_generate_greeting_custom_name(mcp_client: SimpleMCPClient) -> None:
    """Test generate_greeting with custom name parameter"""
    custom_name = "Alice"

    # Call generate_greeting with custom name
    result = mcp_client.call_tool("generate_greeting", {"name": custom_name})

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Verify response structure
    assert "content" in result, f"Expected 'content' in result, got: {result}"
    assert result["content"], f"Expected non-empty content, got: {result['content']}"

    # Extract greeting message
    greeting = result["content"][0]["text"]

    # Should contain the custom name
    assert (
        custom_name in greeting
    ), f"Expected '{custom_name}' in greeting, got: '{greeting}'"


def test_calculate_days_until_date_future(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with a future date"""
    # Calculate a date 30 days from now
    future_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime(
        "%Y-%m-%d"
    )

    # Call the tool
    result = mcp_client.call_tool(
        "calculate_days_until_date", {"target_date": future_date}
    )

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Verify response structure
    assert "content" in result, f"Expected 'content' in result, got: {result}"
    assert result["content"], f"Expected non-empty content, got: {result['content']}"

    # Parse the JSON result
    import json

    result_data = json.loads(result["content"][0]["text"])

    # Verify structure and values
    assert "target_date" in result_data
    assert "current_date" in result_data
    assert "days_difference" in result_data
    assert "is_future" in result_data
    assert "is_past" in result_data
    assert "is_today" in result_data

    # Future date should have positive days and is_future=True
    assert (
        result_data["days_difference"] > 0
    ), f"Expected positive days for future date, got: {result_data['days_difference']}"
    assert result_data["is_future"] is True
    assert result_data["is_past"] is False
    assert result_data["is_today"] is False


def test_calculate_days_until_date_past(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with a past date"""
    # Calculate a date 30 days ago
    past_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
        "%Y-%m-%d"
    )

    # Call the tool
    result = mcp_client.call_tool(
        "calculate_days_until_date", {"target_date": past_date}
    )

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Parse the JSON result
    import json

    result_data = json.loads(result["content"][0]["text"])

    # Past date should have negative days and is_past=True
    assert (
        result_data["days_difference"] < 0
    ), f"Expected negative days for past date, got: {result_data['days_difference']}"
    assert result_data["is_future"] is False
    assert result_data["is_past"] is True
    assert result_data["is_today"] is False


def test_calculate_days_until_date_today(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with today's date"""
    # Use today's date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Call the tool
    result = mcp_client.call_tool(
        "calculate_days_until_date", {"target_date": today_date}
    )

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Parse the JSON result
    import json

    result_data = json.loads(result["content"][0]["text"])

    # Today should have 0 or very close to 0 days (allowing for time differences)
    days_diff = result_data["days_difference"]
    assert (
        abs(days_diff) <= 1
    ), f"Expected days difference to be 0 or ±1 for today, got: {days_diff}"

    # If it's exactly 0, should be marked as today
    if days_diff == 0:
        assert result_data["is_today"] is True
        assert result_data["is_future"] is False
        assert result_data["is_past"] is False


def test_calculate_days_until_date_invalid_format(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with invalid date format"""
    # Use invalid date format
    invalid_date = "2024/12/25"  # Wrong format

    # Call the tool
    result = mcp_client.call_tool(
        "calculate_days_until_date", {"target_date": invalid_date}
    )

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Parse the JSON result
    import json

    result_data = json.loads(result["content"][0]["text"])

    # Should contain error message
    assert (
        "error" in result_data
    ), f"Expected error for invalid date format, got: {result_data}"
    assert (
        "YYYY-MM-DD" in result_data["error"]
    ), f"Expected format hint in error message: {result_data['error']}"


def test_get_learning_tips_default(mcp_client: SimpleMCPClient) -> None:
    """Test get_learning_tips with default (no category)"""
    # Call get_learning_tips without parameters
    result = mcp_client.call_tool("get_learning_tips")

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # The result is already a Python object (list), not a JSON string
    # FastMCP automatically serializes Python return values
    content_text = result["content"][0]["text"]

    # Check if it's a JSON string or already parsed
    import json

    try:
        # Try to parse as JSON first
        tips_list = json.loads(content_text)
    except json.JSONDecodeError:
        # If it fails, check if it's a single tip string (first element of the list)
        # In this case, we need to check the actual response format
        assert isinstance(
            content_text, str
        ), f"Expected string content, got: {type(content_text)}"
        assert (
            len(content_text)
            > 0
            # Should contain MCP-related content
        ), f"Expected non-empty content, got: '{content_text}'"
        assert (
            "mcp" in content_text.lower()
            or "tool" in content_text.lower()
            or "server" in content_text.lower()
        ), f"Expected MCP-related content, got: '{content_text}'"
        return

    # If it parsed as JSON, verify it's a list
    assert isinstance(tips_list, list), f"Expected list of tips, got: {type(tips_list)}"
    assert len(tips_list) > 0, f"Expected non-empty tips list, got: {tips_list}"
    # Should contain MCP-related content
    tips_text = " ".join(tips_list).lower()
    assert (
        "mcp" in tips_text or "server" in tips_text or "configure" in tips_text
    ), f"Expected MCP-related tips, got: {tips_list}"


def test_get_learning_tips_specific_categories(mcp_client: SimpleMCPClient) -> None:
    """Test get_learning_tips with specific categories"""
    categories = ["mcp-test"]

    for category in categories:
        # Call get_learning_tips with specific category
        result = mcp_client.call_tool("get_learning_tips", {"category": category})

        # Check for errors
        assert (
            "error" not in result
        ), f"Tool call failed for category '{category}' with JSON-RPC error: {result.get('error')}"
        assert not result.get(
            "isError"
        ), f"Tool call failed for category '{category}' with FastMCP error: {result}"

        # The result might be a string or JSON, handle both cases
        content_text = result["content"][0]["text"]

        import json

        try:
            # Try to parse as JSON first
            tips_list = json.loads(content_text)
            # Should return a list of tips
            assert isinstance(
                tips_list, list
            ), f"Expected list of tips for '{category}', got: {type(tips_list)}"
            assert (
                len(tips_list) > 0
            ), f"Expected non-empty tips list for '{category}', got: {tips_list}"
        except json.JSONDecodeError:
            # If it's not JSON, it should be a string with content
            assert isinstance(
                content_text, str
            ), f"Expected string content for '{category}', got: {type(content_text)}"
            assert (
                len(content_text) > 0
            ), f"Expected non-empty content for '{category}', got: '{content_text}'"


def test_get_learning_tips_invalid_category(mcp_client: SimpleMCPClient) -> None:
    """Test get_learning_tips with invalid category"""
    # Call get_learning_tips with invalid category
    result = mcp_client.call_tool("get_learning_tips", {"category": "invalid_category"})

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # The result might be a string or JSON, handle both cases
    content_text = result["content"][0]["text"]

    import json

    try:
        # Try to parse as JSON first
        response_list = json.loads(content_text)
        # Should return error message in the list
        assert isinstance(
            response_list, list
        ), f"Expected list response, got: {type(response_list)}"
        assert (
            len(response_list) > 0
        ), f"Expected non-empty response list, got: {response_list}"
        assert (
            "Error" in response_list[0] or "not found" in response_list[0]
        ), f"Expected error message, got: {response_list[0]}"
    except json.JSONDecodeError:
        # If it's not JSON, it should be an error string
        assert (
            "Error" in content_text or "not found" in content_text
        ), f"Expected error message, got: '{content_text}'"


def test_list_tools(mcp_client: SimpleMCPClient) -> None:
    """Test that we can list available tools and find expected tools"""
    # Get list of available tools
    tools = mcp_client.list_tools()

    # Verify tools list structure
    assert tools, "Expected non-empty tools list"
    assert len(tools) >= 4, f"Expected at least 4 tools, found {len(tools)} tools"

    # Get tool names
    tool_names = [tool.get("name") for tool in tools]

    # Verify expected tools exist
    expected_tools = [
        "get_current_time",
        "generate_greeting",
        "calculate_days_until_date",
        "get_learning_tips",
    ]
    for expected_tool in expected_tools:
        assert (
            expected_tool in tool_names
        ), f"Expected tool '{expected_tool}' not found in: {tool_names}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
