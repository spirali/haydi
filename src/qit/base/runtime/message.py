class MessageTag(object):
    ITERATOR_ITEM = "iterator_item"
    ITERATOR_STOP = "iterator_stop"


class Message(object):
    def __init__(self, tag, data=None):
        self.tag = tag

        if data is None:
            data = {}

        self.data = data

    def __repr__(self):
        return "[{}]: {}".format(self.tag, self.data)
