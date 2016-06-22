import math
from distributed import Executor

from qit.base.runtime.message import MessageTag, Message
from qit.base.transform import Transformation


def set_and_compute_unwrap(args):
    return set_and_compute(*args)


def set_and_compute(graph, action_factory, index, count):
    graph = graph.create()

    if graph.size:
        count = min(max(graph.size - index, 0), count)

    if count == 0:
        return Message(MessageTag.PROCESS_ITERATOR_STOP)

    graph.set(index)
    action = action_factory.create()

    try:
        for _ in xrange(count):
            item = graph.next()
            action.handle_item(item)
        return Message(MessageTag.PROCESS_ITERATOR_ITEM, action.get_result())
    except StopIteration:
        return Message(MessageTag.PROCESS_ITERATOR_ITEM, action.get_result())


class DistributedSplitIterator(Transformation):
    def __init__(self, parent, action_factory, config, parallel_subgraph):
        super(DistributedSplitIterator, self).__init__(parent)
        self.action_factory = action_factory
        self.config = config
        self.executor = Executor(config.address)
        self.action = self.action_factory.create()
        self.parallel_subgraph = parallel_subgraph
        self.subgraph_iterator = self.parallel_subgraph.create()
        self.iterated_count = 0

        if self.parent.size:
            batch = int(math.ceil(
                self.parent.size / float(config.worker_count)))
            self.batch = min(int(batch), 10000)
        else:
            self.batch = 100  # TODO: support generators

    def next(self):
        if self.parent.size and self.iterated_count >= self.parent.size:
            raise StopIteration()

        if self.parent.size:
            task_count = int(math.ceil(self.parent.size / float(self.batch)))
        else:
            task_count = self.config.worker_count

        tasks = self._distribute_map(task_count)
        data = self.executor.gather(tasks)

        result = []
        for item in data:
            if item.tag == MessageTag.PROCESS_ITERATOR_ITEM:
                result.append(item.data)

        return self.action.reduce(result)

    def _distribute_map(self, task_count):
        index = self.iterated_count
        args = [(self.parallel_subgraph, self.action_factory,
                 index + i * self.batch, self.batch)
                for i in xrange(task_count)]
        self.iterated_count += task_count * self.batch

        return self.executor.map(set_and_compute_unwrap, args)

    def _distribute_submit(self, task_count):
        index = self.iterated_count
        args = [(index + i * self.batch, self.batch)
                for i in xrange(task_count)]
        self.iterated_count += task_count * self.batch

        return [self.executor.submit(set_and_compute, self.subgraph_iterator,
                                     self.action_factory, *arg)
                for arg in args]

    def _distribute_broadcast(self, task_count):
        index = self.iterated_count
        args = [(index + i * self.batch, self.batch)
                for i in xrange(task_count)]
        self.iterated_count += task_count * self.batch

        [data_future] = self.executor.scatter(
            [self.subgraph_iterator], broadcast=True)

        return [self.executor.submit(set_and_compute, data_future,
                                     self.action_factory, *arg)
                for arg in args]
