from enum import Enum


class ProcessMessage(object):
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data


class MessageTag(Enum):
    ITERATOR_PROGRESS = "ITERATOR_PROGRESS"


class ParallelContext(object):
    def __init__(self):
        self.msg_callbacks = []

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def run(self, iterator):
        raise NotImplementedError()

    def init(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()

    def create_process(self):
        raise NotImplementedError()

    def destroy_process(self, process):
        raise NotImplementedError()

    def on_message_received(self, callback):
        self.msg_callbacks.append(callback)

    def post_message(self, tag, iterator_id, data=None):
        raise NotImplementedError()

    def _notify_message(self, tag, iterator_id, data):
        if isinstance(tag, MessageTag):
            tag = tag.value

        for callback in self.msg_callbacks:
            callback(tag, iterator_id, data)
