import itertools

from .iteration import choose_iterator, iterate_with_timeout


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

        it = choose_iterator(domain, method, transformations)

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
