

class QitException(BaseException):
    pass


class InnerParallelContext(QitException):
    pass


class TooManySplits(QitException):
    pass
