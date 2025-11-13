"""Custom exception classes for VFXVox Pipeline Utils."""

from pathlib import Path
from typing import Optional, Any


class VFXVoxError(Exception):
    """Base exception for all toolkit errors.

    Attributes:
        message: Error message
        details: Optional dictionary with additional error context
    """

    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize VFXVoxError.

        Args:
            message: Error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ValidationError(VFXVoxError):
    """Raised when validation fails.

    Attributes:
        message: Error message
        target: The target that failed validation
        issues: List of validation issues
    """

    def __init__(
        self, message: str, target: Optional[Any] = None, issues: Optional[list] = None
    ):
        """Initialize ValidationError.

        Args:
            message: Error message
            target: The target that failed validation
            issues: List of validation issues
        """
        details = {}
        if target is not None:
            details["target"] = str(target)
        if issues:
            details["issue_count"] = len(issues)

        super().__init__(message, details)
        self.target = target
        self.issues = issues or []


class FileNotFoundError(VFXVoxError):
    """Raised when a required file is not found.

    Attributes:
        message: Error message
        path: Path to the missing file
    """

    def __init__(self, message: str, path: Optional[Path] = None):
        """Initialize FileNotFoundError.

        Args:
            message: Error message
            path: Path to the missing file
        """
        details = {}
        if path is not None:
            details["path"] = str(path)

        super().__init__(message, details)
        self.path = path


class InvalidFormatError(VFXVoxError):
    """Raised when a file format is not supported.

    Attributes:
        message: Error message
        format: The unsupported format
        supported_formats: List of supported formats
    """

    def __init__(
        self,
        message: str,
        format: Optional[str] = None,
        supported_formats: Optional[list] = None,
    ):
        """Initialize InvalidFormatError.

        Args:
            message: Error message
            format: The unsupported format
            supported_formats: List of supported formats
        """
        details = {}
        if format is not None:
            details["format"] = format
        if supported_formats:
            details["supported_formats"] = ", ".join(supported_formats)

        super().__init__(message, details)
        self.format = format
        self.supported_formats = supported_formats or []


class ConfigurationError(VFXVoxError):
    """Raised when configuration is invalid or missing.

    Attributes:
        message: Error message
        config_key: The configuration key that caused the error
    """

    def __init__(self, message: str, config_key: Optional[str] = None):
        """Initialize ConfigurationError.

        Args:
            message: Error message
            config_key: The configuration key that caused the error
        """
        details = {}
        if config_key is not None:
            details["config_key"] = config_key

        super().__init__(message, details)
        self.config_key = config_key
