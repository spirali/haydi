from threading import Thread
from datetime import datetime

import cloudpickle
import distributed
from distributed import Scheduler, Nanny as Worker, Executor, as_completed
from tornado.ioloop import IOLoop
import time
import itertools

from qit.base.iterator import NoValue


class DistributedContext(object):
    io_loop = None
    io_thread = None

    def __init__(self,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=0,
                 write_partial_results=None,
                 track_progress=False):

        self.worker_count = spawn_workers
        self.ip = ip
        self.port = port
        self.active = False
        self.write_partial_results = write_partial_results
        self.track_progress = track_progress
        self.execution_count = 0
        self.start_time = datetime.now()

        if not DistributedContext.io_loop:
            DistributedContext.io_loop = IOLoop()
            DistributedContext.io_thread = Thread(
                target=DistributedContext.io_loop.start)
            DistributedContext.io_thread.daemon = True
            DistributedContext.io_thread.start()

        if spawn_workers > 0:
            self.scheduler = self._create_scheduler()
            self.workers = [self._create_worker()
                            for i in xrange(spawn_workers)]
            time.sleep(0.5)  # wait for workers to spawn

        self.executor = Executor((ip, port))

    def run(self, domain,
            worker_reduce_fn, worker_reduce_init,
            global_reduce_fn, global_reduce_init):
        size = domain.steps
        assert size is not None  # TODO: Iterators without size

        workers = 0
        for name, value in self.executor.ncores().items():
            workers += value

        if workers == 0:
            raise Exception("There are no workers")

        batch_count = workers * 4
        batch_size = max(int(round(size / float(batch_count))), 1)
        batches = self._create_batches(batch_size, size, domain,
                                       worker_reduce_fn, worker_reduce_init)

        futures = self.executor.map(process_batch, batches)

        if self.track_progress:
            distributed.diagnostics.progress(futures)

        if self.write_partial_results is not None:
            results = []
            partial_results = []
            partial_count = 0

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                partial_results.append(result)

                if len(partial_results) % self.write_partial_results == 0:
                    self._write_partial_result(partial_results, partial_count)
                    partial_results = []
                    partial_count += 1

            self.execution_count += 1
        else:
            results = self.executor.gather(futures)

        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        results = results[:domain.size]  # trim results to required size

        if global_reduce_fn is None:
            return results
        else:
            if global_reduce_init is None:
                return reduce(global_reduce_fn, results)
            else:
                return reduce(global_reduce_fn, results, global_reduce_init)

    def _create_scheduler(self):
        scheduler = Scheduler(ip=self.ip)
        scheduler.start(self.port)
        return scheduler

    def _create_worker(self):
        worker = Worker(center_ip=self.ip,
                        center_port=self.port,
                        ncores=1)
        worker.start(0)
        return worker

    def _create_batches(self, batch_size, size,
                        domain,
                        worker_reduce_fn,
                        worker_reduce_init):
        batches = []
        i = 0

        while True:
            new = i + batch_size
            if i + batch_size <= size:
                batches.append((domain, i, batch_size,
                                worker_reduce_fn, worker_reduce_init))
                i = new
                if new == size:
                    break
            else:
                batches.append((domain, i, size - i,
                                worker_reduce_fn, worker_reduce_init))
                break

        return batches

    def _write_partial_result(self, partial_results, partial_count):
        with open("pyqit-{}-{}-{}".format(
                int(time.mktime(self.start_time.timetuple())),
                self.execution_count,
                partial_count), "w") as f:
            cloudpickle.dump(partial_results, f)


def process_batch(arg):
    domain, start, size, reduce_fn, reduce_init = arg
    iterator = domain.create_iterator()
    iterator.set_step(start)

    items = []
    try:
        for i in xrange(size):
            item = iterator.step()
            if item is not NoValue:
                items.append(item)
    except StopIteration:
        pass

    if reduce_fn is None:
        return items
    else:
        if reduce_init is None:
            return reduce(reduce_fn, items)
        else:
            return reduce(reduce_fn, items, reduce_init)
