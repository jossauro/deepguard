"""DeepGuard - Offline image forensics and deepfake detection.

A professional CLI tool for detecting image and document manipulation,
deepfakes, and digital tampering. Runs completely offline with no API keys required.
"""

__version__ = "1.0.0"
__author__ = "Camilo Girardelli"
__email__ = "camilo@girardellitecnologia.com"
__license__ = "MIT"

from .analyzer import ForensicAnalyzer
from .models import ForensicReport, Verdict

__all__ = ["ForensicAnalyzer", "ForensicReport", "Verdict", "__version__"]
