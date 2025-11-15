"""
Core plugin infrastructure components.

This module contains the core classes and interfaces for the plugin system,
including the plugin manager, validator interface, context abstraction,
and session management.
"""

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

__all__ = [
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
