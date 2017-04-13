import itertools

import iterhelpers


class SerialContext(object):

    def run(self, pipeline,
            timeout=None, dump_jobs=None, otf_trace=None):
        it = iterhelpers.make_iter_by_method(pipeline.domain, pipeline.method)
        it = iterhelpers.apply_transformations(it, pipeline.transformations)

        if pipeline.take_count is not None:
            it = itertools.islice(it,
                                  pipeline.take_count)

        if timeout:
            it = iterhelpers.iterate_with_timeout(it, timeout)

        action = pipeline.action
        print action
        worker_reduce_fn = action.worker_reduce_fn
        global_reduce_fn = action.global_reduce_fn
        worker_reduce_init = action.worker_reduce_init
        global_reduce_init = action.global_reduce_init

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
