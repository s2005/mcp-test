import random

def register_greeting_tools(mcp):
    """Register greeting-related tools with the MCP server."""
    
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
            f"Hello {name}! Welcome to the MCP test server!",
            f"Hi there, {name}! Great to see you using MCP!",
            f"Greetings {name}! Hope you're having a fantastic day!",
            f"Hey {name}! Ready to explore Model Context Protocol?"
        ]
        return random.choice(greetings)
