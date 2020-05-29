import os

from hocr_parser.bbox import BBox
from hocr_parser.parser import HOCRNode, HOCRParser


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

    def test_bbox(self):
        # no bboxes at all
        p = self.get_parser_for_file("parser_test_bbox_no_boxes.hocr")
        assert p.bbox is None

        # one bbox
        p = self.get_parser_for_file("parser_test_bbox_one_box.hocr")
        expected = BBox((0, 0, 1000, 1000))
        assert p.bbox == expected

        # nested + overlapping bboxes
        p = self.get_parser_for_file("parser_test_bbox_overlapping_boxes.hocr")
        expected = BBox((25, 25, 1175, 650))
        assert p.bbox == expected
