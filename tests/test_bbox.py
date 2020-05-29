from hocr_parser.bbox_wrapper import BBox


class TestBBox:
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
        boxes = [
            BBox((1, 2, 10, 12)),
            BBox((5, 4, 8, 10)),
            BBox((6, 7, 7, 9))
        ]
        expected = BBox((1, 2, 10, 12))
        assert BBox.max_bbox(boxes) == expected

        # overlapping boxes
        boxes = [
            BBox((1, 1, 4, 5)),
            BBox((3, 3, 5, 7))
        ]
        expected = BBox((1, 1, 5, 7))
        assert BBox.max_bbox(boxes) == expected

        # non-overlapping boxes
        boxes = [
            BBox((4, 2, 9, 5)),
            BBox((1, 3, 3, 4)),
            BBox((6, 6, 8, 8))
        ]
        expected = BBox((1, 2, 9, 8))
        assert BBox.max_bbox(boxes) == expected
