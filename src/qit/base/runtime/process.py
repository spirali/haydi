import multiprocessing as mp

from message import Message, MessageTag


class Process(object):
    def __init__(self, context, name="", batch_amount=300):
        self.context = context
        self.process = None
        self.name = name
        self.input_queue = mp.Queue()
        self.batch_amount = batch_amount

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

    def terminate(self):
        self.process.terminate()

    def compute(self, factory, output_queue):
        self.process = mp.Process(target=self._compute_fn,
                                  args=(factory, output_queue))
        self.process.start()

    def send_message(self, msg):
        self.input_queue.put(msg)

    def _compute_fn(self, factory, output_queue):
        items = []

        iter = factory.create()
        for item in iter:
            if not self.input_queue.empty():
                msg = self.input_queue.get()
                if msg.tag == MessageTag.CALCULATION_STOP:
                    self.input_queue.close()
                    output_queue.close()
                    return
            items.append(item)

            if len(items) == self.batch_amount:
                output_queue.put(
                    Message(MessageTag.PROCESS_ITERATOR_ITEM, items))
                items = []

        output_queue.put(Message(MessageTag.PROCESS_ITERATOR_STOP))
