import multiprocessing as mp
from time import sleep

from parallelcontext import ProcessMessage


class Process(object):
    def __init__(self):
        self.process = None
        self.msg_queue = mp.Queue()

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

    def _compute_fn(self, iterator):
        data = list(iterator)

        self.msg_queue.put(ProcessMessage("result", data))

    def get_data(self):
        return self.msg_queue.get(block=True)

    def compute(self, *args, **kwargs):
        self.process = mp.Process(target=self._compute_fn, args=(args[0],))
        self.process.start()
