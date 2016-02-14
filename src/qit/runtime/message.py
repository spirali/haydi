class MessageTag(object):
    SHOW_ITERATOR_PROGRESS = "show_iterator_progress"

    CONTEXT_START = "context_start"
    CONTEXT_STOP = "context_stop"

    NOTIFICATION_MESSAGE = "notification_message"

    PROCESS_START = "process_start"
    PROCESS_STOP = "process_stop"
    PROCESS_ITERATOR_ITEM = "process_iterator_item"
    PROCESS_ITERATOR_STOP = "process_iterator_stop"

    CALCULATION_STOP = "calculation_stop"


class Message(object):
    def __init__(self, tag, data=None):
        self.tag = tag

        if data is None:
            data = {}

        self.data = data

    def __repr__(self):
        return "[{}]: {}".format(self.tag, self.data)


class MessageListener(object):
    def handle_message(self, message):
        raise NotImplementedError()
