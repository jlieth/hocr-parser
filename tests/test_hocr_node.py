import math

import lxml.html
import lxml.etree
import pytest

from hocr_formatter.bbox import BBox
from hocr_formatter.parser import HOCRNode, MalformedOCRException


class TestOCRNode:
    @staticmethod
    def get_body_node_from_string(s: str) -> HOCRNode:
        return HOCRNode.from_string(s).find("body")

    @staticmethod
    def get_element_node_from_string(s: str) -> HOCRNode:
        lookup = lxml.etree.ElementDefaultClassLookup(element=HOCRNode)
        parser = lxml.etree.HTMLParser(encoding="utf-8")
        parser.set_element_class_lookup(lookup)
        return lxml.html.fragment_fromstring(s, parser=parser)

    def test_equality(self):
        # different type should not be equal
        s = "<body><span>Test</span></body>"
        body = self.get_body_node_from_string(s)
        assert body != s

        # same doc should be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        assert body1 == body2

        # different order but same value of attributes should be equal
        body1 = self.get_body_node_from_string(
            "<body><span id='word1' class='ocrx_word'>Foo</span></body>"
        )
        body2 = self.get_body_node_from_string(
            "<body><span class='ocrx_word' id='word1'>Foo</span></body>"
        )
        assert body1 == body2

        # repeated space inside tags should equal single space
        body1 = self.get_body_node_from_string("<body><p>Foo Bar</p></body>")
        body2 = self.get_body_node_from_string("<body><p>Foo   Bar</p></body>")
        assert body1 == body2

        # whitespace between tags should be equal to no whitespaces
        body1 = self.get_body_node_from_string("""
            <body>
                <p>Foo</p>  <span>Bar</span>  Baz
            </body>
        """)
        body2 = self.get_body_node_from_string(
            "<body><p>Foo</p><span>Bar</span>Baz<body>"
        )
        assert body1 == body2

        # different tags should not be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><p>Foo</p></body>")
        assert body1 != body2

        # different text should not be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><span>Bar</span></body>")
        assert body1 != body2

        # different attribute values should not be equal
        body1 = self.get_body_node_from_string(
            "<body><span class='ocrx_word'>Foo</span></body>"
        )
        body2 = self.get_body_node_from_string(
            "<body><span class='ocr_line'>Foo</span></body>"
        )
        assert body1 != body2

    def test_parent(self):
        body = self.get_body_node_from_string("<body><p>test</p></body>")
        p = body.find("p")

        # p node should return body node as parent
        assert p.parent == body

    def test_children(self):
        s = """
            <body>
                <div class="ocr_carea">
                    <span class="ocrx_word">Foo</span>
                    <span class="non_ocr">Bar</span>
                    Random text
                    <span class="ocrx_word">Baz</span> 
                </div>
                <!-- comment -->
                <br>
                <span class="ocrx_word">Foo</span>
                Random text
                <p>
                    <span class="ocrx_word">Foo</span>
                    <span class="non_ocr">Bar</span>
                    Random text
                    <span class="ocrx_word">Baz</span> 
                </p>
                <p>Random text</p>
                <span class="ocr_line">
                    <span class="non_ocr">Bar</span>
                    Random text
                </span>
            </body>
        """

        body = self.get_body_node_from_string(s)
        assert list(body.children) == list(body.iterchildren())

    def test_id(self):
        node = self.get_element_node_from_string("<span id='word1'>Foo</span>")
        assert node.id == "word1"

        # no id
        node = self.get_element_node_from_string("<span>Foo</span>")
        assert node.id is None

    def test_ocr_class(self):
        # no class name should return None
        node = self.get_element_node_from_string("<p>Foo</p>")
        assert node.ocr_class is None

        # a class name not starting with ocr should return None
        node = self.get_element_node_from_string("<p class='bar'>Foo</p>")
        assert node.ocr_class is None

        # ocr class name should be returned correctly
        node = self.get_element_node_from_string("<p class='ocr_line'>Foo</p>")
        assert node.ocr_class == "ocr_line"

        # multiple class names
        node = self.get_element_node_from_string("<p class='foo ocr_line'>Foo</p>")
        assert node.ocr_class == "ocr_line"

    def test_ocr_properties(self):
        # no title attribute
        node = self.get_element_node_from_string("<p>Foo</p>")
        assert node.ocr_properties == {}

        # empty title string
        node = self.get_element_node_from_string("<p title=''>Foo</p>")
        assert node.ocr_properties == {}

        # with properties
        node = self.get_element_node_from_string(
            "<p title='bbox 103 215 194 247; x_wconf 93'>Foo</p>"
        )
        expected_properties = {"x_wconf": "93", "bbox": "103 215 194 247"}
        assert node.ocr_properties == expected_properties

        # malformed
        node = self.get_element_node_from_string("<p title='foo; bar baz'>Foo</p>")
        with pytest.raises(MalformedOCRException):
            _ = node.ocr_properties

    def test_bbox(self):
        # no bbox given
        node = self.get_element_node_from_string("<p>Foo</p>")
        assert node.bbox is None

        # wrong number of coordinates
        node = self.get_element_node_from_string("<p title='bbox 103 215 194'>Foo</p>")
        with pytest.raises(MalformedOCRException):
            _ = node.bbox

        # not ints
        node = self.get_element_node_from_string("<p title='bbox a b c d'>Foo</p>")
        with pytest.raises(MalformedOCRException):
            _ = node.bbox

        # all fine
        node = self.get_element_node_from_string("<p title='bbox 103 215 194 247'>Foo</p>")
        assert node.bbox == BBox((103, 215, 194, 247))

    def test_parent_bbox(self):
        # no parent (should only happen on html tag, but anyway)
        s = "<html><body></body></html>"
        html = self.get_body_node_from_string(s).parent
        assert html.parent_bbox is None

        # parent has no bbox
        s = "<body><div><p id='node'>Foo</p></div></body>"
        body = self.get_body_node_from_string(s)
        node = body.get_element_by_id("node")
        assert node.parent_bbox is None

        # direct parent has bbox
        s = "<body><div title='bbox 1 5 17 33'><p id='node'>Foo</p></div></body>"
        body = self.get_body_node_from_string(s)
        node = body.get_element_by_id("node")
        expected = BBox((1, 5, 17, 33))
        assert node.parent_bbox == expected

        # more distant ancestor has bbox
        s = """
            <body>
                <div title='bbox 1 5 17 33'>
                    <div>
                        <p>
                            <span id='node'>Foo</span>
                        </p>
                    </div>
                </div>
            </body>
        """
        body = self.get_body_node_from_string(s)
        node = body.get_element_by_id("node")
        expected = BBox((1, 5, 17, 33))
        assert node.parent_bbox == expected

    def test_confidences(self):
        # no confidence property given should return None
        node = self.get_element_node_from_string("<p title='bbox 103 215 194'>Foo</p>")
        assert node.confidence is None

        # x_wconf given should return its value (as float)
        node = self.get_element_node_from_string("<p title='x_wconf 80'>Foo</p>")
        assert type(node.confidence) == float
        assert math.isclose(node.confidence, 80)

        # malformed x_wconf should raise MalformedOCRException
        node = self.get_element_node_from_string("<p title='x_wconf eighty'>Foo</p>")
        with pytest.raises(MalformedOCRException):
            _ = node.confidence

        # x_confs given should result in average of its values
        node = self.get_element_node_from_string("<p title='x_confs 20 7 90'>Foo</p>")
        assert type(node.confidence) == float
        assert math.isclose(node.confidence, 39)

        # malformed x_confs should raise MalformedOCRException
        node = self.get_element_node_from_string("<p title='x_confs a b c'>Foo</p>")
        with pytest.raises(MalformedOCRException):
            _ = node.confidence

        # x_wconf should take precedence over x_confs
        node = self.get_element_node_from_string("<p title='x_wconf 80; x_confs 20 5 90'>Foo</p>")
        assert math.isclose(node.confidence, 80)
