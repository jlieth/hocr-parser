import os

import pytest

from hocr_parser.bbox import BBox
from hocr_parser.exceptions import EmptyDocumentException, MissingRequiredMetaField
from hocr_parser.hocr_document import HOCRDocument
from hocr_parser.hocr_node import HOCRNode


class TestOCRDocument:
    @staticmethod
    def get_parser_for_file(s: str) -> HOCRDocument:
        pwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(pwd, "testdata", s)
        return HOCRDocument(filepath)

    @staticmethod
    def get_body_node_from_string(s: str) -> HOCRNode:
        return HOCRNode.from_string(s).find("body")

    def test_init(self):
        # test empty file
        with pytest.raises(EmptyDocumentException):
            _ = self.get_parser_for_file("test_init_empty_file.hocr")

        # test valid file
        doc = self.get_parser_for_file("test_init_valid_file.hocr")
        assert isinstance(doc.html, HOCRNode)

    def test_body(self):
        # test hocr file without body tag
        p = self.get_parser_for_file("test_body_no_body_tag.hocr")
        assert p.body is None

        # test hocr file with body tag
        p = self.get_parser_for_file("test_body_with_body_tag.hocr")
        expected = self.get_body_node_from_string("<body><p>Foo</p></body>")
        assert p.body == expected

    def test_ocr_system(self):
        # test hocr file without ocr-system meta tag
        p = self.get_parser_for_file("document_test_ocr_system_no_meta_tag.hocr")

        with pytest.warns(MissingRequiredMetaField):
            _ = p.ocr_system

        # with tag
        p = self.get_parser_for_file("document_test_ocr_system_with_meta_tag.hocr")
        expected = "tesseract 4.0.0-beta.1"
        assert p.ocr_system == expected

    def test_ocr_capabilities(self):
        # no meta tag
        p = self.get_parser_for_file("document_test_ocr_capabilities_no_meta_tag.hocr")

        with pytest.warns(MissingRequiredMetaField):
            capabilities = p.ocr_capabilities

        assert capabilities == []

        p = self.get_parser_for_file("document_test_ocr_capabilities_with_meta_tag.hocr")
        expected = ["ocr_page", "ocr_carea", "ocr_par", "ocr_line", "ocrx_word"]
        assert p.ocr_capabilities == expected

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
