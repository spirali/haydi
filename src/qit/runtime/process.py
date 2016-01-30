import multiprocessing as mp
import os

from message import Message, MessageTag
from qit.session import session


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

    def _compute_fn(self, factory, output_queue):
        session.post_message(Message(MessageTag.PROCESS_START, {"pid": os.getpid()}))

        for item in factory.create():
            output_queue.put(Message(MessageTag.PROCESS_ITERATOR_ITEM, item))

        output_queue.put(Message(MessageTag.PROCESS_ITERATOR_STOP))
        session.post_message(Message(MessageTag.PROCESS_STOP, {"pid": os.getpid()}))

    def compute(self, factory, output_queue):
        self.process = mp.Process(target=self._compute_fn, args=(factory, output_queue))
        self.process.start()
