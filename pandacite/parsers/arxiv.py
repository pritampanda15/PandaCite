class ArXivParser:
    """Parse arXiv IDs to extract metadata"""
    
    def __init__(self, extractor):
        self.extractor = extractor
    
    def parse(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Parse an arXiv ID and return metadata"""
        return self.extractor.extract_from_arxiv(arxiv_id)