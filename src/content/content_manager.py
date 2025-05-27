"""ContentManager for centralized content access."""

from typing import Dict, List, Any, Optional


class ContentManager:
    """Centralized content management for all externalized content."""
    
    def __init__(self, content_data: Dict[str, Any]):
        """Initialize ContentManager with content data.
        
        Args:
            content_data: Dictionary containing all content sections (tips, messages, prompts)
        """
        self.content_data = content_data
    
    def get_greetings(self) -> List[str]:
        """Get greeting message templates.
        
        Returns:
            List of greeting templates with {name} placeholders
        """
        return self.content_data.get("messages", {}).get("greetings", [])
    
    def get_tips(self, category: Optional[str] = None) -> List[str]:
        """Get tips for a specific category or default MCP tips.
        
        Args:
            category: Tips category to retrieve. If None, returns MCP tips.
            
        Returns:
            List of tips for the specified category
        """
        tips = self.content_data.get("tips", {})
        if category:
            return tips.get(category, [])
        return tips.get("mcp", [])
    
    def get_all_tips(self) -> Dict[str, List[str]]:
        """Get all tips organized by category.
        
        Returns:
            Dictionary mapping category names to lists of tips
        """
        return self.content_data.get("tips", {})
    
    def get_tip_categories(self) -> List[str]:
        """Get list of available tip categories.
        
        Returns:
            List of tip category names
        """
        return list(self.content_data.get("tips", {}).keys())
    
    def get_messages(self, category: str) -> List[str]:
        """Get messages for a specific category.
        
        Args:
            category: Message category to retrieve
            
        Returns:
            List of messages for the specified category
        """
        return self.content_data.get("messages", {}).get(category, [])
    
    def get_all_messages(self) -> Dict[str, List[str]]:
        """Get all messages organized by category.
        
        Returns:
            Dictionary mapping category names to lists of messages
        """
        return self.content_data.get("messages", {})
    
    def get_prompts(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get prompts for a specific category or all prompts.
        
        Args:
            category: Prompt category to retrieve. If None, returns all prompts.
            
        Returns:
            Dictionary of prompts for the specified category or all prompts
        """
        prompts = self.content_data.get("prompts", {})
        if category:
            return prompts.get(category, {})
        return prompts
    
    def get_prompt_categories(self) -> List[str]:
        """Get list of available prompt categories.
        
        Returns:
            List of prompt category names
        """
        return list(self.content_data.get("prompts", {}).keys())
    
    def has_category(self, section: str, category: str) -> bool:
        """Check if a category exists in a specific section.
        
        Args:
            section: Content section ('tips', 'messages', 'prompts')
            category: Category name to check
            
        Returns:
            True if category exists in the section, False otherwise
        """
        section_data = self.content_data.get(section, {})
        return category in section_data