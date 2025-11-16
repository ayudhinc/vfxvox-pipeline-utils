"""
VFXVox Plugin API - Unified abstraction layer for DCC integration.

This package provides a plugin system that enables VFXVox validators to work
seamlessly across different Digital Content Creation (DCC) applications.
"""

from vfxvox_pipeline_utils.plugins.core.plugin_manager import (
    PluginManager,
    get_plugin_manager,
    reset_plugin_manager,
)
from vfxvox_pipeline_utils.plugins.core.context import (
    ValidationContext,
    SceneElement,
    SceneInfo,
    ValidationScope,
    IssueSeverity,
)
from vfxvox_pipeline_utils.plugins.core.validator_interface import (
    ValidatorPlugin,
    ValidatorMetadata,
    ValidatorParameter,
    ValidationResult,
    ValidationIssue,
    ValidationSummary,
    FixResult,
    UIConfig,
    create_validation_issue,
    create_validation_result,
    validate_validator_implementation,
)
from vfxvox_pipeline_utils.plugins.core.session_manager import (
    SessionManager,
    ValidationSession,
    SessionFilters,
)
from vfxvox_pipeline_utils.plugins.core.exceptions import (
    PluginError,
    AdapterError,
    ValidatorError,
    SessionError,
    ConfigurationError,
    RegistrationError,
)

__version__ = "1.0.0"

__all__ = [
    # Plugin Manager
    "PluginManager",
    "get_plugin_manager",
    "reset_plugin_manager",
    # Context
    "ValidationContext",
    "SceneElement",
    "SceneInfo",
    "ValidationScope",
    "IssueSeverity",
    # Validator Interface
    "ValidatorPlugin",
    "ValidatorMetadata",
    "ValidatorParameter",
    "ValidationResult",
    "ValidationIssue",
    "ValidationSummary",
    "FixResult",
    "UIConfig",
    "create_validation_issue",
    "create_validation_result",
    "validate_validator_implementation",
    # Session Management
    "SessionManager",
    "ValidationSession",
    "SessionFilters",
    # Exceptions
    "PluginError",
    "AdapterError",
    "ValidatorError",
    "SessionError",
    "ConfigurationError",
    "RegistrationError",
]
