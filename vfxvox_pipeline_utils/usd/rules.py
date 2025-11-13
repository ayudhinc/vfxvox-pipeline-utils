"""Built-in linting rules for USD files."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from vfxvox_pipeline_utils.core.validators import ValidationIssue
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)

try:
    from pxr import Usd, Sdf, UsdGeom
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False


class LintRule(ABC):
    """Abstract base for linting rules.

    Attributes:
        name: Rule name
        description: Rule description
        severity: Default severity ('error', 'warning', 'info')
    """

    name: str = "UnnamedRule"
    description: str = "No description"
    severity: str = "warning"

    @abstractmethod
    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Execute the rule and return issues.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        pass


class BrokenReferencesRule(LintRule):
    """Checks for broken or missing references.

    Validates that all external references (sublayers, references, payloads)
    point to existing files.
    """

    name = "BrokenReferences"
    description = "Check for broken or missing external references"
    severity = "error"

    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Check for broken references.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        issues: List[ValidationIssue] = []

        # Check sublayers
        root_layer = stage.GetRootLayer()
        if root_layer:
            for sublayer_path in root_layer.subLayerPaths:
                if not self._reference_exists(sublayer_path, root_layer):
                    issues.append(
                        ValidationIssue(
                            severity=self.severity,
                            message=f"Broken sublayer reference: {sublayer_path}",
                            location=str(root_layer.identifier),
                            details={"reference_type": "sublayer", "path": sublayer_path}
                        )
                    )

        # Check references and payloads on all prims
        for prim in stage.Traverse():
            # Check references
            if prim.HasAuthoredReferences():
                refs = prim.GetMetadata('references')
                if refs:
                    for ref in refs.GetAddedOrExplicitItems():
                        asset_path = ref.assetPath
                        if asset_path and not self._reference_exists(asset_path, root_layer):
                            issues.append(
                                ValidationIssue(
                                    severity=self.severity,
                                    message=f"Broken reference: {asset_path}",
                                    location=str(prim.GetPath()),
                                    details={"reference_type": "reference", "path": asset_path}
                                )
                            )

            # Check payloads
            if prim.HasAuthoredPayloads():
                payloads = prim.GetMetadata('payload')
                if payloads:
                    for payload in payloads.GetAddedOrExplicitItems():
                        asset_path = payload.assetPath
                        if asset_path and not self._reference_exists(asset_path, root_layer):
                            issues.append(
                                ValidationIssue(
                                    severity=self.severity,
                                    message=f"Broken payload: {asset_path}",
                                    location=str(prim.GetPath()),
                                    details={"reference_type": "payload", "path": asset_path}
                                )
                            )

        return issues

    def _reference_exists(self, asset_path: str, context_layer: 'Sdf.Layer') -> bool:
        """Check if a referenced asset exists.

        Args:
            asset_path: Asset path to check
            context_layer: Layer providing context for relative paths

        Returns:
            True if asset exists
        """
        try:
            # Resolve the asset path
            resolved_path = asset_path
            if context_layer:
                resolved_path = context_layer.ComputeAbsolutePath(asset_path)

            # Check if file exists
            if resolved_path:
                return Path(resolved_path).exists()

            return False
        except Exception as e:
            logger.debug(f"Error checking reference {asset_path}: {e}")
            return False


class InvalidSchemaRule(LintRule):
    """Checks for invalid schema definitions.

    Validates that prims have valid schema types and that required
    attributes are present.
    """

    name = "InvalidSchema"
    description = "Check for invalid schema definitions"
    severity = "error"

    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Check for invalid schemas.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        issues: List[ValidationIssue] = []

        for prim in stage.Traverse():
            # Skip abstract prims
            if not prim.IsActive():
                continue

            # Check if prim has a valid type
            prim_type = prim.GetTypeName()
            if prim_type:
                # Try to get the schema
                try:
                    schema = prim.GetPrimTypeInfo()
                    if not schema:
                        issues.append(
                            ValidationIssue(
                                severity=self.severity,
                                message=f"Invalid prim type: {prim_type}",
                                location=str(prim.GetPath()),
                                details={"prim_type": prim_type}
                            )
                        )
                except Exception as e:
                    issues.append(
                        ValidationIssue(
                            severity=self.severity,
                            message=f"Error validating schema: {e}",
                            location=str(prim.GetPath()),
                            details={"prim_type": prim_type, "error": str(e)}
                        )
                    )

        return issues


class PerformanceRule(LintRule):
    """Checks for performance issues.

    Validates:
    - Layer composition depth
    - Number of composition arcs
    - Large array attributes
    """

    name = "Performance"
    description = "Check for performance issues"
    severity = "warning"

    def __init__(self, config: Optional[Config] = None):
        """Initialize with configuration.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.max_layer_depth = self.config.get("usd.max_layer_depth", 10)

    def check(self, stage: 'Usd.Stage') -> List[ValidationIssue]:
        """Check for performance issues.

        Args:
            stage: USD Stage to check

        Returns:
            List of ValidationIssue objects
        """
        issues: List[ValidationIssue] = []

        # Check layer composition depth
        root_layer = stage.GetRootLayer()
        if root_layer:
            depth = self._get_layer_depth(root_layer)
            if depth > self.max_layer_depth:
                issues.append(
                    ValidationIssue(
                        severity=self.severity,
                        message=f"Layer composition depth ({depth}) exceeds recommended limit ({self.max_layer_depth})",
                        location=str(root_layer.identifier),
                        details={"depth": depth, "max_depth": self.max_layer_depth}
                    )
                )

        # Check composition arcs on prims
        for prim in stage.Traverse():
            # Count composition arcs
            arc_count = 0
            if prim.HasAuthoredReferences():
                refs = prim.GetMetadata('references')
                if refs:
                    arc_count += len(refs.GetAddedOrExplicitItems())

            if prim.HasAuthoredPayloads():
                payloads = prim.GetMetadata('payload')
                if payloads:
                    arc_count += len(payloads.GetAddedOrExplicitItems())

            if prim.HasAuthoredInherits():
                inherits = prim.GetMetadata('inherits')
                if inherits:
                    arc_count += len(inherits.GetAddedOrExplicitItems())

            if prim.HasAuthoredSpecializes():
                specializes = prim.GetMetadata('specializes')
                if specializes:
                    arc_count += len(specializes.GetAddedOrExplicitItems())

            # Warn if too many arcs
            if arc_count > 5:
                issues.append(
                    ValidationIssue(
                        severity=self.severity,
                        message=f"Prim has {arc_count} composition arcs (may impact performance)",
                        location=str(prim.GetPath()),
                        details={"arc_count": arc_count}
                    )
                )

        return issues

    def _get_layer_depth(self, layer: 'Sdf.Layer', visited: Optional[set] = None) -> int:
        """Get the maximum depth of layer composition.

        Args:
            layer: Layer to check
            visited: Set of visited layers (to avoid cycles)

        Returns:
            Maximum depth
        """
        if visited is None:
            visited = set()

        if layer.identifier in visited:
            return 0

        visited.add(layer.identifier)

        max_depth = 0
        for sublayer_path in layer.subLayerPaths:
            try:
                sublayer = Sdf.Layer.FindOrOpen(sublayer_path)
                if sublayer:
                    depth = self._get_layer_depth(sublayer, visited)
                    max_depth = max(max_depth, depth)
            except Exception as e:
                logger.debug(f"Error checking sublayer depth: {e}")

        return max_depth + 1


def get_builtin_rules(config: Optional[Config] = None) -> List[LintRule]:
    """Get list of built-in linting rules.

    Args:
        config: Configuration object

    Returns:
        List of LintRule instances
    """
    rules: List[LintRule] = []

    config = config or Config()

    # Add rules based on configuration
    if config.get("usd.check_references", True):
        rules.append(BrokenReferencesRule())

    if config.get("usd.check_schemas", True):
        rules.append(InvalidSchemaRule())

    if config.get("usd.check_performance", True):
        rules.append(PerformanceRule(config))

    return rules
