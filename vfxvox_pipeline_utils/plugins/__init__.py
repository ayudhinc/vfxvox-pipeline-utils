"""
VFXVox Plugin API - Unified abstraction layer for DCC integration.

This package provides a plugin system that enables VFXVox validators to work
seamlessly across different Digital Content Creation (DCC) applications.
"""

from vfxvox_pipeline_utils.plugins.core.plugin_manager import PluginManager
from vfxvox_pipeline_utils.plugins.core.validator_interface import (
    ValidatorPlugin,
    ValidatorMetadata,
    ValidatorParameter,
)
from vfxvox_pipeline_utils.plugins.core.context import (
    ValidationContext,
    SceneElement,
    SceneInfo,
    ValidationScope,
)
from vfxvox_pipeline_utils.plugins.core.session_manager import (
    SessionManager,
    ValidationSession,
)

__version__ = "1.0.0"

__all__ = [
    "PluginManager",
    "ValidatorPlugin",
    "ValidatorMetadata",
    "ValidatorParameter",
    "ValidationContext",
    "SceneElement",
    "SceneInfo",
    "ValidationScope",
    "SessionManager",
    "ValidationSession",
]
