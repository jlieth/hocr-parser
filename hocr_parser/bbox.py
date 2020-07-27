from typing import Optional, Sequence, Tuple


class BBox:
    def __init__(self, x: Tuple[int, int, int, int]):
        """
        Creates a new bbox from given tuple x containing four integer values.

        :param x: tuple with four integer values representing the upper left
            and lower right corner of the bbox (in order XYXY)
        :raises TypeError: f the argument x has no length
        :raises ValueError:
            - if the length of x is unequal to 4
            - if the items in x are not integers
        """
        # check if x has a length
        try:
            length = len(x)
        except TypeError:
            raise TypeError("Can't determine length of argument.")

        # check if length is exactly 4
        if not length == 4:
            raise ValueError("Length of argument is not 4.")

        # check if values in x are integers by casting all values to float
        try:
            _ = [float(val) for val in x]
        except ValueError:
            raise ValueError("Values are not integers.")

        # all OK, save values
        self.x1 = x[0]
        self.y1 = x[1]
        self.x2 = x[2]
        self.y2 = x[3]

    def __repr__(self):
        return "BBox(({}, {}, {}, {}))".format(self.x1, self.y1, self.x2, self.y2)

    def __eq__(self, other: object):
        """"Checks self for equality with other object.

        Two BBoxes are considered identical if their x1, y1, x2, y2 values
        are identical.
        """
        if not type(self) == type(other):
            return False

        return (
            self.x1 == getattr(other, "x1")
            and self.y1 == getattr(other, "y1")
            and self.x2 == getattr(other, "x2")
            and self.y2 == getattr(other, "y2")
        )

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @staticmethod
    def max_bbox(boxes: Sequence["BBox"]) -> Optional["BBox"]:
        """Returns the maximum (outer) BBox for a given list of BBoxes

        In other words, calculates a new, possibly bigger BBox that contains
        all boxes passed to this function.

        :param boxes: Sequence of BBox instances
        :return: BBox, or None if the input list is empty
        """
        if len(boxes) == 0:
            return None

        # looking for smallest x1, y1 and largest x2, y2
        x1 = min([b.x1 for b in boxes])
        y1 = min([b.y1 for b in boxes])
        x2 = max([b.x2 for b in boxes])
        y2 = max([b.y2 for b in boxes])

        return BBox((x1, y1, x2, y2))
