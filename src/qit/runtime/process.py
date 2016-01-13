import multiprocessing as mp
import os

from message import Message


class Process(object):
    def __init__(self, context):
        self.context = context
        self.process = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        pass

    def stop(self):
        if self.process is not None:
            self.process.join()

    def _compute_fn(self, iterator, output_queue):
        self.context.post_message(Message("process-start", {"pid": os.getpid()}))

        for item in iterator:
            output_queue.put(Message("item", item))
            self.context.post_message(Message("process-item", {"pid": os.getpid()}))

        output_queue.put(Message("stop"))
        self.context.post_message(Message("process-stop", {"pid": os.getpid()}))

    def compute(self, iterator, output_queue):
        self.process = mp.Process(target=self._compute_fn, args=(iterator, output_queue))
        self.process.start()
