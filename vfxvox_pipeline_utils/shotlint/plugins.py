"""Plugin system for custom ShotLint validators."""

import importlib
from pathlib import Path
from typing import List, Dict, Any, Callable

from vfxvox_pipeline_utils.core.validators import ValidationIssue
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


class PluginLoader:
    """Loads and executes custom validation plugins.

    Plugins can be specified as:
    - "module.path:function" - Load specific function from module
    - "module.path" - Load 'validate' function from module
    """

    @staticmethod
    def load_plugin(module_spec: str) -> Callable:
        """Load a plugin from module specification.

        Args:
            module_spec: Module specification like "my_module:my_func" or "my_module"

        Returns:
            Callable plugin function

        Raises:
            ImportError: If module cannot be imported
            AttributeError: If function not found in module
        """
        if ":" in module_spec:
            # Format: module:function
            module_name, func_name = module_spec.split(":", 1)
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
        else:
            # Format: module (expects 'validate' function)
            module = importlib.import_module(module_spec)
            func = getattr(module, "validate")

        if not callable(func):
            raise TypeError(f"Plugin {module_spec} is not callable")

        logger.debug(f"Loaded plugin: {module_spec}")
        return func

    @staticmethod
    def execute_plugin(
        plugin: Callable,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute plugin with context and return results.

        Args:
            plugin: Plugin function to execute
            context: Context dictionary with 'root' and 'options'

        Returns:
            List of issue dictionaries from plugin

        The plugin should return a list of dictionaries with keys:
        - rule (optional): Rule name
        - level: 'error', 'warning', or 'info'
        - message: Issue description
        - path (optional): Path where issue was found
        """
        try:
            results = plugin(context)
            return results or []
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}", exc_info=True)
            return [
                {
                    "level": "error",
                    "message": f"Plugin crashed: {e}",
                    "path": str(context.get("root", "")),
                }
            ]


class PluginRule:
    """Executes custom plugin validators.

    Example rule:
        ```yaml
        - name: "Custom check"
          type: "plugin"
          module: "my_studio.validators:check_metadata"
          options:
            required_fields: ["artist", "date"]
        ```

    Plugin function signature:
        ```python
        def validate(context: dict) -> List[dict]:
            '''
            Args:
                context: Dict with 'root' (Path) and 'options' (dict)

            Returns:
                List of issue dicts with keys:
                - level: 'error', 'warning', or 'info'
                - message: Issue description
                - rule (optional): Rule name
                - path (optional): Path where issue found
            '''
            root = context["root"]
            options = context["options"]

            issues = []
            # ... validation logic ...
            return issues
        ```
    """

    def check(self, root: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute plugin and return issues.

        Args:
            root: Root directory
            rule: Rule dictionary with 'module' and optional 'options'

        Returns:
            List of ValidationIssue objects
        """
        module_spec = rule.get("module")
        options = rule.get("options", {})
        rule_name = rule.get("name", "plugin")

        if not module_spec:
            return [
                ValidationIssue(
                    severity="error",
                    message="plugin rule missing 'module' field",
                    location=rule_name
                )
            ]

        # Load plugin
        try:
            plugin = PluginLoader.load_plugin(module_spec)
        except (ImportError, AttributeError, TypeError) as e:
            logger.error(f"Failed to load plugin '{module_spec}': {e}")
            return [
                ValidationIssue(
                    severity="error",
                    message=f"Failed to load plugin: {e}",
                    location=rule_name,
                    details={"module": module_spec, "error": str(e)}
                )
            ]

        # Execute plugin
        context = {
            "root": root,
            "options": options,
        }

        plugin_results = PluginLoader.execute_plugin(plugin, context)

        # Convert plugin results to ValidationIssue objects
        issues: List[ValidationIssue] = []

        for result in plugin_results:
            # Map 'level' to 'severity'
            severity = result.get("level", "error")
            if severity not in {"error", "warning", "info"}:
                logger.warning(f"Invalid severity '{severity}' from plugin, using 'error'")
                severity = "error"

            message = result.get("message", "Plugin reported an issue")
            location = result.get("path")
            details = {k: v for k, v in result.items() if k not in {"level", "message", "path", "rule"}}

            # Use plugin's rule name if provided, otherwise use our rule name
            if "rule" in result:
                details["plugin_rule"] = result["rule"]

            issues.append(
                ValidationIssue(
                    severity=severity,
                    message=message,
                    location=location,
                    details=details if details else None
                )
            )

        logger.debug(f"Plugin '{module_spec}' returned {len(issues)} issues")
        return issues
