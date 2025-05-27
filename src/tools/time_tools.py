import datetime
from typing import Dict, Any

def register_time_tools(mcp):
    """Register time-related tools with the MCP server."""
    
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
