"""
Validator plugin interface.

This module defines the base interface that all validator plugins must implement,
along with supporting data structures for metadata, parameters, and results.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from vfxvox_pipeline_utils.plugins.core.context import (
    IssueSeverity,
    SceneElement,
    ValidationContext,
)


@dataclass
class ValidatorMetadata:
    """Metadata describing a validator plugin."""
    id: str
    name: str
    description: str
    version: str
    author: str
    supported_dccs: List[str]  # ["maya", "houdini", "nuke", "blender", "standalone"]
    category: str  # "scene", "geometry", "usd", "sequence", "render"
    requires_selection: bool
    supports_batch: bool
    estimated_duration: str  # "fast", "medium", "slow"


@dataclass
class ValidatorParameter:
    """A configurable parameter for a validator."""
    name: str
    label: str
    type: str  # "string", "int", "float", "bool", "choice", "file", "directory"
    default: Any
    required: bool
    description: str
    choices: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class ValidationIssue:
    """A single validation issue."""
    issue_id: str
    severity: IssueSeverity
    category: str
    message: str
    description: str
    element: Optional[SceneElement] = None
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    can_auto_fix: bool = False
    documentation_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationSummary:
    """Summary of validation results."""
    total_issues: int
    errors: int
    warnings: int
    info: int
    passed: bool


@dataclass
class ValidationResult:
    """Result from a validation operation."""
    validator_id: str
    validator_name: str
    context_id: str
    timestamp: datetime
    duration_seconds: float
    issues: List[ValidationIssue]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_errors(self) -> bool:
        """Check if result contains any errors."""
        return any(i.severity == IssueSeverity.ERROR for i in self.issues)
        
    def has_warnings(self) -> bool:
        """Check if result contains any warnings."""
        return any(i.severity == IssueSeverity.WARNING for i in self.issues)
        
    def get_summary(self) -> ValidationSummary:
        """Get summary statistics for this result."""
        errors = sum(1 for i in self.issues if i.severity == IssueSeverity.ERROR)
        warnings = sum(1 for i in self.issues if i.severity == IssueSeverity.WARNING)
        info = sum(1 for i in self.issues if i.severity == IssueSeverity.INFO)
        
        return ValidationSummary(
            total_issues=len(self.issues),
            errors=errors,
            warnings=warnings,
            info=info,
            passed=len(self.issues) == 0
        )


@dataclass
class FixResult:
    """Result from an auto-fix operation."""
    success: bool
    message: str
    modified_elements: List[SceneElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UIConfig:
    """UI configuration for a validator."""
    icon: Optional[str] = None
    color: Optional[str] = None
    shortcut: Optional[str] = None
    tooltip: Optional[str] = None


class ValidatorPlugin(ABC):
    """Base interface for validator plugins."""
    
    @abstractmethod
    def get_metadata(self) -> ValidatorMetadata:
        """Return validator metadata including name, description, supported DCCs."""
        pass
        
    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute validation with the given context."""
        pass
        
    @abstractmethod
    def get_parameters(self) -> List[ValidatorParameter]:
        """Return list of configurable parameters for this validator."""
        pass
        
    def supports_dcc(self, dcc_name: str) -> bool:
        """Check if this validator supports the given DCC."""
        return dcc_name in self.get_metadata().supported_dccs
        
    def get_ui_config(self) -> Optional[UIConfig]:
        """Return UI configuration for this validator."""
        return None
        
    def can_auto_fix(self) -> bool:
        """Return True if this validator can automatically fix issues."""
        return False
        
    def auto_fix(
        self,
        issue: ValidationIssue,
        context: ValidationContext
    ) -> FixResult:
        """Attempt to automatically fix the given issue."""
        raise NotImplementedError("Auto-fix not supported")
