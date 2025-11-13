"""Custom rule loading and execution for USD linting."""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

from vfxvox_pipeline_utils.core.validators import ValidationIssue
from vfxvox_pipeline_utils.core.logging import get_logger
from vfxvox_pipeline_utils.core.exceptions import ConfigurationError
from .rules import LintRule

logger = get_logger(__name__)

try:
    from pxr import Usd
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False


class CustomRuleLoader:
    """Loads and manages custom linting rules from configuration.

    Supports:
    - Naming convention rules
    - Required metadata rules
    - Custom Python rules (via plugins)
    """

    def __init__(self, config_path: Path):
        """Initialize loader with custom rules configuration.

        Args:
            config_path: Path to YAML configuration file

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise ConfigurationError(
                f"Custom rules configuration not found: {config_path}",
                config_key=str(config_path)
            )

        # Load configuration
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in custom rules: {e}",
                config_key=str(config_path)
            )

        if not isinstance(self.config, dict):
            raise ConfigurationError(
                "Custom rules configuration must be a dictionary",
                config_key=str(config_path)
            )

    def load_rules(self) -> List[LintRule]:
        """Load custom rules from configuration.

        Returns:
            List of LintRule instances
        """
        rules: List[LintRule] = []

        custom_rules = self.config.get('custom_rules', [])

        for rule_config in custom_rules:
            try:
                rule = self._create_rule(rule_config)
                if rule:
                    rules.append(rule)
            except Exception as e:
                logger.error(f"Failed to create custom rule: {e}")

        logger.info(f"Loaded {len(rules)} custom rules")
        return rules

    def _create_rule(self, rule_config: Dict[str, Any]) -> LintRule:
        """Create a rule from configuration.

        Args:
            rule_config: Rule configuration dictionary

        Returns:
            LintRule instance

        Raises:
            ConfigurationError: If rule configuration is invalid
        """
        rule_type = rule_config.get('type')
        rule_name = rule_config.get('name', 'UnnamedRule')

        if rule_type == 'naming':
            return NamingConventionRule(rule_config)
        elif rule_type == 'metadata':
            return RequiredMetadataRule(rule_config)
        else:
            raise ConfigurationError(
                f"Unknown custom rule type: {rule_type}",
                config_key=rule_name
            )


class NamingConventionRule(LintRule):
    """Validates naming conventions based on patterns.

    Configuration example:
    ```yaml
    - name: "Naming conventions"
      type: "naming"
      patterns:
        prim: "^[A-Z][a-zA-Z0-9_]*$"
        property: "^[a-z][a-zA-Z0-9_]*$"
      severity: "warning"
    ```
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration.

        Args:
            config: Rule configuration dictionary
        """
        self.name = config.get('name', 'NamingConvention')
        self.description = config.get('description', 'Check naming conventions')
        self.severity = config.get('severity', 'warning')

        # Compile patterns
        self.patterns = {}
        patterns_config = config.get('patterns', {})

        for key, pattern in patterns_config.items():
            try:
                self.patterns[key] = re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern for {key}: {e}")

    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Check naming conventions.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        issues: List[ValidationIssue] = []

        prim_pattern = self.patterns.get('prim')
        property_pattern = self.patterns.get('property')

        for prim in stage.Traverse():
            # Check prim name
            if prim_pattern:
                prim_name = prim.GetName()
                if prim_name and not prim_pattern.match(prim_name):
                    issues.append(
                        ValidationIssue(
                            severity=self.severity,
                            message=f"Prim name '{prim_name}' doesn't match naming convention",
                            location=str(prim.GetPath()),
                            details={
                                "prim_name": prim_name,
                                "expected_pattern": prim_pattern.pattern
                            }
                        )
                    )

            # Check property names
            if property_pattern:
                for prop in prim.GetProperties():
                    prop_name = prop.GetName()
                    if not property_pattern.match(prop_name):
                        issues.append(
                            ValidationIssue(
                                severity=self.severity,
                                message=f"Property name '{prop_name}' doesn't match naming convention",
                                location=str(prim.GetPath()),
                                details={
                                    "property_name": prop_name,
                                    "expected_pattern": property_pattern.pattern
                                }
                            )
                        )

        return issues


class RequiredMetadataRule(LintRule):
    """Validates required metadata fields.

    Configuration example:
    ```yaml
    - name: "Required metadata"
      type: "metadata"
      required_fields:
        - "assetInfo:identifier"
        - "assetInfo:version"
      severity: "error"
    ```
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration.

        Args:
            config: Rule configuration dictionary
        """
        self.name = config.get('name', 'RequiredMetadata')
        self.description = config.get('description', 'Check required metadata')
        self.severity = config.get('severity', 'error')
        self.required_fields = config.get('required_fields', [])

    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Check required metadata.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        issues: List[ValidationIssue] = []

        # Check root layer metadata
        root_layer = stage.GetRootLayer()
        if root_layer:
            for field in self.required_fields:
                # Handle nested fields like "assetInfo:identifier"
                if ':' in field:
                    parts = field.split(':')
                    metadata = root_layer.customLayerData

                    # Navigate nested structure
                    value = metadata
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = None
                            break

                    if value is None:
                        issues.append(
                            ValidationIssue(
                                severity=self.severity,
                                message=f"Missing required metadata: {field}",
                                location=str(root_layer.identifier),
                                details={"required_field": field}
                            )
                        )
                else:
                    # Simple field
                    if not root_layer.HasField(field):
                        issues.append(
                            ValidationIssue(
                                severity=self.severity,
                                message=f"Missing required metadata: {field}",
                                location=str(root_layer.identifier),
                                details={"required_field": field}
                            )
                        )

        return issues
