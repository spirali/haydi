from .util import TimeoutManager
import itertools


def iterate_with_timeout(iterator, timeout):
    timeout_mgr = TimeoutManager(timeout)
    for item in iterator:
        yield item
        if timeout_mgr.is_finished():
            return


def _generate(domain):
    while True:
        yield domain.generate_one()


class SerialContext(object):

    def run(self,
            domain,
            method,
            transformations,
            take_count,
            worker_reduce_fn,
            worker_reduce_init,
            global_reduce_fn,
            global_reduce_init,
            timeout=None,
            dump_jobs=False,
            otf_trace=False):

        if method == "iterate":
            it = domain.create_iter()
        elif method == "generate":
            it = _generate(domain)
        elif method == "cnfs":
            it = domain.create_cn_iter()
        else:
            raise Exception("Internal error, invalid method")

        for tr in transformations:
            it = tr.transform_iter(it)

        if take_count is not None:
            it = itertools.islice(it,
                                  take_count)

        if timeout:
            it = iterate_with_timeout(it, timeout)

        if worker_reduce_fn:
            if worker_reduce_init is None:
                try:
                    first = it.next()
                except StopIteration:
                    if global_reduce_fn is None:
                        return []
                    else:
                        return global_reduce_init()
            else:
                first = worker_reduce_init()

            result = reduce(
                worker_reduce_fn, it, first)
        else:
            result = list(it)

        if global_reduce_fn:
            if worker_reduce_fn and global_reduce_fn:
                result = (result,)
            if global_reduce_init is None:
                if not result:
                    return None
                return reduce(global_reduce_fn, result)
            else:
                return reduce(global_reduce_fn, result, global_reduce_init())
        else:
            return result
