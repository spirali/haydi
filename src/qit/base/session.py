from exception import InnerParallelContext, ParallelContextNotSet


class Session(object):
    def __init__(self):
        from runtime.serialcontext import SerialContext

        self.listeners = []
        self.serial_context = SerialContext()
        self.parallel_context = None
        self.worker = None

    def get_context(self, parallel):
        if parallel and not self.parallel_context:
            raise ParallelContextNotSet()

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
