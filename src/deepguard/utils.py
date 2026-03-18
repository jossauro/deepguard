"""Utility functions for image processing and report generation."""

import base64
import io
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image


SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".pdf"}


def load_image(file_path: str) -> Tuple[Image.Image, str]:
    """Load image from file and return PIL Image object and format.

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (PIL Image, format string)

    Raises:
        ValueError: If file format not supported or file cannot be read
    """
    path = Path(file_path)

    if not path.exists():
        raise ValueError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {suffix}. Supported: {SUPPORTED_FORMATS}")

    try:
        if suffix == ".pdf":
            # For PDF, convert first page to image
            try:
                import fitz
                doc = fitz.open(file_path)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data))
                doc.close()
            except ImportError:
                raise ValueError("PDF support requires pymupdf. Install with: pip install pymupdf")
        else:
            image = Image.open(file_path)
            if image.mode == "RGBA":
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                image = rgb_image
            elif image.mode not in ["RGB", "L"]:
                image = image.convert("RGB")

        return image, suffix.lstrip(".")

    except Exception as e:
        raise ValueError(f"Failed to load image: {str(e)}")


def is_supported_format(file_path: str) -> bool:
    """Check if file format is supported."""
    return Path(file_path).suffix.lower() in SUPPORTED_FORMATS


def numpy_to_base64(arr: np.ndarray) -> str:
    """Convert numpy array to base64 PNG for HTML embedding.

    Args:
        arr: Numpy array (H x W or H x W x 3)

    Returns:
        Base64 encoded PNG string
    """
    if arr.dtype != np.uint8:
        if arr.max() <= 1.0:
            arr = (arr * 255).astype(np.uint8)
        else:
            arr = np.clip(arr, 0, 255).astype(np.uint8)

    if len(arr.shape) == 2:
        # Grayscale - convert to RGB for consistency
        arr = np.stack([arr] * 3, axis=-1)

    image = Image.fromarray(arr)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 PNG.

    Args:
        image: PIL Image object

    Returns:
        Base64 encoded PNG string
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def normalize_array(arr: np.ndarray) -> np.ndarray:
    """Normalize numpy array to 0-1 range."""
    min_val = arr.min()
    max_val = arr.max()

    if max_val == min_val:
        return np.zeros_like(arr, dtype=np.float32)

    return ((arr - min_val) / (max_val - min_val)).astype(np.float32)


def apply_colormap(arr: np.ndarray, colormap: str = "jet") -> np.ndarray:
    """Apply colormap to grayscale array.

    Args:
        arr: Grayscale array (H x W)
        colormap: Colormap name (jet, hot, cool, viridis, etc.)

    Returns:
        RGB array (H x W x 3)
    """
    import cv2

    arr_normalized = (normalize_array(arr) * 255).astype(np.uint8)

    colormap_id = getattr(cv2, f"COLORMAP_{colormap.upper()}", cv2.COLORMAP_JET)
    return cv2.applyColorMap(arr_normalized, colormap_id)
