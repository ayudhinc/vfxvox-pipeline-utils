"""USD linter for validating Universal Scene Description files."""

from pathlib import Path
from typing import List, Optional

from vfxvox_pipeline_utils.core.validators import BaseValidator, ValidationResult, ValidationIssue
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.exceptions import FileNotFoundError, InvalidFormatError
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)

# Check if USD is available
try:
    from pxr import Usd, Sdf
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    logger.warning("USD Python bindings not available. Install with: pip install usd-core")


class USDLinter(BaseValidator):
    """Lints USD files for issues and best practices.

    Checks for:
    - Broken or missing references
    - Invalid schema definitions
    - Performance issues (layer depth, composition complexity)
    - Custom studio-specific rules

    Example:
        >>> linter = USDLinter()
        >>> result = linter.validate(Path("asset.usd"))
        >>> if result.has_errors():
        ...     print(f"Found {result.error_count()} errors")

    Note:
        Requires USD Python bindings (usd-core package)
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize linter with configuration.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.rules: List = []

    def validate(self, file_path: Path) -> ValidationResult:
        """Lint a USD file and return results.

        Args:
            file_path: Path to USD file (.usd, .usda, .usdc, .usdz)

        Returns:
            ValidationResult with issues found

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidFormatError: If file is not a USD file
            ImportError: If USD Python bindings not available
        """
        # Convert to Path
        file_path = Path(file_path) if not isinstance(file_path, Path) else file_path

        logger.info(f"Linting USD file: {file_path}")

        # Check USD availability
        if not USD_AVAILABLE:
            raise ImportError(
                "USD Python bindings not installed. "
                "Install with: pip install vfxvox-pipeline-utils[usd]"
            )

        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"USD file not found: {file_path}",
                path=file_path
            )

        # Validate file format
        valid_extensions = {'.usd', '.usda', '.usdc', '.usdz'}
        if file_path.suffix.lower() not in valid_extensions:
            raise InvalidFormatError(
                f"Not a USD file: {file_path}",
                format=file_path.suffix,
                supported_formats=list(valid_extensions)
            )

        # Create result
        result = ValidationResult(
            passed=True,
            metadata={
                "validator": "USDLinter",
                "file_path": str(file_path),
                "file_format": file_path.suffix,
            }
        )

        try:
            # Load USD stage
            stage = self.load_stage(file_path)

            if not stage:
                result.add_issue(
                    severity="error",
                    message="Failed to load USD stage",
                    location=str(file_path)
                )
                return result

            # Update metadata
            result.metadata.update({
                "stage_loaded": True,
                "root_layer": str(stage.GetRootLayer().identifier) if stage.GetRootLayer() else None,
            })

            # Apply linting rules
            issues = self.apply_rules(stage)
            for issue in issues:
                result.issues.append(issue)

            logger.info(
                f"Linting complete: {result.error_count()} errors, "
                f"{result.warning_count()} warnings"
            )

        except Exception as e:
            logger.error(f"Linting failed: {e}", exc_info=True)
            result.add_issue(
                severity="error",
                message=f"Linting failed: {e}",
                location=str(file_path)
            )

        return result

    def load_stage(self, file_path: Path) -> Optional['Usd.Stage']:
        """Load USD stage for analysis.

        Args:
            file_path: Path to USD file

        Returns:
            Usd.Stage object or None if loading fails
        """
        try:
            stage = Usd.Stage.Open(str(file_path))
            if stage:
                logger.debug(f"Loaded USD stage: {file_path}")
            else:
                logger.error(f"Failed to open USD stage: {file_path}")
            return stage
        except Exception as e:
            logger.error(f"Error loading USD stage: {e}", exc_info=True)
            return None

    def apply_rules(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Apply all linting rules to the stage.

        Args:
            stage: USD Stage to lint

        Returns:
            List of ValidationIssue objects
        """
        from .rules import get_builtin_rules

        issues: List[ValidationIssue] = []

        # Get built-in rules
        rules = get_builtin_rules(self.config)

        # Apply each rule
        for rule in rules:
            try:
                logger.debug(f"Applying rule: {rule.name}")
                rule_issues = rule.check(stage)
                issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Rule '{rule.name}' failed: {e}", exc_info=True)
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=f"Rule execution failed: {e}",
                        location=rule.name,
                        details={"error": str(e)}
                    )
                )

        # Load and apply custom rules if configured
        custom_rules_path = self.config.get("usd.custom_rules_path")
        if custom_rules_path:
            try:
                from .custom_rules import CustomRuleLoader
                loader = CustomRuleLoader(Path(custom_rules_path))
                custom_rules = loader.load_rules()

                for rule in custom_rules:
                    try:
                        logger.debug(f"Applying custom rule: {rule.name}")
                        rule_issues = rule.check(stage)
                        issues.extend(rule_issues)
                    except Exception as e:
                        logger.error(f"Custom rule '{rule.name}' failed: {e}")
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                message=f"Custom rule execution failed: {e}",
                                location=rule.name,
                                details={"error": str(e)}
                            )
                        )
            except Exception as e:
                logger.error(f"Failed to load custom rules: {e}")
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Failed to load custom rules: {e}",
                        location=str(custom_rules_path)
                    )
                )

        return issues
