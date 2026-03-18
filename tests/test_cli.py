"""Tests for CLI commands."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner
from PIL import Image

from deepguard.cli import main


@pytest.fixture
def sample_image_file():
    """Create a temporary test image file."""
    img = Image.new("RGB", (200, 200), color="blue")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name, format="JPEG")
        yield f.name
    Path(f.name).unlink()


@pytest.fixture
def cli_runner():
    """Create CLI test runner."""
    return CliRunner()


def test_cli_analyze_command(cli_runner, sample_image_file):
    """Test analyze command."""
    result = cli_runner.invoke(main, ["analyze", sample_image_file, "--no-open"])

    assert result.exit_code == 0
    assert "Analysis Complete" in result.output or "complete" in result.output.lower()


def test_cli_analyze_invalid_file(cli_runner):
    """Test analyze with invalid file."""
    result = cli_runner.invoke(main, ["analyze", "/nonexistent/file.jpg"])

    assert result.exit_code != 0


def test_cli_analyze_unsupported_format(cli_runner):
    """Test analyze with unsupported format."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"test")
        temp_file = f.name

    try:
        result = cli_runner.invoke(main, ["analyze", temp_file])
        assert result.exit_code != 0
        assert "unsupported" in result.output.lower()
    finally:
        Path(temp_file).unlink()


def test_cli_metadata_command(cli_runner, sample_image_file):
    """Test metadata command."""
    result = cli_runner.invoke(main, ["metadata", sample_image_file])

    assert result.exit_code == 0


def test_cli_metadata_json_format(cli_runner, sample_image_file):
    """Test metadata with JSON format."""
    result = cli_runner.invoke(main, ["metadata", sample_image_file, "--format", "json"])

    assert result.exit_code == 0
    assert "{" in result.output


def test_cli_batch_command(cli_runner):
    """Test batch command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test images
        for i in range(2):
            img = Image.new("RGB", (100, 100), color="red")
            img.save(f"{tmpdir}/test_{i}.jpg")

        result = cli_runner.invoke(main, ["batch", tmpdir])

        assert result.exit_code == 0
        assert "Analyzed" in result.output or "analyzed" in result.output.lower()


def test_cli_report_command(cli_runner, sample_image_file):
    """Test report command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = f"{tmpdir}/report.html"
        result = cli_runner.invoke(main, ["report", sample_image_file, "--output", output_file])

        assert result.exit_code == 0
        assert Path(output_file).exists()


def test_cli_analyze_with_output(cli_runner, sample_image_file):
    """Test analyze with custom output path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = f"{tmpdir}/custom_report.html"
        result = cli_runner.invoke(
            main,
            ["analyze", sample_image_file, "--output", output_file, "--no-open"],
        )

        assert result.exit_code == 0
        assert Path(output_file).exists()


def test_cli_main_group(cli_runner):
    """Test main CLI group."""
    result = cli_runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "analyze" in result.output
    assert "batch" in result.output
