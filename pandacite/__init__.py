"""
PandaCite - Python-based Citation Manager
"""
__version__ = "0.3.0"
__author__ = "Pritam Kumar Panda"
__email__ = "pritam@stanford.edu"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Pritam Kumar Panda"

from pandacite.formatters import FORMATTERS
from pandacite.formatters.base import BaseCitationFormatter
from pandacite.citation_manager import EnhancedCitationManager
from pandacite.extractors import EnhancedMetadataExtractor, IDDetector

__all__ = [
    "EnhancedCitationManager",
    "EnhancedMetadataExtractor",
    "IDDetector",
    "BaseCitationFormatter",
    "FORMATTERS",
]
