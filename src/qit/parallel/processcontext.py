import multiprocessing as mp

from parallelcontext import ParallelContext, ProcessMessage
from process import Process


class ProcessContext(ParallelContext):
    def __init__(self):
        super(ProcessContext, self).__init__()
        self.master = None

    def run(self, iterator):
        self.master = Process()

        with self.master:
            self.master.compute(iterator)

            while True:
                msg = self.master.get_data()  # blocks until it gets the result

                if msg.tag == "result":
                    return msg.data
                elif msg.tag == "notify":
                    self._notify_message(msg.data["tag"], msg.data["iterator_id"], msg.data["data"])

        return None

    def create_process(self):
        process = Process()
        process.start()
        return process

    def destroy_process(self, process):
        process.stop()

    def post_message(self, tag, iterator_id, data=None):  # called in different process
        self.master.msg_queue.put(ProcessMessage("notify", {
            "tag": tag,
            "iterator_id": iterator_id,
            "data": data
        }))

    def init(self):
        pass

    def shutdown(self):
        pass
