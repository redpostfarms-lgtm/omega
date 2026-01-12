#!/usr/bin/env python3
"""
Setup configuration for The Gatekeeper
=======================================
Installation script for The Gatekeeper system.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]

setup(
    name="gatekeeper",
    version="1.0.0",
    description="The Gatekeeper - Complete Security Monitoring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Red Post Farms, LLC",
    author_email="",
    url="",
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "gatekeeper=gatekeeper_integration_module:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
