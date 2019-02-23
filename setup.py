#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

REQUIREMENTS = [
    "beautifulsoup4",
    "pillow",
    "hocr_parser"
]

setup(
    name="hocr-converter",
    version="0.1",
    author="jlieth",
    license="GNU General Public License v3 (GPLv3)",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.5",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
)

