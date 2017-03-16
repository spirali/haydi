from .domain import Domain
from .basictypes import Set
from .canonicals import canonical_builder


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
        return self.product.size

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
        """
        domain = self.domain
        def make_fn(map_item, candidate):
            new_items = map_item.items[:]
            new_items.append((keys[len(new_items)], candidate))
            m = Map(new_items, True)
            if len(new_items) == len(keys):
                return m, None, True, None
            return m, value_domain, False, get_bounds(keys[len(new_items)])
        return canonical_builder(
            value_domain, Map(()), make_fn, get_bounds(keys[0]))
        """
