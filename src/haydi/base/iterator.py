class NoValueType(object):

    def __init__(self):
        # Make sure that instance is unique
        assert NoValue is None

    def __repr__(self):
        return "NoValue"

NoValue = None
NoValue = NoValueType()


class Iterator(object):

    size = None
    steps = None
    exact_size = False

    def __init__(self):
        self.size = None

    def __iter__(self):
        return self

    def create(self):
        return self

    def reset(self):
        raise NotImplementedError()

    def set_step(self, index):
        raise Exception("set not implemented for {}".format(type(self)))

    def to_list(self):
        return list(self)

    def to_step_list(self):
        return list(StepIterator(self))

    def step(self):
        return self.next()


class StepIterator(Iterator):

    def __init__(self, iterator):
        self.iterator = iterator

    def next(self):
        return self.iterator.step()

    def step(self):
        return self.iterator.step()

    def set_step(self, index):
        self.iterator.set_step(index)

    def reset(self):
        self.iterator.reset()


class GeneratingIterator(Iterator):

    exact_size = True

    def __init__(self, generator_fn):
        super(GeneratingIterator, self).__init__()
        self.generator_fn = generator_fn

    def next(self):
        return self.generator_fn()

    def reset(self):
        pass

    def set_step(self, index):
        pass


class EmptyIterator(Iterator):

    size = 0
    steps = 0
    exact_size = True

    def __init__(self):
        super(EmptyIterator, self).__init__()

    def next(self):
        raise StopIteration()

    def reset(self):
        pass

    def set_step(self, index):
        assert index == 0
