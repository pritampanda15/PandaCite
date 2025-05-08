class PMIDParser:
    """Parse PMID to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Parse a PMID and return metadata"""
        return self.extractor.extract_from_pmid(pmid)