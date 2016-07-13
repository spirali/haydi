from runtime.serialcontext import SerialContext


class Session(object):
    def __init__(self):
        self.listeners = []
        self.serial_context = SerialContext()
        self.parallel_context = None
        self.worker = None

    def get_context(self, parallel):
        if parallel:
            if self.parallel_context is None:
                raise Exception("No parallel context")
            elif self.parallel_context.active:
                return self.serial_context
            return self.parallel_context
        else:
            return self.serial_context

    def set_worker(self, worker):
        self.worker = worker

    def set_parallel_context(self, ctx):
        self.parallel_context = ctx

session = Session()
