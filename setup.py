#!/usr/bin/env python
"""Setup configuration for DeepGuard."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="deepguard",
    version="1.0.0",
    author="Camilo Girardelli",
    author_email="camilo@girardellitecnologia.com",
    description="Offline image forensics and deepfake detection from your terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cameronwdata/deepguard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "deepguard": ["templates/*.html"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "deepguard=deepguard.cli:main",
        ],
    },
)
