import os
from typing import Optional

import lxml.html
import lxml.etree

from hocr_parser.hocr_document import HOCRDocument
from hocr_parser.hocr_node import HOCRNode


class BaseTestClass:
    @staticmethod
    def get_testfile_path(filename: str) -> str:
        """Returns the absolute path for testdata file"""
        pwd = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pwd, "testdata", filename)

    def get_document(self, filename: str, encoding: str = "utf-8") -> HOCRDocument:
        filepath = self.get_testfile_path(filename)
        return HOCRDocument(filepath, encoding=encoding)

    def get_body(self, filename: str) -> Optional[HOCRNode]:
        document = self.get_document(filename)
        return document.body

    @staticmethod
    def get_body_from_string(s: str) -> HOCRNode:
        return HOCRNode.fromstring(s).find("body")

    @staticmethod
    def get_node_from_string(s: str) -> HOCRNode:
        lookup = lxml.etree.ElementDefaultClassLookup(element=HOCRNode)
        parser = lxml.etree.HTMLParser(encoding="utf-8")
        parser.set_element_class_lookup(lookup)
        return lxml.html.fragment_fromstring(s, parser=parser)
