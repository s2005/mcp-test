#!/usr/bin/env python3
"""
Test MCP resources functionality
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
    assert "MCP" in content or "mcp-test" in content.lower(), f"Expected MCP content in resource, got: {content[:100]}..."
    assert "tips" in content.lower(), f"Expected tips content in resource, got: {content[:100]}..."


def test_read_resource_category_tips(mcp_client: SimpleMCPClient) -> None:
    """Test reading category-specific tips resources"""
    categories = ["mcp"]
    
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
