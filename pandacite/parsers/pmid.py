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

class PMIDParser:
    """Parse PMID to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Parse a PMID and return metadata"""
        return self.extractor.extract_from_pmid(pmid)