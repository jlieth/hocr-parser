from typing import Dict, Iterable, Optional

import lxml.html
import lxml.etree
from lxml.doctestcompare import LHTMLOutputChecker, PARSE_HTML


class MalformedOCRException(Exception):
    pass


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

    def __eq__(self, o: object) -> bool:
        """Compares the HOCRNode to another object

        The problem with comparing HTML is that minor differences in markup
        still represent the same tree with the same elements. lxml has a
        utility meant to make output checking in doctests more readable
        by comparing the functional equivalency. Read here:
        https://lxml.de/lxmlhtml.html#running-html-doctests

        Though this isn't a doctest, this functionality is essentially what
        is needed to compare two nodes. The comparator lives in
        lxml.doctestcompare.LHTMLOutputChecker, which is used with the
        PARSE_HTML optionflag.

        The following is considered functionally equivalent by the output
        checker and will therefore evaluate as true:
        - Different order of attributes
        - Repeated spaces inside a tag
        - Whitespace between tags
        """
        if not type(self) == type(o):
            return False

        checker = LHTMLOutputChecker()
        return checker.check_output(
            want=lxml.etree.tostring(self.elem),
            got=lxml.etree.tostring(o.elem),
            optionflags=PARSE_HTML
        )

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

    @property
    def children(self) -> Iterable["HOCRNode"]:
        return self.elem.iterchildren()

    @property
    def id(self) -> Optional[str]:
        return self.elem.get("id")

    @property
    def ocr_class(self) -> Optional[str]:
        return self.elem.get("class")

    @property
    def ocr_properties(self) -> Dict[str, str]:
        d = {}

        title = self.elem.get("title", "")
        if title == "":
            return d

        for prop in title.split(";"):
            prop = prop.strip()
            splt = prop.split(" ", 1)
            if not len(splt) == 2:
                raise MalformedOCRException(f"Malformed properties: {prop}")
            key, val = splt
            d[key] = val

        return d
