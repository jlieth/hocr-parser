import lxml.html

from hocr_formatter.parser import HOCRNode


class TestOCRNode:
    @staticmethod
    def get_body_node_from_string(s: str) -> HOCRNode:
        document = lxml.html.document_fromstring(s)
        body = document.find("body")
        return HOCRNode(body)

    def test_parent(self):
        body = self.get_body_node_from_string("<body><p>test</p></body>")
        p = HOCRNode(body.elem.find("p"))

        # body node should return no parent
        assert body.parent is None

        # p node should return body node as parent
        assert p.parent == body
