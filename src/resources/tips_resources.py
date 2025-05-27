def register_tips_resources(mcp, tips_by_category):
    """Register tips-related resources with the MCP server."""

    @mcp.resource("tips://mcp")
    def get_learning_tips_resource() -> str:
        """
        Get a list of learning tips for MCP development.

        Returns:
            Learning tips formatted as a string
        """
        # Use MCP tips from tips_by_category as default
        tips = tips_by_category["mcp"]

        # Format as a readable string resource
        formatted_tips = "MCP Tips:\n\n"
        for i, tip in enumerate(tips, 1):
            formatted_tips += f"{i}. {tip}\n"

        return formatted_tips

    # Dynamic resource by category
    @mcp.resource("tips://category/{category}")
    def get_tips_by_category(category: str) -> str:
        """
        Get learning tips for a specific category.

        Args:
            category: The category of tips to retrieve (mcp, python, docker)

        Returns:
            Formatted learning tips for the specified category
        """
        # Convert category to lowercase for case-insensitive matching
        category_lower = category.lower()

        # Check if category exists
        if category_lower not in tips_by_category:
            available_categories = ", ".join(tips_by_category.keys())
            return f"Category '{category}' not found.\n\nAvailable categories: {available_categories}"

        # Get tips for the specified category
        tips = tips_by_category[category_lower]

        # Format as a readable string resource
        formatted_tips = f"{category.upper()} Learning Tips:\n\n"
        for i, tip in enumerate(tips, 1):
            formatted_tips += f"{i}. {tip}\n"

        # Add footer with available categories
        other_categories = [
            cat for cat in tips_by_category.keys() if cat != category_lower
        ]
        formatted_tips += f"\nOther available categories: {', '.join(other_categories)}"

        return formatted_tips
