class Message(object):
    def __init__(self, tag, data=None):
        self.tag = tag
        self.data = data

    def __repr__(self):
        return "[{}]: {}".format(self.tag, self.data)


class MessageListener(object):
    def handle_message(self, message):
        raise NotImplementedError()
