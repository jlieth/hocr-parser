import lxml.html

from hocr_formatter.parser import HOCRNode


class TestOCRNode:
    @staticmethod
    def get_body_node_from_string(s: str) -> HOCRNode:
        document = lxml.html.document_fromstring(s)
        body = document.find("body")
        return HOCRNode(body)

    def test_equality(self):
        # different type should not be equal
        s = "<body><span>Test</span></body>"
        body = self.get_body_node_from_string(s)
        assert body != s

        # same doc should be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        assert body1 == body2

        # different order but same value of attributes should be equal
        body1 = self.get_body_node_from_string(
            "<body><span id='word1' class='ocrx_word'>Foo</span></body>"
        )
        body2 = self.get_body_node_from_string(
            "<body><span class='ocrx_word' id='word1'>Foo</span></body>"
        )
        assert body1 == body2

        # repeated space inside tags should equal single space
        body1 = self.get_body_node_from_string("<body><p>Foo Bar</p></body>")
        body2 = self.get_body_node_from_string("<body><p>Foo   Bar</p></body>")
        assert body1 == body2

        # whitespace between tags should be equal to no whitespaces
        body1 = self.get_body_node_from_string("""
            <body>
                <p>Foo</p>  <span>Bar</span>  Baz
            </body>
        """)
        body2 = self.get_body_node_from_string(
            "<body><p>Foo</p><span>Bar</span>Baz<body>"
        )
        assert body1 == body2

        # different tags should not be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><p>Foo</p></body>")
        assert body1 != body2

        # different text should not be equal
        body1 = self.get_body_node_from_string("<body><span>Foo</span></body>")
        body2 = self.get_body_node_from_string("<body><span>Bar</span></body>")
        assert body1 != body2

        # different attribute values should not be equal
        body1 = self.get_body_node_from_string(
            "<body><span class='ocrx_word'>Foo</span></body>"
        )
        body2 = self.get_body_node_from_string(
            "<body><span class='ocr_line'>Foo</span></body>"
        )
        assert body1 != body2

    def test_parent(self):
        body = self.get_body_node_from_string("<body><p>test</p></body>")
        p = HOCRNode(body.elem.find("p"))

        # body node should return no parent
        assert body.parent is None

        # p node should return body node as parent
        assert p.parent == body

    def test_children(self):
        s = """
            <body>
                <div class="ocr_carea">
                    <span class="ocrx_word">Foo</span>
                    <span class="non_ocr">Bar</span>
                    Random text
                    <span class="ocrx_word">Baz</span> 
                </div>
                <!-- comment -->
                <br>
                <span class="ocrx_word">Foo</span>
                Random text
                <p>
                    <span class="ocrx_word">Foo</span>
                    <span class="non_ocr">Bar</span>
                    Random text
                    <span class="ocrx_word">Baz</span> 
                </p>
                <p>Random text</p>
                <span class="ocr_line">
                    <span class="non_ocr">Bar</span>
                    Random text
                </span>
            </body>
        """

        body = self.get_body_node_from_string(s)
        assert list(body.children) == list(body.elem.iterchildren())

    def test_id(self):
        elem = lxml.html.fragment_fromstring("<span id='word1'>Foo</span>")
        node = HOCRNode(elem)
        assert node.id == "word1"

        # no id
        elem = lxml.html.fragment_fromstring("<span>Foo</span>")
        node = HOCRNode(elem)
        assert node.id is None

    def test_ocr_class(self):
        elem = lxml.html.fragment_fromstring("<p class='ocr_line'>Foo</p>")
        node = HOCRNode(elem)
        assert node.ocr_class == "ocr_line"

        # no ocr_class (should only happen on body element)
        elem = lxml.html.fragment_fromstring("<p>Foo</p>")
        node = HOCRNode(elem)
        assert node.ocr_class is None
