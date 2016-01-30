from exception import InnerParallelContext


class Session(object):
    def __init__(self):
        self.listeners = []
        self.parallel_context = None
        self.contexts = []

    def create_context(self, parallel):
        from runtime import serialcontext

        if parallel and self.parallel_context:
            raise InnerParallelContext()

        if not parallel:
            ctx = serialcontext.SerialContext()
        else:
            ctx = self._create_parallel_context()
            self.parallel_context = ctx

        self.contexts.append(ctx)

        return ctx

    def destroy_context(self, context):
        if context.is_parallel():
            self.parallel_context = None

        self.contexts.remove(context)

    def post_message(self, message):
        if self.parallel_context and not self.parallel_context.is_master():
            self.parallel_context.transmit_to_master(message)
        else:
            self.broadcast_message(message)

    def add_message_listener(self, listener):
        self.listeners.append(listener)

    def broadcast_message(self, message):
        for listener in self.listeners:
            listener.handle_message(message)

    def _create_parallel_context(self):
        from runtime import mpicontext, processcontext

        if mpicontext.MpiRun:
            return mpicontext.MpiContext()
        else:
            return processcontext.ProcessContext()

session = Session()
