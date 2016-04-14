import logging
import sys

from context import ParallelContext
from qit.base.exception import NotEnoughMpiNodes
from qit.base.session import session
from qit.base.factory import TransformationFactory

from mpicomm import MpiTag, MpiCommunicator
from mpiiterator import MpiRegionJoinIterator, MpiRegionSplitIterator,\
    MpiReceiveIterator, MpiSplitIterator
import mpidetection
from mpi4py import MPI


def shutdown_workers():
    comm = MpiCommunicator()

    if comm.rank == 0:
        for i in xrange(1, comm.size):
            comm.send("quit", i, tag=MpiTag.APP_QUIT)


class MpiWorker(object):
    def __init__(self):
        self.comm = MpiCommunicator()
        session.set_worker(self)

    def run(self):
        while True:
            msg = self.comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            if msg.tag == MpiTag.APP_QUIT:
                break
            elif msg.tag == MpiTag.CALCULATION_START:
                self._calculate(msg)

    def _calculate(self, msg):
        iterator = msg.data.create()

        for item in iterator:
            if self.comm.has_message(MpiTag.CALCULATION_STOP):
                break

    def post_message(self, msg):
        # send to master
        self.comm.send(msg, 0, tag=MpiTag.NOTIFICATION_MESSAGE)


class MpiContext(ParallelContext):
    def __init__(self):
        super(MpiContext, self).__init__()
        self.comm = MpiCommunicator()
        self.worker_index = 1

        if self.comm.size < 2:
            raise BaseException("MPI context has to be run with at"
                                "least 2 MPI processes")

    def init(self):
        pass

    def is_master(self):
        return self.comm.rank == 0

    def do_computation(self, graph, action):
        self.preprocess_splits(graph)

        worker = self._fetch_worker()
        worker_node = TransformationFactory(MpiRegionJoinIterator, 0)
        graph.append(graph.last_transformation, worker_node)

        for node in reversed(graph.nodes):
            if node.klass.is_join():
                worker, worker_node = self._parallelize_iterator(
                    graph, node, worker, worker_node)

        if worker is not None:
            self._distribute_computation(worker,
                                         graph.copy_starting_at(worker_node))

        return self._master(action)

    def transmit_to_master(self, message):
        self.comm.send(message, 0, MpiTag.NOTIFICATION_MESSAGE)

    def finish_computation(self):
        for worker in xrange(1, self.worker_index):
            self.comm.send("end", worker, MpiTag.CALCULATION_STOP)

    def _master(self, action):
        try:
            while self._receive_msg(action):
                pass
        except StopIteration:
            self.finish_computation()

        while True:
            if self.comm.has_message():
                self._receive_msg(action)
            else:
                break

        return action.get_result()

    def _receive_msg(self, action):
        msg = self.comm.recv()

        if msg.tag == MpiTag.NOTIFICATION_MESSAGE:
            session.post_message(msg.data)
        elif msg.tag == MpiTag.ITERATOR_ITEM:
            for item in msg.data:
                if not action.handle_item(item):
                    raise StopIteration()
        elif msg.tag == MpiTag.ITERATOR_STOP:
            return False

        return True

    def _parallelize_iterator(self, graph, join, worker, start_node):
        """
        :param graph: graph
        :param join: join transformation
        :param worker: worker assigned for current receive
        :param start_node: starting node of the assigned worker
        :return: worker assigned for next split
        """
        split = join

        # assumes that the graph is correct with respect
        # to split-join pairing and we deal only with transformations
        # TODO: copy iterator attributes
        while not split.klass.is_split():
            split = graph.get_previous_node(split)

        process_count = split.args[0]

        # MPI > parallel region > Join
        split_worker = self._fetch_worker()

        parallel_iter_begin = TransformationFactory(MpiRegionJoinIterator,
                                                    worker)
        graph.replace(join, parallel_iter_begin)
        parallel_iter_end = TransformationFactory(MpiRegionSplitIterator,
                                                  split_worker)
        graph.replace(split, parallel_iter_end)

        # MPI > Join
        mpi_join = TransformationFactory(MpiReceiveIterator,
                                         process_count)
        graph.append(parallel_iter_begin, mpi_join)

        workers = [self._fetch_worker() for _ in xrange(process_count)]

        # Split > MPI
        mpi_distribute = TransformationFactory(MpiSplitIterator, workers)
        graph.prepend(parallel_iter_end, mpi_distribute)

        # this has to be distributed first
        self._distribute_computation(worker,
                                     graph.copy_starting_at(start_node))

        # assign to multiple nodes
        for i in xrange(process_count):
            self._distribute_computation(workers[i],
                                         graph.copy_starting_at(
                                             parallel_iter_begin))

        return split_worker, mpi_distribute

    def _distribute_computation(self, worker, graph):
        self.comm.send(graph, worker, MpiTag.CALCULATION_START,
                       synchronous=True)

    def _fetch_worker(self):
        if self.worker_index >= self.comm.size:
            raise NotEnoughMpiNodes()

        index = self.worker_index
        self.worker_index += 1
        return index


if mpidetection.mpi_available:
    comm = MpiCommunicator()

    if "-d" in sys.argv:
        logging.basicConfig(filename="mpi-{}.log".format(comm.rank),
                            filemode="w",
                            format="%(asctime)s %(message)s",
                            datefmt="%I:%M:%S",
                            level=logging.DEBUG)

    if comm.rank != 0:
        MpiWorker().run()
        exit(0)
