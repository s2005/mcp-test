"""
Dynamic configuration tests for the externalization system.

This module tests the system's ability to handle dynamic JSON configurations
and edge cases in content loading and validation.
"""

import unittest
import tempfile
import json
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from content.content_manager import ContentManager
from utils import load_content_from_json
from prompts.prompts import validate_prompt_structure, get_prompt_categories


class TestDynamicConfigurations(unittest.TestCase):
    """Test dynamic configuration loading and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_files = []
    
    def tearDown(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass
    
    def create_temp_json_file(self, content_data):
        """Create a temporary JSON file and track it for cleanup."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(content_data, temp_file, indent=2)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def test_minimal_configuration(self):
        """Test system with minimal JSON configuration."""
        minimal_config = {
            "tips": {
                "basic": ["A simple tip"]
            }
        }
        
        temp_file = self.create_temp_json_file(minimal_config)
        
        # Test loading
        loaded_content = load_content_from_json(temp_file)
        self.assertEqual(loaded_content["tips"]["basic"], ["A simple tip"])
        
        # Test ContentManager
        content_manager = ContentManager(loaded_content)
        tips = content_manager.get_tips("basic")
        self.assertEqual(tips, ["A simple tip"])
    
    def test_tips_only_configuration(self):
        """Test configuration with only tips section."""
        tips_only_config = {
            "tips": {
                "development": [
                    "Write clean, readable code",
                    "Use version control for all projects",
                    "Test your code thoroughly"
                ],
                "deployment": [
                    "Use environment variables for configuration",
                    "Monitor your applications in production",
                    "Have a rollback plan ready"
                ]
            }
        }
        
        temp_file = self.create_temp_json_file(tips_only_config)
        loaded_content = load_content_from_json(temp_file)
        
        content_manager = ContentManager(loaded_content)
        
        # Test category access
        dev_tips = content_manager.get_tips("development")
        deploy_tips = content_manager.get_tips("deployment")
        
        self.assertEqual(len(dev_tips), 3)
        self.assertEqual(len(deploy_tips), 3)
        self.assertIn("clean, readable code", dev_tips[0])
        self.assertIn("environment variables", deploy_tips[0])
    
    def test_messages_only_configuration(self):
        """Test configuration with only messages section."""
        messages_only_config = {
            "messages": {
                "greetings": [
                    "Welcome {name} to our system!",
                    "Hello {name}, ready to get started?",
                    "Hi {name}! Let's build something amazing!"
                ],
                "farewells": [
                    "Goodbye {name}, see you soon!",
                    "Thanks for using our system, {name}!",
                    "Until next time, {name}!"
                ]
            }
        }
        
        temp_file = self.create_temp_json_file(messages_only_config)
        loaded_content = load_content_from_json(temp_file)
        
        content_manager = ContentManager(loaded_content)
        
        # Test greetings
        greetings = content_manager.get_greetings()
        self.assertEqual(len(greetings), 3)
        self.assertTrue(all("{name}" in greeting for greeting in greetings))
        
        # Test missing tips gracefully
        tips = content_manager.get_tips()
        self.assertEqual(tips, [])
    
    def test_prompts_only_configuration(self):
        """Test configuration with only prompts section."""
        prompts_only_config = {
            "prompts": {
                "custom": {
                    "simple_prompt": {
                        "name": "simple_prompt",
                        "description": "A simple test prompt",
                        "template": "Help me with {task} using {approach}",
                        "role": "user",
                        "arguments": [
                            {
                                "name": "task",
                                "type": "string",
                                "description": "The task to help with",
                                "required": True
                            },
                            {
                                "name": "approach",
                                "type": "string",
                                "description": "The approach to use",
                                "default": "best practices",
                                "required": False
                            }
                        ]
                    }
                }
            }
        }
        
        temp_file = self.create_temp_json_file(prompts_only_config)
        loaded_content = load_content_from_json(temp_file)
        
        # Test prompt structure validation
        is_valid = validate_prompt_structure(loaded_content)
        self.assertTrue(is_valid)
        
        # Test category extraction
        categories = get_prompt_categories(loaded_content)
        self.assertEqual(categories, ["custom"])
    
    def test_complex_nested_configuration(self):
        """Test configuration with complex nested structures."""
        complex_config = {
            "tips": {
                "web_development": [
                    "Use semantic HTML elements",
                    "Optimize images for web delivery",
                    "Implement responsive design principles"
                ],
                "mobile_development": [
                    "Design for touch interfaces",
                    "Optimize for battery life",
                    "Test on real devices"
                ]
            },
            "messages": {
                "greetings": [
                    "Welcome to the advanced system, {name}!"
                ]
            }
        }
        
        temp_file = self.create_temp_json_file(complex_config)
        loaded_content = load_content_from_json(temp_file)
        
        content_manager = ContentManager(loaded_content)
        
        # Test that the system handles the configuration correctly
        web_tips = content_manager.get_tips("web_development")
        self.assertIsInstance(web_tips, list)
        self.assertEqual(len(web_tips), 3)
        
        mobile_tips = content_manager.get_tips("mobile_development")
        self.assertIsInstance(mobile_tips, list)
        self.assertEqual(len(mobile_tips), 3)
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON configurations."""
        # Create file with invalid JSON
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('{"invalid": json, "syntax": }')
        temp_file.close()
        self.temp_files.append(temp_file.name)
        
        # Should raise an exception or return None
        with self.assertRaises(ValueError):
            load_content_from_json(temp_file.name)
    
    def test_missing_file_handling(self):
        """Test handling of missing configuration files."""
        nonexistent_file = "/path/that/does/not/exist.json"
        
        # Should handle missing file gracefully
        with self.assertRaises(FileNotFoundError):
            load_content_from_json(nonexistent_file)
    
    def test_empty_json_file(self):
        """Test handling of empty JSON file."""
        empty_config = {}
        
        temp_file = self.create_temp_json_file(empty_config)
        loaded_content = load_content_from_json(temp_file)
        
        self.assertEqual(loaded_content, {})
        
        # ContentManager should handle empty data gracefully
        content_manager = ContentManager(loaded_content)
        self.assertEqual(content_manager.get_tips(), [])
        self.assertEqual(content_manager.get_greetings(), [])
    
    def test_large_configuration_performance(self):
        """Test performance with large configuration files."""
        import time
        
        # Create large configuration
        large_config = {
            "tips": {},
            "messages": {
                "greetings": [f"Hello user_{i}, {{name}}!" for i in range(1000)]
            },
            "prompts": {}
        }
        
        # Add many tip categories with many tips each
        for category_num in range(100):
            category_name = f"category_{category_num}"
            large_config["tips"][category_name] = [
                f"Tip {tip_num} for {category_name}" for tip_num in range(50)
            ]
        
        temp_file = self.create_temp_json_file(large_config)
        
        # Measure loading time
        start_time = time.time()
        loaded_content = load_content_from_json(temp_file)
        load_time = time.time() - start_time
        
        # Measure ContentManager creation time
        start_time = time.time()
        content_manager = ContentManager(loaded_content)
        creation_time = time.time() - start_time
        
        # Measure access time
        start_time = time.time()
        for i in range(100):
            content_manager.get_tips(f"category_{i}")
        access_time = time.time() - start_time
        
        # Performance assertions (should complete quickly)
        self.assertLess(load_time, 1.0, "JSON loading should be fast")
        self.assertLess(creation_time, 0.1, "ContentManager creation should be fast")
        self.assertLess(access_time, 0.5, "Content access should be fast")
        
        # Verify content integrity
        self.assertEqual(len(loaded_content["messages"]["greetings"]), 1000)
        self.assertEqual(len(loaded_content["tips"]), 100)
    
    def test_unicode_content_handling(self):
        """Test handling of unicode content in configurations."""
        unicode_config = {
            "tips": {
                "international": [
                    "Bonjour! Use UTF-8 encoding for international characters",
                    "¡Hola! Test your application with different locales",
                    "こんにちは! Consider right-to-left languages in your UI",
                    "مرحبا! Handle unicode properly in all text processing"
                ]
            },
            "messages": {
                "greetings": [
                    "Welcome {name}! 🎉",
                    "Hello {name}! ✨",
                    "Greetings {name}! 🚀"
                ]
            }
        }
        
        temp_file = self.create_temp_json_file(unicode_config)
        loaded_content = load_content_from_json(temp_file)
        
        content_manager = ContentManager(loaded_content)
        
        # Test unicode tips
        intl_tips = content_manager.get_tips("international")
        self.assertEqual(len(intl_tips), 4)
        self.assertIn("Bonjour!", intl_tips[0])
        self.assertIn("こんにちは!", intl_tips[2])
        
        # Test unicode greetings
        greetings = content_manager.get_greetings()
        self.assertTrue(any("🎉" in greeting for greeting in greetings))
        self.assertTrue(any("✨" in greeting for greeting in greetings))
    
    def test_content_validation_edge_cases(self):
        """Test prompt validation with edge cases."""
        edge_cases = [
            # Missing template
            {
                "prompts": {
                    "test": {
                        "invalid_prompt": {
                            "description": "Missing template"
                        }
                    }
                }
            },
            # Invalid prompt structure
            {
                "prompts": {
                    "test": "not_a_dict"
                }
            },
            # Non-dict prompts section
            {
                "prompts": "not_a_dict"
            }
        ]
        
        for i, edge_case in enumerate(edge_cases):
            with self.subTest(case=i):
                is_valid = validate_prompt_structure(edge_case)
                self.assertFalse(is_valid, f"Edge case {i} should be invalid")
    
    def test_dynamic_content_updates(self):
        """Test behavior when content is dynamically updated."""
        initial_config = {
            "tips": {
                "initial": ["Initial tip"]
            },
            "messages": {
                "greetings": ["Hello {name}!"]
            }
        }
        
        # Create initial manager
        manager1 = ContentManager(initial_config)
        self.assertEqual(manager1.get_tips("initial"), ["Initial tip"])
        
        # Update configuration
        updated_config = {
            "tips": {
                "initial": ["Initial tip", "Updated tip"],
                "new_category": ["New category tip"]
            },
            "messages": {
                "greetings": ["Hello {name}!", "Hi {name}!"]
            }
        }
        
        # Create new manager with updated content
        manager2 = ContentManager(updated_config)
        
        # Verify updates
        self.assertEqual(len(manager2.get_tips("initial")), 2)
        self.assertEqual(manager2.get_tips("new_category"), ["New category tip"])
        self.assertEqual(len(manager2.get_greetings()), 2)
        
        # Verify original manager is unchanged
        self.assertEqual(len(manager1.get_tips("initial")), 1)
        self.assertEqual(manager1.get_tips("new_category"), [])


if __name__ == '__main__':
    unittest.main()