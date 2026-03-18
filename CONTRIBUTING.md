# Contributing to DeepGuard

Thank you for your interest in contributing to DeepGuard! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Report issues and concerns professionally

## How to Contribute

### Reporting Bugs

Found a bug? Create an issue on GitHub with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Screenshots if applicable

### Suggesting Enhancements

Have an idea? Please:

- Create an issue describing the feature
- Explain the use case and benefit
- Provide examples if possible
- Be open to discussion and feedback

### Submitting Code Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following the style guide below
4. Add tests for new functionality
5. Run tests: `pytest tests/`
6. Commit with clear messages: `git commit -m "Add feature X"`
7. Push to your fork: `git push origin feature/your-feature`
8. Create a Pull Request with a clear description

## Development Setup

Install development dependencies:

```bash
pip install -e ".[dev]"
pip install pytest pytest-cov black isort mypy
```

Run tests:

```bash
pytest tests/ -v
```

Format code:

```bash
black src/ tests/
isort src/ tests/
```

Type checking:

```bash
mypy src/deepguard
```

## Code Style Guide

- Follow PEP 8
- Use type hints for all function signatures
- Add docstrings to all functions and classes
- Maximum line length: 100 characters
- Use descriptive variable names
- Write clear, readable code

### Example Function:

```python
def analyze_image(
    file_path: str,
    techniques: Optional[List[str]] = None
) -> ForensicReport:
    """Analyze image for forensic evidence.

    Args:
        file_path: Path to image file
        techniques: List of techniques to apply (all if None)

    Returns:
        ForensicReport with analysis results

    Raises:
        ValueError: If file not found or format unsupported
    """
    # Implementation...
    pass
```

## Testing Requirements

- Write tests for all new features
- Maintain at least 80% code coverage
- Test edge cases and error conditions
- Use descriptive test names

Example test:

```python
def test_ela_detects_manipulation():
    """Test that ELA detects basic image manipulation."""
    # Setup test image
    # Run analysis
    # Assert manipulation detected
    pass
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new code
- Include examples for new features
- Update type hints documentation

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Add description of changes
4. Link related issues
5. Await review from maintainers

## Questions?

Feel free to:

- Open an issue for clarification
- Join our discussions
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for making DeepGuard better!
