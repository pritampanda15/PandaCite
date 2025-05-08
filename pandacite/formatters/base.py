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

class BaseCitationFormatter:
    """Base class for citation formatters"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a citation string"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation"""
        raise NotImplementedError("Subclasses must implement this method")