from .domain import Domain
from .domain import Product
from .basictypes import Map, compare
from .cnf import canonical_builder, get_bounds


class Mappings(Domain):

    def __init__(self, key_domain, value_domain, name=None):
        keys_size = key_domain.size
        if key_domain.filtered or keys_size is None:
            keys = tuple(sorted(key_domain, cmp=compare))
            keys_size = len(keys)
        else:
            keys = None
        product = Product((value_domain,) * keys_size)
        super(Mappings, self).__init__(name)
        self._set_flags_from_domain(value_domain)
        self.key_domain = key_domain
        self.value_domain = value_domain
        self.product = product
        self.keys = keys

    def _compute_size(self):
        return self.product.size

    def create_iter(self, step=0):
        keys = self.keys
        if keys is None:
            keys = tuple(sorted(self.key_domain, cmp=compare))
            self.keys = keys

        for values in self.product.create_iter(step):
            yield Map(zip(keys, values))

    def generate_one(self):
        return Map(zip(self.key_domain, self.product.generate_one()))

    def create_cn_iter(self):
        keys = self.keys
        if keys is None:
            keys = tuple(sorted(self.key_domain, cmp=compare))
            self.keys = keys

        value_domain = self.value_domain

        def make_fn(map_item, candidate):
            new_items = list(map_item.items)
            new_items.append((keys[len(new_items)], candidate))
            m = Map(new_items, True)
            if len(new_items) == len(keys):
                return m, None, True, None
            return m, value_domain, False, get_bounds(keys[len(new_items)])
        return canonical_builder(
            value_domain, Map(()), make_fn, get_bounds(keys[0]))
