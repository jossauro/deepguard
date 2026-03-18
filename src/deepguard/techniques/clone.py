"""Copy-Move Clone Detection forensic technique.

Detects duplicated regions within an image using DCT-based block matching,
identifying copy-paste forgeries and cloning artifacts.
"""

from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image

from deepguard.models import TechniqueResult
from deepguard.utils import apply_colormap


class CopyMoveDetection:
    """Detect copy-move forgeries using DCT block matching."""

    def __init__(self, block_size: int = 16, threshold: float = 0.95):
        """Initialize copy-move detector.

        Args:
            block_size: Size of blocks for DCT analysis
            threshold: Similarity threshold for matching blocks
        """
        self.block_size = block_size
        self.threshold = threshold

    def analyze(self, image: Image.Image) -> Tuple[TechniqueResult, np.ndarray]:
        """Detect copy-move forgeries.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (TechniqueResult, clone heatmap as numpy array)
        """
        # Convert to grayscale
        if image.mode != "L":
            img_gray = image.convert("L")
        else:
            img_gray = image

        img_array = np.array(img_gray, dtype=np.float32)
        h, w = img_array.shape

        # Extract DCT features for each block
        blocks = []
        positions = []

        for y in range(0, h - self.block_size, self.block_size):
            for x in range(0, w - self.block_size, self.block_size):
                block = img_array[y : y + self.block_size, x : x + self.block_size]
                dct = cv2.dct(block)
                feature = dct.flatten()
                blocks.append(feature)
                positions.append((x, y))

        blocks = np.array(blocks)

        # Find similar blocks
        clone_pairs = []
        clone_map = np.zeros_like(img_array)

        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                # Compute similarity using cosine distance
                similarity = self._cosine_similarity(blocks[i], blocks[j])

                if similarity > self.threshold:
                    clone_pairs.append((i, j, similarity))
                    # Mark both blocks on clone map
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    clone_map[
                        y1 : y1 + self.block_size, x1 : x1 + self.block_size
                    ] = 255
                    clone_map[
                        y2 : y2 + self.block_size, x2 : x2 + self.block_size
                    ] = 255

        # Determine verdict
        num_clones = len(clone_pairs)
        confidence = min(100.0, (num_clones / 10.0) * 100) if num_clones > 0 else 0.0

        verdict = "MANIPULATED" if confidence > 50 else (
            "SUSPICIOUS" if confidence > 20 else "AUTHENTIC"
        )

        clone_heatmap = apply_colormap(clone_map / 255.0, "jet")

        result = TechniqueResult(
            name="Copy-Move Detection",
            confidence=confidence,
            verdict=verdict,
            description=(
                "Uses DCT-based block matching to identify duplicated regions "
                "within images, detecting copy-paste forgeries."
            ),
            details={
                "num_clone_pairs": num_clones,
                "block_size": self.block_size,
                "similarity_threshold": self.threshold,
            },
        )

        return result, clone_heatmap

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score 0-1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)
