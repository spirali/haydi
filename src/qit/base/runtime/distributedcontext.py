import os
from threading import Thread
from datetime import datetime
import time
import itertools
import logging
import socket

import cloudpickle
import distributed
import resource
from distributed import Scheduler, Nanny as Worker, Executor, as_completed
from tornado.ioloop import IOLoop

from qit.base.iterator import NoValue


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


class JobObserver(object):
    def on_computation_start(self, batch_count, batch_size):
        pass

    def on_job_completed(self, job):
        """
        :type job: Job
        """
        pass


class DistributedContext(object):
    """
    Parallel context that uses the
    `distributed <http://distributed.readthedocs.io>`_ library to distribute
    work amongst workers in a cluster to speed up the computation.

    It can either connect to an already running cluster or create a new one.

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
                 write_partial_results=None,
                 track_progress=False,
                 time_limit=None,
                 job_observer=None):
        """

        :type ip: string
        :type port: int
        :type spawn_workers: int
        :type write_partial_results: int
        :type track_progress: bool
        :type time_limit: int
        :type job_observer: JobObserver
        """

        self.worker_count = spawn_workers
        self.ip = ip
        self.port = port
        self.active = False
        self.write_partial_results = write_partial_results
        self.track_progress = track_progress
        self.execution_count = 0
        self.timeout = TimeoutManager(time_limit) if time_limit else None
        self.job_observer = job_observer

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
            global_reduce_fn, global_reduce_init):
        size = domain.steps
        assert size is not None  # TODO: Iterators without size

        workers = 0
        for name, value in self.executor.ncores().items():
            workers += value

        if workers == 0:
            raise Exception("There are no workers")

        batch_count = workers * 4
        batch_size = max(int(round(size / float(batch_count))), 1)
        batches = self._create_batches(batch_size, size, domain,
                                       worker_reduce_fn, worker_reduce_init)

        logging.info("Qit: starting {} batches with size {}".format(
            batch_count, batch_size))

        if self.job_observer:
            self.job_observer.on_computation_start(batch_count, batch_size)

        futures = self.executor.map(process_batch, batches)

        if self.track_progress:
            distributed.diagnostics.progress(futures)

        if self.write_partial_results is not None:
            result_saver = ResultSaver(self.execution_count,
                                       self.write_partial_results)
        else:
            result_saver = None

        timeouted = False
        results = []

        for future in as_completed(futures):
            job = future.result()
            if result_saver:
                result_saver.handle_result(job.result)
            if self.job_observer:
                self.job_observer.on_job_completed(job)

            results.append(job.result)

            if self.timeout and self.timeout.is_finished():
                logging.info("Qit: timeouted after {} seconds".format(
                    self.timeout.timeout))
                timeouted = True
                break

        # order results
        if not timeouted:
            results = [j.result for j in self.executor.gather(futures)]

        self.execution_count += 1

        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        logging.info("Qit: finished run with size {} (taking {})".format(
            len(results), domain.size))

        results = results[:domain.size]  # trim results to required size

        if global_reduce_fn is None:
            return results
        else:
            if global_reduce_init is None:
                return reduce(global_reduce_fn, results)
            else:
                return reduce(global_reduce_fn, results, global_reduce_init())

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

    def _create_batches(self, batch_size, size,
                        domain,
                        worker_reduce_fn,
                        worker_reduce_init):
        batches = []
        i = 0

        while True:
            new = i + batch_size
            if i + batch_size <= size:
                batches.append((domain, i, batch_size,
                                worker_reduce_fn, worker_reduce_init))
                i = new
                if new == size:
                    break
            else:
                batches.append((domain, i, size - i,
                                worker_reduce_fn, worker_reduce_init))
                break

        return batches


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
