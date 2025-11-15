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
    """Base interface for validator plugins.
    
    All validator plugins must inherit from this class and implement
    the abstract methods: get_metadata, validate, and get_parameters.
    
    Example:
        class MyValidator(ValidatorPlugin):
            def get_metadata(self) -> ValidatorMetadata:
                return ValidatorMetadata(
                    id="my_validator",
                    name="My Validator",
                    description="Validates something",
                    version="1.0.0",
                    author="Studio",
                    supported_dccs=["maya", "houdini"],
                    category="geometry",
                    requires_selection=True,
                    supports_batch=False,
                    estimated_duration="fast"
                )
            
            def validate(self, context: ValidationContext) -> ValidationResult:
                # Validation logic here
                pass
            
            def get_parameters(self) -> List[ValidatorParameter]:
                return []
    """
    
    @abstractmethod
    def get_metadata(self) -> ValidatorMetadata:
        """Return validator metadata including name, description, supported DCCs.
        
        Returns:
            ValidatorMetadata: Metadata describing this validator.
        """
        pass
        
    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute validation with the given context.
        
        Args:
            context: Validation context containing scene data and parameters.
            
        Returns:
            ValidationResult: Result containing any issues found.
            
        Raises:
            ValidatorError: If validation fails to execute.
        """
        pass
        
    @abstractmethod
    def get_parameters(self) -> List[ValidatorParameter]:
        """Return list of configurable parameters for this validator.
        
        Returns:
            List of ValidatorParameter objects describing configurable options.
        """
        pass
        
    def supports_dcc(self, dcc_name: str) -> bool:
        """Check if this validator supports the given DCC.
        
        Args:
            dcc_name: Name of the DCC application (e.g., "maya", "houdini").
            
        Returns:
            True if this validator supports the DCC, False otherwise.
        """
        return dcc_name in self.get_metadata().supported_dccs
        
    def get_ui_config(self) -> Optional[UIConfig]:
        """Return UI configuration for this validator.
        
        Returns:
            UIConfig object or None if no custom UI configuration.
        """
        return None
        
    def can_auto_fix(self) -> bool:
        """Return True if this validator can automatically fix issues.
        
        Returns:
            True if auto-fix is supported, False otherwise.
        """
        return False
        
    def auto_fix(
        self,
        issue: ValidationIssue,
        context: ValidationContext
    ) -> FixResult:
        """Attempt to automatically fix the given issue.
        
        Args:
            issue: The validation issue to fix.
            context: Validation context for accessing scene data.
            
        Returns:
            FixResult indicating success or failure.
            
        Raises:
            NotImplementedError: If auto-fix is not supported.
        """
        raise NotImplementedError("Auto-fix not supported")
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize parameter values.
        
        Args:
            parameters: Dictionary of parameter values to validate.
            
        Returns:
            Dictionary of validated and normalized parameters.
            
        Raises:
            ValueError: If required parameters are missing or invalid.
        """
        param_defs = {p.name: p for p in self.get_parameters()}
        validated = {}
        
        # Check required parameters
        for param_name, param_def in param_defs.items():
            if param_def.required and param_name not in parameters:
                raise ValueError(f"Required parameter '{param_name}' is missing")
        
        # Validate and normalize each parameter
        for param_name, value in parameters.items():
            if param_name not in param_defs:
                # Unknown parameter, skip or warn
                continue
                
            param_def = param_defs[param_name]
            validated[param_name] = self._validate_parameter_value(
                param_name, value, param_def
            )
        
        # Add defaults for missing optional parameters
        for param_name, param_def in param_defs.items():
            if param_name not in validated:
                validated[param_name] = param_def.default
        
        return validated
    
    def _validate_parameter_value(
        self,
        name: str,
        value: Any,
        param_def: ValidatorParameter
    ) -> Any:
        """Validate a single parameter value.
        
        Args:
            name: Parameter name.
            value: Parameter value to validate.
            param_def: Parameter definition.
            
        Returns:
            Validated and normalized value.
            
        Raises:
            ValueError: If value is invalid.
        """
        param_type = param_def.type
        
        # Type validation
        if param_type == "int":
            try:
                value = int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Parameter '{name}' must be an integer")
                
            if param_def.min_value is not None and value < param_def.min_value:
                raise ValueError(
                    f"Parameter '{name}' must be >= {param_def.min_value}"
                )
            if param_def.max_value is not None and value > param_def.max_value:
                raise ValueError(
                    f"Parameter '{name}' must be <= {param_def.max_value}"
                )
                
        elif param_type == "float":
            try:
                value = float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Parameter '{name}' must be a number")
                
            if param_def.min_value is not None and value < param_def.min_value:
                raise ValueError(
                    f"Parameter '{name}' must be >= {param_def.min_value}"
                )
            if param_def.max_value is not None and value > param_def.max_value:
                raise ValueError(
                    f"Parameter '{name}' must be <= {param_def.max_value}"
                )
                
        elif param_type == "bool":
            if isinstance(value, str):
                value = value.lower() in ("true", "yes", "1", "on")
            else:
                value = bool(value)
                
        elif param_type == "choice":
            if param_def.choices and value not in param_def.choices:
                raise ValueError(
                    f"Parameter '{name}' must be one of {param_def.choices}"
                )
                
        elif param_type == "string":
            value = str(value)
            
        elif param_type in ("file", "directory"):
            value = str(value)
            # Could add path validation here
        
        return value



def create_validation_issue(
    severity: IssueSeverity,
    category: str,
    message: str,
    description: str,
    element: Optional[SceneElement] = None,
    location: Optional[str] = None,
    suggested_fix: Optional[str] = None,
    can_auto_fix: bool = False,
    documentation_url: Optional[str] = None,
    **metadata
) -> ValidationIssue:
    """Helper function to create a ValidationIssue.
    
    Args:
        severity: Issue severity level.
        category: Issue category.
        message: Short issue message.
        description: Detailed issue description.
        element: Optional scene element associated with issue.
        location: Optional location string.
        suggested_fix: Optional suggestion for fixing the issue.
        can_auto_fix: Whether this issue can be automatically fixed.
        documentation_url: Optional URL to documentation.
        **metadata: Additional metadata as keyword arguments.
        
    Returns:
        ValidationIssue object.
    """
    import uuid
    
    return ValidationIssue(
        issue_id=str(uuid.uuid4()),
        severity=severity,
        category=category,
        message=message,
        description=description,
        element=element,
        location=location,
        suggested_fix=suggested_fix,
        can_auto_fix=can_auto_fix,
        documentation_url=documentation_url,
        metadata=metadata
    )


def create_validation_result(
    validator_id: str,
    validator_name: str,
    context_id: str,
    duration_seconds: float,
    issues: List[ValidationIssue],
    **metadata
) -> ValidationResult:
    """Helper function to create a ValidationResult.
    
    Args:
        validator_id: Unique validator identifier.
        validator_name: Human-readable validator name.
        context_id: ID of the validation context.
        duration_seconds: Time taken to execute validation.
        issues: List of validation issues found.
        **metadata: Additional metadata as keyword arguments.
        
    Returns:
        ValidationResult object.
    """
    return ValidationResult(
        validator_id=validator_id,
        validator_name=validator_name,
        context_id=context_id,
        timestamp=datetime.utcnow(),
        duration_seconds=duration_seconds,
        issues=issues,
        metadata=metadata
    )


def validate_validator_implementation(validator: ValidatorPlugin) -> List[str]:
    """Validate that a validator implementation is correct.
    
    Checks that the validator properly implements the required interface
    and returns valid metadata and parameters.
    
    Args:
        validator: Validator instance to validate.
        
    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    
    # Check metadata
    try:
        metadata = validator.get_metadata()
        
        if not metadata.id:
            errors.append("Validator metadata must have a non-empty id")
        if not metadata.name:
            errors.append("Validator metadata must have a non-empty name")
        if not metadata.version:
            errors.append("Validator metadata must have a version")
        if not metadata.supported_dccs:
            errors.append("Validator must support at least one DCC")
        if metadata.category not in [
            "scene", "geometry", "usd", "sequence", "render", "custom"
        ]:
            errors.append(
                f"Invalid category '{metadata.category}'. Must be one of: "
                "scene, geometry, usd, sequence, render, custom"
            )
        if metadata.estimated_duration not in ["fast", "medium", "slow"]:
            errors.append(
                f"Invalid estimated_duration '{metadata.estimated_duration}'. "
                "Must be one of: fast, medium, slow"
            )
            
    except Exception as e:
        errors.append(f"Error getting metadata: {e}")
    
    # Check parameters
    try:
        parameters = validator.get_parameters()
        
        param_names = set()
        for param in parameters:
            if not param.name:
                errors.append("Parameter must have a non-empty name")
            elif param.name in param_names:
                errors.append(f"Duplicate parameter name: {param.name}")
            else:
                param_names.add(param.name)
                
            if param.type not in [
                "string", "int", "float", "bool", "choice", "file", "directory"
            ]:
                errors.append(
                    f"Invalid parameter type '{param.type}' for parameter "
                    f"'{param.name}'"
                )
                
            if param.type == "choice" and not param.choices:
                errors.append(
                    f"Parameter '{param.name}' has type 'choice' but no choices"
                )
                
    except Exception as e:
        errors.append(f"Error getting parameters: {e}")
    
    return errors
