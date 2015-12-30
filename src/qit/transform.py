
from iterator import Iterator

class Transformation(Iterator):

    def __init__(self, parent):
        self.parent = parent


class TakeTransformation(Transformation):

    def __init__(self, parent, count):
        super(TakeTransformation, self).__init__(parent)
        self.count = count

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
