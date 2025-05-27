from typing import List, Optional

def register_tips_tools(mcp, tips_by_category):
    """Register tips-related tools with the MCP server."""
    
    @mcp.tool()
    def get_learning_tips(category: Optional[str] = None) -> List[str]:
        """
        Get a list of learning tips for development.
        
        Args:
            category: Optional category to filter tips.                 If not provided, returns MCP-test tips.
        
        Returns:
            List of helpful tips for learning
        """
        if category is None:
            # Default behavior - return MCP-test tips from tips_by_category
            return tips_by_category["mcp-test"].copy()
        
        # Convert category to lowercase for case-insensitive matching
        category_lower = category.lower()
        
        # Check if category exists
        if category_lower not in tips_by_category:
            available_categories = list(tips_by_category.keys())
            return [f"Error: Category '{category}' not found. Available categories: {', '.join(available_categories)}"]
        
        # Return tips for the specified category
        return tips_by_category[category_lower].copy()
