from .domain import Domain
from .cnf import expand, is_canonical

import random


class Values(Domain):
    """
    A domain created from a collection of Python objects.

    Args:
        values (collection): A collection of items that is
                             used as the content for the new domain
        name (string): Name of domain

    Examples:

        >>> hd.Values(("a", "b", 123, 431))
        <Values size=4 {'a', 'b', 123, 431}>
    """

    step_jumps = True

    def __init__(self, values=None, name=None):
        super(Values, self).__init__(name)
        values = tuple(values)
        self._size = len(values)
        self.values = values

    def generate_one(self):
        return random.choice(self.values)

    def _make_iter(self, step):
        while step < len(self.values):
            yield self.values[step]
            step += 1
        raise StopIteration()

    def to_values(self, max_size=None):
        return self


class CnfValues(Domain):
    """
    A domain defined by canonical elements.

    The domain is automatically filled with all isomorphic elements.

    Args:
        values (collection): A collection of canonical items
        name (string): Name of domain

    Examples:

        >>> a = hd.ASet(3, "a")
        >>> a0, a1, a2 = a

        >>> list(hd.CnfValues((a0, "x")))
        [a0, a1, a2, 'x']

        >>> list(hd.CnfValues((a0, "x")).cnfs())
        [a0, 'x']
    """

    strict = True

    def __init__(self, values, name=None, _check=True):
        super(CnfValues, self).__init__(name)
        values = tuple(values)
        if _check:
            if not all(is_canonical(value) for value in values):
                raise Exception("CnfValues accepts only canonical values")
        self.values = values

    def _compute_size(self):
        return None

    def create_cn_iter(self):
        return iter(self.values)

    def create_iter(self, step=0):
        assert step == 0
        for item in self.values:
            for item2 in expand(item):
                yield item2

    def to_cnf_values(self, max_size=None):
        return self
