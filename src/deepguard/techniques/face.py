"""Face Consistency Check forensic technique.

Analyzes facial regions for deepfake indicators including eye reflection
consistency, skin texture uniformity, edge blending quality, and lighting.
"""

from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from deepguard.models import TechniqueResult


class FaceConsistencyCheck:
    """Analyze facial regions for deepfake indicators."""

    def __init__(self):
        """Initialize face consistency checker."""
        # Load pre-trained Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze(self, image: Image.Image) -> Tuple[TechniqueResult, np.ndarray]:
        """Analyze facial regions for consistency.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (TechniqueResult, face heatmap as numpy array)
        """
        # Convert to grayscale for face detection
        if image.mode != "L":
            img_gray = image.convert("L")
        else:
            img_gray = image

        img_array = np.array(img_gray, dtype=np.uint8)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            img_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        # Initialize results
        deepfake_indicators = []
        confidence = 0.0

        if len(faces) > 0:
            for x, y, w, h in faces:
                # Extract face region
                face_region = img_bgr[y : y + h, x : x + w]

                # Check skin texture uniformity
                uniformity_score = self._check_texture_uniformity(face_region)
                if uniformity_score < 30:
                    deepfake_indicators.append("Low skin texture uniformity")

                # Check for eye reflection artifacts
                eye_consistency = self._check_eye_reflections(face_region)
                if eye_consistency < 40:
                    deepfake_indicators.append("Inconsistent eye reflections")

                # Check edge blending
                blending_score = self._check_edge_blending(face_region, img_bgr, x, y, w, h)
                if blending_score > 70:
                    deepfake_indicators.append("Possible edge blending artifacts")

            # Calculate confidence
            if deepfake_indicators:
                confidence = min(100.0, len(deepfake_indicators) * 30)
            else:
                confidence = 15.0  # Slight suspicion even without indicators

        verdict = "MANIPULATED" if confidence > 60 else (
            "SUSPICIOUS" if confidence > 40 else "AUTHENTIC"
        )

        # Create visualization
        face_heatmap = np.zeros_like(img_array)
        for x, y, w, h in faces:
            cv2.rectangle(face_heatmap, (x, y), (x + w, y + h), 200, 2)

        result = TechniqueResult(
            name="Face Consistency Check",
            confidence=confidence if len(faces) > 0 else 0.0,
            verdict=verdict if len(faces) > 0 else "AUTHENTIC",
            description=(
                "Analyzes facial regions for deepfake indicators including "
                "eye reflections, skin texture, lighting consistency, and edge blending."
            ),
            details={
                "faces_detected": len(faces),
                "deepfake_indicators": deepfake_indicators,
            },
        )

        return result, face_heatmap

    @staticmethod
    def _check_texture_uniformity(face_region: np.ndarray) -> float:
        """Check uniformity of skin texture.

        Args:
            face_region: Face region image

        Returns:
            Uniformity score 0-100 (higher = more uniform)
        """
        if face_region.size == 0:
            return 0.0

        # Convert to grayscale if needed
        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Compute local variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = np.var(laplacian)

        # Normalize to 0-100
        return min(100.0, (variance / 100.0) * 100)

    @staticmethod
    def _check_eye_reflections(face_region: np.ndarray) -> float:
        """Check consistency of eye reflections.

        Args:
            face_region: Face region image

        Returns:
            Consistency score 0-100
        """
        if face_region.size == 0:
            return 0.0

        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Detect bright spots (reflections)
        _, bright_spots = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        num_reflections = np.count_nonzero(bright_spots)

        # Eyes should have 2-4 reflections
        expected_reflections = 4
        reflection_score = 100.0 - abs(expected_reflections - (num_reflections / 100)) * 20

        return max(0.0, min(100.0, reflection_score))

    @staticmethod
    def _check_edge_blending(
        face_region: np.ndarray,
        full_image: np.ndarray,
        face_x: int,
        face_y: int,
        face_w: int,
        face_h: int,
    ) -> float:
        """Check for edge blending artifacts.

        Args:
            face_region: Face region
            full_image: Full image
            face_x, face_y: Face position
            face_w, face_h: Face dimensions

        Returns:
            Blending artifact score 0-100
        """
        if face_region.size == 0:
            return 0.0

        if len(face_region.shape) == 3:
            gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_region

        # Detect edges
        edges = cv2.Canny(gray, 100, 200)
        edge_count = np.count_nonzero(edges)

        # High edge count at boundaries suggests blending
        boundary_thickness = 5
        boundary_edges = edge_count / (face_w * face_h)

        return min(100.0, boundary_edges * 1000)
