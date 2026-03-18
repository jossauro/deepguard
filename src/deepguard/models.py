"""Data models for forensic analysis results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class Verdict(str, Enum):
    """Analysis verdict classification."""

    AUTHENTIC = "AUTHENTIC"
    SUSPICIOUS = "SUSPICIOUS"
    MANIPULATED = "MANIPULATED"


@dataclass
class TechniqueResult:
    """Result from a single forensic technique."""

    name: str
    confidence: float
    verdict: str
    details: Dict[str, Any] = field(default_factory=dict)
    heatmap_data: Optional[str] = None  # Base64 encoded image
    description: str = ""


@dataclass
class MetadataInfo:
    """Extracted metadata from image."""

    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    timestamp: Optional[str] = None
    gps_coordinates: Optional[tuple] = None
    software: Optional[str] = None
    orientation: int = 1
    width: Optional[int] = None
    height: Optional[int] = None
    raw_exif: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForensicReport:
    """Complete forensic analysis report."""

    file_path: str
    timestamp: str
    overall_verdict: Verdict
    confidence_score: float
    techniques: Dict[str, TechniqueResult] = field(default_factory=dict)
    metadata: MetadataInfo = field(default_factory=MetadataInfo)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    image_width: Optional[int] = None
    image_height: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp,
            "overall_verdict": self.overall_verdict.value,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "techniques": {
                name: {
                    "confidence": result.confidence,
                    "verdict": result.verdict,
                    "description": result.description,
                    "details": result.details,
                }
                for name, result in self.techniques.items()
            },
            "metadata": {
                "camera_make": self.metadata.camera_make,
                "camera_model": self.metadata.camera_model,
                "timestamp": self.metadata.timestamp,
                "gps_coordinates": self.metadata.gps_coordinates,
                "software": self.metadata.software,
                "orientation": self.metadata.orientation,
                "width": self.metadata.width,
                "height": self.metadata.height,
            },
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }
