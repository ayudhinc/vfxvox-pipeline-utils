"""
Plugin manager for validator and adapter registration.

This module provides the central registry for validators and DCC adapters,
along with plugin lifecycle management and DCC detection.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from vfxvox_pipeline_utils.plugins.core.exceptions import (
    PluginError,
    RegistrationError,
)
from vfxvox_pipeline_utils.plugins.core.session_manager import SessionManager
from vfxvox_pipeline_utils.plugins.core.validator_interface import (
    ValidatorMetadata,
    ValidatorPlugin,
    validate_validator_implementation,
)


class PluginManager:
    """Central registry for validators and DCC adapters.
    
    The PluginManager is responsible for:
    - Registering and managing validator plugins
    - Registering and managing DCC adapters
    - Auto-detecting the current DCC environment
    - Initializing the plugin system
    - Managing validation sessions
    
    Example:
        manager = PluginManager()
        manager.register_validator(my_validator)
        manager.initialize()
        
        validators = manager.list_validators(dcc_filter="maya")
        validator = manager.get_validator("my_validator_id")
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize plugin manager with optional config.
        
        Args:
            config_path: Optional path to configuration file.
        """
        self._validators: Dict[str, ValidatorPlugin] = {}
        self._validator_metadata: Dict[str, ValidatorMetadata] = {}
        self._adapters: Dict[str, "DCCAdapter"] = {}
        self._session_manager = SessionManager()
        self._current_adapter: Optional["DCCAdapter"] = None
        self._config = self._load_config(config_path)
        self._initialized = False
        
    def register_validator(
        self,
        validator: ValidatorPlugin,
        validate: bool = True
    ) -> None:
        """Register a validator plugin.
        
        Args:
            validator: Validator plugin instance to register.
            validate: Whether to validate the validator implementation.
            
        Raises:
            RegistrationError: If validator is invalid or already registered.
        """
        # Validate the validator implementation
        if validate:
            errors = validate_validator_implementation(validator)
            if errors:
                raise RegistrationError(
                    f"Validator validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
                )
        
        # Get metadata
        try:
            metadata = validator.get_metadata()
        except Exception as e:
            raise RegistrationError(f"Failed to get validator metadata: {e}")
        
        # Check for duplicate registration
        if metadata.id in self._validators:
            raise RegistrationError(
                f"Validator with id '{metadata.id}' is already registered"
            )
        
        # Register the validator
        self._validators[metadata.id] = validator
        self._validator_metadata[metadata.id] = metadata
        
    def register_adapter(
        self,
        dcc_name: str,
        adapter: "DCCAdapter"
    ) -> None:
        """Register a DCC adapter.
        
        Args:
            dcc_name: Name of the DCC (e.g., "maya", "houdini").
            adapter: DCC adapter instance.
            
        Raises:
            RegistrationError: If adapter is already registered.
        """
        if dcc_name in self._adapters:
            raise RegistrationError(
                f"Adapter for DCC '{dcc_name}' is already registered"
            )
        
        self._adapters[dcc_name] = adapter
        
    def get_validator(self, validator_id: str) -> ValidatorPlugin:
        """Get a registered validator by ID.
        
        Args:
            validator_id: Unique validator identifier.
            
        Returns:
            ValidatorPlugin instance.
            
        Raises:
            PluginError: If validator is not found.
        """
        if validator_id not in self._validators:
            raise PluginError(f"Validator '{validator_id}' not found")
        
        return self._validators[validator_id]
        
    def list_validators(
        self,
        dcc_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[ValidatorMetadata]:
        """List all registered validators, optionally filtered.
        
        Args:
            dcc_filter: Optional DCC name to filter by.
            category_filter: Optional category to filter by.
            
        Returns:
            List of ValidatorMetadata objects.
        """
        results = list(self._validator_metadata.values())
        
        if dcc_filter:
            results = [
                m for m in results
                if dcc_filter in m.supported_dccs or "standalone" in m.supported_dccs
            ]
        
        if category_filter:
            results = [m for m in results if m.category == category_filter]
        
        return sorted(results, key=lambda m: m.name)
        
    def detect_dcc(self) -> Optional[str]:
        """Auto-detect the current DCC application.
        
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
        
        # No DCC detected, running standalone
        return "standalone"
        
    def initialize(self, dcc_name: Optional[str] = None) -> bool:
        """Initialize the plugin system for the current DCC.
        
        Args:
            dcc_name: Optional DCC name. If not provided, auto-detect.
            
        Returns:
            True if initialization succeeded, False otherwise.
            
        Raises:
            PluginError: If initialization fails.
        """
        if self._initialized:
            return True
        
        # Detect or use provided DCC name
        if dcc_name is None:
            dcc_name = self.detect_dcc()
        
        if dcc_name is None:
            raise PluginError("Could not detect DCC environment")
        
        # Get the adapter for this DCC
        if dcc_name != "standalone" and dcc_name in self._adapters:
            self._current_adapter = self._adapters[dcc_name]
        
        self._initialized = True
        return True
        
    def get_current_adapter(self) -> Optional["DCCAdapter"]:
        """Get the current DCC adapter.
        
        Returns:
            Current DCCAdapter instance or None if not initialized.
        """
        return self._current_adapter
        
    def get_session_manager(self) -> SessionManager:
        """Get the session manager.
        
        Returns:
            SessionManager instance.
        """
        return self._session_manager
        
    def is_initialized(self) -> bool:
        """Check if the plugin system is initialized.
        
        Returns:
            True if initialized, False otherwise.
        """
        return self._initialized
        
    def get_validator_count(self) -> int:
        """Get the number of registered validators.
        
        Returns:
            Number of registered validators.
        """
        return len(self._validators)
        
    def get_adapter_count(self) -> int:
        """Get the number of registered adapters.
        
        Returns:
            Number of registered adapters.
        """
        return len(self._adapters)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file.
            
        Returns:
            Configuration dictionary.
        """
        if config_path is None:
            # Try to find default config
            config_path = self._find_default_config()
        
        if config_path and os.path.exists(config_path):
            import yaml
            
            try:
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                # Log warning but don't fail
                print(f"Warning: Failed to load config from {config_path}: {e}")
                return {}
        
        return {}
        
    def _find_default_config(self) -> Optional[str]:
        """Find the default configuration file.
        
        Returns:
            Path to default config file or None.
        """
        # Look for config in package
        try:
            from vfxvox_pipeline_utils.plugins import config
            config_dir = Path(config.__file__).parent
            config_file = config_dir / "plugin_config.yaml"
            
            if config_file.exists():
                return str(config_file)
        except Exception:
            pass
        
        # Look for config in user home
        home_config = Path.home() / ".vfxvox" / "plugin_config.yaml"
        if home_config.exists():
            return str(home_config)
        
        return None


# Global plugin manager instance
_global_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance.
    
    Returns:
        Global PluginManager instance.
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = PluginManager()
    
    return _global_manager


def reset_plugin_manager() -> None:
    """Reset the global plugin manager instance.
    
    Useful for testing.
    """
    global _global_manager
    _global_manager = None
