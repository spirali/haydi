from .haydisession import session


class Action(object):

    worker_reduce_fn = None
    worker_reduce_init = None
    global_reduce_fn = None
    global_reduce_init = None

    def __init__(self, domain):
        """
        :type domain: haydi.base.factory.IteratorFactory
        """
        self.domain = domain

    def run(self, parallel=False, timeout=None,
            dump_jobs=False, otf_trace=False):
        """
        :type parallel: bool
        :type timeout: int
        :type dump_jobs: bool
        :type otf_trace: bool
        :return: Returns the computed result.
        """
        ctx = session.get_context(parallel)
        result = ctx.run(self.domain,
                         self.worker_reduce_fn,
                         self.worker_reduce_init,
                         self.global_reduce_fn,
                         self.global_reduce_init,
                         timeout,
                         dump_jobs,
                         otf_trace)
        return self.postprocess(result)

    def postprocess(self, value):
        return value

    def __iter__(self):
        return iter(self.run())


class Collect(Action):

    def __init__(self, domain, postprocess_fn):
        """
        :type domain: haydi.base.factory.IteratorFactory
        """
        super(Collect, self).__init__(domain)
        if postprocess_fn:
            self.postprocess = postprocess_fn


class Reduce(Action):

    def __init__(self, domain, reduce_fn, init_value=0, associative=True):
        """
        :type domain: haydi.base.factory.IteratorFactory
        :type fn: function
        """
        super(Reduce, self).__init__(domain)
        if associative:
            self.worker_reduce_fn = reduce_fn
        self.global_reduce_fn = reduce_fn
        self.global_reduce_init = lambda: init_value


class MaxAll(Action):

    def __init__(self, domain, key_fn):
        """
        :type domain: haydi.base.factory.IteratorFactory
        :type key_fn: function
        """

        def worker_fn(pair, item):
            value = key_fn(item)
            best_value, best_items = pair
            if best_value is None or value > best_value:
                return (value, [item])
            if value == best_value:
                best_items.append(item)
            return pair

        def global_fn(pair1, pair2):
            best_value1, best_items1 = pair1
            best_value2, best_items2 = pair2
            if best_value1 == best_value2:
                return (best_value1, best_items1 + best_items2)
            elif best_value1 < best_value2:
                return pair2
            else:
                return pair1

        super(MaxAll, self).__init__(domain)
        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: (None, None)
        self.global_reduce_fn = global_fn

    def postprocess(self, value):
        if value:
            return value[1]


class Groups(Action):

    def __init__(self, domain, key_fn, max_items_per_group):
        def worker_fn(samples, item):
            value = key_fn(item)
            if value is None:
                return samples
            items = samples.get(value)
            if items is None:
                samples[value] = [item]
            elif len(items) < max_items_per_group:
                items.append(item)
            return samples

        def global_fn(samples1, samples2):
            for key, items1 in samples1.items():
                r = max_items_per_group - len(items1)
                if r > 0:
                    items2 = samples2.get(key)
                    if items2:
                        items1.extend(items2[:r])

            keys = set(samples2.keys())
            keys.difference_update(samples1.keys())
            for key in keys:
                samples1[key] = samples2[key]
            return samples1

        super(Groups, self).__init__(domain)
        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: {}
        self.global_reduce_fn = global_fn


class GroupsAndCounts(Action):

    def __init__(self, domain, key_fn, max_items_per_group):
        def worker_fn(samples, item):
            value = key_fn(item)
            if value is None:
                return samples
            items = samples.get(value)
            if items is None:
                samples[value] = [1, item]
            elif len(items) <= max_items_per_group:
                items.append(item)
                items[0] += 1
            else:
                items[0] += 1
            return samples

        def global_fn(samples1, samples2):
            for key, items1 in samples1.items():
                items2 = samples2.get(key)
                if items2:
                    items1[0] += items2[0]
                    r = max_items_per_group - (len(items1) - 1)
                    if r > 0:
                        items1.extend(items2[1:r+1])

            keys = set(samples2.keys())
            keys.difference_update(samples1.keys())
            for key in keys:
                samples1[key] = samples2[key]
            return samples1

        super(GroupsAndCounts, self).__init__(domain)
        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: {}
        self.global_reduce_fn = global_fn
