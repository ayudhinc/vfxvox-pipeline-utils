"""
Core plugin infrastructure components.

This module contains the core classes and interfaces for the plugin system,
including the plugin manager, validator interface, context abstraction,
and session management.
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
    IssueSeverity,
)
from vfxvox_pipeline_utils.plugins.core.session_manager import (
    SessionManager,
    ValidationSession,
    SessionFilters,
)
from vfxvox_pipeline_utils.plugins.core.result_aggregator import ResultAggregator

__all__ = [
    "PluginManager",
    "ValidatorPlugin",
    "ValidatorMetadata",
    "ValidatorParameter",
    "ValidationContext",
    "SceneElement",
    "SceneInfo",
    "ValidationScope",
    "IssueSeverity",
    "SessionManager",
    "ValidationSession",
    "SessionFilters",
    "ResultAggregator",
]
