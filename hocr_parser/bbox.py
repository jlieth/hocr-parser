from typing import Optional, Sequence, Tuple


class BBox:
    """This class represents the information in the hOCR bbox parameter."""

    def __init__(self, x: Tuple[int, int, int, int]):
        """
        Creates a new bbox from given tuple ``x`` containing four int values.

        :param x:
            tuple with four integer values representing the upper left
            and lower right corner of the bbox (in order XYXY)
        :raises TypeError: if param ``x`` is of incorrect type
        :raises ValueError:
            - if the length of param ``x`` is not 4
            - if the items in param ``x`` are not integers
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
        self.x0 = x[0]  #: x-value of the upper-left corner
        self.y0 = x[1]  #: y0: y-value of the upper-left corner
        self.x1 = x[2]  #: x1: x-value of the lower-right corner
        self.y1 = x[3]  #: y-value of the lower-right corner

    def __repr__(self) -> str:
        """Returns a string representation of the object.

        :Example: ``"BBox((100, 50, 350, 100))"``
        :rtype: str
        """
        return "BBox(({}, {}, {}, {}))".format(self.x0, self.y0, self.x1, self.y1)

    def __eq__(self, other: object) -> bool:
        """Checks self for equality with other object.

        Two BBoxes are considered identical if their :attr:`BBox.x0`, ``y0``, ``x1``
        and ``y1`` values are identical.

        :param other: Other object to be checked for equality
        :rtype: bool
        """
        if not type(self) == type(other):
            return False

        return (
            self.x0 == getattr(other, "x0")
            and self.y0 == getattr(other, "y0")
            and self.x1 == getattr(other, "x1")
            and self.y1 == getattr(other, "y1")
        )

    @property
    def width(self) -> int:
        """Returns the width of the `BBox` in pixels

        The width is the difference between ``self.x1`` and ``self.x0``.

        :type: int
        """
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        """Returns the height of the `BBox` in pixels

        The height is the difference between ``self.y1`` and ``self.y0``.

        :type: int
        """
        return self.y1 - self.y0

    @staticmethod
    def max_bbox(boxes: Sequence["BBox"]) -> Optional["BBox"]:
        """Returns the maximum (outer) `BBox` for a given list of BBoxes

        In other words, calculates a new, possibly bigger BBox that contains
        all boxes passed to this function.

        :param boxes: Sequence of BBox instances
        :return: the maximum outer BBox around all input BBoxes
        :rtype: `BBox`, or None if the input list is empty
        """
        if len(boxes) == 0:
            return None

        # looking for smallest x0, y0 and largest x1, y1
        x0 = min([b.x0 for b in boxes])
        y0 = min([b.y0 for b in boxes])
        x1 = max([b.x1 for b in boxes])
        y1 = max([b.y1 for b in boxes])

        return BBox((x0, y0, x1, y1))
