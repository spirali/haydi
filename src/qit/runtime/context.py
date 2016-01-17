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

    def post_message(self, message):
        raise NotImplementedError()

    def _notify_message(self, message):
        for callback in self.msg_callbacks:
            callback(message)
