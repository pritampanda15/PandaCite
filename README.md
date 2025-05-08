# PandaCite

<img src="logo/pandacite.png" width="400" alt="PandaCite Logo">

A Python-based citation manager similar to EndNote or Mendeley.

## Features

- Generate citations from DOI, PMID, arXiv, ISBN, URL, and more
- Support for 20+ citation styles (APA, Chicago, Nature, Science, etc.)
- Process Word documents and automatically update citations
- Numbered citation styles with proper reference management

## Installation

```bash
pip install pandacite

## Usage

# Generate a single citation
pandacite single --id "10.1038/s41586-020-2649-2" --format nature

# Process Word document
pandacite word --input manuscript.docx --output manuscript_with_citations.docx --format ieee

## PYTHON API

from pandacite import EnhancedCitationManager

# Create citation manager
manager = EnhancedCitationManager()

# Generate a citation
citation = manager.process_single_citation("doi", "10.1038/s41586-020-2649-2", "nature")
print(citation)


## Supported Citation Styles

APA
Chicago
MLA
Harvard
Nature
Science
IEEE
Vancouver
...and many more!

## License
MIT License