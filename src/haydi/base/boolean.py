from .values import Values


class Boolean(Values):
    """Two-element domain containing values 'True' and 'False'

    This domain is equivalent to ``haydi.Values((False, True), name="Boolean")``

    Example:

        >>> hd.Boolean()
        <Boolean size=2 {False, True}>

    """
    def __init__(self):
        super(Boolean, self).__init__((False, True))
