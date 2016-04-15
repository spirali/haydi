import time
from copy import copy
from iterator import Iterator


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

    def copy(self):
        t = copy(self)
        t.parent = t.parent.copy()
        return t

    def get_parents(self):
        return [self.parent]

    def skip(self, start_index, count):
        return self.parent.skip(start_index, count)

    def reset(self):
        self.parent.reset()

    def set(self, index):
        self.parent.set(index)


class YieldTransformation(Transformation):
    @staticmethod
    def is_stateful():
        return True

    def __init__(self, parent):
        super(YieldTransformation, self).__init__(parent)
        self.data = []
        self.index = 0

    def next(self):
        if self.index == len(self.data):
            self.data = self.parent.next()
            self.index = 0

        if len(self.data) == 0:
            raise StopIteration()

        item = self.data[self.index]
        self.index += 1
        return item


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

    def set(self, index):
        assert index < self.count
        self.parent.set(index)

    def __repr__(self):
        return "Take {} items".format(self.count)


class MapTransformation(Transformation):

    def __init__(self, parent, fn):
        super(MapTransformation, self).__init__(parent)
        self.fn = fn

    def next(self):
        return self.fn(next(self.parent))

    def set(self, index):
        self.parent.set(index)

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
