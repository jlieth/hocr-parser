import lxml.html


class HOCRParser:
    def __init__(self, filename: str):
        with open(filename, encoding="utf-8") as f:
            data = f.read()
            self.html = lxml.html.document_fromstring(data)
