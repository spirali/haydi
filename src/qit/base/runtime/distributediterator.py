import math
from distributed import Executor

from qit.base.runtime.message import MessageTag, Message
from qit.base.transform import Transformation


def set_and_compute_unwrap(args):
    return set_and_compute(*args)


def set_and_compute(graph, index, count):
    graph.set(index)

    if graph.size:
        count = min(max(graph.size - index, 0), count)

    if count == 0:
        return Message(MessageTag.PROCESS_ITERATOR_STOP)

    try:
        result = []
        for i in xrange(count):
            result.append(graph.next())
        return Message(MessageTag.PROCESS_ITERATOR_ITEM, result)
    except StopIteration:
        return Message(MessageTag.PROCESS_ITERATOR_STOP)


class DistributedSplitIterator(Transformation):
    def __init__(self, parent, config, parallel_subgraph):
        super(DistributedSplitIterator, self).__init__(parent)
        self.config = config
        self.executor = Executor(config.address)
        self.parallel_subgraph = parallel_subgraph
        self.subgraph_iterator = self.parallel_subgraph.create()
        self.index = 0
        if self.parent.size:
            self.batch = int(math.ceil(
                (self.parent.size / config.worker_count)) * 0.1)
        else:
            self.batch = 100

    def next(self):
        if self.parent.size:
            task_count = int(math.ceil(self.parent.size / self.batch))
        else:
            task_count = self.config.worker_count

        index = self.index
        args = [(index + i * self.batch, self.batch)
                for i in xrange(task_count)]
        self.index += task_count * self.batch

        [data_future] = self.executor.scatter([self.subgraph_iterator],
                                              broadcast=True)
        tasks = [self.executor.submit(set_and_compute, data_future, *arg)
                 for arg in args]
        data = self.executor.gather(tasks)

        result = []
        for item in data:
            if item.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                result += item.data

        return result
