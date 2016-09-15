from qitsession import session


class Action(object):

    worker_reduce_fn = None
    worker_reduce_init = None
    global_reduce_fn = None
    global_reduce_init = None

    def __init__(self, domain):
        """
        :type domain: qit.base.factory.IteratorFactory
        """
        self.domain = domain

    def run(self, parallel=False):
        """
        :type parallel: bool
        :return: Returns the computed result.
        """
        ctx = session.get_context(parallel)
        result = ctx.run(self.domain,
                         self.worker_reduce_fn,
                         self.worker_reduce_init,
                         self.global_reduce_fn,
                         self.global_reduce_init)
        return self.postprocess(result)

    def postprocess(self, value):
        return value

    def __iter__(self):
        return iter(self.run())


class Collect(Action):

    def __init__(self, domain, postprocess_fn):
        """
        :type domain: qit.base.factory.IteratorFactory
        """
        super(Collect, self).__init__(domain)
        if postprocess_fn:
            self.postprocess = postprocess_fn


class Reduce(Action):

    def __init__(self, domain, reduce_fn, init_value=0, associative=True):
        """
        :type domain: qit.base.factory.IteratorFactory
        :type fn: function
        """
        super(Reduce, self).__init__(domain)
        if associative:
            self.worker_reduce_fn = reduce_fn
        self.global_reduce_fn = reduce_fn
        self.global_reduce_init = init_value


class MaxAll(Action):

    def __init__(self, domain, key_fn):
        """
        :type domain: qit.base.factory.IteratorFactory
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
        self.worker_reduce_init = (None, None)
        self.global_reduce_fn = global_fn

    def postprocess(self, value):
        if value:
            return value[1]


class Samples(Action):

    def __init__(self, domain, key_fn, max_samples_per_key):
        def worker_fn(samples, item):
            value = key_fn(item)
            if value is None:
                return samples
            items = samples.get(value)
            if items is None:
                samples[value] = [item]
            elif len(items) < max_samples_per_key:
                items.append(item)
            return samples

        def global_fn(samples1, samples2):
            for key, items1 in samples1.items():
                r = max_samples_per_key - len(items1)
                if r > 0:
                    items2 = samples2.get(key)
                    if items2:
                        items1.extend(items2[:r])

            keys = set(samples2.keys())
            keys.difference_update(samples1.keys())
            for key in keys:
                samples1[key] = samples2[key]
            return samples1

        super(Samples, self).__init__(domain)
        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = {}
        self.global_reduce_fn = global_fn
