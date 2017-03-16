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
        self.domain = domain
        self.min_size = min_size
        self.max_size = max_size
        self.values = None

    def _compute_size(self):
        return self.product.size

    def create_iter(self, step=0):
        raise Exception("TODO")

    def generate_one(self):
        raise Exception("TODO")

    def create_cn_iter(self):
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
