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
    domain, start, size, reduce_fn, reduce_init, timelimit = arg
    worker_name = "{}#{}".format(socket.gethostname(), os.getpid())
    job = Job(worker_name, start, size)

    random_init(worker_name)

    iterator = domain.iterate_steps(start, start + size)
    result = []

    if timelimit is not None:
        for item in iterator:
            result.append(item)
            if timelimit - time.time() < 60:    # return partial results
                break
    else:
        result = list(iterator)

    if reduce_fn is not None:
        if reduce_init is None:
            result = reduce(reduce_fn, result)
        else:
            result = reduce(reduce_fn, result, reduce_init())

    job.finish(result)
    return job
