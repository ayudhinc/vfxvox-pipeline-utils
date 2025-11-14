"""Tests for ShotLint plugin system."""

import pytest
from pathlib import Path

from vfxvox_pipeline_utils.shotlint.plugins import PluginLoader, PluginRule
from vfxvox_pipeline_utils.core.exceptions import ValidationError


@pytest.mark.unit
def test_plugin_loader_initialization():
    """Test PluginLoader initializes correctly."""
    loader = PluginLoader()
    assert loader is not None


@pytest.mark.unit
def test_load_plugin_with_function_spec(temp_dir):
    """Test loading plugin with module:function specification."""
    # Create a test plugin module
    plugin_code = '''
def custom_validator(context):
    """Test validator plugin."""
    return []
'''
    
    plugin_file = temp_dir / "test_plugin.py"
    plugin_file.write_text(plugin_code)
    
    loader = PluginLoader()
    
    # Add temp_dir to sys.path temporarily
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        plugin = loader.load_plugin("test_plugin:custom_validator")
        assert plugin is not None
        assert callable(plugin)
    finally:
        sys.path.remove(str(temp_dir))


@pytest.mark.unit
def test_load_plugin_with_module_spec(temp_dir):
    """Test loading plugin with module specification (uses validate function)."""
    # Create a test plugin module with validate function
    plugin_code = '''
def validate(context):
    """Default validate function."""
    return []
'''
    
    plugin_file = temp_dir / "test_plugin2.py"
    plugin_file.write_text(plugin_code)
    
    loader = PluginLoader()
    
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        plugin = loader.load_plugin("test_plugin2")
        assert plugin is not None
        assert callable(plugin)
    finally:
        sys.path.remove(str(temp_dir))


@pytest.mark.unit
def test_load_nonexistent_plugin():
    """Test loading nonexistent plugin raises error."""
    loader = PluginLoader()
    
    with pytest.raises(Exception):  # ImportError or ModuleNotFoundError
        loader.load_plugin("nonexistent_module:function")


@pytest.mark.unit
def test_execute_plugin_with_valid_results(temp_dir):
    """Test executing plugin that returns valid results."""
    plugin_code = '''
def custom_validator(context):
    """Test validator that returns issues."""
    return [
        {
            "rule": "custom_check",
            "level": "warning",
            "message": "Custom issue found",
            "path": "test/path"
        }
    ]
'''
    
    plugin_file = temp_dir / "test_plugin3.py"
    plugin_file.write_text(plugin_code)
    
    loader = PluginLoader()
    
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        plugin = loader.load_plugin("test_plugin3:custom_validator")
        
        context = {
            "root": temp_dir,
            "options": {}
        }
        
        results = loader.execute_plugin(plugin, context)
        
        assert len(results) == 1
        assert results[0]["rule"] == "custom_check"
        assert results[0]["level"] == "warning"
    finally:
        sys.path.remove(str(temp_dir))


@pytest.mark.unit
def test_execute_plugin_with_exception(temp_dir):
    """Test executing plugin that raises exception."""
    plugin_code = '''
def failing_validator(context):
    """Test validator that raises exception."""
    raise ValueError("Plugin error")
'''
    
    plugin_file = temp_dir / "test_plugin4.py"
    plugin_file.write_text(plugin_code)
    
    loader = PluginLoader()
    
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        plugin = loader.load_plugin("test_plugin4:failing_validator")
        
        context = {
            "root": temp_dir,
            "options": {}
        }
        
        # Plugin errors should be caught and handled gracefully
        results = loader.execute_plugin(plugin, context)
        
        # Should return empty list or error result
        assert isinstance(results, list)
    finally:
        sys.path.remove(str(temp_dir))


@pytest.mark.integration
def test_plugin_rule_integration(temp_dir, create_test_directory_structure):
    """Test PluginRule integration with validator."""
    # Create test plugin
    plugin_code = '''
def check_metadata(context):
    """Check for metadata files."""
    root = context["root"]
    issues = []
    
    # Check if metadata file exists
    metadata_file = root / "metadata.yaml"
    if not metadata_file.exists():
        issues.append({
            "rule": "metadata_check",
            "level": "warning",
            "message": "Metadata file missing",
            "path": str(root)
        })
    
    return issues
'''
    
    plugin_file = temp_dir / "metadata_plugin.py"
    plugin_file.write_text(plugin_code)
    
    # Create test structure without metadata
    structure = {
        "seq_010": {
            "shot_010": None
        }
    }
    
    test_dir = create_test_directory_structure(structure)
    
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        rule_config = {
            "name": "Metadata check",
            "type": "plugin",
            "module": "metadata_plugin:check_metadata",
            "level": "warning",
            "options": {}
        }
        
        rule = PluginRule()
        issues = rule.check(test_dir, rule_config)
        
        assert len(issues) > 0
        assert any("metadata" in issue.message.lower() for issue in issues)
    finally:
        sys.path.remove(str(temp_dir))


@pytest.mark.unit
def test_plugin_with_options(temp_dir):
    """Test plugin receives and uses options."""
    plugin_code = '''
def configurable_validator(context):
    """Validator that uses options."""
    options = context.get("options", {})
    required_fields = options.get("required_fields", [])
    
    issues = []
    for field in required_fields:
        issues.append({
            "rule": "field_check",
            "level": "info",
            "message": f"Checking field: {field}",
            "path": str(context["root"])
        })
    
    return issues
'''
    
    plugin_file = temp_dir / "test_plugin5.py"
    plugin_file.write_text(plugin_code)
    
    loader = PluginLoader()
    
    import sys
    sys.path.insert(0, str(temp_dir))
    
    try:
        plugin = loader.load_plugin("test_plugin5:configurable_validator")
        
        context = {
            "root": temp_dir,
            "options": {
                "required_fields": ["artist", "date", "version"]
            }
        }
        
        results = loader.execute_plugin(plugin, context)
        
        assert len(results) == 3
        assert all("Checking field:" in r["message"] for r in results)
    finally:
        sys.path.remove(str(temp_dir))
