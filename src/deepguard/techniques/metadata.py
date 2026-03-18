"""Metadata Forensics technique.

Extracts and analyzes EXIF data, ICC profiles, and other metadata
to identify inconsistencies indicating manipulation.
"""

from typing import Any, Dict, Optional, Tuple

import exifread
from PIL import Image

from deepguard.models import MetadataInfo, TechniqueResult


class MetadataForensics:
    """Extract and analyze image metadata for inconsistencies."""

    EDITING_SOFTWARE = {
        "adobe",
        "photoshop",
        "gimp",
        "lightroom",
        "pixelmator",
        "affinity",
        "capture",
    }

    def analyze(self, file_path: str, image: Image.Image) -> Tuple[TechniqueResult, MetadataInfo]:
        """Extract and analyze metadata.

        Args:
            file_path: Path to image file
            image: PIL Image object

        Returns:
            Tuple of (TechniqueResult, MetadataInfo)
        """
        metadata = MetadataInfo()
        warnings = []
        editing_indicators = []

        try:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)

            # Extract camera information
            metadata.camera_make = self._get_tag(tags, "Image Make")
            metadata.camera_model = self._get_tag(tags, "Image Model")
            metadata.timestamp = self._get_tag(tags, "EXIF DateTimeOriginal")
            metadata.software = self._get_tag(tags, "Image Software")

            # Extract dimensions
            metadata.width = int(image.width)
            metadata.height = int(image.height)

            # Check for editing software
            if metadata.software:
                software_lower = metadata.software.lower()
                for soft in self.EDITING_SOFTWARE:
                    if soft in software_lower:
                        editing_indicators.append(f"Edited with {metadata.software}")

            # Check for orientation tag (common in edited images)
            orientation = self._get_tag(tags, "Image Orientation")
            if orientation:
                metadata.orientation = int(orientation)

            # Extract GPS if present
            gps_lat = self._get_tag(tags, "GPS GPSLatitude")
            gps_lon = self._get_tag(tags, "GPS GPSLongitude")
            if gps_lat and gps_lon:
                metadata.gps_coordinates = (float(gps_lat), float(gps_lon))

            # Store raw EXIF
            metadata.raw_exif = {k: str(v) for k, v in tags.items()}

        except Exception as e:
            warnings.append(f"Could not read EXIF data: {str(e)}")

        # Determine verdict based on metadata
        confidence = len(editing_indicators) * 25
        verdict = "SUSPICIOUS" if confidence > 0 else "AUTHENTIC"

        result = TechniqueResult(
            name="Metadata Forensics",
            confidence=min(100.0, confidence),
            verdict=verdict,
            description=(
                "Analyzes EXIF data, camera metadata, and software signatures "
                "for signs of editing or manipulation."
            ),
            details={
                "camera_make": metadata.camera_make,
                "camera_model": metadata.camera_model,
                "software": metadata.software,
                "editing_indicators": editing_indicators,
                "has_gps": metadata.gps_coordinates is not None,
            },
        )

        return result, metadata

    @staticmethod
    def _get_tag(tags: Dict[str, Any], tag_name: str) -> Optional[str]:
        """Safely extract EXIF tag value.

        Args:
            tags: EXIF tags dictionary
            tag_name: Name of tag to extract

        Returns:
            Tag value as string or None
        """
        try:
            if tag_name in tags:
                return str(tags[tag_name].values)
            return None
        except Exception:
            return None
