from exception import InnerParallelContext
from runtime import mpidetection


class Session(object):
    def __init__(self):
        from runtime.serialcontext import SerialContext
        from runtime.processcontext import ProcessContext

        self.listeners = []
        self.serial_context = SerialContext()
        self.parallel_context = ProcessContext()
        self.worker = None

    def get_context(self, parallel):
        if parallel and self.parallel_context.has_computation:
            raise InnerParallelContext()

        if parallel:
            ctx = self.parallel_context
        else:
            ctx = self.serial_context

        return ctx

    def set_worker(self, worker):
        self.worker = worker

    def set_parallel_context(self, ctx):
        self.parallel_context = ctx

session = Session()


def mpi_shutdown():
    if mpidetection.mpi_available:
        from runtime import mpicontext
        mpicontext.shutdown_workers()
