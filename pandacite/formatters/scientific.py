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
from .base import BaseCitationFormatter

class ElsevierFormatter(BaseCitationFormatter):
    """Format citations in Elsevier style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an Elsevier-style citation"""
        # Elsevier typically uses the Vancouver system
        
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 6:
                authors = ", ".join(metadata["authors"][:6]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
        
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')};"
        
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')})"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Elsevier"""
        if metadata.get("authors"):
            first_author = metadata["authors"][0].split(",")[0]
            if len(metadata["authors"]) > 1:
                return f"({first_author} et al., {metadata.get('year', '')})"
            else:
                return f"({first_author}, {metadata.get('year', '')})"
        else:
            return f"(Anonymous, {metadata.get('year', '')})"

class SpringerFormatter(BaseCitationFormatter):
    """Format citations in Springer style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Springer-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 3:
                authors = metadata["authors"][0] + " et al"
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}: {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}"
            
        if metadata.get("volume"):
            citation += f" {metadata.get('volume', '')}"
            
        if metadata.get("pages"):
            citation += f", {metadata.get('pages', '')}"
            
        if metadata.get("year"):
            citation += f" ({metadata.get('year', '')})"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Springer"""
        if metadata.get("authors"):
            first_author = metadata["authors"][0].split(",")[0]
            if len(metadata["authors"]) > 1:
                return f"{first_author} et al. ({metadata.get('year', '')})"
            else:
                return f"{first_author} ({metadata.get('year', '')})"
        else:
            return f"Anonymous ({metadata.get('year', '')})"

class APAFormatter(BaseCitationFormatter):
    """Format citations in APA style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an APA-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 7:
                authors = ", ".join(metadata["authors"][:6]) + ", ... " + metadata["authors"][-1]
            else:
                authors = ", ".join(metadata["authors"])
            
            # Replace last comma with "&"
            last_comma_index = authors.rfind(",")
            if last_comma_index != -1:
                authors = authors[:last_comma_index] + " &" + authors[last_comma_index+1:]
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. ({metadata.get('year', '')}). {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}"
            
            if metadata.get("volume"):
                citation += f", {metadata.get('volume', '')}"
                
                if metadata.get("issue"):
                    citation += f"({metadata.get('issue', '')})"
                    
            if metadata.get("pages"):
                citation += f", {metadata.get('pages', '')}"
        
        citation += "."
        
        if metadata.get("doi"):
            citation += f" https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for APA"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"({author}, {metadata.get('year', '')})"
            elif len(metadata["authors"]) == 2:
                author1 = metadata["authors"][0].split(",")[0]
                author2 = metadata["authors"][1].split(",")[0]
                return f"({author1} & {author2}, {metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"({author} et al., {metadata.get('year', '')})"
        else:
            return f"(Anonymous, {metadata.get('year', '')})"

# Additional citation formatters for various journal styles

class NatureFormatter(BaseCitationFormatter):
    """Format citations in Nature style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Nature-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 5:
                authors = ", ".join(metadata["authors"][:5]) + " et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} "
        citation += f"{metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')} "
            
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}). "
        
        if metadata.get("doi"):
            citation += f"https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Nature"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} ({metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al. ({metadata.get('year', '')})"
        else:
            return f"Anonymous ({metadata.get('year', '')})"

class ScienceFormatter(BaseCitationFormatter):
    """Format citations in Science style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Science-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 5:
                authors = ", ".join(metadata["authors"][:5]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}, "
        citation += f"{metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}. "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')} "
            
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}). "
        
        if metadata.get("doi"):
            citation += f"doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Science"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} ({metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al. ({metadata.get('year', '')})"
        else:
            return f"Anonymous ({metadata.get('year', '')})"

class IEEEFormatter(BaseCitationFormatter):
    """Format citations in IEEE style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an IEEE-style citation"""
        # Format authors with initials
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] + "." for name in first_name.split()])
                    formatted_authors.append(f"{last_name}, {initials}")
                else:
                    formatted_authors.append(author)
            
            if len(formatted_authors) > 3:
                authors = ", ".join(formatted_authors[:3]) + ", et al."
            else:
                authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}, \"{metadata.get('title', '')},\" "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}, "
            
        if metadata.get("volume"):
            citation += f"vol. {metadata.get('volume', '')}, "
            
        if metadata.get("issue"):
            citation += f"no. {metadata.get('issue', '')}, "
            
        if metadata.get("pages"):
            citation += f"pp. {metadata.get('pages', '').replace('-', '–')}, "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}. "
        
        if metadata.get("doi"):
            citation += f"doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for IEEE"""
        # IEEE uses numbered citations, but we'll return author-date for consistency
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"[{author}, {metadata.get('year', '')}]"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"[{author} et al., {metadata.get('year', '')}]"
        else:
            return f"[Anonymous, {metadata.get('year', '')}]"

class ChicagoFormatter(BaseCitationFormatter):
    """Format citations in Chicago style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Chicago-style citation"""
        # Format authors
        if metadata.get("authors"):
            # Flip first author only
            formatted_authors = []
            for i, author in enumerate(metadata["authors"]):
                parts = author.split(",")
                if i == 0 and len(parts) == 2:
                    # Keep first author as Last, First
                    formatted_authors.append(author)
                elif len(parts) == 2:
                    # Flip subsequent authors to First Last
                    formatted_authors.append(f"{parts[1].strip()} {parts[0].strip()}")
                else:
                    formatted_authors.append(author)
            
            if len(formatted_authors) > 10:
                authors = ", ".join(formatted_authors[:7]) + ", et al."
            else:
                authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. \"{metadata.get('title', '')}.\" "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("issue"):
            citation += f"no. {metadata.get('issue', '')} "
            
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}): "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}. "
        else:
            citation += ". "
        
        if metadata.get("doi"):
            citation += f"https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Chicago"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"({author} {metadata.get('year', '')})"
            elif len(metadata["authors"]) == 2:
                author1 = metadata["authors"][0].split(",")[0]
                author2 = metadata["authors"][1].split(",")[0]
                return f"({author1} and {author2} {metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"({author} et al. {metadata.get('year', '')})"
        else:
            return f"(Anonymous {metadata.get('year', '')})"

class MLAFormatter(BaseCitationFormatter):
    """Format citations in MLA style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an MLA-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                authors = metadata["authors"][0]
            elif len(metadata["authors"]) == 2:
                parts1 = metadata["authors"][0].split(",")
                parts2 = metadata["authors"][1].split(",")
                
                if len(parts1) == 2 and len(parts2) == 2:
                    # First author as Last, First; second as First Last
                    authors = f"{parts1[0]}, {parts1[1].strip()} and {parts2[1].strip()} {parts2[0]}"
                else:
                    authors = f"{metadata['authors'][0]} and {metadata['authors'][1]}"
            elif len(metadata["authors"]) > 2:
                authors = f"{metadata['authors'][0]}, et al."
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. \"{metadata.get('title', '')}.\" "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}, "
            
        if metadata.get("volume"):
            citation += f"vol. {metadata.get('volume', '')}, "
            
        if metadata.get("issue"):
            citation += f"no. {metadata.get('issue', '')}, "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}, "
            
        if metadata.get("pages"):
            citation += f"pp. {metadata.get('pages', '')}. "
        else:
            citation += ". "
        
        if metadata.get("doi"):
            citation += f"DOI: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for MLA"""
        if metadata.get("authors"):
            author = metadata["authors"][0].split(",")[0]
            return f"({author})"
        else:
            return "(Anonymous)"

class HarvardFormatter(BaseCitationFormatter):
    """Format citations in Harvard style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Harvard-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] + "." for name in first_name.split()])
                    formatted_authors.append(f"{last_name}, {initials}")
                else:
                    formatted_authors.append(author)
            
            if len(formatted_authors) > 3:
                authors = ", ".join(formatted_authors[:3]) + ", et al."
            else:
                authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} "
        
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}). "
            
        citation += f"{metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}, "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')}), "
        else:
            citation += ", "
            
        if metadata.get("pages"):
            citation += f"pp. {metadata.get('pages', '')}. "
        else:
            citation += ". "
        
        if metadata.get("doi"):
            citation += f"doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Harvard"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"({author}, {metadata.get('year', '')})"
            elif len(metadata["authors"]) == 2:
                author1 = metadata["authors"][0].split(",")[0]
                author2 = metadata["authors"][1].split(",")[0]
                return f"({author1} and {author2}, {metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"({author} et al., {metadata.get('year', '')})"
        else:
            return f"(Anonymous, {metadata.get('year', '')})"

class VancouverFormatter(BaseCitationFormatter):
    """Format citations in Vancouver style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Vancouver-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] for name in first_name.split()])
                    formatted_authors.append(f"{last_name} {initials}")
                else:
                    formatted_authors.append(author)
            
            if len(formatted_authors) > 6:
                authors = " ".join(formatted_authors[:6]) + ", et al."
            else:
                authors = " ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}. "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}"
            
        if metadata.get("volume"):
            citation += f";{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')})"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Vancouver (numbered)"""
        # Vancouver typically uses a numbered reference system
        # This is a placeholder since we don't track reference numbers
        return "(N)"

class BMCFormatter(BaseCitationFormatter):
    """Format citations in BMC style (BioMed Central)"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a BMC-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 30:
                authors = ", ".join(metadata["authors"][:30]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}: {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}"
            
        if metadata.get("volume"):
            citation += f", {metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')})"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for BMC"""
        if metadata.get("authors"):
            first_author = metadata["authors"][0].split(",")[0]
            if len(metadata["authors"]) > 1:
                return f"{first_author} et al. [{metadata.get('year', '')}]"
            else:
                return f"{first_author} [{metadata.get('year', '')}]"
        else:
            return f"Anonymous [{metadata.get('year', '')}]"

class PLOSFormatter(BaseCitationFormatter):
    """Format citations in PLOS style (Public Library of Science)"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a PLOS-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 10:
                authors = ", ".join(metadata["authors"][:10]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} "
        
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}) "
            
        citation += f"{metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')}): "
        else:
            citation += ": "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}. "
        else:
            citation += ". "
        
        if metadata.get("doi"):
            citation += f"https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for PLOS"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}, {metadata.get('year', '')}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al., {metadata.get('year', '')}"
        else:
            return f"Anonymous, {metadata.get('year', '')}"

class CellFormatter(BaseCitationFormatter):
    """Format citations in Cell style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a Cell-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] + "." for name in first_name.split()])
                    formatted_authors.append(f"{last_name}, {initials}")
                else:
                    formatted_authors.append(author)
            
            authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} "
        
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')}). "
            
        citation += f"{metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}. "
        else:
            citation += ". "
        
        if metadata.get("doi"):
            citation += f"https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Cell"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"({author}, {metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"({author} et al., {metadata.get('year', '')})"
        else:
            return f"(Anonymous, {metadata.get('year', '')})"
        
class JAMAFormatter(BaseCitationFormatter):
    """Format citations in JAMA (Journal of the American Medical Association) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a JAMA-style citation"""
        # Format authors - JAMA uses et al after 6 authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 6:
                authors = ", ".join(metadata["authors"][:6]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}. "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}"
            
        if metadata.get("volume"):
            citation += f";{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')})"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi:{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for JAMA"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}"
            elif len(metadata["authors"]) == 2:
                author1 = metadata["authors"][0].split(",")[0]
                author2 = metadata["authors"][1].split(",")[0]
                return f"{author1} and {author2}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al"
        else:
            return "Anonymous"

class BMJFormatter(BaseCitationFormatter):
    """Format citations in BMJ (British Medical Journal) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a BMJ-style citation"""
        # Format authors - BMJ uses et al after 6 authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 6:
                authors = ", ".join(metadata["authors"][:6]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}"
            
        if metadata.get("volume"):
            citation += f";{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')})"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for BMJ"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al"
        else:
            return "Anonymous"

class NEJMFormatter(BaseCitationFormatter):
    """Format citations in NEJM (New England Journal of Medicine) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a NEJM-style citation"""
        # Format authors - NEJM lists all authors
        if metadata.get("authors"):
            authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}"
            
        if metadata.get("volume"):
            citation += f";{metadata.get('volume', '')}"
            
        if metadata.get("pages"):
            citation += f":{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" DOI: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for NEJM"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al."
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al."
        else:
            return "Anonymous"

class JBCFormatter(BaseCitationFormatter):
    """Format citations in JBC (Journal of Biological Chemistry) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a JBC-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] + "." for name in first_name.split()])
                    formatted_authors.append(f"{last_name}, {initials}")
                else:
                    formatted_authors.append(author)
            
            authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} ({metadata.get('year', '')}) {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for JBC"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} ({metadata.get('year', '')})"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al. ({metadata.get('year', '')})"
        else:
            return f"Anonymous ({metadata.get('year', '')})"

class ACMFormatter(BaseCitationFormatter):
    """Format citations in ACM (Association for Computing Machinery) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an ACM-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = " ".join([name[0] + "." for name in first_name.split()])
                    formatted_authors.append(f"{first_name[0]}. {last_name}")
                else:
                    formatted_authors.append(author)
            
            authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}. {metadata.get('year', '')}. {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("issue"):
            citation += f"{metadata.get('issue', '')} "
            
        if metadata.get("pages"):
            citation += f"({metadata.get('year', '')}), {metadata.get('pages', '')}. "
        else:
            citation += f"({metadata.get('year', '')}). "
        
        if metadata.get("doi"):
            citation += f"https://doi.org/{metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for ACM"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"[{author} {metadata.get('year', '')}]"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"[{author} et al. {metadata.get('year', '')}]"
        else:
            return f"[Anonymous {metadata.get('year', '')}]"

class OxfordFormatter(BaseCitationFormatter):
    """Format citations in Oxford style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into Oxford-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    formatted_authors.append(f"{last_name}, {first_name[0]}.")
                else:
                    formatted_authors.append(author)
            
            if len(formatted_authors) > 4:
                authors = ", ".join(formatted_authors[:4]) + ", et al."
            else:
                authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}, '{metadata.get('title', '')}', "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}, "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"/{metadata.get('issue', '')}"
            
        citation += f" ({metadata.get('year', '')}), "
            
        if metadata.get("pages"):
            citation += f"pp. {metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for Oxford"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}, {metadata.get('year', '')}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al., {metadata.get('year', '')}"
        else:
            return f"Anonymous, {metadata.get('year', '')}"

class RSCFormatter(BaseCitationFormatter):
    """Format citations in RSC (Royal Society of Chemistry) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an RSC-style citation"""
        # Format authors
        if metadata.get("authors"):
            if len(metadata["authors"]) > 30:
                authors = ", ".join(metadata["authors"][:30]) + ", et al."
            else:
                authors = ", ".join(metadata["authors"])
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}, {metadata.get('title', '')}, "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')}, "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}, "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" DOI: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for RSC"""
        return f"{metadata.get('journal', '')} {metadata.get('year', '')}"

class ACSFormatter(BaseCitationFormatter):
    """Format citations in ACS (American Chemical Society) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an ACS-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials
                    initials = "".join([name[0] + "." for name in first_name.split()]) 
                    formatted_authors.append(f"{last_name}, {initials}")
                else:
                    formatted_authors.append(author)
            
            authors = "; ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors} {metadata.get('title', '')}. "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("year"):
            citation += f"{metadata.get('year', '')}, "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}"
            
        if metadata.get("issue"):
            citation += f"({metadata.get('issue', '')}), "
        else:
            citation += ", "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')}"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" DOI: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for ACS"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}, {metadata.get('year', '')}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al., {metadata.get('year', '')}"
        else:
            return f"Anonymous, {metadata.get('year', '')}"

class AIPFormatter(BaseCitationFormatter):
    """Format citations in AIP (American Institute of Physics) style"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into an AIP-style citation"""
        # Format authors
        if metadata.get("authors"):
            formatted_authors = []
            for author in metadata["authors"]:
                parts = author.split(",")
                if len(parts) == 2:
                    last_name = parts[0].strip()
                    first_name = parts[1].strip()
                    # Get initials with spaces
                    initials = " ".join([name[0] + "." for name in first_name.split()]) 
                    formatted_authors.append(f"{first_name[0]}. {last_name}")
                else:
                    formatted_authors.append(author)
            
            authors = ", ".join(formatted_authors)
        else:
            authors = "Anonymous"
        
        # Build the citation
        citation = f"{authors}, \"{metadata.get('title', '')},\" "
        
        if metadata.get("journal"):
            citation += f"{metadata.get('journal', '')} "
            
        if metadata.get("volume"):
            citation += f"{metadata.get('volume', '')}, "
            
        if metadata.get("pages"):
            citation += f"{metadata.get('pages', '')} "
            
        if metadata.get("year"):
            citation += f"({metadata.get('year', '')})"
            
        citation += "."
        
        if metadata.get("doi"):
            citation += f" doi: {metadata.get('doi', '')}"
        
        return citation
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation for AIP"""
        if metadata.get("authors"):
            if len(metadata["authors"]) == 1:
                author = metadata["authors"][0].split(",")[0]
                return f"{author}, {metadata.get('year', '')}"
            else:
                author = metadata["authors"][0].split(",")[0]
                return f"{author} et al., {metadata.get('year', '')}"
        else:
            return f"Anonymous, {metadata.get('year', '')}"