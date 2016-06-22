import pytest

from qit.base.runtime.processcontext import ProcessContext
from qit.base.session import session
from testutils import init
init()

import qit  # noqa
from qit.base.exception import TooManySplits  # noqa


@pytest.fixture(scope="function", autouse=True)
def set_parallel_context():
    session.set_parallel_context(ProcessContext())


def test_auto_split():
    r = qit.Range(10000).iterate()\
        .filter(lambda x: x % 2 == 0)\
        .map(lambda x: x + 1)\
        .collect().run(parallel=True)

    assert set(r) == set([x + 1 for x in xrange(10000) if x % 2 == 0])


def test_manual_split():
    r = qit.Range(10000).iterate().split(4)\
        .filter(lambda x: x % 2 == 0)\
        .map(lambda x: x + 1)\
        .collect().run(parallel=True)

    assert set(r) == set([x + 1 for x in xrange(10000) if x % 2 == 0])


def test_too_many_splits():
    with pytest.raises(TooManySplits):
        qit.Range(100).iterate().split(4).map(lambda x: x)\
            .split(2).map(lambda x: x).collect().run(parallel=True)


def test_parallel_take():
    r = qit.Range(1000).iterate().take(50).map(lambda x: x + 1).\
        collect().run(parallel=True)
    assert set(r) == set([x + 1 for x in xrange(50)])
