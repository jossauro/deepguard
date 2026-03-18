"""Error Level Analysis (ELA) forensic technique.

ELA detects compression inconsistencies from image editing by analyzing
how much the image changes when re-saved at a known JPEG quality.
"""

from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from deepguard.models import TechniqueResult
from deepguard.utils import apply_colormap, normalize_array


class ErrorLevelAnalysis:
    """Error Level Analysis for compression inconsistency detection."""

    def __init__(self, quality: int = 90):
        """Initialize ELA.

        Args:
            quality: JPEG quality for re-encoding (default 90)
        """
        self.quality = quality

    def analyze(self, image: Image.Image) -> Tuple[TechniqueResult, np.ndarray]:
        """Perform Error Level Analysis.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (TechniqueResult, ELA heatmap as numpy array)
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert to numpy array
        original = np.array(image, dtype=np.float32)

        # Resave at known quality
        import io

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=self.quality)
        buffer.seek(0)
        recompressed = np.array(Image.open(buffer).convert("RGB"), dtype=np.float32)

        # Compute difference
        diff = np.abs(original - recompressed)
        ela_map = np.max(diff, axis=2)

        # Calculate statistics
        mean_error = np.mean(ela_map)
        std_error = np.std(ela_map)
        max_error = np.max(ela_map)
        percentile_95 = np.percentile(ela_map, 95)

        # Determine if manipulation is likely
        # Higher mean error and variance suggest editing
        manipulation_score = min(100.0, (mean_error / 20.0) * 100)

        verdict = "MANIPULATED" if manipulation_score > 60 else (
            "SUSPICIOUS" if manipulation_score > 40 else "AUTHENTIC"
        )

        heatmap = apply_colormap(ela_map, "jet")

        result = TechniqueResult(
            name="Error Level Analysis",
            confidence=min(100.0, abs(manipulation_score)),
            verdict=verdict,
            description=(
                "Detects compression inconsistencies from editing by comparing "
                "re-saved JPEG blocks with originals."
            ),
            heatmap_data=None,
            details={
                "mean_error": float(mean_error),
                "std_error": float(std_error),
                "max_error": float(max_error),
                "percentile_95": float(percentile_95),
                "manipulation_score": float(manipulation_score),
            },
        )

        return result, heatmap

    def _compute_manipulation_probability(self, ela_map: np.ndarray) -> float:
        """Compute probability of manipulation from ELA map.

        Args:
            ela_map: Error level map

        Returns:
            Probability score 0-100
        """
        mean_error = np.mean(ela_map)
        std_error = np.std(ela_map)

        # High mean and variance indicate likely editing
        score = (mean_error + std_error) / 2.0

        return min(100.0, score * 2.0)
