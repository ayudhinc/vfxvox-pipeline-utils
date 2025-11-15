"""
Custom exceptions for the plugin system.

This module defines exception classes for different error categories
in the plugin system.
"""


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    pass


class AdapterError(PluginError):
    """Raised when DCC adapter fails."""
    pass


class ValidatorError(PluginError):
    """Raised when validator execution fails."""
    pass


class SessionError(PluginError):
    """Raised when session operations fail."""
    pass


class ConfigurationError(PluginError):
    """Raised when configuration loading or validation fails."""
    pass


class RegistrationError(PluginError):
    """Raised when plugin registration fails."""
    pass
