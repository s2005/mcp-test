import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.content.content_manager import ContentManager


def register_greeting_tools(mcp, content_manager: "ContentManager"):
    """Register greeting-related tools with the MCP server.

    Args:
        mcp: The MCP server instance
        content_manager: ContentManager instance for accessing externalized content
    """

    @mcp.tool()
    def generate_greeting(name: str = "User") -> str:
        """
        Generate a personalized greeting message.

        Args:
            name: The name of the person to greet (default: "User")

        Returns:
            A personalized greeting message
        """
        # Get greeting templates from ContentManager
        greeting_templates = content_manager.get_greetings()

        if not greeting_templates:
            # Fallback in case no greetings are configured
            return f"Hello {name}! Welcome to the MCP test server!"

        # Format each template with the provided name and select one randomly
        formatted_greetings = [
            template.format(name=name) for template in greeting_templates
        ]
        return random.choice(formatted_greetings)
