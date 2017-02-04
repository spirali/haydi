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
    :type arg: (haydi.base.runtime.scheduler.WorkerArgs, int, int)
    :rtype: Job
    """
    worker_args, start, size = arg
    worker_name = "{}#{}".format(socket.gethostname(), os.getpid())
    job = Job(worker_name, start, size)

    random_init(worker_name)

    iterator = worker_args.domain.iterate_steps(start, start + size)
    result = []

    if worker_args.timelimit is not None:
        for item in iterator:
            result.append(item)
            # return partial results
            if worker_args.timelimit - time.time() < 60:
                break
    else:
        result = list(iterator)

    if worker_args.reduce_fn is not None:
        if worker_args.reduce_init is None:
            result = reduce(worker_args.reduce_fn, result)
        else:
            result = reduce(worker_args.reduce_fn, result,
                            worker_args.reduce_init())

    job.finish(result)
    return job
