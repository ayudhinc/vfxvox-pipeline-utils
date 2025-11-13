"""Frame detection and scanning for image sequences."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from vfxvox_pipeline_utils.core.logging import get_logger
from vfxvox_pipeline_utils.core.exceptions import InvalidFormatError

logger = get_logger(__name__)


@dataclass
class FrameInfo:
    """Information about a single frame.

    Attributes:
        frame_number: Frame number in the sequence
        file_path: Path to the frame file
        exists: Whether the file exists
        readable: Whether the file can be read
        resolution: Image resolution as (width, height)
        bit_depth: Bit depth of the image
        format: Image format (e.g., 'exr', 'dpx', 'png')
    """

    frame_number: int
    file_path: Path
    exists: bool
    readable: bool
    resolution: Optional[Tuple[int, int]] = None
    bit_depth: Optional[int] = None
    format: Optional[str] = None


class SequenceScanner:
    """Scans and analyzes image sequences.

    Supports multiple pattern formats:
    - Printf-style: shot_010.%04d.exr
    - Hash-style: shot_010.####.exr
    - Range-style: shot_010.[1001-1100].exr

    Example:
        >>> scanner = SequenceScanner("shot_010.%04d.exr")
        >>> frames = scanner.detect_frames()
        >>> print(f"Found {len(frames)} frames")
    """

    def __init__(self, pattern: str):
        """Initialize scanner with sequence pattern.

        Args:
            pattern: File pattern for the sequence

        Raises:
            InvalidFormatError: If pattern format is not recognized
        """
        self.pattern = pattern
        self.base_path = Path(pattern).parent
        self.filename_pattern = Path(pattern).name

        # Parse pattern to extract components
        self._parse_pattern()

    def _parse_pattern(self) -> None:
        """Parse the pattern to extract base name, frame format, and extension.

        Raises:
            InvalidFormatError: If pattern cannot be parsed
        """
        # Try printf-style: %04d, %d, etc.
        printf_match = re.search(r'%(\d*)d', self.filename_pattern)
        if printf_match:
            self.pattern_type = "printf"
            self.padding = int(printf_match.group(1)) if printf_match.group(1) else 0
            self.base_name = self.filename_pattern[:printf_match.start()]
            self.extension = self.filename_pattern[printf_match.end():]
            self.frame_regex = re.compile(
                re.escape(self.base_name) + r'(\d+)' + re.escape(self.extension)
            )
            logger.debug(f"Parsed printf pattern: base={self.base_name}, padding={self.padding}, ext={self.extension}")
            return

        # Try hash-style: ####, ###, etc.
        hash_match = re.search(r'(#+)', self.filename_pattern)
        if hash_match:
            self.pattern_type = "hash"
            self.padding = len(hash_match.group(1))
            self.base_name = self.filename_pattern[:hash_match.start()]
            self.extension = self.filename_pattern[hash_match.end():]
            self.frame_regex = re.compile(
                re.escape(self.base_name) + r'(\d+)' + re.escape(self.extension)
            )
            logger.debug(f"Parsed hash pattern: base={self.base_name}, padding={self.padding}, ext={self.extension}")
            return

        # Try range-style: [1001-1100]
        range_match = re.search(r'\[(\d+)-(\d+)\]', self.filename_pattern)
        if range_match:
            self.pattern_type = "range"
            self.frame_start = int(range_match.group(1))
            self.frame_end = int(range_match.group(2))
            self.padding = len(range_match.group(1))
            self.base_name = self.filename_pattern[:range_match.start()]
            self.extension = self.filename_pattern[range_match.end():]
            self.frame_regex = re.compile(
                re.escape(self.base_name) + r'(\d+)' + re.escape(self.extension)
            )
            logger.debug(
                f"Parsed range pattern: base={self.base_name}, "
                f"range={self.frame_start}-{self.frame_end}, ext={self.extension}"
            )
            return

        raise InvalidFormatError(
            f"Unrecognized pattern format: {self.filename_pattern}",
            format=self.filename_pattern,
            supported_formats=["printf (%04d)", "hash (####)", "range ([1001-1100])"]
        )

    def detect_frames(self) -> List[int]:
        """Detect all frame numbers in the sequence by scanning the directory.

        Returns:
            Sorted list of frame numbers found

        Example:
            >>> scanner = SequenceScanner("shot.%04d.exr")
            >>> frames = scanner.detect_frames()
            >>> print(frames)  # [1001, 1002, 1003, ...]
        """
        if not self.base_path.exists():
            logger.warning(f"Directory does not exist: {self.base_path}")
            return []

        frame_numbers = []

        for file_path in self.base_path.iterdir():
            if not file_path.is_file():
                continue

            match = self.frame_regex.match(file_path.name)
            if match:
                frame_number = int(match.group(1))
                frame_numbers.append(frame_number)

        frame_numbers.sort()
        logger.debug(f"Detected {len(frame_numbers)} frames")

        return frame_numbers

    def scan_frame(self, frame_number: int) -> FrameInfo:
        """Scan a single frame and gather information.

        Args:
            frame_number: Frame number to scan

        Returns:
            FrameInfo with frame details
        """
        # Construct filename
        if self.padding > 0:
            frame_str = str(frame_number).zfill(self.padding)
        else:
            frame_str = str(frame_number)

        filename = f"{self.base_name}{frame_str}{self.extension}"
        file_path = self.base_path / filename

        # Check existence
        exists = file_path.exists()
        readable = False

        if exists:
            try:
                # Try to open file to check readability
                with open(file_path, 'rb') as f:
                    f.read(1)
                readable = True
            except Exception as e:
                logger.debug(f"Frame {frame_number} not readable: {e}")

        # Get format from extension
        format_name = self.extension.lstrip('.').lower() if self.extension else None

        frame_info = FrameInfo(
            frame_number=frame_number,
            file_path=file_path,
            exists=exists,
            readable=readable,
            format=format_name
        )

        # Read metadata if file is readable
        if readable:
            self._read_frame_metadata(frame_info)

        return frame_info

    def _read_frame_metadata(self, frame_info: FrameInfo) -> None:
        """Read metadata from frame file.

        Args:
            frame_info: FrameInfo to populate with metadata
        """
        from .formats import get_format_handler

        try:
            handler = get_format_handler(frame_info.file_path)
            if handler:
                metadata = handler.read_metadata(frame_info.file_path)
                frame_info.resolution = metadata.get('resolution')
                frame_info.bit_depth = metadata.get('bit_depth')
        except Exception as e:
            logger.debug(f"Failed to read metadata for {frame_info.file_path}: {e}")

    def scan_all(self) -> List[FrameInfo]:
        """Scan all detected frames.

        Returns:
            List of FrameInfo for all frames

        Example:
            >>> scanner = SequenceScanner("shot.%04d.exr")
            >>> frames = scanner.scan_all()
            >>> for frame in frames:
            ...     print(f"Frame {frame.frame_number}: {frame.resolution}")
        """
        frame_numbers = self.detect_frames()
        frames = []

        for frame_number in frame_numbers:
            frame_info = self.scan_frame(frame_number)
            frames.append(frame_info)

        logger.info(f"Scanned {len(frames)} frames")
        return frames

    def get_frame_range(self) -> Optional[Tuple[int, int]]:
        """Get the frame range from detected frames.

        Returns:
            Tuple of (first_frame, last_frame) or None if no frames found
        """
        frames = self.detect_frames()
        if not frames:
            return None
        return (frames[0], frames[-1])
