from threading import Thread

import time
from distributed import Scheduler, Nanny as Worker, Executor
from context import ParallelContext
from tornado.ioloop import IOLoop

from qit.base.runtime.distributediterator import DistributedSplitIterator
from qit.base.transform import JoinTransformation, YieldTransformation
from qit.base.factory import TransformationFactory


class DistributedContext(ParallelContext):
    io_loop = None
    io_thread = None

    def __init__(self,
                 n_workers=4,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=False):

        super(DistributedContext, self).__init__()

        self.n_workers = n_workers
        self.ip = ip
        self.port = port

        if not DistributedContext.io_loop:
            DistributedContext.io_loop = IOLoop()
            DistributedContext.io_thread = Thread(
                target=DistributedContext.io_loop.start)
            DistributedContext.io_thread.daemon = True
            DistributedContext.io_thread.start()

        if spawn_workers:
            self.scheduler = self._create_scheduler()
            self.workers = [self._create_worker()
                            for i in xrange(self.n_workers)]
            time.sleep(0.5)  # wait for workers to spawn

        self.executor = Executor((ip, port))

    def is_master(self):
        pass

    def transmit_to_master(self, message):
        pass

    def do_computation(self, computegraph, action):
        self.preprocess_splits(computegraph)

        self._distribute_iterator(computegraph,
                                  computegraph.last_transformation)

        for item in computegraph.create():
            if not action.handle_item(item):
                break

    def _distribute_iterator(self, computegraph, node):
        """
        :type computegraph: qit.base.computegraph.ComputeGraph
        :type node: qit.base.factory.TransformationFactory
        """
        assert node.klass == JoinTransformation

        split = node
        while split and not split.klass.is_split():
            split = computegraph.get_previous_node(split)

        assert split

        parallel_subgraph = computegraph.copy_starting_at(
            computegraph.get_previous_node(node))

        distributed_split = TransformationFactory(
            DistributedSplitIterator, computegraph.action_factory,
            self, parallel_subgraph
        )

        computegraph.replace(node, distributed_split)
        computegraph.reparent(distributed_split, split)

        yield_transform = TransformationFactory(YieldTransformation)
        computegraph.append(distributed_split, yield_transform)

    def _create_scheduler(self):
        scheduler = Scheduler(ip=self.ip)
        scheduler.start(self.port)
        return scheduler

    def _create_worker(self):
        worker = Worker(center_ip=self.ip,
                        center_port=self.port,
                        ncores=1)
        worker.start(0)
        return worker
