
from .domain import Domain, StepSkip
from .values import Values
from .canonicals import canonical_builder

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
        super(Product, self).__init__(name)
        self._set_flags_from_domains(domains)
        self.domains = tuple(domains)
        self.unordered = unordered
        self.cache_size = max(len(domains), cache_size) if cache_size else 0

        if unordered:
            if len(set(domains)) > 1:
                raise Exception("Not implemented for discitinct domains")

    def create_cn_iter(self):
        def make_fn(item, candidate):
            item += (candidate,)
            if len(item) == len(domains):
                return item, None, True, None
            return item, domains[len(item)], False, None
        domains = self.domains
        return canonical_builder(domains[0], (), make_fn, None)

    def create_iter(self, step=0):
        if self.unordered:
            if self.filtered:
                return self.iterate_steps(step, self.size)
            else:
                return self._create_uproduct_iter(step)
        else:
            return self._create_product_iter(step)

    def create_skip_iter(self, step):
        if self.unordered:
            return self._create_uproduct_step_iter(step)
        else:
            return self._create_product_step_iter(step)

    def _init_iters(self, step):
        if step:
            iters = []
            for d in reversed(self.domains):
                steps = d.size
                iters.append(d.create_iter(step % steps))
                step /= steps
            iters.reverse()
            return iters
        else:
            return [d.create_iter() for d in self.domains]

    def _create_product_iter(self, step):
        if step >= self.size:
            return

        domains = self.domains
        if not domains:
            yield ()
            return

        iters = self._init_iters(step)
        values = [None] * len(domains)
        last = len(domains) - 1
        i = 0
        while i >= 0:
            if i == last:
                for v in iters[i]:
                    values[i] = v
                    yield tuple(values)
                iters[i] = domains[i].create_iter()
                i -= 1
            else:
                try:
                    values[i] = next(iters[i])
                    i += 1
                except StopIteration:
                    iters[i] = domains[i].create_iter()
                    i -= 1

    def _init_uproduct_iter(self, index):
        assert len(self.domains) == 2
        steps = self.domains[0].size - 1  # -1 to ignore diagonal
        # The root of y * size - ((y - 1) * y) / 2 - index
        # y * size = full rectangle
        # ((y-1) * y) / 2 = missing elements to full rectangle
        y = int(0.5 * (-math.sqrt(-8 * index + 4 * steps**2 + 4 * steps + 1) +
                       2 * steps + 1))
        x = index - y * steps + ((y - 1) * y / 2) + y
        return [x + 1, y]

    def _create_uproduct_iter(self, step):
        if step >= self.size:
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
        if step >= self.size:
            return
        domains = self.domains
        w = 1
        weights = []
        for d in reversed(domains):
            weights.append(w)
            w *= d.size
        weights.reverse()

        values = [None] * len(domains)
        iters = []

        last = len(domains) - 1
        for i in xrange(last):  # We want to skip last
            it = domains[i].create_step_iter(step / weights[i])
            iters.append(it)
            try:
                v = it.next()
            except StopIteration:
                i += 1
                for j in xrange(i, len(domains)):
                    iters.append(domains[j].create_step_iter(0))
                break

            if isinstance(v, StepSkip):
                v = v.value
                if v > 1:
                    yield StepSkip((v - 1) * weights[i])
                s = weights[i] - step % weights[i]
                if s > 0:
                    yield StepSkip(s)
                for j in xrange(i + 1, len(domains)):
                    iters.append(domains[j].create_step_iter(0))
                break
            else:
                values[i] = v
                step = step % weights[i]
        else:
            i = last
            iters.append(domains[last].create_step_iter(step))

        while i >= 0:
            if i == last:
                for v in iters[i]:
                    if isinstance(v, StepSkip):
                        yield v
                    else:
                        values[last] = v
                        yield tuple(values)
                iters[i] = domains[i].create_step_iter(0)
                i -= 1
            else:
                try:
                    v = next(iters[i])
                    while isinstance(v, StepSkip):
                        yield StepSkip(weights[i] * v.value)
                        v = next(iters[i])
                    values[i] = v
                    i += 1
                except StopIteration:
                    iters[i] = domains[i].create_step_iter(0)
                    i -= 1

    def _create_uproduct_step_iter(self, step):
        domain = self.domains[0]
        if step >= self.size:
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

    def _compute_size(self):
        result = 1
        if self.unordered:
            for i, d in enumerate(self.domains):
                s = d.size
                if s is None:
                    return None
                result *= s - i
            return result / math.factorial(len(self.domains))
        else:
            for d in self.domains:
                s = d.size
                if s is None:
                    return None
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
