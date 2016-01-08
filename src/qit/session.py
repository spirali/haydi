from enum import Enum

from parallel.processcontext import ProcessContext


class ParallelType(Enum):
    Process = 1
    MPI = 2


class Session(object):
    def __init__(self, parallel_type=ParallelType.Process):
        self.parallel_type = parallel_type
        self.visualizers = []

    def create_context(self):
        if self.parallel_type == ParallelType.Process:
            ctx = ProcessContext()
            ctx.on_message_received(self._handle_message)

            return ctx
        else:
            raise NotImplementedError()

    def add_visualizer(self, visualizer):
        self.visualizers.append(visualizer)

    def _handle_message(self, tag, iterator_id, data):
        for visualizer in self.visualizers:
            if tag in visualizer.get_tags():
                visualizer.handle_message(tag, iterator_id, data)
