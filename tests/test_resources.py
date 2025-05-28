#!/usr/bin/env python3
"""
Test MCP resources functionality
"""

from typing import Generator

import pytest

from src.client import SimpleMCPClient
from src.resources.tips_resources import register_tips_resources


# Mock MCP object for testing resource registration
class MockMCP:
    def __init__(self):
        self.decorated_functions = {}

    def resource(self, uri: str):
        """
        Mock decorator for MCP resources.

        Args:
            uri: The URI for the resource.

        Returns:
            A decorator that returns the original function unmodified
            and stores it for later retrieval.
        """
        def decorator(func):
            # Simple way to identify the function for this specific task
            if "tips://category/" in uri:
                self.decorated_functions['get_tips_by_category'] = func
            # Add more conditions if other functions were to be tested this way
            # Optionally, we could attach the uri to the function for inspection
            # setattr(func, '_mcp_uri', uri)
            return func  # Return the function undecorated
        return decorator


# Mock tips data for testing
MOCK_TIPS_DATA = {
    "python": [
        "Tip: Use virtual environments to manage project dependencies.",
        "Tip: List comprehensions can make your code more concise and readable.",
        "Tip: Always close files you open."
    ],
    "docker": [
        "Tip: Optimize your Docker images for size by using multi-stage builds.",
        "Tip: Use .dockerignore to exclude unnecessary files from your build context."
    ],
    "general": [],  # For testing empty tips scenario
    "testing": [    # For testing 'other available categories' and non-empty list
        "Tip: Write tests for your code.",
        "Tip: Ensure tests cover edge cases."
    ]
}


# Test suite for tips_resources.py using direct function calls via mock
class TestTipsResources:
    def setup_method(self, method):
        """
        Set up each test method.
        This involves creating a mock MCP object, registering the tips resources
        (which decorates the target function and stores it in the mock),
        and then retrieving the target function for testing.
        """
        self.mock_mcp = MockMCP()
        # Call register_tips_resources, which will use the mock_mcp's decorator
        # and populate mock_mcp.decorated_functions
        register_tips_resources(mcp=self.mock_mcp, tips_by_category=MOCK_TIPS_DATA)

        # Get the function to test
        self.get_tips_by_category_func = self.mock_mcp.decorated_functions.get('get_tips_by_category')
        assert self.get_tips_by_category_func is not None, \
            "Failed to retrieve get_tips_by_category function via mock MCP"

    def test_placeholder(self):
        """
        A placeholder test to ensure that the setup_method correctly retrieves
        the get_tips_by_category function.
        """
        assert self.get_tips_by_category_func is not None

    def test_get_tips_by_category_existing_category(self):
        """
        Test retrieving tips for an existing category with various casings.
        Ensures correct title, tips, and "Other available categories" footer.
        """
        category_to_test = "python"
        category_casings = [
            category_to_test.lower(),
            category_to_test.upper(),
            category_to_test.capitalize(),
            "pYtHoN"  # Mixed case
        ]

        expected_tips = MOCK_TIPS_DATA[category_to_test]
        all_categories = sorted(MOCK_TIPS_DATA.keys()) # For predictable order in footer check
        
        other_categories = [cat for cat in all_categories if cat != category_to_test]


        for category_input in category_casings:
            result_string = self.get_tips_by_category_func(category_input)

            # 1. Assert title
            expected_title = f"{category_to_test.upper()} Learning Tips:\n\n"
            assert result_string.startswith(expected_title), \
                f"Failed for input '{category_input}'. Expected title: '{expected_title}'"

            # 2. Assert tips content
            for i, tip in enumerate(expected_tips):
                expected_tip_line = f"{i + 1}. {tip}"
                assert expected_tip_line in result_string, \
                    f"Failed for input '{category_input}'. Missing tip: '{expected_tip_line}'"

            # 3. Assert "Other available categories" footer
            footer_intro = "\n\nOther available categories: "
            assert footer_intro in result_string, \
                f"Failed for input '{category_input}'. Missing footer intro."
            
            # Check for presence of each other category in the part of the string after the intro
            footer_content_start_index = result_string.find(footer_intro) + len(footer_intro)
            footer_content = result_string[footer_content_start_index:]

            for other_cat in other_categories:
                assert other_cat in footer_content, \
                    f"Failed for input '{category_input}'. Missing '{other_cat}' in footer."
            
            # Ensure the current category is NOT in the "other categories" list
            assert category_to_test not in footer_content, \
                f"Failed for input '{category_input}'. Current category '{category_to_test}' found in footer."

    def test_get_tips_by_category_non_existing_category(self):
        """
        Test retrieving tips for a non-existing category.
        Ensures it returns a "not found" message along with a list of available categories.
        """
        non_existing_category = "java"
        result_string = self.get_tips_by_category_func(non_existing_category)

        # 1. Assert "Category not found" message
        expected_not_found_message = f"Category '{non_existing_category}' not found."
        assert expected_not_found_message in result_string, \
            f"Expected message '{expected_not_found_message}' not found in result."

        # 2. Assert "Available categories" list
        available_categories_intro = "Available categories: "
        assert available_categories_intro in result_string, \
            "Expected 'Available categories: ' intro not found in result."

        # Check for presence of each actual category from MOCK_TIPS_DATA
        # in the part of the string after the intro
        available_list_start_index = result_string.find(available_categories_intro) + len(available_categories_intro)
        available_list_content = result_string[available_list_start_index:]

        for actual_category in MOCK_TIPS_DATA.keys():
            assert actual_category in available_list_content, \
                f"Expected category '{actual_category}' not found in available categories list."

    def test_get_tips_by_category_empty_tips(self):
        """
        Test retrieving tips for a category that has an empty list of tips.
        Ensures correct title, no numbered tips, and correct footer.
        """
        category_with_empty_tips = "general"  # As defined in MOCK_TIPS_DATA
        result_string = self.get_tips_by_category_func(category_with_empty_tips)

        # 1. Assert title
        expected_title = f"{category_with_empty_tips.upper()} Learning Tips:\n\n"
        assert result_string.startswith(expected_title), \
            f"Expected title: '{expected_title}' not found or incorrect."

        # 2. Assert structure for empty tips (title followed by double newline then footer)
        all_categories = sorted(MOCK_TIPS_DATA.keys())
        other_categories_list = [cat for cat in all_categories if cat != category_with_empty_tips]
        
        # The function joins with ", " - let's replicate that for the expected string
        other_categories_str = ", ".join(other_categories_list)
        
        expected_structure_after_title = f"\n\nOther available categories: {other_categories_str}"
        
        # Check that the part of the string immediately after the title contains the footer intro
        content_after_title = result_string[len(expected_title):]
        
        # For empty tips, the function currently produces a single newline before the footer.
        footer_intro = "\nOther available categories: " 
        assert content_after_title.startswith(footer_intro), \
            f"Structure after title for empty tips category is incorrect. Expected footer intro '{footer_intro}' (single newline) not found at the start of: '{content_after_title}'"

        # Extract the actual list of other categories from the footer
        actual_other_categories_str = content_after_title[len(footer_intro):]
        
        # Verify each expected other category is present in the actual list
        for other_cat in other_categories_list:
            assert other_cat in actual_other_categories_str, \
                f"Expected other category '{other_cat}' not found in footer: '{actual_other_categories_str}'"

        # Ensure the current category is NOT in the "other categories" list
        assert category_with_empty_tips not in actual_other_categories_str, \
            f"Current category '{category_with_empty_tips}' found in footer: '{actual_other_categories_str}'"

        # 3. As a sanity check, ensure no numbered list items are present
        # Check the content *before* the footer intro for numbered tips
        content_before_footer = content_after_title[:content_after_title.find(footer_intro)]
        assert "1." not in content_before_footer, "Found '1.' indicating a tip, which should not be present for empty list."
        assert "2." not in content_before_footer, "Found '2.' indicating a tip, which should not be present for empty list."


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
        server_started = client.start_server(
            "python", ["src/server.py", "-j", "src/data/content.json"]
        )
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
    assert (
        len(resources) >= 1
    ), f"Expected at least 1 resource, found {len(resources)} resources"

    # Get resource URIs
    resource_uris = [resource.get("uri") for resource in resources]

    # Should contain tips resources
    tips_resources = [uri for uri in resource_uris if uri and "tips://" in uri]
    assert (
        len(tips_resources) > 0
    ), f"Expected tips:// resources, found URIs: {resource_uris}"


def test_read_resource_mcp_tips(mcp_client: SimpleMCPClient) -> None:
    """Test reading the MCP tips resource"""
    # Read the MCP tips resource
    result = mcp_client.read_resource("tips://mcp")

    # Check for errors
    assert (
        "error" not in result
    ), f"Resource read failed with JSON-RPC error: {result.get('error')}"
    assert not result.get(
        "isError"
    ), f"Resource read failed with FastMCP error: {result}"

    # Verify response structure
    assert "contents" in result, f"Expected 'contents' in result, got: {result}"
    assert result["contents"], f"Expected non-empty contents, got: {result['contents']}"
    assert (
        len(result["contents"]) > 0
    ), f"Expected contents array with items, got: {result['contents']}"

    # Extract content
    content = result["contents"][0]["text"]
    # Should contain MCP-related content
    assert (
        "MCP" in content or "mcp-test" in content.lower()
    ), f"Expected MCP content in resource, got: {content[:100]}..."
    assert (
        "tips" in content.lower()
    ), f"Expected tips content in resource, got: {content[:100]}..."


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
        assert not result.get(
            "isError"
        ), f"Resource read failed for '{uri}' with FastMCP error: {result}"

        # Verify response structure
        assert (
            "contents" in result
        ), f"Expected 'contents' in result for '{uri}', got: {result}"
        assert result[
            "contents"
        ], f"Expected non-empty contents for '{uri}', got: {result['contents']}"

        # Extract content
        content = result["contents"][0]["text"]

        # Should contain category-specific content
        assert (
            category.upper() in content
        ), f"Expected '{category.upper()}' in resource content, got: {content[:100]}..."


def test_read_resource_mcp_tips_missing(mcp_client: SimpleMCPClient) -> None:
    """Test reading MCP tips when they are missing from the data source."""
    # This test requires a server instance with specific data.
    # We'll create a new client and server instance for this test case
    # to avoid interfering with the shared mcp_client fixture if it uses default data.

    client = SimpleMCPClient()
    try:
        # Start server with the JSON file that has no MCP tips
        server_started = client.start_server(
            "python", ["src/server.py", "-j", "tests/data/tips_categories_no_mcp.json"]
        )
        assert server_started, "Failed to start MCP server for missing tips test"

        initialized = client.initialize()
        assert initialized, "Failed to initialize MCP client for missing tips test"

        result = client.read_resource("tips://mcp")

        assert "error" not in result, f"Resource read failed with JSON-RPC error: {result.get('error')}"
        assert not result.get("isError"), f"Resource read failed with FastMCP error: {result}"
        assert "contents" in result, f"Expected 'contents' in result, got: {result}"
        assert result["contents"], f"Expected non-empty contents, got: {result['contents']}"
        
        content = result["contents"][0]["text"]
        expected_message = "MCP Tips:\n\nNo MCP tips available at the moment."
        assert content == expected_message, f"Expected '{expected_message}', got '{content}'"

    finally:
        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
