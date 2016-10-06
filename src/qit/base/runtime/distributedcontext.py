import os
from threading import Thread
from datetime import datetime
import time
import itertools
import logging
import socket
import resource
import collections

import math

from qit.base.exception import QitException
from qit.base.iterator import NoValue

try:
    import cloudpickle
    from distributed import Scheduler, Nanny as Worker, Executor, as_completed
    from tornado.ioloop import IOLoop

    DistributedImportError = None
except Exception as e:
    DistributedImportError = e


class ResultSaver(object):
    def __init__(self, id, write_count):
        """
        :type id: int
        :type write_count: int
        """
        self.time = datetime.now()
        self.id = id
        self.write_count = write_count
        self.results = []
        self.counter = 0

    def handle_result(self, result):
        self.results.append(result)

        if len(self.results) % self.write_count == 0:
            self._write_partial_result(self.results, self.counter)
            self.results = []
            self.counter += 1

    def _write_partial_result(self, results, counter):
        filename = "pyqit-{}-{}-{}".format(
                int(time.mktime(self.time.timetuple())),
                self.id,
                counter)
        with open(filename, "w") as f:
            cloudpickle.dump(results, f)
        logging.info("Qit: Writing file {} ({} results)".format(
            filename, len(results)))


class TimeoutManager(object):
    def __init__(self, timeout):
        """
        :type timeout: int
        """
        self.timeout = timeout
        self.start = datetime.now()

    def is_finished(self):
        return (datetime.now() - self.start).seconds >= self.timeout


class Job(object):
    def __init__(self, worker_id, start_index, size):
        """
        :type worker_id: str
        :type start_index: int
        :type size: int
        """
        self.worker_id = worker_id
        self.start_index = start_index
        self.size = size
        self.result = None
        self.start_time = datetime.now()
        self.end_time = None
        self.memory_snapshot = None

    def finish(self, result):
        self.result = result
        self.end_time = datetime.now()
        self.memory_snapshot = resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss

    def get_duration(self):
        return (self.end_time - self.start_time).total_seconds()


class JobScheduler(object):
    """
    Creates computational graphs for distributed and iterates through them.
    Can be limited by domain size or timeout.
    """
    def __init__(self,
                 executor,
                 worker_count,
                 timeout,
                 domain,
                 worker_reduce_fn,
                 worker_reduce_init):
        """
        :param executor: distributed executor
        :param worker_count: number of workers in the cluster
        :param timeout: timeout in seconds
        :param domain: domain to be iterated
        :param worker_reduce_fn:
        :param worker_reduce_init:
        """
        self.executor = executor
        self.worker_count = worker_count
        self.size = domain.steps
        self.domain = domain
        self.worker_reduce_fn = worker_reduce_fn
        self.worker_reduce_init = worker_reduce_init
        self.job_histogram = collections.deque(maxlen=10)
        self.index_scheduled = 0
        self.index_completed = 0
        self.batch_size = None
        self.timeout_mgr = TimeoutManager(timeout) if timeout else None
        self.ordered_futures = []
        self.active_futures = self._create_first_batch()
        # <made-up amount> of minutes per batch is "optimal"
        self.target_time = 60 * 2

    def iterate_jobs(self):
        """
        Iterate through all jobs until the domain size is depleted or
        time runs out.
        :return: completed future
        """
        for future in as_completed(self.active_futures):
            job = future.result()
            self._add_job(job)
            yield future

            if self.timeouted():
                return
        self._schedule()
        if self._has_more_work():
            self.active_futures = self._schedule()
            for future in self.iterate_jobs():
                yield future

    def timeouted(self):
        return self.timeout_mgr and self.timeout_mgr.is_finished()

    def _schedule(self):
        """
        Adjust batch size according to the average duration of recent jobs
        and create new futures.
        :rtype: list of distributed.client.Future
        :return: newly scheduled futures
        """
        duration = self._get_avg_duration()
        delta = duration / float(self.target_time)
        delta = self._clamp(delta, 0.1, 1.2)
        self.batch_size = int(self.batch_size / delta)

        return self._create_futures(self._get_batch_count(), self.batch_size)

    def _clamp(self, value, minimum, maximum):
        return min(maximum, max(minimum, value))

    def _get_avg_duration(self):
        total_duration = sum([j.get_duration() for j in self.job_histogram])
        return total_duration / float(len(self.job_histogram))

    def _create_first_batch(self):
        batch_count = self._get_batch_count()

        if self.size:
            total_size = int(math.ceil(self.size / float(batch_count)))
            if total_size < 100:
                self.batch_size = total_size
            else:
                self.batch_size = min(total_size, self._batch_size(0.05))
        else:
            self.batch_size = self._batch_size(0.01)

        return self._create_futures(batch_count, self.batch_size)

    def _get_batch_count(self):
        return self.worker_count * 4

    def _create_futures(self, batch_count, batch_size):
        batches = self._create_batches(batch_count, batch_size)
        futures = self.executor.map(process_batch, batches)
        self.ordered_futures += futures
        return futures

    def _add_job(self, job):
        self.job_histogram.append(job)
        self.index_completed += job.size

    def _has_more_work(self):
        return not self.size or self.index_completed < self.size

    def _batch_size(self, percent):
        if self.size:
            return int(self.size * percent)
        else:
            return int(percent * 1000)

    def _create_batches(self, count, batch_size):
        batches = []
        for _ in xrange(count):
            start = self.index_scheduled
            batches.append((self.domain, start, batch_size,
                            self.worker_reduce_fn, self.worker_reduce_init))
            self.index_scheduled = start + batch_size

        return batches


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
    io_loop = None
    io_thread = None

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

        if DistributedImportError:
            raise QitException("distributed must be properly installed in "
                               "order to use the DistributedContext\n"
                               "Error:\n{}"
                               .format(DistributedImportError))

        self.worker_count = spawn_workers
        self.ip = ip
        self.port = port
        self.active = False
        self.write_partial_results = write_partial_results
        self.execution_count = 0

        if not DistributedContext.io_loop:
            DistributedContext.io_loop = IOLoop()
            DistributedContext.io_thread = Thread(
                target=DistributedContext.io_loop.start)
            DistributedContext.io_thread.daemon = True
            DistributedContext.io_thread.start()

        if spawn_workers > 0:
            self.scheduler = self._create_scheduler()
            self.workers = [self._create_worker()
                            for i in xrange(spawn_workers)]
            time.sleep(0.5)  # wait for workers to spawn

        self.executor = Executor((ip, port))

    def run(self, domain,
            worker_reduce_fn, worker_reduce_init,
            global_reduce_fn, global_reduce_init,
            timeout=None):
        size = domain.steps

        if self.write_partial_results is not None:
            result_saver = ResultSaver(self.execution_count,
                                       self.write_partial_results)
        else:
            result_saver = None

        scheduler = JobScheduler(self.executor, self._get_worker_count(),
                                 timeout, domain,
                                 worker_reduce_fn, worker_reduce_init)

        results = []
        for future in scheduler.iterate_jobs():
            result = future.result().result
            results.append(result)
            if result_saver:
                result_saver.handle_result(result)

        # order the results if not timeouted
        if not scheduler.timeouted():
            results = [j.result for j in self.executor.gather(
                scheduler.ordered_futures)]

        self.execution_count += 1

        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        if size:
            logging.info("Qit: finished run with size {} (taking {})".format(
                len(results), domain.size))

            results = results[:domain.size]  # trim results to required size
        else:
            logging.info("Qit: finished run")

        if global_reduce_fn is None:
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
            raise QitException("There are no workers")

        return workers

    def _create_scheduler(self):
        scheduler = Scheduler(ip=self.ip)
        scheduler.start(self.port)
        return scheduler

    def _create_worker(self):
        worker = Worker(self.ip,
                        self.port,
                        ncores=1)
        worker.start(0)
        return worker


def process_batch(arg):
    """
    :param arg:
    :rtype: Job
    """
    domain, start, size, reduce_fn, reduce_init = arg
    job = Job("{}#{}".format(socket.gethostname(), os.getpid()), start, size)

    iterator = domain.create_iterator()
    iterator.set_step(start)

    def item_generator():
        for i in xrange(size):
            item = iterator.step()
            if item is not NoValue:
                yield item

    if reduce_fn is None:
        result = list(item_generator())
    else:
        if reduce_init is None:
            result = reduce(reduce_fn, item_generator())
        else:
            result = reduce(reduce_fn, item_generator(), reduce_init())

    job.finish(result)
    return job
