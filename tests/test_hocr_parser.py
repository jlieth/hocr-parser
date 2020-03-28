import os

from hocr_formatter.bbox import BBox
from hocr_formatter.parser import HOCRNode, HOCRParser


class TestOCRNode:
    @staticmethod
    def get_parser_for_file(s: str) -> HOCRParser:
        pwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(pwd, "testdata", s)
        return HOCRParser(filepath)

    @staticmethod
    def get_body_node_from_string(s: str) -> HOCRNode:
        return HOCRNode.from_string(s).find("body")

    def test_root(self):
        # test hocr file without body tag
        p = self.get_parser_for_file("parser_test_root_no_body.hocr")
        assert p.root is None

        # test hocr file with body tag
        p = self.get_parser_for_file("parser_test_root_with_body_tag.hocr")
        expected = self.get_body_node_from_string("<body><p>Foo</p></body>")
        assert p.root == expected

