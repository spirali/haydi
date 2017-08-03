from .domain import Domain
from .basictypes import Set, compare
from .cnf import canonical_builder
from .utils import ncr
import random


class Subsets(Domain):
    """Domain of subsets of a domain

    When a single argument is provided, the resulting domain contains all
    subsets:

    Args:
        domain (Domain): Input domain

    When two arguments are provided, the resulting domain contains
    subsets of a given size:

    Args:
        domain (Domain): Input domain
        size (int): Size of subsets

    When three arguments are provided, the resulting domain contains
    subsets of a size in a given range:

    Args:
        domain (Domain): Input domain
        min_size (int): Minimum size of the subsets
        max_size (int): Max size of the subsets

    Examples:
        >>> a = hd.Range(3)
        >>> hd.Subsets(a)
        <Subsets size=8 {{}, {0}, {0, 1}, {0, 1, 2}, {0, 2}, ...}>
        >>> hd.Subsets(a, 2)
        <Subsets size=3 {{0, 1}, {0, 2}, {1, 2}}>
        >>> hd.Subsets(a, 0, 1)
        <Subsets size=4 {{}, {0}, {1}, {2}}>
    """

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
        self._cache = None

    def _compute_size(self):
        domain_size = self.domain.size
        return sum(ncr(domain_size, i)
                   for i in xrange(self.min_size, self.max_size+1))

    def _get_cache(self):
        # Since Subsets domain is exponentially larger than the inner
        # domain, this means that the inner domain is isually very small
        # so we are going to cache to it.
        if self._cache is not None:
            return self._cache
        else:
            self._cache = tuple(self.domain)
            return self._cache

    def _make_iter(self, step):
        assert step == 0  # sets not yet implemented
        cache = self._get_cache()
        min_size = self.min_size
        max_size = self.max_size

        set_class = self.set_class

        if min_size == 0:
            yield set_class(())

        if max_size == 0:
            return

        indices = [0] * max_size
        values = [cache[0]] * max_size
        i = 0
        last = max_size - 1
        size = len(cache)
        while i >= 0:
            if i == last:
                for index in xrange(indices[i], size):
                    values[i] = cache[index]
                    yield set_class(values)
                i -= 1
                continue

            ii = indices[i]
            if ii < size:
                values[i] = cache[ii]
                indices[i] += 1
                ii += 1
                i += 1
                indices[i] = ii
                if i >= min_size:
                    yield set_class(values[:i])
            else:
                i -= 1

    def generate_one(self):
        cache = self._get_cache()
        if self.max_size == self.min_size:
            size = self.min_size
        else:
            i = random.randint(0, self.size - 1)
            for size in range(self.max_size, self.min_size, -1):
                c = ncr(len(cache), size)
                if i < c:
                    break
                i -= c
            else:
                size = self.min_size
        return self.set_class(random.sample(cache, size))

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
