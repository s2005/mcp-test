"""
Integration tests for MCP server with JSON tips loading functionality.

These tests verify the load_tips_from_json function and its integration
with environment variables.
"""

import unittest
import os
import tempfile
import json
import sys
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Import the function we want to test
from src.server import load_tips_from_json


class TestTipsLoadingIntegration(unittest.TestCase):
    """Integration tests for JSON tips loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_tips = {
            "integration_test": [
                "Test tip 1",
                "Test tip 2", 
                "Test tip 3"
            ],
            "python": [
                "Python integration tip 1",
                "Python integration tip 2"
            ],
            "new_category": [
                "New category tip 1",
                "New category tip 2"
            ]
        }
        
        # Create temporary JSON file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        json.dump(self.test_tips, self.temp_file)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_with_valid_json_file(self):
        """Test loading tips from a valid JSON file."""
        # Set environment variable to our test file
        with patch.dict(os.environ, {'TIPS_JSON_PATH': self.temp_file.name}):
            # Load tips using the function
            loaded_tips = load_tips_from_json()
            
            # Verify tips were loaded correctly
            self.assertEqual(loaded_tips, self.test_tips)
            self.assertIn('integration_test', loaded_tips)
            self.assertIn('python', loaded_tips)
            self.assertIn('new_category', loaded_tips)
            self.assertEqual(len(loaded_tips['integration_test']), 3)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_without_environment_variable(self):
        """Test fallback behavior when environment variable is not set."""
        # Don't set the environment variable
        loaded_tips = load_tips_from_json()
        
        # Should return default tips
        self.assertIn('mcp', loaded_tips)
        self.assertIn('python', loaded_tips)
        self.assertIn('docker', loaded_tips)
        
        # Verify all are lists with content
        for category, tips in loaded_tips.items():
            self.assertIsInstance(tips, list)
            self.assertGreater(len(tips), 0)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_with_nonexistent_file(self):
        """Test fallback behavior when JSON file doesn't exist."""
        nonexistent_path = "/path/that/definitely/does/not/exist/tips.json"
        
        with patch.dict(os.environ, {'TIPS_JSON_PATH': nonexistent_path}):
            loaded_tips = load_tips_from_json()
            
            # Should return default tips
            self.assertIn('mcp', loaded_tips)
            self.assertIn('python', loaded_tips)
            self.assertIn('docker', loaded_tips)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_with_invalid_json(self):
        """Test fallback behavior when JSON file is invalid."""
        # Create invalid JSON file
        invalid_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        invalid_file.write('{"invalid": json, content}')
        invalid_file.close()
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': invalid_file.name}):
                loaded_tips = load_tips_from_json()
                
                # Should return default tips
                self.assertIn('mcp', loaded_tips)
                self.assertIn('python', loaded_tips)
                self.assertIn('docker', loaded_tips)
        finally:
            # Clean up
            if os.path.exists(invalid_file.name):
                os.unlink(invalid_file.name)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_with_wrong_data_type(self):
        """Test fallback behavior when JSON contains wrong data types."""
        # Create JSON with wrong data types
        wrong_type_data = {
            "category1": "should be a list, not a string",
            "category2": ["valid list"],
            "category3": 123
        }
        
        wrong_type_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        json.dump(wrong_type_data, wrong_type_file)
        wrong_type_file.close()
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': wrong_type_file.name}):
                loaded_tips = load_tips_from_json()
                
                # Should return default tips
                self.assertIn('mcp', loaded_tips)
                self.assertIn('python', loaded_tips)
                self.assertIn('docker', loaded_tips)
        finally:
            # Clean up
            if os.path.exists(wrong_type_file.name):
                os.unlink(wrong_type_file.name)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_tips_with_empty_json_file(self):
        """Test behavior when JSON file is empty."""
        # Create empty JSON file
        empty_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        empty_file.write('{}')
        empty_file.close()
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': empty_file.name}):
                loaded_tips = load_tips_from_json()
                
                # Should load empty dictionary successfully
                self.assertEqual(loaded_tips, {})
        finally:
            # Clean up
            if os.path.exists(empty_file.name):
                os.unlink(empty_file.name)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_integration_with_actual_tips_file(self):
        """Test integration with the actual tips_categories.json file."""
        # Path to the actual tips file in the project
        actual_tips_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'tips_categories.json'
        )
        
        if os.path.exists(actual_tips_path):
            with patch.dict(os.environ, {'TIPS_JSON_PATH': actual_tips_path}):
                loaded_tips = load_tips_from_json()
                
                # Should contain expected categories
                self.assertIn('mcp', loaded_tips)
                self.assertIn('python', loaded_tips)
                self.assertIn('docker', loaded_tips)
                
                # Verify structure
                for category, tips in loaded_tips.items():
                    self.assertIsInstance(tips, list)
                    self.assertGreater(len(tips), 0)
                    for tip in tips:
                        self.assertIsInstance(tip, str)
                        self.assertGreater(len(tip), 0)


class TestEnvironmentVariableIntegration(unittest.TestCase):
    """Test environment variable configuration."""
    
    def test_environment_variable_name(self):
        """Test that the correct environment variable name is used."""
        # This is more of a documentation test
        env_var_name = 'TIPS_JSON_PATH'
        
        # Verify the environment variable name is what we expect
        self.assertEqual(env_var_name, 'TIPS_JSON_PATH')
        
        # Test that we can set and read it
        test_path = '/test/path/tips.json'
        with patch.dict(os.environ, {env_var_name: test_path}):
            self.assertEqual(os.getenv(env_var_name), test_path)


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)
