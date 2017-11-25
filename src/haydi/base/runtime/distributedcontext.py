from __future__ import print_function

import itertools
import os
import socket
import time
from Queue import Empty
from datetime import timedelta

from haydi.base.exception import HaydiException, TimeoutException

try:
    from distributed import Client, LocalCluster
    from distributed.http import HTTPScheduler

    from .strategy import StepStrategy, PrecomputeStrategy, GeneratorStrategy
    from .trace import OTFTracer, Tracer

    from .scheduler import JobScheduler
    from .util import haydi_logger, ProgressLogger, TimeoutManager

    package_import_error = None
except ImportError as e:
    package_import_error = e


def check_package_requirements():
    if package_import_error:
        raise HaydiException("Packages 'distributed' and 'monotonic' must "
                             "be properly installed in "
                             "order to use the DistributedContext\n"
                             "Error:\n{}"
                             .format(package_import_error))


def get_worker_count(executor):
    workers = 0
    for name, value in executor.ncores().items():
        workers += value

    if workers == 0:
        raise HaydiException("There are no workers")

    return workers


def create_strategy(pipeline, timeout=None):
    if pipeline.method == "generate":
        return GeneratorStrategy(pipeline, timeout)
    elif pipeline.method == "iterate" and pipeline.domain.step_jumps:
        return StepStrategy(pipeline, timeout)
    else:
        return PrecomputeStrategy(pipeline, timeout)


class DistributedContext(object):
    """
    Parallel context that uses the
    `distributed <http://distributed.readthedocs.io>`_ library to distribute
    work amongst workers in a cluster to speed up the computation.

    It can either connect to an already running cluster or create a local one.
    If a local cluster is created, every worker will be spawned in a single
    process with one thread.

    Partial results can be saved to disk during the computation
    to avoid losing all results if the program ends abruptly.

    Args:
        ip (string): IP address of a distributed cluster
        port (int): TCP port of a distributed cluster
        spawn_workers (int):
            - If `spawn_workers` is ``0``
                - connect to an existing cluster located at (ip, port)
            - If `spawn_workers` is ``n``
                - create a local cluster with ``n`` workers
    """

    def __init__(self,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=0):
        """

        :type ip: string
        :param ip: IP of distributed scheduler
        :type port: int
        :param port: port of distributed scheduler
        :type spawn_workers: int
        :param spawn_workers: True if a computation cluster should be spawned
        """

        check_package_requirements()

        self.worker_count = spawn_workers
        self.ip = ip
        self.port = port
        self.active = False

        if spawn_workers > 0:
            self.cluster = LocalCluster(ip=ip,
                                        scheduler_port=port,
                                        n_workers=spawn_workers,
                                        threads_per_worker=1,
                                        diagnostics_port=None,
                                        services={
                                            ("http", port + 1): HTTPScheduler
                                        })
            self.executor = Client(self.cluster)
        else:
            self.executor = Client((ip, port))

    def run(self,
            pipeline,
            timeout=None,
            otf_trace=False):

        if otf_trace:
            tracer = OTFTracer("otf-{}".format(int(time.time())))
        else:
            tracer = Tracer()

        worker_count = get_worker_count(self.executor)
        tracer.trace_workers(worker_count)

        strategy = create_strategy(pipeline, timeout)
        size = strategy.size

        name = "{} (pid {})".format(socket.gethostname(), os.getpid())
        start_msg = "Starting run with size {} and worker count {} on {}". \
            format(size, worker_count, name)
        haydi_logger.info(start_msg)

        scheduler = JobScheduler(self.executor,
                                 worker_count,
                                 strategy,
                                 timeout,
                                 tracer)

        jobs = self._run_computation(scheduler, timeout)
        results = [job.result for job in jobs]

        action = pipeline.action

        if action.worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        if pipeline.take_count:
            results = results[:pipeline.take_count]

        haydi_logger.info("Size of domain: {}".format(pipeline.domain.size))
        tracer.trace_finish()

        if action.global_reduce_fn is None or len(results) == 0:
            return results
        else:
            if action.global_reduce_init is None:
                return reduce(action.global_reduce_fn, results)
            else:
                return reduce(action.global_reduce_fn, results,
                              action.global_reduce_init())

    def _run_computation(self, scheduler, timeout):
        progress_logger = ProgressLogger(timedelta(seconds=10))
        jobs = []
        timeout_mgr = TimeoutManager(timeout) if timeout else None

        def consume_job():
            job = scheduler.job_queue.get(block=False)
            jobs.append(job)
            progress_logger.handle_job(scheduler, job)

        def is_timeouted():
            return timeout_mgr and timeout_mgr.is_finished()

        scheduler.start()

        try:
            while not (scheduler.completed or scheduler.canceled):
                if is_timeouted():
                    raise TimeoutException()

                try:
                    consume_job()
                except Empty:
                    time.sleep(3)

            # extract remaining jobs
            while True:
                try:
                    consume_job()
                except Empty:
                    break

        except KeyboardInterrupt:
            pass
        except TimeoutException:
            haydi_logger.info("Run timeouted after {} seconds".format(
                timeout_mgr.get_time_from_start()))

        scheduler.stop()

        # order the results
        jobs.sort(key=lambda job: job.start_index)

        self._log_statistics(scheduler, jobs)

        return jobs

    def _log_statistics(self, scheduler, jobs):
        haydi_logger.info("Total scheduled: {}".format(
            scheduler.index_scheduled))
        haydi_logger.info("Total completed: {}".format(
            scheduler.index_completed))

        size_hist = {}
        for job in jobs:
            if job.size not in size_hist:
                size_hist[job.size] = []
            size_hist[job.size].append(job.get_duration())

        for size, times in sorted(size_hist.iteritems(), key=lambda x: x[0]):
            count = len(times)
            haydi_logger.info("Batch size {} had {} jobs with avg time {}"
                              .format(size, count, sum(times) / float(count)))
