class Iterator(object):

    size = None
    exact_size = False

    def __init__(self):
        self.size = None

    def __iter__(self):
        return self

    def create(self):
        return self

    def reset(self):
        raise NotImplementedError()

    def set(self, index):
        raise Exception("set not implemented for {}".format(type(self)))

    def to_list(self):
        return list(self)


class GeneratingIterator(Iterator):

    exact_size = True

    def __init__(self, generator_fn):
        super(GeneratingIterator, self).__init__()
        self.generator_fn = generator_fn

    def next(self):
        return self.generator_fn()

    def reset(self):
        pass

    def set(self):
        pass


class EmptyIterator(Iterator):

    size = 0
    exact_size = True

    def __init__(self):
        super(EmptyIterator, self).__init__()

    def next(self):
        raise StopIteration()

    def reset(self):
        pass

    def set(self):
        pass
