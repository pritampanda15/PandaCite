"""Offline tests: every formatter handles full, sparse and odd metadata."""
import pytest

from pandacite.formatters import FORMATTERS

CASES = {
    "full": {"authors": ["Smith, John A.", "Doe, Jane"], "title": "A title", "journal": "Nature",
             "year": "2020", "volume": "5", "issue": "2", "pages": "1-10", "doi": "10.1/x"},
    "empty": {},
    "no_authors": {"authors": [], "title": "T", "year": "2020"},
    "mononym": {"authors": ["Aristotle"], "title": "T", "year": "2020"},
    # Shape of the placeholder metadata the CLI creates for unmatched citations
    "placeholder": {"authors": ["Smith, "], "title": "T", "year": "2020"},
    "many_authors": {"authors": [f"A{i}, B" for i in range(30)], "title": "T", "year": "2020"},
}


@pytest.mark.parametrize("style", sorted(FORMATTERS))
@pytest.mark.parametrize("case", sorted(CASES))
def test_formatter_does_not_crash(style, case):
    formatter = FORMATTERS[style]
    assert isinstance(formatter.format_citation(dict(CASES[case])), str)
    assert isinstance(formatter.format_in_text_citation(dict(CASES[case])), str)


@pytest.mark.parametrize("style", ["acm", "aip"])
def test_all_initials_kept(style):
    citation = FORMATTERS[style].format_citation(CASES["full"])
    assert "J. A. Smith" in citation
