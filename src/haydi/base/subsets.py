from .domain import Domain
from .basictypes import Set, compare
from .cnf import canonical_builder
from .utils import ncr
import random


class Subsets(Domain):

    def __init__(self,
                 domain,
                 min_size=None,
                 max_size=None,
                 set_class=Set,
                 name=None):
        if min_size is None:
            min_size = 0
            if max_size is None:
                assert domain.size is not None
                max_size = domain.size
        elif max_size is None:
            max_size = min_size

        super(Subsets, self).__init__(name)
        self._set_flags_from_domain(domain)
        self.step_jumps = False  # steps not yet implemented
        self.domain = domain
        self.min_size = min_size
        self.max_size = max_size
        self.set_class = set_class
        assert not isinstance(self.set_class, str)
        if set_class != Set and set_class is not tuple:
            self.strict = False
        self.values = None

    def _compute_size(self):
        domain_size = self.domain.size
        return sum(ncr(domain_size, i)
                   for i in xrange(self.min_size, self.max_size+1))

    def create_iter(self, step=0):
        assert step == 0  # sets not yet implemented
        domain = self.domain
        min_size = self.min_size
        max_size = self.max_size

        set_class = self.set_class

        if min_size == 0:
            yield set_class(())

        if max_size == 0:
            return

        iters = [None] * max_size
        iters[0] = domain.create_iter()
        indices = [0] * max_size
        values = [None] * max_size
        i = 0
        last = max_size - 1
        while i >= 0:
            if i == last:
                for v in domain.create_iter(indices[i]):
                    values[i] = v
                    yield set_class(values)
                i -= 1
                continue
            try:
                values[i] = iters[i].next()
                indices[i] += 1
                ii = indices[i]
                i += 1
                indices[i] = ii
                iters[i] = domain.create_iter(ii)
                if i >= min_size:
                    yield set_class(values[:i])
            except StopIteration:
                i -= 1

    def generate_one(self):
        domain_size = self.size
        if self.max_size == self.min_size:
            size = self.min_size
        else:
            i = random.randint(0, domain_size - 1)
            for size in range(self.max_size, self.min_size, -1):
                c = ncr(domain_size, size)
                if i < c:
                    break
                i -= c
            else:
                size = self.min_size
        raise Exception("TODO")

    def create_cn_iter(self):
        domain = self.domain
        max_size = self.max_size
        min_size = self.min_size

        def make_fn(s, candidate):
            items = s.items
            if items and compare(items[-1], candidate) != -1:
                return None, None, None, None
            new_items = list(items)
            new_items.append(candidate)
            s = Set(new_items, True)
            if len(new_items) == max_size:
                return s, None, True, None
            return s, domain, len(new_items) >= min_size, None
        if min_size == 0:
            yield Set((), True)
        for item in canonical_builder(domain, Set((), True), make_fn, None):
            yield item

    def _remap_domains(self, transformation):
        return Subsets(transformation(self.domain), self.min_size,
                       self.max_size, self.set_class, self.name)
