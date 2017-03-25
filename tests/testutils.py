import os
import sys

import pytest

TEST_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(TEST_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")


slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


def init():
    if SRC_DIR not in sys.path:
        sys.path.insert(0, SRC_DIR)
