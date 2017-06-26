import utils


class Action(object):

    worker_reduce_fn = None
    worker_reduce_init = None
    global_reduce_fn = None
    global_reduce_init = None

    def postprocess(self, value):
        return value


class Collect(Action):
    pass


class Reduce(Action):

    def __init__(self, reduce_fn, init_value=0, associative=True):
        if associative:
            self.worker_reduce_fn = reduce_fn
        self.global_reduce_fn = reduce_fn
        self.global_reduce_init = lambda: init_value


class Max(Action):

    def __init__(self, key_fn, size):

        if key_fn is None:
            key_fn = utils.identity

        def worker_fn(pair, item):
            value = key_fn(item)
            best_value, best_items = pair
            if best_value is None or value > best_value:
                return (value, [item])
            if value == best_value and (size is None or
                                        len(best_items) < size):
                best_items.append(item)
            return pair

        def global_fn(pair1, pair2):
            best_value1, best_items1 = pair1
            best_value2, best_items2 = pair2
            if best_value1 == best_value2:
                if size is None:
                    return (best_value1, best_items1 + best_items2)
                elif len(best_items1) == size:
                    return pair1
                elif len(best_items2) == size:
                    return pair2
                else:
                    return (best_value1,
                            best_items1 + best_items2[:size -
                                                      len(best_items1)])
            elif best_value1 < best_value2:
                return pair2
            else:
                return pair1

        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: (None, None)
        self.global_reduce_fn = global_fn

    def postprocess(self, value):
        if value:
            return value[1]


class Groups(Action):

    def __init__(self, key_fn, max_items_per_group):

        def worker_fn(samples, item):
            value = key_fn(item)
            if value is None:
                return samples
            items = samples.get(value)
            if items is None:
                samples[value] = [item]
            elif (max_items_per_group is None or
                  len(items) < max_items_per_group):
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

        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: {}
        self.global_reduce_fn = global_fn


class GroupsAndCounts(Action):

    def __init__(self, key_fn, max_items_per_group):
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

        self.worker_reduce_fn = worker_fn
        self.worker_reduce_init = lambda: {}
        self.global_reduce_fn = global_fn
