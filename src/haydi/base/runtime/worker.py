import os
import random
import socket
import time

from .iteration import generate, iterate_steps, apply_transformations
from .scheduler import Job


random_initialized = False


def random_init(worker):
    global random_initialized

    if not random_initialized:
        random_initialized = True
        random.seed(os.urandom(16) + worker + str(time.time()))


def worker_compute(iterator, start, size, timelimit, reduce_fn, reduce_init):
    worker_name = "{}#{}".format(socket.gethostname(), os.getpid())
    random_init(worker_name)

    job = Job(worker_name, start, size)
    result = []

    if timelimit is not None:
        for item in iterator:
            result.append(item)
            # return partial results
            if timelimit - time.time() < 60:
                break
    else:
        result = list(iterator)

    if reduce_fn is not None:
        if reduce_init is None:
            result = reduce(reduce_fn, result)
        else:
            result = reduce(reduce_fn, result,
                            reduce_init())

    job.finish(result)
    return job


def worker_step(arg):
    """
    :type arg: (dict, int, int)
    :rtype: Job
    """
    worker_args, start, size = arg
    iterator = iterate_steps(worker_args["domain"],
                             worker_args["transformations"],
                             start, start + size)

    return worker_compute(iterator, start, size,
                          worker_args["timelimit"],
                          worker_args["reduce_fn"],
                          worker_args["reduce_init"])


def worker_precomputed(arg):
    """
    :type arg: (dict, haydi.base.values.Values, int)
    :rtype: Job
    """
    worker_args, values, size = arg
    iterator = apply_transformations(values.create_iter(),
                                     worker_args["transformations"])

    return worker_compute(iterator, 0, size,
                          worker_args["timelimit"],
                          worker_args["reduce_fn"],
                          worker_args["reduce_init"])


def worker_generator(arg):
    """
        :type arg: (dict, int, int)
        :rtype: Job
        """
    worker_args, start, size = arg
    domain_iter = generate(worker_args["domain"])

    def iterator():
        for i in xrange(size):
            yield domain_iter.next()

    it = apply_transformations(iterator(), worker_args["transformations"])

    return worker_compute(it, start, size,
                          worker_args["timelimit"],
                          worker_args["reduce_fn"],
                          worker_args["reduce_init"])
