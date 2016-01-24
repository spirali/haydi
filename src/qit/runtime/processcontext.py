import multiprocessing as mp
import time

from context import ParallelContext
from process import Process
from message import Message, MessageTag
from qit.iterator import Iterator
from qit.transform import JoinTransformation, SplitTransformation


class QueueIterator(Iterator):
    def __init__(self, queue, tag=None):
        super(QueueIterator, self).__init__()
        self.queue = queue
        self.tag = tag

    def next(self):
        message = self.queue.get()

        if message.tag == MessageTag.PROCESS_ITERATOR_STOP:
            return self.handle_stop(message)
        elif message.tag == MessageTag.PROCESS_ITERATOR_ITEM:
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


class ProcessContext(ParallelContext):
    def __init__(self):
        super(ProcessContext, self).__init__()
        self.msg_queue = mp.Queue()
        self.processes = []

    def run(self, iterator_graph):
        self.preprocess_splits(iterator_graph)

        for node in iterator_graph.nodes:
            if isinstance(node.iterator, JoinTransformation):
                self._parallelize_iterator(node)

        collect_process = Process(self)
        collect_process.compute(iterator_graph.nodes[0].iterator, self.msg_queue)

        result = []

        self._notify_message(Message(MessageTag.CONTEXT_START))

        # collect notify messages and results
        while True:
            msg = self.msg_queue.get(True)
            if msg.tag == MessageTag.NOTIFICATION_MESSAGE:
                msg.data["message"].data["timestamp"] = msg.data["timestamp"]
                self._notify_message(msg.data["message"])
            elif msg.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                result.append(msg.data)
            elif msg.tag == MessageTag.PROCESS_ITERATOR_STOP:
                break

        while not self.msg_queue.empty():  # collect remaining notify messages
            msg = self.msg_queue.get()
            assert msg.tag == MessageTag.NOTIFICATION_MESSAGE
            msg.data["message"].data["timestamp"] = msg.data["timestamp"]
            self._notify_message(msg.data["message"])

        self._notify_message(Message(MessageTag.CONTEXT_STOP))

        collect_process.stop()
        for p in self.processes:
            p.stop()

        return result

    def post_message(self, message):  # called in a worker process
        self.msg_queue.put(
            Message(MessageTag.NOTIFICATION_MESSAGE, {
                "timestamp": time.time(),
                "message": message
            }
            ))

    def init(self):
        pass

    def shutdown(self):
        pass

    def _parallelize_iterator(self, node):
        split = node

        # assumes that the graph is correct with respect to split-join pairing and we deal only with transformations
        while not isinstance(split.iterator, SplitTransformation):
            split = split.inputs[0]

        process_count = split.iterator.process_count

        output_queue = mp.Queue()
        parallel_iter_begin = node.iterator.parent
        node.iterator = QueueJoinIterator(output_queue, process_count, "join")
        node.iterator.size = parallel_iter_begin.size

        if node.output:
            node.output.iterator.parent = node.iterator

        processes = []

        for i in xrange(process_count):
            processes.append(Process(self))

        input_queue = mp.Queue()
        input_iterator = QueueIterator(input_queue, "map")
        input_iterator.size = split.iterator.size
        split.output.iterator.parent = input_iterator

        for p in processes:
            p.compute(parallel_iter_begin, output_queue)

        split_process = Process(self)
        split_process.compute(split.iterator.parent, input_queue)

        self.processes += processes
        self.processes.append(split_process)
