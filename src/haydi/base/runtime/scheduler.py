import Queue
import math
import traceback
from threading import Thread

import monotonic
from distributed import as_completed

from .util import TimeoutManager, haydi_logger


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
        self.start_time = monotonic.monotonic()
        self.end_time = None

    def finish(self, result):
        self.result = result
        self.end_time = monotonic.monotonic()

    def get_duration(self):
        return self.end_time - self.start_time

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
                 strategy,
                 timeout,
                 domain,
                 worker_reduce_fn,
                 worker_reduce_init,
                 tracer):
        """
        :param executor: distributed executor
        :param worker_count: number of workers in the cluster
        :type strategy: haydi.base.runtime.strategy.WorkerStrategy
        :type timeout: datetime.timedelta
        :param timeout: timeout for the computation
        :param domain: domain to be iterated
        :param worker_reduce_fn:
        :param worker_reduce_init:
        :type tracer: haydi.base.runtime.trace.Tracer
        """
        self.executor = executor
        self.worker_count = worker_count
        self.size = strategy.get_size(domain)
        self.strategy = strategy
        self.tracer = tracer
        self.domain = domain
        self.worker_reduce_fn = worker_reduce_fn
        self.worker_reduce_init = worker_reduce_init
        self.index_scheduled = 0
        self.index_completed = 0
        self.job_size = None
        self.timeout_mgr = TimeoutManager(timeout) if timeout else None
        self.ordered_futures = []
        self.backlog_per_worker = 4
        self.target_time = 60 * 3
        self.target_time_active = self.target_time
        self.completed_jobs = []
        self.job_queue = Queue.Queue()
        self.job_thread = None
        self.completed = False
        self.canceled = False

    def start(self):
        self.strategy.start(self)
        self.job_thread = Thread(target=self._iterate_jobs)
        self.job_thread.daemon = True
        self.job_thread.start()

    def stop(self):
        self.canceled = True

        size = len(self.ordered_futures)
        for i in xrange(size):
            self.ordered_futures[i].cancel()

    def _iterate_jobs(self):
        """
        Iterate through all jobs until the domain size is depleted or
        time runs out.
        :return: completed job
        """
        backlog_half = self.backlog_per_worker / 2
        active_futures = self._init_futures(self.backlog_per_worker)
        next_futures = []

        try:
            while ((self._has_more_work() or
                   self.index_completed < self.index_scheduled) and
                   not self.canceled):
                iterated = 0
                for future in as_completed(active_futures):
                    job = future.result()
                    self._mark_job_completed(job)
                    iterated += 1

                    self.tracer.trace_job(job)

                    if iterated >= (backlog_half * self.worker_count):
                        iterated = 0
                        if self._has_more_work():
                            next_futures += self._schedule(backlog_half)

                if self._has_more_work():
                    next_futures += self._schedule(backlog_half)

                active_futures = next_futures
                next_futures = []
        except Exception as e:
            haydi_logger.error(traceback.format_exc(e))

        self.completed = True

    def _schedule(self, count_per_worker):
        """
        Adjust batch size according to the average duration of recent jobs
        and create new futures.
        :param count_per_worker: how many jobs should be spawned per worker
        :rtype: list of distributed.client.Future
        :return: newly scheduled futures
        """
        self._check_falloff()
        duration = self._get_avg_duration()
        delta = duration / float(self.target_time_active)
        delta = self._clamp(delta, 0.6, 1.25)

        previous_size = self.job_size
        self.job_size = int(self.job_size / delta)

        self.tracer.trace_job_size(self.job_size)

        haydi_logger.info("Scheduling: avg duration {}, size {} -> {}"
                          .format(duration, previous_size, self.job_size))

        return self._create_futures(self._create_distribution(
            self.worker_count * count_per_worker, self.job_size))

    def _check_falloff(self):
        if not self.timeout_mgr:
            return

        total = self.timeout_mgr.get_total_time()
        remaining = self.timeout_mgr.get_remaining_time()
        limit = total * 0.2

        if remaining < limit:
            ratio = remaining / float(limit)
            self.target_time_active = self.target_time * ratio

    def _clamp(self, value, minimum, maximum):
        return min(maximum, max(minimum, value))

    def _get_avg_duration(self):
        job_histogram = self.completed_jobs[-self.worker_count:]
        total_duration = sum([j.get_duration() for j in job_histogram])
        return total_duration / float(len(job_histogram))

    def _init_futures(self, count_per_worker):
        job_count = self.worker_count * count_per_worker
        self.job_size = 50

        if self.size:
            total_size = int(math.ceil(self.size / float(job_count)))
            if total_size < self.job_size:
                self.job_size = total_size

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
                batches.append(self.strategy.get_args_for_batch(start,
                                                                job_size))
                self.index_scheduled = start + job_size

        if len(batches) > 0:
            self.tracer.trace_index_scheduled(self.index_scheduled)
            self.tracer.trace_comment("Sending {} jobs with size {}"
                                      .format(len(batches), self.job_size))
            futures = self.strategy.create_futures(self, batches)
            self.ordered_futures += futures
            return futures
        else:
            return []

    def _mark_job_completed(self, job):
        self.completed_jobs.append(job)
        self.index_completed += job.size

        self.tracer.trace_index_completed(self.index_completed)

        self.job_queue.put(job)

    def _get_remaining_work(self):
        if self.size:
            return self.size - self.index_scheduled
        else:
            return -1

    def _has_more_work(self):
        return not self.size or self.index_scheduled < self.size
