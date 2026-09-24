"""Offline tests: extractor HTTP handling, manager, BibTeX export and Word processing."""
from unittest import mock

import pytest
from docx import Document

from pandacite import EnhancedCitationManager
from pandacite.extractors import metadata as md_module
from pandacite.extractors.detector import IDDetector
from pandacite.processors.numbered import NumberedCitationProcessor
from pandacite.processors.word import CommandLineWordProcessor

CROSSREF = {"message": {
    "title": ["A title"], "author": [{"family": "Smith", "given": "John"}],
    "container-title": ["Nature"], "issued": {"date-parts": [[2020, 1]]},
    "volume": "5", "page": "1-10", "DOI": "10.1038/x",
}}


def fake_response(json_data=None, content=b""):
    response = mock.Mock()
    response.json.return_value = json_data
    response.content = content
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def manager():
    return EnhancedCitationManager()


def test_requests_have_timeout_and_user_agent():
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(CROSSREF)) as get:
        md_module.EnhancedMetadataExtractor().extract_from_doi("10.1038/x")
    kwargs = get.call_args.kwargs
    assert kwargs["timeout"] == md_module.REQUEST_TIMEOUT
    assert "PandaCite" in kwargs["headers"]["User-Agent"]


def test_doi_url_is_normalized_and_year_falls_back_to_issued():
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(CROSSREF)) as get:
        metadata = md_module.EnhancedMetadataExtractor().extract_from_doi("https://doi.org/10.1038/x")
    assert get.call_args.args[0] == "https://api.crossref.org/works/10.1038/x"
    assert metadata["year"] == "2020"
    assert metadata["authors"] == ["Smith, John"]


def test_crossref_empty_title_list():
    data = {"message": dict(CROSSREF["message"], title=[])}
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(data)):
        metadata = md_module.EnhancedMetadataExtractor().extract_from_doi("10.1038/x")
    assert metadata["title"] == ""


def test_arxiv_prefix_is_not_mangled():
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(content=b"<feed/>")) as get:
        md_module.EnhancedMetadataExtractor().extract_from_arxiv("arXiv:2101.00001v2")
    assert get.call_args.args[0].endswith("id_list=2101.00001")


def test_pubmed_url_with_trailing_slash():
    extractor = md_module.EnhancedMetadataExtractor()
    with mock.patch.object(extractor, "extract_from_pmid", return_value={}) as pmid:
        extractor.extract_from_url("https://pubmed.ncbi.nlm.nih.gov/12345678/")
    pmid.assert_called_once_with("12345678")


def test_bibtex_export_keys_are_valid_and_unique(manager, tmp_path):
    entry = {"authors": ["van der Berg, Ann"], "year": "2020", "title": "T"}
    manager.citation_data = {"a": dict(entry), "b": dict(entry)}
    out = tmp_path / "refs.bib"
    assert manager.export_bibtex(str(out))
    text = out.read_text(encoding="utf-8")
    assert "@article{vanderBerg2020," in text
    assert "@article{vanderBerg2020a," in text


def test_export_citations_writes_unicode(manager, tmp_path):
    out = tmp_path / "refs.txt"
    assert manager.export_citations(["Smith J, pp. 1–10"], str(out))
    assert "–" in out.read_text(encoding="utf-8")


def test_word_scan_ignores_bare_numbers(manager):
    processor = CommandLineWordProcessor(manager)
    citations = {}
    processor._process_text_for_citations(
        "In 2020 we saw [1] and (Smith, 2019). See PMID: 12345 and 10.1038/x.",
        citations, IDDetector())
    direct = {c["id_value"] for c in citations.values() if c["pattern"] == "direct_id"}
    assert direct == {"12345", "10.1038/x"}


def test_numbered_citations_follow_text_order(manager):
    doc = Document()
    doc.add_paragraph("First B then A.")
    citations = {"a": {"source_text": "A", "metadata_key": "ka"},
                 "b": {"source_text": "B", "metadata_key": "kb"}}
    order = NumberedCitationProcessor(manager).process_document(doc, citations, {}, "ieee")
    assert order == {"kb": 1, "ka": 2}


def test_word_document_end_to_end(manager, tmp_path):
    src, out = tmp_path / "in.docx", tmp_path / "out.docx"
    doc = Document()
    doc.add_paragraph("As shown by 10.1038/x, pandas are great.")
    doc.save(src)

    processor = CommandLineWordProcessor(manager)
    document, citations = processor.process_document(str(src), "apa", IDDetector())
    metadata = {"doi-10.1038/x-metadata": {"authors": ["Smith, John"], "year": "2020",
                                           "title": "T", "journal": "J"}}
    for citation in citations.values():
        citation["metadata_key"] = "doi-10.1038/x-metadata"
    assert processor.update_document_with_citations(document, citations, metadata, "apa", str(out))
    text = "\n".join(p.text for p in Document(out).paragraphs)
    assert "10.1038/x" not in text.split("References")[0]
    assert "References" in text


def test_pubmed_authors_and_abbreviated_pages():
    data = {"uid": "1", "title": "T.", "pages": "54-8", "pubdate": "2013 Aug 1",
            "authors": [{"name": "Zhou XL"}, {"name": "van der Berg A"}, {"name": "COVID Consortium"}]}
    metadata = md_module.EnhancedMetadataExtractor()._parse_pubmed_data(data)
    assert metadata["authors"] == ["Zhou, X. L.", "van der Berg, A.", "COVID Consortium"]
    assert metadata["pages"] == "54-58"
    assert metadata["title"] == "T"


def test_arxiv_entry_gets_datacite_doi():
    feed = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <id>http://arxiv.org/abs/1706.03762v7</id><title>T</title>
        <published>2017-06-12T00:00:00Z</published></entry></feed>"""
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(content=feed)):
        metadata = md_module.EnhancedMetadataExtractor().extract_from_arxiv("1706.03762")
    assert metadata["doi"] == "10.48550/arXiv.1706.03762"


def test_parenthesised_ids_are_not_double_wrapped(manager):
    doc = Document()
    paragraph = doc.add_paragraph("Shown before (10.1/x).")
    citations = {"c": {"source_text": "10.1/x", "metadata_key": "k"}}
    CommandLineWordProcessor(manager)._update_paragraph_citations(
        paragraph, citations, {"k": {"in_text": "(Smith, 2020)"}})
    assert paragraph.text == "Shown before (Smith, 2020)."
    paragraph.text = "Shown before (10.1/x)."
    NumberedCitationProcessor(manager)._update_paragraph_with_numbers(paragraph, citations, {"k": 1})
    assert paragraph.text == "Shown before [1]."


def _add_hyperlink(paragraph, url, text):
    from docx.opc.constants import RELATIONSHIP_TYPE
    from docx.oxml.shared import OxmlElement, qn
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), paragraph.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True))
    run, t = OxmlElement("w:r"), OxmlElement("w:t")
    t.text = text
    run.append(t)
    link.append(run)
    paragraph._p.append(link)


def _add_field_hyperlink(paragraph, url, text):
    from docx.oxml.shared import OxmlElement, qn
    for kind, instr, result in (("begin", None, None), (None, f' HYPERLINK "{url}" ', None),
                                ("separate", None, None), (None, None, text), ("end", None, None)):
        run = OxmlElement("w:r")
        if kind:
            char = OxmlElement("w:fldChar")
            char.set(qn("w:fldCharType"), kind)
            run.append(char)
        else:
            node = OxmlElement("w:instrText" if instr else "w:t")
            node.text = instr or result
            run.append(node)
        paragraph._p.append(run)


def test_extract_hyperlinks_elements_and_field_codes():
    from pandacite.processors.word import extract_hyperlinks
    paragraph = Document().add_paragraph("Shown before (")
    _add_hyperlink(paragraph, "https://pubmed.ncbi.nlm.nih.gov/1/?utm_source=chatgpt.com", "Yip et al., 2013")
    paragraph.add_run("; ")
    _add_field_hyperlink(paragraph, "https://pubmed.ncbi.nlm.nih.gov/2/", "Jurd et al., 2003")
    paragraph.add_run(").")
    assert extract_hyperlinks(paragraph) == {
        "Yip et al., 2013": "https://pubmed.ncbi.nlm.nih.gov/1/",
        "Jurd et al., 2003": "https://pubmed.ncbi.nlm.nih.gov/2/",
    }


def test_author_year_groups_are_split_and_linked(manager):
    citations = {}
    CommandLineWordProcessor(manager)._process_text_for_citations(
        "Known (Yip et al., 2013;\xa0Panda and Bertaccini, 2026) but not (EC = 0.47 μM) or (see 2003).",
        citations, IDDetector(), {"Yip et al., 2013": "https://pubmed.ncbi.nlm.nih.gov/1/"})
    assert {k: c for k, c in citations.items() if c["pattern"] == "author_year"} == {
        "Yip et al.-2013": {"author": "Yip et al.", "year": "2013", "pattern": "author_year",
                            "source_text": "Yip et al., 2013", "id_type": "url",
                            "id_value": "https://pubmed.ncbi.nlm.nih.gov/1/"},
        "Panda and Bertaccini-2026": {"author": "Panda and Bertaccini", "year": "2026",
                                      "pattern": "author_year", "source_text": "Panda and Bertaccini, 2026"},
    }


def test_grouped_citations_render_per_style(manager):
    citations = {"a": {"pattern": "author_year", "source_text": "Yip et al., 2013", "metadata_key": "ka"},
                 "b": {"pattern": "author_year", "source_text": "Jurd, 2003", "metadata_key": "kb"}}
    paragraph = Document().add_paragraph("Known (Yip et al., 2013; Jurd, 2003).")
    CommandLineWordProcessor(manager)._update_paragraph_citations(
        paragraph, citations, {"ka": {"in_text": "(Yip et al., 2013)"}, "kb": {"in_text": "(Jurd, 2003)"}})
    assert paragraph.text == "Known (Yip et al., 2013; Jurd, 2003)."

    doc = Document()
    doc.add_paragraph("Known (Yip et al., 2013; Jurd, 2003).")
    processor = NumberedCitationProcessor(manager)
    numbers = processor.process_document(doc, citations, {}, "science")
    processor.format_in_text_citations(doc, citations, numbers)
    assert doc.paragraphs[0].text == "Known (1, 2)."


def test_compress_numbers():
    from pandacite.processors.numbered import compress_numbers
    assert compress_numbers([3, 1, 2, 5, 6, 9]) == "1–3, 5, 6, 9"


def test_ncbi_429_is_retried():
    limited = fake_response()
    limited.status_code, limited.headers = 429, {"Retry-After": "0"}
    ok = fake_response({"result": {"1": {"uid": "1", "title": "T"}}})
    ok.status_code = 200
    with mock.patch.object(md_module.requests, "get", side_effect=[limited, ok]) as get, \
         mock.patch.object(md_module.time, "sleep"):
        metadata = md_module.EnhancedMetadataExtractor().extract_from_pmid("1")
    assert get.call_count == 2
    assert metadata["title"] == "T"


def test_pubmed_name_suffix():
    assert md_module._pubmed_author("Walsh RM Jr") == "Walsh Jr., R. M."


def test_crossref_titles_are_cleaned():
    data = {"message": dict(CROSSREF["message"], title=["Alchemical Free\nEnergy of <i>GABA</i>"])}
    with mock.patch.object(md_module.requests, "get", return_value=fake_response(data)):
        metadata = md_module.EnhancedMetadataExtractor().extract_from_doi("10.1038/x")
    assert metadata["title"] == "Alchemical Free Energy of GABA"
