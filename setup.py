#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

REQUIREMENTS = ["lxml", "cssselect"]

DEV_REQUIREMENTS = [
    "tox",
    "pytest",
    "pytest-mock",
    "pytest-random-order",
    "pytest-mypy",
    "pytest-flake8",
    "pytest-black",
    "pytest-cov",
    "lxml-stubs",
]

setup(
    name="hocr-parser",
    version="0.3.0",
    author="jlieth",
    license="GNU General Public License v3 (GPLv3)",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.6",
    install_requires=REQUIREMENTS,
    tests_require=DEV_REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
)
