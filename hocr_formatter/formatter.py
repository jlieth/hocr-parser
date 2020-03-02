import base64
from io import BytesIO

from bs4 import BeautifulSoup
from hocr_parser.parser import HOCRDocument, Word

from bbox import BBox2D, XYXY

try:
    from PIL import Image
except ImportError:
    pass


def extract_confidence(word):
    parts = word["title"].split(";")
    for part in parts:
        part = part.strip()
        if part.startswith("x_wconf"):
            confidence = part.split(" ")[1]
            confidence = int(confidence)
            return confidence
    return 0


def confidence_to_hsl(confidence):
    percentage = confidence/100
    hue = 255/2 * percentage
    return "hsl(%s, 100%%, 30%%, 50%%)" % hue


class Converter:
    def __init__(self, hocr, settings=None, image_path=None):
        self.image_path = image_path
        self.document = None
        self.hocr = BeautifulSoup(hocr, "html.parser")
        self.output = BeautifulSoup("""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset='utf-8'>
                    <style>
                        #ocr_document { width: 100%; }
                        .ocr_page {
                            margin: 0 auto;
                            border: 1px solid black;
                        }
                    </style>
                </head>
            <body>
                <div id='ocr_document'></div>
            </body>
            </html>
        """, "html.parser")

        if not settings:
            self.settings = {
                "scaling_factor": 1,
                "html_output": "document"
            }
        else:
            self.settings = settings

    def get_median_line_height(self, lines):
        heights = []

        for line in lines:
            bbox = BBox2D(line.coordinates, mode=XYXY)
            heights.append(bbox.height)

        heights.sort()

        middle = int((len(heights) - 1) / 2)
        if len(heights) % 2:
            median_height = heights[middle]
        else:
            median_height = (heights[middle] + heights[middle + 1]) / 2.0

        return self.settings["scaling_factor"] * median_height

    def merge_words(self, word_ids, content=None):
        if len(word_ids) == 0:
            return

        words = []
        for id_ in word_ids:
            elem = self.hocr.find(id=id_)
            if not elem:
                continue
            words.append(elem)

        if len(words) == 0:
            return

        parent = None
        merged_id = None
        merged_content = []
        merged_confidence = []
        merged_bbox = {"top": [], "left": [], "bottom": [], "right": []}

        for i, word in enumerate(words):
            confidence = extract_confidence(word)
            parsed_word = Word(parent=None, hocr_html=word)
            coordinates = parsed_word.coordinates

            merged_content.append(word.string)
            merged_confidence.append(confidence)

            merged_bbox["left"].append(coordinates[0])
            merged_bbox["top"].append(coordinates[1])
            merged_bbox["right"].append(coordinates[2])
            merged_bbox["bottom"].append(coordinates[3])

            if i == 0:
                parent = word.parent
                merged_id = word["id"]

            word.decompose()

        new_content = " ".join(merged_content)
        new_confidence = min(merged_confidence)
        new_bbox = {
            "top": min(merged_bbox["top"]),
            "left": min(merged_bbox["left"]),
            "bottom": max(merged_bbox["bottom"]),
            "right": max(merged_bbox["right"])
        }

        new_word = self.output.new_tag("span")
        new_word["id"] = merged_id
        new_word["class"] = "ocrx_word"

        if content:
            new_word.append(content)
            new_word["title"] = "bbox %s %s %s %s; x_wconf 100" % (
                new_bbox["left"], new_bbox["top"],
                new_bbox["right"], new_bbox["bottom"]
            )
        else:
            new_word.append(new_content)
            new_word["title"] = "bbox %s %s %s %s; x_wconf %s" % (
                new_bbox["left"], new_bbox["top"], new_bbox["right"],
                new_bbox["bottom"], new_confidence
            )

        parent.append(new_word)

    def create_pages(self):
        self.document = HOCRDocument(self.hocr.prettify())
        for page in self.document.pages:
            bbox = BBox2D(page.coordinates, mode=XYXY)
            height = self.settings["scaling_factor"] * bbox.height
            width = self.settings["scaling_factor"] * bbox.width

            page_div = self.output.new_tag("div")
            page_div["class"] = "ocr_page"
            page_div["style"] = """
                height: %spx;
                width: %spx;
                position: relative;
            """ % (height, width)

            for area in page.areas:
                area_div = self.create_child_elem(area, "ocr_area")
                page_div.append(area_div)
                for paragraph in area.paragraphs:
                    paragraph_div = self.create_child_elem(paragraph, "ocr_paragraph")
                    area_div.append(paragraph_div)
                    median_line_height = self.get_median_line_height(paragraph.lines)
                    for line in paragraph.lines:
                        line_div = self.create_child_elem(line, "ocr_line")
                        paragraph_div.append(line_div)
                        for word in line.words:
                            word_span = self.create_child_elem(word, "ocr_word", median_line_height)
                            line_div.append(word_span)

            container = self.output.find(id="ocr_document")
            container.append(page_div)

    def create_child_elem(self, hocr_obj, class_name, median_line_height=None):
        if class_name == "ocr_word":
            element = self.output.new_tag("span")
        else:
            element = self.output.new_tag("div")

        element["id"] = hocr_obj.id
        element["class"] = class_name
        self.set_position(hocr_obj, element)
        self.set_dimensons(hocr_obj, element)

        if class_name == "ocr_word":
            bbox = BBox2D(hocr_obj.coordinates, mode=XYXY)
            #self.add_bboxed_image_to_dataset(element, bbox)
            element.append(hocr_obj.ocr_text)
            confidence = extract_confidence(hocr_obj._hocr_html)
            element["data-confidence"] = confidence
            element["style"] += """
                font-size: %spx;
            """ % (0.8*median_line_height)

        return element

    def add_bbox_to_dataset(self, element, bbox):
        scaling_factor = self.settings["scaling_factor"]

        element["data-bbox-width"] = bbox.width
        element["data-bbox-height"] = bbox.height
        element["data-bbox-top"] = bbox.top
        element["data-bbox-left"] = bbox.left
        element["data-bbox-bottom"] = bbox.bottom
        element["data-bbox-right"] = bbox.right

        element["data-scaled-bbox-width"] = scaling_factor * bbox.width
        element["data-scaled-bbox-height"] = scaling_factor * bbox.height
        element["data-scaled-bbox-top"] = scaling_factor * bbox.top
        element["data-scaled-bbox-left"] = scaling_factor * bbox.left
        element["data-scaled-bbox-bottom"] = scaling_factor * bbox.bottom
        element["data-scaled-bbox-right"] = scaling_factor * bbox.right

    def add_bboxed_image_to_dataset(self, element, bbox):
        img = Image.open(self.image_path)
        box = (bbox.left, bbox.top, bbox.right, bbox.bottom)
        bboxed_image = img.crop(box)
        buffered = BytesIO()
        bboxed_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        element["data-element-image"] = "data:image/png;base64," + img_str

    def set_position(self, hocr_obj, element):
        scaling_factor = self.settings["scaling_factor"]
        parent = hocr_obj.parent
        child_coordinates = hocr_obj.coordinates

        if not parent:
            bbox = BBox2D(child_coordinates, mode=XYXY)
            left = scaling_factor * bbox.left
            top = scaling_factor * bbox.top
        else:
            parent_bbox = parent.coordinates
            left = scaling_factor * (child_coordinates[0] - parent_bbox[0])
            top = scaling_factor * (child_coordinates[1] - parent_bbox[1])

        element["style"] = """
            position: absolute;
            top: %spx;
            left: %spx;
            overflow: visible;
            white-space: nowrap;
        """ % (top, left)

    def set_dimensons(self, hocr_obj, element):
        scaling_factor = self.settings["scaling_factor"]

        bbox = BBox2D(hocr_obj.coordinates, mode=XYXY)
        width = scaling_factor * bbox.width
        height = scaling_factor * bbox.height

        element["style"] += """
            height: %spx;
            width: %spx;
        """ % (height, width)


if __name__ == "__main__":
    import sys
    hocr_file = sys.argv[1]
    outfile = hocr_file.rsplit(".", 1)[0] + "_converted.html"

    with open(hocr_file) as f:
        hocr_data = f.read()

    products = [
    ]

    c = Converter(hocr_data, {"scaling_factor": 1})

    for product in products:
        c.merge_words(product["hocr_name_ids"])

    c.create_pages()
    with open(outfile, "w") as f:
        f.write(c.output.prettify())
    #print(c.output.prettify())
