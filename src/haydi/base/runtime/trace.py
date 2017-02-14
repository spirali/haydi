from haydi.base.exception import HaydiException

try:
    import otf
    import monotonic
    otf_import_error = None
except Exception as e:
    otf_import_error = e


class Tracer(object):
    def trace_workers(self, count):
        pass

    def trace_finish(self):
        pass

    def trace_comment(self, comment):
        pass

    def trace_job_size(self, size):
        pass

    def trace_job(self, job):
        pass

    def trace_index_scheduled(self, value):
        pass

    def trace_index_completed(self, value):
        pass


class OTFTracer(Tracer):
    def __init__(self, name):
        if otf_import_error:
            raise HaydiException("otf and monotonic must be properly installed"
                                 "in order to use the OTFTracer\n"
                                 "Error:\n{}"
                                 .format(otf_import_error))
        self.name = name
        self.manager = otf.OTF_FileManager_open(1000)
        self.writer = otf.OTF_Writer_open(name, 10000, self.manager)
        self.worker_count = None
        self.worker_map = {"master": [1, 0]}
        self.comment_marker_id = 101
        self.job_size_id = 201
        self.job_scheduled_id = 202
        self.job_completed_id = 203
        self.worker_compute_id = 301
        self.time_scale = 1000
        self._init()

    def trace_workers(self, count):
        self.worker_count = count

        time = self._get_time()
        otf.OTF_Writer_writeDefProcess(self.writer, 0,
                                       self.worker_map["master"][0], "master", 0)
        otf.OTF_Writer_writeBeginProcess(self.writer, time,
                                         self.worker_map["master"][0])
        self.worker_map["master"][1] = time

        for i in xrange(2, count + 2):
            otf.OTF_Writer_writeDefProcess(self.writer, 0, i,
                                           "worker {}".format(i - 1), 0)
            otf.OTF_Writer_writeBeginProcess(self.writer, self._get_time(), i)

    def trace_finish(self):
        for i in xrange(1, self.worker_count + 2):
            otf.OTF_Writer_writeEndProcess(self.writer, self._get_time(), i)

        otf.OTF_Writer_close(self.writer)
        otf.OTF_FileManager_close(self.manager)

    def trace_comment(self, comment):
        otf.OTF_Writer_writeMarker(self.writer, self._get_time(), 1,
                                   self.comment_marker_id, comment)

    def trace_job_size(self, size):
        otf.OTF_Writer_writeCounter(self.writer, self._get_time(), 1,
                                    self.job_size_id, size)

    def trace_index_scheduled(self, value):
        otf.OTF_Writer_writeCounter(self.writer, self._get_time(), 1,
                                    self.job_scheduled_id, value)

    def trace_index_completed(self, value):
        otf.OTF_Writer_writeCounter(self.writer, self._get_time(), 1,
                                    self.job_completed_id, value)

    def trace_job(self, job):
        worker_id, last_time = self._add_worker(job.worker_id)
        duration = max(int(job.get_duration() * self.time_scale), 1)
        current_time = self._get_time()
        start = max(last_time + 1, current_time - duration)
        end = start + duration

        if start >= current_time:
            return

        self.worker_map[job.worker_id][1] = end

        otf.OTF_Writer_writeEnter(self.writer, start,
                                  self.worker_compute_id, worker_id, 0)
        otf.OTF_Writer_writeLeave(self.writer, end,
                                  self.worker_compute_id, worker_id, 0)

    def _get_time(self):
        return int(monotonic.monotonic() * self.time_scale)

    def _add_worker(self, name):
        if name not in self.worker_map:
            worker_id = len(self.worker_map) + 1
            self.worker_map[name] = [worker_id, 0]
        return self.worker_map[name]

    def _init(self):
        otf.OTF_Writer_writeDefTimerResolution(self.writer, 0, self.time_scale)
        otf.OTF_Writer_writeDefMarker(self.writer, 0, self.comment_marker_id,
                                      "Comment", otf.OTF_MARKER_TYPE_HINT)
        otf.OTF_Writer_writeDefCounter(self.writer, 0,
                                       self.job_size_id, "Job size",
                                       otf.OTF_COUNTER_TYPE_ABS |
                                       otf.OTF_COUNTER_SCOPE_POINT, 0,
                                       "instances per job")
        otf.OTF_Writer_writeDefCounter(self.writer, 0,
                                       self.job_scheduled_id, "Count scheduled",
                                       otf.OTF_COUNTER_TYPE_ABS |
                                       otf.OTF_COUNTER_SCOPE_POINT, 0,
                                       "instances scheduled")
        otf.OTF_Writer_writeDefCounter(self.writer, 0,
                                       self.job_completed_id, "Count completed",
                                       otf.OTF_COUNTER_TYPE_ABS |
                                       otf.OTF_COUNTER_SCOPE_POINT, 0,
                                       "instances completed")

        otf.OTF_Writer_writeDefFunction(self.writer, 0, self.worker_compute_id,
                                        "WorkerCompute", 0, 0)
