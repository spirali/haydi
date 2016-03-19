import logging

from mpicomm import MpiCommunicator, MpiTag
from qit.base.transform import Transformation


class Batch(object):
    def __init__(self, count):
        self.count = count
        self.items = []
        self.item_index = 0

    def add(self, item):
        self.items.append(item)

    def add_all(self, items):
        self.items += items

    def get_all(self):
        items = self.items
        self.items = []
        self.item_index = 0
        return items

    def get_single(self):
        item = self.items[self.item_index]
        self.item_index += 1
        return item

    def is_ready(self):
        return len(self.items) >= self.count

    def has_items(self):
        return self.item_index < len(self.items)


class MpiIterator(Transformation):
    def __init__(self, parent):
        super(MpiIterator, self).__init__(parent)
        self.comm = MpiCommunicator()

    def log(self, str):
        logging.debug(str)


class MpiReceiveIterator(MpiIterator):
    def __init__(self, parent, group_count,
                 source=MpiCommunicator.ANY_SOURCE,
                 tag=MpiCommunicator.ANY_TAG):
        super(MpiReceiveIterator, self).__init__(parent)
        self.group_count = group_count
        self.stop_count = 0
        self.source = source
        self.tag = tag
        self.batch = Batch(0)

    def next(self):
        if self.batch.has_items():
            return self.batch.get_single()

        message = self.comm.recv()

        if message.tag == MpiTag.ITERATOR_ITEM:
            self.batch.add_all(message.data)
            return self.next()
        elif message.tag == MpiTag.ITERATOR_STOP:
            self.stop_count += 1
            if self.group_count == self.stop_count:
                raise StopIteration()
            else:
                return self.next()


class MpiRegionJoinIterator(MpiIterator):
    def __init__(self, parent, destination, batch=300):
        super(MpiRegionJoinIterator, self).__init__(parent)
        self.destination = destination
        self.batch = Batch(batch)

    def next(self):
        try:
            item = next(self.parent)
            self.batch.add(item)

            if self.batch.is_ready():
                self._give_result(self.batch.get_all())
        except StopIteration:
            leftover = self.batch.get_all()

            if len(leftover) > 0:
                self._give_result(leftover)

            self.comm.send("", self.destination, tag=MpiTag.ITERATOR_STOP)
            raise StopIteration()

    def _give_result(self, items):
        self.comm.send(items, self.destination, tag=MpiTag.ITERATOR_ITEM)


class MpiRegionSplitIterator(MpiIterator):
    def __init__(self, parent, source):
        super(MpiRegionSplitIterator, self).__init__(parent)
        self.source = source
        self.batch = Batch(0)

    def next(self):
        if self.batch.has_items():
            return self.batch.get_single()

        message = self.comm.recv(self.source, MpiCommunicator.ANY_TAG)

        if message.tag == MpiTag.NODE_JOB_OFFER:
            self.batch.add_all(message.data)
            return self.next()
        elif message.tag == MpiTag.ITERATOR_STOP:
            raise StopIteration()


class MpiSplitIterator(MpiIterator):
    def __init__(self, parent, group, batch=300):
        super(MpiSplitIterator, self).__init__(parent)
        self.group = group
        self.group_index = 0
        self.batch = Batch(batch)

    def next(self):
        try:
            item = next(self.parent)
            self.batch.add(item)

            if self.batch.is_ready():
                self._distribute(self.batch.get_all())
        except StopIteration:
            leftover = self.batch.get_all()
            if len(leftover) > 0:
                self._distribute(leftover)

            for node in self.group:
                self.comm.send("", node, MpiTag.ITERATOR_STOP)
            raise StopIteration()

    def _distribute(self, items):
        self.comm.send(items, self._get_target(), MpiTag.NODE_JOB_OFFER)

    def _get_target(self):
        target = self.group[self.group_index]
        self.group_index = (self.group_index + 1) % len(self.group)
        return target
