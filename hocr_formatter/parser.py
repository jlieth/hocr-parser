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
