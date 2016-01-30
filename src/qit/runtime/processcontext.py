import multiprocessing as mp
import os

from context import ParallelContext
from process import Process
from message import MessageTag
from qit.factory import IteratorFactory
from qit.iterator import Iterator
from qit.session import session
from qit.transform import JoinTransformation


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
        self.master_pid = None

    def is_master(self):
        return os.getpid() == self.master_pid

    def get_result(self, iterator_factory):
        self.master_pid = os.getpid()
        iterator_factory = self.preprocess_splits(iterator_factory)

        node = iterator_factory
        while node:
            if node.iterator_class.is_join():
                self._parallelize_iterator(node)
            node = node.input

        collect_process = Process(self)
        collect_process.compute(iterator_factory, self.msg_queue)

        result = []

        # collect notify messages and results
        while True:
            msg = self.msg_queue.get(True)
            if msg.tag == MessageTag.NOTIFICATION_MESSAGE:
                msg.data["message"].data["timestamp"] = msg.data["timestamp"]
                session.post_message(msg.data["message"])
            elif msg.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                result.append(msg.data)
            elif msg.tag == MessageTag.PROCESS_ITERATOR_STOP:
                break

        while not self.msg_queue.empty():  # collect remaining notify messages
            msg = self.msg_queue.get()
            assert msg.tag == MessageTag.NOTIFICATION_MESSAGE
            msg.data["message"].data["timestamp"] = msg.data["timestamp"]
            session.post_message(msg.data["message"])

        collect_process.stop()
        for p in self.processes:
            p.stop()

        return result

    def transmit_to_master(self, message):  # called in a worker process
        self.msg_queue.put(message)

    def init(self):
        pass

    def shutdown(self):
        pass

    def _parallelize_iterator(self, node):
        assert node.iterator_class == JoinTransformation

        split = node

        # assumes that the graph is correct with respect to split-join pairing
        # and we deal only with transformations
        while split and not split.iterator_class.is_split():
            split = split.input

        assert split

        process_count = split.args[0]

        # TODO
        output_queue = mp.Queue()
        queue_join = IteratorFactory(QueueJoinIterator,
                                     output_queue,
                                     process_count,
                                     "join")  # TODO: pass size
        parallel_iter_begin = node.input  # first iterator that is parallelized
        node.replace(queue_join)

        processes = []

        for i in xrange(process_count):
            processes.append(Process(self))

        input_queue = mp.Queue()
        queue_iterator = IteratorFactory(QueueIterator, input_queue, "map")
        # TODO: pass size

        split.append(queue_iterator)

        for p in processes:
            p.compute(parallel_iter_begin, output_queue)

        split_process = Process(self)
        split_process.compute(split.input, input_queue)

        self.processes += processes
        self.processes.append(split_process)
