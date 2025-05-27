"""
Tests for consolidated prompt architecture.

This module tests the consolidated prompt registration system that
replaces the previous category-specific prompt files.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prompts.prompts import (
    register_all_prompts,
    get_prompt_categories,
    get_prompts_by_category,
    validate_prompt_structure
)


class TestConsolidatedPrompts(unittest.TestCase):
    """Test consolidated prompt registration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_mcp = MagicMock()
        
        # Sample content data for testing
        self.content_data = {
            "prompts": {
                "development": {
                    "code_review_prompt": {
                        "description": "Generate a code review prompt",
                        "template": "Review this {language} code for quality and best practices",
                        "arguments": [
                            {
                                "name": "language",
                                "type": "string",
                                "description": "Programming language",
                                "default": "python"
                            }
                        ]
                    },
                    "mcp_development_prompt": {
                        "description": "Generate an MCP development prompt",
                        "template": "Help develop an MCP {component_type} at {complexity} level",
                        "arguments": [
                            {
                                "name": "component_type",
                                "type": "string",
                                "description": "Type of MCP component",
                                "default": "tool"
                            },
                            {
                                "name": "complexity",
                                "type": "string", 
                                "description": "Complexity level",
                                "default": "intermediate"
                            }
                        ]
                    }
                },
                "learning": {
                    "learning_plan_prompt": {
                        "description": "Generate a learning plan prompt",
                        "template": "Create a {timeframe} learning plan for {topic} at {skill_level} level",
                        "arguments": [
                            {
                                "name": "topic",
                                "type": "string",
                                "description": "Topic to learn",
                                "required": True
                            },
                            {
                                "name": "skill_level",
                                "type": "string",
                                "description": "Current skill level",
                                "default": "beginner"
                            },
                            {
                                "name": "timeframe",
                                "type": "string",
                                "description": "Learning timeframe",
                                "default": "1 month"
                            }
                        ]
                    }
                },
                "planning": {
                    "project_planning_prompt": {
                        "description": "Generate a project planning prompt",
                        "template": "Plan a {project_type} project for {team_size} team over {timeline}",
                        "arguments": [
                            {
                                "name": "project_type",
                                "type": "string",
                                "description": "Type of project",
                                "required": True
                            },
                            {
                                "name": "team_size",
                                "type": "string",
                                "description": "Team size",
                                "default": "1-3"
                            },
                            {
                                "name": "timeline",
                                "type": "string",
                                "description": "Project timeline",
                                "default": "1-3 months"
                            }
                        ]
                    }
                }
            },
            "tips": {
                "mcp": ["Test tip 1", "Test tip 2"]
            },
            "messages": {
                "greetings": ["Hello {name}!", "Hi {name}!"]
            }
        }
    
    @patch('prompts.prompts.PromptRegistry')
    def test_register_all_prompts(self, mock_registry_class):
        """Test registering all prompts from content data."""
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        register_all_prompts(self.mock_mcp, self.content_data)
        
        # Verify PromptRegistry was created and used
        mock_registry_class.assert_called_once()
        mock_registry.register_prompts_from_json.assert_called_once_with(
            self.mock_mcp, self.content_data
        )
    
    def test_get_prompt_categories(self):
        """Test getting prompt categories."""
        categories = get_prompt_categories(self.content_data)
        
        expected_categories = ["development", "learning", "planning"]
        self.assertEqual(sorted(categories), sorted(expected_categories))
    
    def test_get_prompt_categories_empty_data(self):
        """Test getting prompt categories from empty data."""
        empty_data = {}
        categories = get_prompt_categories(empty_data)
        
        self.assertEqual(categories, [])
    
    def test_get_prompts_by_category(self):
        """Test getting prompts by category."""
        development_prompts = get_prompts_by_category(self.content_data, "development")
        
        self.assertIn("code_review_prompt", development_prompts)
        self.assertIn("mcp_development_prompt", development_prompts)
        self.assertEqual(len(development_prompts), 2)
    
    def test_get_prompts_by_category_nonexistent(self):
        """Test getting prompts for non-existent category."""
        prompts = get_prompts_by_category(self.content_data, "nonexistent")
        
        self.assertEqual(prompts, {})
    
    def test_validate_prompt_structure_valid(self):
        """Test validating valid prompt structure."""
        is_valid = validate_prompt_structure(self.content_data)
        
        self.assertTrue(is_valid)
    
    def test_validate_prompt_structure_invalid_no_prompts(self):
        """Test validating structure without prompts section."""
        invalid_data = {"tips": ["tip1", "tip2"]}
        is_valid = validate_prompt_structure(invalid_data)
        
        self.assertTrue(is_valid)  # Should still be valid as prompts section is optional
    
    def test_validate_prompt_structure_invalid_no_template(self):
        """Test validating structure with missing template."""
        invalid_data = {
            "prompts": {
                "test": {
                    "invalid_prompt": {
                        "description": "Missing template"
                        # No template field
                    }
                }
            }
        }
        is_valid = validate_prompt_structure(invalid_data)
        
        self.assertFalse(is_valid)
    
    def test_validate_prompt_structure_not_dict(self):
        """Test validating non-dictionary input."""
        is_valid = validate_prompt_structure("not a dict")  # type: ignore
        
        self.assertFalse(is_valid)
    
    def test_get_prompt_categories_with_complex_structure(self):
        """Test prompt categories with nested complex structure."""
        complex_data = {
            "prompts": {
                "development": {"prompt1": {"template": "test"}},
                "learning": {"prompt2": {"template": "test"}},
                "planning": {"prompt3": {"template": "test"}},
                "custom": {"prompt4": {"template": "test"}}
            }
        }
        
        categories = get_prompt_categories(complex_data)
        expected = ["development", "learning", "planning", "custom"]
        
        self.assertEqual(sorted(categories), sorted(expected))


if __name__ == '__main__':
    unittest.main()