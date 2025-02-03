#!/usr/bin/env python3
from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text("utf-8")
REQUIREMENTS = (HERE / "requirements.txt").read_text().splitlines()

setup(
    name="fishweb",
    version="0.1.0",
    description="Web apps like serverless",
    long_description=README,
    long_description_content_type="text/markdown",
    author="SlumberDemon",
    author_email="hi@sofa.sh",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_packages(where="."),
    install_requires=REQUIREMENTS,
    package_dir={"": "."},
    entry_points={
        "console_scripts": [
            "fishweb=fishweb.main:app",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/slumberdemon/fishweb/issues",
        "Source": "https://github.com/slumberdemon/fishweb",
    },
)
