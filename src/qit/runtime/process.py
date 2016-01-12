import multiprocessing as mp

from context import ProcessMessage


class Process(object):
    def __init__(self):
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
        for item in iterator:
            output_queue.put(ProcessMessage("item", item))

        output_queue.put(ProcessMessage("stop"))

    def compute(self, iterator, output_queue):
        self.process = mp.Process(target=self._compute_fn, args=(iterator, output_queue))
        self.process.start()
