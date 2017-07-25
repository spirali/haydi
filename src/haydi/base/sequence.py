
from .domain import Domain
from .product import Product
from .join import Join
from .cnf import canonical_builder


class Sequences(Domain):

    """Sequences over a domain

    When two arguments are provided, the resulting domain contains
    sequences of a given length:

    Args:
        domain (Domain): Input domain
        length (int): Size of sequences

    When three arguments are provided, the resulting domain contains
    sequences of a length in a given range:

    Args:
        domain (Domain): Input domain
        min_size (int): Minimum length of the sequences
        max_size (int): Maximum length of the sequences

    Examples:
        >>> a = hd.Range(3)
        >>> hd.Sequences(a, 2)
        <Sequences size=9 {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), ...}>
        >>> hd.Sequences(a, 0, 2)
        <Sequences size=13 {(), (0,), (1,), (2,), (0, 0), ...}>
    """

    def __init__(self, domain, min_length, max_length=None, name=None):
        if max_length is None:
            max_length = min_length

        super(Sequences, self).__init__(name)
        self._set_flags_from_domain(domain)
        self.min_length = min_length
        self.max_length = max_length
        self.domain = domain

        if min_length == max_length:
            helper = Product((domain,) * min_length)
        else:
            helper = Join([Product((domain,) * i)
                          for i in range(min_length, max_length + 1)])
        self.helper = helper

    def _compute_size(self):
        return self.helper.size

    def create_cn_iter(self):
        def make_fn(item, candidate):
            item += (candidate,)
            if len(item) == max_length:
                return item, None, True, None
            return item, domain, len(item) >= min_length, None
        domain = self.domain
        max_length = self.max_length
        min_length = self.min_length
        if min_length == 0:
            yield ()
        for item in canonical_builder(domain, (), make_fn, None):
            yield item

    def _make_iter(self, step):
        return self.helper.create_iter(step)

    def generate_one(self):
        return self.helper.generate_one()

    def _remap_domains(self, transformation):
        return Sequences(transformation(self.domain), self.min_length,
                         self.max_length, self.name)
