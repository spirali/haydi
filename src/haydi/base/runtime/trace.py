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

    def trace_job_send(self, job):
        """
        Args:
            job: .scheduler.Job
        """
        pass

    def trace_job_recv(self, job):
        """
        Args:
            job: .scheduler.Job
        """
        pass

    def trace_finish(self):
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
        self.worker_map = {"master": 1}

    def trace_job_recv(self, job):
        self._add_worker(job.worker_id)

        otf.OTF_Writer_writeSendMsg(self.writer, self.time(),
                                    self.worker_map[job.worker_id],
                                    self.worker_map["master"],
                                    0, 0, job.size, 0)
        otf.OTF_Writer_writeRecvMsg(self.writer, self.time(),
                                    self.worker_map["master"],
                                    self.worker_map[job.worker_id],
                                    0, 0, job.size, 0)

    def trace_workers(self, count):
        self.worker_count = count

        otf.OTF_Writer_writeDefTimerResolution(self.writer, 0, 1)

        otf.OTF_Writer_writeDefProcess(self.writer, 0,
                                       self.worker_map["master"], "master", 0)
        otf.OTF_Writer_writeBeginProcess(self.writer, self.time(),
                                         self.worker_map["master"])

        for i in xrange(2, count + 2):
            otf.OTF_Writer_writeDefProcess(self.writer, 0, i,
                                           "worker {}".format(i - 1), 0)

    def trace_finish(self):
        for i in xrange(1, self.worker_count + 2):
            otf.OTF_Writer_writeEndProcess(self.writer, self.time(), i)

        otf.OTF_Writer_close(self.writer)
        otf.OTF_FileManager_close(self.manager)

    def time(self):
        return int(monotonic.monotonic())

    def _add_worker(self, name):
        if name not in self.worker_map:
            worker_id = len(self.worker_map) + 1
            self.worker_map[name] = worker_id
            otf.OTF_Writer_writeBeginProcess(self.writer, self.time(),
                                             worker_id)
