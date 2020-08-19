import pytest

from hocr_parser.bbox import BBox
from hocr_parser.hocr_node import HOCRNode
from hocr_parser.exceptions import (
    EmptyDocumentException,
    EncodingError,
    MissingRequiredMetaField,
)

from .base import BaseTestClass


class TestOCRDocument(BaseTestClass):
    def test_init(self):
        # test empty file
        with pytest.raises(EmptyDocumentException):
            _ = self.get_document("document_test_init_empty_file.hocr")

        # test valid file
        doc = self.get_document("document_test_init_valid_file.hocr")
        assert isinstance(doc.html, HOCRNode)

        # test different encoding
        filename = "document_test_file_encodings_utf16le.hocr"
        doc = self.get_document(filename, encoding="utf-16le")
        assert doc.body.ocr_text == "fööbär"
        assert doc.html.getroottree().docinfo.encoding == "utf-16le"

    def test_read_file(self):
        filename = "document_test_file_encodings_utf16le.hocr"

        # test wrong encoding
        with pytest.raises(EncodingError):
            _ = self.get_document(filename, encoding="utf-8")

    def test_file_encodings(self):
        # utf-8
        doc = self.get_document("document_test_file_encodings_utf8.hocr")
        assert doc.body.ocr_text == "fööbär"
        assert doc.html.getroottree().docinfo.encoding == "utf-8"

        # utf-16-le
        filename = "document_test_file_encodings_utf16le.hocr"
        doc = self.get_document(filename, encoding="utf-16le")
        assert doc.body.ocr_text == "fööbär"

    def test_body(self):
        # test hocr file without body tag
        doc = self.get_document("document_test_body_no_body_tag.hocr")
        assert doc.body is None

        # test hocr file with body tag
        doc = self.get_document("document_test_body_with_body_tag.hocr")
        expected = self.get_body_from_string("<html><body><p>Foo</p></body></html>")
        assert doc.body == expected

    def test_ocr_system(self):
        # test hocr file without ocr-system meta tag
        doc = self.get_document("document_test_ocr_system_no_meta_tag.hocr")

        with pytest.warns(MissingRequiredMetaField):
            _ = doc.ocr_system

        # with tag
        doc = self.get_document("document_test_ocr_system_with_meta_tag.hocr")
        expected = "tesseract 4.0.0-beta.1"
        assert doc.ocr_system == expected

    def test_ocr_capabilities(self):
        # no meta tag
        doc = self.get_document("document_test_ocr_capabilities_no_tag.hocr")

        with pytest.warns(MissingRequiredMetaField):
            capabilities = doc.ocr_capabilities

        assert capabilities == []

        doc = self.get_document("document_test_ocr_capabilities_with_tag.hocr")
        expected = ["ocr_page", "ocr_carea", "ocr_par", "ocr_line", "ocrx_word"]
        assert doc.ocr_capabilities == expected

    def test_bbox(self):
        # no bboxes at all
        doc = self.get_document("document_test_bbox_no_boxes.hocr")
        assert doc.bbox is None

        # one bbox
        doc = self.get_document("document_test_bbox_one_box.hocr")
        expected = BBox((0, 0, 1000, 1000))
        assert doc.bbox == expected

        # nested + overlapping bboxes
        doc = self.get_document("document_test_bbox_overlapping_boxes.hocr")
        expected = BBox((25, 25, 1175, 650))
        assert doc.bbox == expected
