from setuptools import setup, find_packages

setup(
    name="pandacite",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-docx>=0.8.11",
        "beautifulsoup4>=4.9.3",
    ],
    entry_points={
        "console_scripts": [
            "pandacite=pandacite.cli:main",
        ],
    },
    author="Dr. Pritam Kumar Panda",
    author_email="pritam@stanford.edu",
    description="A Python-based citation manager like EndNote or Mendeley",
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