import pytest

from hocr_parser.bbox import BBox


class TestBBox:
    def test_init(self):
        # arg not a sequence with len()
        with pytest.raises(TypeError):
            BBox(1234)

        # len of arg is not equal to 4
        with pytest.raises(ValueError):
            BBox((1, 2, 3, 4, 5))

        # values in arg are not integers
        with pytest.raises(ValueError):
            BBox(("a", "b", "c", "d"))

        # valid args
        bbox = BBox((-123, -456, 123, 456))
        assert bbox.x1 == -123
        assert bbox.y1 == -456
        assert bbox.x2 == 123
        assert bbox.y2 == 456

    def test_repr(self):
        bbox = BBox((-123, -456, 123, 456))
        assert bbox.__repr__() == "BBox((-123, -456, 123, 456))"

    def test_eq(self):
        bbox1 = BBox((-123, -456, 123, 456))
        bbox2 = BBox((-123, -456, 123, 456))
        bbox3 = BBox((456, 789, 789, 890))

        assert bbox1 == bbox2
        assert not bbox1 == bbox3
        assert not bbox1 == (-123, -456, 123, 456)

    def test_width(self):
        bbox = BBox((-123, -456, 123, 456))
        assert bbox.width == 123 + 123

    def test_height(self):
        bbox = BBox((-123, -456, 123, 456))
        assert bbox.height == 456 + 456

    def test_max_bbox(self):
        # empty list should return None
        boxes = []
        expected = None
        assert BBox.max_bbox(boxes) == expected

        # only one bbox should return max bbox equal to that box
        boxes = [BBox((10, 20, 100, 120))]
        expected = BBox((10, 20, 100, 120))
        assert BBox.max_bbox(boxes) == expected

        # bboxes contained in each other should return bbox equal to outer box
        boxes = [BBox((1, 2, 10, 12)), BBox((5, 4, 8, 10)), BBox((6, 7, 7, 9))]
        expected = BBox((1, 2, 10, 12))
        assert BBox.max_bbox(boxes) == expected

        # overlapping boxes
        boxes = [BBox((1, 1, 4, 5)), BBox((3, 3, 5, 7))]
        expected = BBox((1, 1, 5, 7))
        assert BBox.max_bbox(boxes) == expected

        # non-overlapping boxes
        boxes = [BBox((4, 2, 9, 5)), BBox((1, 3, 3, 4)), BBox((6, 6, 8, 8))]
        expected = BBox((1, 2, 9, 8))
        assert BBox.max_bbox(boxes) == expected
