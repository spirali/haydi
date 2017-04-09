from datetime import datetime, timedelta
import time
#  import cloudpickle
import logging


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

    def handle_job(self, scheduler, job):
        self.results.append(job.result)

        if len(self.results) % self.write_count == 0:
            self._write_partial_result(self.results, self.counter)
            self.results = []
            self.counter += 1

    def _write_partial_result(self, results, counter):
        filename = "haydi-{}-{}-{}".format(
                int(time.mktime(self.time.timetuple())),
                self.id,
                counter)
        with open(filename, "w") as f:
            cloudpickle.dump(results, f)
        haydi_logger.info("Writing file {} ({} results)".format(
            filename, len(results)))


class TimeoutManager(object):
    def __init__(self, timeout):
        """
        :type timeout: int | timedelta
        """
        if isinstance(timeout, timedelta):
            timeout = timeout.total_seconds()
        self.timeout = timeout
        self.end = time.time() + timeout
        self.start = datetime.now()

    def is_finished(self):
        return self.get_remaining_time() <= 0

    def get_total_time(self):
        return self.timeout

    def get_remaining_time(self):
        return self.timeout - self.get_time_from_start()

    def get_time_from_start(self):
        return (datetime.now() - self.start).total_seconds()

    def reset(self):
        self.start = datetime.now()


class ProgressLogger(object):
    def __init__(self, log_repeat):
        self.timeout_mgr = TimeoutManager(log_repeat)
        self.last_percent = 0

    def handle_job(self, scheduler, job):
        self._log_progress(scheduler)

    def _log_progress(self, scheduler):
        if scheduler.size:
            percent = (scheduler.index_completed / float(scheduler.size)) * 100
            if percent - self.last_percent >= 1.0:
                haydi_logger.info("Iterated {} % ({} elements)".format(
                    percent, scheduler.index_completed))
                self.last_percent = percent
        else:
            if self.timeout_mgr.is_finished():
                self.timeout_mgr.reset()
                haydi_logger.info("Generated {} elements".format(
                    scheduler.index_completed))


class JobOffsetLogger(object):
    def __init__(self):
        self.iterated = 0
        self.histogram = []

    def handle_job(self, scheduler, job):
        if self.iterated % 10 == 0 and len(self.histogram) > 1:
            offset_sum = 0

            for i in xrange(len(self.histogram) - 1):
                diff = self.histogram[i + 1] - self.histogram[i]
                offset_sum += abs(diff)

            offset = offset_sum / float(len(self.histogram) - 1)
            self.histogram = []

            haydi_logger.info("Job offset: {}".format(offset))
        self.histogram.append(time.time())


haydi_logger = logging.getLogger("Haydi")
