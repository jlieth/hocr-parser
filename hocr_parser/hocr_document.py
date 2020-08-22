from typing import Iterable, List, Optional
import warnings

from .bbox import BBox
from .exceptions import EncodingError, EmptyDocumentException, MissingRequiredMetaField
from .hocr_node import HOCRNode


class HOCRDocument:
    def __init__(self, filename: str, encoding: str = "utf-8"):
        """Creates a new HOCRDocument instance from the HOCR file `filename`

        :param filename: Filename of the input HOCR document
        :param encoding: (optional) Encoding to be for the document.
            Default is utf-8.
        :raises EncodingError: When opening the file with the given encoding
            raises a UnicodeDecodeError.
        :raises EmptyDocumentException: When the given file is empty
        """
        # try to open the file with the given encoding
        data = self._read_file(filename, encoding)

        # if no data was read, the document is empty
        if len(data) == 0:
            raise EmptyDocumentException("Document is empty")

        # parse document to node
        self.html = HOCRNode.fromstring(data, encoding=encoding)

    @staticmethod
    def _read_file(filename: str, encoding: str) -> str:
        try:
            with open(filename, encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            msg = f"Couldn't open file {filename} with encoding {encoding}."
            raise EncodingError(msg)

    @property
    def root(self) -> Optional["HOCRNode"]:
        """Returns the root node of the document if available

        :return: root element as HOCRNode, or None if no body tag exists
        """
        return self.html.getroottree().getroot()

    @property
    def body(self) -> Optional["HOCRNode"]:
        """Returns the body node of the document if available

        :return: body element as HOCRNode, or None if no body tag exists
        """
        return self.html.find("body")

    @property
    def ocr_system(self) -> Optional[str]:
        """Searches for the ocr-system meta tag and returns its content.

        From the spec:

            'ocr-system: Indicates software and version that generated the
            hOCR document. Every hOCR document must have exactly one
            ocr-system metadata field'

            -- see http://kba.cloud/hocr-spec/1.2/#propdef-ocr-system

        Example tag:
        <meta name='ocr-system' content='tesseract 4.0.0-beta.1' />

        :return: The content of the meta tag named ocr-system
        """
        try:
            meta = self.html.cssselect("meta[name='ocr-system']")[0]
            return meta.get("content")
        except IndexError:
            warnings.warn("Missing ocr-system", MissingRequiredMetaField)
            return None

    @property
    def ocr_capabilities(self) -> List[str]:
        """Searches for the ocr-capabilitiesm meta tag and returns its content.

        From the spec:

            'ocr-capabilities: Features consumers of the hOCR document can
            expect. See §6.2 Capabilities for possible values.
            Every hOCR document must have exactly one ocr-capabilities
            metadata field'

            -- see http://kba.cloud/hocr-spec/1.2/#propdef-ocr-capabilities

        The capabilities meta field should list the HOCR features present in
        the document: The HOCR elements used (e.g. ocr_line, ocr_page) and
        the properties one can expect to encounter in an element's title or
        other properties (see http://kba.cloud/hocr-spec/1.2/#capabilities).

        Example tag:
        <meta name='ocr-capabilities' content='ocr_page ocr_line ocrx_word' />

        :return: A list, potentially of length zero, of the capabilities in
            the content of the meta tag named ocr-system, split at whitespace.
        """
        capabilities = []

        try:
            meta = self.html.cssselect("meta[name='ocr-capabilities']")[0]
            capabilities = meta.get("content").split()
        except IndexError:
            warnings.warn("Missing ocr-capabilities", MissingRequiredMetaField)

        return capabilities

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
                boxes.append(box)

        return BBox.max_bbox(boxes)

    def iter(self) -> Iterable["HOCRNode"]:
        """Iterates tree in depth first pre-order"""
        if self.body is None:
            return []
        else:
            return self.body.iter()
