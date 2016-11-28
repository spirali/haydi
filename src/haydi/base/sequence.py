
from .domain import Domain


class Sequence(Domain):

    def __init__(self, domain, length, name=None):
        size = self._compute_size(domain.size, length)
        steps = self._compute_size(domain.steps, length)
        super(Sequence, self).__init__(size, domain.exact_size, steps, name)
        self.length = length
        self.domain = domain

    def create_iter(self, step=0):
        if step >= self.steps:
            return

        ln = self.length
        if ln == 0:
            yield ()
            return

        if step:
            iters = []
            steps = self.domain.steps
            for i in xrange(ln):
                iters.append(self.domain.create_iter(step % steps))
                step /= steps
        else:
            iters = [self.domain.create_iter() for i in xrange(ln)]

        value = [None] * ln
        i = ln - 1
        while i < ln:
            if i == 0:
                for v in iters[0]:
                    value[0] = v
                    yield tuple(value)
                i = 1
                iters[0] = self.domain.create_iter()
            else:
                try:
                    value[i] = next(iters[i])
                    i -= 1
                except StopIteration:
                    iters[i] = self.domain.create_iter()
                    i += 1

    def generate_one(self):
        return tuple(self.domain.generate_one() for i in xrange(self.length))

    def _compute_size(self, size, length):
        if size is None:
            return None
        result = 1
        for i in xrange(length):
            result *= size
        return result
