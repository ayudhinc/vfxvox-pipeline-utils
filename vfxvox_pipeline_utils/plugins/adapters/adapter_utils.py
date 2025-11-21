"""
Adapter utility functions.

This module provides utility functions for DCC adapters including path normalization,
scene element conversion, DCC detection, and adapter factory.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from vfxvox_pipeline_utils.plugins.core.context import SceneElement
from vfxvox_pipeline_utils.plugins.core.exceptions import AdapterError


def normalize_path(path: str, dcc_name: Optional[str] = None) -> str:
    """Normalize a file path for cross-platform compatibility.
    
    Args:
        path: Path to normalize.
        dcc_name: Optional DCC name for DCC-specific normalization.
        
    Returns:
        Normalized path string.
    """
    if not path:
        return path
    
    # Convert to Path object for normalization
    p = Path(path)
    
    # Resolve to absolute path if relative
    if not p.is_absolute():
        p = p.resolve()
    
    # Convert to forward slashes (Unix-style)
    normalized = str(p).replace("\\", "/")
    
    # DCC-specific normalization
    if dcc_name == "maya":
        # Maya prefers forward slashes
        pass
    elif dcc_name == "houdini":
        # Houdini uses forward slashes
        pass
    elif dcc_name == "nuke":
        # Nuke uses forward slashes
        pass
    elif dcc_name == "blender":
        # Blender uses forward slashes
        pass
    
    return normalized


def convert_to_relative_path(
    path: str,
    base_path: str,
    dcc_name: Optional[str] = None
) -> str:
    """Convert an absolute path to relative path.
    
    Args:
        path: Absolute path to convert.
        base_path: Base path for relative conversion.
        dcc_name: Optional DCC name for DCC-specific handling.
        
    Returns:
        Relative path string.
    """
    try:
        p = Path(path)
        base = Path(base_path)
        
        # Get relative path
        rel_path = p.relative_to(base)
        
        # Normalize
        return normalize_path(str(rel_path), dcc_name)
    except ValueError:
        # Paths are on different drives or not related
        return normalize_path(path, dcc_name)


def create_scene_element(
    element_id: str,
    element_type: str,
    name: str,
    path: str,
    dcc_handle: Any = None,
    **properties
) -> SceneElement:
    """Helper to create a SceneElement with consistent formatting.
    
    Args:
        element_id: Unique element identifier.
        element_type: Type of element (e.g., "node", "object", "geometry").
        name: Human-readable name.
        path: Hierarchical path in scene.
        dcc_handle: DCC-specific object reference.
        **properties: Additional properties as keyword arguments.
        
    Returns:
        SceneElement instance.
    """
    return SceneElement(
        element_id=element_id,
        element_type=element_type,
        name=name,
        path=path,
        properties=properties,
        dcc_handle=dcc_handle
    )


def extract_element_name(path: str, separator: str = "|") -> str:
    """Extract element name from hierarchical path.
    
    Args:
        path: Hierarchical path (e.g., "|group|object").
        separator: Path separator character.
        
    Returns:
        Element name (last component of path).
    """
    if not path:
        return ""
    
    parts = path.split(separator)
    # Filter out empty parts
    parts = [p for p in parts if p]
    
    return parts[-1] if parts else ""


def detect_current_dcc() -> Optional[str]:
    """Detect the currently running DCC application.
    
    Returns:
        DCC name if detected, None otherwise.
    """
    # Check for Maya
    try:
        import maya.cmds
        return "maya"
    except ImportError:
        pass
    
    # Check for Houdini
    try:
        import hou
        return "houdini"
    except ImportError:
        pass
    
    # Check for Nuke
    try:
        import nuke
        return "nuke"
    except ImportError:
        pass
    
    # Check for Blender
    try:
        import bpy
        if hasattr(bpy, "app"):
            return "blender"
    except ImportError:
        pass
    
    # No DCC detected
    return None


def get_dcc_module_name(dcc_name: str) -> str:
    """Get the main module name for a DCC.
    
    Args:
        dcc_name: Name of the DCC.
        
    Returns:
        Module name string.
    """
    module_map = {
        "maya": "maya.cmds",
        "houdini": "hou",
        "nuke": "nuke",
        "blender": "bpy"
    }
    
    return module_map.get(dcc_name, "")


def is_dcc_available(dcc_name: str) -> bool:
    """Check if a specific DCC is available.
    
    Args:
        dcc_name: Name of the DCC to check.
        
    Returns:
        True if DCC is available, False otherwise.
    """
    module_name = get_dcc_module_name(dcc_name)
    
    if not module_name:
        return False
    
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def get_available_dccs() -> List[str]:
    """Get list of available DCCs.
    
    Returns:
        List of DCC names that are available.
    """
    dccs = ["maya", "houdini", "nuke", "blender"]
    return [dcc for dcc in dccs if is_dcc_available(dcc)]


class AdapterFactory:
    """Factory for creating DCC adapter instances.
    
    The AdapterFactory automatically selects and creates the appropriate
    adapter based on the current DCC environment.
    
    Example:
        factory = AdapterFactory()
        adapter = factory.create_adapter()  # Auto-detect
        
        # Or specify DCC
        adapter = factory.create_adapter("maya")
    """
    
    def __init__(self):
        """Initialize the adapter factory."""
        self._adapter_classes: Dict[str, Type] = {}
        self._adapter_instances: Dict[str, Any] = {}
        
    def register_adapter_class(
        self,
        dcc_name: str,
        adapter_class: Type
    ) -> None:
        """Register an adapter class for a DCC.
        
        Args:
            dcc_name: Name of the DCC.
            adapter_class: Adapter class to register.
        """
        self._adapter_classes[dcc_name] = adapter_class
        
    def create_adapter(
        self,
        dcc_name: Optional[str] = None,
        reuse_instance: bool = True
    ) -> Optional[Any]:
        """Create or get an adapter instance.
        
        Args:
            dcc_name: Optional DCC name. If not provided, auto-detect.
            reuse_instance: Whether to reuse existing instance.
            
        Returns:
            Adapter instance or None if not available.
            
        Raises:
            AdapterError: If adapter creation fails.
        """
        # Auto-detect if not specified
        if dcc_name is None:
            dcc_name = detect_current_dcc()
        
        if dcc_name is None:
            return None
        
        # Return existing instance if requested
        if reuse_instance and dcc_name in self._adapter_instances:
            return self._adapter_instances[dcc_name]
        
        # Check if adapter class is registered
        if dcc_name not in self._adapter_classes:
            # Try to import adapter dynamically
            self._try_import_adapter(dcc_name)
        
        if dcc_name not in self._adapter_classes:
            raise AdapterError(
                f"No adapter registered for DCC '{dcc_name}'"
            )
        
        # Create new instance
        try:
            adapter_class = self._adapter_classes[dcc_name]
            adapter = adapter_class()
            
            if reuse_instance:
                self._adapter_instances[dcc_name] = adapter
            
            return adapter
        except Exception as e:
            raise AdapterError(
                f"Failed to create adapter for '{dcc_name}': {e}"
            )
    
    def get_registered_dccs(self) -> List[str]:
        """Get list of registered DCC names.
        
        Returns:
            List of DCC names with registered adapters.
        """
        return list(self._adapter_classes.keys())
    
    def clear_instances(self) -> None:
        """Clear all cached adapter instances."""
        # Cleanup adapters
        for adapter in self._adapter_instances.values():
            if hasattr(adapter, "cleanup"):
                try:
                    adapter.cleanup()
                except Exception:
                    pass
        
        self._adapter_instances.clear()
    
    def _try_import_adapter(self, dcc_name: str) -> None:
        """Try to dynamically import an adapter.
        
        Args:
            dcc_name: Name of the DCC.
        """
        adapter_module_map = {
            "maya": "vfxvox_pipeline_utils.plugins.adapters.maya_adapter",
            "houdini": "vfxvox_pipeline_utils.plugins.adapters.houdini_adapter",
            "nuke": "vfxvox_pipeline_utils.plugins.adapters.nuke_adapter",
            "blender": "vfxvox_pipeline_utils.plugins.adapters.blender_adapter"
        }
        
        module_name = adapter_module_map.get(dcc_name)
        if not module_name:
            return
        
        try:
            module = __import__(module_name, fromlist=[""])
            
            # Get adapter class (assumes class name is <DCC>Adapter)
            class_name = f"{dcc_name.capitalize()}Adapter"
            if hasattr(module, class_name):
                adapter_class = getattr(module, class_name)
                self.register_adapter_class(dcc_name, adapter_class)
        except ImportError:
            pass


# Global adapter factory instance
_global_factory: Optional[AdapterFactory] = None


def get_adapter_factory() -> AdapterFactory:
    """Get the global adapter factory instance.
    
    Returns:
        Global AdapterFactory instance.
    """
    global _global_factory
    
    if _global_factory is None:
        _global_factory = AdapterFactory()
    
    return _global_factory


def reset_adapter_factory() -> None:
    """Reset the global adapter factory instance.
    
    Useful for testing.
    """
    global _global_factory
    
    if _global_factory:
        _global_factory.clear_instances()
    
    _global_factory = None
