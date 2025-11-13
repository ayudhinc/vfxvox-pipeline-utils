"""Custom exception classes for VFXVox Pipeline Utils."""


class VFXVoxError(Exception):
    """Base exception for all toolkit errors."""

    pass


class ValidationError(VFXVoxError):
    """Raised when validation fails."""

    pass


class FileNotFoundError(VFXVoxError):
    """Raised when a required file is not found."""

    pass


class InvalidFormatError(VFXVoxError):
    """Raised when a file format is not supported."""

    pass
