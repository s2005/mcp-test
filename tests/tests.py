#!/usr/bin/env python3
"""
Test LinkedIn Demo MCP server using pytest
"""

import pytest
import datetime
from typing import Generator
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
        pytest.fail(f"Expected datetime format 'YYYY-MM-DD HH:MM:SS', got: '{actual_result}'")


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
    assert result["content"], f"Expected non-empty content, got: {result['content']}"    # Extract greeting message
    greeting = result["content"][0]["text"]
    
    # Should contain "User" as default name
    assert "User" in greeting, f"Expected 'User' in greeting, got: '{greeting}'"
    # Should be a greeting message (more flexible assertion)
    assert any(word in greeting.lower() for word in ["hello", "hi", "greetings", "hey"]), f"Expected greeting words in: '{greeting}'"


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
    assert custom_name in greeting, f"Expected '{custom_name}' in greeting, got: '{greeting}'"


def test_calculate_days_until_date_future(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with a future date"""
    # Calculate a date 30 days from now
    future_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Call the tool
    result = mcp_client.call_tool("calculate_days_until_date", {"target_date": future_date})

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
    assert result_data["days_difference"] > 0, f"Expected positive days for future date, got: {result_data['days_difference']}"
    assert result_data["is_future"] is True
    assert result_data["is_past"] is False
    assert result_data["is_today"] is False


def test_calculate_days_until_date_past(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with a past date"""
    # Calculate a date 30 days ago
    past_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Call the tool
    result = mcp_client.call_tool("calculate_days_until_date", {"target_date": past_date})

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Parse the JSON result
    import json
    result_data = json.loads(result["content"][0]["text"])
    
    # Past date should have negative days and is_past=True
    assert result_data["days_difference"] < 0, f"Expected negative days for past date, got: {result_data['days_difference']}"
    assert result_data["is_future"] is False
    assert result_data["is_past"] is True
    assert result_data["is_today"] is False


def test_calculate_days_until_date_today(mcp_client: SimpleMCPClient) -> None:
    """Test calculate_days_until_date with today's date"""
    # Use today's date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Call the tool
    result = mcp_client.call_tool("calculate_days_until_date", {"target_date": today_date})

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
    assert abs(days_diff) <= 1, f"Expected days difference to be 0 or ±1 for today, got: {days_diff}"
    
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
    result = mcp_client.call_tool("calculate_days_until_date", {"target_date": invalid_date})

    # Check for errors
    assert (
        "error" not in result
    ), f"Tool call failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Tool call failed with FastMCP error: {result}"

    # Parse the JSON result
    import json
    result_data = json.loads(result["content"][0]["text"])
    
    # Should contain error message
    assert "error" in result_data, f"Expected error for invalid date format, got: {result_data}"
    assert "YYYY-MM-DD" in result_data["error"], f"Expected format hint in error message: {result_data['error']}"


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
        assert isinstance(content_text, str), f"Expected string content, got: {type(content_text)}"
        assert len(content_text) > 0, f"Expected non-empty content, got: '{content_text}'"
        # Should contain MCP-related content
        assert "mcp" in content_text.lower() or "tool" in content_text.lower(), f"Expected MCP-related content, got: '{content_text}'"
        return
    
    # If it parsed as JSON, verify it's a list
    assert isinstance(tips_list, list), f"Expected list of tips, got: {type(tips_list)}"
    assert len(tips_list) > 0, f"Expected non-empty tips list, got: {tips_list}"
    
    # Should contain MCP-related content
    tips_text = " ".join(tips_list).lower()
    assert "mcp" in tips_text, f"Expected MCP-related tips, got: {tips_list}"


def test_get_learning_tips_specific_categories(mcp_client: SimpleMCPClient) -> None:
    """Test get_learning_tips with specific categories"""
    categories = ["mcp", "python", "docker"]
    
    for category in categories:
        # Call get_learning_tips with specific category
        result = mcp_client.call_tool("get_learning_tips", {"category": category})

        # Check for errors
        assert (
            "error" not in result
        ), f"Tool call failed for category '{category}' with JSON-RPC error: {result.get('error')}"
        assert not result.get("isError"), f"Tool call failed for category '{category}' with FastMCP error: {result}"

        # The result might be a string or JSON, handle both cases
        content_text = result["content"][0]["text"]
        
        import json
        try:
            # Try to parse as JSON first
            tips_list = json.loads(content_text)
            # Should return a list of tips
            assert isinstance(tips_list, list), f"Expected list of tips for '{category}', got: {type(tips_list)}"
            assert len(tips_list) > 0, f"Expected non-empty tips list for '{category}', got: {tips_list}"
        except json.JSONDecodeError:
            # If it's not JSON, it should be a string with content
            assert isinstance(content_text, str), f"Expected string content for '{category}', got: {type(content_text)}"
            assert len(content_text) > 0, f"Expected non-empty content for '{category}', got: '{content_text}'"


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
        assert isinstance(response_list, list), f"Expected list response, got: {type(response_list)}"
        assert len(response_list) > 0, f"Expected non-empty response list, got: {response_list}"
        assert "Error" in response_list[0] or "not found" in response_list[0], f"Expected error message, got: {response_list[0]}"
    except json.JSONDecodeError:
        # If it's not JSON, it should be an error string
        assert "Error" in content_text or "not found" in content_text, f"Expected error message, got: '{content_text}'"


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
    expected_tools = ["get_current_time", "generate_greeting", "calculate_days_until_date", "get_learning_tips"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Expected tool '{expected_tool}' not found in: {tool_names}"


def test_list_resources(mcp_client: SimpleMCPClient) -> None:
    """Test that we can list available resources"""
    # Get list of available resources
    resources = mcp_client.list_resources()

    # Verify resources list structure
    assert resources, "Expected non-empty resources list"
    assert len(resources) >= 1, f"Expected at least 1 resource, found {len(resources)} resources"

    # Get resource URIs
    resource_uris = [resource.get("uri") for resource in resources]
    
    # Should contain tips resources
    tips_resources = [uri for uri in resource_uris if uri and "tips://" in uri]
    assert len(tips_resources) > 0, f"Expected tips:// resources, found URIs: {resource_uris}"


def test_read_resource_mcp_tips(mcp_client: SimpleMCPClient) -> None:
    """Test reading the MCP tips resource"""
    # Read the MCP tips resource
    result = mcp_client.read_resource("tips://mcp")

    # Check for errors
    assert (
        "error" not in result
    ), f"Resource read failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Resource read failed with FastMCP error: {result}"

    # Verify response structure
    assert "contents" in result, f"Expected 'contents' in result, got: {result}"
    assert result["contents"], f"Expected non-empty contents, got: {result['contents']}"
    assert len(result["contents"]) > 0, f"Expected contents array with items, got: {result['contents']}"

    # Extract content
    content = result["contents"][0]["text"]
    
    # Should contain MCP-related content
    assert "MCP" in content, f"Expected MCP content in resource, got: {content[:100]}..."
    assert "tips" in content.lower(), f"Expected tips content in resource, got: {content[:100]}..."


def test_read_resource_category_tips(mcp_client: SimpleMCPClient) -> None:
    """Test reading category-specific tips resources"""
    categories = ["mcp", "python", "docker"]
    
    for category in categories:
        uri = f"tips://category/{category}"
        
        # Read the category tips resource
        result = mcp_client.read_resource(uri)

        # Check for errors
        assert (
            "error" not in result
        ), f"Resource read failed for '{uri}' with JSON-RPC error: {result.get('error')}"
        assert not result.get("isError"), f"Resource read failed for '{uri}' with FastMCP error: {result}"

        # Verify response structure
        assert "contents" in result, f"Expected 'contents' in result for '{uri}', got: {result}"
        assert result["contents"], f"Expected non-empty contents for '{uri}', got: {result['contents']}"

        # Extract content
        content = result["contents"][0]["text"]
        
        # Should contain category-specific content
        assert category.upper() in content, f"Expected '{category.upper()}' in resource content, got: {content[:100]}..."


# ============ PROMPT TESTS ============

def test_list_prompts(mcp_client: SimpleMCPClient) -> None:
    """Test listing available prompts"""
    # List prompts
    prompts = mcp_client.list_prompts()

    # Should return a list
    assert isinstance(prompts, list), f"Expected list of prompts, got: {type(prompts)}"
    assert prompts, "Expected non-empty prompts list"
    assert len(prompts) >= 5, f"Expected at least 5 prompts, found {len(prompts)} prompts"

    # Get prompt names
    prompt_names = [prompt.get("name") for prompt in prompts]
    
    # Should contain expected prompt names
    expected_prompts = [
        "code_review_prompt",
        "learning_plan_prompt", 
        "debugging_assistant_prompt",
        "project_planning_prompt",
        "mcp_development_prompt"
    ]
    
    for expected_prompt in expected_prompts:
        assert expected_prompt in prompt_names, f"Expected prompt '{expected_prompt}' in available prompts: {prompt_names}"

    # Verify prompt structure
    for prompt in prompts:
        assert "name" in prompt, f"Expected 'name' in prompt, got: {prompt}"
        assert "description" in prompt, f"Expected 'description' in prompt, got: {prompt}"
        assert prompt["name"], f"Expected non-empty name in prompt, got: {prompt}"
        assert prompt["description"], f"Expected non-empty description in prompt, got: {prompt}"


def test_get_code_review_prompt_default_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting code review prompt with default arguments"""
    # Get prompt with default args
    result = mcp_client.get_prompt("code_review_prompt")

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"

    # Verify response structure
    assert "messages" in result, f"Expected 'messages' in result, got: {result}"
    assert result["messages"], f"Expected non-empty messages, got: {result['messages']}"
    assert len(result["messages"]) >= 1, f"Expected at least 1 message, got: {len(result['messages'])}"    # Check message structure
    message = result["messages"][0]
    assert "role" in message, f"Expected 'role' in message, got: {message}"
    assert "content" in message, f"Expected 'content' in message, got: {message}"
    assert message["role"] == "user", f"Expected role 'user', got: {message['role']}"    # Check content contains expected elements
    content = message["content"]
    # Content should be a dict with 'text' field
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    assert "python" in content_text.lower(), f"Expected 'python' in default content"
    assert "function" in content_text.lower(), f"Expected 'function' in default content"
    assert "review" in content_text.lower(), f"Expected 'review' in content"
    assert "best practices" in content_text.lower(), f"Expected 'best practices' in content"


def test_get_code_review_prompt_custom_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting code review prompt with custom arguments"""
    # Get prompt with custom args
    result = mcp_client.get_prompt("code_review_prompt", {
        "language": "javascript",
        "code_type": "class"
    })

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure
    assert "messages" in result, f"Expected 'messages' in result, got: {result}"
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains custom parameters
    assert "javascript" in content_text.lower(), f"Expected 'javascript' in custom content, got: {content_text[:200]}..."
    assert "class" in content_text.lower(), f"Expected 'class' in custom content, got: {content_text[:200]}..."
    assert "JAVASCRIPT" in content_text.upper(), f"Expected 'JAVASCRIPT' in uppercase content"
    assert "CLASS" in content_text.upper(), f"Expected 'CLASS' in uppercase content"


def test_get_learning_plan_prompt_default_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting learning plan prompt with default arguments"""
    # Get prompt with required topic and defaults
    result = mcp_client.get_prompt("learning_plan_prompt", {"topic": "FastAPI"})

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure
    assert "messages" in result, f"Expected 'messages' in result, got: {result}"
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains expected elements
    assert "FastAPI" in content_text, f"Expected 'FastAPI' in content"
    assert "beginner" in content_text.lower(), f"Expected default 'beginner' level in content"
    assert "1 month" in content_text.lower(), f"Expected default '1 month' timeframe in content"
    assert "Learning Objectives" in content_text, f"Expected 'Learning Objectives' section"
    assert "Weekly Breakdown" in content_text, f"Expected 'Weekly Breakdown' section"


def test_get_learning_plan_prompt_custom_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting learning plan prompt with custom arguments"""
    # Get prompt with custom args
    result = mcp_client.get_prompt("learning_plan_prompt", {
        "topic": "Docker",
        "skill_level": "advanced",
        "timeframe": "6 months"
    })

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure and custom content
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains custom parameters
    assert "Docker" in content_text, f"Expected 'Docker' in content"
    assert "advanced" in content_text.lower(), f"Expected 'advanced' level in content"
    assert "6 months" in content_text.lower(), f"Expected '6 months' timeframe in content"


def test_get_debugging_assistant_prompt_default_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting debugging assistant prompt with default arguments"""
    # Get prompt with defaults
    result = mcp_client.get_prompt("debugging_assistant_prompt")

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure
    assert "messages" in result, f"Expected 'messages' in result, got: {result}"
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains expected elements
    assert "python" in content_text.lower(), f"Expected default 'python' language in content"
    assert "runtime" in content_text.lower(), f"Expected default 'runtime' error type in content"
    assert "stack trace analysis" in content_text.lower(), f"Expected runtime debugging steps"
    assert "Root cause analysis" in content_text, f"Expected debugging methodology"


def test_get_debugging_assistant_prompt_custom_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting debugging assistant prompt with custom arguments"""
    # Get prompt with custom args
    result = mcp_client.get_prompt("debugging_assistant_prompt", {
        "language": "typescript",
        "error_type": "performance"
    })

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify custom content
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains custom parameters
    assert "typescript" in content_text.lower(), f"Expected 'typescript' in content"
    assert "performance" in content_text.lower(), f"Expected 'performance' error type in content"
    assert "profiling" in content_text.lower(), f"Expected performance debugging steps"
    assert "TYPESCRIPT" in content_text.upper(), f"Expected 'TYPESCRIPT' in uppercase content"


def test_get_project_planning_prompt_default_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting project planning prompt with default arguments"""
    # Get prompt with required project_type and defaults
    result = mcp_client.get_prompt("project_planning_prompt", {"project_type": "web app"})

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains expected elements
    assert "web app" in content_text.lower(), f"Expected 'web app' project type in content"
    assert "1-3" in content_text, f"Expected default team size '1-3' in content"
    assert "1-3 months" in content_text, f"Expected default timeline '1-3 months' in content"
    assert "Architecture Design" in content_text, f"Expected architecture section"
    assert "Development Plan" in content_text, f"Expected development plan section"


def test_get_project_planning_prompt_custom_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting project planning prompt with custom arguments"""
    # Get prompt with custom args
    result = mcp_client.get_prompt("project_planning_prompt", {
        "project_type": "mobile app",
        "team_size": "5-10",
        "timeline": "12 months"
    })

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify custom content
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains custom parameters
    assert "mobile app" in content_text.lower(), f"Expected 'mobile app' project type in content"
    assert "5-10" in content_text, f"Expected '5-10' team size in content"
    assert "12 months" in content_text, f"Expected '12 months' timeline in content"


def test_get_mcp_development_prompt_default_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting MCP development prompt with default arguments"""
    # Get prompt with defaults
    result = mcp_client.get_prompt("mcp_development_prompt")

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify response structure
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains expected elements
    assert "tool" in content_text.lower(), f"Expected default 'tool' component type in content"
    assert "intermediate" in content_text.lower(), f"Expected default 'intermediate' complexity in content"
    assert "MCP (Model Context Protocol)" in content_text, f"Expected MCP explanation"
    assert "@mcp.tool()" in content_text, f"Expected FastMCP decorator example"
    assert "functions that can be called by the LLM" in content_text, f"Expected tool explanation"


def test_get_mcp_development_prompt_custom_args(mcp_client: SimpleMCPClient) -> None:
    """Test getting MCP development prompt with custom arguments"""
    # Get prompt with custom args
    result = mcp_client.get_prompt("mcp_development_prompt", {
        "component_type": "resource",
        "complexity": "advanced"
    })

    # Check for errors
    assert (
        "error" not in result
    ), f"Prompt request failed with JSON-RPC error: {result.get('error')}"
    assert not result.get("isError"), f"Prompt request failed with FastMCP error: {result}"    # Verify custom content
    message = result["messages"][0]
    content = message["content"]

    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)

    # Check content contains custom parameters
    assert "resource" in content_text.lower(), f"Expected 'resource' component type in content"
    assert "advanced" in content_text.lower(), f"Expected 'advanced' complexity in content"
    assert "@mcp.resource()" in content_text, f"Expected resource decorator example"
    assert "static or dynamic content" in content_text, f"Expected resource explanation"


def test_get_nonexistent_prompt(mcp_client: SimpleMCPClient) -> None:
    """Test getting a prompt that doesn't exist"""
    # Try to get a non-existent prompt
    result = mcp_client.get_prompt("nonexistent_prompt")

    # Should return an error
    assert "error" in result, f"Expected error for nonexistent prompt, got: {result}"


def test_prompt_argument_validation(mcp_client: SimpleMCPClient) -> None:
    """Test prompt argument handling and validation"""
    # Test with empty arguments
    result = mcp_client.get_prompt("code_review_prompt", {})
    assert "error" not in result, f"Should handle empty arguments, got error: {result.get('error')}"
    
    # Test with valid arguments
    result = mcp_client.get_prompt("code_review_prompt", {
        "language": "python",
        "code_type": "function"
    })
    assert "error" not in result, f"Should handle valid arguments, got error: {result.get('error')}"
    
    # Verify the expected argument is processed
    message = result["messages"][0]
    content = message["content"]
    # Handle content structure (dict with 'text' field)
    if isinstance(content, dict):
        content_text = content.get("text", "")
    else:
        content_text = str(content)
    assert "python" in content_text.lower(), f"Expected argument should be processed"
    
    # Test with unexpected arguments (should fail with validation error)
    result = mcp_client.get_prompt("code_review_prompt", {
        "language": "python",
        "unexpected_arg": "should_be_rejected"
    })
    assert "error" in result, f"Should reject unexpected arguments with validation error, got: {result}"


if __name__ == "__main__":
    # Allow running tests directly with python tests.py
    pytest.main([__file__, "-v"])
