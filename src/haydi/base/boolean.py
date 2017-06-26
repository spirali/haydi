from .values import Values


class Boolean(Values):
    """Two-element domain containing values 'True' and 'False'

    This domain is essentially equivalent to ``haydi.Values((False, True))``

    """
    def __init__(self):
        super(Boolean, self).__init__((False, True))
