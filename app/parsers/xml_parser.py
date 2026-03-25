from xml.etree import ElementTree as ET
import lxml.etree as lxml_etree


def parse_xml_unsafe(xml_string: str) -> ET.Element:
    return ET.fromstring(xml_string)


def parse_lxml_unsafe(xml_bytes: bytes) -> lxml_etree._Element:
    parser = lxml_etree.XMLParser(resolve_entities=True)
    return lxml_etree.fromstring(xml_bytes, parser)


BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<root>&lol3;</root>"""


def parse_billion_laughs() -> ET.Element:
    return ET.fromstring(BILLION_LAUGHS)
