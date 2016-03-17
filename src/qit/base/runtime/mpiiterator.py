from mpicomm import MpiCommunicator, MpiTag
from qit.base.transform import Transformation


class MpiIterator(Transformation):
    def __init__(self, parent):
        super(MpiIterator, self).__init__(parent)
        self.comm = MpiCommunicator()

    def write(self, str):
        # print("[{0}]: {1}".format(self.comm.rank, str))
        pass


class MpiReceiveIterator(MpiIterator):
    def __init__(self, parent, group_count,
                 source=MpiCommunicator.ANY_SOURCE,
                 tag=MpiCommunicator.ANY_TAG):
        super(MpiReceiveIterator, self).__init__(parent)
        self.group_count = group_count
        self.stop_count = 0
        self.source = source
        self.tag = tag

    def next(self):
        self.write("Receive receiving from {}, tag {}".format(
            self.source, self.tag))
        message = self.comm.recv()

        self.write("Receive received {}".format(message))

        if message.tag == MpiTag.ITERATOR_ITEM:
            return message.data
        elif message.tag == MpiTag.ITERATOR_STOP:
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
        except StopIteration:
            self.write("RegionJoin ending")
            self.comm.send("", self.destination, tag=MpiTag.ITERATOR_STOP)
            raise StopIteration()


class MpiRegionSplitIterator(MpiIterator):
    def __init__(self, parent, source):
        super(MpiRegionSplitIterator, self).__init__(parent)
        self.source = source

    def next(self):
        self.write("RegionSplit waits for data from {}".format(self.source))
        message = self.comm.recv(self.source, MpiCommunicator.ANY_TAG)

        self.write("RegionSplit received item {}".format(message))

        if message.tag == MpiTag.NODE_JOB_OFFER:
            return message.data
        elif message.tag == MpiTag.ITERATOR_STOP:
            raise StopIteration()


class MpiSplitIterator(MpiIterator):
    def __init__(self, parent, group):
        super(MpiSplitIterator, self).__init__(parent)
        self.group = group
        self.group_index = 0

    def next(self):
        try:
            item = next(self.parent)
            self.write("Split generated item {0}".format(item))

            target = self._get_target()

            self.write("Split sending to {0}".format(target))
            self.comm.send(item, target, tag=MpiTag.NODE_JOB_OFFER)
        except StopIteration:
            self.write("Split ending, notifying group {}".format(self.group))
            for node in self.group:
                self.comm.send("", node, MpiTag.ITERATOR_STOP)
            raise StopIteration()

    def _get_target(self):
        target = self.group[self.group_index]
        self.group_index = (self.group_index + 1) % len(self.group)
        return target
