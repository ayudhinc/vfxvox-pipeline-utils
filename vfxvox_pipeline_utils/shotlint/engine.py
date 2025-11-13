"""Rule execution engine for ShotLint."""

from pathlib import Path
from typing import List, Dict, Any, Callable

from vfxvox_pipeline_utils.core.validators import ValidationIssue
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


class RuleEngine:
    """Executes validation rules against directory structures.

    The engine dispatches rules to appropriate handlers based on rule type
    and collects validation issues.
    """

    def __init__(self, root: Path):
        """Initialize rule engine.

        Args:
            root: Root directory being validated
        """
        self.root = Path(root)
        self._dispatch: Dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register rule type handlers."""
        from .rules import (
            PathPatternRule,
            FilenameRegexRule,
            FrameSequenceRule,
            MustExistRule,
        )
        from .plugins import PluginRule

        self._dispatch = {
            "path_pattern": PathPatternRule().check,
            "filename_regex": FilenameRegexRule().check,
            "frame_sequence": FrameSequenceRule().check,
            "must_exist": MustExistRule().check,
            "plugin": PluginRule().check,
        }

    def execute_rule(self, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute a single rule and return issues.

        Args:
            rule: Rule dictionary with 'type', 'name', and rule-specific fields

        Returns:
            List of ValidationIssue objects
        """
        rule_type = rule.get("type")
        rule_name = rule.get("name", "<unknown>")

        handler = self._dispatch.get(rule_type)

        if not handler:
            logger.warning(f"Unknown rule type: {rule_type}")
            return [
                ValidationIssue(
                    severity="warning",
                    message=f"Unknown rule type: {rule_type}",
                    location=rule_name,
                    details={"rule_type": rule_type}
                )
            ]

        try:
            return handler(self.root, rule)
        except Exception as e:
            logger.error(f"Rule '{rule_name}' failed: {e}", exc_info=True)
            return [
                ValidationIssue(
                    severity="error",
                    message=f"Rule execution failed: {e}",
                    location=rule_name,
                    details={"error": str(e), "rule": rule}
                )
            ]

    def execute_all(self, rules: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Execute all rules and aggregate results.

        Args:
            rules: List of rule dictionaries

        Returns:
            List of all ValidationIssue objects from all rules
        """
        all_issues: List[ValidationIssue] = []

        for rule in rules:
            issues = self.execute_rule(rule)
            all_issues.extend(issues)

        return all_issues
