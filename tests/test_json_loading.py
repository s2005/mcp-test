#!/usr/bin/env python3
"""
Test JSON tips loading functionality for MCP test server
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open

# Import the function we want to test
import sys
sys.path.append('src')
from src.server import load_tips_from_json


class TestTipsJSONLoading:
    """Test class for tips JSON loading functionality"""
    
    def test_load_tips_with_valid_json_file(self):
        """Test loading tips from a valid JSON file"""
        # Create test data
        test_tips = {
            "category1": ["Tip 1", "Tip 2", "Tip 3"],
            "category2": ["Docker tip 1", "Docker tip 2"],
            "mcp-test": ["MCP tip 1"]
        }
        
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_tips, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Test with direct path parameter (new functionality)
            result = load_tips_from_json(temp_file_path)
                
            # Verify the result matches our test data
            assert result == test_tips
            assert "mcp-test" in result
            assert len(result["category1"]) == 3
            assert result["category1"][0] == "Tip 1"
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def test_load_tips_with_valid_json_file_env_var(self):
        """Test loading tips from a valid JSON file using environment variable"""
        # Create test data
        test_tips = {
            "category1": ["Tip 1", "Tip 2", "Tip 3"],
            "category2": ["Docker tip 1", "Docker tip 2"],
            "mcp-test": ["MCP tip 1"]
        }
        
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_tips, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Test with environment variable (original functionality)
            with patch.dict(os.environ, {'TIPS_JSON_PATH': temp_file_path}):
                result = load_tips_from_json()
                
            # Verify the result matches our test data
            assert result == test_tips
            assert "mcp-test" in result
            assert len(result["category1"]) == 3
            assert result["category1"][0] == "Tip 1"
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def test_load_tips_path_parameter_takes_precedence(self):
        """Test that path parameter takes precedence over environment variable"""
        # Create two different test files
        env_tips = {"env": ["Environment tip"]}
        param_tips = {"param": ["Parameter tip"]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as env_file:
            json.dump(env_tips, env_file)
            env_file_path = env_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as param_file:
            json.dump(param_tips, param_file)
            param_file_path = param_file.name
        
        try:
            # Set environment variable but also provide path parameter
            with patch.dict(os.environ, {'TIPS_JSON_PATH': env_file_path}):
                result = load_tips_from_json(param_file_path)
                
            # Should use the parameter file, not the environment file
            assert result == param_tips
            assert "param" in result
            assert "env" not in result
            
        finally:
            os.unlink(env_file_path)
            os.unlink(param_file_path)

    def test_load_tips_no_environment_variable(self):
        """Test fallback behavior when TIPS_JSON_PATH is not set"""
        # Ensure environment variable is not set
        with patch.dict(os.environ, {}, clear=True):
            result = load_tips_from_json()
            
        # Should return default tips
        assert isinstance(result, dict)
        assert "mcp-test" in result
        assert isinstance(result["mcp-test"], list)
        assert len(result["mcp-test"]) >= 1  # Should have at least one default tip    def test_load_tips_file_not_found(self):
        """Test behavior when JSON file doesn't exist"""
        non_existent_path = "/path/that/does/not/exist/tips.json"
        
        # Test with direct path parameter
        result = load_tips_from_json(non_existent_path)
        
        # Should return default tips
        assert isinstance(result, dict)
        assert "mcp-test" in result

    def test_load_tips_file_not_found_env_var(self):
        """Test behavior when JSON file doesn't exist (using env var)"""
        non_existent_path = "/path/that/does/not/exist/tips.json"
        
        with patch.dict(os.environ, {'TIPS_JSON_PATH': non_existent_path}):
            result = load_tips_from_json()
              # Should return default tips
        assert isinstance(result, dict)
        assert "mcp-test" in result

    def test_load_tips_invalid_json_format(self):
        """Test behavior when JSON file contains invalid JSON"""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write('{"invalid": json content}')  # Invalid JSON
            temp_file_path = temp_file.name
        
        try:
            # Test with direct path parameter
            result = load_tips_from_json(temp_file_path)
                
            # Should return default tips due to JSON error
            assert isinstance(result, dict)
            assert "mcp-test" in result
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_non_dict_json(self):
        """Test behavior when JSON file contains valid JSON but not a dictionary"""
        # Create a temporary file with valid JSON that's not a dict
        test_data = ["tip1", "tip2", "tip3"]  # List instead of dict
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Test with direct path parameter
            result = load_tips_from_json(temp_file_path)
                
            # Should return default tips due to format error
            assert isinstance(result, dict)
            assert "mcp-test" in result
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_invalid_category_format(self):
        """Test behavior when JSON contains categories with non-list values"""
        # Create test data with invalid category format
        test_tips = {
            "category1": ["Valid tip 1", "Valid tip 2"],
            "category2": "This should be a list, not a string",  # Invalid format
            "mcp-test": ["Valid MCP tip"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_tips, temp_file)
            temp_file_path = temp_file.name
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': temp_file_path}):
                result = load_tips_from_json()
                
            # Should return default tips due to validation error
            assert isinstance(result, dict)
            assert "mcp-test" in result
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_empty_json_file(self):
        """Test behavior when JSON file is empty"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write('')  # Empty file
            temp_file_path = temp_file.name
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': temp_file_path}):
                result = load_tips_from_json()
                
            # Should return default tips due to JSON error
            assert isinstance(result, dict)
            assert "mcp-test" in result
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_permission_error(self):
        """Test behavior when file exists but cannot be read"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump({"test": ["tip"]}, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Mock open to raise PermissionError
            with patch.dict(os.environ, {'TIPS_JSON_PATH': temp_file_path}):
                with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                    result = load_tips_from_json()
                    
            # Should return default tips due to permission error
            assert isinstance(result, dict)
            assert "mcp-test" in result
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_with_unicode_content(self):
        """Test loading tips with Unicode characters"""
        # Create test data with Unicode characters
        test_tips = {
            "category1": ["Use 🐍 Python's built-in functions", "Follow PEP 8 📝 guidelines"],
            "category2": ["Use multi-stage builds 🏗️", "Keep images small 📦"],
            "mcp-test": ["Model Context Protocol 🤖 tips"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(test_tips, temp_file, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        try:
            with patch.dict(os.environ, {'TIPS_JSON_PATH': temp_file_path}):
                result = load_tips_from_json()
                
            # Verify Unicode content is preserved
            assert result == test_tips
            assert "🐍" in result["category1"][0]
            assert "🏗️" in result["category2"][0]
            assert "🤖" in result["mcp-test"][0]
            
        finally:
            os.unlink(temp_file_path)

    def test_load_tips_with_test_data_file(self):
        """Test loading tips from the existing test data file"""
        test_data_path = "tests/data/tips_categories.json"
        
        # Test with direct path parameter
        result = load_tips_from_json(test_data_path)
        
        # Verify we got the expected categories from the test file
        assert isinstance(result, dict)
        assert "mcp" in result
        assert "python" in result 
        assert "docker" in result
        assert len(result["mcp"]) > 0
        assert len(result["python"]) > 0
        assert len(result["docker"]) > 0
        
        # Verify some expected content
        assert isinstance(result["mcp"], list)
        assert isinstance(result["python"], list)
        assert isinstance(result["docker"], list)


if __name__ == "__main__":
    pytest.main([__file__])
