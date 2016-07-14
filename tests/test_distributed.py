import os
import pytest
import signal
import time

from subprocess import Popen, PIPE

from testutils import init, SRC_DIR
init()

from qit import Range   # noqa
from qit.base.session import session  # noqa
from qit.base.runtime.distributedcontext import DistributedContext  # noqa


class DCluster(object):

    def __init__(self, port):
        self.sched_proc = None
        self.worker_procs = None
        self.port = port

    def start(self, n_workers):
        self.sched_proc = Popen(["dscheduler", "--host", "127.0.0.1",
                            "--port", str(self.port)],
                           stdout=PIPE, stderr=PIPE)

        time.sleep(0.3)  # wait for the scheduler to spawn

        env = os.environ.copy()
        pythonpath = env["PYTHONPATH"] if "PYTHONPATH" in env else ""
        env["PYTHONPATH"] = "{}:{}".format(pythonpath, SRC_DIR)

        self.worker_procs = [
            Popen(["dworker", "--nprocs", "1", "--nthreads", "1",
                   "127.0.0.1:{}".format(self.port)],
                  env=env,
                  stdout=PIPE, stderr=PIPE)
            for _ in xrange(4)]

        time.sleep(1.5)  # wait for the workers to spawn

        session.set_parallel_context(DistributedContext(
            n_workers=n_workers, port=self.port))
        assert len(session.parallel_context.executor.ncores()) == n_workers

    def stop(self):
        if self.sched_proc:
            # Checkt that processes are still running
            assert not self.sched_proc.poll()
        if self.worker_procs:
            assert not any(w.poll() for w in self.worker_procs)

            for p in self.worker_procs:
                p.kill()

        if self.sched_proc:
            self.sched_proc.kill()

        self.sched_proc = None
        self.worker_procs = None


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
    i = x.map(lambda x: x * 10).filter(lambda x: x < 600)
    result = i.run(True)
    expect = i.run(False)
    assert result == expect
