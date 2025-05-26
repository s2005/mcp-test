from mcp.server.fastmcp import FastMCP
import datetime
import random
from typing import Dict, List, Optional, Any

# Create an MCP server
mcp = FastMCP("LinkedIn Demo")

# Category-specific tips - single source of truth
TIPS_BY_CATEGORY = {
    "mcp": [
        "Start with simple tools and gradually add complexity",
        "Use the MCP Inspector to test your servers during development",
        "Read the official MCP documentation at modelcontextprotocol.io",
        "Join the MCP community discussions on GitHub",
        "Practice with both Python and TypeScript implementations",
        "Test your MCP servers with Claude Desktop for real-world usage",
        "Use proper error handling in your tool functions",
        "Document your tools clearly with descriptive docstrings",
        "Consider security when exposing system resources",
        "Start with local development before deploying to production"
    ],
    "python": [
        "Use virtual environments to isolate project dependencies",
        "Follow PEP 8 style guidelines for consistent code formatting",
        "Write comprehensive docstrings for all functions and classes",
        "Use type hints to improve code readability and catch errors",
        "Implement proper exception handling with try-except blocks",
        "Use list comprehensions for concise and readable code",
        "Learn and use Python's built-in modules like itertools and collections",
        "Write unit tests using pytest or unittest framework",
        "Use logging instead of print statements for debugging",
        "Follow the DRY (Don't Repeat Yourself) principle"
    ],
    "docker": [
        "Use multi-stage builds to reduce final image size",
        "Always specify exact versions in your Dockerfile",
        "Use .dockerignore to exclude unnecessary files",
        "Run containers as non-root users for security",
        "Use health checks to monitor container status",
        "Leverage Docker layer caching for faster builds",
        "Keep your base images updated and secure",
        "Use docker-compose for multi-container applications",
        "Store secrets securely using Docker secrets or environment variables",
        "Monitor container resource usage and set appropriate limits"
    ]
}

@mcp.tool()
def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time as a formatted string
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def generate_greeting(name: str = "User") -> str:
    """
    Generate a personalized greeting message.
    
    Args:
        name: The name of the person to greet (default: "User")
    
    Returns:
        A personalized greeting message
    """
    greetings = [
        f"Hello {name}! Welcome to the LinkedIn Demo MCP server!",
        f"Hi there, {name}! Great to see you using MCP!",
        f"Greetings {name}! Hope you're having a fantastic day!",
        f"Hey {name}! Ready to explore Model Context Protocol?"
    ]
    return random.choice(greetings)

@mcp.tool()
def calculate_days_until_date(target_date: str) -> Dict[str, Any]:
    """
    Calculate the number of days between today and a target date.
    
    Args:
        target_date: Target date in YYYY-MM-DD format
    
    Returns:
        Dictionary with calculation results and information
    """
    try:
        target = datetime.datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.datetime.now()
        difference = target - today
        days = difference.days
        
        if days > 0:
            message = f"{days} days until {target_date}"
        elif days < 0:
            message = f"{target_date} was {abs(days)} days ago"
        else:
            message = f"{target_date} is today!"
        
        return {
            "target_date": target_date,
            "current_date": today.strftime("%Y-%m-%d"),
            "days_difference": days,
            "message": message,
            "is_future": days > 0,
            "is_past": days < 0,
            "is_today": days == 0
        }
    except ValueError:
        return {
            "error": "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25)"
        }

@mcp.resource("tips://mcp")
def get_learning_tips_resource() -> str:
    """
    Get a list of learning tips for MCP development.
    
    Returns:
        Learning tips formatted as a string
    """
    # Use MCP tips from TIPS_BY_CATEGORY as default
    tips = TIPS_BY_CATEGORY["mcp"]
    
    # Format as a readable string resource
    formatted_tips = "MCP Development Learning Tips:\n\n"
    for i, tip in enumerate(tips, 1):
        formatted_tips += f"{i}. {tip}\n"
    
    return formatted_tips

@mcp.tool()
def get_learning_tips(category: Optional[str] = None) -> List[str]:
    """
    Get a list of learning tips for development.
    
    Args:
        category: Optional category to filter tips (mcp, python, docker). 
                 If not provided, returns MCP tips.
    
    Returns:
        List of helpful tips for learning
    """
    if category is None:
        # Default behavior - return MCP tips from TIPS_BY_CATEGORY
        return TIPS_BY_CATEGORY["mcp"].copy()
    
    # Convert category to lowercase for case-insensitive matching
    category_lower = category.lower()
    
    # Check if category exists
    if category_lower not in TIPS_BY_CATEGORY:
        available_categories = list(TIPS_BY_CATEGORY.keys())
        return [f"Error: Category '{category}' not found. Available categories: {', '.join(available_categories)}"]
    
    # Return tips for the specified category
    return TIPS_BY_CATEGORY[category_lower].copy()

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
    if category_lower not in TIPS_BY_CATEGORY:
        available_categories = ", ".join(TIPS_BY_CATEGORY.keys())
        return f"Category '{category}' not found.\n\nAvailable categories: {available_categories}"
    
    # Get tips for the specified category
    tips = TIPS_BY_CATEGORY[category_lower]
    
    # Format as a readable string resource
    formatted_tips = f"{category.upper()} Learning Tips:\n\n"
    for i, tip in enumerate(tips, 1):
        formatted_tips += f"{i}. {tip}\n"
    
    # Add footer with available categories
    formatted_tips += f"\nOther available categories: {', '.join([cat for cat in TIPS_BY_CATEGORY.keys() if cat != category_lower])}"
    
    return formatted_tips

if __name__ == "__main__":
    # mcp.run(protocol="stdio", port=8000, debug=True)
    mcp.run()
