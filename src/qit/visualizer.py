from __future__ import print_function

import matplotlib.pyplot as plt
import time

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


class ProgressPlotVisualizer(MessageListener):
    def __init__(self):
        self.values = []
        self.timestamps = []
        plt.ion()
        plt.ylabel("Items processed")
        plt.xlabel("Time (s)")

        self.label_set = False
        self.initial_timestamp = None

    def handle_message(self, message):
        if message.tag == MessageTag.SHOW_ITERATOR_PROGRESS:
            if not self.label_set and message.data["relative"]:
                plt.ylabel("% completed")
                plt.title("{0} progress".format(message.data["name"]))
                self.label_set = True

            self.values.append(message.data["count"])
            self.timestamps.append(time.time() - self.initial_timestamp)

            plt.plot(self.timestamps, self.values)
            plt.draw()
        elif message.tag == MessageTag.CONTEXT_START:
            self.initial_timestamp = time.time()
            plt.show()
        elif message.tag == MessageTag.CONTEXT_STOP:
            plt.ioff()
            plt.show()