import os
import random
import socket
import time

from .scheduler import Job

random_initialized = False


def random_init(worker):
    global random_initialized

    if not random_initialized:
        random_initialized = True
        random.seed(os.urandom(16) + worker + str(time.time()))


def worker_process_step(arg):
    """
    :param arg:
    :rtype: Job
    """
    domain, start, size, reduce_fn, reduce_init = arg
    worker_name = "{}#{}".format(socket.gethostname(), os.getpid())
    job = Job(worker_name, start, size)

    random_init(worker_name)

    iterator = domain.iterate_steps(start, start + size)

    if reduce_fn is None:
        result = list(iterator)
    else:
        if reduce_init is None:
            result = reduce(reduce_fn, iterator)
        else:
            result = reduce(reduce_fn, iterator, reduce_init())

    job.finish(result)
    return job
