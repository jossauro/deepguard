"""Tests for Metadata Forensics technique."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from deepguard.techniques.metadata import MetadataForensics


@pytest.fixture
def sample_image_file():
    """Create a temporary test image file."""
    img = Image.new("RGB", (100, 100), color="red")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name, format="JPEG")
        yield f.name
    Path(f.name).unlink()


def test_metadata_forensics_initialization():
    """Test MetadataForensics initialization."""
    mf = MetadataForensics()
    assert mf is not None
    assert hasattr(mf, "EDITING_SOFTWARE")


def test_metadata_analyze_returns_tuple(sample_image_file):
    """Test that analyze returns a tuple."""
    image = Image.open(sample_image_file)
    mf = MetadataForensics()

    result = mf.analyze(sample_image_file, image)

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_metadata_result_properties(sample_image_file):
    """Test metadata result has expected properties."""
    image = Image.open(sample_image_file)
    mf = MetadataForensics()

    result, metadata = mf.analyze(sample_image_file, image)

    assert result.name == "Metadata Forensics"
    assert result.verdict in ["AUTHENTIC", "SUSPICIOUS", "MANIPULATED"]
    assert 0 <= result.confidence <= 100


def test_metadata_info_structure(sample_image_file):
    """Test MetadataInfo structure."""
    image = Image.open(sample_image_file)
    mf = MetadataForensics()

    _, metadata = mf.analyze(sample_image_file, image)

    assert hasattr(metadata, "camera_make")
    assert hasattr(metadata, "camera_model")
    assert hasattr(metadata, "timestamp")
    assert hasattr(metadata, "software")
    assert hasattr(metadata, "width")
    assert hasattr(metadata, "height")


def test_metadata_detects_dimensions(sample_image_file):
    """Test metadata correctly detects image dimensions."""
    image = Image.open(sample_image_file)
    mf = MetadataForensics()

    _, metadata = mf.analyze(sample_image_file, image)

    assert metadata.width == 100
    assert metadata.height == 100


def test_metadata_has_description(sample_image_file):
    """Test that metadata result has description."""
    image = Image.open(sample_image_file)
    mf = MetadataForensics()

    result, _ = mf.analyze(sample_image_file, image)

    assert len(result.description) > 0
    assert "exif" in result.description.lower()


def test_metadata_editing_software_detection():
    """Test detection of editing software."""
    mf = MetadataForensics()

    assert "adobe" in mf.EDITING_SOFTWARE
    assert "photoshop" in mf.EDITING_SOFTWARE
    assert "gimp" in mf.EDITING_SOFTWARE
