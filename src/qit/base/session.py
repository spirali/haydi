from runtime.serialcontext import SerialContext


class Session(object):
    def __init__(self):
        self.listeners = []
        self.serial_context = SerialContext()
        self.parallel_context = None
        self.worker = None

    def get_context(self, parallel):
        if not parallel or self.parallel_context.active:
            return self.serial_context
        else:
            return self.parallel_context

    def set_worker(self, worker):
        self.worker = worker

    def set_parallel_context(self, ctx):
        self.parallel_context = ctx

session = Session()
