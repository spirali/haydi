from context import ParallelContext
from qit.exception import NotEnoughMpiNodes
from qit.factory import TransformationFactory
from qit.session import session
from qit.transform import Transformation

MpiRun = True

try:
    from mpi4py import MPI

    if MPI.COMM_WORLD.Get_size() < 2:
        raise Exception()
except:
    MpiRun = False


class MpiWorker(object):
    def __init__(self, size, rank):
        self.size = size
        self.rank = rank
        self.comm = MPI.COMM_WORLD
        session.set_worker(self)

    def run(self):
        while True:
            msg = self._receive_msg()
            if msg.tag == MpiTag.APP_QUIT:
                break
            elif msg.tag == MpiTag.CALCULATION_START:
                self._calculate(msg)

    def _calculate(self, msg):
        iterator = msg.data.create()

        for item in iterator:
            if self._has_msg(MpiTag.CALCULATION_STOP):
                break

    def _receive_msg(self):
        status = MPI.Status()
        msg = self.comm.recv(source=MPI.ANY_SOURCE,
                             tag=MPI.ANY_TAG, status=status)
        return MpiMessage(msg, status.tag, status.source)

    def _has_msg(self, tag=MPI.ANY_TAG, source=MPI.ANY_SOURCE):
        status = MPI.Status()
        self.comm.iprobe(source=source,
                         tag=tag,
                         status=status)
        return status.count > 0

    def post_message(self, msg):
        # send to master
        self.comm.send(msg, 0, tag=MpiTag.NOTIFICATION_MESSAGE)


class MpiMessage(object):
    def __init__(self, data=None, tag=None, source=None):
        self.data = data
        self.tag = tag
        self.source = source


class MpiTag(object):
    NOTIFICATION_MESSAGE = 100

    ITERATOR_ITEM = 200
    ITERATOR_STOP = 201

    APP_QUIT = 300

    NODE_JOB_REQUEST = 400
    NODE_JOB_OFFER = 401
    CALCULATION_START = 402
    CALCULATION_STOP = 403

    ITERATOR_REGION_START = 1000


class MpiIterator(Transformation):
    def __init__(self, parent):
        super(MpiIterator, self).__init__(parent)
        self.comm = MPI.COMM_WORLD

    def write(self, str):
        # print("[{0}]: {1}".format(self.comm.Get_rank(), str))
        pass


class MpiReceiveIterator(MpiIterator):
    def __init__(self, parent, group_count,
                 source=MPI.ANY_SOURCE,
                 tag=MPI.ANY_TAG):
        super(MpiReceiveIterator, self).__init__(parent)
        self.group_count = group_count
        self.stop_count = 0
        self.source = source
        self.tag = tag

    def next(self):
        self.write("Receive receiving...")
        status = MPI.Status()
        message = self.comm.recv(source=self.source,
                                 tag=self.tag,
                                 status=status)

        self.write("Receive received {}".format(message))

        if status.tag == MpiTag.ITERATOR_ITEM:
            return message
        elif status.tag == MpiTag.ITERATOR_STOP:
            self.stop_count += 1
            if self.group_count == self.stop_count:
                raise StopIteration()
            else:
                return self.next()


class MpiRegionJoinIterator(MpiIterator):
    def __init__(self, parent, destination):
        super(MpiRegionJoinIterator, self).__init__(parent)
        self.destination = destination

    def next(self):
        try:
            item = next(self.parent)

            self.write("RegionJoin sending to {0}".format(self.destination))
            self.comm.send(item, self.destination, tag=MpiTag.ITERATOR_ITEM)
        except:
            self.write("RegionJoin ending")
            self.comm.send("", self.destination, tag=MpiTag.ITERATOR_STOP)
            raise StopIteration()


class MpiRegionSplitIterator(MpiIterator):
    def __init__(self, parent, source):
        super(MpiRegionSplitIterator, self).__init__(parent)
        self.source = source

    def next(self):
        self.write("RegionSplit requesting data from {0}".format(self.source))
        self.comm.send("", self.source, tag=MpiTag.NODE_JOB_REQUEST)

        status = MPI.Status()
        message = self.comm.recv(source=self.source,
                                 tag=MPI.ANY_TAG,
                                 status=status)

        self.write("RegionSplit received item {}".format(message))

        if status.tag == MpiTag.NODE_JOB_OFFER:
            return message
        elif status.tag == MpiTag.ITERATOR_STOP:
            raise StopIteration()


class MpiSplitIterator(MpiIterator):
    def __init__(self, parent, group):
        super(MpiSplitIterator, self).__init__(parent)
        self.group = group

    def next(self):
        try:
            item = next(self.parent)
            self.write("Split generated item {0}".format(item))
            status = MPI.Status()
            self.comm.recv(source=MPI.ANY_SOURCE,
                           tag=MpiTag.NODE_JOB_REQUEST,
                           status=status)
            self.write("Split sending to {0}".format(status.source))
            self.comm.send(item, status.source, tag=MpiTag.NODE_JOB_OFFER)
        except:
            for node in self.group:
                self.comm.send("", node, MpiTag.ITERATOR_STOP)
            raise StopIteration()


class MpiContext(ParallelContext):
    def __init__(self):
        super(MpiContext, self).__init__()
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()
        self.worker_index = 1

        if self.comm.Get_size() < 2:
            raise BaseException("MPI context has to be run with at"
                                "least 2 MPI processes")

    def init(self):
        pass

    def is_master(self):
        return self.rank == 0

    def compute_action(self, graph, action):
        self.preprocess_splits(graph)

        first_worker = self._fetch_worker()
        previous_worker = first_worker

        for node in graph.nodes:
            if node.factory.klass.is_join():
                previous_worker = self._parallelize_iterator(graph,
                                                             node,
                                                             previous_worker)

        start_iterator = TransformationFactory(MpiRegionJoinIterator, 0)
        graph.append(graph.last_transformation, start_iterator)

        self._distribute_computation(first_worker, graph)

        return self._master(graph, action)

    def transmit_to_master(self, message):
        self.comm.send(message, 0, MpiTag.NOTIFICATION_MESSAGE)

    def finish_computation(self):
        for worker in xrange(1, self.worker_index):
            self.comm.send("end", worker, MpiTag.CALCULATION_STOP)

    def _master(self, graph, action):
        try:
            while self._receive_msg(action):
                pass
        except StopIteration:
            self.finish_computation()

        while True:
            status = MPI.Status()
            self.comm.iprobe(source=MPI.ANY_SOURCE,
                             tag=MPI.ANY_TAG,
                             status=status)
            if status.count > 0:
                self._receive_msg(action)
            else:
                break

        return action.get_result()

    def _receive_msg(self, action):
        status = MPI.Status()
        message = self.comm.recv(source=MPI.ANY_SOURCE,
                                 tag=MPI.ANY_TAG,
                                 status=status)

        if status.tag == MpiTag.NOTIFICATION_MESSAGE:
            session.post_message(message)
        elif status.tag == MpiTag.ITERATOR_ITEM:
            if not action.handle_item(message):
                raise StopIteration()
        elif status.tag == MpiTag.ITERATOR_STOP:
            return False

        return True

    def _parallelize_iterator(self, graph, join, previous_worker):
        split = join

        # assumes that the graph is correct with respect
        # to split-join pairing and we deal only with transformations
        # TODO: copy iterator attributes
        while not split.factory.klass.is_split():
            split = split.input

        process_count = split.factory.args[0]

        # MPI > parallel region > Join
        split_worker = self._fetch_worker()
        parallel_iter_begin = TransformationFactory(MpiRegionJoinIterator,
                                                    previous_worker)
        parallel_begin_node = graph.replace(join, parallel_iter_begin)
        parallel_iter_end = TransformationFactory(MpiRegionSplitIterator,
                                                  split_worker)
        parallel_end_node = graph.replace(split, parallel_iter_end)

        # MPI > Join
        mpi_join = TransformationFactory(MpiReceiveIterator,
                                         process_count)
        graph.append(parallel_begin_node, mpi_join)

        workers = [self._fetch_worker() for i in xrange(process_count)]

        # Split > MPI
        mpi_distribute = TransformationFactory(MpiSplitIterator, workers)
        mpi_distribute_node = graph.prepend(parallel_end_node, mpi_distribute)

        self._distribute_computation(split_worker,
                                     graph.copy_starting_at(
                                         mpi_distribute_node))

        # assign to multiple nodes
        for i in xrange(process_count):
            self._distribute_computation(workers[i],
                                         graph.copy_starting_at(
                                             parallel_begin_node))

        return split_worker

    def _distribute_computation(self, worker, graph):
        self.comm.send(graph, worker, MpiTag.CALCULATION_START)

    def _fetch_worker(self):
        if self.worker_index >= self.size:
            raise NotEnoughMpiNodes()

        index = self.worker_index
        self.worker_index += 1
        return index

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
if rank != 0:
    MpiWorker(size, rank).run()
    exit(0)
