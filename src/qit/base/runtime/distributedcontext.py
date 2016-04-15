from threading import Thread

from distributed import Scheduler, Worker
from context import ParallelContext
from tornado.ioloop import IOLoop

from qit.base.runtime.distributediterator import DistributedSplitIterator
from qit.base.transform import JoinTransformation, YieldTransformation
from qit.base.factory import TransformationFactory

loop = IOLoop()
t = Thread(target=loop.start)
t.daemon = True
t.start()


class DistributedConfig(object):
    def __init__(self, worker_count=4,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_compute_nodes=True):
        self._worker_count = worker_count
        self._address = (ip, port)
        self._spawn_compute_nodes = spawn_compute_nodes

    @property
    def worker_count(self):
        return self._worker_count

    @property
    def ip(self):
        return self._address[0]

    @property
    def port(self):
        return self._address[1]

    @property
    def address(self):
        return self._address

    @property
    def spawn_compute_nodes(self):
        return self._spawn_compute_nodes


class DistributedContext(ParallelContext):
    def __init__(self, config):
        super(DistributedContext, self).__init__()
        self.config = config

        if config.spawn_compute_nodes:

            self.scheduler = self._create_scheduler(self.config.address)
            self.workers = [self._create_worker(self.config.address)
                        for i in xrange(self.config.worker_count)]

    def is_master(self):
        pass

    def transmit_to_master(self, message):
        pass

    def init(self):
        self._create_scheduler(self.address)

        for i in xrange(4):
            self._create_worker(self.address)

    def shutdown(self):
        pass

    def do_computation(self, graph, action):
        self.preprocess_splits(graph)

        node = graph.last_transformation
        while node:
            if node.klass.is_join():
                node = self._parallelize_iterator(graph, node)
            node = graph.get_previous_node(node)

        # collect notify messages and results
        for item in graph.create():
            action.handle_item(item)

    def _parallelize_iterator(self, graph, node):
        assert node.klass == JoinTransformation

        split = node
        while split and not split.klass.is_split():
            split = graph.get_previous_node(split)

        assert split

        parallel_subgraph = graph.copy_starting_at(
            graph.get_previous_node(node))

        distributed_split = TransformationFactory(
            DistributedSplitIterator, self.config, parallel_subgraph
        )

        graph.replace(node, distributed_split)
        graph.reparent(distributed_split, split)

        yield_transform = TransformationFactory(YieldTransformation)
        graph.append(distributed_split, yield_transform)

        return distributed_split

    def _create_scheduler(self, address):
        scheduler = Scheduler(ip=address[0])
        scheduler.start(address[1])
        return scheduler

    def _create_worker(self, address):
        worker = Worker(center_ip=address[0],
                        center_port=address[1],
                        ncores=1)
        worker.start(0)
        return worker
