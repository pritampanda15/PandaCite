import sys
import os
from setuptools import setup, find_packages

# Read requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="pandacite",
    version="0.1.0",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "pandacite=pandacite.cli:main",
        ],
    },
    author="Dr. Pritam Kumar Panda",
    author_email="pritam@stanford.edu",
    description="A Python-based citation manager",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pritampanda15/pandacite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
