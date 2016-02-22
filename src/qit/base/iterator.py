class Iterator(object):
    @staticmethod
    def is_split():
        return False

    @staticmethod
    def is_join():
        return False

    @staticmethod
    def is_transformation():
        return False

    @staticmethod
    def is_stateful():
        return True

    def __init__(self):
        self.size = None

    def __iter__(self):
        return self

    def create(self):
        return self

    def reset(self):
        raise NotImplementedError()

    def get_parents(self):
        return []

    def skip(self, start_index, count):
        raise NotImplementedError()

    def set(self, index):
        raise NotImplementedError()

    def to_list(self):
        return list(self)


class GeneratingIterator(Iterator):

    def __init__(self, generator_fn):
        super(GeneratingIterator, self).__init__()
        self.generator_fn = generator_fn

    def next(self):
        return self.generator_fn()

    def reset(self):
        pass


class EmptyIterator(Iterator):

    def __init__(self):
        super(EmptyIterator, self).__init__()

    def next(self):
        raise StopIteration()

    def reset(self):
        pass
