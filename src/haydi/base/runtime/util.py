import logging
import time
from datetime import datetime, timedelta


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


def setup_logger():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger("Haydi")


haydi_logger = setup_logger()
