# ===== Parser Classes =====

class DOIParser:
    """Parse DOI to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, doi: str) -> Optional[Dict[str, Any]]:
        """Parse a DOI and return metadata"""
        return self.extractor.extract_from_doi(doi)