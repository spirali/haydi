# coding=utf-8

import os
import sys
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(ROOT_DIR, "docs/source")

sys.path.append(DOC_DIR)
from conf import version  # noqa


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="haydi",
    version=str(version),
    author="Stanislav Böhm",
    author_email="stanislav.bohm@vsb.cz",
    description="Generator and enumerator for automata related problems",
    license="MIT",
    keywords="dpda map reduce",
    url="http://haydi.readthedocs.io",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['distributed', 'monotonic', 'futures'],
    long_description=read('README.md'),
)
