import multiprocessing as mp
import os

from context import ParallelContext
from process import Process
from message import MessageTag, Message
from qit.factory import TransformationFactory
from qit.session import session
from qit.transform import JoinTransformation, Transformation


class QueueIterator(Transformation):
    def __init__(self, parent, queue, tag=None):
        super(QueueIterator, self).__init__(parent)
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
    def __init__(self, parent, queue, process_count=1, tag=None):
        super(QueueJoinIterator, self).__init__(parent, queue, tag)
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

    def compute_action(self, graph, action):
        self.master_pid = os.getpid()
        self.preprocess_splits(graph)

        node = graph.last_transformation
        while node:
            if node.factory.klass.is_join():
                self._parallelize_iterator(graph, node)
            node = node.input

        collect_process = Process(self)
        collect_process.compute(graph, self.msg_queue)
        self.processes.append(collect_process)

        terminated_early = False

        # collect notify messages and results
        while True:
            msg = self.msg_queue.get(True)
            if msg.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                if not action.handle_item(msg.data):
                    for p in self.processes:
                        p.terminate()
                    terminated_early = True
                    break
            elif msg.tag == MessageTag.PROCESS_ITERATOR_STOP:
                break
            else:
                session.post_message(msg)

        if not terminated_early:
            # collect remaining notify messages
            while not self.msg_queue.empty():
                msg = self.msg_queue.get()
                assert msg.tag in (MessageTag.PROCESS_ITERATOR_ITEM,
                                   MessageTag.PROCESS_ITERATOR_STOP)
                session.post_message(msg)

        for p in self.processes:
            p.stop()

    def transmit_to_master(self, message):  # called in a worker process
        self.msg_queue.put(message)

    def init(self):
        pass

    def shutdown(self):
        pass

    def finish_computation(self):
        self._stop_processes()

    def _stop_processes(self):
        for p in self.processes:
            p.send_message(Message(MessageTag.CALCULATION_STOP))

    def _parallelize_iterator(self, graph, node):
        assert node.factory.klass == JoinTransformation

        split = node

        # assumes that the graph is correct with respect to split-join pairing
        # and we deal only with transformations
        while split and not split.factory.klass.is_split():
            split = split.input

        assert split

        process_count = split.factory.args[0]

        output_queue = mp.Queue()
        queue_join = TransformationFactory(
            QueueJoinIterator,
            output_queue,
            process_count,
            "join"
        )  # TODO: pass size
        parallel_iter_begin = node.input  # first iterator that is parallelized
        graph.replace(node, queue_join)

        processes = []

        for i in xrange(process_count):
            processes.append(Process(self))

        input_queue = mp.Queue()
        queue_iterator = TransformationFactory(
            QueueIterator, input_queue, "map"
        )
        # TODO: pass size

        graph.append(split, queue_iterator)

        for p in processes:
            p.compute(graph.copy_starting_at(parallel_iter_begin),
                      output_queue)

        split_process = Process(self)
        split_process.compute(graph.copy_starting_at(split.input), input_queue)

        self.processes += processes
        self.processes.append(split_process)
