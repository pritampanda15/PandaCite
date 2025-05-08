import requests
import json
import sys
import os
import re
import argparse
from typing import Dict, Any, List, Optional, Tuple
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse
from docx import Document



class IDDetector:
    """Detect and categorize different types of identifiers"""
    
    def detect_id_type(self, identifier: str) -> str:
        """
        Detect the type of identifier
        
        Args:
            identifier: The identifier string
            
        Returns:
            The detected type ("doi", "pmid", "arxiv", "isbn", "url", "bibtex", "ris", "unknown")
        """
        identifier = identifier.strip()
        
        # Check if it's a DOI
        if identifier.startswith("10.") or "doi.org" in identifier.lower():
            return "doi"
        
        # Check if it's a PMID
        if identifier.isdigit() and len(identifier) <= 8:
            return "pmid"
        
        # Check if it's an arXiv ID
        if (identifier.startswith("arXiv:") or 
            (re.match(r"\d{4}\.\d{4,5}", identifier)) or 
            (re.match(r"\d{7}", identifier) and len(identifier) == 7)):
            return "arxiv"
        
        # Check if it's an ISBN
        if (re.match(r"^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$", identifier)):
            return "isbn"
        
        # Check if it's a URL
        if (identifier.startswith("http://") or 
            identifier.startswith("https://") or 
            identifier.startswith("www.")):
            return "url"
        
        # Check if it's a BibTeX entry
        if identifier.startswith("@") and "{" in identifier and "=" in identifier:
            return "bibtex"
        
        # Check if it's a RIS entry
        if "TY  -" in identifier and "ER  -" in identifier:
            return "ris"
        
        # If nothing matches, return unknown
        return "unknown"