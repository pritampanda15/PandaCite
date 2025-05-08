from pandacite.formatters import FORMATTERS
from pandacite.extractors.metadata import EnhancedMetadataExtractor
from pandacite.extractors.detector import IDDetector
from pandacite.parsers import DOIParser, PMIDParser, ArXivParser, ISBNParser, URLParser, BibTexParser, RISParser
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
from pandacite.formatters import (
    ElsevierFormatter,
    SpringerFormatter,
    APAFormatter,
    NatureFormatter,
    ScienceFormatter,
    IEEEFormatter,
    ChicagoFormatter,
    MLAFormatter,
    HarvardFormatter,
    VancouverFormatter,
    BMCFormatter,
    PLOSFormatter,
    CellFormatter,
    JAMAFormatter,
    BMJFormatter,
    NEJMFormatter,
    JBCFormatter,
    RSCFormatter,
    ACSFormatter,
    AIPFormatter,
    ACMFormatter,
    OxfordFormatter
)
from pandacite.parsers import (
    DOIParser,
    PMIDParser,
    ArXivParser,
    ISBNParser,
    URLParser,
    BibTexParser,
    RISParser
)
from pandacite.extractors.metadata import EnhancedMetadataExtractor
from pandacite.extractors.detector import IDDetector


class EnhancedCitationManager:
    """Enhanced command-line citation manager with support for multiple sources and formats"""
    
    def __init__(self):
        """Initialize the citation manager"""
        self.metadata_extractor = EnhancedMetadataExtractor()
        
        # Initialize parsers
        self.parsers = {
            "doi": DOIParser(self.metadata_extractor),
            "pmid": PMIDParser(self.metadata_extractor),
            "arxiv": ArXivParser(self.metadata_extractor),
            "isbn": ISBNParser(self.metadata_extractor),
            "url": URLParser(self.metadata_extractor),
            "bibtex": BibTexParser(),
            "ris": RISParser()
        }
        
        # Initialize formatters
        self.formatters = {
            # Basic styles
            "elsevier": ElsevierFormatter(),
            "springer": SpringerFormatter(),
            "apa": APAFormatter(),
            
            # General journal styles
            "nature": NatureFormatter(),
            "science": ScienceFormatter(),
            "ieee": IEEEFormatter(),
            "chicago": ChicagoFormatter(),
            "mla": MLAFormatter(),
            "harvard": HarvardFormatter(),
            "vancouver": VancouverFormatter(),
            "bmc": BMCFormatter(),
            "plos": PLOSFormatter(),
            "cell": CellFormatter(),
            
            # Medical journal styles
            "jama": JAMAFormatter(),
            "bmj": BMJFormatter(),
            "nejm": NEJMFormatter(),
            
            # Scientific journal styles
            "jbc": JBCFormatter(),
            "rsc": RSCFormatter(),
            "acs": ACSFormatter(),
            "aip": AIPFormatter(),
            
            # Computer science and humanities
            "acm": ACMFormatter(),
            "oxford": OxfordFormatter()
        }
        
        self.citation_data = {}
        self.id_detector = IDDetector()
    
    def extract_metadata(self, id_type: str, id_value: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata based on ID type and value
        
        Args:
            id_type: Type of identifier
            id_value: Identifier value
            
        Returns:
            Metadata dictionary if successful, None otherwise
        """
        parser = self.parsers.get(id_type.lower())
        if parser:
            return parser.parse(id_value)
        else:
            print(f"Unsupported ID type: {id_type}")
            return None
    
    def format_citation(self, metadata: Dict[str, Any], format_name: str) -> Optional[str]:
        """
        Format metadata using the specified formatter
        
        Args:
            metadata: Metadata dictionary
            format_name: Citation format name
            
        Returns:
            Formatted citation if successful, None otherwise
        """
        formatter = self.formatters.get(format_name.lower())
        if formatter:
            return formatter.format_citation(metadata)
        else:
            print(f"Unsupported format: {format_name}")
            return None
    
    def process_single_citation(self, id_type: str, id_value: str, format_name: str) -> Optional[str]:
        """
        Process a single citation
        
        Args:
            id_type: Type of identifier
            id_value: Identifier value
            format_name: Citation format name
            
        Returns:
            Formatted citation if successful, None otherwise
        """
        # Auto-detect ID type if set to "auto"
        if id_type.lower() == "auto":
            id_type = self.id_detector.detect_id_type(id_value)
            print(f"Detected ID type: {id_type}")
        
        metadata = self.extract_metadata(id_type, id_value)
        if metadata:
            citation = self.format_citation(metadata, format_name)
            if citation:
                # Store metadata for later use
                key = f"{id_type}_{id_value}"
                metadata["formatted_citation"] = citation
                self.citation_data[key] = metadata
                return citation
        return None
    
    def process_batch_citations(self, ids: List[str], id_type: str, format_name: str) -> List[str]:
        """
        Process multiple citations
        
        Args:
            ids: List of identifiers
            id_type: Type of identifier
            format_name: Citation format name
            
        Returns:
            List of formatted citations
        """
        results = []
        for id_value in ids:
            id_value = id_value.strip()
            if not id_value:
                continue
            
            # Auto-detect ID type if set to "auto"
            current_id_type = id_type
            if id_type.lower() == "auto":
                current_id_type = self.id_detector.detect_id_type(id_value)
                print(f"Detected ID type for '{id_value}': {current_id_type}")
            
            citation = self.process_single_citation(current_id_type, id_value, format_name)
            if citation:
                results.append(citation)
            else:
                results.append(f"Failed to retrieve/format citation for {current_id_type} {id_value}")
        
        return results
    
    def process_file(self, file_path: str, id_type: str, format_name: str) -> List[str]:
        """
        Process IDs from a file
        
        Args:
            file_path: Path to the file containing identifiers
            id_type: Type of identifier
            format_name: Citation format name
            
        Returns:
            List of formatted citations
        """
        try:
            with open(file_path, "r") as file:
                ids = [line.strip() for line in file if line.strip()]
            return self.process_batch_citations(ids, id_type, format_name)
        except Exception as e:
            print(f"Error processing file: {e}")
            return []
    
    def export_citations(self, citations: List[str], output_path: str) -> bool:
        """
        Export citations to a file
        
        Args:
            citations: List of formatted citations
            output_path: Path to save the citations
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, "w") as file:
                for citation in citations:
                    file.write(citation + "\n\n")
            return True
        except Exception as e:
            print(f"Error exporting citations: {e}")
            return False
    
    def export_bibtex(self, output_path: str) -> bool:
        """
        Export citations to a BibTeX file
        
        Args:
            output_path: Path to save the BibTeX file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, "w") as file:
                for key, metadata in self.citation_data.items():
                    bibtex_entry = self._convert_to_bibtex(key, metadata)
                    file.write(bibtex_entry + "\n\n")
            return True
        except Exception as e:
            print(f"Error exporting BibTeX: {e}")
            return False
    
    def _convert_to_bibtex(self, key: str, metadata: Dict[str, Any]) -> str:
        """
        Convert metadata to BibTeX format
        
        Args:
            key: Citation key
            metadata: Metadata dictionary
            
        Returns:
            BibTeX entry
        """
        # Determine entry type
        entry_type = "article"
        if "type" in metadata:
            if metadata["type"] == "book":
                entry_type = "book"
            elif metadata["type"] == "inproceedings" or metadata["type"] == "conference-paper":
                entry_type = "inproceedings"
            elif metadata["type"] == "preprint":
                entry_type = "unpublished"
        
        # Create BibTeX key
        if "authors" in metadata and metadata["authors"]:
            first_author = metadata["authors"][0].split(",")[0]
            bibtex_key = f"{first_author}{metadata.get('year', '')}"
        else:
            bibtex_key = f"citation{key}"
        
        # Start building the BibTeX entry
        bibtex = f"@{entry_type}{{{bibtex_key},\n"
        
        # Add authors
        if "authors" in metadata and metadata["authors"]:
            authors = " and ".join(metadata["authors"])
            bibtex += f"  author = {{{authors}}},\n"
        
        # Add title
        if "title" in metadata and metadata["title"]:
            bibtex += f"  title = {{{metadata['title']}}},\n"
        
        # Add journal/booktitle
        if "journal" in metadata and metadata["journal"]:
            if entry_type == "inproceedings":
                bibtex += f"  booktitle = {{{metadata['journal']}}},\n"
            else:
                bibtex += f"  journal = {{{metadata['journal']}}},\n"
        
        # Add year
        if "year" in metadata and metadata["year"]:
            bibtex += f"  year = {{{metadata['year']}}},\n"
        
        # Add volume
        if "volume" in metadata and metadata["volume"]:
            bibtex += f"  volume = {{{metadata['volume']}}},\n"
        
        # Add number/issue
        if "issue" in metadata and metadata["issue"]:
            bibtex += f"  number = {{{metadata['issue']}}},\n"
        
        # Add pages
        if "pages" in metadata and metadata["pages"]:
            bibtex += f"  pages = {{{metadata['pages']}}},\n"
        
        # Add DOI
        if "doi" in metadata and metadata["doi"]:
            bibtex += f"  doi = {{{metadata['doi']}}},\n"
        
        # Add URL
        if "url" in metadata and metadata["url"]:
            bibtex += f"  url = {{{metadata['url']}}},\n"
        
        # Add publisher
        if "publisher" in metadata and metadata["publisher"]:
            bibtex += f"  publisher = {{{metadata['publisher']}}},\n"
        
        # Add abstract
        if "abstract" in metadata and metadata["abstract"]:
            # Truncate long abstracts
            abstract = metadata["abstract"]
            if len(abstract) > 500:
                abstract = abstract[:497] + "..."
            bibtex += f"  abstract = {{{abstract}}},\n"
        
        # Remove the trailing comma and newline, and close the entry
        bibtex = bibtex.rstrip(",\n") + "\n}"
        
        return bibtex