
from .domain import Domain, StepSkip
from .values import Values

import math
from collections import namedtuple


class Product(Domain):

    _generator_cache = None

    def __init__(self,
                 domains,
                 name=None,
                 unordered=False,
                 cache_size=0):
        domains = tuple(domains)
        size = self._compute_size([d.size for d in domains], unordered)
        steps = self._compute_size([d.steps for d in domains], unordered)
        exact_size = all(d.exact_size for d in domains)
        super(Product, self).__init__(size, exact_size, steps, name)
        self.domains = tuple(domains)
        self.unordered = unordered
        self.cache_size = max(len(domains), cache_size) if cache_size else 0

        if unordered:
            if len(set(domains)) > 1:
                raise Exception("Not implemented for discitinct domains")

    def create_iter(self, step=0):
        if self.unordered:
            if self.exact_size:
                return self._create_uproduct_iter(step)
            else:
                return self.iterate_steps(step, self.steps)
        else:
            return self._create_product_iter(step)

    def create_step_iter(self, step):
        if self.unordered:
            return self._create_uproduct_step_iter(step)
        else:
            return self._create_product_step_iter(step)

    def _init_iters(self, step):
        if step:
            iters = []
            for d in self.domains:
                steps = d.steps
                iters.append(d.create_iter(step % steps))
                step /= steps
            return iters
        else:
            return [d.create_iter() for d in self.domains]

    def _init_step_iters(self, step):
        if step:
            iters = []
            for d in self.domains:
                steps = d.steps
                iters.append(d.create_step_iter(step % steps))
                step /= steps
            return iters
        else:
            return [d.create_step_iter(0) for d in self.domains]

    def _create_product_iter(self, step):
        if step >= self.steps:
            return
        domains = self.domains
        iters = self._init_iters(step)
        values = [None] * len(domains)
        ln = len(domains)

        i = ln - 1
        while i < ln:
            if i == 0:
                for v in iters[i]:
                    values[0] = v
                    yield tuple(values)
                iters[i] = domains[i].create_iter()
                i = 1
            else:
                try:
                    values[i] = next(iters[i])
                    i -= 1
                except StopIteration:
                    iters[i] = domains[i].create_iter()
                    i += 1

    def _init_uproduct_iter(self, index):
        assert len(self.domains) == 2
        steps = self.domains[0].steps - 1  # -1 to ignore diagonal
        # The root of y * size - ((y - 1) * y) / 2 - index
        # y * size = full rectangle
        # ((y-1) * y) / 2 = missing elements to full rectangle
        y = int(0.5 * (-math.sqrt(-8 * index + 4 * steps**2 + 4 * steps + 1) +
                       2 * steps + 1))
        x = index - y * steps + ((y - 1) * y / 2) + y
        return [x + 1, y]

    def _create_uproduct_iter(self, step):
        if step >= self.steps:
            return
        ln = len(self.domains)
        domain = self.domains[0]
        if step:
            indices = self._init_uproduct_iter(step)
        else:
            indices = range(len(self.domains))
            indices.reverse()

        iters = [None] * ln
        values = [None] * ln

        for i, d in reversed(list(enumerate(self.domains))):
            iters[i] = d.create_iter(indices[i])
            if i == 0:
                break
            try:
                values[i] = next(iters[i])
            except StopIteration:
                break
        while i < ln:
            if i == 0:
                for v in iters[i]:
                    values[0] = v
                    yield tuple(values)
                i = 1
            else:
                indices[i] += 1
                try:
                    values[i] = next(iters[i])
                    for j in xrange(i - 1, 0, -1):
                        indices[j] = indices[j + 1] + 1
                        iters[j] = domain.create_iter(indices[j])
                        values[j] = next(iters[j])

                    iters[0] = domain.create_iter(indices[1] + 1)
                    i = 0
                except StopIteration:
                    i += 1

    def _create_product_step_iter(self, step):
        if step >= self.steps:
            return
        domains = self.domains
        iters = self._init_step_iters(step)
        values = [None] * len(domains)
        ln = len(domains)
        w = 1
        weights = []
        for d in domains:
            weights.append(w)
            w *= d.steps

        i = ln - 1
        while i < ln:
            if i == 0:
                for v in iters[i]:
                    if isinstance(v, StepSkip):
                        yield v
                    else:
                        values[0] = v
                        yield tuple(values)
                iters[i] = domains[i].create_step_iter(0)
                i = 1
            else:
                try:
                    v = next(iters[i])
                    while isinstance(v, StepSkip):
                        yield StepSkip(weights[i] * v.value)
                        v = next(iters[i])
                    values[i] = v
                    i -= 1
                except StopIteration:
                    iters[i] = domains[i].create_step_iter(0)
                    i += 1

    def _create_uproduct_step_iter(self, step):
        domain = self.domains[0]
        if step >= self.steps:
            return
        if step:
            indices = self._init_uproduct_iter(step)
        else:
            indices = range(len(self.domains))
            indices.reverse()

        j_start, i = indices
        it = domain.create_step_iter(i)
        while i < domain.size:
            v1 = next(it)
            if isinstance(v1, StepSkip):
                s = domain.size - j_start
                count = 0
                for x in xrange(v1.value):
                    count += s
                    s -= 1
                yield StepSkip(count)
                j_start = i + 2
                i += 1
                continue
            i += 1
            it0 = domain.create_step_iter(j_start)
            for v0 in it0:
                if isinstance(v0, StepSkip):
                    yield v0
                else:
                    yield (v0, v1)
            j_start = i + 1

    def generate_one(self):
        if self._generator_cache:
            try:
                return next(self._generator_cache)
            except StopIteration:
                pass  # Let us generate new one

        if self.cache_size:
            if self.unordered:
                values = Values(
                    tuple(self.domains[0].generate(self.cache_size)))
                self._generator_cache = iter(Product(
                    (values,) * len(self.domains), unordered=True))
            else:
                if self._generator_cache:
                    try:
                        return next(self._generator_cache)
                    except StopIteration:
                        pass  # Let us generate new one
                values = [Values(tuple(d.generate(self.cache_size)))
                          for d in self.domains]
                self._generator_cache = iter(Product(values))

            return self._generator_cache.next()
        else:
            return tuple(d.generate_one() for d in self.domains)

    def _compute_size(self, sizes, unordered):
        if any(s is None for s in sizes):
            return None
        result = 1

        if unordered:
            for i, s in enumerate(sizes):
                result *= s - i
            return result / math.factorial(len(sizes))
        else:
            for s in sizes:
                result *= s
            return result

    def __mul__(self, other):
        return Product(self.domains + (other,))


def NamedProduct(named_domains,
                 type_name=None,
                 name=None,
                 unordered=False):
    def make_instance(value):
        return ntuple(*value)

    if type_name is None:
        if name is None:
            type_name = "NamedProduct"
        else:
            type_name = name
    ntuple = namedtuple(type_name, [n for n, d in named_domains])
    domain = Product([d for n, d in named_domains], unordered=unordered)
    domain = domain.map(make_instance)
    domain.name = name
    del n
    del d
    return domain
