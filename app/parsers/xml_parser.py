# =============================================================
# FICHIER VOLONTAIREMENT VULNERABLE — A DES FINS EDUCATIVES
# OWASP A05 — Security Misconfiguration
# XXE — XML External Entity Injection
# =============================================================

from xml.etree import ElementTree as ET
import lxml.etree as lxml_etree

# ---- XXE avec xml.etree ----
# Détecté par : Bandit (B314)
# CWE-611 : Improper Restriction of XML External Entity Reference
# Payload XXE classique :
# <?xml version="1.0"?>
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# <root>&xxe;</root>
def parse_xml_unsafe(xml_string: str) -> ET.Element:
    return ET.fromstring(xml_string)

# ---- XXE avec lxml sans protection ----
# Détecté par : Bandit (B320)
# lxml avec resolve_entities=True (défaut) → XXE possible
def parse_lxml_unsafe(xml_bytes: bytes) -> lxml_etree._Element:
    parser = lxml_etree.XMLParser(resolve_entities=True)
    return lxml_etree.fromstring(xml_bytes, parser)

# ---- Billion Laughs Attack ----
# CWE-776 : Improper Restriction of Recursive Entity References
# Payload qui explose la mémoire via entités imbriquées
BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<root>&lol3;</root>"""

def parse_billion_laughs() -> ET.Element:
    return ET.fromstring(BILLION_LAUGHS)
