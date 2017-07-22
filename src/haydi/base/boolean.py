from .values import Values


class Boolean(Values):
    """Two-element domain containing values 'True' and 'False'

    Example:

        >>> hd.Boolean()
        <Boolean size=2 {False, True}>
        >>> list(hd.Boolean())
        [True, False]

    """
    def __init__(self):
        super(Boolean, self).__init__((False, True))
        self.strict = True

    def create_cn_iter(self):
        return iter(self.values)
