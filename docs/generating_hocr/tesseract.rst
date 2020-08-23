Tesseract
=========

`Tesseract <https://github.com/tesseract-ocr/tesseract>`_ is probably the most
commonly used open-source OCR engine.

Using Tesseract to create hOCR files
------------------------------------
Given an image `<image.jpg>`, you can instruct Tesseract to run OCR and create
an hOCR output file `<output.hocr>` like this::
    
    tesseract image.jpg output hocr

There are a large number of options to improve Tesseract's recognition
performance. Most importantly, I suppose, is specifying the language of the
text in the image as well as the kind of page layout Tesseract should expect.

Language
^^^^^^^^
You can check which languages your Tesseract supports with::
    
    tesseract --list-langs

The language can be given with the `-l <language>` option.::

    tesseract -l eng image.jpg output hocr


Page layout
^^^^^^^^^^^
