"""Tests for Error Level Analysis technique."""

import numpy as np
import pytest
from PIL import Image

from deepguard.techniques.ela import ErrorLevelAnalysis


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    return Image.fromarray(arr, mode="RGB")


@pytest.fixture
def edited_region_image():
    """Create an image with an edited region."""
    arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image = Image.fromarray(arr, mode="RGB")

    # Paste a different region to simulate editing
    edited_arr = np.ones((30, 30, 3), dtype=np.uint8) * 100
    edited_image = Image.fromarray(edited_arr, mode="RGB")
    image.paste(edited_image, (20, 20))

    return image


def test_ela_initialization():
    """Test ELA initialization."""
    ela = ErrorLevelAnalysis(quality=90)
    assert ela.quality == 90


def test_ela_custom_quality():
    """Test ELA with custom quality setting."""
    ela = ErrorLevelAnalysis(quality=75)
    assert ela.quality == 75


def test_ela_analyze_authentic_image(sample_image):
    """Test ELA on potentially authentic image."""
    ela = ErrorLevelAnalysis()
    result, heatmap = ela.analyze(sample_image)

    assert result.name == "Error Level Analysis"
    assert 0 <= result.confidence <= 100
    assert result.verdict in ["AUTHENTIC", "SUSPICIOUS", "MANIPULATED"]
    assert heatmap.shape == (sample_image.height, sample_image.width, 3)


def test_ela_analyze_edited_image(edited_region_image):
    """Test ELA on edited image."""
    ela = ErrorLevelAnalysis()
    result, heatmap = ela.analyze(edited_region_image)

    assert result.verdict in ["AUTHENTIC", "SUSPICIOUS", "MANIPULATED"]
    assert "details" in result.__dict__
    assert "mean_error" in result.details
    assert "std_error" in result.details


def test_ela_returns_correct_heatmap_shape(sample_image):
    """Test ELA heatmap dimensions."""
    ela = ErrorLevelAnalysis()
    result, heatmap = ela.analyze(sample_image)

    assert heatmap.shape == (sample_image.height, sample_image.width, 3)
    assert heatmap.dtype == np.uint8


def test_ela_confidence_in_valid_range(sample_image):
    """Test that confidence is in valid range."""
    ela = ErrorLevelAnalysis()
    result, _ = ela.analyze(sample_image)

    assert 0 <= result.confidence <= 100
    assert isinstance(result.confidence, float)


def test_ela_has_description(sample_image):
    """Test that ELA result has description."""
    ela = ErrorLevelAnalysis()
    result, _ = ela.analyze(sample_image)

    assert len(result.description) > 0
    assert "compression" in result.description.lower()


def test_ela_grayscale_image():
    """Test ELA on grayscale image."""
    arr = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    image = Image.fromarray(arr, mode="L")

    ela = ErrorLevelAnalysis()
    result, heatmap = ela.analyze(image)

    assert result.verdict in ["AUTHENTIC", "SUSPICIOUS", "MANIPULATED"]
    assert heatmap.shape == (100, 100, 3)
