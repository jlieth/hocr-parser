# hocr-parser
Python parser for hOCR files using lxml

[![Build Status](https://travis-ci.org/jlieth/hocr-parser.svg?branch=master)](https://travis-ci.org/jlieth/hocr-parser)
[![codecov](https://codecov.io/gh/jlieth/hocr-parser/branch/master/graph/badge.svg)](https://codecov.io/gh/jlieth/hocr-parser)
[![Coverage Status](https://coveralls.io/repos/github/jlieth/hocr-parser/badge.svg?branch=master)](https://coveralls.io/github/jlieth/hocr-parser?branch=master)

hOCR is an open standard for representing the results of optical character
recognition (OCR). The results of OCR (the recognized text, layout, styles,
etc.) are represented in hOCR using XHTML. This Python module parses an
existing hOCR file and gives easy access to the hOCR elements and their
attributes.

## Install
Python 3.6+ is required, and you'll probably want to use some kind of
virtual environment to install this package. Until I push the package to
PyPi, you can install directly from Github with pip:

```
pip install git+https://github.com/jlieth/hocr-parser
```

## Similar projects
* [hocr-parser](https://github.com/athento/hocr-parser) by
  [Athento](https://github.com/athento), and its forks. Uses BeautifulSoup
  for parsing
* [hocr-tools](https://github.com/ocropus/hocr-tools) by
  [OCRopus](https://github.com/ocropus). Not a parser exactly, but has
  several tools to work with hOCR files
* [hocr-spec-python](https://github.com/kba/hocr-spec-python) by 
  [Konstantin Baierer](https://github.com/kba), editor of the hOCR spec.
  hOCR validator written in Python.

## External links
* [hOCR spec 1.2](http://kba.cloud/hocr-spec/1.2/)
* [hOCR on Wikipedia](https://en.wikipedia.org/wiki/HOCR)
