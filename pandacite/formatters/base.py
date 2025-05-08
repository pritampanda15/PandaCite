class BaseCitationFormatter:
    """Base class for citation formatters"""
    
    def format_citation(self, metadata: Dict[str, Any]) -> str:
        """Format metadata into a citation string"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_in_text_citation(self, metadata: Dict[str, Any]) -> str:
        """Format in-text citation"""
        raise NotImplementedError("Subclasses must implement this method")