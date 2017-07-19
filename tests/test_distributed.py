from datetime import timedelta

import pytest
import random

from testutils import init, slow

init()

from haydi import Range   # noqa
from haydi.base.runtime.distributedcontext import DistributedContext  # noqa
import haydi as hd  # noqa


class DCluster(object):

    def __init__(self, port):
        self.port = port
        self.cluster = None
        self.ctx = None

    def start(self, n_workers):
        import distributed

        self.cluster = distributed.LocalCluster(
            n_workers=n_workers,
            threads_per_worker=1,
            scheduler_port=self.port,
            diagnostics_port=None
        )

        self.ctx = DistributedContext(port=self.port)
        assert len(self.ctx.executor.ncores()) == n_workers

    def stop(self):
        if self.cluster:
            self.cluster.close()


@pytest.yield_fixture(scope="module", autouse=True)
def cluster4():
    c = DCluster(9021)
    c.start(4)
    yield c
    c.stop()


@slow
def test_dist_map(cluster4):
    count = 10000
    x = Range(count)
    result = x.map(lambda x: x + 1).collect().run(cluster4.ctx)

    assert result == [item + 1 for item in xrange(count)]


@slow
def test_dist_filter(cluster4):
    x = Range(211)
    y = x * x
    i = y.map(lambda x: x * 10).filter(lambda x: x < 600)
    result = i.run(cluster4.ctx)
    expect = i.run()
    assert result == expect


@slow
def test_dist_simple_take(cluster4):
    x = Range(10).take(3)
    result = x.run(cluster4.ctx)
    assert result == [0, 1, 2]


@slow
def test_dist_take_filter(cluster4):
    x = Range(10).filter(lambda x: x > 5).take(3)
    result = x.run(cluster4.ctx)
    assert result == [6, 7, 8]


@slow
def test_dist_generate(cluster4):
    x = Range(10).generate(100)
    result = x.run(cluster4.ctx)
    assert len(result) == 100
    for i in result:
        assert 0 <= i < 10


@slow
def test_dist_samples(cluster4):
    a = ["A"] * 200 + ["B"] * 100 + ["C"] * 3 + ["D"] * 10
    random.shuffle(a)

    result = hd.Values(a).groups(lambda x: x, 1).run(cluster4.ctx)
    assert {"A": ["A"], "B": ["B"], "C": ["C"], "D": ["D"]} == result

    result = hd.Values(a).groups(lambda x: x, 10).run(cluster4.ctx)
    expected = {"A": ["A"] * 10,
                "B": ["B"] * 10,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups(lambda x: x, 150).run(cluster4.ctx)
    expected = {"A": ["A"] * 150,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups(lambda x: x, 1500).run(cluster4.ctx)
    expected = {"A": ["A"] * 200,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected


@slow
def test_dist_samples_and_counts(cluster4):
    a = ["A"] * 200 + ["B"] * 100 + ["C"] * 3 + ["D"] * 10
    random.shuffle(a)

    result = hd.Values(a).groups_counts(lambda x: x, 1).run(cluster4.ctx)
    assert {"A": [200, "A"], "B": [100, "B"], "C": [3, "C"],
            "D": [10, "D"]} == result

    result = hd.Values(a).groups_counts(lambda x: x, 10).run(cluster4.ctx)
    expected = {"A": [200] + ["A"] * 10,
                "B": [100] + ["B"] * 10,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups_counts(lambda x: x, 150).run(cluster4.ctx)
    expected = {"A": [200] + ["A"] * 150,
                "B": [100] + ["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = hd.Values(a).groups_counts(lambda x: x, 1500).run(cluster4.ctx)
    expected = {"A": [200] + ["A"] * 200,
                "B": [100] + ["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected


@slow
def test_dist_timeout(cluster4):
    r = hd.Range(100000)

    def fn(x):
        return sum(xrange(x * x))

    result = r.map(fn).max(lambda x: x).run(
        cluster4.ctx, timeout=timedelta(seconds=4))
    assert result is not None
    assert result > 0


@slow
def test_dist_precompute(cluster4):
    states = hd.ASet(2, "q")
    alphabet = hd.ASet(2, "a")

    delta = hd.Mappings(states * alphabet, states)
    r1 = delta.cnfs().run()
    r2 = delta.cnfs().run(cluster4.ctx)

    assert len(r1) == len(r2)
