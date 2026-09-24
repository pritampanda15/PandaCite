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

class ISBNParser:
    """Parse ISBN numbers to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Parse an ISBN and return metadata"""
        return self.extractor.extract_from_isbn(isbn)

class URLParser:
    """Parse URLs to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a URL and return metadata"""
        return self.extractor.extract_from_url(url)

def _bibtex_fields(bibtex: str) -> List[Tuple[str, str]]:
    """Extract (name, value) pairs; values may be {nested {braces}}, "quoted" or bare"""
    fields = []
    field_start = re.compile(r'(\w+)\s*=\s*')
    match = field_start.search(bibtex)
    while match:
        pos = match.end()
        if pos >= len(bibtex):
            break
        opener = bibtex[pos]
        if opener == "{":
            depth, end = 0, pos
            while end < len(bibtex):
                if bibtex[end] == "{":
                    depth += 1
                elif bibtex[end] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                end += 1
            value = bibtex[pos + 1:end]
        elif opener == '"':
            end = bibtex.find('"', pos + 1)
            end = len(bibtex) if end == -1 else end
            value = bibtex[pos + 1:end]
        else:
            value = re.match(r'[^,}\s]*', bibtex[pos:]).group(0)
            end = pos + len(value)
        # Drop protective inner braces: {The {DNA} story} -> The DNA story
        fields.append((match.group(1), re.sub(r"\s+", " ", value.replace("{", "").replace("}", "")).strip()))
        match = field_start.search(bibtex, end + 1)
    return fields


class BibTexParser:
    """Parse BibTeX entries to extract metadata"""
    
    def parse(self, bibtex: str) -> Optional[Dict[str, Any]]:
        """Parse a BibTeX entry and return metadata"""
        try:
            # Simple BibTeX parser
            metadata = {
                "authors": []
            }
            
            # Extract entry type and key
            type_match = re.search(r'@(\w+)\s*\{([^,]+)', bibtex)
            if type_match:
                entry_type = type_match.group(1).lower()
                entry_key = type_match.group(2)
                
                metadata["type"] = entry_type
                metadata["id"] = entry_key
            
            # Extract fields
            for field, value in _bibtex_fields(bibtex):
                field = field.lower()
                
                if field == "author":
                    # Split authors by "and"
                    authors = value.split(" and ")
                    for author in authors:
                        author = author.strip()
                        # Convert to "Last, First" format if needed
                        if "," not in author:
                            names = author.split()
                            if len(names) > 1:
                                first_names = " ".join(names[:-1])
                                last_name = names[-1]
                                author = f"{last_name}, {first_names}"
                        
                        metadata["authors"].append(author)
                else:
                    metadata[field] = value
            
            # Map common BibTeX fields to our standard format
            field_mapping = {
                "title": "title",
                "journal": "journal",
                "year": "year",
                "volume": "volume",
                "number": "issue",
                "pages": "pages",
                "doi": "doi",
                "url": "url",
                "publisher": "publisher",
                "booktitle": "booktitle",
                "address": "address",
                "abstract": "abstract",
                "keywords": "keywords"
            }
            
            standardized_metadata = {}
            for bibtex_field, standard_field in field_mapping.items():
                if bibtex_field in metadata:
                    standardized_metadata[standard_field] = metadata[bibtex_field]
            
            # Add authors
            standardized_metadata["authors"] = metadata["authors"]
            
            # Ensure essential fields are present
            for field in ["title", "authors", "year"]:
                if field not in standardized_metadata:
                    standardized_metadata[field] = ""
            
            return standardized_metadata
        except Exception as e:
            print(f"Error parsing BibTeX entry: {e}")
            return None

class RISParser:
    """Parse RIS (Research Information Systems) entries to extract metadata"""
    
    def parse(self, ris: str) -> Optional[Dict[str, Any]]:
        """Parse a RIS entry and return metadata"""
        try:
            metadata = {
                "authors": []
            }
            
            start_page = end_page = ""
            
            # Split the RIS string into lines
            lines = ris.strip().split("\n")
            
            # Process each line
            for line in lines:
                line = line.strip()
                if not line or len(line) < 6:
                    continue
                
                # Extract tag and value
                tag = line[:2].strip()
                value = line[6:].strip()
                
                if tag == "TY":
                    # Publication type
                    metadata["type"] = value
                elif tag == "AU" or tag == "A1" or tag == "A2":
                    # Author
                    author = value
                    # Convert to "Last, First" format if needed
                    if "," not in author:
                        names = author.split()
                        if len(names) > 1:
                            first_names = " ".join(names[:-1])
                            last_name = names[-1]
                            author = f"{last_name}, {first_names}"
                    
                    metadata["authors"].append(author)
                elif tag == "TI" or tag == "T1":
                    # Title
                    metadata["title"] = value
                elif tag == "JO" or tag == "JF" or tag == "JA":
                    # Journal
                    metadata["journal"] = value
                elif tag == "VL":
                    # Volume
                    metadata["volume"] = value
                elif tag == "IS":
                    # Issue
                    metadata["issue"] = value
                elif tag == "SP":
                    # Start page
                    start_page = value
                elif tag == "EP":
                    # End page
                    end_page = value
                elif tag == "PY" or tag == "Y1":
                    # Publication year
                    if "/" in value:
                        # Extract just the year
                        metadata["year"] = value.split("/")[0]
                    else:
                        metadata["year"] = value
                elif tag == "DO":
                    # DOI
                    metadata["doi"] = value
                elif tag == "UR":
                    # URL
                    metadata["url"] = value
                elif tag == "PB":
                    # Publisher
                    metadata["publisher"] = value
                elif tag == "AB":
                    # Abstract
                    metadata["abstract"] = value
                elif tag == "KW":
                    # Keywords
                    if "keywords" not in metadata:
                        metadata["keywords"] = []
                    metadata["keywords"].append(value)
            
            if start_page or end_page:
                metadata["pages"] = "-".join(p for p in (start_page, end_page) if p)
            
            # Ensure essential fields are present
            for field in ["title", "authors", "year"]:
                if field not in metadata:
                    metadata[field] = ""
            
            return metadata
        except Exception as e:
            print(f"Error parsing RIS entry: {e}")
            return None