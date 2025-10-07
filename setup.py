"""
Setup configuration for AI Newsletter Scraper.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')

setup(
    name="ai-newsletter-scraper",
    version="1.0.0",
    description="A modular and extensible content scraping framework for AI-related news",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Newsletter Team",
    author_email="team@ainewsletter.dev",
    url="https://github.com/yourusername/ai-newsletter-v2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "twitter": [
            "tweepy>=4.14.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="scraper ai news newsletter reddit rss blog twitter",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-newsletter-v2/issues",
        "Source": "https://github.com/yourusername/ai-newsletter-v2",
        "Documentation": "https://github.com/yourusername/ai-newsletter-v2/docs",
    },
)

