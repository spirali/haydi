
from iterator import Iterator
from runtime.context import MessageTag


class Transformation(Iterator):

    def __init__(self, parent):
        super(Transformation, self).__init__()
        self.parent = parent
        self.size = parent.size
        self.child = None

    def get_parents(self):
        return [self.parent]

    def skip(self, start_index, count):
        return self.parent.skip(start_index, count)


class TakeTransformation(Transformation):

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


class ShowTransformation(Transformation):

    def __init__(self, parent, notify_count):
        super(ShowTransformation, self).__init__(parent)
        self.notify_count = notify_count
        self.count = 0

    def next(self):
        value = next(self.parent)

        self.count += 1

        if self.count % self.notify_count == 0:
            size = self.parent.size
            if size is None:
                self.context.post_message(MessageTag.ITERATOR_PROGRESS, self.id, self.count)
            else:
                self.context.post_message(MessageTag.ITERATOR_PROGRESS, self.id, (self.count / float(size)) * 100)

        return value

    def __repr__(self):
        return "Show every {} items".format(self.notify_count)


class SplitTransformation(Transformation):

    def __init__(self, parent, process_count):
        super(SplitTransformation, self).__init__(parent)
        self.process_count = process_count

    def next(self):
        return next(self.parent)

    def __repr__(self):
        return "Split"


class JoinTransformation(Transformation):

    def __init__(self, parent):
        super(JoinTransformation, self).__init__(parent)

    def next(self):
        return next(self.parent)

    def __repr__(self):
        return "Join"
