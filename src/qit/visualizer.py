from __future__ import print_function

from runtime.message import MessageListener, MessageTag


class ProgressConsoleVisualizer(MessageListener):
    def __init__(self, one_line=False):
        self.one_line = one_line

    def handle_message(self, message):
        if message.tag == MessageTag.SHOW_ITERATOR_PROGRESS:
            print("\r{}: {} %".format(message.data["name"], message.data["count"]), end=self._get_end())
        elif message.tag == MessageTag.CONTEXT_STOP:
            print("")

    def _get_end(self):
        if self.one_line:
            return ""
        else:
            return "\n"
