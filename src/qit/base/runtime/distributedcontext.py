import atexit
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

from distributed.http import HTTPScheduler

from qit.base.qitsession import session
from qit.base.exception import QitException
from qit.base.iterator import NoValue

try:
    import cloudpickle
    from distributed import Scheduler, Nanny as Worker, Executor,\
        as_completed, LocalCluster
    from tornado.ioloop import IOLoop

    DistributedImportError = None
except Exception as e:
    DistributedImportError = e


qitLogger = logging.getLogger("Qit")


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

    def __str__(self):
        return "Job(worker={}, from={}, to={}".format(
            self.worker_id,
            self.start_index,
            self.start_index + self.size)


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
        :type timeout: datetime.timedelta
        :param timeout: timeout for the computation
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
        self.index_scheduled = 0
        self.index_completed = 0
        self.job_size = None
        self.timeout_mgr = TimeoutManager(timeout.total_seconds())\
            if timeout else None
        self.ordered_futures = []
        self.backlog_per_worker = 4
        self.active_futures = self._init_futures(self.backlog_per_worker)
        self.next_futures = []
        # <made-up amount> of minutes per batch is "optimal"
        self.target_time = 60 * 2
        self.completed_jobs = []

    # davat joby do fronty po kazdem jobu
    def iterate_jobs(self):
        """
        Iterate through all jobs until the domain size is depleted or
        time runs out.
        :return: completed job
        """
        if len(self.next_futures) > 0:
            self.active_futures = self.next_futures
            self.next_futures = []

        iterated = 0
        for future in as_completed(self.active_futures):
            job = future.result()
            self._add_job(job)
            iterated += 1

            if self.timeouted():
                return self.completed_jobs

            if iterated / self.worker_count >= 2:
                if self._has_more_work():
                    self.next_futures += self._schedule(
                        self.backlog_per_worker / 2)

        if self._has_more_work():
            self.next_futures += self._schedule(self.backlog_per_worker / 2)
            return self.iterate_jobs()
        else:
            return self.completed_jobs

    def timeouted(self):
        return self.timeout_mgr and self.timeout_mgr.is_finished()

    def _schedule(self, count_per_worker):
        """
        Adjust batch size according to the average duration of recent jobs
        and create new futures.
        :param count_per_worker: how many jobs should be spawned per worker
        :rtype: list of distributed.client.Future
        :return: newly scheduled futures
        """
        duration = self._get_avg_duration()
        delta = duration / float(self.target_time)
        delta = self._clamp(delta, 0.1, 1.2)
        self.job_size = int(self.job_size / delta)

        return self._create_futures(self._create_distribution(
            self.worker_count * count_per_worker, self.job_size))

    def _clamp(self, value, minimum, maximum):
        return min(maximum, max(minimum, value))

    def _get_avg_duration(self):
        job_histogram = self.completed_jobs[-10:]
        total_duration = sum([j.get_duration() for j in job_histogram])
        return total_duration / float(len(job_histogram))

    def _init_futures(self, count_per_worker):
        job_count = self.worker_count * count_per_worker

        if self.size:
            total_size = int(math.ceil(self.size / float(job_count)))
            if total_size < 100:
                self.job_size = total_size
            else:
                self.job_size = min(total_size, int(self.size * 0.05))
        else:
            self.job_size = 50

        return self._create_futures(self._create_distribution(
            self.worker_count * count_per_worker, self.job_size))

    def _create_distribution(self, job_count, job_size):
        return [job_size] * job_count

    def _truncate(self, job_distribution):
        """
        :type job_distribution: list of int
        :return:
        """
        if self.size:
            remaining = self._get_remaining_work()
            expected = sum(job_distribution)
            if expected > remaining:
                per_job = remaining / len(job_distribution)
                job_distribution = self._create_distribution(
                    len(job_distribution), per_job)
                leftover = remaining - (per_job * len(job_distribution))
                job_distribution[0] += leftover
                assert sum(job_distribution) == remaining

        return job_distribution

    def _create_futures(self, job_distribution):
        """
        :type job_distribution: list of int
        :return:
        """
        job_distribution = self._truncate(job_distribution)
        batches = []
        for job_size in job_distribution:
            if job_size > 0:
                start = self.index_scheduled
                batches.append((self.domain, start, job_size,
                            self.worker_reduce_fn, self.worker_reduce_init))
                self.index_scheduled = start + job_size

        if len(batches) > 0:
            futures = self.executor.map(process_batch, batches)
            self.ordered_futures += futures
            return futures
        else:
            return []

    def _add_job(self, job):
        self.completed_jobs.append(job)
        self.index_completed += job.size

    def _get_remaining_work(self):
        if self.size:
            return self.size - self.index_scheduled
        else:
            return -1

    def _has_more_work(self):
        return not self.size or self.index_scheduled < self.size


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

        if spawn_workers > 0:
            self.cluster = LocalCluster(ip=ip,
                                        scheduler_port=port,
                                        n_workers=spawn_workers,
                                        threads_per_worker=1,
                                        diagnostics_port=None)
            self.executor = Executor(self.cluster)
        else:
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

        scheduler = JobScheduler(self.executor,
                                 self._get_worker_count(),
                                 timeout, domain,
                                 worker_reduce_fn, worker_reduce_init)

        jobs = scheduler.iterate_jobs()
        """for job in :
            result = job.result
            print("Received job: {}".format(job))
            jobs.append(job)
            if result_saver:
                result_saver.handle_result(result)"""

        # order the results
        start = time.time()
        jobs.sort(key=lambda job: job.start_index)
        results = [job.result for job in jobs]
        qitLogger.info("Qit: ordering took {} ms".format(time.time() - start))

        self.execution_count += 1

        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        if size:
            qitLogger.info("Qit: finished run with size {} (taking {})".format(
                len(results), domain.size))

            results = results[:domain.size]  # trim results to required size
        else:
            qitLogger.info("Qit: finished run")

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
            raise QitException("There are no workers")

        return workers


def process_batch(arg):
    """
    :param arg:
    :rtype: Job
    """
    domain, start, size, reduce_fn, reduce_init = arg
    job = Job("{}#{}".format(socket.gethostname(), os.getpid()), start, size)

    print(job)

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
