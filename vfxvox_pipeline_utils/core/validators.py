"""Base validator classes and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    severity: str  # 'error', 'warning', 'info'
    message: str
    location: Optional[str] = None
    details: Optional[dict] = None


@dataclass
class ValidationResult:
    """Represents the result of a validation operation."""

    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def has_errors(self) -> bool:
        """Check if result contains any errors."""
        return any(issue.severity == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if result contains any warnings."""
        return any(issue.severity == "warning" for issue in self.issues)


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    @abstractmethod
    def validate(self, target: Any) -> ValidationResult:
        """Perform validation and return results.

        Args:
            target: The target to validate (file path, directory, etc.)

        Returns:
            ValidationResult with issues found
        """
        pass
