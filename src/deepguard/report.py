"""HTML forensic report generator."""

import json
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from deepguard.models import ForensicReport
from deepguard.utils import image_to_base64, numpy_to_base64


class ReportGenerator:
    """Generate HTML forensic reports."""

    def __init__(self):
        """Initialize report generator with Jinja2 environment."""
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_html(self, report: ForensicReport, original_image_path: str) -> str:
        """Generate HTML forensic report.

        Args:
            report: ForensicReport object
            original_image_path: Path to original image for embedding

        Returns:
            HTML string
        """
        # Load and embed original image
        try:
            from PIL import Image

            original_image = Image.open(original_image_path)
            image_base64 = image_to_base64(original_image)
        except Exception:
            image_base64 = None

        # Prepare verdict color
        verdict_colors = {
            "AUTHENTIC": "#10b981",
            "SUSPICIOUS": "#f59e0b",
            "MANIPULATED": "#ef4444",
        }

        # Load template
        template = self.env.get_template("report.html")

        # Render HTML
        html = template.render(
            report=report,
            verdict_color=verdict_colors.get(report.overall_verdict.value, "#6b7280"),
            image_base64=image_base64,
            json_dump=json.dumps,
        )

        return html

    def generate_json(self, report: ForensicReport) -> str:
        """Generate JSON report.

        Args:
            report: ForensicReport object

        Returns:
            JSON string
        """
        return json.dumps(report.to_dict(), indent=2)

    def save_html(self, report: ForensicReport, output_path: str, original_image_path: str) -> str:
        """Generate and save HTML report.

        Args:
            report: ForensicReport object
            output_path: Where to save HTML file
            original_image_path: Path to original image

        Returns:
            Path to saved file
        """
        html = self.generate_html(report, original_image_path)

        Path(output_path).write_text(html, encoding="utf-8")

        return output_path

    def save_json(self, report: ForensicReport, output_path: str) -> str:
        """Generate and save JSON report.

        Args:
            report: ForensicReport object
            output_path: Where to save JSON file

        Returns:
            Path to saved file
        """
        json_str = self.generate_json(report)

        Path(output_path).write_text(json_str, encoding="utf-8")

        return output_path
