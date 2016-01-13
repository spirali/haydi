import multiprocessing as mp

import time

from context import Context
from process import Process
from iterator import Iterator

from transform import JoinTransformation, SplitTransformation


class QueueIterator(Iterator):
    def __init__(self, queue, tag=None):
        super(QueueIterator, self).__init__()
        self.queue = queue
        self.tag = tag

    def next(self):
        #import os

        message = self.queue.get()

        #print("Read message {0} on process {1}, {2}".format(message, os.getpid(), self.tag))

        if message.tag == "stop":
            return self.handle_stop(message)
        elif message.tag == "item":
            return message.data
        else:
            raise KeyError()

    def handle_stop(self, message):
        self.queue.put(message)
        raise StopIteration()


class QueueJoinIterator(QueueIterator):
    def __init__(self, queue, process_count=1, tag=None):
        super(QueueJoinIterator, self).__init__(queue, tag)
        self.process_count = process_count
        self.processed_ended = 0

    def handle_stop(self, message):
        self.processed_ended += 1

        if self.processed_ended == self.process_count:
            raise StopIteration()
        else:
            return self.next()


class ProcessContext(Context):
    def __init__(self):
        super(ProcessContext, self).__init__()
        self.notify_queue = mp.Queue()
        self.processes = []

    def run(self, iterator_graph):
        for node in iterator_graph.nodes:
            if isinstance(node.iterator, JoinTransformation):
                self._paralellize_iterator(node)

        collect_process = Process(self)
        collect_queue = mp.Queue()
        collect_process.compute(iterator_graph.nodes[0].iterator, collect_queue)

        result = []

        while True:
            try:
                notify_msg = self.notify_queue.get(True, 0.01)
                self._notify_message(notify_msg)
            except:
                pass

            try:
                stop = False
                while True:
                    message = collect_queue.get(True, 0.1)
                    if message.tag == "stop":
                        stop = True
                        break
                    elif message.tag == "item":
                        result.append(message.data)

                if stop:
                    break
            except:
                pass

        while not self.notify_queue.empty():
            self._notify_message(self.notify_queue.get())

        collect_process.stop()
        for p in self.processes:
            p.stop()

        return result

    def post_message(self, message):  # called in a worker process
        if "timestamp" not in message.data:
            message.data["timestamp"] = time.time()

        self.notify_queue.put(message)

    def init(self):
        pass

    def shutdown(self):
        pass

    def _paralellize_iterator(self, node):
        split = node

        # assumes that the graph is correct with respect to split-join pairing and we deal only with transformations
        while not isinstance(split.iterator, SplitTransformation):
            split = split.inputs[0]

        process_count = split.iterator.process_count

        output_queue = mp.Queue()
        parallel_iter_begin = node.iterator.parent
        node.iterator = QueueJoinIterator(output_queue, process_count, "join")

        if node.output:
            node.output.iterator.parent = node.iterator

        processes = []

        for i in xrange(process_count):
            processes.append(Process(self))

        input_queue = mp.Queue()
        input_iterator = QueueIterator(input_queue, "map")
        split.output.iterator.parent = input_iterator

        for p in processes:
            p.compute(parallel_iter_begin, output_queue)

        split_process = Process(self)
        split_process.compute(split.iterator.parent, input_queue)

        self.processes += processes
        self.processes.append(split_process)