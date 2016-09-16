import os
import pytest
import time
import random

from subprocess import Popen, PIPE

import signal

from testutils import init, SRC_DIR
init()

from qit import Range   # noqa
from qit import session  # noqa
from qit.base.runtime.distributedcontext import DistributedContext, \
    JobObserver  # noqa
import qit  # noqa


class DCluster(object):

    def __init__(self, port):
        self.sched_proc = None
        self.worker_proc = None
        self.port = port

    def start(self, n_workers):
        self.sched_proc = Popen(["dscheduler", "--host", "127.0.0.1",
                                 "--port", str(self.port)],
                                stdout=PIPE, stderr=PIPE)

        time.sleep(0.3)  # wait for the scheduler to spawn

        env = os.environ.copy()
        pythonpath = env["PYTHONPATH"] if "PYTHONPATH" in env else ""
        env["PYTHONPATH"] = "{}:{}".format(pythonpath, SRC_DIR)

        self.worker_proc = Popen(["dworker", "--nprocs",
                                  str(n_workers), "--nthreads", "1",
                                  "127.0.0.1:{}".format(self.port)],
                                 env=env,
                                 stdout=PIPE, stderr=PIPE)

        time.sleep(1.5)  # wait for the workers to spawn

        session.set_parallel_context(DistributedContext(port=self.port))
        assert len(session.parallel_context.executor.ncores()) == n_workers

    def stop(self):
        if self.sched_proc:
            # Check that processes are still running
            assert not self.sched_proc.poll()
        if self.worker_proc:
            assert not self.worker_proc.poll()
            os.kill(self.worker_proc.pid, signal.SIGINT)

        if self.sched_proc:
            os.kill(self.sched_proc.pid, signal.SIGINT)

        self.sched_proc = None
        self.worker_proc = None


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

    result = qit.Values(a).samples(lambda x: x, 1).run(True)
    assert {"A": ["A"], "B": ["B"], "C": ["C"], "D": ["D"]} == result

    result = qit.Values(a).samples(lambda x: x, 10).run(True)
    expected = {"A": ["A"] * 10,
                "B": ["B"] * 10,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = qit.Values(a).samples(lambda x: x, 150).run(True)
    expected = {"A": ["A"] * 150,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

    result = qit.Values(a).samples(lambda x: x, 1500).run(True)
    expected = {"A": ["A"] * 200,
                "B": ["B"] * 100,
                "C": ["C"] * 3,
                "D": ["D"] * 10}
    assert result == expected

def test_dist_samples_and_counts(cluster4):
    a = ["A"] * 200 + ["B"] * 100 + ["C"] * 3 + ["D"] * 10
    random.shuffle(a)

    result = qit.Values(a).samples_and_counts(lambda x: x, 1).run(True)
    assert {"A": [200, "A"], "B": [100, "B"], "C": [3, "C"], "D": [10, "D"]} == result

    result = qit.Values(a).samples_and_counts(lambda x: x, 10).run(True)
    expected = {"A": [200] + ["A"] * 10,
                "B": [100] + ["B"] * 10,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = qit.Values(a).samples_and_counts(lambda x: x, 150).run(True)
    expected = {"A": [200] + ["A"] * 150,
                "B": [100] +["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected

    result = qit.Values(a).samples_and_counts(lambda x: x, 1500).run(True)
    expected = {"A": [200] + ["A"] * 200,
                "B": [100] + ["B"] * 100,
                "C": [3] + ["C"] * 3,
                "D": [10] + ["D"] * 10}
    assert result == expected




def test_dist_observer(cluster4):
    size = 1024

    class Observer(JobObserver):
        def __init__(self):
            self.batch_count = None
            self.jobs = []

        def on_computation_start(self, batch_count, batch_size):
            self.batch_count = batch_count
            assert batch_count * batch_size == size

        def on_job_completed(self, job):
            self.jobs.append(job)

    observer = Observer()
    session.parallel_context.job_observer = observer

    qit.Range(size).map(lambda x: x + 1).run(True)
    assert observer.batch_count == len(observer.jobs)
