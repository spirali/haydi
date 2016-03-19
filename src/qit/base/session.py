from exception import InnerParallelContext
from runtime import mpidetection


class Session(object):
    def __init__(self):
        self.listeners = []
        self.main_context = None
        self.worker = None
        self.contexts = []

    def create_context(self, parallel):
        from runtime import serialcontext

        if parallel and self._has_parallel_ctx():
            raise InnerParallelContext()

        if not parallel:
            ctx = serialcontext.SerialContext()
        else:
            ctx = self._create_parallel_context()

        if not self.main_context:
            self.main_context = ctx

        self.contexts.append(ctx)

        return ctx

    def is_context_main(self, ctx):
        return ctx == self.main_context

    def set_worker(self, worker):
        self.worker = worker

    def destroy_context(self, context):
        if context == self.main_context:
            self.main_context = None

        self.contexts.remove(context)

    def post_message(self, message):
        if self.worker:
            self.worker.post_message(message)
        elif self._has_parallel_ctx() and not self.main_context.is_master():
            self.main_context.transmit_to_master(message)
        else:
            self.broadcast_message(message)

    def add_message_listener(self, listener):
        self.listeners.append(listener)

    def broadcast_message(self, message):
        for listener in self.listeners:
            listener.handle_message(message)

    def _has_parallel_ctx(self):
        return self.main_context and self.main_context.is_parallel()

    def _create_parallel_context(self):
        if mpidetection.mpi_available:
            from runtime import mpicontext
            return mpicontext.MpiContext()
        else:
            from runtime import processcontext
            return processcontext.ProcessContext()

session = Session()


def mpi_shutdown():
    if mpidetection.mpi_available:
        from runtime import mpicontext
        mpicontext.shutdown_workers()
