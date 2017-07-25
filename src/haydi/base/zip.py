from .domain import Domain


class Zip(Domain):
    """
    Zip of domains.

    Produces tuples of consecutive elements from the given domains.
    The size of this domain is set to the smallest size of the given domains.

    Args:
        domains (sequence of Domains): Domains that will be zipped.
        name (str or None): Name of the domain

    Examples:
        >>> a = hd.Range(3)
        >>> b = hd.Values(("a", "b"))
        >>> hd.Zip((a, b))
        <Zip size=2 {(0, 'a'), (1, 'b')}>
    """

    def __init__(self, domains, name=None):
        super(Zip, self).__init__(name)
        domains = tuple(domains)
        self._set_flags_from_domains(domains)
        self.domains = domains
        self.strict = False
        self.step_jumps = not self.filtered

    def _compute_size(self):
        return min(d.size for d in self.domains)

    def create_cn_iter(self):
        raise NotImplementedError()

    def _make_iter(self, step):
        if not self.step_jumps:
            assert step == 0

        if not self.domains:
            return

        iters = tuple(map(lambda d: d.create_iter(step), self.domains))

        while True:
            values = tuple(map(lambda i: i.next(), iters))
            yield values

    def generate_one(self):
        return tuple(map(lambda d: d.generate_one(), self.domains))
