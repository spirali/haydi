from enum import Enum


class ProcessMessage(object):
    def __init__(self, tag, data=None):
        self.tag = tag
        self.data = data

    def __repr__(self):
        return "[{}]: {}".format(self.tag, self.data)


class MessageTag(Enum):
    ITERATOR_PROGRESS = "ITERATOR_PROGRESS"


class Context(object):
    def __init__(self):
        self.msg_callbacks = []

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def run(self, iterator_graph):
        raise NotImplementedError()

    def init(self):
        pass

    def shutdown(self):
        pass

    def on_message_received(self, callback):
        self.msg_callbacks.append(callback)

    def post_message(self, tag, iterator_id, data=None):
        raise NotImplementedError()

    def _notify_message(self, tag, iterator_id, data):
        if isinstance(tag, MessageTag):
            tag = tag.value

        for callback in self.msg_callbacks:
            callback(tag, iterator_id, data)
