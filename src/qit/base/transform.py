import time

from runtime.message import Message, MessageTag

from iterator import Iterator
from qit.base.session import session


class Transformation(Iterator):
    @staticmethod
    def is_transformation():
        return True

    @staticmethod
    def is_stateful():
        return False

    def __init__(self, parent):
        super(Transformation, self).__init__()
        self.parent = parent
        self.size = parent.size

    def get_parents(self):
        return [self.parent]

    def skip(self, start_index, count):
        return self.parent.skip(start_index, count)

    def reset(self):
        self.parent.reset()


class TakeTransformation(Transformation):
    @staticmethod
    def is_stateful():
        return True

    def __init__(self, parent, count):
        super(TakeTransformation, self).__init__(parent)
        self.count = count

        if parent.size is not None:
            self.size = max(parent.size, self.count)

    def next(self):
        if self.count <= 0:
            raise StopIteration()
        self.count -= 1
        return next(self.parent)

    def __repr__(self):
        return "Take {} items".format(self.count)


class MapTransformation(Transformation):

    def __init__(self, parent, fn):
        super(MapTransformation, self).__init__(parent)
        self.fn = fn

    def next(self):
        return self.fn(next(self.parent))

    def __repr__(self):
        return "Map"


class FilterTransformation(Transformation):

    def __init__(self, parent, fn):
        super(FilterTransformation, self).__init__(parent)
        self.fn = fn

    def next(self):
        v = next(self.parent)
        while not self.fn(v):
            v = next(self.parent)
        return v

    def __repr__(self):
        return "Filter"


class ProgressTransformation(Transformation):
    @staticmethod
    def is_stateful():
        return True

    def __init__(self, parent, name, notify_count):
        super(ProgressTransformation, self).__init__(parent)
        self.notify_count = notify_count
        self.name = name
        self.count = 0

    def next(self):
        value = next(self.parent)

        self.count += 1

        if self.count % self.notify_count == 0:
            count = self.count

            session.post_message(Message(MessageTag.SHOW_ITERATOR_PROGRESS, {
                "name": self.name,
                "count": count,
                "total": self.size,
                "relative": True if self.size else None
            }))

        return value

    def __repr__(self):
        return "Show every {} items".format(self.notify_count)


class SplitTransformation(Transformation):
    @staticmethod
    def is_split():
        return True

    def __init__(self, parent, process_count):
        super(SplitTransformation, self).__init__(parent)
        self.process_count = process_count

    def next(self):
        return next(self.parent)

    def __repr__(self):
        return "Split into {} processes".format(self.process_count)


class JoinTransformation(Transformation):
    @staticmethod
    def is_join():
        return True

    def __init__(self, parent):
        super(JoinTransformation, self).__init__(parent)

    def next(self):
        return next(self.parent)

    def __repr__(self):
        return "Join"


class TimeoutTransformation(Transformation):
    def __init__(self, parent, timeout):
        super(TimeoutTransformation, self).__init__(parent)
        self.timeout = timeout
        self.start = None

    def next(self):
        if not self.start:
            self.start = time.time()

        if time.time() - self.start >= self.timeout:
            raise StopIteration()
        else:
            return next(self.parent)
