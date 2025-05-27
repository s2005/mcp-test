"""
Complete integration tests for the externalization system.

This module tests the complete end-to-end functionality of the
content externalization system with custom JSON configurations.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from content.content_manager import ContentManager
from server import register_all_components
from utils import load_content_from_json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestCompleteIntegration(unittest.TestCase):
    """Test complete system integration with externalized content."""

    def setUp(self):
        """Set up test fixtures with complete content configuration."""
        self.mock_mcp = MagicMock()

        # Complete content configuration for testing
        self.complete_content = {
            "tips": {
                "mcp": [
                    "Configure this server by adding it to your MCP client configuration file",
                    "Set the TIPS_JSON_PATH environment variable to load custom tips from a JSON file",
                    "Use 'uv run src/server.py' to start the server in development mode",
                ],
                "python": [
                    "Use virtual environments to isolate project dependencies",
                    "Follow PEP 8 style guidelines for consistent code formatting",
                    "Write unit tests for all your functions and classes",
                ],
                "docker": [
                    "Use multi-stage builds to reduce image size",
                    "Always specify exact versions in your Dockerfile",
                    "Use .dockerignore to exclude unnecessary files",
                ],
            },
            "messages": {
                "greetings": [
                    "Hello {name}! Welcome to the MCP test server!",
                    "Hi there, {name}! Great to see you using MCP!",
                    "Greetings {name}! Hope you're having a fantastic day!",
                    "Hey {name}! Ready to explore Model Context Protocol?",
                ]
            },
            "prompts": {
                "development": {
                    "code_review_prompt": {
                        "name": "code_review_prompt",
                        "description": "Generate a prompt template for code review assistance",
                        "template": "Please review this {language} {code_type} and provide detailed feedback on:\n\n1. Code quality and best practices\n2. Performance considerations\n3. Security implications\n4. Readability and maintainability\n5. Potential bugs or edge cases\n6. Suggestions for improvement\n\nFocus on {language}-specific conventions and provide actionable recommendations.\n\nCode to review:\n[PASTE YOUR {language} {code_type} HERE]",
                        "role": "user",
                        "arguments": [
                            {
                                "name": "language",
                                "type": "string",
                                "description": "Programming language for the code review",
                                "default": "python",
                                "required": False,
                            },
                            {
                                "name": "code_type",
                                "type": "string",
                                "description": "Type of code to review (function, class, module, etc.)",
                                "default": "function",
                                "required": False,
                            },
                        ],
                    },
                    "mcp_development_prompt": {
                        "name": "mcp_development_prompt",
                        "description": "Generate a prompt template for MCP development assistance",
                        "template": "Help me develop an MCP (Model Context Protocol) {component_type} at {complexity} level.\n\n**What I want to build:**\n[DESCRIBE YOUR MCP {component_type} REQUIREMENTS]\n\n**Use Case:**\n[EXPLAIN HOW THIS WILL BE USED WITH LLMs]\n\n**Technical Requirements:**\n[LIST ANY SPECIFIC TECHNICAL NEEDS OR CONSTRAINTS]\n\nPlease provide guidance on building {component_type} including implementation approach, MCP protocol compliance, code examples, testing strategy, and best practices.",
                        "role": "user",
                        "arguments": [
                            {
                                "name": "component_type",
                                "type": "string",
                                "description": "Type of MCP component to develop",
                                "default": "tool",
                                "required": False,
                            },
                            {
                                "name": "complexity",
                                "type": "string",
                                "description": "Complexity level",
                                "default": "intermediate",
                                "required": False,
                            },
                        ],
                    },
                },
                "learning": {
                    "learning_plan_prompt": {
                        "name": "learning_plan_prompt",
                        "description": "Generate a personalized learning plan prompt template",
                        "template": "Create a comprehensive {timeframe} learning plan for {topic} suitable for a {skill_level} level learner.\n\nPlease include:\n\n1. **Learning Objectives**: Clear, measurable goals\n2. **Prerequisites**: What should be known before starting\n3. **Weekly Breakdown**: Detailed week-by-week plan\n4. **Resources**: Books, courses, tutorials, and practice projects\n5. **Hands-on Projects**: Practical exercises to reinforce learning\n6. **Milestones**: Checkpoints to track progress\n7. **Assessment**: How to evaluate understanding\n8. **Next Steps**: What to learn after completing this plan\n\nMake the plan practical and actionable with specific recommendations for someone at the {skill_level} level.",
                        "role": "user",
                        "arguments": [
                            {
                                "name": "topic",
                                "type": "string",
                                "description": "The subject or technology to learn",
                                "required": True,
                            },
                            {
                                "name": "skill_level",
                                "type": "string",
                                "description": "Current skill level",
                                "default": "beginner",
                                "required": False,
                            },
                            {
                                "name": "timeframe",
                                "type": "string",
                                "description": "Available time for learning",
                                "default": "1 month",
                                "required": False,
                            },
                        ],
                    }
                },
                "planning": {
                    "project_planning_prompt": {
                        "name": "project_planning_prompt",
                        "description": "Generate a project planning and architecture prompt template",
                        "template": "Help me plan and architect a {project_type} project for a team of {team_size} people with a {timeline} timeline.\n\n**Project Requirements:**\n[DESCRIBE YOUR PROJECT REQUIREMENTS AND GOALS]\n\n**Technical Constraints:**\n[LIST ANY TECHNICAL CONSTRAINTS, PREFERRED TECHNOLOGIES, ETC.]\n\n**Target Audience:**\n[DESCRIBE WHO WILL USE THIS PROJECT]\n\nPlease provide a comprehensive project plan including architecture design, development plan, technical specifications, project management, and best practices.",
                        "role": "user",
                        "arguments": [
                            {
                                "name": "project_type",
                                "type": "string",
                                "description": "Type of project",
                                "required": True,
                            },
                            {
                                "name": "team_size",
                                "type": "string",
                                "description": "Size of the development team",
                                "default": "1-3",
                                "required": False,
                            },
                            {
                                "name": "timeline",
                                "type": "string",
                                "description": "Expected project timeline",
                                "default": "1-3 months",
                                "required": False,
                            },
                        ],
                    }
                },
            },
        }

    def create_temp_content_file(self, content_data):
        """Create a temporary JSON file with content data."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(content_data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name

    def test_complete_content_loading(self):
        """Test loading complete content configuration from JSON."""
        temp_file = self.create_temp_content_file(self.complete_content)

        try:
            loaded_content = load_content_from_json(temp_file)

            # Verify all sections are loaded
            self.assertIn("tips", loaded_content)
            self.assertIn("messages", loaded_content)
            self.assertIn("prompts", loaded_content)

            # Verify content integrity
            self.assertEqual(loaded_content["tips"], self.complete_content["tips"])
            self.assertEqual(
                loaded_content["messages"], self.complete_content["messages"]
            )
            self.assertEqual(
                loaded_content["prompts"], self.complete_content["prompts"]
            )

        finally:
            os.unlink(temp_file)

    def test_content_manager_integration(self):
        """Test ContentManager with complete content data."""
        content_manager = ContentManager(self.complete_content)

        # Test greetings
        greetings = content_manager.get_greetings()
        self.assertEqual(len(greetings), 4)
        self.assertTrue(all("{name}" in greeting for greeting in greetings))

        # Test tips by category
        mcp_tips = content_manager.get_tips("mcp")
        self.assertEqual(len(mcp_tips), 3)

        python_tips = content_manager.get_tips("python")
        self.assertEqual(len(python_tips), 3)

        # Test default tips (should return mcp)
        default_tips = content_manager.get_tips()
        self.assertEqual(default_tips, mcp_tips)

    @patch("server.register_time_tools")
    @patch("server.register_greeting_tools")
    @patch("server.register_tips_tools")
    @patch("server.register_tips_resources")
    @patch("server.PromptRegistry")
    def test_complete_server_registration(
        self,
        mock_prompt_registry,
        mock_tips_resources,
        mock_tips_tools,
        mock_greeting_tools,
        mock_time_tools,
    ):
        """Test complete server component registration."""
        mock_registry_instance = MagicMock()
        mock_prompt_registry.return_value = mock_registry_instance

        # Register all components
        register_all_components(self.complete_content)

        # Verify all tools were registered
        mock_time_tools.assert_called_once()
        mock_greeting_tools.assert_called_once()
        mock_tips_tools.assert_called_once()

        # Verify resources were registered
        mock_tips_resources.assert_called_once()

        # Verify prompts were registered
        mock_prompt_registry.assert_called_once()
        mock_registry_instance.register_prompts_from_json.assert_called_once()

    def test_dynamic_content_modification(self):
        """Test system behavior with dynamically modified content."""
        # Start with basic content
        basic_content = {
            "tips": {"test": ["Basic tip"]},
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {},
        }

        content_manager = ContentManager(basic_content)

        # Test initial state
        self.assertEqual(content_manager.get_tips("test"), ["Basic tip"])
        self.assertEqual(len(content_manager.get_greetings()), 1)

        # Modify content dynamically
        basic_content["tips"]["test"].append("Additional tip")
        basic_content["messages"]["greetings"].append("Hi {name}!")

        # Create new manager with modified content
        updated_manager = ContentManager(basic_content)

        # Verify changes are reflected
        self.assertEqual(len(updated_manager.get_tips("test")), 2)
        self.assertEqual(len(updated_manager.get_greetings()), 2)

    def test_edge_case_empty_content(self):
        """Test system behavior with minimal/empty content."""
        minimal_content = {}

        content_manager = ContentManager(minimal_content)

        # Should handle empty content gracefully
        self.assertEqual(content_manager.get_greetings(), [])
        self.assertEqual(content_manager.get_tips(), [])
        self.assertEqual(content_manager.get_tips("nonexistent"), [])

    def test_prompt_categories_validation(self):
        """Test validation of all prompt categories."""
        prompt_data = self.complete_content["prompts"]

        # Verify all categories exist
        self.assertIn("development", prompt_data)
        self.assertIn("learning", prompt_data)
        self.assertIn("planning", prompt_data)

        # Verify each category has proper prompt structure
        for category, prompts in prompt_data.items():
            self.assertIsInstance(prompts, dict)

            for prompt_name, prompt_def in prompts.items():
                self.assertIsInstance(prompt_def, dict)
                self.assertIn("template", prompt_def)
                self.assertIn("description", prompt_def)
                self.assertIn("arguments", prompt_def)

                # Verify arguments structure
                arguments = prompt_def["arguments"]
                self.assertIsInstance(arguments, list)

                for arg in arguments:
                    self.assertIn("name", arg)
                    self.assertIn("type", arg)
                    self.assertIn("description", arg)

    def test_performance_with_large_content(self):
        """Test system performance with large content configurations."""
        # Create large content set
        large_content = {
            "tips": {},
            "messages": {"greetings": [f"Hello {i}!" for i in range(100)]},
            "prompts": {},
        }

        # Add many tip categories
        for i in range(50):
            large_content["tips"][f"category_{i}"] = [
                f"Tip {j} for category {i}" for j in range(20)
            ]

        # Test ContentManager performance
        import time

        start_time = time.time()

        content_manager = ContentManager(large_content)

        # Perform operations
        for i in range(50):
            content_manager.get_tips(f"category_{i}")

        greetings = content_manager.get_greetings()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete quickly (under 1 second)
        self.assertLess(execution_time, 1.0)
        self.assertEqual(len(greetings), 100)

    def test_content_isolation(self):
        """Test that different ContentManager instances don't interfere."""
        content1 = {
            "tips": {"test": ["Content 1 tip"]},
            "messages": {"greetings": ["Hello from content 1!"]},
        }

        content2 = {
            "tips": {"test": ["Content 2 tip"]},
            "messages": {"greetings": ["Hello from content 2!"]},
        }

        manager1 = ContentManager(content1)
        manager2 = ContentManager(content2)

        # Verify isolation
        self.assertEqual(manager1.get_tips("test"), ["Content 1 tip"])
        self.assertEqual(manager2.get_tips("test"), ["Content 2 tip"])

        self.assertIn("content 1", manager1.get_greetings()[0])
        self.assertIn("content 2", manager2.get_greetings()[0])


if __name__ == "__main__":
    unittest.main()
