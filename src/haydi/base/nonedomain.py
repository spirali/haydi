from .values import Values


class NoneDomain(Values):
    """A single-element domain containing None

    Example:

        >>> hd.NoneDomain()
        <NoneDomain size=1 {None}>
        >>> list(hd.NoneDomain())
        [None]

    """
    def __init__(self):
        super(NoneDomain, self).__init__((None,))
        self.strict = True

    def create_cn_iter(self):
        return iter(self.values)
