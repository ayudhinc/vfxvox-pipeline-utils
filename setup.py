"""Setup configuration for vfxvox-pipeline-utils."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="vfxvox-pipeline-utils",
    version="0.1.0",
    description="Open source toolkit for VFX production pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VFXVox",
    author_email="pipeline-utils@vfxvox.org",
    url="https://github.com/ayudhinc/vfxvox-pipeline-utils",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "PyYAML>=6.0",
        "Pillow>=9.0",
    ],
    extras_require={
        "usd": ["usd-core>=22.11"],
        "oiio": ["OpenImageIO>=2.4"],
        "all": ["usd-core>=22.11", "OpenImageIO>=2.4"],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vfxvox=vfxvox_pipeline_utils.cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="vfx pipeline validation usd sequence shotlint",
    project_urls={
        "Bug Reports": "https://github.com/ayudhinc/vfxvox-pipeline-utils/issues",
        "Source": "https://github.com/ayudhinc/vfxvox-pipeline-utils",
        "Documentation": "https://github.com/ayudhinc/vfxvox-pipeline-utils/docs",
    },
)
