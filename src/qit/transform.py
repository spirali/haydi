
from iterator import Iterator
from parallel.parallelcontext import MessageTag


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


class MapTransformation(Transformation):

    def __init__(self, parent, fn):
        super(MapTransformation, self).__init__(parent)
        self.fn = fn

    def next(self):
        return self.fn(next(self.parent))


class FilterTransformation(Transformation):

    def __init__(self, parent, fn):
        super(FilterTransformation, self).__init__(parent)
        self.fn = fn

    def next(self):
        v = next(self.parent)
        while not self.fn(v):
            v = next(self.parent)
        return v


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


class SplitTransformation(Transformation):

    def __init__(self, parent):
        super(SplitTransformation, self).__init__(parent)
        self.processes = []
        self.join = None

    def next(self):
        return next(self.parent)

    def create_processes(self):
        process_count = 4
        size = self.size / process_count

        for i in xrange(process_count):
            self.processes.append(self.context.create_process())
            self.child.parent = self.skip(i * size, size)
            self.processes[i].compute(self.join.parent)

        return list(self.processes)


class JoinTransformation(Transformation):

    def __init__(self, parent):
        super(JoinTransformation, self).__init__(parent)
        self.split = None
        self.first_call = True
        self.result = []

    def next(self):
        assert self.split

        if self.first_call:
            self.split.create_processes()
            self.first_call = False

            for p in self.split.processes:
                output = p.get_data()
                assert output.tag == "result"
                self.result += output.data
            self.result = iter(self.result)

        return next(self.result)
