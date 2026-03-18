"""Main forensic analyzer orchestrating all analysis techniques."""

import time
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from deepguard.models import ForensicReport, TechniqueResult, Verdict
from deepguard.techniques import (
    CopyMoveDetection,
    ErrorLevelAnalysis,
    FaceConsistencyCheck,
    MetadataForensics,
    NoiseAnalysis,
)
from deepguard.utils import load_image


class ForensicAnalyzer:
    """Main forensic analysis orchestrator."""

    def __init__(self):
        """Initialize forensic analyzer with all techniques."""
        self.ela = ErrorLevelAnalysis(quality=90)
        self.noise = NoiseAnalysis()
        self.metadata = MetadataForensics()
        self.clone = CopyMoveDetection()
        self.face = FaceConsistencyCheck()

    def analyze(self, file_path: str) -> ForensicReport:
        """Analyze a single image file.

        Args:
            file_path: Path to image file

        Returns:
            ForensicReport with complete analysis results
        """
        start_time = time.time()

        # Load image
        image, _ = load_image(file_path)

        # Initialize report
        report = ForensicReport(
            file_path=file_path,
            timestamp=time._strftime(time.localtime()),
            overall_verdict=Verdict.AUTHENTIC,
            confidence_score=0.0,
            image_width=image.width,
            image_height=image.height,
        )

        try:
            # Run all analysis techniques
            ela_result, _ = self.ela.analyze(image)
            report.techniques["ELA"] = ela_result

            noise_result, _ = self.noise.analyze(image)
            report.techniques["Noise"] = noise_result

            metadata_result, metadata_info = self.metadata.analyze(file_path, image)
            report.techniques["Metadata"] = metadata_result
            report.metadata = metadata_info

            clone_result, _ = self.clone.analyze(image)
            report.techniques["CloneDetection"] = clone_result

            face_result, _ = self.face.analyze(image)
            report.techniques["FaceCheck"] = face_result

            # Calculate overall verdict and confidence
            verdicts = {"MANIPULATED": 0, "SUSPICIOUS": 0, "AUTHENTIC": 0}
            total_confidence = 0.0

            for technique in report.techniques.values():
                verdicts[technique.verdict] += 1
                total_confidence += technique.confidence

            # Determine overall verdict
            if verdicts["MANIPULATED"] >= 3:
                report.overall_verdict = Verdict.MANIPULATED
            elif verdicts["MANIPULATED"] >= 1 or verdicts["SUSPICIOUS"] >= 3:
                report.overall_verdict = Verdict.SUSPICIOUS
            else:
                report.overall_verdict = Verdict.AUTHENTIC

            # Calculate average confidence
            report.confidence_score = total_confidence / len(report.techniques)

            # Add recommendations
            self._add_recommendations(report)

        except Exception as e:
            report.warnings.append(f"Analysis error: {str(e)}")

        # Calculate processing time
        report.processing_time_ms = (time.time() - start_time) * 1000

        return report

    def batch_analyze(
        self, folder_path: str, recursive: bool = False
    ) -> List[ForensicReport]:
        """Analyze all images in a folder.

        Args:
            folder_path: Path to folder containing images
            recursive: Whether to search subdirectories

        Returns:
            List of ForensicReport objects
        """
        reports = []
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")

        # Find all supported image files
        pattern = "**/*" if recursive else "*"
        for file_path in folder.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in {
                ".jpg",
                ".jpeg",
                ".png",
                ".tiff",
                ".tif",
                ".bmp",
                ".webp",
            }:
                try:
                    report = self.analyze(str(file_path))
                    reports.append(report)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {str(e)}")

        return reports

    @staticmethod
    def _add_recommendations(report: ForensicReport) -> None:
        """Add recommendations based on analysis results.

        Args:
            report: ForensicReport to add recommendations to
        """
        if report.overall_verdict == Verdict.MANIPULATED:
            report.recommendations.extend([
                "High confidence of manipulation detected",
                "Consider consulting a professional forensic expert",
                "Compare with original source if available",
            ])
        elif report.overall_verdict == Verdict.SUSPICIOUS:
            report.recommendations.extend([
                "Some anomalies detected - further investigation recommended",
                "Multiple analysis techniques show concerning results",
                "Request metadata from original source",
            ])
        else:
            report.recommendations.append("No obvious signs of manipulation detected")

        if not report.metadata.camera_make and not report.metadata.camera_model:
            report.recommendations.append("No camera EXIF data found - image may have been stripped")

        if report.metadata.software:
            report.recommendations.append(f"Image may have been edited with {report.metadata.software}")
