from .domain import Domain
from .basictypes import Set, compare
from .canonicals import canonical_builder, is_canonical
from .utils import ncr

class Sets(Domain):

    def __init__(self, domain, min_size=None, max_size=None, name=None):
        if min_size is None:
            min_size = 0
            if max_size is None:
                assert domain.size is not None
                max_size = domain.size
        elif max_size is None:
            max_size = min_size

        super(Sets, self).__init__(name)
        self._set_flags_from_domain(domain)
        self.step_jumps = False  # steps not yet implemented
        self.domain = domain
        self.min_size = min_size
        self.max_size = max_size
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

        if min_size == 0:
            yield Set(())

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
                    yield Set(values)
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
                    yield Set(values[:i])
            except StopIteration:
                i -= 1

    def generate_one(self):
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
