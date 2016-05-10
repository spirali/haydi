import os
import pytest
import signal
import time

from subprocess import Popen, PIPE

from testutils import init, SRC_DIR
init()

from qit import Range   # noqa
from qit.base.session import session  # noqa
from qit.base.runtime.distributedcontext import DistributedContext, \
    DistributedConfig   # noqa


@pytest.fixture(scope="module", autouse=True)
def distributed_init():
    import logging
    logging.disable(logging.INFO)


@pytest.fixture(scope="function")
def port():
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()

    return port


def test_create_cluster(port):
    session.set_parallel_context(DistributedContext(
        DistributedConfig(worker_count=4, port=port,
                          spawn_compute_nodes=True)))

    count = 10000
    x = Range(count)
    result = x.iterate().map(lambda x: x + 1).collect().run(True)

    assert result == [item + 1 for item in xrange(count)]


def test_connect_to_cluster(port):
    try:
        sched_proc = Popen(["dscheduler", "--host", "127.0.0.1",
                            "--port", str(port)],
                           stdout=PIPE, stderr=PIPE
                           )

        time.sleep(1)  # wait for the scheduler to spawn

        env = os.environ.copy()
        pythonpath = env["PYTHONPATH"] if "PYTHONPATH" in env else ""
        env["PYTHONPATH"] = "{}:{}".format(pythonpath, SRC_DIR)

        worker_proc = [
            Popen(["dworker", "--nprocs", "1", "--nthreads", "1",
                   "127.0.0.1:{}".format(port)],
                  env=env,
                  stdout=PIPE, stderr=PIPE
                  )
            for _ in xrange(4)]

        time.sleep(2)  # wait for the workers to spawn

        session.set_parallel_context(DistributedContext(DistributedConfig(
            worker_count=4, port=port, spawn_compute_nodes=False
        )))

        count = 10000
        x = Range(count)
        result = x.iterate().map(lambda x: x + 1).collect().run(True)

        assert result == [item + 1 for item in xrange(count)]
    finally:
        # kill processes "nicely"
        [p.send_signal(signal.SIGINT) for p in worker_proc]
        sched_proc.send_signal(signal.SIGINT)