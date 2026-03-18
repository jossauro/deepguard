"""Noise Pattern Analysis forensic technique.

Analyzes noise consistency across image regions to detect splicing
and image tampering through statistical anomalies.
"""

from typing import Tuple

import cv2
import numpy as np
from PIL import Image
from scipy import signal

from deepguard.models import TechniqueResult
from deepguard.utils import apply_colormap


class NoiseAnalysis:
    """Noise pattern analysis for tampering detection."""

    def analyze(self, image: Image.Image) -> Tuple[TechniqueResult, np.ndarray]:
        """Perform noise pattern analysis.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (TechniqueResult, noise heatmap as numpy array)
        """
        # Convert to grayscale
        if image.mode != "L":
            image = image.convert("L")

        img_array = np.array(image, dtype=np.float32)

        # Extract noise using high-pass filter
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32)
        noise_map = cv2.filter2D(img_array, -1, kernel)
        noise_map = np.abs(noise_map)

        # Divide image into blocks and analyze noise consistency
        block_size = 32
        h, w = img_array.shape
        block_variance = []
        block_mean = []

        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = noise_map[y : y + block_size, x : x + block_size]
                block_variance.append(np.var(block))
                block_mean.append(np.mean(block))

        if not block_variance:
            confidence = 0.0
            verdict = "AUTHENTIC"
        else:
            block_variance = np.array(block_variance)
            block_mean = np.array(block_mean)

            # High variance in noise patterns suggests tampering
            variance_of_variance = np.var(block_variance)
            mean_variance = np.mean(block_variance)

            # Normalize score
            if mean_variance > 0:
                noise_inconsistency = (variance_of_variance / mean_variance) * 50
            else:
                noise_inconsistency = 0.0

            confidence = min(100.0, noise_inconsistency)
            verdict = "MANIPULATED" if confidence > 65 else (
                "SUSPICIOUS" if confidence > 45 else "AUTHENTIC"
            )

        # Create visualization of noise patterns
        noise_heatmap = apply_colormap(noise_map / np.max(noise_map), "hot")

        result = TechniqueResult(
            name="Noise Pattern Analysis",
            confidence=confidence,
            verdict=verdict,
            description=(
                "Analyzes noise consistency using high-pass filtering and "
                "block-wise statistical analysis to detect splicing."
            ),
            details={
                "block_size": block_size,
                "num_blocks_analyzed": len(block_variance),
                "mean_noise_level": float(np.mean(noise_map)) if len(noise_map) > 0 else 0.0,
            },
        )

        return result, noise_heatmap
