"""Tests for ContentManager class."""

import json
import tempfile
import os
from src.content.content_manager import ContentManager


class TestContentManager:
    """Test suite for ContentManager functionality."""
    
    def test_init_with_empty_content(self):
        """Test ContentManager initialization with empty content."""
        manager = ContentManager({})
        assert manager.content_data == {}
    
    def test_init_with_full_content(self):
        """Test ContentManager initialization with complete content."""
        content = {
            "tips": {"python": ["Use virtual environments"]},
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {"development": {"test": {"name": "test"}}}
        }
        manager = ContentManager(content)
        assert manager.content_data == content
    
    def test_get_greetings_success(self):
        """Test successful retrieval of greeting messages."""
        content = {
            "messages": {
                "greetings": [
                    "Hello {name}! Welcome!",
                    "Hi {name}! Great to see you!"
                ]
            }
        }
        manager = ContentManager(content)
        greetings = manager.get_greetings()
        
        assert len(greetings) == 2
        assert "Hello {name}! Welcome!" in greetings
        assert "Hi {name}! Great to see you!" in greetings
    
    def test_get_greetings_missing_section(self):
        """Test get_greetings with missing messages section."""
        manager = ContentManager({})
        greetings = manager.get_greetings()
        assert greetings == []
    
    def test_get_greetings_missing_greetings(self):
        """Test get_greetings with missing greetings category."""
        content = {"messages": {"other": ["test"]}}
        manager = ContentManager(content)
        greetings = manager.get_greetings()
        assert greetings == []
    
    def test_get_tips_default_category(self):
        """Test get_tips with default MCP category."""
        content = {
            "tips": {
                "mcp": ["Tip 1", "Tip 2"],
                "python": ["Python tip"]
            }
        }
        manager = ContentManager(content)
        tips = manager.get_tips()
        
        assert len(tips) == 2
        assert "Tip 1" in tips
        assert "Tip 2" in tips
    
    def test_get_tips_specific_category(self):
        """Test get_tips with specific category."""
        content = {
            "tips": {
                "mcp": ["MCP tip"],
                "python": ["Python tip 1", "Python tip 2"]
            }
        }
        manager = ContentManager(content)
        tips = manager.get_tips("python")
        
        assert len(tips) == 2
        assert "Python tip 1" in tips
        assert "Python tip 2" in tips
    
    def test_get_tips_nonexistent_category(self):
        """Test get_tips with nonexistent category."""
        content = {"tips": {"mcp": ["MCP tip"]}}
        manager = ContentManager(content)
        tips = manager.get_tips("nonexistent")
        assert tips == []
    
    def test_get_tips_missing_section(self):
        """Test get_tips with missing tips section."""
        manager = ContentManager({})
        tips = manager.get_tips()
        assert tips == []
    
    def test_get_all_tips(self):
        """Test get_all_tips method."""
        content = {
            "tips": {
                "mcp": ["MCP tip"],
                "python": ["Python tip"],
                "docker": ["Docker tip"]
            }
        }
        manager = ContentManager(content)
        all_tips = manager.get_all_tips()
        
        assert len(all_tips) == 3
        assert "mcp" in all_tips
        assert "python" in all_tips
        assert "docker" in all_tips
        assert all_tips["mcp"] == ["MCP tip"]
    
    def test_get_tip_categories(self):
        """Test get_tip_categories method."""
        content = {
            "tips": {
                "mcp": ["tip1"],
                "python": ["tip2"],
                "docker": ["tip3"]
            }
        }
        manager = ContentManager(content)
        categories = manager.get_tip_categories()
        
        assert len(categories) == 3
        assert "mcp" in categories
        assert "python" in categories
        assert "docker" in categories
    
    def test_get_messages(self):
        """Test get_messages method for specific category."""
        content = {
            "messages": {
                "greetings": ["Hello {name}!"],
                "farewells": ["Goodbye!", "See you later!"]
            }
        }
        manager = ContentManager(content)
        farewells = manager.get_messages("farewells")
        
        assert len(farewells) == 2
        assert "Goodbye!" in farewells
        assert "See you later!" in farewells
    
    def test_get_all_messages(self):
        """Test get_all_messages method."""
        content = {
            "messages": {
                "greetings": ["Hello {name}!"],
                "farewells": ["Goodbye!"]
            }
        }
        manager = ContentManager(content)
        all_messages = manager.get_all_messages()
        
        assert len(all_messages) == 2
        assert "greetings" in all_messages
        assert "farewells" in all_messages
        assert all_messages["greetings"] == ["Hello {name}!"]
    
    def test_get_prompts_specific_category(self):
        """Test get_prompts with specific category."""
        content = {
            "prompts": {
                "development": {"prompt1": {"name": "prompt1"}},
                "learning": {"prompt2": {"name": "prompt2"}}
            }
        }
        manager = ContentManager(content)
        dev_prompts = manager.get_prompts("development")
        
        assert "prompt1" in dev_prompts
        assert dev_prompts["prompt1"]["name"] == "prompt1"
        assert "prompt2" not in dev_prompts
    
    def test_get_prompts_all_categories(self):
        """Test get_prompts without category (all prompts)."""
        content = {
            "prompts": {
                "development": {"prompt1": {"name": "prompt1"}},
                "learning": {"prompt2": {"name": "prompt2"}}
            }
        }
        manager = ContentManager(content)
        all_prompts = manager.get_prompts()
        
        assert len(all_prompts) == 2
        assert "development" in all_prompts
        assert "learning" in all_prompts
    
    def test_get_prompt_categories(self):
        """Test get_prompt_categories method."""
        content = {
            "prompts": {
                "development": {"prompt1": {}},
                "learning": {"prompt2": {}},
                "planning": {"prompt3": {}}
            }
        }
        manager = ContentManager(content)
        categories = manager.get_prompt_categories()
        
        assert len(categories) == 3
        assert "development" in categories
        assert "learning" in categories
        assert "planning" in categories
    
    def test_has_category(self):
        """Test has_category method."""
        content = {
            "tips": {"python": ["tip"]},
            "messages": {"greetings": ["hello"]},
            "prompts": {"development": {"prompt": {}}}
        }
        manager = ContentManager(content)
        
        # Test existing categories
        assert manager.has_category("tips", "python") is True
        assert manager.has_category("messages", "greetings") is True
        assert manager.has_category("prompts", "development") is True
        
        # Test non-existing categories
        assert manager.has_category("tips", "nonexistent") is False
        assert manager.has_category("messages", "nonexistent") is False
        assert manager.has_category("prompts", "nonexistent") is False
        
        # Test non-existing sections
        assert manager.has_category("nonexistent", "category") is False


class TestContentManagerDynamic:
    """Dynamic JSON testing for ContentManager."""
    
    def test_dynamic_json_loading(self):
        """Test ContentManager with dynamically created JSON."""
        temp_content = {
            "tips": {
                "custom": ["Custom tip 1", "Custom tip 2"],
                "testing": ["Test tip"]
            },
            "messages": {
                "greetings": ["Hello {name}! Welcome to testing!"],
                "custom_messages": ["Custom message"]
            },
            "prompts": {
                "custom_category": {
                    "test_prompt": {
                        "name": "test_prompt",
                        "description": "A test prompt",
                        "template": "Test template with {param}",
                        "role": "user"
                    }
                }
            }
        }
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_content, f)
            temp_file = f.name
        
        try:
            # Load and test content
            with open(temp_file, 'r') as f:
                loaded_content = json.load(f)
            
            manager = ContentManager(loaded_content)
            
            # Test custom tips
            custom_tips = manager.get_tips("custom")
            assert len(custom_tips) == 2
            assert "Custom tip 1" in custom_tips
            
            # Test custom greetings
            greetings = manager.get_greetings()
            assert len(greetings) == 1
            assert "{name}" in greetings[0]
            
            # Test custom prompts
            custom_prompts = manager.get_prompts("custom_category")
            assert "test_prompt" in custom_prompts
            
            # Test categories
            tip_categories = manager.get_tip_categories()
            assert "custom" in tip_categories
            assert "testing" in tip_categories
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_edge_cases(self):
        """Test ContentManager with edge case content."""
        edge_content = {
            "tips": {},  # Empty tips
            "messages": {
                "greetings": []  # Empty greetings
            },
            "prompts": {
                "empty_category": {}  # Empty prompt category
            }
        }
        
        manager = ContentManager(edge_content)
        
        # Test empty cases
        assert manager.get_tips() == []
        assert manager.get_greetings() == []
        assert manager.get_prompts("empty_category") == {}
        assert manager.get_tip_categories() == []