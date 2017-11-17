# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

description = "Command line application to visualize the timeline of Spark executions."

main_ns = {}
with open("viewsparktimeline/version.py") as ver_file:
    exec(ver_file.read(), main_ns)

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_descr = f.read()

setup(
    name="view-spark-timeline",
    version = main_ns['__version__'],

    description = description,
    long_description = long_descr,
    license = "MIT",
    url = "https://github.com/fpoli/view-spark-timeline",

    author = "Federico Poli",
    author_email = "federpoli@gmail.com",

    packages = find_packages(exclude=["tests"]),

    entry_points = {
        "console_scripts": [
            "view-spark-timeline = viewsparktimeline.cli:main"
        ]
    },

    install_requires = [
        "svgwrite==1.1.11",
        "ujson==1.35"
    ],
    extras_require = {
        "dev": [
            "twine==1.9.1",
            "nose==1.3.7",
            "pycodestyle==2.3.1"
        ]
    },

    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ]
)
