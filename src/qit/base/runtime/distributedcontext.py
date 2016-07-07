from threading import Thread

import time
from distributed import Scheduler, Nanny as Worker, Executor
from context import ParallelContext
from tornado.ioloop import IOLoop

from qit.base.action import Collect
from qit.base.runtime.distributediterator import DistributedSplitIterator
from qit.base.transform import JoinTransformation, YieldTransformation
from qit.base.factory import TransformationFactory, ActionFactory


class DistributedContext(ParallelContext):
    IO_LOOP_STARTED = False

    def __init__(self,
                 n_workers=4,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=False):

        super(DistributedContext, self).__init__()

        self.n_workers = n_workers
        self.ip = ip
        self.port = port

        if not DistributedContext.IO_LOOP_STARTED:
            loop = IOLoop()
            t = Thread(target=loop.start)
            t.daemon = True
            t.start()
            DistributedContext.IO_LOOP_STARTED = True

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

    def do_computation(self, graph, action, action_factory):
        self.preprocess_splits(graph)

        if not action.is_associative():
            action_factory = ActionFactory(Collect, graph.factory)

        node = graph.last_transformation
        while node:
            if node.klass.is_join():
                node = self._distribute_iterator(graph, node, action_factory)
                action_factory = ActionFactory(Collect, graph.factory)
            node = graph.get_previous_node(node)

        # collect notify messages and results
        for item in graph.create():
            action.handle_item(item)

    def _distribute_iterator(self, graph, node, action_factory):
        assert node.klass == JoinTransformation

        split = node
        while split and not split.klass.is_split():
            split = graph.get_previous_node(split)

        assert split

        parallel_subgraph = graph.copy_starting_at(
            graph.get_previous_node(node))

        distributed_split = TransformationFactory(
            DistributedSplitIterator, action_factory,
            self.config, parallel_subgraph
        )

        graph.replace(node, distributed_split)
        graph.reparent(distributed_split, split)

        yield_transform = TransformationFactory(YieldTransformation)
        graph.append(distributed_split, yield_transform)

        return distributed_split

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
