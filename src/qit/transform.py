
from iterator import Iterator
from runtime.message import Message, MessageTag


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


class ProgressTransformation(Transformation):

    def __init__(self, parent, name, notify_count):
        super(ProgressTransformation, self).__init__(parent)
        self.notify_count = notify_count
        self.name = name
        self.count = 0

    def next(self):
        value = next(self.parent)

        self.count += 1

        if self.count % self.notify_count == 0:
            size = self.parent.size
            count = self.count

            if size:
                count = (self.count / float(size)) * 100

            self.context.post_message(Message(MessageTag.SHOW_ITERATOR_PROGRESS, {
                "id": self.id,
                "name": self.name,
                "count": count,
                "total": self.size,
                "relative": True if self.size else None
            }))

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
        return "Split into {} processes".format(self.process_count)


class JoinTransformation(Transformation):

    def __init__(self, parent):
        super(JoinTransformation, self).__init__(parent)

    def next(self):
        return next(self.parent)

    def __repr__(self):
        return "Join"
