"""Rule type implementations for ShotLint."""

import re
import glob as glob_module
from pathlib import Path
from typing import List, Dict, Any

from vfxvox_pipeline_utils.core.validators import ValidationIssue
from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


class PathPatternRule:
    """Validates folder structure against patterns.

    Checks if directory paths match expected hierarchy patterns with
    variable substitution.

    Example rule:
        ```yaml
        - name: "Shot structure"
          type: "path_pattern"
          pattern: "seq_{sequence}/shot_{shot}/comp/v{version}"
          vars:
            sequence: "\\d{3}"
            shot: "\\d{3}"
            version: "v\\d{3}"
        ```
    """

    def check(self, root: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if directories match the pattern.

        Args:
            root: Root directory to check
            rule: Rule dictionary with 'pattern' and 'vars' keys

        Returns:
            List of ValidationIssue objects
        """
        pattern = rule.get("pattern")
        vars_dict = rule.get("vars", {})
        rule_name = rule.get("name", "path_pattern")

        if not pattern:
            return [
                ValidationIssue(
                    severity="error",
                    message="path_pattern rule missing 'pattern' field",
                    location=rule_name
                )
            ]

        # Convert pattern to regex
        regex_pattern = self._render_pattern(pattern, vars_dict)

        # Walk directory tree looking for matches
        found_match = False
        for dirpath in root.rglob("*"):
            if not dirpath.is_dir():
                continue

            rel_path = dirpath.relative_to(root).as_posix()
            if regex_pattern.match(rel_path):
                found_match = True
                logger.debug(f"Pattern matched: {rel_path}")
                break

        if not found_match:
            return [
                ValidationIssue(
                    severity="warning",
                    message=f"No path matched pattern '{pattern}'",
                    location=str(root),
                    details={"pattern": pattern, "vars": vars_dict}
                )
            ]

        return []

    def _render_pattern(self, pattern: str, vars_dict: Dict[str, str]) -> re.Pattern:
        """Convert a template pattern into a regex.

        Args:
            pattern: Pattern like "seq_{sequence}/shot_{shot}"
            vars_dict: Variable definitions like {"sequence": "\\d{3}"}

        Returns:
            Compiled regex pattern
        """
        # Escape the pattern for regex
        rx = re.escape(pattern)

        # Replace variables with their regex patterns
        for key, val in vars_dict.items():
            placeholder = re.escape("{" + key + "}")
            rx = rx.replace(placeholder, f"(?P<{key}>{val})")

        return re.compile("^" + rx + "$")


class FilenameRegexRule:
    """Validates filenames match regex patterns.

    Checks if any filenames in the directory tree match the specified regex.

    Example rule:
        ```yaml
        - name: "EXR naming"
          type: "filename_regex"
          regex: "^shot_\\d{3}_v\\d{3}_comp\\.exr$"
        ```
    """

    def check(self, root: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if filenames match the regex.

        Args:
            root: Root directory to check
            rule: Rule dictionary with 'regex' key

        Returns:
            List of ValidationIssue objects
        """
        regex_str = rule.get("regex")
        rule_name = rule.get("name", "filename_regex")

        if not regex_str:
            return [
                ValidationIssue(
                    severity="error",
                    message="filename_regex rule missing 'regex' field",
                    location=rule_name
                )
            ]

        try:
            regex = re.compile(regex_str)
        except re.error as e:
            return [
                ValidationIssue(
                    severity="error",
                    message=f"Invalid regex pattern: {e}",
                    location=rule_name,
                    details={"regex": regex_str}
                )
            ]

        # Search for matching filenames
        match_count = 0
        for filepath in root.rglob("*"):
            if filepath.is_file() and regex.match(filepath.name):
                match_count += 1
                logger.debug(f"Filename matched: {filepath.name}")

        if match_count == 0:
            return [
                ValidationIssue(
                    severity="warning",
                    message="No filenames matched the regex",
                    location=str(root),
                    details={"regex": regex_str}
                )
            ]

        return []


class FrameSequenceRule:
    """Checks for missing frames in sequences.

    Validates that all expected frames exist in an image sequence.

    Example rule:
        ```yaml
        - name: "Comp frames"
          type: "frame_sequence"
          folder: "seq_010/shot_020/comp/v001"
          base: "shot_020_v001_comp"
          ext: ".exr"
          start: 1001
          end: 1100
          padding: 4
        ```
    """

    def check(self, root: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Check for missing frames in a sequence.

        Args:
            root: Root directory
            rule: Rule dictionary with folder, base, ext, start, end, padding

        Returns:
            List of ValidationIssue objects
        """
        rule_name = rule.get("name", "frame_sequence")
        folder_rel = rule.get("folder")
        base = rule.get("base")
        ext = rule.get("ext", ".exr")
        start = rule.get("start")
        end = rule.get("end")
        padding = rule.get("padding", 4)

        # Validate required fields
        if not all([folder_rel, base, start is not None, end is not None]):
            return [
                ValidationIssue(
                    severity="error",
                    message="frame_sequence rule missing required fields (folder, base, start, end)",
                    location=rule_name
                )
            ]

        folder = root / folder_rel

        # Check if folder exists
        if not folder.exists():
            return [
                ValidationIssue(
                    severity="error",
                    message=f"Folder missing: {folder_rel}",
                    location=str(folder),
                    details={"expected_folder": folder_rel}
                )
            ]

        if not folder.is_dir():
            return [
                ValidationIssue(
                    severity="error",
                    message=f"Path is not a directory: {folder_rel}",
                    location=str(folder)
                )
            ]

        # Find present frames
        present_frames = set()
        for filepath in folder.iterdir():
            if not filepath.is_file():
                continue

            filename = filepath.name
            if filename.startswith(base) and filename.endswith(ext):
                # Extract frame number
                # Format: base.####.ext
                frame_part = filename[len(base) + 1: -len(ext)]
                if frame_part.isdigit():
                    present_frames.add(int(frame_part))

        # Check for missing frames
        expected_frames = set(range(start, end + 1))
        missing_frames = sorted(expected_frames - present_frames)

        if missing_frames:
            if len(missing_frames) > 10:
                sample = missing_frames[:10]
                message = f"{len(missing_frames)} frames missing. Sample: {sample}"
            else:
                message = f"Missing frames: {missing_frames}"

            return [
                ValidationIssue(
                    severity="error",
                    message=message,
                    location=str(folder),
                    details={
                        "missing_count": len(missing_frames),
                        "missing_frames": missing_frames,
                        "expected_range": f"{start}-{end}",
                        "found_count": len(present_frames)
                    }
                )
            ]

        logger.debug(f"All {len(expected_frames)} frames present in {folder_rel}")
        return []


class MustExistRule:
    """Verifies required files/folders exist.

    Uses glob patterns to check for file or directory presence.

    Example rule:
        ```yaml
        - name: "Plate files"
          type: "must_exist"
          glob: "seq_*/shot_*/plate/*_plate.*"
        ```
    """

    def check(self, root: Path, rule: Dict[str, Any]) -> List[ValidationIssue]:
        """Check if files matching glob pattern exist.

        Args:
            root: Root directory
            rule: Rule dictionary with 'glob' key

        Returns:
            List of ValidationIssue objects
        """
        glob_pattern = rule.get("glob")
        rule_name = rule.get("name", "must_exist")

        if not glob_pattern:
            return [
                ValidationIssue(
                    severity="error",
                    message="must_exist rule missing 'glob' field",
                    location=rule_name
                )
            ]

        # Use glob to find matches
        pattern_path = str(root / glob_pattern)
        matches = glob_module.glob(pattern_path, recursive=True)

        if not matches:
            return [
                ValidationIssue(
                    severity="error",
                    message=f"No matches for glob: {glob_pattern}",
                    location=str(root),
                    details={"glob": glob_pattern}
                )
            ]

        logger.debug(f"Found {len(matches)} matches for glob: {glob_pattern}")
        return []
