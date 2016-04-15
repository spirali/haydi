import math
from distributed import Executor

from qit.base.runtime.message import MessageTag, Message
from qit.base.transform import Transformation


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
        self.batch = int(math.ceil(
            (self.parent.size / config.worker_count) * 0.1))

    def next(self):
        """dask = {}
        keys = []
        for worker in xrange(self.config.worker_count):
            key = "j{}".format(worker)
            dask[key] = (set_and_compute,
                         self.subgraph_iterator,
                         self.index,
                         self.batch)
            keys.append(key)
            self.index += self.batch

        data = self.executor.get(dask, keys)
        """

        futures = []
        for worker in xrange(self.config.worker_count):
            futures.append(self.executor.submit(set_and_compute,
                                                self.subgraph_iterator,
                                                self.index,
                                                self.batch))
            self.index += self.batch

        data = self.executor.gather(futures)

        result = []
        for item in data:
            if item.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                result += item.data

        return result
