from typing import Iterable, Optional

from .bbox import BBox
from .hocr_node import HOCRNode


class HOCRParser:
    def __init__(self, filename: str):
        with open(filename, encoding="utf-8") as f:
            data = bytes(f.read(), encoding="utf-8")
            self.html = HOCRNode.from_string(data)

    @property
    def root(self) -> Optional["HOCRNode"]:
        """Returns the body node of the document if available

        :return: body element as HOCRNode, or None if no body tag exists
        """
        element = self.html.find("body")
        if element is not None:
            return element

    @property
    def bbox(self) -> Optional[BBox]:
        """Returns the max BBox containing all other BBoxes of tree nodes

        Iterates over the tree, collecting all BBoxes and calls
        BBox.max_bbox with the list of BBoxes as argument.

        :return: BBox, or None if the list of collected bboxes is empty
        """
        boxes = []
        for node in self.iter():
            box = node.bbox
            if box:
                boxes.append(node.bbox)

        return BBox.max_bbox(boxes)

    def iter(self) -> Iterable["HOCRNode"]:
        """Iterates tree in depth first pre-order"""
        return self.root.iter()
