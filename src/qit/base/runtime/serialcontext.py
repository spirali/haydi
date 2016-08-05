class SerialContext(object):

    def run(self, domain, worker_reduce_fn, worker_reduce_init,
            global_reduce_fn, global_reduce_init):
        if worker_reduce_fn:
            it = domain.create_iterator()
            if worker_reduce_init is None:
                try:
                    first = it.next()
                except StopIteration:
                    if global_reduce_fn is None:
                        return []
                    else:
                        return global_reduce_init
            else:
                first = worker_reduce_init
            result = reduce(worker_reduce_fn, it, first)
        else:
            result = list(domain.create_iterator())

        if global_reduce_fn:
            if worker_reduce_fn and global_reduce_fn:
                result = (result,)
            if global_reduce_init is None:
                if not result:
                    return None
                return reduce(global_reduce_fn, result)
            else:
                return reduce(global_reduce_fn, result, global_reduce_init)
        else:
            return result
