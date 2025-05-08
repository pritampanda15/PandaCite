from .base import BaseCitationFormatter
from .basic import APAFormatter, ChicagoFormatter, MLAFormatter, HarvardFormatter
from .scientific import ElsevierFormatter, SpringerFormatter, NatureFormatter, ScienceFormatter, IEEEFormatter, RSCFormatter, ACSFormatter, AIPFormatter, CellFormatter, ACMFormatter, OxfordFormatter, JAMAFormatter, BMJFormatter, NEJMFormatter, VancouverFormatter, JBCFormatter, BMCFormatter, PLOSFormatter

# Create a dictionary of all formatters for easy access
FORMATTERS = {
    "elsevier": ElsevierFormatter(),
    "springer": SpringerFormatter(),
    "apa": APAFormatter(),
    "nature": NatureFormatter(),
    "science": ScienceFormatter(),
    "ieee": IEEEFormatter(),
    "chicago": ChicagoFormatter(),
    "mla": MLAFormatter(),
    "harvard": HarvardFormatter(),
    "vancouver": VancouverFormatter(),
    "bmc": BMCFormatter(),
    "plos": PLOSFormatter(),
    "cell": CellFormatter(),
    "jama": JAMAFormatter(),
    "bmj": BMJFormatter(),
    "nejm": NEJMFormatter(),
    "jbc": JBCFormatter(),
    "rsc": RSCFormatter(),
    "acs": ACSFormatter(),
    "aip": AIPFormatter(),
    "acm": ACMFormatter(),
    "oxford": OxfordFormatter()
}