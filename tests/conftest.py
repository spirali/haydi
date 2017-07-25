import os
import sys
import pytest

TEST_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")


if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
                     help="run slow tests")


def pytest_runtest_setup(item):
    """Skip tests if they are marked as slow and --runslow is not given"""
    if getattr(item.obj, 'slow', None) and not item.config.getvalue('runslow'):
        pytest.skip('slow tests not requested')
