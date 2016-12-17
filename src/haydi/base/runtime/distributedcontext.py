from __future__ import print_function

import itertools
import os
import socket
import time
from datetime import timedelta

from haydi.base.exception import HaydiException

try:
    import cloudpickle
    from distributed import Client, as_completed, LocalCluster
    from distributed.http import HTTPScheduler

    from .scheduler import JobScheduler
    from .util import haydi_logger, ResultSaver, ProgressLogger, Logger, \
        JobOffsetLogger

    distributed_import_error = None
except Exception as e:
    distributed_import_error = e


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
        write_partial_results (int):
            - If `write_partial_results` is ``None``
                - no partial results can be saved
            - If `write_partial_results` is ``n``
                - partial results are saved after every ``n-th`` job
    """

    def __init__(self,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=0,
                 write_partial_results=None):
        """

        :type ip: string
        :param ip: IP of distributed scheduler
        :type port: int
        :param port: port of distributed scheduler
        :type spawn_workers: int
        :param spawn_workers: True if a computation cluster should be spawned
        :type write_partial_results: int
        :param write_partial_results:
            n -> every n jobs a temporary result will be saved to disk
            None -> no temporary results will be stored
        """

        if distributed_import_error:
            raise HaydiException("distributed must be properly installed in"
                                 "order to use the DistributedContext\n"
                                 "Error:\n{}"
                                 .format(distributed_import_error))

        Logger.init_file_logger()

        self.worker_count = spawn_workers
        self.ip = ip
        self.port = port
        self.active = False
        self.write_partial_results = write_partial_results
        self.execution_count = 0

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

    def run(self, domain,
            worker_reduce_fn, worker_reduce_init,
            global_reduce_fn, global_reduce_init,
            timeout=None):
        size = domain.steps

        name = "{} (pid {})".format(socket.gethostname(), os.getpid())
        start_msg = "Starting run with size {} and worker count {} on {}".\
            format(size, self._get_worker_count(), name)

        haydi_logger.info(start_msg)

        scheduler = JobScheduler(self.executor,
                                 self._get_worker_count(),
                                 timeout, domain,
                                 worker_reduce_fn, worker_reduce_init)

        if self.write_partial_results is not None:
            result_saver = ResultSaver(self.execution_count,
                                       self.write_partial_results)
            scheduler.add_job_callback(result_saver.handle_job)

        progress_logger = ProgressLogger(timedelta(seconds=3))
        scheduler.add_job_callback(progress_logger.handle_job)

        try:
            jobs = scheduler.iterate_jobs()
        except KeyboardInterrupt:
            jobs = scheduler.completed_jobs

        # order the results
        start = time.time()
        jobs.sort(key=lambda job: job.start_index)
        results = [job.result for job in jobs]
        haydi_logger.info("Ordering took {} ms".format(time.time() - start))

        self.execution_count += 1

        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        if size:
            results = results[:domain.size]  # trim results to required size

        haydi_logger.info("Finished run with size {}".format(domain.size))
        haydi_logger.info("Iterated {} elements".format(
            sum([job.size for job in jobs])))

        if global_reduce_fn is None or len(results) == 0:
            return results
        else:
            if global_reduce_init is None:
                return reduce(global_reduce_fn, results)
            else:
                return reduce(global_reduce_fn, results, global_reduce_init())

    def _get_worker_count(self):
        workers = 0
        for name, value in self.executor.ncores().items():
            workers += value

        if workers == 0:
            raise HaydiException("There are no workers")

        return workers
