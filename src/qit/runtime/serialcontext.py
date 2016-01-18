from context import Context
from message import Message, MessageTag


class SerialContext(Context):
    def run(self, iterator_graph):
        self.post_message(Message(MessageTag.CONTEXT_START))

        result = list(iterator_graph.nodes[0].iterator)

        self.post_message(Message(MessageTag.CONTEXT_STOP))

        return result

    def post_message(self, message):
        self._notify_message(message)
