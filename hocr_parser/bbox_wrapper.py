from typing import Optional, Sequence, Tuple

from bbox import BBox2D, XYXY


class BBox(BBox2D):
    """Wrapper for the BBox2D class from the bbox package."""

    def __init__(self, x: Tuple[int, int, int, int]):
        super().__init__(x, mode=XYXY)

    @staticmethod
    def max_bbox(boxes: Sequence["BBox"]) -> Optional["BBox"]:
        """Returns the maximum (outer) BBox for a given list of BBoxes

        In other words, calculates a new, possibly bigger BBox that contains
        all boxes passed to this function.

        :param boxes: Sequence of BBox instances
        :return: BBox, or None if the input list is empty
        """
        if len(boxes) == 0:
            return

        # looking for smallest x1, y1 and largest x2, y2
        x1 = min([b.x1 for b in boxes])
        y1 = min([b.y1 for b in boxes])
        x2 = max([b.x2 for b in boxes])
        y2 = max([b.y2 for b in boxes])

        return BBox((x1, y1, x2, y2))
