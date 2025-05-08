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


class EnhancedMetadataExtractor:
    """Enhanced metadata extractor with support for more sources"""
    
    def __init__(self):
        self.api_keys = {
            "scopus": "",  # Add your Scopus API key here if available
            "semantic_scholar": "",  # Add your Semantic Scholar API key here if available
        }
    
    def extract_from_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a DOI using the Crossref API"""
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "message" in data:
                return self._parse_crossref_data(data["message"])
            
            # If Crossref fails, try DataCite
            return self._try_datacite_doi(doi)
        except Exception as e:
            print(f"Error extracting metadata from Crossref DOI {doi}: {e}")
            # Try DataCite as a fallback
            return self._try_datacite_doi(doi)
    
    def _try_datacite_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Try to get metadata from DataCite API"""
        url = f"https://api.datacite.org/dois/{doi}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and "attributes" in data["data"]:
                return self._parse_datacite_data(data["data"]["attributes"])
            return None
        except Exception as e:
            print(f"Error extracting metadata from DataCite DOI {doi}: {e}")
            return None
    
    def extract_from_pmid(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a PMID using the NCBI E-utilities API"""
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "json"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "result" in data and pmid in data["result"]:
                return self._parse_pubmed_data(data["result"][pmid])
            return None
        except Exception as e:
            print(f"Error extracting metadata from PMID {pmid}: {e}")
            return None
    
    def extract_from_arxiv(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from an arXiv ID using the arXiv API"""
        # Clean the arXiv ID (remove version if present)
        if "v" in arxiv_id:
            arxiv_id = arxiv_id.split("v")[0]
        
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML response
            root = ET.fromstring(response.content)
            
            # Find the entry element
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entry = root.find(".//atom:entry", ns)
            
            if entry is not None:
                return self._parse_arxiv_entry(entry, ns)
            return None
        except Exception as e:
            print(f"Error extracting metadata from arXiv ID {arxiv_id}: {e}")
            return None
    
    def extract_from_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from an ISBN using the Open Library API"""
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            key = f"ISBN:{isbn}"
            if key in data:
                return self._parse_openlibrary_data(data[key])
            return None
        except Exception as e:
            print(f"Error extracting metadata from ISBN {isbn}: {e}")
            return None
    
    # Update the extract_from_url method in the EnhancedMetadataExtractor class

    def extract_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a URL"""
        # Direct Science.org DOI extraction - no HTTP request needed
        if "science.org/doi/" in url or "sciencemag.org/doi/" in url:
            # Pattern to extract DOI directly from Science URLs
            doi_pattern = r'(?:science\.org|sciencemag\.org)/doi/(?:abs/|full/|pdf/|)?(10\.\d{4,9}/[^/\s?#]+)'
            doi_match = re.search(doi_pattern, url)
            
            if doi_match:
                doi = doi_match.group(1)
                print(f"Directly extracted DOI {doi} from Science.org URL without making a request")
                return self.extract_from_doi(doi)
            
            # Alternative: simpler pattern as fallback
            doi_match = re.search(r'10\.\d{4,9}/[^/\s?#]+', url)
            if doi_match:
                doi = doi_match.group(0)
                print(f"Extracted DOI {doi} from URL using simple pattern")
                return self.extract_from_doi(doi)
        
        # Check if it's a PMC URL
        if "pmc.ncbi.nlm.nih.gov/articles/PMC" in url:
            # Extract PMC ID
            pmc_match = re.search(r'PMC(\d+)', url)
            if pmc_match:
                pmc_id = pmc_match.group(1)
                # Try to convert PMC ID to PMID using NCBI's eutils
                try:
                    convert_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=PMC{pmc_id}[pmcid]&retmode=json"
                    response = requests.get(
                        convert_url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
                    )
                    data = response.json()
                    if "esearchresult" in data and "idlist" in data["esearchresult"] and data["esearchresult"]["idlist"]:
                        pmid = data["esearchresult"]["idlist"][0]
                        return self.extract_from_pmid(pmid)
                except Exception as e:
                    print(f"Error converting PMC{pmc_id} to PMID: {e}")
                    # Try direct extraction with proper headers
                    return self._extract_from_generic_url_with_headers(url)
        
        # Check if it's a known publisher URL
        if "nature.com" in url:
            return self._extract_from_nature_url(url)
        elif "science.org" in url:
            # For Science.org URLs, try to use more robust browser headers
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.google.com/",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0"
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                # Use BeautifulSoup to parse if available
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    metadata = {
                        "title": "",
                        "authors": [],
                        "journal": "Science",
                        "year": "",
                        "url": url
                    }
                    
                    # Extract title
                    title_tag = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "citation_title"})
                    if title_tag:
                        metadata["title"] = title_tag.get("content", "")
                    else:
                        title_tag = soup.find("title")
                        if title_tag:
                            metadata["title"] = title_tag.text
                    
                    # Extract authors
                    author_tags = soup.find_all("meta", attrs={"name": "citation_author"})
                    if author_tags:
                        metadata["authors"] = [tag.get("content", "") for tag in author_tags]
                    else:
                        # Try alternative method
                        author_elements = soup.select(".contrib-author")
                        if author_elements:
                            metadata["authors"] = [author.text.strip() for author in author_elements]
                    
                    # Extract date/year
                    date_tag = soup.find("meta", attrs={"name": "citation_publication_date"})
                    if date_tag:
                        date_content = date_tag.get("content", "")
                        if date_content and len(date_content) >= 4:
                            metadata["year"] = date_content[:4]
                    
                    # Extract DOI
                    doi_tag = soup.find("meta", attrs={"name": "citation_doi"})
                    if doi_tag:
                        metadata["doi"] = doi_tag.get("content", "")
                    
                    return metadata
                except ImportError:
                    print("BeautifulSoup not available, trying DOI extraction")
                    # Fall back to DOI extraction
                    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.IGNORECASE)
                    if doi_match:
                        doi = doi_match.group(0)
                        return self.extract_from_doi(doi)
                    
            except Exception as e:
                print(f"Error processing Science.org URL: {e}")
                # Try to extract DOI as a fallback
                doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.IGNORECASE)
                if doi_match:
                    doi = doi_match.group(0)
                    print(f"Falling back to DOI extraction: {doi}")
                    return self.extract_from_doi(doi)
                return None
                
        elif "pubmed.ncbi.nlm.nih.gov" in url:
            # Extract PMID from PubMed URL
            pmid = url.split("/")[-1].split("?")[0]
            return self.extract_from_pmid(pmid)
        elif "doi.org" in url:
            # Extract DOI from DOI URL
            doi = url.split("doi.org/")[-1]
            return self.extract_from_doi(doi)
        elif "arxiv.org" in url:
            # Extract arXiv ID from arXiv URL
            if "abs" in url:
                arxiv_id = url.split("abs/")[-1].split("v")[0]
                return self.extract_from_arxiv(arxiv_id)
        
        # Generic URL handling - use web scraping with meta tags
        return self._extract_from_generic_url_with_headers(url)

    def _extract_from_generic_url_with_headers(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a generic URL using meta tags with proper headers"""
        try:
            # Use a more browser-like User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/",
                "DNT": "1"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Check for DOI in the URL or page content
            doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.IGNORECASE)
            if not doi_match:
                doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', response.text, re.IGNORECASE)
            
            if doi_match:
                doi = doi_match.group(0)
                print(f"Found DOI in URL/content: {doi}, trying DOI extraction")
                doi_metadata = self.extract_from_doi(doi)
                if doi_metadata:
                    return doi_metadata
            
            # Use BeautifulSoup to parse HTML if available
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                metadata = {
                    "title": "",
                    "authors": [],
                    "journal": "",
                    "year": "",
                    "url": url
                }
                
                # Extract title
                title_tag = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "citation_title"})
                if title_tag:
                    metadata["title"] = title_tag.get("content", "")
                else:
                    title_tag = soup.find("title")
                    if title_tag:
                        metadata["title"] = title_tag.text
                
                # Extract authors
                author_tags = soup.find_all("meta", attrs={"name": "citation_author"})
                if author_tags:
                    metadata["authors"] = [tag.get("content", "") for tag in author_tags]
                
                # Extract journal
                journal_tag = soup.find("meta", attrs={"name": "citation_journal_title"})
                if journal_tag:
                    metadata["journal"] = journal_tag.get("content", "")
                
                # Extract year
                date_tag = soup.find("meta", attrs={"name": "citation_publication_date"})
                if date_tag:
                    date_content = date_tag.get("content", "")
                    if date_content and len(date_content) >= 4:
                        metadata["year"] = date_content[:4]
                
                # Extract DOI
                doi_tag = soup.find("meta", attrs={"name": "citation_doi"})
                if doi_tag:
                    metadata["doi"] = doi_tag.get("content", "")
                
                return metadata
            except ImportError:
                # If BeautifulSoup is not available, use a simpler approach
                print("BeautifulSoup not available, using simple extraction")
                metadata = {
                    "title": "",
                    "authors": [],
                    "url": url
                }
                
                # Simple title extraction
                title_match = re.search(r"<title>(.*?)</title>", response.text)
                if title_match:
                    metadata["title"] = title_match.group(1)
                
                return metadata
        except Exception as e:
            print(f"Error extracting metadata from URL {url}: {e}")
            # Last resort: Try to find a DOI and use that
            doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', url, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(0)
                print(f"Last resort: Trying DOI extraction from URL pattern: {doi}")
                return self.extract_from_doi(doi)
            return None
    
    def _extract_from_generic_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a generic URL using meta tags"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Use BeautifulSoup to parse HTML if available
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                metadata = {
                    "title": "",
                    "authors": [],
                    "journal": "",
                    "year": "",
                    "url": url
                }
                
                # Extract title
                title_tag = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "citation_title"})
                if title_tag:
                    metadata["title"] = title_tag.get("content", "")
                else:
                    title_tag = soup.find("title")
                    if title_tag:
                        metadata["title"] = title_tag.text
                
                # Extract authors
                author_tags = soup.find_all("meta", attrs={"name": "citation_author"})
                if author_tags:
                    metadata["authors"] = [tag.get("content", "") for tag in author_tags]
                
                # Extract journal
                journal_tag = soup.find("meta", attrs={"name": "citation_journal_title"})
                if journal_tag:
                    metadata["journal"] = journal_tag.get("content", "")
                
                # Extract year
                date_tag = soup.find("meta", attrs={"name": "citation_publication_date"})
                if date_tag:
                    date_content = date_tag.get("content", "")
                    if date_content and len(date_content) >= 4:
                        metadata["year"] = date_content[:4]
                
                # Extract DOI
                doi_tag = soup.find("meta", attrs={"name": "citation_doi"})
                if doi_tag:
                    metadata["doi"] = doi_tag.get("content", "")
                
                return metadata
            except ImportError:
                # If BeautifulSoup is not available, use a simpler approach
                print("BeautifulSoup not available, using simple extraction")
                metadata = {
                    "title": "",
                    "authors": [],
                    "url": url
                }
                
                # Simple title extraction
                title_match = re.search(r"<title>(.*?)</title>", response.text)
                if title_match:
                    metadata["title"] = title_match.group(1)
                
                return metadata
        except Exception as e:
            print(f"Error extracting metadata from URL {url}: {e}")
            return None
    
    def _extract_from_nature_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a Nature URL"""
        # This would implement specific logic for Nature articles
        # For now, use the generic URL extractor
        return self._extract_from_generic_url_with_headers(url)

    
    def _extract_from_science_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a Science URL"""
        # This would implement specific logic for Science articles
        # For now, use the generic URL extractor
        return self._extract_from_generic_url_with_headers(url)
    
    def _parse_crossref_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Crossref API response into standardized metadata format"""
        metadata = {
            "title": data.get("title", [""])[0] if isinstance(data.get("title", []), list) else data.get("title", ""),
            "authors": [],
            "journal": data.get("container-title", [""])[0] if isinstance(data.get("container-title", []), list) else "",
            "year": str(data.get("published", {}).get("date-parts", [[""]])[0][0]) if "published" in data else "",
            "volume": data.get("volume", ""),
            "issue": data.get("issue", ""),
            "pages": data.get("page", ""),
            "doi": data.get("DOI", ""),
            "url": data.get("URL", ""),
            "publisher": data.get("publisher", ""),
            "type": data.get("type", ""),
        }
        
        # Extract authors
        if "author" in data and isinstance(data["author"], list):
            for author in data["author"]:
                name = ""
                if "family" in author and "given" in author:
                    name = f"{author['family']}, {author['given']}"
                elif "name" in author:
                    name = author["name"]
                
                if name:
                    metadata["authors"].append(name)
        
        # Extract abstract if available
        if "abstract" in data:
            metadata["abstract"] = data["abstract"]
        
        # Extract keywords if available
        if "subject" in data and isinstance(data["subject"], list):
            metadata["keywords"] = data["subject"]
        
        return metadata
    
    def _parse_datacite_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse DataCite API response into standardized metadata format"""
        metadata = {
            "title": data.get("title", ""),
            "authors": [],
            "year": data.get("publicationYear", ""),
            "doi": data.get("doi", ""),
            "url": f"https://doi.org/{data.get('doi', '')}",
            "publisher": data.get("publisher", ""),
            "type": data.get("resourceType", {}).get("resourceTypeGeneral", ""),
        }
        
        # Extract authors
        if "creators" in data and isinstance(data["creators"], list):
            for creator in data["creators"]:
                if "name" in creator:
                    metadata["authors"].append(creator["name"])
        
        # Extract journal/container title if available
        if "container" in data and "title" in data["container"]:
            metadata["journal"] = data["container"]["title"]
        
        # Extract volume, issue, pages if available
        if "relatedIdentifiers" in data:
            for identifier in data["relatedIdentifiers"]:
                if identifier.get("relationType") == "IsPartOf":
                    parts = identifier.get("relatedIdentifier", "").split(":")
                    if len(parts) > 1:
                        if "volume" in parts[0].lower():
                            metadata["volume"] = parts[1]
                        elif "issue" in parts[0].lower():
                            metadata["issue"] = parts[1]
                        elif "page" in parts[0].lower():
                            metadata["pages"] = parts[1]
        
        return metadata
    
    def _parse_pubmed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse PubMed API response into standardized metadata format"""
        metadata = {
            "title": data.get("title", ""),
            "authors": [],
            "journal": data.get("fulljournalname", "") or data.get("source", ""),
            "year": data.get("pubdate", "").split()[0] if data.get("pubdate", "") else "",
            "volume": data.get("volume", ""),
            "issue": data.get("issue", ""),
            "pages": data.get("pages", ""),
            "doi": next((id_data.get("value", "") for id_data in data.get("articleids", []) 
                         if id_data.get("idtype", "") == "doi"), ""),
            "pmid": next((id_data.get("value", "") for id_data in data.get("articleids", []) 
                         if id_data.get("idtype", "") == "pubmed"), ""),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{data.get('uid', '')}/" if data.get('uid', '') else "",
            "publisher": data.get("publishername", ""),
            "type": "journal-article",
        }
        
        # Extract authors
        if "authors" in data and isinstance(data["authors"], list):
            for author in data["authors"]:
                if "name" in author:
                    metadata["authors"].append(author["name"])
        
        # Extract abstract if available
        if "bookabstract" in data and data["bookabstract"]:
            metadata["abstract"] = data["bookabstract"]
        
        # Extract keywords if available
        if "keywords" in data and isinstance(data["keywords"], list):
            metadata["keywords"] = data["keywords"]
        
        return metadata
    
    def _parse_arxiv_entry(self, entry, ns: Dict[str, str]) -> Dict[str, Any]:
        """Parse arXiv API entry into standardized metadata format"""
        # Get the title
        title_element = entry.find("atom:title", ns)
        title = title_element.text if title_element is not None else ""
        
        # Get the authors
        authors = []
        for author_element in entry.findall("atom:author/atom:name", ns):
            # Convert author name to "Last, First" format
            name_parts = author_element.text.split()
            if len(name_parts) > 1:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])
                authors.append(f"{last_name}, {first_name}")
            else:
                authors.append(author_element.text)
        
        # Get the publication date
        date_element = entry.find("atom:published", ns)
        year = date_element.text[:4] if date_element is not None else ""
        
        # Get the DOI if available
        doi = ""
        for link_element in entry.findall("atom:link", ns):
            if link_element.get("title") == "doi":
                doi_url = link_element.get("href", "")
                if "doi.org/" in doi_url:
                    doi = doi_url.split("doi.org/")[-1]
        
        # Get the abstract
        summary_element = entry.find("atom:summary", ns)
        abstract = summary_element.text if summary_element is not None else ""
        
        # Get the URL
        url = ""
        for link_element in entry.findall("atom:link", ns):
            if link_element.get("rel") == "alternate":
                url = link_element.get("href", "")
        
        # Get the arXiv ID
        id_element = entry.find("atom:id", ns)
        arxiv_id = id_element.text.split("/")[-1] if id_element is not None else ""
        
        # Get the categories (subjects)
        categories = []
        for category_element in entry.findall("atom:category", ns):
            term = category_element.get("term")
            if term:
                categories.append(term)
        
        metadata = {
            "title": title,
            "authors": authors,
            "journal": "arXiv",
            "year": year,
            "doi": doi,
            "url": url,
            "arxiv_id": arxiv_id,
            "abstract": abstract,
            "type": "preprint",
            "keywords": categories
        }
        
        return metadata
    
    def _parse_openlibrary_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Open Library API response into standardized metadata format"""
        metadata = {
            "title": data.get("title", ""),
            "authors": [],
            "year": "",
            "publisher": "",
            "isbn": "",
            "url": data.get("url", ""),
            "type": "book",
        }
        
        # Extract authors
        if "authors" in data and isinstance(data["authors"], list):
            for author in data["authors"]:
                if "name" in author:
                    metadata["authors"].append(author["name"])
        
        # Extract publication year
        if "publish_date" in data:
            publish_date = data["publish_date"]
            # Extract year from the publish date
            year_match = re.search(r"\d{4}", publish_date)
            if year_match:
                metadata["year"] = year_match.group(0)
        
        # Extract publisher
        if "publishers" in data and isinstance(data["publishers"], list) and len(data["publishers"]) > 0:
            metadata["publisher"] = data["publishers"][0].get("name", "")
        
        # Extract ISBN
        if "identifiers" in data and "isbn_13" in data["identifiers"]:
            metadata["isbn"] = data["identifiers"]["isbn_13"][0]
        elif "identifiers" in data and "isbn_10" in data["identifiers"]:
            metadata["isbn"] = data["identifiers"]["isbn_10"][0]
        
        return metadata