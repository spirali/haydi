import functools


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

    def first(self, default=None):
        try:
            return next(self)
        except StopIteration:
            return default

    def reduce(self, fn):
        return functools.reduce(fn, self)

    def all_max(self, key_fn):
        it = iter(self)
        try:
            obj = next(it)
        except StopIteration:
            return None
        max_value = key_fn(obj)
        objects = [obj]
        for obj in self:
            value = key_fn(obj)
            if value < max_value:
                continue
            elif value == max_value:
                objects.append(obj)
            else:
                objects = [obj]
                max_value = value
        return objects

    def reset(self):
        raise NotImplementedError()

    def get_parents(self):
        return []

    def skip(self, start_index, count):
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
