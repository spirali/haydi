from datetime import timedelta

import pytest
import random

from testutils import init
init()

from haydi import Range   # noqa
from haydi import session  # noqa
from haydi.base.runtime.distributedcontext import DistributedContext  # noqa
import haydi as hd # noqa


class DCluster(object):

    def __init__(self, port):
        self.port = port
        self.cluster = None

    def start(self, n_workers):
        import distributed

        self.cluster = distributed.LocalCluster(
            n_workers=n_workers,
            threads_per_worker=1,
            scheduler_port=self.port,
            diagnostics_port=None
        )

        session.set_parallel_context(DistributedContext(port=self.port))
        assert len(session.parallel_context.executor.ncores()) == n_workers

    def stop(self):
        if self.cluster:
            self.cluster.close()


@pytest.yield_fixture(scope="module", autouse=True)
def cluster4():
    c = DCluster(9021)
    c.start(4)
    yield c
    c.stop()


def test_dist_map(cluster4):
    count = 10000
    x = Range(count)
    result = x.map(lambda x: x + 1).collect().run(True)

    assert result == [item + 1 for item in xrange(count)]


def test_dist_filter(cluster4):
    x = Range(211)
    y = x * x
    i = y.map(lambda x: x * 10).filter(lambda x: x < 600)
    result = i.run(True)
    expect = i.run(False)
    assert result == expect


def test_dist_simple_take(cluster4):
    x = Range(10).take(3)
    result = x.run(True)
    assert result == [0, 1, 2]


def test_dist_take_filter(cluster4):
    x = Range(10).filter(lambda x: x > 5).take(3)
    result = x.run(True)
    assert result == [6, 7, 8]


def test_dist_generate(cluster4):
    x = Range(10).generate(100)
    result = x.run(True)
    assert len(result) == 100
    for i in result:
        assert 0 <= i < 10


def test_dist_samples(cluster4):
    a = ["A"] * 200 + ["B"] * 100 + ["C"] * 3 + ["D"] * 10
    random.shuffle(a)

    result = hd.Values(a).groups(lambda x: x, 1).run(True)
    assert {"A": ["A"], "B": ["B"], "C": ["C"], "D": ["D"]} == result

    result = hd.Values(a).groups(lambda x: x, 10).run(True)
    expected = {"A": ["A"] * 10,
                "B": ["B"] * 10,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups(lambda x: x, 150).run(True)
    expected = {"A": ["A"] * 150,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups(lambda x: x, 1500).run(True)
    expected = {"A": ["A"] * 200,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected


def test_dist_samples_and_counts(cluster4):
    a = ["A"] * 200 + ["B"] * 100 + ["C"] * 3 + ["D"] * 10
    random.shuffle(a)

    result = hd.Values(a).groups_counts(lambda x: x, 1).run(True)
    assert {"A": [200, "A"], "B": [100, "B"], "C": [3, "C"],
            "D": [10, "D"]} == result

    result = hd.Values(a).groups_counts(lambda x: x, 10).run(True)
    expected = {"A": [200] + ["A"] * 10,
                "B": [100] + ["B"] * 10,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups_counts(lambda x: x, 150).run(True)
    expected = {"A": [200] + ["A"] * 150,
                "B": [100] + ["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups_counts(lambda x: x, 1500).run(True)
    expected = {"A": [200] + ["A"] * 200,
                "B": [100] + ["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected


def test_dist_timeout(cluster4):
    r = hd.Range(1000000)

    def fn(x):
        return sum([i for i in xrange(x * x)])

    result = r.map(fn).max_all(lambda x: x).run(
        True, timeout=timedelta(seconds=6))
    assert result is not None
    assert result > 0
