"""
PandaCite - Python-based Citation Manager
"""
__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "pritam@stanford.edu"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Pritam Kumar Panda"
from pandacite.formatters.base import BaseCitationFormatter




__all__ = [
    "CitationManager",
    "BaseCitationFormatter",
    "FORMATTERS",
    "PARSERS",
    "PROCESSORS",
    "extract_metadata_from_file",
    "extract_metadata_from_text",
    "extract_metadata_from_url",
    "extract_metadata_from_doi",
    "extract_metadata_from_pdf",
    "extract_metadata_from_docx",
    "extract_metadata_from_bibtex",
    "extract_metadata_from_ris",
    "extract_metadata_from_endnote",
    "CitationManagerError",
    "CitationFormatError",
    "CitationParserError",
    "CitationProcessorError",
    "DEFAULT_CITATION_FORMAT",
    "DEFAULT_CITATION_STYLE",
    "SUPPORTED_CITATION_FORMATS",
    "SUPPORTED_CITATION_STYLES",
]