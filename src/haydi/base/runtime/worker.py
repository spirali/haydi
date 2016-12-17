import os
import random
import socket
import traceback
import time
from datetime import datetime

from haydi import NoValue
from .scheduler import Job


class RandomSeed(object):
    initialized = False

    @staticmethod
    def initialize(worker):
        if not RandomSeed.initialized:
            RandomSeed.initialized = True
            random.seed(os.urandom(16) + worker + str(time.time()))


def worker_process_step(arg):
    """
    :param arg:
    :rtype: Job
    """
    domain, start, size, reduce_fn, reduce_init = arg
    worker_name = "{}#{}".format(socket.gethostname(), os.getpid())
    job = Job(worker_name, start, size)

    RandomSeed.initialize(worker_name)

    try:
        iterator = domain.create_iterator()
        iterator.set_step(start)

        def item_generator():
            for i in xrange(size):
                item = iterator.step()
                if item is not NoValue:
                    yield item

        if reduce_fn is None:
            result = list(item_generator())
        else:
            if reduce_init is None:
                result = reduce(reduce_fn, item_generator())
            else:
                result = reduce(reduce_fn, item_generator(), reduce_init())

        job.finish(result)
        return job
    except Exception as e:
        with open("{}-error-{}".format(worker_name, datetime.now()), "w") as f:
            f.write(traceback.format_exc(e) + "\n")
            f.write("start: {}, size: {}".format(start, size))

        raise e
