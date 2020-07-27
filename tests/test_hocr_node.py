import math
import os

import lxml.html
import lxml.etree
import pytest

from hocr_parser.bbox import BBox
from hocr_parser.exceptions import MalformedOCRException
from hocr_parser.hocr_node import HOCRNode


class TestOCRNode:
    @staticmethod
    def get_body_node_from_file(filename: str):
        pwd = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(pwd, "testdata", filename)
        with open(filepath, encoding="utf-8") as f:
            data = f.read().encode("utf-8")
            return HOCRNode.from_string(data).find("body")

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
        body = self.get_body_node_from_file("node_test_equality.hocr")
        assert not body == "Foo"

        # same tag should be equal
        nodes = body.cssselect("#same span")
        assert nodes[0] == nodes[1]

        # repeated space inside tags should equal single space
        nodes = body.cssselect("#repeated_space span")
        assert nodes[0] == nodes[1]

        # whitespace between tags should be equal to no whitespaces
        nodes = body.cssselect("#whitespace_between_tags div")
        assert nodes[0] == nodes[1]

        # different order but same value of attributes should be equal
        nodes = body.cssselect("#attr_different_order_same_value span")
        assert nodes[0] == nodes[1]

        # different tags should not be equal
        node1 = body.cssselect("#different_tags span")[0]
        node2 = body.cssselect("#different_tags p")[0]
        assert not node1 == node2

        # different content should not be equal
        nodes = body.cssselect("#different_content span")
        assert not nodes[0] == nodes[1]

        # different attribute values should not be equal
        nodes = body.cssselect("#different_attr_values span")
        assert not nodes[0] == nodes[1]

        # node with additional attribute should NOT be equal
        nodes = body.cssselect("#additional_attrs span")
        assert not nodes[0] == nodes[1]

    def test_parent(self):
        body = self.get_body_node_from_string("<body><p>test</p></body>")
        p = body.find("p")

        # p node should return body node as parent
        assert p.parent == body

    def test_children(self):
        body = self.get_body_node_from_file("node_test_children.hocr")

        # no children
        node = body.cssselect("#no_children")[0]
        assert list(node.children) == []

        # node that only contains text has no children
        node = body.cssselect("#only_text")[0]
        assert list(node.children) == []

        # node that only contains a <br>: counts as child
        node = body.cssselect("#break")[0]
        assert len(list(node.children)) == 1

        # node that only contains a comment: counts as child
        node = body.cssselect("#only_comment")[0]
        assert len(list(node.children)) == 1

        # node with multiple children
        node = body.cssselect("#multiple_children")[0]
        assert list(node.children) == node.cssselect(".child")

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
        body = self.get_body_node_from_file("node_test_bbox.hocr")

        # no bbox given
        node = body.get_element_by_id("no_bbox")
        assert node.bbox is None

        # wrong number of coordinates
        node = body.get_element_by_id("wrong_number_of_coordinates")
        with pytest.raises(MalformedOCRException):
            _ = node.bbox

        # coordinates aren't ints
        node = body.get_element_by_id("coordinates_not_ints")
        with pytest.raises(MalformedOCRException):
            _ = node.bbox

        # valid bbox
        node = body.get_element_by_id("valid_bbox")
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

    def test_rel_bbox(self):
        body = self.get_body_node_from_file("node_test_rel_bbox.hocr")

        # no bbox on element
        node = body.get_element_by_id("no_bbox")
        assert node.rel_bbox is None

        # bbox on node + bbox on direct ancestor
        node = body.get_element_by_id("bbox_on_node_and_direct_ancestor")
        expected = BBox((33, 0, 66, 20))
        assert node.rel_bbox == expected

        # bbox on node + bbox on more distant ancestor
        node = body.get_element_by_id("bbox_on_node_and_distant_ancestor")
        expected = BBox((38, 5, 71, 25))
        assert node.rel_bbox == expected

        # bbox on node + no bbox on ancestors
        node = body.get_element_by_id("bbox_on_node_and_no_ancestor")
        assert node.rel_bbox == node.bbox

    def test_confidences(self):
        body = self.get_body_node_from_file("node_test_confidence.hocr")

        # no confidence property given should return None
        node: HOCRNode = body.get_element_by_id("no_confidence")
        assert node.confidence is None

        # x_wconf given should return its value (as float)
        node: HOCRNode = body.get_element_by_id("x_wconf_given")
        assert type(node.confidence) == float
        assert math.isclose(node.confidence, 80)

        # malformed x_wconf should raise MalformedOCRException
        node: HOCRNode = body.get_element_by_id("malformed_x_wconf")
        with pytest.raises(MalformedOCRException):
            _ = node.confidence

        # x_confs given should result in average of its values
        node: HOCRNode = body.get_element_by_id("x_confs_given")
        assert type(node.confidence) == float
        assert math.isclose(node.confidence, 39)

        # malformed x_confs should raise MalformedOCRException
        node: HOCRNode = body.get_element_by_id("malformed_x_confs")
        with pytest.raises(MalformedOCRException):
            _ = node.confidence

        # x_wconf should take precedence over x_confs
        node: HOCRNode = body.get_element_by_id("x_wconf_and_x_confs")
        assert math.isclose(node.confidence, 80)

    def test_finding_elements(self):
        """Tests the element properties on HOCRNode.

        These properties are currently tested:
        - HOCRNode.pages
        - HOCRNode.areas
        - HOCRNode.paragraphs
        - HOCRNode.lines
        - HOCRNode.words
        """
        implemented_elements = ["pages", "areas", "paragraphs", "lines", "words"]

        for elem in implemented_elements:
            filename = f"node_test_find_{elem}.hocr"
            body = self.get_body_node_from_file(filename)

            # no elements of this kind in specified node in test page
            node_id = f"no_{elem}"
            node = body.get_element_by_id(node_id)
            assert getattr(node, elem) == []

            # two elements of this kind in specified node in test page
            node_id = f"two_{elem}"
            node = body.get_element_by_id(node_id)
            expected = node.cssselect(".expected")
            result = getattr(node, elem)
            assert result == expected
            assert len(result) == 2

            # there should be three elements of this kind in entire body
            expected = body.cssselect(".expected")
            result = getattr(body, elem)
            assert result == expected
            assert len(result) == 3

    def test_ocr_text(self):
        body = self.get_body_node_from_file("node_test_ocr_text.hocr")

        test_cases = [
            {"id": "words", "expected": "Foo bar Baz."},
            {"id": "lines", "expected": "Foo\nbar\nBaz."},
            {"id": "paragraphs", "expected": "Foo\n bar\n Baz."},
            {"id": "areas", "expected": "Foo\n\nbar\n\nBaz."},
            {"id": "pages", "expected": "Foo\n\nbar\n\nBaz."},
            {"id": "mix", "expected": "foo foo\n\nfoo\nfoo\n\nfoo\n foo"},
            {"id": "no_whitespace", "expected": "Foo bar"},
            {"id": "nested", "expected": "Foo bar Baz.\nBaz. bar Foo"},
            {"id": "empty_child", "expected": "foo"},
            {"id": "inline_text", "expected": "bar foo bar foo bar"},
        ]

        for case in test_cases:
            print(case["id"])
            node = body.get_element_by_id(case["id"])
            assert node.ocr_text == case["expected"]
