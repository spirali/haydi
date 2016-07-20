from threading import Thread
from distributed import Scheduler, Nanny as Worker, Executor
from tornado.ioloop import IOLoop
import time
import itertools


class DistributedContext(object):
    io_loop = None
    io_thread = None

    def __init__(self,
                 n_workers=4,
                 ip="127.0.0.1",
                 port=8787,
                 spawn_workers=False):

        self.n_workers = n_workers
        self.ip = ip
        self.port = port
        self.active = False

        if not DistributedContext.io_loop:
            DistributedContext.io_loop = IOLoop()
            DistributedContext.io_thread = Thread(
                target=DistributedContext.io_loop.start)
            DistributedContext.io_thread.daemon = True
            DistributedContext.io_thread.start()

        if spawn_workers:
            self.scheduler = self._create_scheduler()
            self.workers = [self._create_worker()
                            for i in xrange(self.n_workers)]
            time.sleep(0.5)  # wait for workers to spawn

        self.executor = Executor((ip, port))

    def run(self, domain,
            worker_reduce_fn, worker_reduce_init,
            global_reduce_fn, global_reduce_init):
        size = domain.size
        assert size is not None  # TODO: Iterators without size

        workers = 0
        for name, value in self.executor.ncores().items():
            workers += value

        if workers == 0:
            raise Exception("There are no workers")

        batch_count = workers * 4
        batch_size = int(round(size / float(batch_count)))
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

        futures = self.executor.map(process_batch, batches)
        results = self.executor.gather(futures)
        if worker_reduce_fn is None:
            results = list(itertools.chain.from_iterable(results))

        if global_reduce_fn is None:
            return results
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


def process_batch(arg):
    domain, start, size, reduce_fn, reduce_init = arg
    iterator = domain.create_iterator()
    iterator.set(start)

    items = []
    try:
        for i in xrange(size):
            items.append(iterator.next())
    except StopIteration:
        pass

    if reduce_fn is None:
        return items
    else:
        return reduce(reduce_fn,
                      items,
                      reduce_init)
