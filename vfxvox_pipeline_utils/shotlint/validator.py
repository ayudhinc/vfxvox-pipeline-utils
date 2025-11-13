"""ShotLint validator for directory structure validation."""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from vfxvox_pipeline_utils.core.validators import BaseValidator, ValidationResult, ValidationIssue
from vfxvox_pipeline_utils.core.exceptions import FileNotFoundError, ConfigurationError
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


class ShotLintValidator(BaseValidator):
    """Validates directory structures using rule-based configuration.

    This validator checks directory structures against declarative YAML rules,
    supporting path patterns, filename regex, frame sequences, file presence,
    and custom plugins.

    Example:
        >>> validator = ShotLintValidator()
        >>> result = validator.validate("./project", rules_path="rules.yaml")
        >>> if result.has_errors():
        ...     print(f"Found {result.error_count()} errors")
    """

    def __init__(self):
        """Initialize ShotLint validator."""
        self.rules: List[Dict[str, Any]] = []

    def validate(self, root: Path, rules_path: Path) -> ValidationResult:
        """Validate a directory structure against rules.

        Args:
            root: Root directory to validate (as Path or string)
            rules_path: Path to YAML rules file

        Returns:
            ValidationResult with issues found

        Raises:
            FileNotFoundError: If root directory or rules file doesn't exist
            ConfigurationError: If rules file is invalid
        """
        # Convert to Path objects
        root = Path(root) if not isinstance(root, Path) else root
        rules_path = Path(rules_path) if not isinstance(rules_path, Path) else rules_path

        # Validate inputs
        if not root.exists():
            raise FileNotFoundError(
                f"Root directory not found: {root}",
                path=root
            )

        if not root.is_dir():
            raise FileNotFoundError(
                f"Root path is not a directory: {root}",
                path=root
            )

        if not rules_path.exists():
            raise FileNotFoundError(
                f"Rules file not found: {rules_path}",
                path=rules_path
            )

        # Load rules
        try:
            self.rules = self.load_rules(rules_path)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load rules: {e}",
                config_key=str(rules_path)
            )

        # Create result
        result = ValidationResult(
            passed=True,
            metadata={
                "validator": "ShotLintValidator",
                "root": str(root),
                "rules_file": str(rules_path),
                "rule_count": len(self.rules),
            }
        )

        # Execute rules
        logger.info(f"Validating {root} with {len(self.rules)} rules")

        for rule in self.rules:
            try:
                self._execute_rule(root, rule, result)
            except Exception as e:
                logger.error(f"Rule '{rule.get('name', '<unknown>')}' crashed: {e}")
                result.add_issue(
                    severity="error",
                    message=f"Rule execution failed: {e}",
                    location=rule.get("name", "<unknown>"),
                    details={"rule": rule}
                )

        logger.info(
            f"Validation complete: {result.error_count()} errors, "
            f"{result.warning_count()} warnings"
        )

        return result

    def load_rules(self, rules_path: Path) -> List[Dict[str, Any]]:
        """Load validation rules from YAML file.

        Args:
            rules_path: Path to YAML rules file

        Returns:
            List of rule dictionaries

        Raises:
            ConfigurationError: If YAML is invalid or missing 'rules' key
        """
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in rules file: {e}",
                config_key=str(rules_path)
            )

        if not isinstance(config, dict):
            raise ConfigurationError(
                "Rules file must contain a dictionary",
                config_key=str(rules_path)
            )

        rules = config.get("rules", [])

        if not isinstance(rules, list):
            raise ConfigurationError(
                "'rules' must be a list",
                config_key=str(rules_path)
            )

        logger.debug(f"Loaded {len(rules)} rules from {rules_path}")
        return rules

    def _execute_rule(
        self,
        root: Path,
        rule: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Execute a single validation rule.

        Args:
            root: Root directory being validated
            rule: Rule dictionary
            result: ValidationResult to add issues to
        """
        from .engine import RuleEngine

        rule_name = rule.get("name", "<unknown>")
        rule_type = rule.get("type")

        if not rule_type:
            result.add_issue(
                severity="warning",
                message="Rule missing 'type' field",
                location=rule_name,
                details={"rule": rule}
            )
            return

        logger.debug(f"Executing rule '{rule_name}' (type: {rule_type})")

        engine = RuleEngine(root)
        issues = engine.execute_rule(rule)

        for issue in issues:
            result.issues.append(issue)
