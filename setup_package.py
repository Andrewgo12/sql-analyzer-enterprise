#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - PACKAGE SETUP
Standard setuptools configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else "SQL Analyzer Enterprise - Professional SQL Analysis Tool"

setup(
    name="sql-analyzer-enterprise",
    version="1.0.0",
    author="SQL Analyzer Team",
    author_email="admin@sqlanalyzer.com",
    description="Enterprise-grade SQL analysis and optimization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Andrewgo12/sql-analyzer-enterprise",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Database Administrators",
        "Topic :: Database",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core web framework
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "websockets>=12.0",
        
        # Template and static files
        "jinja2>=3.1.2",
        "aiofiles>=23.2.1",
        
        # Configuration and environment
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        
        # Security and authentication
        "pyjwt>=2.8.0",
        "cryptography>=41.0.8",
        "passlib[bcrypt]>=1.7.4",
        
        # Database and ORM
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        
        # HTTP client and utilities
        "requests>=2.31.0",
        "httpx>=0.25.0",
        
        # CLI and logging
        "click>=8.1.7",
        "rich>=13.7.0",
        "colorama>=0.4.6",
        
        # Data processing
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        
        # File processing
        "openpyxl>=3.1.0",
        "pypdf2>=3.0.1",
        
        # Validation and parsing
        "pydantic>=2.5.0",
        "sqlparse>=0.4.4",
        
        # Development and testing (optional)
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
            "pre-commit>=3.5.0",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.1.0",
            "cx-oracle>=8.3.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "sentry-sdk>=1.38.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sql-analyzer=web_app.server:main",
            "sql-analyzer-setup=setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "web_app": [
            "static/**/*",
            "templates/**/*",
            "security/**/*",
            "integrations/**/*",
        ],
    },
    zip_safe=False,
    keywords="sql, database, analysis, optimization, enterprise, web, fastapi",
    project_urls={
        "Bug Reports": "https://github.com/Andrewgo12/sql-analyzer-enterprise/issues",
        "Source": "https://github.com/Andrewgo12/sql-analyzer-enterprise",
        "Documentation": "https://github.com/Andrewgo12/sql-analyzer-enterprise/wiki",
    },
)
