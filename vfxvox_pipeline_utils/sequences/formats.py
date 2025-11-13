"""Image format handlers for reading metadata."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Tuple, List

from vfxvox_pipeline_utils.core.logging import get_logger

logger = get_logger(__name__)


class ImageFormatHandler(ABC):
    """Abstract base for image format handlers."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Check if this handler supports the file format.

        Args:
            file_path: Path to the image file

        Returns:
            True if this handler can read the file
        """
        pass

    @abstractmethod
    def read_metadata(self, file_path: Path) -> Dict:
        """Read metadata from the image file.

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary with metadata:
            - resolution: Tuple[int, int] (width, height)
            - bit_depth: int
            - format: str
        """
        pass


class StandardImageHandler(ImageFormatHandler):
    """Handler for standard formats (PNG, JPG, TIFF) using Pillow."""

    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp'}

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a standard image format.

        Args:
            file_path: Path to check

        Returns:
            True if file extension is supported
        """
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS

    def read_metadata(self, file_path: Path) -> Dict:
        """Read metadata using Pillow.

        Args:
            file_path: Path to image file

        Returns:
            Metadata dictionary

        Raises:
            ImportError: If Pillow is not installed
            Exception: If file cannot be read
        """
        try:
            from PIL import Image
        except ImportError:
            logger.error("Pillow not installed, cannot read standard image formats")
            raise ImportError("Pillow is required for PNG/JPG/TIFF support")

        try:
            with Image.open(file_path) as img:
                # Get resolution
                resolution = (img.width, img.height)

                # Get bit depth
                mode_to_depth = {
                    '1': 1,      # 1-bit pixels, black and white
                    'L': 8,      # 8-bit pixels, grayscale
                    'P': 8,      # 8-bit pixels, mapped to any other mode
                    'RGB': 8,    # 3x8-bit pixels, true color
                    'RGBA': 8,   # 4x8-bit pixels, true color with transparency
                    'CMYK': 8,   # 4x8-bit pixels, color separation
                    'YCbCr': 8,  # 3x8-bit pixels, color video format
                    'LAB': 8,    # 3x8-bit pixels, L*a*b color space
                    'HSV': 8,    # 3x8-bit pixels, Hue, Saturation, Value
                    'I': 32,     # 32-bit signed integer pixels
                    'F': 32,     # 32-bit floating point pixels
                    'I;16': 16,  # 16-bit unsigned integer pixels
                    'I;16B': 16, # 16-bit big endian unsigned integer
                    'I;16L': 16, # 16-bit little endian unsigned integer
                }

                bit_depth = mode_to_depth.get(img.mode, 8)

                return {
                    'resolution': resolution,
                    'bit_depth': bit_depth,
                    'format': file_path.suffix.lstrip('.').lower(),
                    'mode': img.mode,
                }

        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            raise


class EXRHandler(ImageFormatHandler):
    """Handler for OpenEXR files using OpenImageIO."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is an EXR file.

        Args:
            file_path: Path to check

        Returns:
            True if file extension is .exr
        """
        return file_path.suffix.lower() == '.exr'

    def read_metadata(self, file_path: Path) -> Dict:
        """Read metadata using OpenImageIO.

        Args:
            file_path: Path to EXR file

        Returns:
            Metadata dictionary

        Raises:
            ImportError: If OpenImageIO is not installed
            Exception: If file cannot be read
        """
        try:
            import OpenImageIO as oiio
        except ImportError:
            logger.warning("OpenImageIO not installed, using basic EXR metadata")
            return self._read_basic_metadata(file_path)

        try:
            img_input = oiio.ImageInput.open(str(file_path))
            if not img_input:
                raise Exception(f"Could not open {file_path}")

            spec = img_input.spec()

            resolution = (spec.width, spec.height)

            # Get bit depth from channel format
            format_to_depth = {
                oiio.UINT8: 8,
                oiio.INT8: 8,
                oiio.UINT16: 16,
                oiio.INT16: 16,
                oiio.UINT32: 32,
                oiio.INT32: 32,
                oiio.HALF: 16,
                oiio.FLOAT: 32,
                oiio.DOUBLE: 64,
            }

            bit_depth = format_to_depth.get(spec.format, 16)

            metadata = {
                'resolution': resolution,
                'bit_depth': bit_depth,
                'format': 'exr',
                'channels': spec.nchannels,
                'channel_names': [spec.channelnames[i] for i in range(spec.nchannels)],
            }

            img_input.close()
            return metadata

        except Exception as e:
            logger.error(f"Failed to read EXR {file_path}: {e}")
            raise

    def _read_basic_metadata(self, file_path: Path) -> Dict:
        """Read basic metadata without OpenImageIO.

        Args:
            file_path: Path to EXR file

        Returns:
            Basic metadata dictionary
        """
        # Return minimal metadata when OpenImageIO is not available
        return {
            'resolution': None,
            'bit_depth': 16,  # Assume half-float
            'format': 'exr',
        }


class DPXHandler(ImageFormatHandler):
    """Handler for DPX files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a DPX file.

        Args:
            file_path: Path to check

        Returns:
            True if file extension is .dpx
        """
        return file_path.suffix.lower() == '.dpx'

    def read_metadata(self, file_path: Path) -> Dict:
        """Read metadata from DPX file.

        Args:
            file_path: Path to DPX file

        Returns:
            Metadata dictionary

        Raises:
            ImportError: If OpenImageIO is not installed
        """
        try:
            import OpenImageIO as oiio
        except ImportError:
            logger.warning("OpenImageIO not installed, cannot read DPX metadata")
            return {
                'resolution': None,
                'bit_depth': 10,  # Common default
                'format': 'dpx',
            }

        try:
            img_input = oiio.ImageInput.open(str(file_path))
            if not img_input:
                raise Exception(f"Could not open {file_path}")

            spec = img_input.spec()
            resolution = (spec.width, spec.height)

            # DPX typically uses 10-bit or 16-bit
            format_to_depth = {
                oiio.UINT8: 8,
                oiio.UINT16: 16,
                oiio.UINT32: 32,
            }
            bit_depth = format_to_depth.get(spec.format, 10)

            metadata = {
                'resolution': resolution,
                'bit_depth': bit_depth,
                'format': 'dpx',
                'channels': spec.nchannels,
            }

            img_input.close()
            return metadata

        except Exception as e:
            logger.error(f"Failed to read DPX {file_path}: {e}")
            raise


# Registry of format handlers
_HANDLERS: List[ImageFormatHandler] = [
    EXRHandler(),
    DPXHandler(),
    StandardImageHandler(),
]


def get_format_handler(file_path: Path) -> Optional[ImageFormatHandler]:
    """Get appropriate format handler for a file.

    Args:
        file_path: Path to image file

    Returns:
        ImageFormatHandler instance or None if no handler found
    """
    for handler in _HANDLERS:
        if handler.can_handle(file_path):
            return handler

    logger.warning(f"No handler found for {file_path.suffix}")
    return None


def register_format_handler(handler: ImageFormatHandler) -> None:
    """Register a custom format handler.

    Args:
        handler: ImageFormatHandler instance to register
    """
    _HANDLERS.insert(0, handler)  # Insert at beginning for priority
    logger.debug(f"Registered format handler: {handler.__class__.__name__}")
