"""Sequence validator for image sequences."""

from pathlib import Path
from typing import List, Optional

from vfxvox_pipeline_utils.core.validators import BaseValidator, ValidationResult, ValidationIssue
from vfxvox_pipeline_utils.core.config import Config
from vfxvox_pipeline_utils.core.logging import get_logger
from .scanner import SequenceScanner, FrameInfo

logger = get_logger(__name__)


class SequenceValidator(BaseValidator):
    """Validates image sequences for common issues.

    Checks for:
    - Missing frames in the sequence
    - Corrupted or unreadable frames
    - Inconsistent resolution across frames
    - Inconsistent bit depth across frames

    Example:
        >>> validator = SequenceValidator()
        >>> result = validator.validate("shot_010.%04d.exr")
        >>> if result.has_errors():
        ...     print(f"Found {result.error_count()} errors")
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize validator with configuration.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()

    def validate(self, pattern: str) -> ValidationResult:
        """Validate a sequence and return results.

        Args:
            pattern: File pattern for the sequence (e.g., "shot.%04d.exr")

        Returns:
            ValidationResult with issues found
        """
        logger.info(f"Validating sequence: {pattern}")

        # Create result
        result = ValidationResult(
            passed=True,
            metadata={
                "validator": "SequenceValidator",
                "pattern": pattern,
            }
        )

        try:
            # Create scanner
            scanner = SequenceScanner(pattern)

            # Scan all frames
            frames = scanner.scan_all()

            if not frames:
                result.add_issue(
                    severity="warning",
                    message="No frames found matching pattern",
                    location=pattern
                )
                return result

            # Update metadata
            frame_range = scanner.get_frame_range()
            result.metadata.update({
                "frame_count": len(frames),
                "frame_range": f"{frame_range[0]}-{frame_range[1]}" if frame_range else None,
            })

            # Run checks
            self.check_missing_frames(frames, result)
            self.check_corrupted_frames(frames, result)

            if self.config.get("sequences.check_resolution", True):
                self.check_resolution_consistency(frames, result)

            if self.config.get("sequences.check_bit_depth", True):
                self.check_bit_depth_consistency(frames, result)

            logger.info(
                f"Validation complete: {result.error_count()} errors, "
                f"{result.warning_count()} warnings"
            )

        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            result.add_issue(
                severity="error",
                message=f"Validation failed: {e}",
                location=pattern
            )

        return result

    def check_missing_frames(self, frames: List[FrameInfo], result: ValidationResult) -> None:
        """Check for missing frames in the sequence.

        Args:
            frames: List of FrameInfo objects
            result: ValidationResult to add issues to
        """
        if not frames:
            return

        # Get frame range
        frame_numbers = [f.frame_number for f in frames]
        first_frame = min(frame_numbers)
        last_frame = max(frame_numbers)

        # Check for gaps
        expected_frames = set(range(first_frame, last_frame + 1))
        present_frames = set(frame_numbers)
        missing_frames = sorted(expected_frames - present_frames)

        if missing_frames:
            # Format message
            if len(missing_frames) > 10:
                sample = missing_frames[:10]
                message = f"{len(missing_frames)} frames missing. Sample: {sample}"
            else:
                message = f"Missing frames: {missing_frames}"

            result.add_issue(
                severity="error",
                message=message,
                location=f"frames {first_frame}-{last_frame}",
                details={
                    "missing_count": len(missing_frames),
                    "missing_frames": missing_frames,
                    "expected_range": f"{first_frame}-{last_frame}",
                    "found_count": len(present_frames)
                }
            )

            logger.warning(f"Missing {len(missing_frames)} frames")

    def check_corrupted_frames(self, frames: List[FrameInfo], result: ValidationResult) -> None:
        """Check for corrupted or unreadable frames.

        Args:
            frames: List of FrameInfo objects
            result: ValidationResult to add issues to
        """
        corrupted = []

        for frame in frames:
            if frame.exists and not frame.readable:
                corrupted.append(frame.frame_number)

        if corrupted:
            if len(corrupted) > 10:
                sample = corrupted[:10]
                message = f"{len(corrupted)} frames corrupted or unreadable. Sample: {sample}"
            else:
                message = f"Corrupted or unreadable frames: {corrupted}"

            result.add_issue(
                severity="error",
                message=message,
                location="sequence",
                details={
                    "corrupted_count": len(corrupted),
                    "corrupted_frames": corrupted
                }
            )

            logger.error(f"Found {len(corrupted)} corrupted frames")

    def check_resolution_consistency(self, frames: List[FrameInfo], result: ValidationResult) -> None:
        """Check that all frames have consistent resolution.

        Args:
            frames: List of FrameInfo objects
            result: ValidationResult to add issues to
        """
        # Get frames with resolution info
        frames_with_res = [f for f in frames if f.resolution is not None]

        if not frames_with_res:
            logger.debug("No resolution information available")
            return

        # Use first frame as reference
        reference_res = frames_with_res[0].resolution
        mismatches = []

        for frame in frames_with_res[1:]:
            if frame.resolution != reference_res:
                mismatches.append({
                    "frame": frame.frame_number,
                    "expected": reference_res,
                    "actual": frame.resolution
                })

        if mismatches:
            if len(mismatches) > 5:
                sample = mismatches[:5]
                message = f"Resolution mismatch in {len(mismatches)} frames. Sample: {sample}"
            else:
                message = f"Resolution mismatch detected: {mismatches}"

            result.add_issue(
                severity="error",
                message=message,
                location="sequence",
                details={
                    "reference_resolution": reference_res,
                    "mismatch_count": len(mismatches),
                    "mismatches": mismatches
                }
            )

            logger.error(f"Resolution mismatch in {len(mismatches)} frames")

    def check_bit_depth_consistency(self, frames: List[FrameInfo], result: ValidationResult) -> None:
        """Check that all frames have consistent bit depth.

        Args:
            frames: List of FrameInfo objects
            result: ValidationResult to add issues to
        """
        # Get frames with bit depth info
        frames_with_depth = [f for f in frames if f.bit_depth is not None]

        if not frames_with_depth:
            logger.debug("No bit depth information available")
            return

        # Use first frame as reference
        reference_depth = frames_with_depth[0].bit_depth
        mismatches = []

        for frame in frames_with_depth[1:]:
            if frame.bit_depth != reference_depth:
                mismatches.append({
                    "frame": frame.frame_number,
                    "expected": reference_depth,
                    "actual": frame.bit_depth
                })

        if mismatches:
            if len(mismatches) > 5:
                sample = mismatches[:5]
                message = f"Bit depth mismatch in {len(mismatches)} frames. Sample: {sample}"
            else:
                message = f"Bit depth mismatch detected: {mismatches}"

            result.add_issue(
                severity="error",
                message=message,
                location="sequence",
                details={
                    "reference_bit_depth": reference_depth,
                    "mismatch_count": len(mismatches),
                    "mismatches": mismatches
                }
            )

            logger.error(f"Bit depth mismatch in {len(mismatches)} frames")
