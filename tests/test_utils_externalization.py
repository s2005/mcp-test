"""Tests for utils content externalization."""

import json
import tempfile
import os
from unittest.mock import patch
from src.utils import load_tips_from_json, load_content_from_json, get_default_content_path, load_default_content


class TestUtilsExternalization:
    """Test suite for utils content externalization."""
    
    def test_load_content_from_json_default(self):
        """Test loading content from default content.json."""
        content = load_content_from_json()
        
        # Should contain all expected sections
        assert isinstance(content, dict)
        assert "tips" in content
        assert "messages" in content
        assert "prompts" in content
        
        # Should have tips for MCP
        tips = content["tips"]
        assert "mcp" in tips
        assert isinstance(tips["mcp"], list)
        assert len(tips["mcp"]) > 0
        
        # Should have greeting messages
        messages = content["messages"]
        assert "greetings" in messages
        assert isinstance(messages["greetings"], list)
        assert len(messages["greetings"]) > 0
    
    def test_load_tips_from_json_uses_content_manager(self):
        """Test that load_tips_from_json extracts tips from full content."""
        tips = load_tips_from_json()
        
        # Should return tips dictionary
        assert isinstance(tips, dict)
        assert "mcp" in tips
        assert "python" in tips
        assert "docker" in tips
        
        # Verify tips content
        mcp_tips = tips["mcp"]
        assert isinstance(mcp_tips, list)
        assert len(mcp_tips) > 0
        assert all(isinstance(tip, str) for tip in mcp_tips)
    
    def test_load_tips_from_json_with_custom_file(self):
        """Test loading tips from custom JSON file."""
        # Create custom content
        custom_content = {
            "tips": {
                "custom": ["Custom tip 1", "Custom tip 2"],
                "testing": ["Test tip"]
            },
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {}
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_content, f)
            temp_file = f.name
        
        try:
            tips = load_tips_from_json(temp_file)
            
            # Should return only the tips section
            assert tips == custom_content["tips"]
            assert "custom" in tips
            assert "testing" in tips
            assert tips["custom"] == ["Custom tip 1", "Custom tip 2"]
            
        finally:
            os.unlink(temp_file)
    
    def test_load_tips_from_json_with_environment_variable(self):
        """Test loading tips using TIPS_JSON_PATH environment variable."""
        # Create custom content
        custom_content = {
            "tips": {"env_test": ["Environment test tip"]},
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {}
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_content, f)
            temp_file = f.name
        
        try:
            # Mock environment variable
            with patch.dict(os.environ, {"TIPS_JSON_PATH": temp_file}):
                tips = load_tips_from_json()
                
                assert "env_test" in tips
                assert tips["env_test"] == ["Environment test tip"]
                
        finally:
            os.unlink(temp_file)
    
    def test_load_tips_from_json_missing_tips_section(self):
        """Test loading tips when tips section is missing."""
        # Content without tips section
        content_without_tips = {
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(content_without_tips, f)
            temp_file = f.name
        
        try:
            tips = load_tips_from_json(temp_file)
            
            # Should return empty dictionary
            assert tips == {}
            
        finally:
            os.unlink(temp_file)
    
    def test_load_tips_from_json_invalid_file(self):
        """Test loading tips from invalid file."""
        tips = load_tips_from_json("/nonexistent/file.json")
        
        # Should return empty dictionary for invalid file
        assert tips == {}
    
    def test_get_default_content_path(self):
        """Test getting default content path."""
        path = get_default_content_path()
        
        # Should be a valid path
        assert isinstance(path, str)
        assert path.endswith("content.json")
        assert os.path.exists(path)
    
    def test_load_default_content(self):
        """Test loading default content."""
        content = load_default_content()
        
        # Should contain all expected sections
        assert isinstance(content, dict)
        assert "tips" in content
        assert "messages" in content
        assert "prompts" in content
        
        # Verify content structure
        assert isinstance(content["tips"], dict)
        assert isinstance(content["messages"], dict)
        assert isinstance(content["prompts"], dict)
    
    def test_no_hardcoded_content_in_utils(self):
        """Test that utils.py no longer contains hardcoded content."""
        # Read the utils.py file
        utils_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'utils.py')
        with open(utils_path, 'r') as f:
            utils_content = f.read()
        
        # Check that hardcoded content is removed
        hardcoded_patterns = [
            "default_tips = {",
            "mcp-test",
            "Configure this server by adding it to your MCP client",
            "Set the TIPS_JSON_PATH environment variable",
            "Use 'uv run src/server.py' to start the server"
        ]
        
        for pattern in hardcoded_patterns:
            assert pattern not in utils_content, f"Found hardcoded content: {pattern}"
    
    def test_backward_compatibility_preserved(self):
        """Test that existing JSON file loading still works."""
        # Create a legacy tips-only JSON file
        legacy_tips = {
            "legacy": ["Legacy tip 1", "Legacy tip 2"],
            "old_format": ["Old format tip"]
        }
        
        # Create a modern content file that includes tips
        modern_content = {
            "tips": legacy_tips,
            "messages": {"greetings": ["Hello {name}!"]},
            "prompts": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(modern_content, f)
            temp_file = f.name
        
        try:
            # Test that tips can still be loaded
            tips = load_tips_from_json(temp_file)
            
            assert tips == legacy_tips
            assert "legacy" in tips
            assert "old_format" in tips
            
        finally:
            os.unlink(temp_file)
    
    def test_tips_extraction_from_complex_content(self):
        """Test tips extraction from complex content structure."""
        complex_content = {
            "tips": {
                "category1": ["Tip 1", "Tip 2"],
                "category2": ["Tip 3", "Tip 4"],
                "category3": ["Tip 5"]
            },
            "messages": {
                "greetings": ["Hello {name}!"],
                "farewells": ["Goodbye!"]
            },
            "prompts": {
                "development": {
                    "prompt1": {
                        "name": "prompt1",
                        "description": "Test prompt",
                        "template": "Test template"
                    }
                },
                "learning": {
                    "prompt2": {
                        "name": "prompt2",
                        "description": "Test prompt 2",
                        "template": "Test template 2"
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(complex_content, f)
            temp_file = f.name
        
        try:
            tips = load_tips_from_json(temp_file)
            
            # Should extract only tips section
            assert tips == complex_content["tips"]
            assert len(tips) == 3
            assert "category1" in tips
            assert "category2" in tips 
            assert "category3" in tips
            
        finally:
            os.unlink(temp_file)