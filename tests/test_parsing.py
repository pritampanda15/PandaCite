"""Offline tests: ID detection, normalization and BibTeX/RIS parsing."""
import pytest

from pandacite.extractors.detector import IDDetector
from pandacite.extractors.metadata import normalize_arxiv_id, normalize_doi
from pandacite.parsers import BibTexParser, RISParser


@pytest.mark.parametrize("identifier, expected", [
    ("10.1038/nature12373", "doi"),
    ("https://doi.org/10.1038/nature12373", "doi"),
    ("doi:10.1038/nature12373", "doi"),
    ("12345678", "pmid"),
    ("PMID: 12345678", "pmid"),
    ("arXiv:2101.00001", "arxiv"),
    ("2101.00001v2", "arxiv"),
    ("9780306406157", "isbn"),
    ("https://example.com/paper", "url"),
    ("www.example.com", "url"),
    ("@article{k, title={T}}", "bibtex"),
    ("TY  - JOUR\nER  -", "ris"),
    ("hello", "unknown"),
])
def test_detect_id_type(identifier, expected):
    assert IDDetector().detect_id_type(identifier) == expected


@pytest.mark.parametrize("raw, expected", [
    ("arXiv:2101.00001", "2101.00001"),
    ("arXiv:2101.00001v3", "2101.00001"),
    ("2101.00001v2", "2101.00001"),
    ("solv-int/9901001", "solv-int/9901001"),
])
def test_normalize_arxiv_id(raw, expected):
    assert normalize_arxiv_id(raw) == expected


@pytest.mark.parametrize("raw", [
    "10.1038/x", "https://doi.org/10.1038/x", "http://dx.doi.org/10.1038/x", "doi: 10.1038/x",
])
def test_normalize_doi(raw):
    assert normalize_doi(raw) == "10.1038/x"


def test_bibtex_nested_braces_and_bare_values():
    entry = """@article{smith2020,
      author = {John Smith and Doe, Jane},
      title = {The {DNA} Story},
      journal = "Nature",
      year = 2020,
      url = {https://x.org/?a=b},
      pages = {1--10}
    }"""
    md = BibTexParser().parse(entry)
    assert md["title"] == "The DNA Story"
    assert md["journal"] == "Nature"
    assert md["year"] == "2020"
    assert md["url"] == "https://x.org/?a=b"
    assert md["pages"] == "1--10"
    assert md["authors"] == ["Smith, John", "Doe, Jane"]


def test_ris_page_range_any_order():
    ris = "TY  - JOUR\nEP  - 20\nSP  - 10\nTI  - T\nPY  - 2020///\nER  - "
    md = RISParser().parse(ris)
    assert md["pages"] == "10-20"
    assert md["year"] == "2020"
