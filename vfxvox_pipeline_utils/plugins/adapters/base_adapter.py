"""
Base DCC adapter interface.

This module defines the abstract base class that all DCC adapters must implement
to provide a unified interface for interacting with different DCC applications.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from vfxvox_pipeline_utils.plugins.core.context import (
    SceneElement,
    SceneInfo,
    ValidationContext,
    ValidationScope,
)
from vfxvox_pipeline_utils.plugins.core.validator_interface import (
    ValidatorMetadata,
    ValidationResult,
)


class DCCAdapter(ABC):
    """Base class for DCC-specific adapters.
    
    DCC adapters translate between DCC-specific APIs and the VFXVox Plugin API
    abstraction layer. Each DCC (Maya, Houdini, Nuke, Blender) has its own
    adapter implementation that inherits from this base class.
    
    The adapter is responsible for:
    - Identifying the DCC and its version
    - Creating validation contexts from DCC scene data
    - Getting scene information and selection
    - Highlighting elements in the DCC
    - Displaying validation results
    - Registering validators in the DCC menu system
    
    Example:
        class MayaAdapter(DCCAdapter):
            def get_dcc_name(self) -> str:
                return "maya"
            
            def get_dcc_version(self) -> str:
                import maya.cmds as cmds
                return cmds.about(version=True)
            
            # Implement other abstract methods...
    """
    
    @abstractmethod
    def get_dcc_name(self) -> str:
        """Return the name of this DCC.
        
        Returns:
            DCC name (e.g., "maya", "houdini", "nuke", "blender").
        """
        pass
        
    @abstractmethod
    def get_dcc_version(self) -> str:
        """Return the version of this DCC.
        
        Returns:
            DCC version string (e.g., "2024.1", "19.5.640").
        """
        pass
        
    @abstractmethod
    def create_context(
        self,
        scope: ValidationScope,
        parameters: Optional[dict] = None
    ) -> ValidationContext:
        """Create a validation context from current DCC state.
        
        Args:
            scope: Scope of validation (selection, scene, file, batch).
            parameters: Optional parameters for context creation.
            
        Returns:
            ValidationContext containing DCC scene data.
            
        Raises:
            AdapterError: If context creation fails.
        """
        pass
        
    @abstractmethod
    def get_selection(self) -> List[SceneElement]:
        """Get currently selected elements.
        
        Returns:
            List of SceneElement objects representing the selection.
        """
        pass
        
    @abstractmethod
    def get_scene_info(self) -> SceneInfo:
        """Get information about the current scene.
        
        Returns:
            SceneInfo object with scene metadata.
        """
        pass
        
    @abstractmethod
    def highlight_elements(self, elements: List[SceneElement]) -> None:
        """Highlight the given elements in the DCC.
        
        Args:
            elements: List of scene elements to highlight/select.
            
        Raises:
            AdapterError: If highlighting fails.
        """
        pass
        
    @abstractmethod
    def show_results_ui(self, results: ValidationResult) -> None:
        """Display validation results in DCC-native UI.
        
        Args:
            results: Validation results to display.
            
        Raises:
            AdapterError: If UI display fails.
        """
        pass
        
    @abstractmethod
    def register_menu(self, validators: List[ValidatorMetadata]) -> None:
        """Register validators in DCC menu system.
        
        Args:
            validators: List of validator metadata for menu creation.
            
        Raises:
            AdapterError: If menu registration fails.
        """
        pass
    
    def is_available(self) -> bool:
        """Check if this DCC is currently available.
        
        Returns:
            True if the DCC is available, False otherwise.
        """
        try:
            self.get_dcc_version()
            return True
        except Exception:
            return False
    
    def get_dcc_info(self) -> dict:
        """Get DCC information as a dictionary.
        
        Returns:
            Dictionary with DCC name and version.
        """
        return {
            "name": self.get_dcc_name(),
            "version": self.get_dcc_version(),
            "available": self.is_available()
        }
    
    def supports_scope(self, scope: ValidationScope) -> bool:
        """Check if this adapter supports the given validation scope.
        
        Args:
            scope: Validation scope to check.
            
        Returns:
            True if scope is supported, False otherwise.
        """
        # By default, all adapters support all scopes
        # Subclasses can override to restrict supported scopes
        return True
    
    def cleanup(self) -> None:
        """Cleanup adapter resources.
        
        Called when the adapter is no longer needed.
        Subclasses can override to perform cleanup operations.
        """
        pass
