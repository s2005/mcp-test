#!/usr/bin/env python3
"""
Test MCP prompts functionality
"""

import pytest
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
    pytest.main([__file__, "-v"])
