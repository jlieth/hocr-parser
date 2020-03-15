from typing import Optional

import lxml.html


class HOCRParser:
    def __init__(self, filename: str):
        with open(filename, encoding="utf-8") as f:
            data = f.read()
            self.html = lxml.html.document_fromstring(data)

    @property
    def root(self) -> Optional["HOCRNode"]:
        element = self.html.find("body")
        if element is not None:
            return HOCRNode(element)


class HOCRNode:
    """Wrapper class for a lxml.html.HtmlElement

    This class isn't meant to be used by itself. It is utilised by the
    HOCRParser class to represent the elements of the HTML tree.
    """

    def __init__(self, elem: lxml.html.HtmlElement):
        self.elem = elem

    @property
    def parent(self) -> Optional["HOCRNode"]:
        """Returns the parent node of this node

        The body node is the outer wrapper of the HOCR document and doesn't
        have a parent.

        :return: HOCRNode, or None
        """
        # don't return parent if current node is the body element
        if self.elem.tag == "body":
            return None

        # return parent if it exists
        parent = self.elem.getparent()
        if parent is not None:
            return HOCRNode(parent)
