"""Base validator classes and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional
from datetime import datetime


@dataclass
class ValidationIssue:
    """Represents a single validation issue.

    Attributes:
        severity: Issue severity ('error', 'warning', 'info')
        message: Human-readable issue description
        location: Optional location where issue was found
        details: Optional dictionary with additional context
    """

    severity: str  # 'error', 'warning', 'info'
    message: str
    location: Optional[str] = None
    details: Optional[dict] = None

    def __post_init__(self):
        """Validate severity level."""
        valid_severities = {"error", "warning", "info"}
        if self.severity not in valid_severities:
            raise ValueError(
                f"Invalid severity '{self.severity}'. Must be one of {valid_severities}"
            )

    def to_dict(self) -> dict:
        """Convert issue to dictionary.

        Returns:
            Dictionary representation of the issue
        """
        return {
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "details": self.details,
        }


@dataclass
class ValidationResult:
    """Represents the result of a validation operation.

    Attributes:
        passed: Whether validation passed without errors
        issues: List of validation issues found
        metadata: Additional metadata about the validation
    """

    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Add timestamp to metadata if not present."""
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now().isoformat()

    def has_errors(self) -> bool:
        """Check if result contains any errors.

        Returns:
            True if any issues have severity 'error'
        """
        return any(issue.severity == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if result contains any warnings.

        Returns:
            True if any issues have severity 'warning'
        """
        return any(issue.severity == "warning" for issue in self.issues)

    def has_issues(self) -> bool:
        """Check if result contains any issues.

        Returns:
            True if there are any issues (errors, warnings, or info)
        """
        return len(self.issues) > 0

    def get_errors(self) -> List[ValidationIssue]:
        """Get all error-level issues.

        Returns:
            List of issues with severity 'error'
        """
        return [issue for issue in self.issues if issue.severity == "error"]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warning-level issues.

        Returns:
            List of issues with severity 'warning'
        """
        return [issue for issue in self.issues if issue.severity == "warning"]

    def get_info(self) -> List[ValidationIssue]:
        """Get all info-level issues.

        Returns:
            List of issues with severity 'info'
        """
        return [issue for issue in self.issues if issue.severity == "info"]

    def error_count(self) -> int:
        """Get count of error-level issues.

        Returns:
            Number of errors
        """
        return len(self.get_errors())

    def warning_count(self) -> int:
        """Get count of warning-level issues.

        Returns:
            Number of warnings
        """
        return len(self.get_warnings())

    def info_count(self) -> int:
        """Get count of info-level issues.

        Returns:
            Number of info messages
        """
        return len(self.get_info())

    def add_issue(
        self,
        severity: str,
        message: str,
        location: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Add a new issue to the result.

        Args:
            severity: Issue severity ('error', 'warning', 'info')
            message: Human-readable issue description
            location: Optional location where issue was found
            details: Optional dictionary with additional context
        """
        issue = ValidationIssue(severity, message, location, details)
        self.issues.append(issue)

        # Update passed status if error added
        if severity == "error":
            self.passed = False

    def to_dict(self) -> dict:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of the result
        """
        return {
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
            "summary": {
                "total_issues": len(self.issues),
                "errors": self.error_count(),
                "warnings": self.warning_count(),
                "info": self.info_count(),
            },
        }


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
