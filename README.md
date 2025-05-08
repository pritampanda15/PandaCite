<div align="center">
    <img src="https://raw.githubusercontent.com/pritampanda15/pandacite/main/logo/pandacite.png" width="500" alt="PandaCite Logo" />
  <p><em>A Python-based citation manager for researchers & writers </em></p>

  <!-- Badges -->
<p align="center">
  <a href="https://pypi.org/project/pandacite/">
    <img src="https://img.shields.io/pypi/v/pandacite.svg" alt="PyPI Version">
  </a>
  <a href="https://github.com/pritampanda15/PandaCite/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/pritampanda15/PandaCite" alt="License">
  </a>
  <a href="https://github.com/pritampanda15/PandaCite/stargazers">
    <img src="https://img.shields.io/github/stars/pritampanda15/PandaCite?style=social" alt="GitHub Stars">
  </a>
  <a href="https://github.com/pritampanda15/PandaCite/issues">
    <img src="https://img.shields.io/github/issues/pritampanda15/PandaCite" alt="GitHub Issues">
  </a>
  <a href="https://github.com/pritampanda15/PandaCite/network/members">
    <img src="https://img.shields.io/github/forks/pritampanda15/PandaCite?style=social" alt="GitHub Forks">
  </a>
  <a href="https://pepy.tech/project/pandacite">
    <img src="https://static.pepy.tech/badge/pandacite" alt="Downloads">
  </a>
</p>
</div>
---

## 🚀 Features

- 🔍 Generate citations from `DOI`, `PMID`, `arXiv`, `ISBN`, `URLs`, and more
- 🖋 Supports **20+ popular citation styles**: APA, Nature, Science, IEEE, Chicago, etc.
- 📄 Automatically process and update citations in Microsoft Word documents (`.docx`)
- 🔢 Full support for **numbered** and **author-year** styles
- 🧠 Interactive CLI & programmable Python API

---

## 📦 Installation

```bash
pip install pandacite
````

---

## 💻 Command Line Usage

### ➤ Generate a single citation

```bash
pandacite single --id "https://doi.org/10.1126/sciadv.abb8097" --format nature
```

### ➤ Process citations in a Word document

```bash
pandacite word --input manuscript.docx --output manuscript_with_citations.docx --format ieee
```

### ➤ Interactive Mode

```bash
pandacite interactive
```

<details>
<summary>📘 CLI Help</summary>

```bash
usage: pandacite [-h] {single,batch,word,interactive} ...

positional arguments:
  {single,batch,word,interactive}
    single        Generate a single citation
    batch         Process multiple citations
    word          Process Word documents
    interactive   Run in interactive mode

optional arguments:
  -h, --help      Show this help message and exit
```

</details>

---

## 🧬 Python API

```python
from pandacite import EnhancedCitationManager

# Create citation manager instance
manager = EnhancedCitationManager()

# Generate a citation
citation = manager.process_single_citation("doi", "10.1038/s41586-020-2649-2", "nature")
print(citation)
```

---

## 🎨 Supported Citation Styles

```python
from pandacite.formatters import (
    APAFormatter, NatureFormatter, ScienceFormatter, IEEEFormatter, 
    ChicagoFormatter, MLAFormatter, HarvardFormatter, VancouverFormatter,
    ElsevierFormatter, SpringerFormatter, BMCFormatter, PLOSFormatter, 
    CellFormatter, JAMAFormatter, BMJFormatter, NEJMFormatter, 
    JBCFormatter, RSCFormatter, ACSFormatter, AIPFormatter, 
    ACMFormatter, OxfordFormatter
)
```

---

## 📥 Supported Parsers

```python
from pandacite.parsers import (
    DOIParser, PMIDParser, ArXivParser, ISBNParser, 
    URLParser, BibTexParser, RISParser
)
```

---

## 🧠 Interactive Demo

A guided command-line session to generate citations with autocompletion and help built-in.

```bash
pandacite interactive
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <em>Built for researchers, writers, and academics who deserve frictionless citations. 🐼</em>
</div>
