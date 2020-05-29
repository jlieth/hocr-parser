from typing import Union, Optional, Iterable, Dict

import lxml.etree
import lxml.html
from lxml.doctestcompare import LHTMLOutputChecker, PARSE_HTML

from .bbox import BBox
from .exceptions import MalformedOCRException


class HOCRNode(lxml.html.HtmlElement):
    """Wrapper class for a lxml.html.HtmlElement

    This class isn't meant to be used by itself. It is utilised by the
    HOCRParser class to represent the elements of the HTML tree.
    """
    HTML = True

    @staticmethod
    def from_string(s: Union[str, bytes]) -> "HOCRNode":
        lookup = lxml.etree.ElementDefaultClassLookup(element=HOCRNode)
        parser = lxml.etree.HTMLParser(encoding="utf-8")
        parser.set_element_class_lookup(lookup)
        return lxml.html.document_fromstring(s, parser=parser)

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
            want=lxml.etree.tostring(self),
            got=lxml.etree.tostring(o),
            optionflags=PARSE_HTML
        )

    @property
    def parent(self) -> Optional["HOCRNode"]:
        """Returns the parent node of this node

        :return: HOCRNode, or None
        """
        # return parent
        return self.getparent()

    @property
    def children(self) -> Iterable["HOCRNode"]:
        return self.iterchildren()

    @property
    def id(self) -> Optional[str]:
        return self.get("id")

    @property
    def ocr_class(self) -> Optional[str]:
        """Returns the html class name of the node (but only if node is ocr)

        All elements defined in the HOCR specification start with ocr.
        If the class name of an element does not start with ocr, it is
        therefore not an ocr element as defined by the spec.

        :return: The class name as str, or None
        """
        for class_ in self.classes:
            if class_.startswith("ocr"):
                return class_

        return None

    @property
    def ocr_properties(self) -> Dict[str, str]:
        d = {}

        title = self.get("title", "")
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

    @property
    def bbox(self) -> Optional[BBox]:
        """Parses the bbox hocr property and returns it as BBox instance

        bbox property spec:
        http://kba.cloud/hocr-spec/1.2/#bbox

        The bbox defines the rectangular bounding box around the hocr element.
        It's given in XYXY format, meaning the first two arguments are the
        coordinates of the upper-left corner of the bounding box and the last
        two arguments are the coordinates of the lower-right corner.

        :return: BBox instance, or None if the element has no bbox property

        :raises hocr_formatter.parser.MalformedOCRException: If the bbox
            property in the title attribute is malformed (wrong number of
            arguments or wrong type of arguments)
        """
        bbox = self.ocr_properties.get("bbox")
        if not bbox:
            return None

        # parse args
        args = bbox.split(" ")
        if not len(args) == 4:
            raise MalformedOCRException("Number of bbox args must be four")

        try:
            x0 = int(args[0])
            y0 = int(args[1])
            x1 = int(args[2])
            y1 = int(args[3])
        except ValueError:
            raise MalformedOCRException("Value of bbox arguments must be uint")

        return BBox((x0, y0, x1, y1))

    @property
    def parent_bbox(self) -> Optional[BBox]:
        """Returns the BBox of the node closest up in the tree that has a BBox

        Traverses the tree upwards through the parent and looks for the first
        node that defines a BBox.

        :return: BBox instance, or None if no parent with a BBox exists
        """
        parent = self.parent
        while parent is not None:
            if parent.bbox:
                return parent.bbox
            else:
                parent = parent.parent

    @property
    def rel_bbox(self) -> Optional[BBox]:
        """Returns a BBox with coordinates relative to the parent element

        The coordinates given in the HOCR bbox attribute are absolute (in the
        sense that they give the coordinates in pixels relative to the source
        picture's origin).

        This method calculates the offset (in pixels) of the current element
        relative to the bbox of the closest ancestor that has a bbox property.

        Possible return values:
        - None if the current element has no bbox property
        - if none of the element's ancestors has a bbox property, the
          returned rel_bbox will equal its bbox
        - if any if the element's ancestors has a bbox property, the
          returned bbox will be the offset of the bbox coordinates relative
          to the upper left corner of the bbox of the closest ancestor

        :return: A BBox instance, or None
        """
        if self.bbox is None:
            return None

        parent_bbox = self.parent_bbox
        if parent_bbox is None:
            return self.bbox

        return BBox((
            self.bbox.x1 - parent_bbox.x1,
            self.bbox.y1 - parent_bbox.y1,
            self.bbox.x2 - parent_bbox.x1,
            self.bbox.y2 - parent_bbox.y1
        ))

    @property
    def confidence(self) -> Optional[float]:
        """Parses confidence properties and returns the value as a single float

        The HOCR standard defines three different properties for indicating
        the confidence of the given ocr word/character:
        - x_wconf: http://kba.cloud/hocr-spec/1.2/#x_wconf
          Property value should be a single float between 0 and 100 indicating
          the confidence for the whole word
        - x_confs: http://kba.cloud/hocr-spec/1.2/#x_confs
          Property values should be one or more floats between 0 and 100
          indicating the confidence for every recognized character
        - nlp: http://kba.cloud/hocr-spec/1.2/#nlp
          Property value is one or more floats, one for each recognized
          character. NLP is the negative log probability and takes on values
          between 0 and infinity for inputs between 0 and 1.

        The confidence properties differ in what their values
        actually represent: For x_wconf and x_confs, higher values mean a
        higher confidence in the recognized word/character. The NLP is
        a negative logarithm and therefore lower when the input is higher,
        meaning that a low value of NLP indicates a high confidence.

        Therefore, confidence values and NLP are neither directly comparable
        nor can be averaged. Since the spec doesn't specify the base for the
        logarithm, the NLP can't be converted to the input confidence either.

        For the purpose of this method I'm only using the values of x_wconf
        and x_confs. If x_wconf is given, its value is returned. If not,
        x_confs is checked and if given, all values are averaged and returned.
        If neither x_wconf nor x_confs is given, None is returned.

        :return: A float if x_confs and/or x_wconf properties are given in
                 the title string of the element; otherwise None
        """
        # return x_wconf if it is given
        x_wconf = self.ocr_properties.get("x_wconf")
        if x_wconf:
            try:
                return float(x_wconf)
            except ValueError:
                raise MalformedOCRException(f"Value of x_wconf must be float")

        # return averaged x_confs if given
        x_confs = self.ocr_properties.get("x_confs")
        if x_confs:
            values = x_confs.split(" ")

            try:
                confidences = [float(x) for x in values]
            except ValueError:
                raise MalformedOCRException(f"Values of x_confs must be float")

            # return average confidence
            return sum(confidences) / len(confidences)